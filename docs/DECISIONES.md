# DECISIONES.md · Registro de decisiones

Decisiones ya tomadas con el usuario. **No las deshagas sin preguntarle.** Agrega las nuevas arriba, con fecha.

| Fecha | Decisión | Por qué / quién |
|---|---|---|
| 26/10/2026 | **Precios solo el Administrador, también en la base** (reglas de Supabase cambiadas con su permiso). **Los PDF de otras maquilas conservan el logo de PROPESA.** **Lotes en varios tanques y traslados entre tanques** (tanque principal + traslados; los kilos de cada tanque salen de repartir lo que hay; salidas primero del principal) | Usuario: «1. solo administración puede ver. 2. mantenlo. 3. continúa» |
| 26/10/2026 | **Maquilas separadas** (PROPESA, Abel, David, Luis Arce; lista en Administración): cada una con sus lotes, órdenes, empaque, embarques e informes, sin mezclarse; el mismo código de lote puede repetirse entre maquilas. **Se cambia tocando el logo**; en otra maquila su nombre va en lugar del logo, en PROPESA y en el Panel general el logo de PROPESA. **El Administrador entra al Panel general** (todas juntas). Compartido: usuarios, proveedores, especies, consignatarios, destinos, pesos y temperatura de tanques. Los compradores solo ven PROPESA | Usuario: «si me meto a cada una no quiero que se mezclen»; «que salga el nombre de la maquila en donde está el logo» |
| 26/10/2026 | **Tallas por maquila** (nombre, rango, color = tape, inglés; agregar, ocultar; no se borran ni se reordenan). **Despatada es una talla** (se guarda, se empaca y se vende); «Kg desperdicio» se queda como estaba (merma al recibir) | Usuario: «en cada maquila cambiar rango y colores… la maquila a veces especifica las categorías»; pregunta 3: sí |
| 26/10/2026 | **Salidas que no son embarque**: para congelar, basura, a recuperación y débil, con nota o folio; solo el Administrador (mismo permiso que los movimientos). No cuentan como mortalidad | Usuario: «todos los que encontraste en el Excel» |
| 26/10/2026 | **Consignatarios y destinos los agrega el Administrador**; Yishunhai también a XMN. **Sin tape por envío: el color es el del consignatario** (se hizo y se quitó el mismo día, a pedido del usuario). **% de mortalidad del cliente y temperatura de arribo** por embarque. **Precio de compra** por recepción (solo el Administrador en la app) | Usuario: preguntas 4, 6 y 7: sí; 5: «quita el color del tape, ya va con cada consignatario» |
| 26/10/2026 | **Hojas del Excel de Martha como PDF para imprimir** (no Excel): Recepción, Envíos, Existencia, Congelación, Precio de compra, Balance. **Sus fórmulas son la referencia**: `excel_reales_t.py` compara la app con ellas usando sus datos reales | Usuario: «solo PDF… para imprimir»; «usa sus fórmulas como fuente de verdad» |
| 24/10/2026 | **Especie en cada entrada**, de una lista que solo cambia el Administrador (Langosta Roja de inicio; los lotes de antes son Langosta Roja). Sale en el PDF de Entrada y en la Hoja de empaque (de los lotes empacados). **Tanques y compradores separan kilos por especie.** Las órdenes no llevan especie: lo pedido resta solo de los totales por talla | Usuario: «diferentes especies en los tanques»; respuestas: lista en Administración · Entrada y Hoja de empaque · separar por especie |
| 22/10/2026 | **Empaque: el avance (completadas · pendientes · %) va arriba de las hieleras y no se mueve**; antes flotaba abajo, debajo del teclado. «Guardar hieleras» sigue abajo | Usuario (captura con el avance encerrado) |
| 22/10/2026 | **Rol Cliente para compradores de fuera (China)**: ven en vivo, en inglés, los kilos disponibles por talla y lo recibido en los últimos 7 días, para hacer ventas. **Disponible = tanques − lo pedido que no ha salido.** **Al cerrar un embarque la salida del tanque se registra sola** (cambia la del 14/oct «salidas a mano»); reabrir la regresa. Sin temperatura, proveedor, lote ni tanque para el comprador. La base solo le deja leer su hoja (reglas de seguridad cambiadas con su permiso) | Usuario: «gente de fuera como en China», «la semana», «lo que va entrando en vivo… para tenerlo a mis consultores y hacer ventas»; 1 A · 2 No · 3 Inglés · 4 Sí |
| 18/10/2026 | **Fechas y horas se escriben** (sin calendario ni reloj del teléfono) con «Hoy»/«Ahora». **Empaque: cada hielera se completa sola** (también en la vista completa) y al terminar se cierra el teclado con «Listo». **Orden: el total sale de las tallas**; tallas opcionales; tarimas y cartón aparte. **Empacar sin lote** y conectarlo después. Proveedor nuevo desde la Entrada (Administrador). Pesos editables desde Embarque. Ventana para instalar la app. Sin CSV, sin «Quitar guardadas», sin «Eliminar orden» en Modo piso, sin «Revisión aparte / se calcula sola» | Usuario, después de usarla en su celular |
| 17/10/2026 | **El proveedor se elige de una lista** (Entrada y hoja de Modo piso) y la app **propone el lote** (WLR + clave + ddmmyy). Proveedores en Administración, **solo el Administrador** los agrega o edita; se guardan nombre, clave, **RFC** y **permiso de pesca**. **Empacar de un lote sin entrada** (lote, proveedor, tanque), siempre disponible, con aviso «Sin entrada · Completar ›»; lo hacen Administrador y Encargado de piso; **no cuenta** en tanques ni en mortalidad hasta completar su entrada. Del papel a la app: **cambio directo, empezando en cero**. Contra errores: solo avisos de «números raros» (pendiente). Sin «Verificó». PDF como el formato oficial (pendiente). **Sin textos de «todavía no», versiones viejas o lotes escritos a mano** dentro de la app (las cajas de guía y los faltantes de los PDF se quedan) | Usuario, después de la prueba con sus documentos reales |
| 17/10/2026 | **«Borrar todos los datos» regresa** solo para el Administrador, escondido en «Configuración avanzada» (respaldo reciente + BORRAR TODO + contraseña). **Rango de temperatura pendiente** (sin avisos). **Órdenes sin clientes finales**, por consignatario con tallas, kg de producto (15/16), tarimas y cartón. **Tarima 9.9 kg.** Consulta puede salir de Modo piso | Usuario |
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
| 14/10/2026 | **Empacar NO resta kilos**: las salidas se siguen registrando a mano en el lote. *Desde el 22/10/2026 la salida se registra sola al cerrar el embarque (empacar sigue sin restar).* | Usuario (pregunta abierta 3) |
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
| 15 oct 2026 | Datos de Entrada obligatorios: hora, temperaturas, kg por caja en tanque y desperdicio | Usuario: «para que no se le olviden» |
| 16 oct 2026 | **Mortalidad final sale del flujo**: 4 pasos (Entrada → Órdenes → Empaque → Embarque); Mortalidad final se calcula sola y se revisa aparte (menú «Revisión») | Usuario: «eso se revisa aparte, no quiero que el flujo me lleve ahí» |
| 16 oct 2026 | Temperatura conectada con Entrada: las temperaturas de cada entrada salen solas en Temperatura, tablero de tanques y lote; las lecturas manuales siguen | Usuario: «que no sea algo aparte, que se actualice solo» |
| 16 oct 2026 | **Peso de la caja = un solo estándar** en Administración (solo el Administrador); Embarque, Órdenes y PDF lo usan; los embarques cerrados conservan su peso | Usuario: en el piso no se pesa, se usa el estándar; «no es claro dónde edito cuánto pesa la caja» |
| 23 oct 2026 | **Los pesos se editan solo en Embarque** («Editar pesos», solo el Administrador); se quitó la tarjeta «Peso de la hielera» de Administración | Usuario: «no me gusta que esté en Administración; quiero que esté en el paso donde se necesita» |
| 16 oct 2026 | **Sin «Borrar todos los datos» en la app.** Primero se escondió en «Configuración avanzada» (respaldo + BORRAR TODO + contraseña, v1.8.4); minutos después el usuario pidió quitarlo por completo (v1.8.5). Solo se hace a mano desde Supabase (`SUPABASE.md` §9) | Usuario: «quita completamente el botón; no quiero que alguien lo pueda hacer, solo lo haría yo manualmente» |
| 14 oct 2026 | Los datos viajan como **registros por cosa** (`app_records`) y la app sigue usando `ST` igual; no se usaron las tablas normalizadas de `schema.sql` | Mantener intacta la app (flujo, pantallas y reglas) y que no choquen dos tablets; las tablas normalizadas quedan para reportes |
| 14 oct 2026 | Sin librería de Supabase: conexión con `fetch` (acceso, registros, función) | Regla de cero dependencias; CSP simple |
| 14 oct 2026 | «Último que guarda gana» por registro; lo pendiente del equipo gana sobre lo que llega mientras no se suba | Simple y suficiente: cada caja, movimiento y nota es su propio registro |
| 14 oct 2026 | Los datos viejos de cada tablet **no se mezclan** con la base; se pueden descargar o borrar desde Administración | Eran de prueba y cada tablet tenía otros |

