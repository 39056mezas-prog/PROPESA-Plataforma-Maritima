# SUPABASE.md · Base compartida (CONECTADA desde la v1.4.0)

> El usuario pidió el 14/oct/2026 que **todos los equipos y todas las cuentas vean la misma información**. La app usa el proyecto de Supabase **`propesa_bc`** (`lktqwmfmdhusscudgflo`, región us-west-1, organización `propesa_org`).
> Antes de cambiar el esquema, las reglas de seguridad o la función de usuarios, **pregúntale al usuario**: los cambios llegan directo a la base que usan todas las tablets.

## 1. Qué hay en Supabase

| Pieza | Para qué |
|---|---|
| `public.app_records` | **Todos los datos de la operación**, un registro por cosa (ver §2). `k` = clave, `v` = contenido (null = borrado), `rev` = número de cambio que solo crece, `updated_at`, `updated_by` |
| Disparador `app_records_stamp` | Pone `rev`, `updated_at` y `updated_by` en cada escritura (la app no los puede falsear) |
| `public.push(rows)` (v1.4.1) | Guarda los cambios de la app **solo si el registro sigue como el equipo lo vio** (`b`). Si otro equipo lo cambió antes, no lo guarda y devuelve lo que hay en la base. Corre con los permisos de quien llama |
| `public.app_records_hist` (v1.4.1) | **Historial:** cada vez que un registro cambia o se borra, el disparador copia aquí cómo estaba (`k`, `v`, `rev`, quién y cuándo). Solo el Administrador lo puede leer; nadie lo edita desde la app. **Desde la v1.16.0 guarda solo 30 días** (se borra solo) y no guarda `D/disp`; la función `cambios(lim)` arma la lista de Administración → «Historial de cambios». Cómo recuperar algo: ver §7 |
| `public.pull(since, lim)` | Cambios con `rev > since`, en orden, con `age` (segundos desde que se escribieron) |
| `public.has_admin()` | ¿Ya hay Administrador? (para mostrar la Configuración inicial) — se puede llamar sin sesión |
| `public.profiles` | Usuarios de la app: `id` (= cuenta de Supabase Auth), `name`, `email`, `role` (`admin`/`piso`/`consulta`), `notify` |
| `public.my_role()` | Rol de quien hace la consulta (lo usan las reglas) |
| Función Edge **`usuarios`** | Alta, cambios y baja de usuarios (solo Administrador) y `setup` del primer Administrador. Es lo único que usa la llave de servicio. Código en `supabase/functions/usuarios/index.ts` |
| `public.auth_user_id(mail)` | Busca una cuenta por correo; solo la puede usar la función `usuarios` |
| Espacio de archivos **`fotos`** (v1.8.0) | Las fotos de las notas: privado, máximo 2 MB por archivo, solo imágenes, rutas `notas/<id de la nota>/<n>.jpg`. Ver = quien tiene perfil; subir y borrar = Administrador y Piso; no se sobrescriben. Archivo `migrations/20261015_fotos.sql` |
| ~~Espacio de archivos `reportes`~~ | **Ya no existe.** Del primer esquema, vacío y sin uso: sus reglas se quitaron en la v1.38.1 (`20261106_quitar_reportes.sql`) y el espacio se borró desde el panel el 6/nov/2026 (verificado: en Storage solo queda `fotos`) |
| Supabase Auth | Correo y contraseña de cada usuario |

Las tablas del primer esquema (`lots`, `movements`, `orders`, `order_lines`, `shipments`, `shipment_orders`, `boxes`, `notes`, `reports`), la función `piso_solo_conteo`, el disparador `al_crear_usuario` y su función `nuevo_perfil` **se borraron el 15/oct/2026** (`supabase/migrations/20261014d_quitar_tablas_viejas.sql`, la aplicó el usuario en Supabase). Antes se verificó que estaban vacías y que nada dependía de ellas. En la base quedan solo `app_records`, `app_records_hist` y `profiles`. El espacio de archivos `reportes` se quedó; las fotos usan su propio espacio `fotos` (v1.8.0) y a `reportes` se le quitaron las reglas en la v1.38.1.

