# SEGURIDAD.md

## 1. Qué protege (v1.4.0)

| Riesgo | Protección | Dónde |
|---|---|---|
| Código inyectado en textos (XSS) | `E()` escapa `& < > " '` en todo texto del usuario | `index.html` |
| Respaldo `.json` malicioso o roto | `cleanST()` valida campo por campo: tipos, rangos, longitudes, ids sin caracteres peligrosos, imágenes solo `data:image/png|jpeg|webp|gif;base64` o referencias `sb:notas/<número>/<0-5>.<jpg|png|webp|gif>`, exige un Administrador | `index.html` |
| Scripts o conexiones a otros sitios | **CSP**: `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self' https://lktqwmfmdhusscudgflo.supabase.co; media-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'self'; form-action 'self'; upgrade-insecure-requests` | `vercel.json` |
| Conexión sin cifrar | HSTS 2 años con subdominios | `vercel.json` |
| Permisos del navegador | `Permissions-Policy`: cámara solo propia (fotos); micrófono, ubicación, pagos, USB apagados | `vercel.json` |
| Otros | `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy`, `Cross-Origin-Opener-Policy: same-origin` | `vercel.json` |
| Versión vieja en caché | `index.html` con `Cache-Control: no-cache` | `vercel.json` |
| Acceso | **Supabase Auth** (correo y contraseña en el servidor). Mínimo 8 caracteres (desde la v1.7.0; antes 6) y contraseñas fáciles prohibidas (las revisa la función `usuarios`). La app ya no guarda ni revisa contraseñas (v1.4.1); el modo local de pruebas, solo en `localhost`, entra con el correo | Supabase, `index.html` |
| Quién ve y quién escribe | **RLS** en la base: ver solo con perfil; escribir solo Administrador y Piso; perfiles solo Administrador. Fotos (v1.8.0): espacio de archivos privado, mismas reglas, solo imágenes de hasta 2 MB y solo en `notas/`. La llave de servicio vive solo en la función `usuarios` | Supabase (`supabase/migrations/`) |
| Borrado por accidente | Confirmación para quitar/eliminar; escribir BORRAR para borrar todo | `index.html` |

`pruebas/csp_t.py` confirma que la app funciona con estas cabeceras y que un script externo sí se bloquea.

## 2. Límites conocidos (decírselos al usuario si pregunta)

- Los permisos finos (quién edita órdenes, cierra lotes, etc.) los aplica la pantalla; la base solo distingue «puede escribir» (Administrador, Piso) de «solo ver» (Consulta). Un Encargado de piso con conocimientos técnicos podría cambiar datos que la pantalla no le deja.
- El registro libre de cuentas está apagado en Supabase. La protección de contraseñas filtradas es del plan Pro; en su lugar, mínimo 8 caracteres y lista de contraseñas fáciles (función `usuarios`). La Configuración inicial solo funciona con la base sin ninguna cuenta (v1.7.0; ver `SUPABASE.md` §5).
- **La sesión sigue abierta al recargar o cerrar el navegador** (v1.2.5, lo pidió el usuario) hasta 12 horas después del último uso. En una tablet compartida, cada quien debe usar «Cerrar sesión» al terminar su turno; si no, el siguiente entra con la cuenta anterior.
- La copia de los datos en cada equipo (IndexedDB `propesa`, desde la v1.6.0) no está cifrada; incluye las fotos que ese equipo ya vio (v1.8.0).
- `api/despierta.js` (v1.8.0) es una dirección pública que solo hace la consulta «¿ya hay Administrador?» con la llave publicable; no lee ni cambia datos. Con `CRON_SECRET` en Vercel solo Vercel la puede usar.
- **Lo que llega de la base se revisa como un respaldo (v1.4.1, reforzado en v1.5.0):** `WN` quita `< > " ' ` & \` de claves, fechas y nombres, deja solo colores `#abc123`, fotos que de verdad son imagen y, desde la v1.5.0, **números donde van números** (`wnn`/`wn0`: temperaturas, kg, desperdicio, vivas, peso de componentes), que antes aceptaban texto y permitían esconder código en el tablero de tanques. Desde la v1.5.1 también revisa que los valores tengan sentido (mismas reglas que `cleanST`): ciudad y consignatario que existen, cajas ≥ 1, fechas que son fechas, categoría R/V/B/A, talla y tipo de movimiento válidos, y `wi` siempre devuelve texto o vacío. Lo que no se puede usar, `WN` lo devuelve como `null` y ese equipo lo ignora (no lo sube ni lo borra). Antes, una cuenta de piso podía guardar directo en la base un nombre de embarque con código escondido que corría en la pantalla del Administrador y se llevaba su sesión (`sincronizacion_t.py` lo prueba en todas las pantallas).
- Historial (v1.4.1): cada cambio o borrado deja la versión anterior en `app_records_hist`, con quién la reemplazó. Solo el Administrador lo lee (ver `SUPABASE.md` §7).
- `'unsafe-inline'` sigue en la CSP porque todo el JS/CSS está en línea y usa algunos `onload`/`onclick` en plantillas. Quitarlo exigiría nonces o hashes.

## 3. Reglas al programar

- Todo texto del usuario pasa por `E()`; los valores en atributos también.
- Nada de `eval`, `new Function` ni `innerHTML` con datos sin escapar.
- No cargues nada de otros dominios. El único permitido es el de Supabase en `connect-src`.
- No pongas usuarios, contraseñas ni la llave de servicio en el código. La llave **publicable** de Supabase sí va en `index.html` (es pública por diseño). Los datos de prueba solo en `pruebas/`.
- Todo campo nuevo de `ST` se valida en `cleanST()`.
- Ninguna conexión a cuentas del usuario (Supabase, correo, Drive) sin que lo pida.
