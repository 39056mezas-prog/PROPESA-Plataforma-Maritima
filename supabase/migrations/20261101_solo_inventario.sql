-- PROPESA · v1.30.0 (1/nov/2026) · Cuenta de «solo inventario»: Consulta y Cliente pasan a ser una sola.
-- Pedido y autorizado por el usuario el 1/nov/2026: «esa cuenta de consulta o cliente no debería de mirar información sensitiva;
-- solo es para que puedan ver qué hay y vender, no mis precios ni mis maquilas», «sí, por favor arreglar eso».
-- Antes, Consulta leía todo app_records menos precios (proveedores, consignatarios, informes, notas), todos los perfiles y las fotos.
-- Ahora:
--   · profiles.mq = maquilas que ve una cuenta de solo inventario (ids; 1 = PROPESA). Solo el Administrador lo cambia.
--   · cliente y consulta leen de app_records SOLO las hojas de disponibilidad de sus maquilas: 'D/disp' (PROPESA) y 'q<id>:D/disp'.
--     pull() corre con los permisos de quien llama, así que solo les devuelve esas filas.
--   · cliente y consulta solo ven su propio perfil; no ven fotos ni «reportes».
--   · Las cuentas «consulta» que había pasan a «cliente» con PROPESA (lo que veía el rol Cliente hasta hoy).
--   · Las hojas de otras maquilas ('q<id>:D/disp') tampoco entran al historial ni a cambios().
-- Admin y piso no cambian. Escribir sigue siendo solo de admin y piso.
-- Orden para reconstruir la base: … → 20261026_precios.sql → este archivo.

alter table public.profiles add column if not exists mq int[] not null default '{}';

create or replace function public.my_mqs() returns int[]
  language sql stable security definer set search_path = public as
$$ select coalesce((select mq from public.profiles where id = auth.uid()), '{}') $$;
revoke all on function public.my_mqs() from public, anon;
grant execute on function public.my_mqs() to authenticated;

update public.profiles set role = 'cliente', mq = '{1}' where role = 'consulta';
update public.profiles set mq = '{1}' where role = 'cliente' and mq = '{}';

alter policy "ver" on public.app_records using (
  (select public.my_role()) = 'admin'
  or ((select public.my_role()) = 'piso' and k !~ '^(q[0-9]+:)?\$/')
  or ((select public.my_role()) in ('cliente','consulta')
      and k ~ '^(q[0-9]+:)?D/disp$'
      and coalesce(substring(k from '^q([0-9]+):')::int, 1) = any (coalesce((select public.my_mqs()), '{}'))));

alter policy "ver" on public.profiles using (
  (select public.my_role()) in ('admin','piso') or id = (select auth.uid()));

alter policy "fotos ver" on storage.objects using (
  bucket_id = 'fotos' and (select public.my_role()) in ('admin','piso'));

alter policy "leer reportes" on storage.objects using (
  bucket_id = 'reportes' and (select public.my_role()) in ('admin','piso'));

create or replace function public.app_records_stamp() returns trigger
  language plpgsql security definer set search_path = public as
$$ begin
  if tg_op = 'UPDATE' and old.k !~ '^(q[0-9]+:)?D/disp$' then
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

create or replace function public.cambios(lim int default 200)
  returns table (k text, v jsonb, antes jsonb, cuando timestamptz, quien uuid)
  language sql stable security invoker set search_path = public as
$$ with x as (
     select a.k, a.v, a.rev, a.updated_at, a.updated_by from public.app_records a
      where a.k !~ '^(q[0-9]+:)?D/disp$' and a.updated_at > clock_timestamp() - interval '30 days'
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
