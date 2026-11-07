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

### Pantalla de acceso · desde la v1.32.0
- Toda la pantalla en azul: logo blanco (`LOGOD`), título, flujo, botón blanco «Iniciar sesión» (texto azul marino) y una vista previa de Panel general (sidebar azul marino, planta en 3D con el mismo dibujo de la app, tarjetas) que se sale por la orilla.
- El formulario sale de lado en un cajón **blanco** (v1.32.1, pedido del usuario: «demasiado azul marino»): título `#0B1D59`, etiqueta «Acceso por rol» y botón Entrar en azul océano `#0472AB` (texto blanco), textos `#46557A`, fondo oscurecido gris neutro `#0a0f1a73`. Igual en tema claro y oscuro. (En la v1.32.0 era azul marino `#0E2A72` → `#0B1D59`.)
- Movimiento: abre en 0.55 s `cubic-bezier(.32,.72,0,1)`, cierra en 0.3 s; con «reducir movimiento», fundido de 0.2 s.

### Pantalla de carga · desde la v1.8.6
- Logo PROPESA en blanco (el mismo `LG`, guardado fijo en el HTML como `#boot`) centrado sobre `#0B1D59`, con tres puntos azul claro que suben y bajan. Mismo azul que `background_color` del manifiesto, así que después de la pantalla de Android (langosta blanca) no hay cambio de color.
- Se desvanece en 0.28 s cuando la app termina de arrancar; en la app instalada se ve al menos 0.5 s. Si se cambia el logo `LG`, hay que regenerar también el de `#boot`.
- El logo PROPESA del menú lateral y del acceso **no cambió** (sigue la recreación en SVG, `LG`).

### Vista previa al compartir el link · desde la v1.8.6
- `og-image.png` (1200×630, ~175 KB): el logo PROPESA en blanco (el mismo `LG` de la app, versión `LOGOD`) y «Plataforma marítima», sobre azul marino `#0B1D59` con un degradado suave. Se genera con Chromium desde el logo de la app; menos de 300 KB por el límite de WhatsApp.
- Etiquetas `og:*` y `twitter:*` en `index.html` con la dirección completa `https://app.propesa.org/og-image.png?v=1` (desde la v1.31.4; antes `propesa.org`, v1.13.2, y `propesa.vercel.app`). Si cambia la imagen, sube `?v=`: WhatsApp, Facebook y Slack guardan la vista previa vieja varios días.

### PDF a color por talla · desde la v1.22.0
- Los PDF con tallas llevan arriba la leyenda de la maquila: una tarjeta por talla del color de esa talla (nombre, gramaje y nombre del color; las claras con borde gris).
- En las tablas, cada columna de talla o categoría lleva el encabezado de su color y la columna teñida (22–30%; el total 45%). El resto de la tabla sigue en azul marino.

### Maquila en los PDF · desde la v1.23.0
- Debajo del logo y la línea azul: banda azul marino `#0B1D59` con «MAQUILA» (8 pt, azul claro) y el nombre en mayúsculas (20 pt, blanco). Páginas siguientes: etiqueta azul marino «MAQUILA X» arriba a la derecha.

### Logotipo de cada maquila · desde la v1.24.0
- PROPESA conserva su logo. Las demás llevan **emblema + «MAQUILA» + nombre**: el emblema tiene sus iniciales en azul marino `#0B1D59` y una ola, sobre una forma y un color propios (Abel: hexágono ámbar `#F5A623` «A»; David: círculo turquesa `#2DD4BF` «D»; Luis Arce: escudo lila `#C4B5FD` «LA»; las nuevas siguen la paleta `MQC`).
- «MAQUILA» va en mayúsculas espaciadas del color de la maquila; el nombre en blanco, grande. El menú lleva una franja de 4 px de ese color arriba; Modo piso y la barra de arriba, abajo.
- Los colores de maquila no se parecen a los de talla (blanco, rojo, verde, amarillo) para no confundirlos. Los PDF no cambian (banda «MAQUILA X» de la v1.23.0).

