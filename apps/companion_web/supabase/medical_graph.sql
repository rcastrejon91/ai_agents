-- Medical knowledge graph schema with curation
create extension if not exists vector;

-- Core nodes
create table if not exists kg_nodes (
  id uuid primary key default gen_random_uuid(),
  kind text not null check (kind in ('Condition','Drug','Gene','Finding','Test','Guideline','Trial','Paper','Org')),
  name text not null,
  canonical_id text,
  source_url text,
  embedding vector(1536),
  created_at timestamptz default now()
);
create index if not exists kg_nodes_name_idx on kg_nodes using gin (to_tsvector('simple', name));
create index if not exists kg_nodes_kind_idx on kg_nodes (kind);
create index if not exists kg_nodes_embedding_idx on kg_nodes (embedding);

-- Typed relationships
create table if not exists kg_edges (
  id uuid primary key default gen_random_uuid(),
  src_id uuid not null references kg_nodes(id) on delete cascade,
  dst_id uuid not null references kg_nodes(id) on delete cascade,
  rel text not null,
  evidence_id uuid references kg_nodes(id) on delete cascade,
  confidence real not null check (confidence between 0 and 1),
  status text not null default 'pending' check (status in ('pending','approved','rejected')),
  created_at timestamptz default now()
);
create index if not exists kg_edges_src_id_idx on kg_edges(src_id);
create index if not exists kg_edges_dst_id_idx on kg_edges(dst_id);
create index if not exists kg_edges_rel_idx on kg_edges(rel);
create index if not exists kg_edges_status_idx on kg_edges(status);

-- Provenance assertions
create table if not exists kg_assertions (
  id uuid primary key default gen_random_uuid(),
  edge_id uuid references kg_edges(id) on delete cascade,
  author text,
  method text,
  justification text,
  raw_snippet text,
  created_at timestamptz default now()
);

-- Upsert helper
create or replace function kg_upsert_node(
  p_kind text, p_name text, p_canonical_id text, p_source_url text, p_embedding vector
) returns kg_nodes as $$
declare r kg_nodes;
begin
  insert into kg_nodes (kind,name,canonical_id,source_url,embedding)
  values (p_kind,p_name,p_canonical_id,p_source_url,p_embedding)
  on conflict (id) do nothing;
  select * into r from kg_nodes
   where lower(name)=lower(p_name) and kind=p_kind and coalesce(canonical_id,'') = coalesce(p_canonical_id,'')
   limit 1;
  if r.id is null then
    insert into kg_nodes (kind,name,canonical_id,source_url,embedding)
    values (p_kind,p_name,p_canonical_id,p_source_url,p_embedding)
    returning * into r;
  end if;
  return r;
end; $$ language plpgsql;

-- Anchor search helper
create or replace function kg_anchor_nodes(p_query text, p_k int default 5)
returns setof kg_nodes as $$
begin
  return query
  select n.* from kg_nodes n
  where n.name ilike '%'||p_query||'%'
  order by length(n.name) asc
  limit p_k;
end; $$ language plpgsql;

-- Pending edges view for curation
create or replace view kg_edges_pending as
select
  e.id, e.rel, e.confidence, e.created_at,
  src.id as src_id, src.kind as src_kind, src.name as src_name,
  dst.id as dst_id, dst.kind as dst_kind, dst.name as dst_name,
  ev.id as ev_id, ev.name as ev_name, ev.source_url as ev_url
from kg_edges e
join kg_nodes src on src.id = e.src_id
join kg_nodes dst on dst.id = e.dst_id
left join kg_nodes ev on ev.id = e.evidence_id
where e.status = 'pending';
