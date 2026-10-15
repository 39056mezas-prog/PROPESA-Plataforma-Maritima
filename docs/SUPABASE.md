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
| Supabase Auth | Correo y contraseña de cada usuario |

Tablas `lots`, `movements`, `orders`, `order_lines`, `shipments`, `shipment_orders`, `boxes`, `notes`, `reports` (del primer esquema, `supabase/schema.sql`): **existen pero la app no las usa** (están vacías, verificado el 14/oct). Borrarlas: `supabase/migrations/20261014d_quitar_tablas_viejas.sql`, **por aplicar** (Supabase pide confirmar los borrados y el 14/oct se canceló). Se pueden aprovechar más adelante para reportes.

Migraciones aplicadas: `esquema_inicial_propesa`, `piso_borra_sus_cajas` (12/oct) y, el 14/oct, `app_records_tabla`, `app_records_reglas`, `ver_solo_con_perfil`, `sellar_funcion_stamp`. Todo junto y comentado en `supabase/migrations/20261014_sincronizacion.sql`.

**v1.4.1 (aplicadas el 14/oct):** `sin_pisar` (función `push`, archivo `20261014b_sin_pisar.sql`) e `historial` (tabla `app_records_hist`, archivo `20261014c_historial.sql`). Se probaron en la base real dentro de una transacción que se deshizo. Función `usuarios` publicada en su versión 2 (se quitó un borrado repetido del perfil: la base ya lo borra en cascada al eliminar la cuenta). Se intentó quitar el disparador `al_crear_usuario` (llama a `nuevo_perfil`, que no hace nada) y la base canceló el paso; se queda, no estorba.

Si algún día la base no tuviera `push`, la app sube como la v1.4.0 (sin revisar choques).

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
| `M/<id>` | nota con fotos (base64) y su `key`; las de embarque usan `emb:@<u>` | `ST.M` |

Los usuarios **no** van en registros: `ST.U` se llena con `profiles`.

## 3. Reglas de seguridad (RLS)

- **Ver:** solo quien tiene perfil (`my_role() is not null`). Una cuenta creada fuera de la app no ve nada.
- **Escribir registros:** Administrador y Encargado de piso. **Consulta** no puede escribir (403).
- **Perfiles:** solo los cambia el Administrador (y la función `usuarios`). Ya no se crean solos al registrarse (`nuevo_perfil` no hace nada); el disparador `solo_admin_cambia_rol` sigue.
- El resto de los permisos por rol (quién edita órdenes, cierra lotes…) lo cuida la app, igual que antes.

## 4. Cómo sincroniza la app (resumen; detalle en `ARQUITECTURA.md` §11)

1. **Local primero:** cada `save()` guarda en el equipo, calcula qué registros cambiaron (`syncStage`) y los anota en una cola (`propesa-out`).
2. **Subir:** `flush()` manda la cola en tandas a `rpc/push`, cada cambio con cómo estaba el registro antes (`propesa-outb`). Consulta no sube nada y **no borra** lo pendiente de otro usuario: espera a que entre un Administrador o Piso en ese equipo.
3. **Bajar:** cada 4 s (30 s con la app en segundo plano, y al volver el internet) `pull()` trae lo nuevo desde el último `rev` y `applyRows()` vuelve a armar `ST`. Lo que este equipo aún no sube gana sobre lo que llega.
4. **Conflictos (v1.4.1):** por registro, **gana el primero que guarda**. Si otro equipo cambió el mismo registro antes (por ejemplo, el Administrador cerró el embarque mientras piso capturaba las vivas sin internet), el cambio del segundo equipo no se guarda: ese equipo recibe lo de la base y ve «No se guardó tu cambio: otro equipo lo cambió antes…». Antes ganaba el último y podía reabrir un embarque o un lote cerrado. Cajas, movimientos, notas y lecturas casi nunca chocan porque cada una es un registro con id propio.
5. **Sin internet:** se sigue capturando; aviso rojo «Sin conexión» mientras haya pendientes; se sube solo al volver.

## 5. Usuarios

- Los dos Administradores que ya estaban en Supabase (creados el 12/oct desde el panel) se dejaron con el correo confirmado para que puedan entrar con la contraseña que les pusieron.
- Para dar de alta a alguien: Administración → «+ Nuevo usuario» (la app llama a la función `usuarios`). Si el correo ya tenía cuenta en Supabase sin perfil, se reutiliza y se le pone la contraseña nueva.
- Recomendado en el panel de Supabase (no se puede desde aquí): **Authentication → Sign In / Providers → desactivar «Allow new users to sign up»** y activar «Leaked password protection». Aunque alguien se registre por fuera, no ve datos (no tiene perfil).

## 6. Pendientes

- **Fotos** a Supabase Storage (hoy viajan en base64 dentro de las notas; pesan).
- **Correo real** del informe con su PDF (Edge Function + Resend/SMTP; falta remitente y dominio).
- El historial (`app_records_hist`) no se limpia solo: revisar su tamaño cada año.
- Pantalla en Administración para ver y recuperar versiones viejas (hoy se hace con SQL, §7).
- Copias de seguridad automáticas (plan de Supabase) además del respaldo `.json`.
- Quitar las tablas viejas sin uso, si el usuario lo aprueba.

## 7. Recuperar algo que se pisó o se borró (v1.4.1)

En el panel de Supabase → SQL Editor:

```sql
-- versiones viejas de un registro (la más reciente primero)
select id, v, replaced_at, replaced_by from app_records_hist where k = 'P/<id del embarque>' order by rev desc;
-- volver a poner una versión (los equipos la reciben solos en segundos)
update app_records set v = (select v from app_records_hist where id = <id del historial>) where k = 'P/<id del embarque>';
```

