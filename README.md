# PROPESA · Plataforma marítima · v1.8.0

Sitio estático de una sola página (HTML + CSS + JavaScript, sin dependencias ni paso de compilación).
Incluye recepción de lotes, captura de cajas, embarques, cierre y mortalidad, temperatura, y fotos y notas por sección.

## Contenido

| Archivo | Para qué sirve |
|---|---|
| `index.html` | Toda la aplicación |
| `manifest.webmanifest`, `favicon.svg`, `icon-*.png`, `apple-touch-icon.png` | Ícono (langosta) y opción "Agregar a pantalla de inicio" en tablet |
| `vercel.json` | Configuración de Vercel (encabezados de seguridad: CSP, HSTS, Permissions-Policy; caché; y la tarea diaria que mantiene despierta la base) |
| `api/despierta.js` | La tarea diaria: una consulta pequeña a la base para que el plan gratis de Supabase no la pause (ver *Fin de temporada*) |
| `supabase/` | Base compartida: `migrations/` (lo que está aplicado en el proyecto `propesa_bc`, incluido el espacio de archivos «fotos»), `functions/usuarios` (alta de usuarios) y `schema.sql` (primer esquema) |
| `pruebas/` | Pruebas automáticas (ver «Pruebas») |
| `CHANGELOG.md` | Cambios por versión |
| `CLAUDE.md` · `AGENTS.md` | Instrucciones para asistentes de IA (empiezan aquí) |
| `docs/` | Contexto completo: producto, UX, marca, arquitectura, datos, decisiones, roadmap, pruebas, seguridad, Supabase, flujo de trabajo, historial y documentos de referencia |
| `.claude/settings.json` | Activa el plugin agent-skills en Claude Code |

## Probar en tu computadora

Abre `index.html` en el navegador, o levanta un servidor local:

```bash
python3 -m http.server 8080
# abre http://localhost:8080
```

## Base compartida

Desde la v1.4.0 los datos viven en Supabase (proyecto `propesa_bc`): **todos los equipos y todas las cuentas ven lo mismo**, y cada equipo guarda una copia para seguir trabajando si se va el internet (lo sube solo al regresar). Detalle en `docs/SUPABASE.md`.

## Primer uso

Cada persona entra con el **correo y la contraseña** que le dio el Administrador. Si la base todavía no tiene ninguna cuenta, la app abre **Configuración inicial** para crear el Administrador (nombre, correo y contraseña de mínimo 8 caracteres; las contraseñas muy fáciles se rechazan). Después, en **Administración**, el Administrador da de alta a los demás usuarios con su rol:

| Rol | Puede |
|---|---|
| Administrador | Todo, incluidos usuarios, respaldo y borrado de datos |
| Encargado de piso | Entra directo a Modo piso: empacar, registrar entradas, cerrar embarques, conteo final |
| Consulta | Solo ver |

Para cargar un respaldo `.json`: Administración → **Restaurar respaldo** (reemplaza los datos de todos los equipos; los usuarios no cambian).

## Subir a GitHub

```bash
cd propesa-plataforma
git init
git add .
git commit -m "PROPESA plataforma marítima"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/propesa-plataforma.git
git push -u origin main
```

(Crea antes el repositorio vacío en github.com.)

## Desplegar en Vercel

1. Entra a https://vercel.com/new e importa el repositorio de GitHub.
2. Configuración: **Framework Preset: Other**, sin Build Command, sin Output Directory (se sirve la raíz).
3. Pulsa **Deploy**. Cada `git push` a `main` vuelve a desplegar automáticamente.

También con la CLI: `npx vercel --prod` dentro de la carpeta.

## Flujo de la plataforma

**Entrada → Órdenes → Empaque → Embarque → Mortalidad final**

