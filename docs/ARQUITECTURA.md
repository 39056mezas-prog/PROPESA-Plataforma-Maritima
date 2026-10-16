# ARQUITECTURA.md · Cómo está hecho el código

## 1. Panorama

| Cosa | Cómo |
|---|---|
| Archivos | **Un solo `index.html`** (~205 KB, ~1,040 líneas): HTML + CSS + JS vanilla. Sin dependencias, sin build, sin npm. |
| Datos | **Base compartida en Supabase** (v1.4.0): todos los equipos ven lo mismo. Copia en el navegador (IndexedDB, `propesa-c1`, desde la v1.6.0) para trabajar sin internet. Modo local de pruebas: `propesa-v4`. |
| Despliegue | GitHub → Vercel (Framework *Other*, sin build, se sirve la raíz). `vercel.json` pone cabeceras de seguridad y caché. |
| PWA ligera | `manifest.webmanifest` + íconos para «Agregar a pantalla de inicio». Sin service worker todavía. |
| Copia suelta | `PROPESA_Plataforma_maritima.html` = el mismo `index.html`. |

**Mantener todo en un archivo** hasta que haya backend. Si algún día se divide, que sea junto con la migración a Supabase.

## 2. Ciclo de la app

```
load() ─► ST (estado global) ─► render() ─► render0() escribe #app.innerHTML
   ▲                                         │
   └── save() ◄── manejadores (data-*) ◄─────┘   go('ruta:param') cambia V y vuelve a dibujar
```

- **`ST`**: todo el estado (ver `DATOS.md`). `save()` lo serializa completo y devuelve `true/false`; si falla, `SAVE_ERR` muestra un aviso rojo fijo (`topBanners`).
- **`me`**: usuario en sesión, **solo en memoria** (recargar cierra la sesión).
- **`V = {v, id}`**: vista actual. `go('orden:3')` → `V={v:'orden',id:'3'}`; limpia estado temporal (`msg`, `form`, `conf`, `HIST`…) y hace scroll arriba.
- **`render()`** crea los índices de dibujo (`RX`) y llama a `render0()`, que decide: sin usuarios → `setupView()`; sin sesión → `loginView()`; Modo piso → `pisoShell(...)`; si no, menú + página de `PG`.
- **Plantillas de texto**: cada página es una función que devuelve HTML (`` `...${E(x)}...` ``). **Siempre `E()` para texto del usuario.**

## 3. Rutas (`PG`) y paso del menú (`STEP`)

```js
PG = { piso, pemp, pent, inicio, recepcion, lote, empaque, empacar, embarques, emb, ordenes, orden, cierre, temperatura, admin, buscar }
STEP = { recepcion:1, lote:1, ordenes:2, orden:2, empaque:3, empacar:3, embarques:4, emb:4, cierre:5 }
```

| Ruta | Parámetro | Pantalla |
|---|---|---|
| `inicio` | — | Panel |
| `recepcion` · `lote:<lote>` | código de lote | Entrada (arriba, tablero de tanques `tanques()`) · detalle de lote |
| `ordenes` · `orden:<id>` | id de orden | Órdenes · detalle |
| `empaque` · `empacar:<orden>.<línea>` | `3.2` | Empaque · empacar un cliente |
| `embarques` · `emb:<i>` | índice en `ST.P` | Embarque · consignación |
| `cierre` | — | Mortalidad final |
| `temperatura`, `admin`, `buscar:<texto>` | | |
| `piso` · `pemp[:o.l]` · `pent` | | Modo piso: inicio, empacar, entrada |

Los nombres internos (`recepcion`, `cierre`) **no se renombran**; solo los textos visibles.

## 4. Eventos

Delegación: un manejador de clic en `document` lee atributos `data-*`; hay manejadores extra para `input`/`change`/`keydown`.

