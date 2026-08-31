-- 只在本项目新建的 Supabase 项目中执行，禁止在原“熵合科技”项目执行。
create extension if not exists pgcrypto;

create table if not exists public.training_reports (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz not null default now(),
    case_data jsonb not null default '{}'::jsonb,
    model_metrics jsonb not null default '{}'::jsonb,
    risk_metrics jsonb not null default '{}'::jsonb,
    final_ratio numeric(5,4) not null check (final_ratio between 0 and 1),
    decision_reason text not null,
    object_path text not null unique
);

alter table public.training_reports enable row level security;
revoke all on table public.training_reports from anon, authenticated;

-- 不建立客户端读写策略。Streamlit 后端使用 Service Role 进行可选存档。
insert into storage.buckets (id, name, public)
values ('training-reports', 'training-reports', false)
on conflict (id) do update set public = false;