1. **Entrada:** se captura el formato de recepción (fecha, hora, proveedor, tanque, temperaturas, lote (se escribe en mayúsculas solo), kg por caja en tanque, kg por talla, kg total y kg de desperdicio). Aquí no se cuentan ni se numeran cajas.
2. **Órdenes:** ciudad destino → consignatario (lista oficial, constante `CONS`) → cliente final → cajas. Se usan 16 kg netos y 19.6 kg brutos por caja (`KGN` y `KGB`; el bruto es la suma de hielera, gel, producto y caja).
3. **Empaque:** las langostas se cuentan al empacar cada pedido. Aparece una fila por cada caja que falta (piezas vivas + categoría + lote) y se guardan todas a la vez; las filas en blanco no se guardan. Cada caja se numera sola. Aquí solo hay notas, sin fotos.
4. **Embarque:** cada orden crea su embarque, pero varias órdenes con el mismo destino y consignatario se pueden juntar en uno solo (botón «Unir» en la orden, o «Agregar otra orden» en el embarque; «Separar» las divide). Las hieleras se suman, se revisan peso y tallas y se cierra el empaque.
5. **Mortalidad final:** conteo final por lote y langostas vivas al llegar; el sistema calcula la pérdida.

## Modo piso

Pantalla con botones grandes para el personal de piso (entra solo con el rol *Encargado de piso*; el Administrador lo prende y apaga con el interruptor estilo iOS «Modo piso», en el menú y en el encabezado). Tocar el logo regresa al inicio en cualquier modo. Cuatro botones: **Empacar cajas**, **Registrar entrada**, **Cerrar embarque**, **Conteo final**.
- *Empacar:* cliente → lote (se salta si solo hay uno) → una tarjeta grande por cada caja del cliente (piezas + ROJO / VERDE / BLANCO). Cada caja **se guarda sola** al tener piezas y categoría y se queda en gris con ✔ en su lugar; se corrige ahí mismo o se quita con «Quitar». «Poner a todas las vacías» aplica una categoría de un toque.
- En Órdenes y Empaque, el aviso rojo «X de Y cajas empacadas» es un botón que lleva directo al cliente al que le faltan cajas.
- *Registrar entrada:* hoja con una fila por lote (proveedor, tanque, lote, kg por talla); «+ Agregar entrada» para más filas, «Más» para temperaturas, kg por caja, desperdicio, fecha y hora, y «Guardar entradas» guarda todas las filas completas (las que tienen errores se quedan marcadas en rojo).
- Colores de talla: 491-610 Blanco · 611-850 Rojo · 851-1220 Verde · 1221-UP Amarillo.

## Ajustes

**Barra superior:** botón **Ajustes** y círculo con la inicial (también en Modo piso). El círculo abre **Administración** (solo admin) y **Cerrar sesión**. En Ajustes: tema **Oscuro / Claro** y **Tamaño del texto** con deslizador de 3 tamaños: Normal, Grande y Muy grande (se guardan en este equipo; `propesa-theme`, `propesa-fs`). Especificación en `SPEC.md`; pruebas en `pruebas/` (`python3 -m http.server 8765` y luego `python3 -I pruebas/ajustes_t.py`, `python3 -I pruebas/menu_t.py` y `python3 -I pruebas/e2e.py`).

## Colores

Los colores están en variables CSS al inicio de `index.html` (`:root`). Marca: `--brand-navy #0B1D59` (barra lateral), `--brand-blue #087DBA` (acciones principales, botón activo), `--brand-cyan #16A6D1` (acentos pequeños: indicador del menú activo, barras de avance, foco). Tema oscuro: fondo `#111827`, tarjetas `#1C2638`, bordes `#2D3B50`, texto `#F1F5F9` / `#A9B7CA`. Estados: verde (completo), ámbar (precaución), rojo (error o pendiente real). El logo no se tocó.

## PDF de cada paso

En Entrada, Órdenes, Empaque, Embarque y Mortalidad final hay una barra con **Descargar PDF** y **Enviar por correo**. El PDF se genera dentro de la app (sin librerías ni internet) con el logo de PROPESA; es el mismo archivo que se descarga y el que se manda por correo. En tablet y celular, *Enviar por correo* abre el menú de compartir con el PDF adjunto; en computadora descarga el PDF y abre el correo para adjuntarlo. Cada cierre de empaque queda en **Administración → Informes de cierre**, con su PDF para descargar o enviar por correo.

## Temperatura

Bitácora real de lecturas por tanque (agua, superficie y producto en °F, 20–110). Guarda fecha, hora y quién capturó; muestra los últimos 7 días con opción de ver todo. El Administrador puede eliminar una lectura equivocada.

## Datos y respaldo

