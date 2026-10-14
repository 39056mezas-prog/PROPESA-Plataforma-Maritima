# DECISIONES.md · Registro de decisiones

Decisiones ya tomadas con el usuario. **No las deshagas sin preguntarle.** Agrega las nuevas arriba, con fecha.

| Fecha | Decisión | Por qué / quién |
|---|---|---|
| 13/10/2026 | **v1.1.0 · Entrada en Modo piso = hoja de varias entradas** (una fila por lote, «+ Agregar entrada», «Guardar entradas» guarda cada fila por separado, errores junto al campo). Sustituye al asistente de una entrada a la vez | Usuario: el operador recibe varios lotes a la vez y abrir una ventana por entrada lo frena |
| 12/10/2026 | **v1.0.0 sin rastros de demo**: sin usuarios precargados; primer uso = Configuración inicial; temperatura real; «Informes de cierre»; «Borrar los datos de este equipo» | Usuario: «como si ya fuera versión final» (/ship) |
| 12/10/2026 | Cabeceras de seguridad (CSP estricta, HSTS, Permissions-Policy) y `no-cache` para `index.html` | /ship, revisión de seguridad |
| 12/10/2026 | Menú del perfil = círculo con la inicial: **Administración** (solo admin) y **Cerrar sesión**. **Ajustes se queda en la barra**, no en el menú | Usuario: mantener Ajustes a la mano por accesibilidad |
| 12/10/2026 | Ajustes deja ver la pantalla de atrás; **3 tamaños de texto** (15/17/20 px) con deslizador | Usuario: garantizar visibilidad en todos los equipos |
| 12/10/2026 | Panel de Ajustes con tema claro/oscuro/del equipo (`SPEC.md`) | Usuario, con /spec |
| 12/10/2026 | Rendimiento: índices por dibujo y listas activas (solo lo reciente + historial) | /webperf |
| 12/10/2026 | Correcciones de /review: guardado fallido visible, contraseñas con hash, fechas locales, respaldo validado, no agregar a embarque cerrado, ids de lote crecientes | /review |
| 12/10/2026 | **Todos los avisos rojos llevan al lugar donde se resuelven** | Usuario |
| 12/10/2026 | El **admin no entra a Modo piso** automáticamente; el piso sí | Usuario |
| 12/10/2026 | Logo = botón de inicio en ambos modos; interruptor estilo iOS para Modo piso; look iOS en piso | Usuario |
| 12/10/2026 | Modo piso: **todas las cajas del cliente a la vez**, cada una se guarda sola, queda **gris con ✔ y editable** | Usuario: «mis empleados anotan varias cajas a la vez»; «que no se borre por si ocupan editarla» |
| 12/10/2026 | Modo piso con botones grandes, prioridad **Empacar cajas** y **Registrar entrada** | Usuario, inspirado en McDonald's |
| 12/10/2026 | Colores de talla: 491-610 Blanco · 611-850 Rojo · 851-1220 Verde · 1221-UP Amarillo | Usuario |
| 12/10/2026 | El Encargado de piso puede registrar entradas (permiso `ent`) | Necesario para Modo piso |
| 10/10/2026 | Paleta de marca: navy `#0B1D59`, azul `#087DBA`, cian `#16A6D1`, proporción 60/30/8/2, sin cambiar layout | Usuario (`docs/referencias/PROPESA_Color_System_Refinement.md`) |
| 10/10/2026 | Base compartida = **Supabase, sin conectar la cuenta todavía** | Usuario |
| 10/10/2026 | El documento final de cada paso es un **PDF**; el mismo se descarga y se manda por correo | Usuario |
| 10/10/2026 | Vista adaptable a computadora y celular (además de tablet) | Usuario: hay gente que solo consulta |
| 10/10/2026 | Un embarque puede juntar varias órdenes (mismo destino y consignatario) | Usuario |
| 10/10/2026 | Empaque: una fila por cada caja que falta, se guardan todas a la vez; en Empaque solo notas, sin fotos | Usuario |
| 10/10/2026 | Ícono de Embarque = camión (igual que Entrada) | Usuario |
| 10/10/2026 | Lote en MAYÚSCULAS en vivo; campo «Kg por caja en tanque» | Usuario |
| oct 2026 | **Cambio de modelo:** en tanque no hay cajas numeradas; las langostas se cuentan al **empacar** cada pedido. Flujo renombrado a Entrada → Órdenes → Empaque → Embarque → Mortalidad final | Usuario (el cambio más importante) |
| oct 2026 | Entrada rehecha con los campos del formato en papel | Usuario (`PROPESA_Control_Recepcion.pdf`) |
| oct 2026 | Módulo de Órdenes con consignatarios oficiales y clientes finales | Usuario |
| oct 2026 | Una sola página HTML sin dependencias hasta tener backend; despliegue GitHub + Vercel | Simplicidad |

## Rechazadas (no repetir sin preguntar)

| Propuesta | Resultado |
|---|---|
| Sistema de color semántico oscuro, números gigantes, estados en el menú | Revertido por completo |
| Galería de fotos de lotes en el Panel | Revertida |
| Modo piso de una caja a la vez | Cambiado a varias cajas |
| Cajas que desaparecen al guardarse | Cambiado a grises con ✔ |
| Ajustes que oscurece la pantalla | Cambiado a panel translúcido |
| Rango libre de tamaños de texto (12–20 px) | Regresó a 3 tamaños |
| Ajustes dentro del menú del perfil | Regresó a la barra |
| Teclado numérico propio en Modo piso | Quitado |
| Botones de «entrar como…» en el acceso | Quitados (/review) |
