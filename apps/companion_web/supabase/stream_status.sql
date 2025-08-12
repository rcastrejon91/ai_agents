create table if not exists stream_status (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  provider_user_id text not null,
  login text,
  live boolean default false,
  last_change timestamptz default now(),
  updated_at timestamptz default now(),
  unique(provider, provider_user_id)
);
