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
| `cierre` | — (sección «Revisión», no es paso) | Mortalidad final |
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
| Embarque | `embarques`, `emb`, `shipFor`, `newShip`, `syncShip`, `syncShipIdx`, `shipLinks`, `moveGroup`, `dropShip`, `joinable`, `shipPanel`, `shipIssues`, `shipAlert`, `truck`, `closeP`; camiones (v1.14.0): `trucks`, `truckPlan(tk)`, `tFill`, `tFix`, `tIss`, `truckCard`, `bpCard` |
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
| `propesa-nt-<id>` | Notificaciones vistas por ese usuario (v1.26.0): `{t: ms de «Marcar todo como visto», k: claves tocadas ('R:<lote>', 'O:<orden>', 'C:<informe>')}` |
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
| Temperatura conectada (v1.8.4) | `tempAll()` junta `ST.T` (lecturas) con las temperaturas de cada entrada de `ST.R` (`src:'ent'`, se calculan, no se copian). La usan Temperatura (filtro `TFIL`, ruta `temperatura:<tanque>`), el tablero de tanques (`ult`) y la tarjeta «Temperatura del tanque desde la entrada» del lote |
| Borrar todos los datos | **No existe** desde la v1.8.5 (se quitaron `advCard`, `rstAll` y `data-a=rst`). Solo a mano desde Supabase: `SUPABASE.md` §9 |
| Teclado de la app en táctiles (v1.8.9) | `KPRO()` (`hover: none` y `pointer: coarse`) → `kpro()` agrega `readonly` a `.pkc`/`.pke` (con `KPON`) y `.ppc`/`.psc`, para que el teclado del sistema no se abra cuando el código mueve el foco |
| Editar orden (v1.8.8) | En `orden()`: `data-oa` `ee`/`se` (fecha, `OA.etd`) y `el:<id>`/`sl:<id>` (cliente y cajas por línea, `OA.ed`); `se` → `syncShipIdx`, `sl` → `syncShip`. Solo `can('lot')` |
| Peso estándar de la caja (v1.8.7) | `ST.W` / `W0`, `pesoStd()`, `pesosSync()` (en cada `render()`: `KGN`, `KGB`), `stdC(h)` para `p.c` en `syncShipIdx`. Se edita solo en Embarque: «Editar pesos» (`data-a=ewp`, `EWP`) abre `pwPanel()` (`data-a=pw`, total en vivo `#pw_n`/`#pw_tt`); `pwfix:<i>`. Desde la v1.13.3 ya no hay tarjeta en Administración ni ruta `admin:pesos`. Registro `W/pesos` |
| Pantalla de carga (v1.8.6) | `#boot` en el HTML (logo fijo, antes que `#app`; su CSS al principio del `<style>`). `boot()` = `boot0()` + `bootDone()` (desvanece y borra; mínimo 0.5 s en la app instalada) |
| Botón de atrás (v1.8.1) | `navSync()` (al final de `render()`) guarda `[pantalla, dato, Modo piso]` en el historial del navegador; `popstate` cierra primero lo que está encima (`navOverlay`) y si no, regresa a la pantalla anterior (limpia como `go()` y pasa por `fixRoute()`). La dirección no cambia |
| Fotos (v1.8.0) | `FQ` cola por subir (IndexedDB `fotos-cola`), `FC` fotos listas para mostrar, `fotoSrc`/`fImg` (src o gris + `data-fp`), `fotoLoad` (IndexedDB `F/<ruta>` o bajada con sesión), `upFotos` (sube antes que `flush`), `fotoMigra` (fotos viejas dentro de notas), `fotoDel`. `outN()` cuenta también las fotos por subir. Detalle: `SUPABASE.md` §8 |
| Acceso | `sbAuth`, `sbToken` (renueva el token solo), `sbFetch`, `cloudLogin`, `cloudSetup`, `checkSetup` (`rpc/has_admin`), `signOut`, `dropSes` |
| Usuarios | `loadProfiles()` llena `ST.U`; `fnUsers(action)` llama a la función `usuarios` (`create`, `update`, `delete`, `setup`) |

## 12. Maquilas, tallas y hojas para imprimir (v1.19.0)

