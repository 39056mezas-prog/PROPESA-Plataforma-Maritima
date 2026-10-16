# SUPABASE.md · Base compartida (CONECTADA desde la v1.4.0)

> El usuario pidió el 14/oct/2026 que **todos los equipos y todas las cuentas vean la misma información**. La app usa el proyecto de Supabase **`propesa_bc`** (`lktqwmfmdhusscudgflo`, región us-west-1, organización `propesa_org`).
> Antes de cambiar el esquema, las reglas de seguridad o la función de usuarios, **pregúntale al usuario**: los cambios llegan directo a la base que usan todas las tablets.

## 1. Qué hay en Supabase

| Pieza | Para qué |
|---|---|
| `public.app_records` | **Todos los datos de la operación**, un registro por cosa (ver §2). `k` = clave, `v` = contenido (null = borrado), `rev` = número de cambio que solo crece, `updated_at`, `updated_by` |
| Disparador `app_records_stamp` | Pone `rev`, `updated_at` y `updated_by` en cada escritura (la app no los puede falsear) |
| `public.push(rows)` (v1.4.1) | Guarda los cambios de la app **solo si el registro sigue como el equipo lo vio** (`b`). Si otro equipo lo cambió antes, no lo guarda y devuelve lo que hay en la base. Corre con los permisos de quien llama |
| `public.app_records_hist` (v1.4.1) | **Historial:** cada vez que un registro cambia o se borra, el disparador copia aquí cómo estaba (`k`, `v`, `rev`, quién y cuándo). Solo el Administrador lo puede leer; nadie lo edita desde la app. Cómo recuperar algo: ver §7 |
| `public.pull(since, lim)` | Cambios con `rev > since`, en orden, con `age` (segundos desde que se escribieron) |
| `public.has_admin()` | ¿Ya hay Administrador? (para mostrar la Configuración inicial) — se puede llamar sin sesión |
| `public.profiles` | Usuarios de la app: `id` (= cuenta de Supabase Auth), `name`, `email`, `role` (`admin`/`piso`/`consulta`), `notify` |
| `public.my_role()` | Rol de quien hace la consulta (lo usan las reglas) |
| Función Edge **`usuarios`** | Alta, cambios y baja de usuarios (solo Administrador) y `setup` del primer Administrador. Es lo único que usa la llave de servicio. Código en `supabase/functions/usuarios/index.ts` |
| `public.auth_user_id(mail)` | Busca una cuenta por correo; solo la puede usar la función `usuarios` |
| Espacio de archivos **`fotos`** (v1.8.0) | Las fotos de las notas: privado, máximo 2 MB por archivo, solo imágenes, rutas `notas/<id de la nota>/<n>.jpg`. Ver = quien tiene perfil; subir y borrar = Administrador y Piso; no se sobrescriben. Archivo `migrations/20261015_fotos.sql` |
| Espacio de archivos `reportes` | Del primer esquema; vacío y sin uso (pensado para los PDF) |
| Supabase Auth | Correo y contraseña de cada usuario |

Las tablas del primer esquema (`lots`, `movements`, `orders`, `order_lines`, `shipments`, `shipment_orders`, `boxes`, `notes`, `reports`), la función `piso_solo_conteo`, el disparador `al_crear_usuario` y su función `nuevo_perfil` **se borraron el 15/oct/2026** (`supabase/migrations/20261014d_quitar_tablas_viejas.sql`, la aplicó el usuario en Supabase). Antes se verificó que estaban vacías y que nada dependía de ellas. En la base quedan solo `app_records`, `app_records_hist` y `profiles`. El espacio de archivos `reportes` se queda (servirá para las fotos).

**Reconstruir la base desde cero** (por ejemplo, en un proyecto nuevo): correr en el SQL Editor, en este orden, `supabase/schema.sql`, `migrations/20261012b_solo_admin_cambia_rol.sql`, `20261014_sincronizacion.sql`, `20261014b_sin_pisar.sql`, `20261014c_historial.sql`, `20261014d_quitar_tablas_viejas.sql` y `20261015_fotos.sql`; después publicar la función `usuarios` y, si la base nueva tiene otra dirección, cambiarla en `index.html` (`SBC`), `vercel.json` (CSP) y `api/despierta.js`. Probado el 15/oct/2026 en un Postgres 16 local: deja las mismas tablas, funciones, disparadores y reglas que `propesa_bc`.

Migraciones aplicadas: `esquema_inicial_propesa`, `piso_borra_sus_cajas` (12/oct) y, el 14/oct, `app_records_tabla`, `app_records_reglas`, `ver_solo_con_perfil`, `sellar_funcion_stamp`. Todo junto y comentado en `supabase/migrations/20261014_sincronizacion.sql`. El 15/oct se aplicó `20261014d_quitar_tablas_viejas.sql` desde el SQL Editor, así que no sale en la lista de migraciones del panel; lo que hizo se verificó con SQL.