| 26 oct 2026 | **Avisos de la entrada:** fecha que no cuadra con el código del lote y hora de madrugada (00:00–04:59). No bloquean; el Administrador corrige o acepta («Está bien así») | Usuario, después de los errores del Excel de Martha |
| 26 oct 2026 | **Salida incompleta:** lo que no se pudo descontar al cerrar el embarque queda como pendiente del embarque, con «Volver a descontar del tanque» | Usuario |
| 26 oct 2026 | **Especie en cada orden** (cambia la del 24/oct): empacar solo de lotes de esa especie; lo pedido resta de su especie para los compradores | Usuario: «Sí, en cada orden» |
| 26 oct 2026 | **Balance de Luis Arce = fórmula de PROPESA** (cuenta despatada y congelados) | Usuario |
| 26 oct 2026 | **Sin rango de temperatura** por ahora (se preguntó otra vez) | Usuario |
| 26 oct 2026 | **Lotes por envío:** cada embarque dice cuánto lleva de cada lote (hieleras, langostas, kg de producto, tallas) en la pantalla, el PDF y el informe por correo | Usuario: «Sí, en el envío y en el PDF» (pregunta 6) |
| 26 oct 2026 | **Cerrar con la hoja de empaque incompleta solo pregunta** (no bloquea); el PDF la marca como incompleta | Usuario: «Solo pregunta (como hoy)» (pregunta 9) |
| 26 oct 2026 | **Órdenes de fechas distintas en un embarque:** se permiten, sin aviso | Usuario (pregunta 12) |
| 26 oct 2026 | **PDF: nombre de la maquila en grande** (banda debajo del logo y etiqueta en las demás páginas); el logo de PROPESA se queda | Usuario: «que sea claro distinguir» |
| 26 oct 2026 | **PDF a color por talla:** leyenda con color y gramaje de las tallas de la maquila del PDF; columnas de talla con encabezado del color y teñidas | Usuario: «que toda la tabla sea de cada color respectivo para que sea más visual» |
| 26 oct 2026 | **Modo piso paso a paso** para «Cerrar embarque» (hieleras → pendientes → cerrar) y «Conteo final» (kg → confirmar). El piso revisa pero solo el Administrador cierra embarques | Usuario: «Sí, los dos» (pregunta 15) |

