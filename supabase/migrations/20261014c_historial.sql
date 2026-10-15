-- PROPESA · v1.4.1 (14/oct/2026): historial de cambios de la base compartida.
-- Cada vez que un registro de app_records cambia (o se borra, v = null), su versión anterior se copia a app_records_hist.
-- Así se puede recuperar lo que se pisó o se borró por error. Solo el Administrador lo puede leer; nadie lo edita desde la app.
-- Para recuperar un registro (SQL en el panel de Supabase):
--   select * from app_records_hist where k = 'P/<id>' order by rev desc;
--   update app_records set v = (select v from app_records_hist where id = <id del historial>) where k = 'P/<id>';
-- shortcut: el historial no se limpia solo; si un día pesa demasiado, borrar lo de más de un año (replaced_at).
create table if not exists public.app_records_hist (
  id bigint generated always as identity primary key,
  k text not null,
  v jsonb,                                              -- cómo estaba (null = ya estaba borrado)
  rev bigint not null,
  updated_at timestamptz not null,
  updated_by uuid,
  replaced_at timestamptz not null default clock_timestamp(),
  replaced_by uuid                                      -- quién lo cambió
);
create index if not exists app_records_hist_k on public.app_records_hist (k, rev);
alter table public.app_records_hist enable row level security;
create policy "ver historial" on public.app_records_hist for select to authenticated
  using ((select public.my_role()) = 'admin');
revoke all on public.app_records_hist from anon, authenticated;
grant select on public.app_records_hist to authenticated;

create or replace function public.app_records_stamp() returns trigger
  language plpgsql security definer set search_path = public as
$$ begin
  if tg_op = 'UPDATE' then
    insert into public.app_records_hist (k, v, rev, updated_at, updated_by, replaced_by)
    values (old.k, old.v, old.rev, old.updated_at, old.updated_by, auth.uid());
  end if;
  new.rev := nextval('public.app_rev');
  new.updated_at := clock_timestamp();
  new.updated_by := auth.uid();
  return new;
end $$;
