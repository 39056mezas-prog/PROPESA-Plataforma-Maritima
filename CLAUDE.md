# CLAUDE.md · Plataforma PROPESA

Instrucciones para cualquier asistente de IA (Claude Code, Claude, Codex, Cursor…) que trabaje en este repositorio.
Léelo completo antes de tocar código. Versión actual de la app: **1.40.0** (7 de noviembre de 2026).

## Qué es

Plataforma web para **PROPESA** (Proveedor del Pescador S.A. de C.V., Ensenada, B.C.), que exporta langosta roja viva a China por avión.
Sigue cada lote por este flujo, que **no se cambia sin permiso del usuario**:

**Entrada → Órdenes → Empaque → Embarque**

## Regla principal de trabajo: plan → aprobación → pruebas (v1.39.0, pedido del usuario)

1. **Primero el plan:** antes de cambiar algo mediano o grande, di qué vas a cambiar, pantalla por pantalla, y **espera su «aprobado»**.
2. **Las pruebas cuestan tiempo:** no corras pruebas antes de que apruebe. Mientras construyes, corre **solo las de lo que tocaste**: `sh pruebas/correr_todo.sh ajustes_t menu_t …`. La corrida completa va **una vez al final**.
3. Si el usuario pide algo a media ronda, se suma al plan sin volver a empezar.

## Ley de Hick y Ley de Fitts (v1.39.0, «actualización Ley de Hick», pedida por el usuario) · aplica a TODA pantalla nueva o cambiada

Lo que el usuario quiere evitar: pantallas llenas, no poder regresar, quedar bloqueado sin poder editar, pantallas sin fin, menús dentro de menús, el botón importante escondido.

**Hick (menos opciones a la vista = decide más rápido):**
- **Una acción principal por pantalla** (azul, `.btn`), arriba en el encabezado (`guide()`); lo demás discreto (`.btn.q`) o plegado (`fold()`).
- **Agrupa y acorta:** máximo ~7 opciones juntas; si hay más, en grupos o pestañas. Nada de menús anidados: todo a un toque desde su pantalla.
- **Siempre se puede regresar:** «‹ Atrás» en la barra (`bkBtn()`/`goBack()`); regresa con lo escrito y el lugar de la pantalla (`SNAP`). No pongas «‹ Volver a…» dentro de la página.
- **Nunca bloquear:** si algo no se puede editar, la pantalla dice por qué y lleva al paso que lo arregla (ej. lote sin entrada → tarjeta `#nejoin` con «Crear su entrada» / «Conectar»).
- **Sin avisos de más:** los pendientes van en la campana; el Centro de operaciones no los repite (el usuario lo pidió).
- **Pantallas con fin:** lo de consulta va plegado al final; listas cortas con «Ver historial».

**Fitts (botones grandes y a la mano; video que compartió el usuario):**
1. La acción principal es grande (≥ 48 px; en Modo piso ~60) para tocarla sin mirar.
2. En tablet y celular la acción principal de la pantalla va abajo, donde están los pulgares: clase `.btn.thumb` (fija abajo; en celular a todo lo ancho).
3. En una lista **toda la fila se toca** (`<tr data-row="pantalla:id">`); los botones de la fila siguen funcionando.
4. **Eliminar lejos de guardar:** `.btn.dq` (texto rojo con bote de basura, sin fondo, al final de la fila de acciones); confirmar dice qué se borra («¿Eliminar el lote X?» → «Sí, eliminar lote» / «No»).
5. Lo que más se toca es lo más grande y lo más cerca.

**Herramienta, no asistente (v1.33.0, decidido por el usuario):** el flujo dice cómo se conectan los datos, no en qué orden se captura. **Desde la v1.39.0 la vista completa abre en el «Centro de operaciones»** (Panel + Formatos juntos, **centro de mando, no otro menú**: 4 números que se tocan → planta 3D → plegados; **sin cuadrícula de accesos a los módulos** (para eso está el menú) **ni lista de avisos** (para eso está la campana); el logo siempre lleva ahí; la maquila se cambia con su propio botón «PROPESA ▾»); el menú no lleva números ni «Siguiente paso». No vuelvas a forzar empezar por la Entrada.

**Pantallas limpias (v1.34.0, decidido por el usuario):** cada sección abre con `guide()` = título, una línea y la acción principal arriba; PDF y correo son botones discretos (`.btn.q`). Lo secundario va en `fold()` (plegable que recuerda si quedó abierto). No vuelvas a poner recuadros azules de explicación ni tarjetas «Archivo de este paso».

**Detalles ordenados (v1.35.0, decidido por el usuario):** en Orden, Embarque y Lote primero va lo que se hace o se corrige; PDF/correo/eliminar en el encabezado; formularios largos que no siempre tocan (Hoja de empaque, indicaciones, pesos, temperatura del lote) plegados con su estado en el renglón, y los avisos rojos abren el plegable. Administración va en pestañas (`ADT`, `go('admin:cat')`).

