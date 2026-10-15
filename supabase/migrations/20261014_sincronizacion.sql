-- PROPESA · Base compartida (versión 1.4.0, 14/oct/2026)
-- Todos los equipos y todas las cuentas ven los mismos datos.
-- Cada lote, movimiento, caja, orden, embarque, informe, lectura de temperatura y nota es un registro en public.app_records.
-- Los usuarios son cuentas de Supabase Auth + public.profiles (nombre, correo, rol, recibe informes).

-- 1. Registros compartidos ------------------------------------------------------------
create sequence if not exists public.app_rev;

create table if not exists public.app_records (
  k text primary key check (char_length(k) between 3 and 300),  -- 'R/<lote>', 'L/<id>', 'B/<caja>', 'OR/<id>', 'P/<id>', 'O/<id>', 'T/<id>', 'M/<id>'
  v jsonb,                                                       -- null = borrado
  rev bigint not null default nextval('public.app_rev'),         -- número de cambio (solo crece)
  updated_at timestamptz not null default clock_timestamp(),
  updated_by uuid
);
create index if not exists app_records_rev on public.app_records (rev);

create or replace function public.app_records_stamp() returns trigger
  language plpgsql security definer set search_path = public as
$$ begin
  new.rev := nextval('public.app_rev');
  new.updated_at := clock_timestamp();
  new.updated_by := auth.uid();
  return new;
end $$;
create trigger app_records_stamp before insert or update on public.app_records
  for each row execute function public.app_records_stamp();

alter table public.app_records enable row level security;
create policy "ver" on public.app_records for select to authenticated
  using ((select public.my_role()) is not null);
create policy "capturar" on public.app_records for insert to authenticated
  with check ((select public.my_role()) in ('admin','piso'));
create policy "editar" on public.app_records for update to authenticated
  using ((select public.my_role()) in ('admin','piso'))
  with check ((select public.my_role()) in ('admin','piso'));
revoke all on public.app_records from anon;
grant select, insert, update on public.app_records to authenticated;

-- Cambios desde un número de cambio. "age" = segundos desde que se escribió (la app vuelve a pedir lo más reciente por si otro equipo estaba guardando al mismo tiempo).
create or replace function public.pull(since bigint, lim int default 500)
  returns table (k text, v jsonb, rev bigint, age double precision)
  language sql stable security invoker set search_path = public as
$$ select r.k, r.v, r.rev, extract(epoch from clock_timestamp() - r.updated_at)::double precision
     from public.app_records r
    where r.rev > since
    order by r.rev
    limit least(greatest(lim, 1), 2000) $$;
revoke all on function public.pull(bigint, int) from public, anon;
grant execute on function public.pull(bigint, int) to authenticated;

-- ¿Ya hay Administrador? (la app lo usa para mostrar la Configuración inicial)
create or replace function public.has_admin() returns boolean
  language sql stable security definer set search_path = public as
$$ select exists (select 1 from public.profiles where role = 'admin') $$;
grant execute on function public.has_admin() to anon, authenticated;

-- 2. Usuarios -------------------------------------------------------------------------
alter table public.profiles add column if not exists email text;
update public.profiles p set email = u.email from auth.users u where u.id = p.id and p.email is distinct from u.email;

-- Ya no se crean perfiles solos al registrarse: solo el Administrador da de alta (función "usuarios").
-- Así, una cuenta creada desde fuera de la app no ve nada.
create or replace function public.nuevo_perfil() returns trigger
  language plpgsql security definer set search_path = public as
$$ begin return new; end $$;

-- Solo el Administrador (o la función "usuarios", con llave de servicio) cambia perfiles.
alter policy "perfil propio o admin" on public.profiles using ((select public.my_role()) = 'admin');

-- Para la función "usuarios": buscar una cuenta ya existente por correo.
create or replace function public.auth_user_id(mail text) returns uuid
  language sql stable security definer set search_path = public, auth as
$$ select id from auth.users where lower(email) = lower(mail) limit 1 $$;
revoke all on function public.auth_user_id(text) from public, anon, authenticated;
grant execute on function public.auth_user_id(text) to service_role;

-- 3. Ver = solo quien tiene perfil (antes bastaba con tener una cuenta) -------------------
do $$ declare t text; begin
  foreach t in array array['profiles','lots','movements','orders','order_lines','shipments','shipment_orders','boxes','notes','reports'] loop
    execute format('alter policy "ver" on public.%I using ((select public.my_role()) is not null)', t);
  end loop;
end $$;

-- 4. La función del disparador no se llama desde fuera.
revoke execute on function public.app_records_stamp() from public, anon, authenticated;