| Atributo | Para qué |
|---|---|
| `data-go="ruta"` | Navegar |
| `data-a="..."` | Acciones generales (`sv` guardar lote, `s0` crear admin, `tq` guardar temperatura, `rst` borrar datos, `lo` salir…) |
| `data-oa` | Órdenes (líneas, unir) |
| `data-pk` | Empaque en vista completa (`addall`, `ed:<seq>` reabrir caja, `ek:K` categoría al corregir, `upd`, `cancel`, `del:<seq>`/`rm:<seq>`) |
| `data-pe` | Modo piso (`all:K`, `sk:seq:K`, `cf`/`rm`; `cf`/`rm` ahora salen dentro del teclado) |
| `data-kp` | Teclado fijo de Empaque (`d:N` número, `clr` Borrar, `bk` ⌫, `k:R`/`k:V`/`k:B` categoría, `prev`/`next`). El teclado lleva `data-kpm` = `piso` o `full` (**no usar `data-mode`**: es el del interruptor de Modo piso; ese choque ya cambió de modo al tocar una categoría) |
| `data-kps` · `data-kpn` | Tarjeta de caja en Modo piso (lugar) · número de caja en cada campo de piezas |
| `data-row` | Filas de la tabla de cajas (**no usar `data-r`**: es el de «Revertir movimiento»; ese choque ya causó un bug grave) |
| `data-ev` | Fotos y notas |
| `data-zs` | Tallas del embarque |
| `data-sh` | Acciones de embarque |
| `data-fin` · `data-alive` | Conteo final por lote · vivas al llegar |
| `data-pdf="dl|mail:<tipo>:<arg>"` | PDF de cada paso |
| `data-jump` | Ir a un campo, enfocarlo y resaltarlo |
| `data-hist` · `data-histoff` | Abrir / cerrar historial de una lista |
| `data-bk="dl|up"` | Descargar / restaurar respaldo |
| `data-settings` · `data-setclose` | Abrir / cerrar Ajustes |
| `data-avatar` · `data-pm` · `data-pmclose` | Menú del perfil |
| `data-tqdel` | Eliminar lectura de temperatura (admin) |

Antes de agregar un `data-*` nuevo, busca que no exista ya con otro significado.

## 5. Mapa de funciones

| Área | Funciones |
|---|---|
| Núcleo | `load`, `seed`, `save`, `render`, `render0`, `go`, `E`, `toast`, `topBanners`, `iconize` |
| Formularios | `renderKeep`, `fail` (conservan lo escrito y marcan el campo) |
| Entrada / lotes | `recepcion`, `lote`, `lotForm`, `saveLot`, `newLotId`, `delLot`, `closeLot`, `post` (movimientos), `mv`, `rev` |
| Órdenes | `ordenes`, `orden`, `ordAssigned`, `ordCsv` (packing list CSV) |
| Empaque | `empaque`, `empacar`, `pkGrid`, `pkCnt`, `pkLive`, `pkEdLive`, `pkUpd`, `pkAnim`, `PKS`, `PKP`, `pendChip`, `goPend`/`goLine` |
| Embarque | `embarques`, `emb`, `shipFor`, `newShip`, `syncShip`, `syncShipIdx`, `shipLinks`, `moveGroup`, `dropShip`, `joinable`, `shipPanel`, `shipIssues`, `shipAlert`, `truck`, `closeP` |
| Mortalidad | `cierre`, `calc`, `donut`, `hbars` |
| Temperatura | `temperatura`, `saveTemp` |
| Panel / búsqueda | `inicio`, `nxt` (siguiente paso), `buscar` |
| Fotos y notas | `evid`, `evDraft`, `shrink` (reduce fotos) |
| Usuarios | `setupView`, `setupSave`, `loginView`, `saveU`, `admin`, `can` (sin contraseñas en la app desde la v1.4.1) |
| Respaldo | `cleanST` (limpia y valida un respaldo antes de usarlo) |
| PDF | `PdfRep` (escritor propio), `pdfEntrada`, `pdfOrdenes`, `pdfEmpaque`, `pdfEmbarque`, `pdfEmbarques`, `pdfMort`, `pdfMake`, `pdfSave`, `pdfMail`, `pdfBar` |
| Teclado de Empaque | `kpPad(mode)`, `kpSync` (después de cada dibujo de Empaque), `kpEl`/`kpOf` (caja activa ↔ campo), `kpList`, `kpFirst` (primera vacía), `kpType`, `kpCatPress`, `kpNav`, `kpLeave` (guarda al cambiar de caja si ya estaba lista), `kpGo`, `kpReveal` (deja la caja a la vista sin quedar detrás del teclado), `catLbl`, `peCv`. Estado `KPT = {k: ruta, t: 'slot:N' / 'row:R' / 'ed', fresh, sig}` (también se guarda en `propesa-ui`) |
| Modo piso | `pisoShell`, `pisoHome`, `pisoEmp`, `peSlots`, `peTry`, `peRender`, `peLine`, `pisoEnt`, `penRow`, `penTr`, `penVal`, `penSave`, `penLive`, `penJump`, `switchMode`, `setPiso` |
| Ajustes | `applyPrefs`, `savePrefs`, `settingsHTML`, `paintSettings`, `openSettings`, `closeSettings`, `syncSetBtns`, `fsSnap` |
| Menú del perfil | `avatarBtn`, `pmenuHTML`, `placePmenu`, `openPmenu`, `closePmenu`, `syncAv` |
| Listas | `histList(key, items, activoFn)` → `{items, bar}` |
| Fechas | `dLoc()` (fecha local; **no usar `toISOString()`**), `fd()` ISO → dd/mm/aaaa |

## 6. Rendimiento