| 27 oct 2026 | **Logotipo por maquila** (emblema con iniciales, forma y color propios + «MAQUILA» + nombre) en menú, Modo piso, celular, menú de maquilas, Panel general y Administración; PROPESA conserva su logo. Los PDF no cambian | Usuario: «make the logo be like "maquila Abel"… easy to recognize when you switch» |
| 27 oct 2026 | **Vivas al llegar, % del cliente y temperatura de arribo se capturan en Revisión → Mortalidad final**, no en el embarque | Usuario: «quiero que esté aparte en la pestaña de revisión, no en la sección de embarque» |
| 27 oct 2026 | **Juntar y separar embarques solo en el embarque**, con Ahora → Así queda, confirmar y Deshacer; la orden solo dice en qué embarque va | Usuario: «pico botones al azar y no sé qué hacen» |
| 27 oct 2026 | **El color de toda consignación (abierta o cerrada) es el del consignatario en Administración**; cambia la regla de la v1.15.0 de que los cerrados conservaban su color | Usuario: «very critical… colors don't match the admin settings» |

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

## 28/oct/2026 (v1.25.0)
- **Despatada es merma** (usuario): entra en Mortalidad final. Decidido por Claude, por confirmar: el conteo final cuenta langostas enteras (esperado sin despatada) y la merma suma la despatada recibida.
- **Orden sin despatada (29/oct, usuario):** la orden no pide hieleras de Despatada; Empaque conserva la categoría Gris (el usuario pidió dejarla).
- **Conteo final = solo langostas enteras** (confirmado por el usuario el 29/oct).
- **Temperatura (29/oct):** el usuario pidió rangos internos basados en el Excel para que no todo salga en rojo; aplican a agua y producto (cada uno con su escala). Con los datos del Excel: agua en rojo 1 de 60, producto en rojo 9 de 53. La tabla de la industria se deja de referencia.
- **Prueba con Excel (29/oct):** los envíos sin tallas en el Excel no se capturan (usuario).
- **Hieleras de otra maquila:** la orden y el embarque son de la maquila que los crea; los kg salen del tanque de la maquila dueña del lote al cerrar.
- **Tanques en 3D (2/nov, usuario):** el color de las canastas es **solo por talla** (listón), con las tallas y colores de la maquila de cada canasta; no hay color por maquila. Las canastas se calculan con «kg por caja en tanque» (obligatorio). Planta: filtros de T1–T4 al este, T5 con filtro, T6 sin filtro, una puerta en cada lado del área de recepción. Va en Entrada y Panel general; todos lo ven (Encargado de piso y Solo inventario: siguiente paso). Solo inventario verá solo lo disponible, con lo pedido quitado del lote más viejo, sin días, lotes, proveedores ni maquilas, y el 3D será lo primero de su pantalla.