| Pieza | Qué hace |
|---|---|
| `MQ`, `STX`, `mqSet(id)` | Maquila abierta (`ST`) y las demás (`STX`). `mqSet` pasa lo compartido (`SHF`), guarda los borradores de la que se deja (`DRX`) y llama `stSync()` |
| `withST(st, fn)` | Corre `fn` con otra maquila como si fuera `ST` (índices `RX` nuevos, tallas de esa maquila); lo usan el Panel general (`mqStats`), el menú del logo (`mqKg`) y `encodeAll` |
| `encodeAll()` / `mqParts(src)` | Todas las maquilas ⇄ registros. La activa se codifica en cada guardado; las demás solo cuando cambian (`ENC_X`). Prefijo `q<id>:` excepto la maquila 1 |
| `stSync()` = `cnSync()` + `szSync()` | Consignatarios/destinos (`CONS`, `PORTS`) y tallas (`S`, `RC`, `TKEY`, `TNM`, `SZC`, `SON`… y el CSS `#szcss`) de lo que está abierto. Se llama en `render()`, al cambiar de maquila, al recibir cambios y al restaurar |
| `mqLogo(cls)` · `#mqmenu` | Botón del logo (menú y Modo piso) y su menú «Cambiar de maquila» (`data-mq`, `data-mqgo`). En otra maquila muestra su nombre (`.mqnm`) en lugar del logo |
| Rutas nuevas | `general` (Panel general, solo Administrador, a donde entra: `home0()`), `hojas` (Hojas para imprimir) |
| Administración | `mqCard` (`data-mqa`), `szCard` (`data-sza`), `consCard` (`data-cna`, `data-cnp`), `destCard` (`data-dsa`) |
| Lote | Movimientos con `MVO`/`mvL`/`L.nt`; `prCard`/`prSave` (`data-a=prs`) |
| Embarque | `data-mc`, `data-ta` (% del cliente y temperatura de arribo; se redibuja con `setTimeout` para no chocar con el `blur`) |
| PDF | `pdfHRec`, `pdfHEnv`, `pdfHExi`, `pdfHCon`, `pdfHPre`, `pdfHBal` (claves `hrec`… en `pdfMake`; argumento `desde|hasta|existencia física`). `PdfRep` agrega «Maquila <nombre>» al subtítulo y `pdfName` al archivo |
| Tanques en 3D (v1.31.0) | `t3View(all)` arriba de `tanques()` (Entrada) y `tanquesGen()` (Panel general). `T3P` planta fija (posición de tanques y filtros), `T3` cámara (`az`, `ax`, `s`, `px`, `py`, `ox`, `oy`) y estado (`zoom`, `pick`, `on` = `localStorage['propesa-3d']`). `t3Data` → `t3Crates` → `t3Inner` (piezas con transformaciones 3D de CSS; solo los lados que ve la cámara, `t3Q`). Letreros en `.t3lab` (capa plana) con `t3Proj`. Cámara animada con `t3Go` (rAF), no con transición de CSS. `t3Mount` corre después de cada render (microtarea) y reusa `T3.node` si la escena no cambió. Eventos: `data-t3t` (agua), `data-t3c` (canasta), `data-t3a` (botones); arrastre con `pointerdown/move/up` en `document` |
| Tanques | `tqDist`, `tqShare`, `tqOf`, `tqTxt`, `recTk`/`recTT`/`recKB` (entrada en dos tanques); `tqCard`/`tqMove` (`data-a=tqmv`), `data-tqx` deshacer (no confundir con `data-tqdel`, que borra lecturas de temperatura) |
| Precio | `WN.$` y el registro `$/<lote>`; `decodeST` lo une a su lote |

## 13. Avisos y especie de la orden (v1.20.0)

- `lotDt(lote)` lee la fecha del código (WLR + clave + ddmmyy); `lotWarn(r)` da los avisos del lote (fecha y hora de madrugada) sin los aceptados en `r.av`. `lotWarnBox(r)` los pinta en el lote (con `data-a="el"` y `data-av="<lote>|<clave>"`); `lotWarnBan()` en Entrada.
- `salidaAuto(p, x)` descuenta lo que puede y deja el resto en `p.sf`; `shipIssues` lo muestra como «Salida incompleta» y `shipAlert` pone «Volver a descontar del tanque» (`data-sfa="<p.u>"`), que quita los movimientos `E/<p.u>` y vuelve a llamar `salidaAuto`. `shipActive` deja a la vista los cerrados con `sf`.
- `ordSp(o)` / `ordEs(o)` = especie de la orden; `ordLots(o)` = lotes abiertos de esa especie (empacar, `pkAuto`, «agregar todas», encabezado y Modo piso). `neSave` y el lote «sin lote» toman la especie de la orden. `spMany()` decide si se ve el selector. `dispCalc` resta lo pedido de su especie (`su` = sin talla).

