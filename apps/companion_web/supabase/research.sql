-- research_tasks: queue of things Lyra should investigate
create table if not exists research_tasks (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  objective text not null,
  status text not null default 'queued', -- queued|running|done|failed
  priority int not null default 5,
  created_at timestamptz default now(),
  started_at timestamptz,
  finished_at timestamptz
);

-- research_logs: all steps + artifacts for auditability
create table if not exists research_logs (
  id bigint generated always as identity primary key,
  task_id uuid references research_tasks(id) on delete cascade,
  phase text not null, -- search|read|score|synthesize|propose|guard|apply|notify|error
  payload jsonb,
  created_at timestamptz default now()
);

-- Seed a first task
insert into research_tasks (title, objective, priority)
values ('Improve medical terminology TTS',
'Find free/open datasets and papers that improve pronunciation and emphasis for clinical terms; propose voice prompt tweaks and a lexicon list.', 8);
