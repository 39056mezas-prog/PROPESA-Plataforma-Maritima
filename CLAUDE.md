# CLAUDE.md · Plataforma PROPESA

Instrucciones para cualquier asistente de IA (Claude Code, Claude, Codex, Cursor…) que trabaje en este repositorio.
Léelo completo antes de tocar código. Versión actual de la app: **1.9.0** (17 de octubre de 2026).

## Qué es

Plataforma web para **PROPESA** (Proveedor del Pescador S.A. de C.V., Ensenada, B.C.), que exporta langosta roja viva a China por avión.
Sigue cada lote por este flujo, que **no se cambia sin permiso del usuario**:

**Entrada → Órdenes → Empaque → Embarque**

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
5. **Sin dependencias ni paso de compilación.** Todo vive en `index.html` (HTML + CSS + JS vanilla, la conexión con Supabase está hecha a mano con `fetch`). La única excepción es `api/despierta.js`, la tarea diaria de Vercel que mantiene despierta la base (tampoco usa librerías). Nada de CDN ni fuentes externas; el único dominio externo permitido en la CSP es el de Supabase.
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
sh pruebas/correr_todo.sh                   # 32 grupos de pruebas, debe terminar en «TODO BIEN»
python3 -I pruebas/rendimiento_t.py         # rendimiento con un año de datos
node pruebas/accesibilidad.mjs pruebas/datos/backup.json   # Lighthouse (npm i lighthouse puppeteer-core)
```

Revisar la sintaxis del JavaScript sin navegador:

```bash
node -e "const s=require('fs').readFileSync('index.html','utf8');const re=/<script>([\s\S]*?)<\/script>/g;let m;while(m=re.exec(s))new Function(m[1]);console.log('ok')"
```

Las pruebas usan Python 3 + Playwright con Chromium. Si `correr_todo.sh` ya levantó un servidor en el 8765, no lo mates con `pkill -f "http.server 8765"` desde la misma línea de comando: el patrón coincide con tu propia shell.

## Antes de dar algo por terminado

- [ ] `sh pruebas/correr_todo.sh` → TODO BIEN (agrega pruebas para lo nuevo).
- [ ] Revisado en 390, 820 y 1440 px, y con texto «Muy grande» (20 px): sin desbordes.
- [ ] Tema claro y oscuro.
- [ ] Sin errores en consola; sin violaciones de la CSP.
- [ ] Documentación y `CHANGELOG.md` al día; versión subida si aplica (constante `APPV` en `index.html`: la usan el menú del perfil y Administración).

## Entregables de cada ronda

El usuario descarga un zip y lo sube él mismo a GitHub; Vercel publica desde `main`. Entrega siempre:
`propesa-plataforma.zip` (esta carpeta completa, sin `__pycache__`), `PROPESA_Plataforma_maritima.html` (copia de `index.html`) y, si cambió, el manual de usuario.
