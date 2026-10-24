-- PROPESA · v1.16.0 (23/oct/2026) · Historial de cambios en Administración, con memoria corta.
-- Pedido del usuario: «ver quién, cuándo y qué valor se cambió… que no ocupe espacio en la base, memoria corta, para arreglar errores».
-- No hay tabla nueva: app_records_hist (20261014c) ya guarda cada versión anterior con quién y cuándo. Aquí solo:
--   1. Se borra sola: al cambiar cualquier registro, se quitan del historial las versiones reemplazadas hace más de 30 días.
--   2. 'D/disp' (la hoja de disponibilidad que la app recalcula sola) ya no entra al historial: no la cambia una persona.
--   3. cambios(lim): los últimos cambios (versión nueva + cómo estaba antes + quién + cuándo) para la pantalla de Administración.
--      Solo el Administrador recibe filas (además, el historial solo lo puede leer el Administrador).
-- Antes de aplicarla (23/oct/2026): 114 versiones en el historial, 112 kB de una base de 12 MB.
-- Orden para reconstruir la base: … → 20261022_cliente.sql → este archivo.

create index if not exists app_records_hist_replaced on public.app_records_hist (replaced_at);

create or replace function public.app_records_stamp() returns trigger
  language plpgsql security definer set search_path = public as
$$ begin
  if tg_op = 'UPDATE' and old.k <> 'D/disp' then
    insert into public.app_records_hist (k, v, rev, updated_at, updated_by, replaced_by)
    values (old.k, old.v, old.rev, old.updated_at, old.updated_by, auth.uid());
    delete from public.app_records_hist where replaced_at < clock_timestamp() - interval '30 days';
  end if;
  new.rev := nextval('public.app_rev');
  new.updated_at := clock_timestamp();
  new.updated_by := auth.uid();
  return new;
end $$;
revoke execute on function public.app_records_stamp() from public, anon, authenticated;

delete from public.app_records_hist where k = 'D/disp' or replaced_at < clock_timestamp() - interval '30 days';

-- Cada versión (la actual en app_records o una vieja en el historial) con la versión que tenía antes ese mismo registro.
-- antes = null y v ≠ null: se creó. v = null: se borró.
create or replace function public.cambios(lim int default 200)
  returns table (k text, v jsonb, antes jsonb, cuando timestamptz, quien uuid)
  language sql stable security invoker set search_path = public as
$$ with x as (
     select a.k, a.v, a.rev, a.updated_at, a.updated_by from public.app_records a
      where a.k <> 'D/disp' and a.updated_at > clock_timestamp() - interval '30 days'
     union all
     select h.k, h.v, h.rev, h.updated_at, h.updated_by from public.app_records_hist h
      where h.updated_at > clock_timestamp() - interval '30 days'
     order by rev desc limit least(greatest(lim, 1), 500))
   select x.k, x.v, p.v, x.updated_at, x.updated_by from x
     left join lateral (select h.v from public.app_records_hist h where h.k = x.k and h.rev < x.rev order by h.rev desc limit 1) p on true
    where (select public.my_role()) = 'admin'
    order by x.rev desc $$;
revoke all on function public.cambios(int) from public, anon;
grant execute on function public.cambios(int) to authenticated;