**v1.4.1 (aplicadas el 14/oct):** `sin_pisar` (función `push`, archivo `20261014b_sin_pisar.sql`) e `historial` (tabla `app_records_hist`, archivo `20261014c_historial.sql`). Se probaron en la base real dentro de una transacción que se deshizo. Función `usuarios` publicada en su versión 2 (se quitó un borrado repetido del perfil: la base ya lo borra en cascada al eliminar la cuenta). Se intentó quitar el disparador `al_crear_usuario` (llama a `nuevo_perfil`, que no hace nada) y la base canceló el paso; se quitó el 15/oct con `20261014d`.

Desde la v1.6.0 la app ya no tiene el camino viejo que subía sin revisar choques: si la base no tuviera `push`, la app marca «No se pudo subir» y guarda lo pendiente en el equipo hasta que se arregle.

## 2. Registros

| Clave | Contenido | Equivale a |
|---|---|---|
| `R/<lote>` | lote completo | `ST.R` |
| `L/<id>` | movimiento | `ST.L` |
| `B/<seq>` | caja, con `lot` y `d` = **id del embarque** (no índice) | `ST.B[lote][]` |
| `OR/<id>` | orden con sus líneas; `sh` apunta a **ids de embarque** | `ST.OR` |
| `P/<u>` | embarque (`u` = id fijo) | `ST.P` |
| `O/<u>` | informe de cierre | `ST.O` |
| `T/<id>` | lectura de temperatura | `ST.T` |
| `M/<id>` | nota y su `key` (las de embarque usan `emb:@<u>`). Desde la v1.8.0 `imgs` trae **referencias** `sb:notas/<id>/<n>.jpg`, no la foto (ver §8) | `ST.M` |

Los usuarios **no** van en registros: `ST.U` se llena con `profiles`.

## 3. Reglas de seguridad (RLS)

- **Ver:** solo quien tiene perfil (`my_role() is not null`). Una cuenta creada fuera de la app no ve nada.
- **Escribir registros:** Administrador y Encargado de piso. **Consulta** no puede escribir (403).
- **Perfiles:** solo los cambia el Administrador (y la función `usuarios`). Ya no se crean solos al registrarse (el disparador `al_crear_usuario` se borró el 15/oct); el disparador `perfil_rol` (función `solo_admin_cambia_rol`, archivo `20261012b_solo_admin_cambia_rol.sql`) rechaza que alguien con sesión que no sea Administrador cambie un rol.
- El resto de los permisos por rol (quién edita órdenes, cierra lotes…) lo cuida la app, igual que antes.

## 4. Cómo sincroniza la app (resumen; detalle en `ARQUITECTURA.md` §11)

1. **Local primero:** cada `save()` guarda en el equipo, calcula qué registros cambiaron (`syncStage`) y los anota en una cola (`propesa-out`).
2. **Subir:** `flush()` manda la cola en tandas a `rpc/push`, cada cambio con cómo estaba el registro antes (`propesa-outb`). Consulta no sube nada y **no borra** lo pendiente de otro usuario: espera a que entre un Administrador o Piso en ese equipo.
3. **Bajar:** cada 4 s (30 s con la app en segundo plano, y al volver el internet) `pull()` trae lo nuevo desde el último `rev` y `applyRows()` vuelve a armar `ST`. Lo que este equipo aún no sube gana sobre lo que llega.
4. **Conflictos (v1.4.1):** por registro, **gana el primero que guarda**. Si otro equipo cambió el mismo registro antes (por ejemplo, el Administrador cerró el embarque mientras piso capturaba las vivas sin internet), el cambio del segundo equipo no se guarda: ese equipo recibe lo de la base y ve «No se guardó tu cambio: otro equipo lo cambió antes…». Antes ganaba el último y podía reabrir un embarque o un lote cerrado. Cajas, movimientos, notas y lecturas casi nunca chocan porque cada una es un registro con id propio. **v1.5.1:** si el mismo registro se vuelve a cambiar mientras el primer cambio sube, el «antes» del segundo pasa a ser lo que se acaba de subir (antes la base lo rechazaba con un aviso falso); si hay un choque de verdad, gana la base también sobre lo que se cambió mientras tanto. Si la base rechaza un cambio pero tiene lo mismo, solo escrito distinto (un registro viejo que `WN` arregló al bajarlo), `flush()` lo vuelve a subir una vez contra lo que hay en la base.
5. **Sin internet:** se sigue capturando; aviso rojo «Sin conexión» mientras haya pendientes; se sube solo al volver.

## 5. Usuarios