## 14. Lotes por envío y paso a paso en Modo piso (v1.21.0)

- `shipByLot(i)` agrupa las hieleras del embarque por lote: `{l, h (hieleras), c (langostas), g (gramos de producto, lnKp de su línea), z (langostas por talla)}`. La usan `lotsInShip(i)` (tabla «Por lote» del embarque, `#emb_lotes`), `pdfEmbarque` (sección «Por lote») y el informe por correo de `closeP`. `lzTxt(z)` = texto por talla. No guarda nada nuevo.
- Rutas de Modo piso `pcer[:p.u]` → `pisoCer` y `pcon[:lote]` → `pisoCon`. El estado del paso vive en `PCE={u,s}` y `PCO={lot,s,kg,er}` (no se guarda). Botones `data-pce` (1, 2, 3, `cerrar` → `closeP`) y `data-pco` (1, 2, `guardar`); `pcoNext()` valida igual que `data-fin`. `pStep`/`pNav` pintan el encabezado y la barra Atrás/Siguiente (`.pnav`).
- `modeDest`: embarques/emb abierto ↔ `pcer`, cierre/lote abierto ↔ `pcon`. `fixRoute` regresa a la lista si el embarque o lote ya no existe. En la vista completa, `pcer`/`pcon` caen a Embarque / Mortalidad final.
- La regla `.cli` de la pantalla de compradores ahora es `div.cli`: pintaba un fondo azul detrás del código del lote o cliente en las tarjetas grandes de Modo piso.

## 15. PDF a color por talla (v1.22.0)

- `R.tallas()` dibuja la leyenda (tarjeta por talla visible de `szAll()`: color, nombre, `szGr(r)`, nombre del color; con «Maquila X» fuera de PROPESA). Se llama antes de los `stats` de cada PDF con tallas.
- En `R.table`, una columna con `zc:'#color'` lleva el encabezado de ese color (texto `fgOn`, borde gris si es claro) y la columna teñida con `pdfTint(color, .22/.30)` (total `.45`). Las celdas aceptan `bg`. Las columnas de talla usan `zc:ZBG[i]`; las de categoría `zc:RC[k][1]`.
- `szGr(r)` = gramaje: «491-610 g», «1221-UP g»; un rango que no es de números (p. ej. «26-32 piezas») se deja igual.
- v1.23.0: `PdfRep` ya no mete «Maquila X» en el subtítulo; `head()` dibuja en la primera página una banda azul marino con «MAQUILA» y `mqName(MQ)` en mayúsculas (20 pt, se achica si no cabe) y en las demás una etiqueta «MAQUILA X» arriba a la derecha.

## 16. Logotipo de maquila, llegada en Revisión, faltantes, juntar/separar y colores (v1.24.0)

- **Maquilas:** `mqCol(id)` (paleta `MQC`, PROPESA = cian), `mqIni(n)` (iniciales), `mqBadge(id)` (SVG: hexágono, círculo o escudo según `(id+1)%3`), `mqLT(id)` (logotipo del menú y Modo piso) y `mqTag(id)` (emblema + nombre en listas). Se calculan del id: no hay nada nuevo en `ST`. `.sb.mqa`, `.phd.mqa` y `.hd.mqa` llevan la franja `--mq`; `.hmq` es el emblema de la barra en celular (abre el mismo menú, `data-mq`).
- **Colores:** `consColor(i)` = `ST.CC[i]` o `XC[i % XC.length]` (lo que enseña Administración). `pCol(p)` lo toma del consignatario de la primera orden del embarque al dibujar (`shipCC`); `p.col` queda solo para embarques sin órdenes. `syncShipIdx` también guarda `p.col = consColor`.
- **Llegada:** `envCli()` en `cierre()` es la captura (`data-alive`, `data-mc`, `data-tar`), un renglón por envío con hieleras o cerrado (últimos 30). `emb()` solo pinta `.arrn` con «Ir a Mortalidad final ›» (`data-go` + `data-jumpto`, que baja hasta la tarjeta).
- **Faltantes:** `lnFalta(o,l)` → `{f, z:[[talla, faltan]]}`; `faltaLn`, `faltaOrd` y `ordFalta(o)` (tarjeta `#ord_falta`).
- **Juntar/separar:** `ordsInShip(i)` (`#ordship`) con `data-shq="ask:join|sep:<orden>:<ciudad|consignatario>:<u del embarque>"`; `SHQ` = pregunta abierta (`shAsk` pinta Ahora → Así queda), `ok` llama `moveGroup`, `SHD` = último cambio con `undo:{oid,k,to}` (`shDone`). Se olvidan al salir de Embarque (`render`). `shipPanel` (orden) solo informa y lleva al embarque. Ya no existe `data-sh`.

