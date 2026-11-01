-- PROPESA · v1.19.0 (26/oct/2026) · Precios de compra: solo el Administrador.
-- Pedido y autorizado por el usuario el 26/oct/2026 («solo administración puede ver», al preguntarle si se cerraban también en la base).
-- La app guarda el precio de cada recepción en su propio registro: '$/<lote>' en PROPESA y 'q<id>:$/<lote>' en otra maquila
-- (el registro del lote, 'R/<lote>', ya no lo trae). Con estas reglas:
--   · leer: el Administrador todo; Piso y Consulta todo menos los precios; Cliente solo 'D/disp' (igual que antes).
--     pull() corre con los permisos de quien llama (security invoker), así que a Piso y Consulta no les llegan los precios.
--   · escribir: el Administrador todo; Piso todo menos los precios; Consulta y Cliente nada (igual que antes).
-- El historial (app_records_hist) ya solo lo lee el Administrador.
-- Orden para reconstruir la base: schema.sql → … → 20261022_cliente.sql → 20261023_historial_corto.sql → este archivo.

alter policy "ver" on public.app_records using (
  (select public.my_role()) = 'admin'
  or ((select public.my_role()) in ('piso','consulta') and k !~ '^(q[0-9]+:)?\$/')
  or ((select public.my_role()) = 'cliente' and k = 'D/disp'));

alter policy "capturar" on public.app_records with check (
  (select public.my_role()) = 'admin'
  or ((select public.my_role()) = 'piso' and k !~ '^(q[0-9]+:)?\$/'));

alter policy "editar" on public.app_records
  using ((select public.my_role()) = 'admin' or ((select public.my_role()) = 'piso' and k !~ '^(q[0-9]+:)?\$/'))
  with check ((select public.my_role()) = 'admin' or ((select public.my_role()) = 'piso' and k !~ '^(q[0-9]+:)?\$/'));
