-- PROPESA · v1.8.0 · Fotos en el espacio de archivos de Supabase (15/oct/2026).
-- Antes cada foto viajaba dentro de su nota (≈120 mil letras por foto) en app_records y en la copia de cada equipo.
-- Ahora la app sube la foto al espacio privado «fotos» (ruta notas/<id de la nota>/<n>.jpg) y la nota solo guarda
-- la referencia «sb:notas/<id>/<n>.jpg». Nadie la ve sin sesión: la app la baja con la sesión de quien la ve.
-- Reglas (iguales a las de app_records): ver = quien tiene perfil; subir y borrar = Administrador y Encargado de piso.
-- No hay regla de cambiar (update): una foto no se sobrescribe; la app usa rutas nuevas.
-- Límite por archivo 2 MB (la app manda ~90 KB: 800 px, JPEG 0.6) y solo imágenes.

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('fotos', 'fotos', false, 2097152, array['image/jpeg','image/png','image/webp','image/gif'])
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit, allowed_mime_types = excluded.allowed_mime_types;

do $$ begin
  if not exists (select 1 from pg_policies where schemaname = 'storage' and tablename = 'objects' and policyname = 'fotos ver') then
    create policy "fotos ver" on storage.objects for select to authenticated
      using (bucket_id = 'fotos' and (select public.my_role()) is not null);
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'storage' and tablename = 'objects' and policyname = 'fotos subir') then
    create policy "fotos subir" on storage.objects for insert to authenticated
      with check (bucket_id = 'fotos' and (select public.my_role()) in ('admin','piso') and (storage.foldername(name))[1] = 'notas');
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'storage' and tablename = 'objects' and policyname = 'fotos borrar') then
    create policy "fotos borrar" on storage.objects for delete to authenticated
      using (bucket_id = 'fotos' and (select public.my_role()) in ('admin','piso'));
  end if;
end $$;
