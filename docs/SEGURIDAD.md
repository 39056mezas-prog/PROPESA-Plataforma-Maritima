# SEGURIDAD.md

## 1. Qué protege la versión 1.0

| Riesgo | Protección | Dónde |
|---|---|---|
| Código inyectado en textos (XSS) | `E()` escapa `& < > " '` en todo texto del usuario | `index.html` |
| Respaldo `.json` malicioso o roto | `cleanST()` valida campo por campo: tipos, rangos, longitudes, ids sin caracteres peligrosos, imágenes solo `data:image/png|jpeg|webp|gif;base64`, exige un Administrador | `index.html` |
| Scripts o conexiones a otros sitios | **CSP**: `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; media-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'self'; form-action 'self'; upgrade-insecure-requests` | `vercel.json` |
| Conexión sin cifrar | HSTS 2 años con subdominios | `vercel.json` |
| Permisos del navegador | `Permissions-Policy`: cámara solo propia (fotos); micrófono, ubicación, pagos, USB apagados | `vercel.json` |
| Otros | `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy`, `Cross-Origin-Opener-Policy: same-origin` | `vercel.json` |
| Versión vieja en caché | `index.html` con `Cache-Control: no-cache` | `vercel.json` |
| Contraseñas en texto | Hash SHA-256 de `'propesa:'+id+':'+contraseña`; mínimo 6 caracteres; lista de contraseñas fáciles prohibidas (`PWD0`) | `index.html` |
| Borrado por accidente | Confirmación para quitar/eliminar; escribir BORRAR para borrar todo | `index.html` |

`pruebas/csp_t.py` confirma que la app funciona con estas cabeceras y que un script externo sí se bloquea.

## 2. Límites conocidos (decírselos al usuario si pregunta)

- **El inicio de sesión se valida en el navegador.** Protege el uso diario, no contra alguien con acceso técnico al equipo (puede leer o cambiar `localStorage`). La protección real llega con Supabase Auth + RLS.
- **La sesión sigue abierta al recargar o cerrar el navegador** (v1.2.5, lo pidió el usuario) hasta 12 horas después del último uso. En una tablet compartida, cada quien debe usar «Cerrar sesión» al terminar su turno; si no, el siguiente entra con la cuenta anterior.
- Los datos no están cifrados en el equipo.
- No hay bitácora de auditoría (quién cambió qué).
- `'unsafe-inline'` sigue en la CSP porque todo el JS/CSS está en línea y usa algunos `onload`/`onclick` en plantillas. Quitarlo exigiría nonces o hashes.

## 3. Reglas al programar

- Todo texto del usuario pasa por `E()`; los valores en atributos también.
- Nada de `eval`, `new Function` ni `innerHTML` con datos sin escapar.
- No cargues nada de otros dominios. Si algún día hace falta (Supabase), agrégalo explícitamente a la CSP y prueba con `csp_t.py`.
- No pongas usuarios, contraseñas, llaves ni tokens en el código. Los datos de prueba solo en `pruebas/`.
- Todo campo nuevo de `ST` se valida en `cleanST()`.
- Ninguna conexión a cuentas del usuario (Supabase, correo, Drive) sin que lo pida.
