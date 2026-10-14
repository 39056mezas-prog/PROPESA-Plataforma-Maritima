# SUPABASE.md · Base compartida (preparada, NO conectada)

> **No conectes la cuenta de Supabase del usuario ni apliques el esquema** hasta que él lo pida explícitamente («supabase pero no conectes mi cuenta aún»). Aunque haya un conector de Supabase disponible en la sesión, no lo uses para crear proyectos, migraciones ni consultas.

## 1. Por qué

Hoy cada tablet tiene sus propios datos. El usuario decidió:
- La copia compartida será **Supabase** (Postgres + Auth + Storage + Realtime).
- Capturan **varias tablets** y hay gente que **solo consulta** (computadora o celular).
- Hay internet **casi siempre**; se asume que se puede capturar sin señal y sincronizar después.
- El archivo final de cada paso es un **PDF**, y **ese mismo PDF es el que se manda por correo**.

## 2. Lo que ya existe: `supabase/schema.sql`

| Tabla | Equivale a |
|---|---|
| `profiles` (+ `my_role()`) | `ST.U` (con Supabase Auth) |
| `lots` | `ST.R` |
| `movements` | `ST.L` (solo se agregan filas; las correcciones son reversas) |
| `orders` · `order_lines` | `ST.OR` |
| `shipments` · `shipment_orders` | `ST.P` y `o.sh` (un embarque junta varias órdenes) |
| `boxes` | `ST.B` |
| `notes` | `ST.M` (texto) |
| `reports` | PDF de cada paso en el bucket privado `reportes` |

- Llaves **UUID**, pesos en **gramos**, `created_by` / `updated_at`.
- **RLS:** sin sesión nadie entra; ver = todos; capturar = admin y piso; editar/borrar = admin; el piso puede actualizar el conteo final del lote y las vivas del embarque.
- **Realtime** en las tablas de operación (para pantallas de consulta).
- **Falta en el esquema:** tabla de **temperatura** (`ST.T`), fotos de las notas (Storage) y bitácora de auditoría.

## 3. Plan de sincronización (orden recomendado)

1. **IDs estables en la app**: hoy los embarques se identifican por su posición en `ST.P`, órdenes/líneas con `max+1` y cajas con `++BN`; dos tablets chocarían. Pasar a UUID y que `b.d` y `o.sh` apunten a ids, no a índices. Con migración.
2. **Local primero**: seguir guardando en el navegador y mandar cambios a una cola; subirlos cuando haya internet; mostrar «pendiente de sincronizar».
3. **Conflictos**: cajas, movimientos, notas y lecturas solo se agregan (no chocan); órdenes, embarques y lotes se editan por campo con «último cambio gana» y `updated_at`.
4. **Usuarios reales**: Supabase Auth + `profiles`; quitar el hash local; el primer admin se crea desde el panel de Supabase o con invitación.
5. **Consulta**: la misma página en solo lectura con Realtime.
6. **Correo con PDF**: al cerrar un embarque, subir el PDF a `reportes` y mandarlo con una Edge Function (Resend o SMTP) a los usuarios con «Recibe informes».
7. **Fotos** a Storage (hoy son base64 en el navegador).
8. **CSP**: agregar el dominio del proyecto Supabase a `connect-src` (y `img-src` si las fotos se sirven de Storage) en `vercel.json`.

## 4. Preguntas abiertas antes de conectar

- ¿Quién puede editar una orden ya empacada?
- ¿Dominio y remitente del correo?
- ¿Los de consulta entran con correo y contraseña?
- ¿Se importan los datos que ya están en cada tablet (respaldo `.json` → tablas)?
- ¿Región del proyecto? (cercana a Tijuana/California).