Probado con un año de datos (500 lotes, 37,400 cajas, 250 órdenes y embarques) y CPU 4× más lenta (≈ tablet): Panel ~36 ms, guardar una caja en piso ~138 ms.

- **Índices de dibujo `RX`**: `render()` arma una vez por dibujo `rxLine`, `rxShip`, `rxMov`, `rxLinks`, `rxLot`, `rxRvd`; funciones como `ordAssigned`, `bal`, `calc`, `shipLinks` los usan si existen y, fuera del dibujo, calculan directo (los manejadores siempre ven datos frescos). Si agregas un cálculo que recorre todas las cajas o movimientos, **úsalo dentro de un índice**.
- **Listas activas** (`histList`, `HIST`): solo lo abierto o reciente; historial de 100 en 100.
- Pendiente: `save()` reescribe todo (~80 ms en tablet con un año). Las fotos ya no inflan los datos: desde la v1.8.0 viven en el espacio de archivos de Supabase (`SUPABASE.md` §8).

## 7. Ajustes y preferencias

- `PREF = {theme, fs}`; `applyPrefs()` pone `data-theme` en `<html>` y `--app-font-size`.
- Un script temprano en `<head>` (dentro de una IIFE para no chocar con variables de la app) aplica tema y tamaño antes de pintar.
- El panel vive en `#setp`, **fuera de `#app`**, para que abrirlo no redibuje ni borre lo capturado. Lo mismo el menú del perfil (`#pmenu`).

## 8. PDF

Escritor propio `PdfRep` (sin librerías): Helvetica con codificación WinAnsi y métricas reales, logo en JPEG, tablas con encabezado repetido, paginación. Cada paso tiene su barra (`pdfBar`) con **Descargar PDF** y **Enviar por correo**: Web Share con archivo en tablet/celular; si no existe, descarga + `mailto:` a los usuarios con «Recibe informes».

## 9. Claves en `localStorage`

| Clave | Contenido |
|---|---|
| `propesa-c1` | Solo en equipos que no han abierto la v1.6.0: copia vieja de `ST`. Al abrir, se pasa a IndexedDB (`propesa` → `kv` → `propesa-c1` = `{st, since}`) y se borra de aquí |
| `propesa-c1-since` | Igual: se pasa a IndexedDB junto con la copia y se borra |
| `propesa-out` | Cola de cambios por subir (`{clave: JSON o 'null'}`) |
| `propesa-outb` | Cómo estaba cada registro de la cola en la base antes del primer cambio (`{clave: JSON o null}`); sin clave = sube sin revisar (cola de la v1.4.0) |
| `propesa-sb` | Sesión de Supabase: `{at, rt, exp, uid}` |
| `propesa-v4` | `ST` del modo local de pruebas; en tablets viejas, sus datos de antes (no se mezclan) |
| `propesa-theme` | `light` / `dark` / sin valor (sigue al equipo) |
| `propesa-fs` | Tamaño de texto (15, 17 o 20) |
| `propesa-piso` | Preferencia de Modo piso del equipo |
| `propesa-z` | Tamaño viejo (solo se lee para migrar) |
| `propesa-ses` | Sesión abierta: `{u: id del usuario, exp}` (en la base compartida, además debe existir `propesa-sb` del mismo usuario). Vence 12 h (`SES_H`) después del último toque o tecla (`LAST_ACT`). Se borra al cerrar sesión |
| `propesa-ui` | Dónde estaba y lo que se estaba escribiendo: `V`, `form`, `uf`, `PKD`, `PE`, `PEN`, `OD`, `OA`, `HIST`, `ND` (sin fotos), scroll de `main` y `f` = valor de cada campo de `#app` (clave = `#id` o etiqueta + atributos `data-*`). Se borra al cerrar sesión |

**Recargar sin perder nada (v1.2.5):** `render()` termina con `uiSoon()` (guardado de `propesa-ui` 150 ms después); también se guarda con cada `input`/`change`/`click`/`keydown` y de inmediato en `pagehide` y `visibilitychange`. Al arrancar, `uiRestore()` revisa la sesión, recupera `me` y el estado, dibuja una vez y vuelve a poner los valores de los campos (sin disparar eventos). Si la ruta guardada ya no existe, el usuario se borró o la sesión venció, se queda en el inicio o en el acceso. Los campos de contraseña, archivos y el buscador no se guardan.

## 10. Archivos del repositorio

