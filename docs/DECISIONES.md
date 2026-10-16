# DECISIONES.md · Registro de decisiones

Decisiones ya tomadas con el usuario. **No las deshagas sin preguntarle.** Agrega las nuevas arriba, con fecha.

| Fecha | Decisión | Por qué / quién |
|---|---|---|
| 15/10/2026 | **Entrada: si falta el lote, las dos pantallas dicen «Escribe el lote.»** (antes la vista completa decía «Escribe el lote de recepción.»). Viene de unir la regla de Entrada (`lotErr`, auditoría #10) | Usuario: «mantenlo como tú dices» |
| 15/10/2026 | **El código del lote se ve completo en su tarjeta de Modo piso** («¿De qué lote sacas las langostas?»): la letra se ajusta al ancho de la tarjeta (hasta el tamaño de antes) y un código muy largo pasa a otro renglón. El código puede ser de cualquier largo | Usuario: «el lote sale dependiendo su entrada» |
| 14/10/2026 | **Auditoría:** (1) `WN` valida números con `wnn`/`wn0` (antes texto → riesgo de código en el tablero de tanques); (2) «En tanques» del Panel solo cuenta lotes abiertos (como el mapa); (3) cambiar de pestaña de lote con cajas sin guardar avisa en vez de moverlas de lote | `/ponytail-audit` |
| 14/10/2026 | **Tablero de tanques arriba de Entrada como el plano del piso** (dibujo del usuario: T1–T4 a la derecha de arriba abajo, T6 junto a T3 y T5 junto a T4 a la izquierda; `tanques()`, `.tqmap`, `TQSEL`). Al tocar un tanque sale su detalle. Por tanque: kg (lotes abiertos con existencia), kg por talla, lotes y última temperatura; «● En vivo» con la base compartida. Sin nivel de llenado hasta saber la capacidad de cada tanque | Usuario: «ver todos mis tanques y en vivo lo que tienen» |
| 14/10/2026 | **Ícono de Entrada = langosta blanca** (silueta del ícono de la app, `IC.recepcion`); Embarque conserva el camión (`IC.camion`). Antes Entrada y Embarque compartían el camión | Usuario |
| 14/10/2026 | **Empaque (vista completa) con tarjetas como Modo piso** y **teclado que se abre y se cierra** (`KPON`, `propesa-kp`, por equipo; abierto por omisión). Abierto: las tarjetas no repiten las categorías. Cerrado: cada tarjeta trae sus botones y el teclado de la tablet (`inputmode` numérico). Se cierra con una **X** en la esquina del teclado y se abre con un **botón flotante con ícono de teclado numérico** sobre la barra de «Guardar cajas» | Usuario (capturas: «se mira muy repetitivo»; «quiero que las cajas se miren así») |
| 14/10/2026 | **Empaque sin lote en cada caja:** el lote se elige una vez con **pestañas por lote** (como Chrome) arriba de las cajas; en tablet y computadora se quedan a la vista al bajar. Las cajas no repiten el lote; al corregir una caja se puede cambiar su lote junto a «Actualizar caja» | Usuario (captura con el lote subrayado) |
| 14/10/2026 | **La barra de arriba dice dónde estás en todos los tamaños** (antes solo en celular), entre el buscador y Ajustes; en Empaque agrega cliente y lote: «Empaque · LHD · Lote WLRCO051026A» | Usuario (recuadro amarillo en la captura) |
| 14/10/2026 | Teclado de Empaque: las 4 tallas en 2×2 en tablet horizontal y computadora (en fila no cabían bien con guantes) | Ajuste al agregar Amarillo |
| 14/10/2026 | **Peso bruto = 19.6 kg por caja/hielera en todos lados** (1.4 hielera + 1.5 gel + 16 producto + 0.7 caja de cartón). La orden usaba 20 kg; ahora usa lo mismo que el embarque (`KGB=19.6`, `kb()` redondea a 1 decimal) | Usuario (pregunta abierta 1) |
| 14/10/2026 | **Categoría de la caja = su talla**, con los colores de talla: Blanco 491-610, Rojo 611-850, Verde 851-1220 y **Amarillo 1221-UP** (nuevo) | Usuario (pregunta abierta 2) |
| 14/10/2026 | **Empacar NO resta kilos**: las salidas se siguen registrando a mano en el lote | Usuario (pregunta abierta 3) |
| 14/10/2026 | **El desperdicio resta del total del lote** (kilos en tanque y mortalidad), no de cada talla | Usuario (pregunta abierta 4) |
| 14/10/2026 | **Respaldo:** aviso rojo al Administrador si pasan 7 días sin descargar respaldo (Supabase sigue en plan gratis, sin respaldos automáticos) | Usuario |
| 14/10/2026 | **Entrega:** el alcance es lo que ya funciona (Formato 02, encabezado del packing list, correo automático y servidor local = fase 2). Supabase en plan gratis y cuentas (Supabase, Vercel, GitHub) a nombre del desarrollador. Piloto de 1–2 semanas con el papel en paralelo. Logo oficial: se pide al cliente | Usuario |
| 14/10/2026 | **Servidor local en la oficina a futuro**; por ahora Supabase. No usar más funciones propias de Supabase para no complicar la mudanza | Usuario |
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
| 14 oct 2026 | **Base compartida en Supabase (`propesa_bc`)**: todos los equipos y cuentas ven lo mismo | El usuario no quería que cada equipo tuviera sus propios datos |
| 14 oct 2026 | Los datos viajan como **registros por cosa** (`app_records`) y la app sigue usando `ST` igual; no se usaron las tablas normalizadas de `schema.sql` | Mantener intacta la app (flujo, pantallas y reglas) y que no choquen dos tablets; las tablas normalizadas quedan para reportes |
| 14 oct 2026 | Sin librería de Supabase: conexión con `fetch` (acceso, registros, función) | Regla de cero dependencias; CSP simple |
| 14 oct 2026 | «Último que guarda gana» por registro; lo pendiente del equipo gana sobre lo que llega mientras no se suba | Simple y suficiente: cada caja, movimiento y nota es su propio registro |
| 14 oct 2026 | Los datos viejos de cada tablet **no se mezclan** con la base; se pueden descargar o borrar desde Administración | Eran de prueba y cada tablet tenía otros |

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