**Textos de formularios (v1.36.0, aprobado por el usuario):** el error de un campo va **junto al campo** con `fail(texto, idDelCampo)` (o `ferShow(id, texto)` sin redibujar); nunca en un aviso flotante que se va ni repetido en otro formulario. Una talla se llama «Chica · 491-610» en pantalla (`szNR(i)`, `szLb(i)`); los rangos del papel solo en el PDF. El tanque se llama «T1». Nada peligroso viene elegido (tipo de movimiento, rol, a. m./p. m.). Ejemplos con «Ej.».

**iPad viejo (v1.37.0, pedido del usuario):** se usa sobre todo en un iPad mini viejo; tiene que correr desde **iOS 12 (Safari 12)**. En el JavaScript **no uses `??` ni `?.`** (deja la app en blanco en iOS 12–13; usa `(a!=null?a:b)`) ni `.at()`, `replaceAll`, `structuredClone`, `dateStyle`; las descargas van con `saveBlob()`. En el CSS, **cada `color-mix()` lleva antes un color fijo `var(--cm-…)`**, nada de `inset:` y `position:sticky` con `-webkit-sticky`. `@container`, `:has`, `:is`, `:focus-visible`, `clamp()` y `gap` sí se pueden usar: la capa `CPX` los resuelve en el iPad viejo (ver `docs/ARQUITECTURA.md` → «iPad viejo»). `pruebas/ipad_viejo_t.py` lo revisa.

**Maquilas (v1.19.0):** cada maquila (PROPESA, Abel, David, Luis Arce) guarda aparte sus datos; `ST` es la maquila abierta y `STX` las demás (ver `docs/DATOS.md`). Todo lo nuevo que sea de la operación va dentro de la maquila; lo de la empresa o lo físico (usuarios, proveedores, consignatarios, tanques) se comparte en `SHF`. **Desde la v1.40.0 las maquilas están fuera del programa** (usuario: «no agregar ni quitar maquilas»): no hay pestaña Maquilas ni botones para agregarlas, ocultarlas o renombrarlas; se dan de alta a mano en la base (`docs/SUPABASE.md` §10). No los vuelvas a poner.

**Eliminar en Catálogos (v1.40.0, aprobado por el usuario):** tallas, proveedores, especies, consignatarios y destinos se pueden eliminar **solo si nunca se usaron en ninguna maquila** (`cdUse`); si ya se usaron, la confirmación dice en qué y ofrece «Ocultar». Tallas y consignatarios van por posición: al borrar uno, `cdDel` recorre lo guardado detrás (z de líneas y embarques; `cons`, `sh`, `_sh` y `ST.CC` en todas las maquilas). Si agregas otro dato guardado por posición de talla o consignatario, agrégalo también a `cdUse` y `cdDel`.

**Mortalidad final va aparte** (decidido por el usuario el 16/oct/2026): no es un paso del flujo; se calcula sola con el conteo final de cada lote y las vivas al llegar de cada envío, y se revisa cuando se necesite (menú → «Revisión»).

La usan en tablet personas de piso con poca experiencia técnica (manos mojadas, guantes, poca luz), y también se consulta en computadora y celular.

## Cómo hablar con el usuario

- **Siempre en español**, tuteando, con palabras sencillas. El usuario escribe en español con algo de inglés; contesta en español.
- No es programador: explica resultados, no código. Nada de jerga (`localStorage`, `render`) en lo que le dices, salvo que él la use.
- Mensajes cortos: qué cambió y qué sigue.

## Lee esto en este orden

| Archivo | Para qué |
|---|---|
| `docs/PRODUCTO.md` | El negocio: flujo, glosario, reglas, roles. **Empieza aquí.** |
| `docs/UX.md` | Cómo debe sentirse la app: principios, Modo piso, avisos, lo que el usuario pidió y lo que rechazó |
| `docs/BRAND.md` | Colores, logo, tipografía, íconos, colores de talla y categoría |
| `docs/ARQUITECTURA.md` | Cómo está hecho el código: rutas, eventos, funciones, rendimiento, PDF |
| `docs/DATOS.md` | Modelo de datos `ST`, migraciones, respaldo |
| `docs/DECISIONES.md` | Decisiones tomadas y por qué (no las deshagas sin preguntar) |
| `docs/ROADMAP.md` | Preguntas abiertas y lo que sigue |
| `docs/PRUEBAS.md` · `docs/SEGURIDAD.md` · `docs/SUPABASE.md` | Calidad, seguridad y la base compartida (Supabase, conectada desde la v1.4.0) |
| `docs/FLUJO_DE_TRABAJO.md` | Cómo trabajar: un cambio a la vez, comandos del plugin agent-skills, publicar |
| `docs/HISTORIAL.md` | Bitácora completa, ronda por ronda |
| `docs/referencias/` | Formatos en papel (PDF) y documentos que el usuario compartió |

