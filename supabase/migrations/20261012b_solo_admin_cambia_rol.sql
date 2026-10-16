-- PROPESA · Regla «solo el Administrador cambia roles» (aplicada el 12/oct/2026 en propesa_bc, dentro de las migraciones
-- `esquema_inicial_propesa` / `piso_borra_sus_cajas`). Hasta el 15/oct/2026 no estaba en ningún archivo del repositorio:
-- se copió tal cual de la base (pg_get_functiondef y pg_get_triggerdef) para que una base reconstruida desde cero la tenga.
--
-- Qué hace: antes de cambiar un perfil, si cambia el rol y quien lo hace tiene sesión (auth.uid() no es null) pero no es
-- Administrador, se rechaza. La función "usuarios" usa la llave de servicio (auth.uid() es null), así que sí puede.
-- Es una segunda barrera: la regla "perfil propio o admin" de profiles ya solo deja editar perfiles al Administrador.
--
-- Orden para reconstruir la base: schema.sql → este archivo → 20261014 → 20261014b → 20261014c → 20261014d.

create or replace function public.solo_admin_cambia_rol() returns trigger
  language plpgsql security definer set search_path to 'public' as
$$
begin
  if new.role is distinct from old.role and auth.uid() is not null and public.my_role() is distinct from 'admin' then
    raise exception 'Solo el administrador puede cambiar roles';
  end if;
  return new;
end $$;

drop trigger if exists perfil_rol on public.profiles;
create trigger perfil_rol before update on public.profiles
  for each row execute function public.solo_admin_cambia_rol();

-- Igual que en la base: solo postgres y service_role pueden llamarla directamente (el disparador la usa de todos modos).
revoke all on function public.solo_admin_cambia_rol() from public, anon, authenticated;
grant execute on function public.solo_admin_cambia_rol() to service_role;