**Reconstruir la base desde cero** (por ejemplo, en un proyecto nuevo): correr en el SQL Editor, en este orden, `supabase/schema.sql`, `migrations/20261012b_solo_admin_cambia_rol.sql`, `20261014_sincronizacion.sql`, `20261014b_sin_pisar.sql`, `20261014c_historial.sql`, `20261014d_quitar_tablas_viejas.sql`, `20261015_fotos.sql`, `20261022_cliente.sql`, `20261023_historial_corto.sql`, `20261026_precios.sql`, `20261101_solo_inventario.sql` y `20261106_quitar_reportes.sql`; después publicar la función `usuarios` y, si la base nueva tiene otra dirección, cambiarla en `index.html` (`SBC`), `vercel.json` (CSP) y `api/despierta.js`. Probado el 15/oct/2026 en un Postgres 16 local: deja las mismas tablas, funciones, disparadores y reglas que `propesa_bc`.

Migraciones aplicadas: `esquema_inicial_propesa`, `piso_borra_sus_cajas` (12/oct) y, el 14/oct, `app_records_tabla`, `app_records_reglas`, `ver_solo_con_perfil`, `sellar_funcion_stamp`. Todo junto y comentado en `supabase/migrations/20261014_sincronizacion.sql`. El 15/oct se aplicó `20261014d_quitar_tablas_viejas.sql` desde el SQL Editor, así que no sale en la lista de migraciones del panel; lo que hizo se verificó con SQL.

**v1.38.1 (aplicada el 6/nov/2026, con permiso del usuario):** `20261106_quitar_reportes` quitó las reglas «leer reportes» y «subir reportes» (el espacio estaba vacío, 0 archivos, y la app nunca lo usó; no tenía límite de tamaño ni de tipo). Verificado después: en `storage.objects` solo quedan las 3 reglas de `fotos`. El espacio no se pudo borrar con SQL (Supabase: «Use the Storage API»); se borró desde el panel ese mismo día. Al reconstruir la base desde cero, `schema.sql` lo vuelve a crear: bórralo en el panel o quita esas líneas.

**v1.19.0 (aplicada el 26/oct, con permiso del usuario):** `precios_solo_admin` (archivo `20261026_precios.sql`): los registros de precio (`$/<lote>` y `q<id>:$/<lote>`) solo los lee y escribe el Administrador. Comprobado en `propesa_bc` dentro de transacciones que se deshicieron: Piso y Consulta ven los lotes y 0 precios, el Administrador los ve; `push` de un precio como Piso → 42501; Piso sigue guardando lo demás.

**v1.16.0 (aplicada el 23/oct, con permiso del usuario):** `historial_corto` (archivo `20261023_historial_corto.sql`): historial de 30 días, sin `D/disp`, función `cambios`. No borró nada (lo más viejo era del 16/oct).

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
| `W/pesos` | peso estándar de la caja (`{h, g, p, c}`, v1.8.7) | `ST.W` |
| `E/<id>` | especie (`{id, n, en, off}`, v1.18.0) | `ST.ES` |
| `C/colores` | color de cada consignatario (`{índice: "#rrggbb"}`, v1.15.0) | `ST.CC` |
| `Q/<id>` · `K/<n>` · `X/<código>` | maquilas · consignatarios · destinos (v1.19.0, compartidos) | `ST.MQL` · `ST.CN` · `ST.DS` |
| `Z/tallas` | tallas de una maquila (v1.19.0) | `ST.SZ` |
| `$/<lote>` | precio de compra del lote (v1.19.0; **solo Administrador**) | `ST.R[].pr` |
| `TQ/<id>` | traslado de kg entre tanques (v1.19.0) | `ST.TQ` |
| `q<id>:<clave>` | **v1.19.0:** cualquier registro de una maquila que no es PROPESA (`q2:R/<lote>`, `q2:OR/<id>`…). Los de PROPESA conservan su clave de siempre. Sin cambios en tablas ni reglas: la clave es texto libre | `STX[id]` |
| `D/disp` | hoja de disponibilidad para los compradores (v1.13.0): `{z: g por talla, u: g pedidos sin talla, e: [[fecha, g por talla]]}`. La calcula cada equipo (`dispCalc`), no vive en `ST` | — |
| `M/<id>` | nota y su `key` (las de embarque usan `emb:@<u>`). Desde la v1.8.0 `imgs` trae **referencias** `sb:notas/<id>/<n>.jpg`, no la foto (ver §8) | `ST.M` |