- Los datos se guardan en la **base compartida** (Supabase, proyecto `propesa_bc`): todos los equipos y cuentas ven lo mismo. Cada equipo guarda una copia y sigue funcionando sin internet; lo que se capture se sube solo cuando regresa la conexión.
- Administración → *Datos y respaldo*: muestra la última actualización con la base y si hay cambios pendientes. **Descarga un respaldo `.json` de vez en cuando.** «Restaurar respaldo» reemplaza los datos de **todos** los equipos (el archivo se revisa y limpia antes; los usuarios no cambian).
- Administración → *Borrar todos los datos*: pide escribir BORRAR y borra en todos los equipos; los usuarios se conservan.
- Lo que cada tablet tenía antes de la v1.4.0 no se mezcla: Administración → *Datos viejos de este equipo* para descargarlo o borrarlo.
- Para las pruebas existe un modo local (`http://localhost:8765/index.html?modo=local`) que no usa la base.

## Fin de temporada (veda)

La langosta roja se pesca del 16 de septiembre al 15 de febrero. En la veda casi nadie abre la app, y el plan gratis de Supabase **pausa la base después de 7 días sin uso**.

**Desde la v1.8.0 esto se cuida solo:** Vercel llama todos los días a `api/despierta.js` (configurado en `vercel.json`, sección `crons`), que hace una consulta pequeña a la base. Con eso la base nunca pasa 7 días sin uso. No hay que hacer nada.

- **Para comprobar que corre:** Vercel → el proyecto → *Settings* → *Cron Jobs* (debe aparecer `/api/despierta`, una vez al día) y *View Logs*: cada día una llamada con respuesta 200. Una respuesta 502 quiere decir que la base no contestó.
- **Opcional:** en Vercel → *Settings* → *Environment Variables*, agrega `CRON_SECRET` con una clave larga cualquiera. Así solo Vercel puede usar esa dirección. Sin ella también funciona (la consulta no lee ni cambia datos).
- **Si algún día la base sí se pausa** (por ejemplo, si se quitó la tarea): Supabase manda un correo. Entra al panel (proyecto `propesa_bc`) y dale **Resume project**; no dejes pasar más de 90 días.
- **Tablets con Safari:** si una tablet pasa más de 7 días sin abrir la app, Safari puede borrar su copia. Los datos no se pierden (viven en la base), salvo lo que esa tablet no haya subido. Antes del 15 de febrero, revisa que Administración diga «Todo lo de este equipo ya está arriba».
- **Si cambian a su propia base de datos**, actualicen la dirección y la llave de `api/despierta.js` (las mismas de `index.html`), o quiten la tarea si su base no se pausa.

## Pruebas

Requieren Python 3 con Playwright y Chromium.

```bash
sh pruebas/correr_todo.sh      # 23 grupos; termina con «TODO BIEN»
```

Extras: `python3 -I pruebas/rendimiento_t.py` (un año de datos, tiempos de pantalla) y `node pruebas/accesibilidad.mjs pruebas/datos/backup.json` (Lighthouse en 15 pantallas, en modo local; requiere `npm i lighthouse puppeteer-core`).

## Actualizar y volver atrás

1. Antes de publicar una versión nueva, descarga un respaldo desde Administración.
2. `git push` a `main` → Vercel despliega solo. `index.html` se sirve con `Cache-Control: no-cache`, así que los equipos toman la versión nueva al recargar.
3. Si algo sale mal: en Vercel → *Deployments* → la versión anterior → **Promote to Production** (vuelta atrás inmediata). Los datos no se tocan: viven en la base compartida.

## Límites conocidos

- Los permisos finos por rol (quién edita órdenes, cierra lotes…) los aplica la pantalla; la base solo distingue «puede escribir» (Administrador, Piso) de «solo ver» (Consulta). Ver `docs/SEGURIDAD.md`.
- Las fotos viven en el espacio de archivos «fotos» de Supabase (plan gratis: 1 GB, unas 10,000 fotos). El respaldo `.json` lleva las notas pero no las fotos.
- «Enviar por correo» usa el menú de compartir del equipo o abre tu programa de correo; no hay servidor de correo.
- El logo es una recreación en SVG; para el archivo oficial, reemplaza la función `LG` en `index.html`.
- La base usa el plan gratis de Supabase: ver *Fin de temporada (veda)*.
