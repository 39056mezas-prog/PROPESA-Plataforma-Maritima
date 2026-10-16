-- PROPESA · APLICADA el 15/oct/2026 en propesa_bc (la aplicó el usuario en Supabase; el 14/oct y el 15/oct la confirmación desde el
-- asistente se canceló). Antes de aplicarla se verificó otra vez que las 9 tablas tenían 0 registros y que nada más dependía de ellas.
-- Tablas del primer esquema (supabase/schema.sql, 12/oct) que la app no usa desde la v1.4.0. Estaban vacías (verificado el 14/oct),
-- igual que el espacio de archivos "reportes". Se van con sus reglas, sus disparadores (lots_piso, shipments_piso) y su lugar
-- en la publicación de cambios en vivo. El espacio "reportes" se queda (Supabase no deja borrarlo con SQL y servirá para las fotos).
drop table if exists public.boxes, public.shipment_orders, public.order_lines, public.movements, public.notes,
  public.reports, public.orders, public.shipments, public.lots cascade;
drop function if exists public.piso_solo_conteo();

-- El disparador al crear usuario ya no hace nada (desde la v1.4.0 los perfiles solo los crea la función "usuarios").
drop trigger if exists al_crear_usuario on auth.users;
drop function if exists public.nuevo_perfil();

-- Se deja schema.sql como está: para reconstruir la base desde cero se corren en orden schema.sql, 20261012b, 20261014, 20261014b,
-- 20261014c y este archivo (probado el 15/oct en un Postgres 16 local: quedan las mismas tablas, funciones y disparadores que en propesa_bc).
