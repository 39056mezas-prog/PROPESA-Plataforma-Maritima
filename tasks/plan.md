# Plan: Panel de Ajustes (aprobado 12/oct/2026)
Decisiones: quitar "A A A"; solo Oscuro/Claro (sin elección = sigue al equipo); inicial 15 px; preferencias por equipo.
1. Texto escalable: font-size px→rem (base 15), `html{font-size:var(--app-font-size)}`, campos ≥16px, quitar `zoom` y botones A A A, migrar `propesa-z`. Verificar: sin desbordes a 20 px.
2. Tema: `data-theme` en <html>, script temprano en <head>, `color-scheme` por tema, revisar que cada regla oscura tenga su gemela. Verificar: contraste ≥4.5:1 en ambos.
3. Panel: botón Ajustes (vista completa + piso), panel fuera de #app, segmentado Oscuro/Claro, deslizador 12–20, foco atrapado, Esc/fuera/✕. Verificar: no borra lo capturado.
4. Pruebas `pruebas/ajustes_t.py` + regresión completa; docs.
