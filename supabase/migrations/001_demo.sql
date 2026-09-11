-- Apply only to a dedicated Cleora project, never another application's database.
CREATE TABLE IF NOT EXISTS public.cleora_demo_workspaces (
 owner varchar PRIMARY KEY,
 data json NOT NULL
);
ALTER TABLE public.cleora_demo_workspaces ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.cleora_demo_workspaces FROM anon, authenticated;
-- No public policies: backend server DB role only. Supabase Auth is not implemented yet.
