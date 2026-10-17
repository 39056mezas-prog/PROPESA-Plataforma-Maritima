# BRAND.md · Identidad visual de PROPESA

La marca es **marina e industrial**: azul marino profundo como ancla, azul océano para las acciones y cian solo como acento escaso. La pantalla tiene que leerse de un vistazo en una planta con poca luz.

Todos los valores viven como variables CSS en `:root` al inicio de `index.html`. **Reutiliza los tokens; no metas colores sueltos.**

## 1. Logo

| Cosa | Regla |
|---|---|
| Archivo | Recreación en SVG dentro del código: `LGP` (trazos) → `LG(o)` → `LOGO` (a color) y `LOGOD` (blanco). **No es el archivo oficial**; cuando el usuario lo suba, reemplaza `LGP`/`LG` sin cambiar tamaños. |
| Colores del logo | Azul oscuro `#0a2373` y azul `#0583c3` (difieren un poco de los tokens de marca; se dejaron así a propósito). |
| Sobre fondo oscuro | Versión blanca (`LOGOD`, clase `.lg.o`). |
| Tamaño | Pequeño: ≈128 px de ancho en el menú lateral; máx. 190 px en acceso y Configuración inicial. |
| Comportamiento | El logo es un botón que regresa al inicio (`.lgb`): vista completa → `inicio`, Modo piso → `piso`. |
| Nombre | PROPESA (en el logo aparece como PROPĒSA). Razón social: Proveedor del Pescador S.A. de C.V. |

### Ícono de la app (favicon) · desde la v1.2.4, langosta blanca desde la v1.8.1
- El ícono de la pestaña del navegador y de «Agregar a pantalla de inicio» (Android e iPhone) es una **langosta blanca** sobre azul marino `#0B1D59`: el mismo dibujo del ícono de Entrada del menú (`IC.recepcion`). Lo pidió el usuario el 15/oct/2026; antes era la misma langosta en rojo `#E8473D` con ojos y segmentos.
- Archivos: `favicon.svg` (esquinas redondas), `icon-192.png`, `icon-512.png`, `apple-touch-icon.png` (cuadrados completos, sin transparencia; el sistema redondea). En los PNG la langosta va al 80 % para caber en la zona segura de Android: por eso `icon-512.png` también se declara `maskable` en `manifest.webmanifest`. Los PNG se sacan del mismo dibujo con Chromium.
- Si se cambia el dibujo, sube el número `?v=` en `index.html` (`<link rel=icon>`, `apple-touch-icon`, `manifest`) y en `manifest.webmanifest`, para que los equipos no se queden con el ícono guardado. Hoy es `?v=4`.
- `icon-1024.png` (v1.8.6, `any` y `maskable`): Android dibuja el ícono de su pantalla de inicio a ~768 px y estiraba el de 512 (se veía pixeleado).

### Pantalla de carga · desde la v1.8.6
- Logo PROPESA en blanco (el mismo `LG`, guardado fijo en el HTML como `#boot`) centrado sobre `#0B1D59`, con tres puntos azul claro que suben y bajan. Mismo azul que `background_color` del manifiesto, así que después de la pantalla de Android (langosta blanca) no hay cambio de color.
- Se desvanece en 0.28 s cuando la app termina de arrancar; en la app instalada se ve al menos 0.5 s. Si se cambia el logo `LG`, hay que regenerar también el de `#boot`.
- El logo PROPESA del menú lateral y del acceso **no cambió** (sigue la recreación en SVG, `LG`).

### Vista previa al compartir el link · desde la v1.8.6
- `og-image.png` (1200×630, ~175 KB): el logo PROPESA en blanco (el mismo `LG` de la app, versión `LOGOD`) y «Plataforma marítima», sobre azul marino `#0B1D59` con un degradado suave. Se genera con Chromium desde el logo de la app; menos de 300 KB por el límite de WhatsApp.
- Etiquetas `og:*` y `twitter:*` en `index.html` con la dirección completa `https://propesa.vercel.app/og-image.png?v=1`. Si cambia la imagen, sube `?v=`: WhatsApp, Facebook y Slack guardan la vista previa vieja varios días.
