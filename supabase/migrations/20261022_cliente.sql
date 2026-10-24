-- PROPESA · v1.13.0 (22/oct/2026) · Rol «cliente»: compradores de fuera (China) que solo ven la disponibilidad.
-- Pedido y autorizado por el usuario el 22/oct/2026 («gente de fuera», «sí» a cambiar las reglas de seguridad).
-- Antes, cualquier cuenta con perfil leía todo app_records (proveedores, consignatarios, notas…), todos los perfiles
-- (nombres y correos del personal) y las fotos. Una cuenta de fuera no puede tener eso, aunque la pantalla lo esconda.
-- Ahora:
--   · cliente lee de app_records SOLO 'D/disp': la hoja de disponibilidad que calcula la app (dispCalc en index.html).
--     pull() corre con los permisos de quien llama (security invoker), así que también solo le devuelve esa fila.
--   · cliente solo ve su propio perfil.
--   · cliente no ve fotos ni el espacio «reportes» (este último lo veía cualquier cuenta, aun sin perfil).
--   · escribir sigue siendo solo de admin y piso (no cambia).
-- Admin, piso y consulta ven lo mismo que antes.
-- Orden para reconstruir la base: schema.sql → 20261012b → 20261014 → 20261014b → 20261014c → 20261014d → 20261015_fotos → este archivo.

alter table public.profiles drop constraint if exists profiles_role_check;
alter table public.profiles add constraint profiles_role_check check (role in ('admin','piso','consulta','cliente'));

alter policy "ver" on public.app_records using (
  (select public.my_role()) in ('admin','piso','consulta')
  or ((select public.my_role()) = 'cliente' and k = 'D/disp'));

alter policy "ver" on public.profiles using (
  (select public.my_role()) in ('admin','piso','consulta') or id = (select auth.uid()));

alter policy "fotos ver" on storage.objects using (
  bucket_id = 'fotos' and (select public.my_role()) in ('admin','piso','consulta'));

alter policy "leer reportes" on storage.objects using (
  bucket_id = 'reportes' and (select public.my_role()) in ('admin','piso','consulta'));