Los usuarios **no** van en registros: `ST.U` se llena con `profiles`.

## 3. Reglas de seguridad (RLS)

- **Cómo aplicar la v1.30.0:** panel de Supabase → proyecto `propesa_bc` → SQL Editor → New query → pegar todo `supabase/migrations/20261101_solo_inventario.sql` → Run. Se puede aplicar antes o después de publicar la app: la versión publicada sigue funcionando (la Consulta queda como Cliente de PROPESA) y la nueva lee los perfiles sin `mq` si todavía no existe (`NO_MQ`).
- **v1.30.0 (`20261101_solo_inventario.sql`, aplicada el 1/nov/2026 con permiso del usuario; verificado: Consulta 1 registro, 1 perfil, 0 fotos; piso y admin 279):** «Solo inventario» (roles `cliente` y `consulta`) lee solo `D/disp` y `q<id>:D/disp` de las maquilas de `profiles.mq` (`my_mqs()`), su propio perfil, y nada de fotos ni «reportes». Las cuentas `consulta` pasan a `cliente` con `{1}`. Lo de abajo describe lo anterior.

- **Ver:** Administrador, Piso y Consulta ven todo; una cuenta creada fuera de la app no ve nada. **Cliente (v1.13.0, `20261022_cliente.sql`) solo ve `D/disp` y su propio perfil**; no ve fotos ni «reportes». `pull()` corre con los permisos de quien llama, así que al Cliente solo le devuelve esa fila.
- **Precios (v1.19.0):** los registros `$/<lote>` (con o sin prefijo de maquila) solo los lee y escribe el Administrador.
- **Escribir registros:** Administrador y Encargado de piso. **Consulta** no puede escribir (403).
- **Perfiles:** solo los cambia el Administrador (y la función `usuarios`). Ya no se crean solos al registrarse (el disparador `al_crear_usuario` se borró el 15/oct); el disparador `perfil_rol` (función `solo_admin_cambia_rol`, archivo `20261012b_solo_admin_cambia_rol.sql`) rechaza que alguien con sesión que no sea Administrador cambie un rol.
- El resto de los permisos por rol (quién edita órdenes, cierra lotes…) lo cuida la app, igual que antes.

## 4. Cómo sincroniza la app (resumen; detalle en `ARQUITECTURA.md` §11)

