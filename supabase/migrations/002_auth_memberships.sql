CREATE TABLE IF NOT EXISTS public.cleora_demo_workspaces (
 owner varchar PRIMARY KEY, data json NOT NULL
);
CREATE TABLE public.cleora_memberships (
 user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
 owner varchar NOT NULL REFERENCES public.cleora_demo_workspaces(owner) ON DELETE CASCADE
);
ALTER TABLE public.cleora_demo_workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cleora_memberships ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.cleora_demo_workspaces FROM anon, authenticated;
REVOKE ALL ON public.cleora_memberships FROM anon, authenticated;
GRANT SELECT ON public.cleora_demo_workspaces, public.cleora_memberships TO authenticated;
CREATE POLICY membership_self_read ON public.cleora_memberships FOR SELECT TO authenticated
 USING (user_id = (SELECT auth.uid()));
CREATE POLICY workspace_member_read ON public.cleora_demo_workspaces FOR SELECT TO authenticated
 USING (EXISTS (SELECT 1 FROM public.cleora_memberships m WHERE m.user_id=(SELECT auth.uid()) AND m.owner=cleora_demo_workspaces.owner));
-- Writes are backend-only. The server verifies Auth identity and membership before mutations.
-- No client insert/update membership permissions; user-editable metadata never grants access.
