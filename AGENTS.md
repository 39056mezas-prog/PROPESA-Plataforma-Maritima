# AGENTS.md

Las instrucciones para asistentes de IA de este proyecto están en **[CLAUDE.md](CLAUDE.md)**: léelo completo antes de trabajar. Aplican a cualquier herramienta (Codex, Cursor, Copilot, Gemini…), no solo a Claude.

Resumen mínimo:
- Proyecto: plataforma de PROPESA para langosta viva, flujo **Entrada → Órdenes → Empaque → Embarque → Mortalidad final**.
- Todo está en `index.html` (HTML + CSS + JS vanilla, sin dependencias). El código es la fuente de verdad.
- Habla con el usuario en español, sin jerga. Un cambio a la vez, con prueba (`sh pruebas/correr_todo.sh`).
- No cambies flujo, textos ni layout sin preguntar. No conectes Supabase ni cuentas del usuario.
- Contexto completo en `docs/`.