- Los dos Administradores que ya estaban en Supabase (creados el 12/oct desde el panel) se dejaron con el correo confirmado para que puedan entrar con la contraseña que les pusieron.
- Para dar de alta a alguien: Administración → «+ Nuevo usuario» (la app llama a la función `usuarios`). Si el correo ya tenía cuenta en Supabase sin perfil, se reutiliza y se le pone la contraseña nueva.
- El registro libre está apagado y el correo confirmado es obligatorio (revisado en la auditoría del 15/oct/2026). La protección de contraseñas filtradas («Leaked password protection») solo existe en el plan Pro; por eso la función `usuarios` pide **mínimo 8 caracteres** y rechaza contraseñas fáciles (v1.7.0).
- **Configuración inicial (`setup`, v1.7.0):** la función solo crea el primer Administrador si la base no tiene **ninguna** cuenta (`profiles` vacía). Antes bastaba con que no hubiera Administrador: si alguien borraba a los Administradores desde el panel, cualquiera que abriera la página se volvía Administrador. Si algún día se quedan sin Administrador, se arregla con SQL en el panel: `update public.profiles set role='admin' where email='…';`.
- **Ojo:** los cambios de `supabase/functions/usuarios/index.ts` solo cuentan cuando se publican en Supabase (no los publica Vercel). **Publicada la versión 3 el 15/oct/2026 (v1.7.1)**, con permiso del usuario: igual al archivo del repositorio, `verify_jwt` apagado como antes (la función revisa la sesión ella misma). Para volver atrás: publicar el `index.ts` de la v1.6.0 (en el historial de git o en el zip anterior).
- **Veda (16 feb – 15 sep):** el plan gratis pausa la base tras 7 días sin uso. **Desde la v1.8.0 Vercel la mantiene despierta solo:** una vez al día llama a `api/despierta.js` (`vercel.json` → `crons`, a las 17:23 UTC ± 1 h), que consulta `rpc/has_admin` con la llave publicable. Cómo comprobarlo: `README.md` → *Fin de temporada*.

## 6. Pendientes

- **Correo real** del informe con su PDF (Edge Function + Resend/SMTP; falta remitente y dominio).
- El historial (`app_records_hist`) no se limpia solo: revisar su tamaño cada año.
- Pantalla en Administración para ver y recuperar versiones viejas (hoy se hace con SQL, §7).
- Copias de seguridad automáticas (plan de Supabase) además del respaldo `.json`.

## 7. Recuperar algo que se pisó o se borró (v1.4.1)

En el panel de Supabase → SQL Editor:

```sql
-- versiones viejas de un registro (la más reciente primero)
select id, v, replaced_at, replaced_by from app_records_hist where k = 'P/<id del embarque>' order by rev desc;
-- volver a poner una versión (los equipos la reciben solos en segundos)
update app_records set v = (select v from app_records_hist where id = <id del historial>) where k = 'P/<id del embarque>';
```

## 8. Fotos (v1.8.0)

- **Al guardar una nota** con fotos, cada foto (800 px, JPEG 0.6, ~90 KB) entra a una cola del equipo (IndexedDB, `fotos-cola`) y la nota guarda solo su referencia `sb:notas/<id de la nota>/<n>.jpg`. En `syncNow()` primero se suben las fotos (`upFotos`, `POST /storage/v1/object/fotos/<ruta>`) y después los registros, así los otros equipos ya encuentran el archivo cuando llega la nota.
- **Sin internet** la foto espera en la cola (cuenta en «cambios pendientes»). Si la base de archivos falla, la nota sí se sube y la foto se reintenta. Si la base **rechaza** una foto (permiso, tamaño), se quita de su nota y se avisa.
- **Para verla**, cada equipo la baja con su sesión (`GET /storage/v1/object/authenticated/fotos/<ruta>`) y la guarda en IndexedDB (`F/<ruta>`), así se sigue viendo sin internet. Mientras baja, el cuadro se ve gris.
- **Eliminar una nota** borra sus fotos; **Borrar todos los datos** también. Si en ese momento no hay internet, los archivos se quedan sin uso en el espacio (no estorban).
- **Fotos viejas dentro de una nota** (un respaldo restaurado o una versión anterior) se pasan solas al espacio de archivos la siguiente vez que sincroniza un Administrador o Piso (`fotoMigra`). La ruta depende solo del id de la nota y del número de foto, así que dos equipos que la pasan al mismo tiempo suben el mismo archivo.
- El respaldo `.json` lleva las notas con sus referencias, no las fotos.
- **Modo local** (pruebas): las fotos siguen dentro de la nota, como antes.
- Plan gratis de Supabase: 1 GB de archivos (unas 10,000 fotos) y 5 GB de descarga al mes.
- Probado: `pruebas/fotos_t.py` con el Supabase de mentira, y en `propesa_bc` (15/oct/2026, dentro de una transacción que se deshizo) que el Administrador sube y ve, y que una cuenta sin perfil o sin sesión no ve ni sube nada. La regla de borrar no se pudo probar en la base real (Supabase pide confirmar los borrados); es igual a la de subir.