`index.html` es **la fuente de verdad**. Si un documento contradice el código, gana el código: corrige el documento.

## Reglas que no se rompen

1. **No cambies el flujo, los textos de pantalla, ni el layout** sin confirmarlo con el usuario. Mejora; no rediseñes.
2. **Un cambio a la vez**, con su prueba, y avisa qué cambió.
3. **No inventes reglas de negocio.** Si falta un dato, pregunta (ver `docs/ROADMAP.md` → Preguntas abiertas).
4. **La app ya usa Supabase** (proyecto `propesa_bc`, ver `docs/SUPABASE.md`): todos los equipos comparten los datos. **No cambies el esquema, las reglas de seguridad ni la función `usuarios` sin preguntar**, y no conectes otras cuentas del usuario (correo, Drive…) sin que lo pida. Las pruebas nunca tocan la base real: usan `pruebas/supabase_falso.py` o el modo local.
5. **Sin dependencias ni paso de compilación.** Todo vive en `index.html` (HTML + CSS + JS vanilla, la conexión con Supabase está hecha a mano con `fetch`). Las únicas excepciones son `api/despierta.js`, la tarea diaria de Vercel que mantiene despierta la base, y `sw.js`, el service worker mínimo que deja instalar la app (v1.12.0); ninguno usa librerías. Nada de CDN ni fuentes externas; el único dominio externo permitido en la CSP es el de Supabase.
6. **Escapa todo texto del usuario con `E()`** antes de meterlo en HTML.
7. **Cualquier cambio a la estructura de `ST` lleva migración**, su limpieza en `cleanST()` **y su lugar en `WN` / `encodeST` / `decodeST`** (lo que no esté ahí no se comparte entre equipos). Los ids nuevos se hacen con `uidN()` / `uidS()`, nunca con contadores ni `max+1`.
8. **No borres lo que el usuario escribió** cuando hay un error (`renderKeep` / `fail`).
9. **Los avisos rojos siempre llevan a donde se resuelven** (botón o chip con destino).
10. **Accesibilidad:** objetivos táctiles de 44 px o más (48 px en botones, ~60 px en Modo piso), contraste AA, foco visible, campos de captura de 16 px o más.
11. Nada de rastros de demo: no metas usuarios, contraseñas o datos de ejemplo en la app. Los datos de prueba viven solo en `pruebas/`.
12. Después de cada sesión, actualiza `CHANGELOG.md`, `docs/HISTORIAL.md` y el documento de `docs/` que corresponda.

## Comandos

```bash
python3 -m http.server 8765                 # servir en http://localhost:8765
sh pruebas/correr_todo.sh                   # TODAS las pruebas (*_t.py + e2e), en paralelo; debe terminar en «TODO BIEN». Solo al final de la ronda
sh pruebas/correr_todo.sh hick_t menu_t     # solo las de lo que tocaste (lo normal mientras construyes)
J=1 sh pruebas/correr_todo.sh               # una por una (si el equipo es lento)
python3 -I pruebas/rendimiento_t.py         # rendimiento con un año de datos
node pruebas/accesibilidad.mjs pruebas/datos/backup.json   # Lighthouse (npm i lighthouse puppeteer-core)
```

Revisar la sintaxis del JavaScript sin navegador:

```bash
node -e "const s=require('fs').readFileSync('index.html','utf8');const re=/<script>([\s\S]*?)<\/script>/g;let m;while(m=re.exec(s))new Function(m[1]);console.log('ok')"
```

Las pruebas usan Python 3 + Playwright con Chromium. Si `correr_todo.sh` ya levantó un servidor en el 8765, no lo mates con `pkill -f "http.server 8765"` desde la misma línea de comando: el patrón coincide con tu propia shell.

## Antes de dar algo por terminado

- [ ] Plan aprobado por el usuario antes de probar; pruebas de lo tocado durante la ronda y `sh pruebas/correr_todo.sh` → TODO BIEN una vez al final (agrega pruebas para lo nuevo; un archivo `*_t.py` nuevo entra solo a la corrida).
- [ ] Revisado en 390, 768 (iPad mini), 820 y 1440 px, y con texto «Muy grande» (20 px): sin desbordes.
- [ ] `ipad_viejo_t.py` en TODO BIEN (se ve y funciona igual en el iPad viejo).
- [ ] Tema claro y oscuro.
- [ ] Sin errores en consola; sin violaciones de la CSP.
- [ ] Documentación y `CHANGELOG.md` al día; versión subida si aplica (constante `APPV` en `index.html`: la usan el menú del perfil y Administración).

## Entregables de cada ronda

El usuario descarga un zip y lo sube él mismo a GitHub; Vercel publica desde `main`. Entrega siempre:
`propesa-plataforma.zip` (esta carpeta completa, sin `__pycache__`), `PROPESA_Plataforma_maritima.html` (copia de `index.html`) y, si cambió, el manual de usuario.