## 5/nov/2026 (v1.37.0)
- **iPad mini viejo (usuario):** la app se usará sobre todo en un iPad mini viejo; no sabía el modelo y pidió «el más viejo posible» → se soporta desde **iOS 12 (iPad mini 2 y 3)**. iOS 9 (iPad mini 1) queda fuera: Safari 9 no tiene lo básico del programa. En navegadores nuevos nada cambia. En equipo viejo (`lite`): sin vidrio esmerilado y la planta 3D empieza apagada (se puede prender).

## 5/nov/2026 (v1.36.0)
- **Textos de formularios (usuario, /impeccable clarify, aprobó los 4 grupos):** error junto al campo y sin repetirse; una talla = «Chica · 491-610» y un tanque = «T1» en pantalla (los PDF siguen el papel); sin tipo de movimiento, rol ni a. m./p. m. elegidos de inicio; ejemplos con «Ej.»; confirmaciones que dicen qué se borra. En Empaque la categoría sigue siendo el color.

## 5/nov/2026 (v1.35.0)
- **Detalles ordenados (usuario, eligió Orden, Embarque, Administración y Lote):** lo que se hace primero; PDF/correo/eliminar en el encabezado; Hoja de empaque, indicaciones de carga, peso del embarque y temperatura del lote plegados con su estado a la vista; Administración en 4 pestañas. Sin cambios de datos ni de reglas.

## 5/nov/2026 (v1.34.0)
- **Pantallas limpias (usuario, aprobó todo):** encabezado corto con la acción principal arriba; PDF/correo discretos; lo secundario plegado; menú sin Panel general ni Administración (siguen en el selector de maquila y en el perfil); Entrada con «+ Nueva entrada» arriba y la planta 3D plegada (en Panel general sigue abierta).

## 5/nov/2026 (v1.33.0)
- **La app es una herramienta de formatos (usuario):** ya no obliga a empezar por la Entrada. La vista completa abre en «Formatos», por rol; el menú no lleva números ni «Siguiente paso». El flujo Entrada → Órdenes → Empaque → Embarque sigue siendo cómo se conectan los datos, no un orden de captura.
- **Eliminar una orden con hieleras empacadas se permite** (usuario: «debería poder borrar si yo quiero»), con confirmación que dice cuántas; si el embarque está cerrado, primero se reabre. Cambia la regla de la v1.8.3. Eliminar un lote con hieleras sigue bloqueado.
- **Corregir una hielera de un embarque cerrado:** «Reabrir para corregir» en Empaque (solo Administrador, con confirmación).
- **Sitio sin teléfono** (usuario): solo correo.
