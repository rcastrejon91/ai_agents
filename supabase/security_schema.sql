create table if not exists security_events (
  id uuid primary key default gen_random_uuid(),
  ts timestamptz not null default now(),
  ip text,
  path text,
  method text,
  query text,
  user_agent text,
  referrer text,
  country text,
  city text,
  event text not null,
  details jsonb
);

alter table security_events enable row level security;

create policy "service can write" on security_events
  for insert to authenticated
  with check (true);
