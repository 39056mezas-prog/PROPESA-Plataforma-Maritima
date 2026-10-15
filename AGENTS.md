# AGENTS.md

Las instrucciones para asistentes de IA de este proyecto están en **[CLAUDE.md](CLAUDE.md)**: léelo completo antes de trabajar. Aplican a cualquier herramienta (Codex, Cursor, Copilot, Gemini…), no solo a Claude.

Resumen mínimo:
- Proyecto: plataforma de PROPESA para langosta viva, flujo **Entrada → Órdenes → Empaque → Embarque → Mortalidad final**.
- Todo está en `index.html` (HTML + CSS + JS vanilla, sin dependencias). El código es la fuente de verdad. Los datos se comparten en Supabase (`docs/SUPABASE.md`).
- Habla con el usuario en español, sin jerga. Un cambio a la vez, con prueba (`sh pruebas/correr_todo.sh`).
- No cambies flujo, textos ni layout sin preguntar. No cambies el esquema ni las reglas de Supabase sin preguntar, y no conectes otras cuentas del usuario. Las pruebas no tocan la base real.
- Contexto completo en `docs/`.
