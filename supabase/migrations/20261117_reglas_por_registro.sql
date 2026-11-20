-- v1.46.0 · Reglas por tipo de registro (auditoría técnica del 17/nov/2026: R2, R8, R13). Archivo: supabase/migrations/20261117_reglas_por_registro.sql
-- v1.55.2 (19/nov/2026): este archivo faltaba en el repositorio aunque estaba APLICADO en propesa_bc desde el 17/nov (migración
-- 20261117224943 «reglas_por_registro»). Se copió tal cual de supabase_migrations.schema_migrations para que el repositorio y la base coincidan.
-- Qué hace: push() pasa a security definer con revisión por tipo de registro (puede_escribir), piso ya no escribe precios, catálogos ni
-- ajustes, ni borra lotes/órdenes/informes ni cambia envíos cerrados; las tablas ya no se escriben directo (solo por push); cerrar_sesiones().
-- Orden para reconstruir la base: … → 20261106_quitar_reportes.sql → este archivo → 20261120_clave_canonica.sql.
create or replace function public.puede_escribir(rol text, k text, cur jsonb, nv jsonb)
  returns boolean language plpgsql immutable set search_path = public as
$$
declare
  base text := regexp_replace(coalesce(k, ''), '^q[0-9]+:', '');
  pre text := split_part(base, '/', 1);
begin
  if rol = 'admin' then return true; end if;
  if rol is distinct from 'piso' then return false; end if;
  if pre in ('$', 'W', 'C', 'V', 'E', 'Q', 'K', 'X', 'Z') then return false; end if;      -- precios, catálogos y ajustes
  if nv is null then                                                                    -- borrar
    if cur is null then return true; end if;
    if pre in ('R', 'OR', 'O') then return false; end if;
    if pre = 'P' and jsonb_typeof(cur) = 'object' and (cur->>'closed') = 'true' then return false; end if;
    return true;
  end if;
  if pre = 'D' then return jsonb_typeof(nv) = 'object' and pg_column_size(nv) < 300000; end if;
  if pre = 'P' and cur is not null and jsonb_typeof(cur) = 'object' and (cur->>'closed') = 'true' then
    if jsonb_typeof(nv) <> 'object' then return false; end if;
    return not exists (
      select 1 from (select jsonb_object_keys(cur) as f union select jsonb_object_keys(nv)) x
       where x.f not in ('alive', 'ta', 'mc', 'ob') and (cur -> x.f) is distinct from (nv -> x.f));
  end if;
  return true;
end $$;
revoke all on function public.puede_escribir(text, text, jsonb, jsonb) from public, anon, authenticated;

drop function if exists public.push(jsonb);
create function public.push(rows jsonb)
  returns table (k text, v jsonb, motivo text)
  language plpgsql security definer set search_path = public as
$$
#variable_conflict use_column
declare r jsonb; nv jsonb; cur jsonb; hay boolean; rol text := public.my_role();
begin
  if rol is null or rol not in ('admin', 'piso') then
    raise exception 'new row violates row-level security policy for table "app_records"' using errcode = '42501';
  end if;
  if jsonb_typeof(rows) is distinct from 'array' then
    raise exception 'push: rows debe ser una lista' using errcode = '22023';
  end if;
  if rol <> 'admin' and exists (select 1 from jsonb_array_elements(rows) e where (e.value->>'k') ~ '^(q[0-9]+:)?\$/') then
    raise exception 'new row violates row-level security policy for table "app_records"' using errcode = '42501';
  end if;
  for r in select value from jsonb_array_elements(rows) loop
    nv := nullif(r->'v', 'null'::jsonb);
    select a.v into cur from public.app_records a where a.k = r->>'k' for update;
    hay := found;
    if not hay then cur := null; end if;
    if hay and cur is not distinct from nv then
      null;
    elsif hay and r ? 'b' and cur is distinct from nullif(r->'b', 'null'::jsonb) then
      return query select r->>'k', cur, 'choque'::text;
    elsif not public.puede_escribir(rol, r->>'k', cur, nv) then
      return query select r->>'k', cur, 'permiso'::text;
    elsif not hay then
      insert into public.app_records (k, v) values (r->>'k', nv) on conflict (k) do nothing;
      if not found then return query select a.k, a.v, 'choque'::text from public.app_records a where a.k = r->>'k'; end if;
    else
      update public.app_records a set v = nv where a.k = r->>'k';
    end if;
  end loop;
end $$;
revoke all on function public.push(jsonb) from public, anon;
grant execute on function public.push(jsonb) to authenticated;

revoke insert, update, delete, truncate, references, trigger on public.app_records from authenticated, anon;
revoke all on public.app_records_hist from anon;
revoke insert, update, delete, truncate, references, trigger on public.app_records_hist from authenticated;
revoke all on public.profiles from anon;
revoke insert, delete, truncate, references, trigger on public.profiles from authenticated;

create or replace function public.cerrar_sesiones(uid uuid)
  returns integer language plpgsql security definer set search_path = public, auth as
$$
declare n integer;
begin
  delete from auth.refresh_tokens where user_id = uid::text;
  delete from auth.sessions where user_id = uid;
  get diagnostics n = row_count;
  return n;
end $$;
revoke all on function public.cerrar_sesiones(uuid) from public, anon, authenticated;
grant execute on function public.cerrar_sesiones(uuid) to service_role;