1. **Local primero:** cada `save()` guarda en el equipo, calcula qué registros cambiaron (`syncStage`) y los anota en una cola (`propesa-out`).
2. **Subir:** `flush()` manda la cola en tandas a `rpc/push`, cada cambio con cómo estaba el registro antes (`propesa-outb`). Consulta no sube nada y **no borra** lo pendiente de otro usuario: espera a que entre un Administrador o Piso en ese equipo.
3. **Bajar:** cada 4 s (30 s con la app en segundo plano, y al volver el internet) `pull()` trae lo nuevo desde el último `rev` y `applyRows()` vuelve a armar `ST`. Lo que este equipo aún no sube gana sobre lo que llega.
4. **Conflictos (v1.4.1):** por registro, **gana el primero que guarda**. Si otro equipo cambió el mismo registro antes (por ejemplo, el Administrador cerró el embarque mientras piso capturaba las vivas sin internet), el cambio del segundo equipo no se guarda: ese equipo recibe lo de la base y ve «No se guardó tu cambio: otro equipo lo cambió antes…». Antes ganaba el último y podía reabrir un embarque o un lote cerrado. Cajas, movimientos, notas y lecturas casi nunca chocan porque cada una es un registro con id propio. **v1.5.1:** si el mismo registro se vuelve a cambiar mientras el primer cambio sube, el «antes» del segundo pasa a ser lo que se acaba de subir (antes la base lo rechazaba con un aviso falso); si hay un choque de verdad, gana la base también sobre lo que se cambió mientras tanto. Si la base rechaza un cambio pero tiene lo mismo, solo escrito distinto (un registro viejo que `WN` arregló al bajarlo), `flush()` lo vuelve a subir una vez contra lo que hay en la base. **v1.38.0:** si la base solo trae campos que el equipo no tenía y lo demás está como lo vio, no es choque: se sube conservando esos campos (antes una tablet con código viejo los borraba). Con versión nueva publicada, el código viejo deja de subir y pide recargar. Los precios pendientes solo los sube un Administrador, y un rechazo (403) ya no borra lo pendiente.
5. **Hoja de disponibilidad (v1.13.0):** cada equipo de Administrador o Piso recalcula `D/disp` al guardar y al recibir cambios de otros (`applyRows` → `syncStage`). Solo depende de los datos, así que todos calculan lo mismo; si dos la suben a la vez, el choque no avisa a nadie (se recalcula sola). Consulta la ignora. El Cliente no sincroniza `ST`: `dispNow()` pide `pull` desde el último cambio que vio.
6. **Sin internet:** se sigue capturando; aviso rojo «Sin conexión» mientras haya pendientes; se sube solo al volver.

## 5. Usuarios

- Los dos Administradores que ya estaban en Supabase (creados el 12/oct desde el panel) se dejaron con el correo confirmado para que puedan entrar con la contraseña que les pusieron.
- Para dar de alta a alguien: Administración → «+ Nuevo usuario» (la app llama a la función `usuarios`). Si el correo ya tenía cuenta en Supabase sin perfil, se reutiliza y se le pone la contraseña nueva.
- El registro libre está apagado y el correo confirmado es obligatorio (revisado en la auditoría del 15/oct/2026). La protección de contraseñas filtradas («Leaked password protection») solo existe en el plan Pro; por eso la función `usuarios` pide **mínimo 8 caracteres** y rechaza contraseñas fáciles (v1.7.0).
- **Configuración inicial (`setup`, v1.7.0):** la función solo crea el primer Administrador si la base no tiene **ninguna** cuenta (`profiles` vacía). Antes bastaba con que no hubiera Administrador: si alguien borraba a los Administradores desde el panel, cualquiera que abriera la página se volvía Administrador. Si algún día se quedan sin Administrador, se arregla con SQL en el panel: `update public.profiles set role='admin' where email='…';`.
- **Ojo:** los cambios de `supabase/functions/usuarios/index.ts` solo cuentan cuando se publican en Supabase (no los publica Vercel). **Publicada la versión 4 el 22/oct/2026 (v1.13.0, acepta el rol `cliente`)**; antes, la versión 3 el 15/oct/2026 (v1.7.1), con permiso del usuario: igual al archivo del repositorio, `verify_jwt` apagado como antes (la función revisa la sesión ella misma). Para volver atrás: publicar el `index.ts` de la v1.6.0 (en el historial de git o en el zip anterior).
- **Veda (16 feb – 15 sep):** el plan gratis pausa la base tras 7 días sin uso. **Desde la v1.8.0 Vercel la mantiene despierta solo:** una vez al día llama a `api/despierta.js` (`vercel.json` → `crons`, a las 17:23 UTC ± 1 h), que consulta `rpc/has_admin` con la llave publicable. Cómo comprobarlo: `README.md` → *Fin de temporada*.

## 6. Pendientes

