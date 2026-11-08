# AGENTS.md

Las instrucciones para asistentes de IA de este proyecto están en **[CLAUDE.md](CLAUDE.md)**: léelo completo antes de trabajar. Aplican a cualquier herramienta (Codex, Cursor, Copilot, Gemini…), no solo a Claude.

Resumen mínimo:
- Proyecto: plataforma de PROPESA para langosta viva, flujo **Entrada → Órdenes → Empaque → Embarque**; Mortalidad final se calcula sola y se revisa aparte (16/oct/2026).
- Todo está en `index.html` (HTML + CSS + JS vanilla, sin dependencias). El código es la fuente de verdad. Los datos se comparten en Supabase (`docs/SUPABASE.md`).
- Habla con el usuario en español, sin jerga. Un cambio a la vez, con prueba (`sh pruebas/correr_todo.sh`).
- No cambies flujo, textos ni layout sin preguntar. No cambies el esquema ni las reglas de Supabase sin preguntar, y no conectes otras cuentas del usuario. Las pruebas no tocan la base real.
- Tiene que correr en un **iPad mini viejo (iOS 12)**: nada de `??` ni `?.` en el JavaScript y cada `color-mix()` con su color fijo antes (ver CLAUDE.md → «iPad viejo»).
- **Plan → aprobación → pruebas:** presenta el plan y espera «aprobado» antes de correr pruebas; durante la ronda solo las de lo que tocaste (`sh pruebas/correr_todo.sh archivo_t …`), la completa una vez al final.
- **Ley de Hick y Ley de Fitts** en toda pantalla: una acción principal grande (abajo en tablet/celular, `.btn.thumb`), «‹ Atrás» siempre, nada bloqueado sin decir cómo arreglarlo, sin menús anidados, filas completas que se tocan, eliminar discreto y lejos de guardar. Detalle en CLAUDE.md.
- Contexto completo en `docs/`.
