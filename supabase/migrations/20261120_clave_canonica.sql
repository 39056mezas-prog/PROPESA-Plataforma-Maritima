-- PROPESA · v1.55.2 (19/nov/2026) · Auditoría de seguridad, hallazgo F1 (claude/AUDITORIA_SEGURIDAD_v1.55.1.md).
-- Una clave de app_records lleva UNA sola marca de maquila ('q2:', 'q12:'…) o ninguna, y luego la columna en mayúsculas ('P/…', '$/…').
-- Antes la base aceptaba 'q1:q1:P/…' y 'q1:q1:$/…' de una cuenta de piso: la regla de precios ('^(q[0-9]+:)?\$/') no las reconocía
-- y la app las armaba como envío o precio sin limpiarlas (código que corría en la pantalla del Administrador, precios inventados).
-- La app v1.55.2 ya las ignora; esta regla hace que la base tampoco las guarde.
-- APLICADA el 19/nov/2026 en propesa_bc con permiso del usuario («sí aplica»). Antes: 0 claves fuera de la forma (ni en app_records ni en
-- el historial de 30 días), o sea, nadie lo había intentado. Probada después como cuenta de piso: «q1:q1:$/…» y «q1:q1:P/…» rechazadas,
-- «T/…» y «q2:T/…» aceptadas (prueba dentro de una transacción que se deshizo).
-- Orden para reconstruir la base: … → 20261106_quitar_reportes.sql → 20261117_reglas_por_registro.sql → este archivo.
--
-- Antes de aplicar, revisar (solo lectura) si alguien ya lo intentó; si sale algo, avisar al usuario con quién y cuándo:
--   select k, updated_at, updated_by from public.app_records where k !~ '^(q[1-9][0-9]*:)?[A-Z$]{1,3}/';
--   select k, replaced_at, replaced_by from public.app_records_hist where k !~ '^(q[1-9][0-9]*:)?[A-Z$]{1,3}/';

-- 1. Quitar las claves con dos marcas de maquila (no las escribe ninguna versión de la app).
delete from public.app_records where k ~ '^q[0-9]+:q';

-- 2. Desde ahora, la base rechaza claves fuera de la forma (aplica también a push(), que desde la v1.46.0 corre como security definer).
alter table public.app_records drop constraint if exists app_records_k_forma;
alter table public.app_records add constraint app_records_k_forma
  check (k ~ '^(q[1-9][0-9]*:)?[A-Z$]{1,3}/.') not valid;
alter table public.app_records validate constraint app_records_k_forma;