- **Correo real** del informe con su PDF (Edge Function + Resend/SMTP; falta remitente y dominio).
- Botón para regresar a una versión vieja desde la pantalla del historial (hoy se ve en Administración y se recupera con SQL, §7). El historial ya se limpia solo a los 30 días (v1.16.0).
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
- **Eliminar una nota** (o una orden) borra sus fotos. Si en ese momento no hay internet, los archivos se quedan sin uso en el espacio (no estorban).
- **Fotos viejas dentro de una nota** (un respaldo restaurado o una versión anterior) se pasan solas al espacio de archivos la siguiente vez que sincroniza un Administrador o Piso (`fotoMigra`). La ruta depende solo del id de la nota y del número de foto, así que dos equipos que la pasan al mismo tiempo suben el mismo archivo.
- El respaldo `.json` lleva las notas con sus referencias, no las fotos.
- **Modo local** (pruebas): las fotos siguen dentro de la nota, como antes.
- Plan gratis de Supabase: 1 GB de archivos (unas 10,000 fotos) y 5 GB de descarga al mes.
- Probado: `pruebas/fotos_t.py` con el Supabase de mentira, y en `propesa_bc` (15/oct/2026, dentro de una transacción que se deshizo) que el Administrador sube y ve, y que una cuenta sin perfil o sin sesión no ve ni sube nada. La regla de borrar no se pudo probar en la base real (Supabase pide confirmar los borrados); es igual a la de subir.

## 9. Borrar todos los datos a mano

Desde la v1.10.1 también se puede desde la app: Administración → «Configuración avanzada» (solo el Administrador; pide respaldo reciente, BORRAR TODO y la contraseña). Lo de abajo sigue sirviendo si la app no está disponible.

Decisión del usuario: nadie puede borrarlo todo desde la app; si algún día hace falta, lo hace el dueño de la cuenta de Supabase.

1. **Antes:** descarga un respaldo (Administración → *Datos y respaldo*) y pide que nadie esté capturando.
2. Supabase → proyecto `propesa_bc` → **SQL Editor** → New query:
   ```sql
   -- Borra lotes, órdenes, embarques, cajas, notas, informes y lecturas de temperatura en TODOS los equipos.
   -- Los usuarios no se tocan. Se marca cada registro como borrado (v = null) en lugar de quitar la fila:
   -- así cada equipo recibe el borrado al sincronizar y no vuelve a subir su copia.
   update public.app_records set v = null where v is not null;
   ```
   Las versiones anteriores quedan en `app_records_hist` (se pueden recuperar con §7). Para borrar también ese historial, sin vuelta atrás: `truncate public.app_records_hist;`
3. **Fotos:** Supabase → **Storage** → `fotos` → selecciona la carpeta `notas` → *Delete*.
4. En las tablets: abrir la app con internet; en unos segundos se vacían solas.

## 10. Agregar o quitar una maquila a mano (desde la v1.40.0)

Decisión del usuario (7/nov/2026): las maquilas están fuera del programa; la app ya no las agrega, oculta ni renombra. Si algún día hace falta, se hace aquí. Lista de siempre: 1 PROPESA, 2 Abel, 3 David, 4 Luis Arce.

1. Supabase → proyecto `propesa_bc` → **SQL Editor** → New query. Primero mira cuáles hay:
   ```sql
   select k, v from public.app_records where k like 'Q/%' and v is not null order by k;
   ```
2. **Si no sale ninguna**, la app está usando la lista de siempre: hay que escribir las 4 antes de agregar otra (si solo escribes la nueva, sería la única).
   ```sql
   insert into public.app_records (k, v) values
     ('Q/1','{"id":1,"n":"PROPESA"}'),('Q/2','{"id":2,"n":"Abel"}'),('Q/3','{"id":3,"n":"David"}'),('Q/4','{"id":4,"n":"Luis Arce"}')
   on conflict (k) do nothing;
   ```
3. **Agregar** (número que no exista, nombre de hasta 40 letras):
   ```sql
   insert into public.app_records (k, v) values ('Q/5','{"id":5,"n":"Nueva maquila"}')
   on conflict (k) do update set v = excluded.v, rev = nextval('public.app_rev'), updated_at = clock_timestamp();
   ```
   **Ocultarla** (sus datos se quedan): el mismo `update` con `{"id":5,"n":"Nueva maquila","off":true}`. **Cambiarle el nombre:** igual, con el nombre nuevo. PROPESA (1) no se oculta.
4. En las tablets: abrir la app con internet; en unos segundos sale en «PROPESA ▾» y en Usuarios (maquilas de cada cuenta de solo inventario).
