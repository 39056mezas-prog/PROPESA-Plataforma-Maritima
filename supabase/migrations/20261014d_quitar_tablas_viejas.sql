-- PROPESA · POR APLICAR (necesita que el usuario confirme el borrado en Supabase; el 14/oct se canceló dos veces).
-- Tablas del primer esquema (supabase/schema.sql, 12/oct) que la app no usa desde la v1.4.0. Estaban vacías (verificado el 14/oct),
-- igual que el espacio de archivos "reportes". Se van con sus reglas, sus disparadores (lots_piso, shipments_piso) y su lugar
-- en la publicación de cambios en vivo. El espacio "reportes" se queda (Supabase no deja borrarlo con SQL y servirá para las fotos).
drop table if exists public.boxes, public.shipment_orders, public.order_lines, public.movements, public.notes,
  public.reports, public.orders, public.shipments, public.lots cascade;
drop function if exists public.piso_solo_conteo();

-- El disparador al crear usuario ya no hace nada (desde la v1.4.0 los perfiles solo los crea la función "usuarios").
drop trigger if exists al_crear_usuario on auth.users;
drop function if exists public.nuevo_perfil();

-- Después de aplicarlo: en supabase/schema.sql dejar solo profiles, my_role() y sus reglas.