```
propesa-plataforma/
├── index.html              ← toda la app
├── CLAUDE.md · AGENTS.md   ← instrucciones para asistentes de IA
├── README.md · CHANGELOG.md
├── SPEC.md · tasks/plan.md ← especificación y plan del panel de Ajustes y menú del perfil
├── docs/                   ← contexto del proyecto (este archivo y los demás)
│   └── referencias/        ← formatos en papel y documentos del usuario
├── pruebas/                ← pruebas automáticas (Playwright/Python) y datos de prueba
├── supabase/               ← schema.sql (primer esquema), migrations/ (lo aplicado en propesa_bc, en orden; ver SUPABASE.md) y functions/usuarios
├── api/despierta.js        ← tarea diaria de Vercel: consulta pequeña para que Supabase no pause la base
├── vercel.json · manifest.webmanifest · íconos
└── .claude/settings.json   ← activa el plugin agent-skills en Claude Code
```

## 11. Base compartida (v1.4.0)

Todo el código está en el bloque «Base compartida (Supabase)» de `index.html`, antes de `ST=load()`.

| Pieza | Qué hace |
|---|---|
| `LOCAL` / `CLOUD` | Modo local solo en `localhost` con `?modo=local` (o `window.PROPESA_LOCAL`), para las pruebas. Todo lo demás usa la base. `window.PROPESA_SB = {url, key}` cambia el servidor (lo usan las pruebas con el Supabase de mentira) |
| `SBC` | URL del proyecto y llave **publicable** (puede ir en el código; la seguridad la dan las reglas RLS) |
| `WN`, `encodeST`, `decodeST` | `ST` ⇄ registros. Cajas con caché por lote (`ENC_C`) para que guardar sea rápido |
| `SHW` | Lo último que se sabe de cada registro (texto + objeto) |
| `syncStage()` | Compara `encodeST()` con `SHW` y anota lo cambiado en `OUT` (`propesa-out`) y, la primera vez, cómo estaba en `OUTB`. Con Consulta no anota nada: vuelve a bajar todo para regresar a lo de la base. Lo llama `save()` |
| `flush()` | Sube `OUT` en tandas a `rpc/push` (≤ 500 registros / 1.5 MB). Lo que choca (otro equipo lo cambió antes) se aplica desde la base con `applyRows()` y avisa. Si la base no tiene `push` (404), ya no sube por otro camino (v1.6.0): queda pendiente con el aviso «No se pudo subir». Si el mismo registro se cambió otra vez mientras subía, su «antes» pasa a ser lo recién subido (v1.5.1). Consulta nunca sube ni vacía la cola |
| `syncNow()` | Sube (`flush`) y baja (`pull`). Si la base rechaza lo que se sube, igual baja lo de los demás y después muestra el error (v1.4.1). `wp()` quita el carácter nulo, que la base no acepta |
| `pull()` / `applyRows()` | Baja `rpc/pull` desde `SINCE` (lo que se guardó con la copia en IndexedDB) (de 1000 en 1000). Solo avanza el número hasta lo que tiene más de 8 s (por si otro equipo estaba guardando). Lo pendiente en `OUT` gana. Rearma `ST`, conserva el embarque abierto (`emb:<i>` por su `u`) y corrige la ruta si algo se borró (`fixRoute`) |
| `syncNow`, `syncLoop`, `syncSoon` | Cada 4 s (30 s en segundo plano), al volver el internet y al regresar a la app; `save()` sube a los 250 ms. Perfiles cada 60 s |
| `softRender()` | Redibuja por cambios de otros sin borrar lo escrito (conserva los campos cambiados por el usuario); si hay un campo con el cursor, espera a que salga |
| `cacheSoon` / `cacheST` / `loadCache` | Copia en el equipo agrupada cada 1.5 s (y al salir de la app); guarda `ST` y `since` juntos en un solo registro de IndexedDB (v1.6.0). `loadCache()` la lee al arrancar (antes de entrar y de sincronizar) y pasa la copia vieja de `localStorage` si la hay. Si no se puede guardar: `CACHE_ERR` y aviso |
| `syncBanners()` | «Descargando los datos compartidos…», «Sin conexión…» (rojo si hay pendientes) |
| Fotos (v1.8.0) | `FQ` cola por subir (IndexedDB `fotos-cola`), `FC` fotos listas para mostrar, `fotoSrc`/`fImg` (src o gris + `data-fp`), `fotoLoad` (IndexedDB `F/<ruta>` o bajada con sesión), `upFotos` (sube antes que `flush`), `fotoMigra` (fotos viejas dentro de notas), `fotoDel`. `outN()` cuenta también las fotos por subir. Detalle: `SUPABASE.md` §8 |
| Acceso | `sbAuth`, `sbToken` (renueva el token solo), `sbFetch`, `cloudLogin`, `cloudSetup`, `checkSetup` (`rpc/has_admin`), `signOut`, `dropSes` |
| Usuarios | `loadProfiles()` llena `ST.U`; `fnUsers(action)` llama a la función `usuarios` (`create`, `update`, `delete`, `setup`) |
