# FLUJO_DE_TRABAJO.md · Cómo seguir construyendo

## 1. Empezar una conversación nueva

1. Abre Claude Code (o Claude con este repositorio/zip adjunto). Claude Code lee `CLAUDE.md` solo.
2. Primer mensaje sugerido:

   > Lee `CLAUDE.md` y los archivos de `docs/`. Vamos a seguir con la plataforma PROPESA. Antes de cambiar nada, dime en 5 líneas qué entendiste del proceso y qué vamos a atacar. No cambies el flujo ni los textos sin confirmármelo.

3. Pide **un cambio a la vez**. Al final de cada cambio: pruebas, `CHANGELOG.md`, `docs/HISTORIAL.md` y zip nuevo.

## 2. Ritmo de trabajo

1. **Entender:** confirma el proceso y la regla de negocio antes de programar. Si falta un dato, pregunta.
2. **Especificar** (cambios medianos o grandes): escribe la especificación con supuestos y criterios de éxito, y espera «aprobado».
3. **Construir** en pasos chicos; respaldo de `index.html` antes de cada cambio grande.
4. **Probar:** `sh pruebas/correr_todo.sh` + prueba nueva para lo agregado + revisión en 390/820/1440 px y texto de 20 px.
5. **Entregar:** zip + HTML + resumen corto en español de qué cambió y qué sigue.
6. **Validar con el piso** los cambios de flujo antes de seguir.

## 3. Plugin agent-skills (Addy Osmani)

El usuario instaló **[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)** y trabaja con sus comandos. `.claude/settings.json` lo deja registrado para este proyecto (Claude Code pedirá instalarlo al abrir la carpeta). Para instalarlo a mano:

```
/plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@addy-agent-skills
```

| Comando | Para qué | Cómo se usó en PROPESA |
|---|---|---|
| `/spec` | Especificación antes de programar (supuestos, alcance, criterios, límites) | Panel de Ajustes y menú del perfil → `SPEC.md` (aprobado por el usuario) |
| `/planning` | Plan en tareas pequeñas verificables | `tasks/plan.md` |
| `/build` | Implementar en pasos chicos con pruebas | Menú del perfil |
| `/test` | Pruebas primero / cobertura | Pruebas en `pruebas/` |
| `/review` | Revisión de código en 5 ejes (correctitud, legibilidad, arquitectura, seguridad, rendimiento) | 6 correcciones (guardado fallido, contraseñas, fechas, XSS en respaldo, embarque cerrado, ids) |
| `/webperf` | Auditoría de rendimiento | Índices por dibujo y listas activas (Panel 7.9 s → 37 ms con un año de datos) |
| `/code-simplify` | Simplificar sin cambiar comportamiento | Aún no |
| `/constraints` | Fijar límites y restricciones antes de construir | Aún no |
| `/ship` | Lista previa al lanzamiento + revisiones de código, seguridad y pruebas → GO/NO-GO con plan de vuelta atrás | v1.0.0 (sin demo, CSP, accesibilidad 100) |

Si los comandos no están disponibles en la sesión, sigue el método leyendo `commands/*.toml` y `skills/*/SKILL.md` del repositorio del plugin.

## 4. Lista para publicar una versión

- [ ] Pruebas: TODO BIEN. Accesibilidad 100. Rendimiento sin regresión.
- [ ] Sin errores en consola ni violaciones de CSP.
- [ ] Sin textos de demo, usuarios o datos de ejemplo en `index.html`.
- [ ] Versión subida en dos lugares de `index.html` (menú del perfil `pmver` y Administración) + `CHANGELOG.md`.
- [ ] README, `docs/` y manual de usuario al día.
- [ ] Zip sin `__pycache__` ni `.pyc`; copia `PROPESA_Plataforma_maritima.html`.
- [ ] Plan de vuelta atrás: respaldo `.json` antes de actualizar; en Vercel → Deployments → versión anterior → **Promote to Production**.

## 5. Entregables y dónde viven

| Entregable | Dónde |
|---|---|
| Código y documentación | Esta carpeta → `propesa-plataforma.zip`. El usuario lo sube a GitHub; Vercel publica desde `main`. |
| App en un archivo | `PROPESA_Plataforma_maritima.html` |
| Manual de usuario | Documento de Claude (Docs) «Manual de usuario · Plataforma PROPESA»; actualízalo si cambia algo que ve el usuario |
| Bitácora | `docs/HISTORIAL.md` (y `PROYECTO_PROPESA.md` en el proyecto de Claude «Propesa») |

## 6. Cómo comunicar

- Español, tuteo, sin jerga. Primero el resultado, luego lo que sigue.
- Si algo no se puede, dilo claro y ofrece la alternativa.
- No narres cada paso; avisa cuando hay algo que ver o decidir.