## 17. Camiones en pestañas y notificaciones (v1.26.0)
- **Pestañas:** `embarques()` pinta `.ttabs` (`role=tablist`, `data-ttab=<tk>`, `#ttab_N`) solo con 2+ camiones; `TTAB` = camión que se ve (`tTab()` cae al primero si ya no existe). Dentro de `#tpanel`: PDF del camión (`pdfBar('embs', tk)`), indicaciones, `truckCard(tk)` y sus consignaciones abiertas. «Camión nuevo» (`data-tk` = `+`) pone `TTAB` en el nuevo. Flechas/Inicio/Fin cambian de pestaña.
- **PDF:** `pdfEmbarques(tk)`: con un camión, el de siempre (todos los embarques); con 2+, solo ese camión y sus embarques abiertos (`Plan_de_carga_Camion_N`).
- **Notificaciones:** `ntBtn(dk)` (campana + `.ntc`) en `.hd .usr` y en `pisoShell`; panel en `#ntmenu` (`ntHTML`, `placeNt`, `openNt`/`closeNt`, Escape y «atrás» lo cierran). `ntFalta()` = `{ti, tx, go, jump}` de `lotWarn`, existencia negativa, `pendLines`, órdenes sin líneas, `shipIssues` y embarques listos para cerrar. `ntRecent()` = `{k, t, c:'n'|'d', …}` de 7 días: entradas (hora = id del primer `RECEPCION`), órdenes (`o.id`) y embarques cerrados (`ST.O[].u`). Tocar (`data-ntgo`) marca visto (`data-ntk`), cierra y hace `go()`; `data-ntj` baja a la parte de la pantalla. Todo se calcula al dibujar: nada nuevo en `ST`.

## 18. Lo más viejo primero, días por proveedor, orden variada y 35 por hielera (v1.27.0)
- **Edad del lote:** `lotDays(r)` = días entre `r.rdate` y hoy (`dLoc`); `lotDue(l)` = `{d, dm, st}` con `dm` = `pv.dm` del proveedor (`pvMatch`) y `st` `'v'` (pasó) / `'u'` (último día) / `''`. `lotOld(l)` = texto del aviso rojo (solo si pasó y tiene kilos); va en `lote()` y en `ntFalta()`.
- **Orden:** `fifo(lotes)` = primero los que pasaron o están en su último día, luego por fecha y hora de entrada; los «sin entrada» al final. `ordLots(o)` lo usa (propios y de otras maquilas por separado), así que la vista completa, Modo piso y `zAuto` ven el mismo orden. `lot1(op)` = único lote propio o el primero con kilos (queda elegido en la vista completa; en Modo piso se sigue preguntando si hay varios, `pisoEmp`). `lotTag(x, primero)` pinta «Más viejo · usar primero», «Último día en tanque» o «⚠ N días · aguanta D».
- **Orden variada:** `zAuto(o, n, kp)` reparte n hieleras de kp kg recorriendo `ordLots(o)` (propios, con entrada) y las tallas de la orden (sin despatada); antes descuenta lo que otras órdenes pidieron por talla y no han empacado (`lnPz`). Devuelve `{z, falta}`. Botón `data-oa="za:ol|le"` en `lnForm`: lee el formulario (`lnRead`), llena `D.z` y vuelve a dibujar; no guarda hasta «Agregar» / «Guardar».
- **35 por hielera:** `PZMAX`/`PZMSG`; se revisa en `pkAuto`, `pkUpd`, «Guardar hieleras», `peTry`, y la corrección en piso (`.psc` y `kpCatPress`); el teclado deja escribir y avisa al guardar.
