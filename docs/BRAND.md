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

### Ícono de la app (favicon) · desde la v1.2.4
- El ícono de la pestaña del navegador y de «Agregar a pantalla de inicio» es una **langosta roja** (`#E8473D`, segmentos `#B5302A`) vista desde arriba, sobre azul marino `#0B1D59`. El usuario lo pidió así porque la empresa es de langosta; **el logo de PROPESA se queda igual** dentro de la app (menú, acceso, PDF).
- Archivos: `favicon.svg` (esquinas redondas), `icon-192.png`, `icon-512.png`, `apple-touch-icon.png` (cuadrados; el sistema redondea). Dibujo original hecho a mano en SVG; los PNG salen de ese mismo dibujo.
- Los enlaces llevan `?v=2` para que los equipos dejen de usar el ícono viejo guardado en caché.

## 2. Paleta de marca

| Token | Hex | Uso |
|---|---|---|
| `--brand-navy` / `--nav` | `#0B1D59` | Menú lateral (degradado a `#07123a`), superficies de marca |
| `--brand-blue` / `--ac` | `#087DBA` | Botones principales, elemento seleccionado, línea inferior del encabezado |
| `--brand-cyan` | `#16A6D1` | Acentos chicos: barra del menú activo, barras de avance, foco en tema oscuro |
| Navy activo | `#1B3680` | Fondo del elemento activo del menú |

**Proporción objetivo** (de `docs/referencias/PROPESA_Color_System_Refinement.md`): ~60 % superficies neutras · ~30 % navy · ~8 % azul océano · ~2 % cian. El cian nunca es fondo grande. Los colores de estado no cuentan en esa proporción.

## 3. Superficies y texto

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--bg` | `#f2f4f6` | `#111827` | Fondo de la página |
| `--cd` | `#fff` | `#1C2638` | Tarjetas |
| `--in` | `#eef1f4` | `#243249` | Campos, chips neutros |
| `--ln` | `#d9e0e6` | `#2D3B50` | Bordes |
| `--hl` | `#e1eff8` | `#2D3B50` | Resaltado |
| `--ink` | `#1c2733` | `#F1F5F9` | Texto principal |
| `--mut` | `#556575` | `#A9B7CA` | Texto secundario |
| `--fr` | `#0B1D59` | `#16A6D1` | Anillo de foco |

- **Encabezado:** blanco en claro (línea inferior de 3 px `#087DBA`); pizarra en oscuro.
- **Campos de captura:** relleno blanco en tema claro, flecha propia en los menús, números sin flechitas.
- **Tema:** claro, oscuro o el del equipo (Ajustes). Se guarda en `propesa-theme`; `data-theme` en `<html>`.

## 4. Colores de estado (semánticos, no de marca)

| Estado | Token / valor | Dónde |
|---|---|---|
| Pendiente o error real | `--alr #d50f1f` (fondo), `--alt #c8001a` (texto), `--alb #fff0f1` (caja) | Chips `.al`, cajas de alerta `.alb`. **Siempre con ícono ⚠ y texto**, nunca solo color. |
| Completo | `--ok #1f7a4d` (claro) / `#22C55E` (oscuro) | Chip `.chip.ok` con ✔ |
| Botón peligroso | `#b8321f` con texto blanco (`.btn.d`) | Borrar, quitar |
| Texto de aviso | `--cor #c23a26` (claro) / `#ff7a66` (oscuro) | |
| Interruptor encendido | `#34C759` (verde iOS) | Interruptor «Modo piso» |

Mortalidad final **no** se pinta de rojo como faltante: es el último paso.

## 5. Colores de talla (decididos por el usuario)

Constante `SZC`; se muestran como borde de 4 px en los campos de kilos y como punto de color (`szDot`) en etiquetas y encabezados.

| Talla (g) | Etiqueta en papel | Color | Hex |
|---|---|---|---|
| 491-610 | 0-650 / 491-610 | Blanco | `#FFFFFF` |
| 611-850 | 651-850 / 611-850 | Rojo | `#E5484D` |
| 851-1220 | 851-1250 / 851-1220 | Verde | `#30A46C` |
| 1221-UP | 1251-UP / 1221-UP | Amarillo | `#F5C518` |

## 6. Categorías de caja (Empaque)

Constante `RC`: **R** Rojo `#e5484d` · **V** Verde `#30a46c` · **B** Blanco `#e8f1f5`. En Modo piso son botones grandes ROJO / VERDE / BLANCO que se reconocen sin leer.
*(Pregunta abierta: ¿la categoría debería ser la talla? Ver `ROADMAP.md`.)*

## 7. Consignaciones y gráficas

Colores de embarque `XC`/`PAL`: `#1c7f9a` verde azulado, `#b0793a` dorado, `#5b6fd0` índigo, `#2a9d8f`, `#9a5fb0` violeta, `#3b87a6`. Se parecen a los de los formatos originales de PVG/HKG; el usuario pidió conservarlos.

## 8. Tipografía

- Fuente del sistema: `system-ui, -apple-system, "Segoe UI", sans-serif`. Sin fuentes externas (la CSP las bloquea y la app debe funcionar sin internet).
- Números tabulares (`font-variant-numeric: tabular-nums`) para que las cifras se alineen.
- Tamaño base `--app-font-size`: **Normal 15 px · Grande 17 px · Muy grande 20 px** (deslizador en Ajustes, `FS_STEPS`). Todo lo demás está en `rem`; los campos de captura nunca bajan de 16 px (`max(16px,1.0667rem)`).
- Títulos en peso 700–800; datos clave en el texto principal, etiquetas en `--mut`.

## 9. Forma y espacio

- Radios: tarjetas 16 px, botones 12 px, cajas de alerta 14 px, chips 999 px.
- Objetivos táctiles: 44 px mínimo, botones 48 px, chips de categoría 58 px, campos de Modo piso ~60 px.
- Tarjetas con borde sutil `--ln`, sin sombras pesadas ni brillos.
- Foco visible siempre: anillo de 2–3 px (`--fr` o `--ac`; blanco sobre el menú).

## 10. Íconos

- Íconos de línea en SVG (`IC`, `viewBox 0 0 24 24`). **Nada de emojis** en la interfaz.
- `iconize()` convierte ⚠ ✔ ✕ ☰ ● del texto en íconos SVG.
- Entrada y Embarque usan el mismo ícono (camión), a petición del usuario.

## 11. Modo piso (estilo iOS)

Encabezado translúcido con desenfoque, título grande, tarjetas con degradado y cuadros de ícono redondeados, interruptor tipo iOS. Mismos tokens de color; respeta tema oscuro. Cajas guardadas: grises con ✔, sin desaparecer.

## 12. Voz y textos

- Español de México, tuteo, frases cortas, verbos claros: «Guardar entrada», «Empacar cajas», «Cerrar empaque y enviar informe».
- Un aviso dice **qué falta y cómo resolverlo** («Faltan 3 · Empacar ›»).
- Sin tecnicismos ni palabras como «demo», «simulado» o «sistema real».
- Rutas internas (`recepcion`, `cierre`) no se renombran; solo cambian los textos visibles.

## 13. Lo que NO se hace (rechazado por el usuario)

- El sistema de color **semántico oscuro** (cian/verde/ámbar/rojo/morado sobre negro-navy, números gigantes, estados en el menú). Se revirtió por completo.
- Azul de marca fuera de las secciones de marca (menú, encabezado, banner, acceso) o reemplazando colores de estado.
- Galería de fotos de lotes en el Panel.
