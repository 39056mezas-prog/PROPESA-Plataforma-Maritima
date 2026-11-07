-- PROPESA · v1.38.1 (6/nov/2026) · Quitar las 2 reglas del espacio de archivos «reportes».
-- Autorizado por el usuario el 6/nov/2026 («arregla 1-8», punto 8 de claude/AUDITORIA_PONYTAIL_v1.38.0.md). Aplicada ese día.
-- «reportes» venía del primer esquema (12/oct) para guardar los PDF; nunca se usó: la app no lo menciona y estaba vacío (0 archivos,
-- revisado antes de aplicar). No tenía límite de tamaño ni de tipo: Piso y Administrador podían subir ahí cualquier archivo.
-- Sin estas reglas ninguna cuenta de la app puede leer ni subir nada ahí.
-- El espacio en sí no se puede borrar con SQL (Supabase lo impide: «Use the Storage API»). Se borró desde el panel el 6/nov/2026
--   (Storage → reportes → ⋯ → Delete bucket); verificado: solo queda «fotos».
-- Las fotos de las notas usan su propio espacio «fotos» (20261015_fotos.sql), que no cambia.
-- Orden para reconstruir la base: … → 20261101_solo_inventario.sql → este archivo.

drop policy if exists "leer reportes" on storage.objects;
drop policy if exists "subir reportes" on storage.objects;
