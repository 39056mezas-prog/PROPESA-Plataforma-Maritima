# Cambios

## 1.12.0 · 18 de octubre de 2026

Pedidos del usuario después de usar la app en su celular.

### Nuevo
- **Ventana para instalar la app.** Al entrar al sitio, en Android y en computadora sale «Instala la app PROPESA» con «Instalar» / «Ahora no»; en iPhone dice cómo agregarla a inicio. No sale si ya está instalada ni durante 7 días después de «Ahora no». Archivo nuevo `sw.js` (solo deja la app instalable; no guarda nada).
- **Empacar sin lote y conectarlo después.** En Empaque (vista completa y Modo piso) hay «Empacar sin lote»: crea un lote provisional de la orden (SIN-LOTE-ddmm) y se empaca normal. Después, en su página, «Conectar con su entrada» pasa sus hieleras al lote correcto y el provisional desaparece.
- **Agregar un proveedor desde la Entrada** («+ Agregar proveedor…» en la lista, solo Administrador), sin perder lo que ya se escribió; queda elegido y propone su lote. También en la hoja de Modo piso.
- **Editar pesos desde Embarque** (Administrador): «Editar pesos» abre ahí mismo hielera, gel, tarima, producto y caja de cartón.

### Cambiado
- **Fechas y horas se escriben** (sin el calendario ni el reloj de Android, que se trababan): dd/mm/aaaa y HH:MM con botón «Hoy» / «Ahora». Las diagonales y los dos puntos se ponen solos. Hora inicial y final del Formato 06 con «Ahora».
- **Empaque (vista completa): cada hielera se completa sola** al tener piezas y categoría (como en Modo piso). Al terminar la última se cierra el teclado y sale «✔ Listo» con animación.
- **Orden:** primero las hieleras por talla y **el total sale solo**; sin tallas se escribe el total (tallas opcionales: el embarque toma las tallas de lo empacado). Kg de producto, tarimas y cajas de cartón van en su propio apartado, «Producto y empaque».
- **Órdenes:** «Nueva orden» va en el encabezado y las órdenes en una tabla (fecha, destino, hieleras, peso bruto, estado, Abrir).
- **Aviso «Sin líneas» → «Falta el destino · Agregar ›».**
- **Entrada (Modo piso):** los datos extra se ven desde el principio («Más datos»). Ya no está «Quitar guardadas de la lista».
- **Mortalidad final** sin «Revisión aparte», «Se calcula sola» ni «No es un paso del flujo».

### Quitado
- «Descargar packing list (CSV)».
- «Eliminar orden» dentro de Modo piso (sigue en la vista completa).

### Pruebas
- `v112_t.py` (109), nueva. Las pruebas de Empaque, Órdenes, fechas, pesos y Mortalidad se pasaron al comportamiento nuevo. 35 grupos, 1961 verificaciones, TODO BIEN.

## 1.11.0 · 17 de octubre de 2026

### Nuevo
- **El proveedor se elige de una lista** (pedido del usuario, después de probar la app con sus documentos reales: el mismo proveedor salía escrito de 3 formas, por ejemplo «SCPP EMANCIPACION SC DE RL» y «SCCP EMANCIPACION»). En la Entrada (vista completa) y en la hoja de entradas de Modo piso.
  - Lista inicial: **SCPP Ensenada SCL (CO)**, **SCPP Emancipación SC de RL (EM)** y **SCPP Leyes de Reforma (LE)**.
  - **La app propone el código del lote** al elegir proveedor y fecha: WLR + clave + día-mes-año (Ensenada + 22/09/26 → **WLRCO220926**). Si ya existe, propone la siguiente letra (WLRCO220926B). Se puede corregir. Si se escribió a mano, ya no se cambia solo. Al tocar el lote propuesto se selecciona completo: lo que se escriba lo reemplaza.
  - **Administración → Proveedores** (solo el Administrador): agregar, editar nombre oficial, clave del lote, **RFC** y **permiso de pesca**, y ocultar (los lotes que ya tiene no cambian; siempre queda al menos uno). Al cambiar el nombre, sus lotes toman el nombre nuevo.
  - Un lote de antes con el nombre exacto de la lista ya cuenta como ese proveedor; a los demás se les pone proveedor al editarlos.
  - El PDF de Entrada trae una tabla de proveedores con su clave, RFC y permiso de pesca.
- **Empacar de un lote sin entrada** (pedido del usuario para dejar el papel: la langosta que ya está en los tanques no tiene entrada en la app).
  - En Empaque (vista completa y Modo piso) hay **«+ Lote sin entrada»**: se escribe el lote y se eligen proveedor y tanque; se empaca normal. Lo pueden hacer el Administrador y el Encargado de piso. Si el lote ya existe, solo se elige.
  - Ese lote sale en amarillo **«Sin entrada»** en Entrada, Empaque y su página, con **«Completar entrada ›»**. Completar abre la Entrada (o la hoja de Modo piso) con lote, proveedor y tanque ya puestos; al guardarla, el lote queda normal y conserva sus hieleras.
  - Mientras no tenga entrada **no cuenta** en el tablero de tanques, en Mortalidad final ni en sus PDF.

### Cambiado
- **Textos más cortos, sin «todavía no» ni versiones viejas** (pedido del usuario): «Todavía no hay lotes. Registra la primera entrada para empezar» → «Registra la primera entrada.»; «Todavía no hay lecturas» → «Sin lecturas»; «Aún no hay informes» → «Sin informes»; «Sin datos todavía» → «Sin datos»; sin «(de una versión anterior)». Los avisos de conexión no cambian.
- Lote sin entrada y proveedores sin explicaciones de más: el aviso dice solo «Lote X · sin entrada» con «Completar entrada ›»; el PDF de Entrada no lo menciona; Administración no habla de lotes escritos a mano.

### Corregido
- «Configuración avanzada» (Administración) a veces se cerraba sola si la pantalla se redibujaba justo después de abrirla.

### Pruebas
- `proveedores_t.py` (128), nueva. Las pruebas que escribían el proveedor ahora lo eligen de la lista. 34 grupos, 1862 verificaciones, TODO BIEN.

## 1.10.1 · 17 de octubre de 2026

### Corregido
- **Con la cuenta de Consulta ya se puede salir de Modo piso.** El interruptor «Modo piso» de arriba solo le salía al Administrador; Consulta entraba desde el menú y se quedaba atorada. Ahora lo ven el Administrador y Consulta. El Encargado de piso sigue entrando directo a Modo piso (decisión del 12/oct).

### Cambiado
- **Temperatura: el rango normal queda pendiente** (pedido del usuario). Ya no se marca nada en rojo, no hay aviso de «fuera de rango» y el PDF no habla de rango. Las columnas (fecha, hora, termómetro flotante, superficie del agua, interna del producto) se quedan.
- **«Borrar todos los datos» regresa, escondido y solo para el Administrador** (pedido del usuario). Está al final de Administración, dentro de «Configuración avanzada» (cerrada). Pide un respaldo descargado en los últimos 15 minutos, escribir BORRAR TODO y la contraseña. Borra lotes, órdenes, embarques, hieleras, notas y fotos, informes y temperaturas en todos los equipos; los usuarios y el peso de la hielera se quedan.

### Pruebas
- `ordenes_t` (salir de Modo piso con Consulta, temperatura sin rango), `sincronizacion_t` (borrar todo: contraseña equivocada no borra; con la correcta llega a todos los equipos), `inicio_t`, `fotos_t`. 33 grupos, 1734 verificaciones, TODO BIEN.

## 1.10.0 · 17 de octubre de 2026

### Nuevo
- **Órdenes por destino y consignatario, como la hoja que usa PROPESA** (pedido del usuario, con su «ORDER LIST» de ejemplo). Por cada consignatario el Administrador captura: **total de hieleras**, **hieleras por talla** (Chica / Mediana / Grande / Jumbo, con sus colores), **kg de producto por hielera (15 o 16)**, **tarimas** y **cajas de cartón**.
  - La app arma la tabla de **peso bruto** (hieleras · gel ice · tarimas · producto · caja de cartón) mientras se escribe, y el total de la orden. Ejemplo de la hoja: 110 hieleras, 6 tarimas, 16 kg, sin cartón = **2138.4 kg**.
  - Las tallas deben sumar el total; si no, no se agrega y se conserva lo escrito.
  - Cada orden lleva un solo destino: después del primer consignatario, la ciudad queda fija. El mismo consignatario no se repite en una orden.
  - **Ya no se capturan clientes finales** (las órdenes de antes conservan los suyos y su peso anterior).
  - El embarque toma las tallas y el peso de la orden (ya no se capturan en Embarque).
  - Al empacar se ve, por talla, cuántas hieleras se pidieron y cuántas van; si no cuadran, aviso rojo en la orden, en Empaque, en Modo piso y en el embarque.
  - El PDF de la orden sale como la hoja: un bloque por consignatario con sus tallas en colores y su tabla de peso bruto, y el peso bruto de toda la orden.
- **Tablero de tanques (Entrada):** por cada talla, cuántas **hieleras de 15 kg** hay en el tanque (y los kg sueltos), y el total.
- **Monitoreo de temperatura de tanques** (control interno): fecha y hora por separado, **termómetro flotante**, **superficie del agua** e **interna del producto**. Rango normal **48.4 a 56.6 °F**: lo que sale se marca en rojo (tabla, tablero de tanques, lote), al guardar avisa, y arriba sale un aviso con «Ver las lecturas en rojo ›». Nuevo **PDF de monitoreo de temperatura** (todas las lecturas, o las del tanque elegido).

### Cambiado
- Peso estándar (Administración): se agrega la **tarima (9.9 kg)**. El producto queda como valor por omisión; en cada orden se elige 15 o 16.

### Pruebas
- `ordenes_t.py` (86), nueva. Las pruebas que agregaban líneas con cliente se pasaron al formulario nuevo. 33 grupos, 1711 verificaciones, TODO BIEN.

## 1.9.0 · 17 de octubre de 2026

### Nuevo
- **Hoja de empaque (Formato 06) en cada orden.** Pedido del usuario: «es requerido por ley para tenerlo en archivo; todo esto debe salir en el correo o PDF». Una hoja por orden (cada orden va a un solo destino; puede llevar varios lotes y varios consignatarios). La ven la orden, Empaque y Modo piso.
  - **La app la llena sola:** fecha, especie (Langosta Roja), destino, consignatario(s), lotes (de las hieleras empacadas), peso bruto (hieleras × peso estándar) y total de hieleras por talla.
  - **La app propone y se puede corregir:** tanques de origen (tanque de cada lote empacado) y tanque y temperatura (última lectura de agua de ese tanque). Al guardar quedan fijos.
  - **Se capturan:** placas (se guardan en mayúsculas), nombre y teléfono del chofer, temperatura del producto, quién realizó y observaciones.
  - **Horas:** la hora inicial se pone sola con la primera hielera; al terminar la última se ponen solas la hora final y quién realizó (se pueden corregir) y aparece «Terminar empaque».
  - **Evaluación del empaque (S / NS / N/D / N/A):** cuatro botones grandes; si todo fue normal, un toque en **S** y queda guardado. Las connotaciones salen al pie de la hoja y del PDF.
  - Lo que falta sale en rojo con «Completar ›» (en la orden y en el embarque). Antes de empacar no se pide nada; con la primera hielera se piden transporte y temperaturas; al terminar, también hora final, quién realizó y evaluación.
  - Cerrar un embarque con la hoja incompleta **pregunta** («¿Cerrar de todos modos?»); si se cierra, el PDF la marca como incompleta. Con el embarque cerrado la hoja ya no se cambia.
  - Sale completa en el PDF de la orden, en el packing list, en el informe del embarque y en el texto del correo de cierre.
- **Indicaciones para la carga en cada embarque** (ej. «ECHAR 2 TARIMAS VACÍAS Y FLEJE»). Pedido del usuario: «que sea algo hard to miss». Recuadro amarillo con letra grande en mayúsculas: arriba del embarque, en el plan del camión y en la tarjeta del embarque, en el inicio de Modo piso y dentro de la hoja de la orden. Sale solo al principio del PDF del embarque, del PDF del camión (plan de embarques) y en el correo de cierre.

### Cambiado
- **«Cajas» → «hieleras» en toda la app y en los PDF** (pedido del usuario: «el término correcto serían hieleras»). Se quedan «Kg por caja en tanque» (dato de Entrada), «caja de cartón» (parte del peso) y la explicación de que en el tanque no se numeran cajas.

### Pruebas
- `hoja_t.py` (110), nueva: hoja completa de punta a punta en tablet y celular, Modo piso, Consulta, PDF, correo, respaldo y base compartida. Las demás pruebas se pasaron a «hieleras». 32 grupos, 1622 verificaciones, TODO BIEN.

## 1.8.9 · 16 de octubre de 2026

### Corregido
- **Empaque en celular: ya no se abre el teclado de Android al completar una caja.** Al tocar la categoría, la app pasa a la siguiente caja y le pone el cursor (para que también funcione un teclado físico); algunos teclados, como el de Samsung, se abrían en ese momento aunque la app pedía que no. Ahora, en celulares y tablets táctiles, las casillas de piezas son de solo lectura para el sistema y se llenan solo con el teclado de la app (vista completa y Modo piso, cajas nuevas y guardadas). En computadora no cambia: el teclado físico sigue escribiendo.

### Pruebas
- `teclado_movil_t.py` (13), nueva: simula un celular Android táctil. 31 grupos, TODO BIEN.

## 1.8.8 · 16 de octubre de 2026

### Nuevo
- **Editar una orden después de crearla** (solo el Administrador, quien crea órdenes):
  - **Fecha del empaque (ETD):** «Cambiar fecha» junto al título de la orden. El nombre del embarque toma la fecha nueva.
  - **Cada línea:** «Editar» para cambiar el cliente final y cuántas cajas. El embarque se actualiza solo (hieleras y peso).
  - No se pueden pedir menos cajas de las que ya están empacadas (lo dice ahí mismo), y no se cambia una línea cuyo embarque ya está cerrado (hay que reabrirlo en Embarque, igual que para agregar líneas).
  - Para cambiar el destino o el consignatario: si la línea no tiene cajas, se elimina y se agrega de nuevo (lo explica al editar).
  - En celular el formulario de edición ocupa todo el ancho, con «Guardar» a la vista.

### Pruebas
- `editar_orden_t.py` (31), nueva. 30 grupos, TODO BIEN.

## 1.8.7 · 16 de octubre de 2026

### Cambiado
- **El peso de la caja se cambia en un solo lugar: Administración → «Peso de la caja».** Antes cada embarque tenía su propia tabla con casillas para editar, hasta abajo y con un título técnico, y no era claro dónde se cambiaba. El usuario confirmó que en el piso no se pesa (se usa el estándar) y que solo el Administrador lo cambia.
  - Peso estándar de cada caja (hielera): hielera vacía 1.4 + gel 1.5 + producto 16 + caja de cartón 0.7 = **19.6 kg brutos, 16 kg netos**. Al escribir se ve el total. Solo el Administrador lo ve y lo cambia; aplica a todos los equipos.
  - **Embarque:** la tarjeta se llama «Peso del embarque», explica que se calcula solo (hieleras × peso estándar) y ya no tiene casillas. El Administrador ve «Cambiar el peso estándar ›», que lleva directo a Administración.
  - **Órdenes y PDF** usan el mismo estándar («16 kg netos y 19.6 kg brutos por caja» ya no está fijo).
  - Al cambiar el estándar se recalculan los embarques abiertos; **los cerrados conservan el peso con el que se cerraron.**
  - Si un embarque abierto trae pesos cambiados a mano de una versión anterior, lo avisa y el Administrador tiene «Usar el peso estándar».
- «Kg por caja en tanque» de Entrada no cambió: es otro dato (cuánto pesa una caja de langosta en el tanque al recibir el lote).

### Pruebas
- `pesos_t.py` (39), nueva; `avisos_t` y `sincronizacion_t` (el peso llega a otro equipo). 29 grupos, TODO BIEN.

## 1.8.6 · 16 de octubre de 2026

### Nuevo
- **Al compartir el link sale el logo de PROPESA.** Imagen `og-image.png` (1200×630, logo en blanco sobre azul marino con «Plataforma marítima») y las etiquetas que leen WhatsApp, Facebook, Slack, X, Teams y LinkedIn (`og:*`, `twitter:*`).
- La descripción del link ya no menciona Mortalidad final como paso: «Seguimiento de cada lote de langosta viva: entrada, órdenes, empaque y embarque.»
- **Pantalla de carga con el logo de PROPESA.** Al abrir la app aparece el logo en blanco sobre azul marino, con tres puntitos, mientras se cargan los datos del equipo; se desvanece sola en cuanto la app está lista (en la app instalada se ve al menos medio segundo para que no parpadee).
- **El ícono de la pantalla de inicio de Android ya no se ve pixeleado.** Android dibuja ese ícono más grande que 512 px y estiraba el de 512; ahora hay uno de 1024 px (normal y para íconos redondos). El fondo de esa pantalla es el mismo azul que la pantalla de carga, así que se pasa de una a otra sin cambio de color. Íconos con `?v=4`.

### Pruebas
- `vista_previa_t.py` (28), nueva: vista previa del link, íconos del manifiesto y pantalla de carga. 28 grupos, TODO BIEN.

## 1.8.5 · 16 de octubre de 2026

### Quitado
- **«Borrar todos los datos» ya no existe en la app** (pedido del usuario: «no quiero que alguien lo pueda hacer, solo lo haría yo manualmente»). Se quitó también la sección «Configuración avanzada» que lo contenía (v1.8.4). Descargar y restaurar respaldo siguen igual. Si algún día hace falta borrar todo, se hace a mano desde Supabase: `docs/SUPABASE.md` §9.

### Pruebas
- `inicio_t`, `fotos_t` y `sincronizacion_t` revisan que el botón ya no existe. 27 grupos, TODO BIEN.

## 1.8.4 · 16 de octubre de 2026

### Cambiado
- **Temperatura conectada con Entrada.** Las temperaturas que se capturan al registrar cada entrada (agua del tanque y producto) aparecen solas en Temperatura, marcadas «Entrada · lote» con enlace al lote. No se copian: si editas o eliminas el lote, cambian solas en todos los equipos.
  - El tablero de tanques muestra la temperatura más reciente de cada tanque, sea de una lectura o de una entrada.
  - Cada lote tiene una tarjeta «Temperatura del tanque desde la entrada», con «+ Registrar lectura».
  - Las lecturas manuales siguen igual, para seguimiento. Temperatura tiene filtro por tanque, y «Registrar» desde un tanque o un lote ya trae ese tanque elegido.
- **Mortalidad final ya no es el paso 5.** El flujo queda en 4 pasos (Entrada → Órdenes → Empaque → Embarque). Mortalidad final está aparte, en el menú → «Revisión», y se sigue calculando sola. El Panel ya no te manda ahí, Embarque ya no tiene «Siguiente: mortalidad final» y las guías dicen «Paso N de 4».
- **«Borrar todos los datos» ya no está a la vista.** Vive dentro de Administración → «Configuración avanzada» (cerrada) y pide tres cosas: descargar un respaldo (en los últimos 15 minutos), escribir BORRAR TODO y tu contraseña. Con la contraseña equivocada no borra nada.

### Corregido
- Administración decía «versión 1.5.0» al final; ahora muestra la versión actual (la misma del menú del perfil).

### Pruebas
- `temperatura_t.py` (47), nueva; `inicio_t`, `fotos_t` y `sincronizacion_t` con el nuevo borrado. 27 grupos, TODO BIEN.

## 1.8.3 · 16 de octubre de 2026

### Nuevo
- **Eliminar una orden** creada por error. Hasta ahora no había forma: solo se podían borrar sus líneas. Al final de la orden hay una sección «Eliminar orden» con su botón; pide confirmar («¿Eliminar la orden del 16/10/2026? No se puede deshacer.»).
  - Solo se puede si la orden **no tiene cajas empacadas**. Si tiene, explica por qué y no aparece el botón.
  - Se lleva sus líneas, sus notas de empaque y los embarques abiertos que se quedan vacíos. Las demás órdenes y cajas no se tocan.
  - Solo el Administrador (quien puede crear órdenes) lo ve. Se borra en todos los equipos.

### Pruebas
- `eliminar_orden_t.py` (33), nueva. 26 grupos, TODO BIEN.

## 1.8.2 · 15 de octubre de 2026

### Cambiado
- **Entrada: todos los datos del formato son obligatorios** (pedido del usuario, para que no se olviden). Además de proveedor, tanque, lote, kg por talla y fecha, ahora también: **hora, temperatura del tanque, temperatura del producto, kg por caja en tanque y kg de desperdicio** (0 si no hubo). La temperatura del tanque debe estar entre 20 y 110 °F, igual que en Temperatura. Aplica en la vista completa y en Modo piso, con la misma regla. Solo al crear un lote: editar uno viejo no obliga a llenarlos.
  - En Modo piso, si una fila ya tiene datos y falta alguno de «Más», el botón lo dice en rojo («Más · Faltan 4») y baja mientras los llenas. Al guardar, la fila se abre y marca cada dato que falta.
  - En la vista completa, al guardar te lleva al primer dato que falta, con su mensaje, sin borrar lo escrito.
- **Cambiar de modo ya no te saca de donde estabas.**
  - Si estás en Modo piso → «Registrar entradas» y apagas Modo piso, te quedas en la misma hoja, ahora dentro de la vista completa, con las mismas filas y datos. Desde ahí puedes guardar, o volver a Entrada con «‹ Volver a Entrada».
  - Si sales de la hoja con entradas sin guardar, la pantalla de Entrada lo avisa con «Terminar de capturarlas ›».
  - Si estás en la vista completa con «+ Nueva entrada» a medio llenar y prendes Modo piso, lo escrito pasa como una fila de la hoja.
  - Empacar en un modo → Empacar del mismo cliente en el otro.
  - En celular, el menú ☰ ya no se queda abierto encima después de cambiar de modo.

### Pruebas
- `cambio_modo_t.py` (29), nueva; `entradas_t.py` con los datos obligatorios. 25 grupos, TODO BIEN.

## 1.8.1 · 15 de octubre de 2026

### Nuevo
- **Botón de atrás (Android y navegador):** regresa a la pantalla anterior de la app en vez de sacarte. Si hay algo abierto encima (una foto en grande, el menú lateral del celular, Ajustes o el menú del perfil), primero lo cierra. En Modo piso regresa a la pantalla anterior de piso, y si acabas de cambiar de modo, regresa al modo y la pantalla donde estabas. Desde la primera pantalla después de entrar, atrás sale de la app como siempre.
- **Ícono de la app y favicon: langosta blanca** sobre azul marino, el mismo dibujo del botón Entrada (antes era roja). Cambia en la pestaña del navegador y en el ícono de «Agregar a pantalla de inicio» (Android e iPhone). En Android el ícono ya llena todo el círculo o cuadro. El logo PROPESA de adentro de la app no cambió.

### Pruebas
- `atras_t.py` (41), nueva. 24 grupos, TODO BIEN.

## 1.8.0 · 15 de octubre de 2026

### Nuevo
- **Las fotos ya no viajan dentro de los datos.** Cada foto se guarda en un espacio de archivos privado de Supabase («fotos») y la nota solo lleva su referencia. Antes cada foto pesaba unas 120 mil letras dentro de la nota, se repetía en todos los equipos y llenaba su memoria.
  - Al guardar una nota, la foto se ve al instante. Se sube antes que la nota, así los demás equipos ya la encuentran.
  - Sin internet, la foto espera en el equipo, aunque se recargue la página, y cuenta como «cambio pendiente». Se sube sola al regresar el internet.
  - Los demás equipos bajan cada foto una sola vez y la guardan; después se ve aunque no haya internet. Mientras baja, el cuadro se ve gris; si tocas una foto que todavía no baja, avisa «La foto todavía se está bajando. Espera unos segundos.»
  - Eliminar una nota borra sus fotos; «Borrar todos los datos» también.
  - Una foto que todavía venga dentro de una nota (por ejemplo, de un respaldo) se pasa sola al espacio de archivos.
  - Si la base rechaza una foto, se quita de su nota y avisa «No se pudo subir una foto: se quitó de su nota.»
  - Ver: Administrador y Piso y Consulta; subir y borrar: Administrador y Piso. Máximo 2 MB por foto (la app manda ~90 KB). Plan gratis: 1 GB, unas 10,000 fotos.
- **La base ya no se pausa en la veda.** Vercel llama una vez al día a `api/despierta.js`, que hace una consulta pequeña a la base («¿ya hay Administrador?»). El plan gratis de Supabase solo pausa después de 7 días sin uso, así que ya no hace falta entrar al panel cada mes. Cómo comprobarlo: README → *Fin de temporada*.

### Base de datos
- Espacio de archivos `fotos` y sus reglas aplicados en `propesa_bc` (`supabase/migrations/20261015_fotos.sql`). Probado en la base real dentro de una transacción que se deshizo.

### Pruebas
- `fotos_t.py` (34) y `despierta_t.py` (8), nuevas. El Supabase de mentira imita el espacio de archivos. 23 grupos, TODO BIEN.

## 1.7.1 · 15 de octubre de 2026

### Corregido
- **Modo piso, «¿De qué lote sacas las langostas?»:** el código del lote ya no se corta dentro de su tarjeta. La letra se ajusta al ancho de la tarjeta (hasta el tamaño de antes) y, si el código es muy largo, pasa a otro renglón. El código puede tener cualquier largo, según como se capturó en Entrada.

### Confirmado
- El texto «Escribe el lote.» de la vista completa (cambio de la 1.6.0) se queda así.
- **Publicada en Supabase la función `usuarios` nueva** (versión 3): ya aplica en la base real que la Configuración inicial solo funcione sin cuentas y que las contraseñas tengan mínimo 8 caracteres (auditoría #15 y #20).

### Base de datos (15/oct, tarde)
- **Se borraron las tablas viejas** del primer esquema en `propesa_bc` (`20261014d_quitar_tablas_viejas.sql`): las 9 tablas sin uso, la función `piso_solo_conteo` y el disparador `al_crear_usuario` con su función `nuevo_perfil`. Antes se revisó que estuvieran vacías y que nada dependiera de ellas. Quedan `app_records`, `app_records_hist` y `profiles` (2 Administradores). La app no cambia.
- **La regla «solo el Administrador cambia roles» ya está en el repositorio** (`supabase/migrations/20261012b_solo_admin_cambia_rol.sql`). Existía en la base desde el 12/oct, pero no en ningún archivo: una base reconstruida desde cero no la habría tenido. Se copió tal cual de la base, sin cambiar nada allá, y se probó en una base local: piso no puede cambiar su rol, el Administrador y la función `usuarios` sí.
- Ya no salen los avisos de Supabase sobre esas tablas. Los que quedan (`has_admin`, `my_role`, contraseñas filtradas del plan Pro) son por diseño.

### Pruebas
- `piso_t.py`: los lotes se ven completos en 390, 820, 1180 y 1440 px, con un código de 17 letras. 21 grupos, 1197 verificaciones, TODO BIEN.

## 1.7.0 · 15 de octubre de 2026

### Corregido (auditoría Parte 2, puntos 13 al 20)
- **13. Fin de temporada:** el README trae una lista de 3 pasos para la veda (respaldo y todo arriba antes del 15 de febrero; revisar el panel de Supabase cada mes y darle «Resume project» si se pausó; confirmar en septiembre antes de prender las tablets).
- **14. iPad/Safari:** resuelto con la copia en IndexedDB de la v1.6.0 (ya no hay límite de 5 MB ni se cuenta doble con emojis o comillas “ ”). El riesgo de que Safari borre la tablet tras 7 días sin abrir la app queda en la lista de la veda.
- **15. Configuración inicial:** la función `usuarios` solo crea el primer Administrador si la base no tiene **ninguna** cuenta. Antes, si alguien borraba a los Administradores desde el panel, cualquiera que abriera la página se volvía Administrador. Mensaje nuevo: «Ya hay cuentas en la base. Para dar de alta un Administrador, pide ayuda a quien administra Supabase.»
- **16. Pruebas sueltas en modo local:** todas las pruebas y Lighthouse usan `?modo=local` por omisión; antes, corridas por separado intentaban entrar a la base real y no probaban nada. `vistas_t.py` ahora sí verifica (nada se sale de la pantalla) y está en `correr_todo.sh`.
- **17. Modo piso, cajas guardadas legibles:** la tarjeta ya no es transparente; «Caja 1» y «✔ Completada» pasan de 2.4–2.5:1 a 4.7–5.3:1 en tema claro (5.7–6.3:1 en oscuro). «Cambiar» (lote) en azul marino en tema claro (13.9:1).
- **18. CSS sin uso:** se borraron 68 reglas de 31 clases (~4 KB). Se comprobó con 252 capturas (todas las pantallas, 3 tamaños, claro/oscuro, texto normal y muy grande) que nada cambia.
- **19. Avisos rojos de 44 px** (antes 23 y 34 px) para tocar con guantes.
- **20. Contraseñas de mínimo 8 caracteres** (antes 6), en la función `usuarios`, en Configuración inicial y en Administración.
- Acceso y Configuración inicial marcados como contenido principal para lectores de pantalla: Lighthouse da 100 en las 15 pantallas.

### Importante
- Los puntos 15 y 20 en la base real necesitan publicar `supabase/functions/usuarios/index.ts` en Supabase (Vercel no lo publica). Ver `docs/SUPABASE.md` §5.

### Pruebas
- `sincronizacion_t.py` (sin Administradores pero con cuentas, contraseñas de 7), `inicio_t.py`, `estados_caja_t.py` (caja guardada sin transparencia), `avisos_t.py` (44 px), `vistas_t.py` (nueva en la lista). 21 grupos, 1173 verificaciones, TODO BIEN; todas pasan también corridas por separado sin indicar la dirección; `rendimiento_t.py` TODO BIEN; Lighthouse 100 en 15 pantallas.

## 1.6.0 · 15 de octubre de 2026

### Corregido (auditoría `/ponytail-audit` de la v1.5.0, puntos 3 al 12; el 1 y el 2 se hicieron en la 1.5.1)
- **3. Las vivas al llegar y las tallas se guardan en el embarque correcto.** Si otro equipo quitaba o unía un embarque mientras escribías, lo capturado se iba a otro embarque. Ahora esos campos y la lista «Unir a otro embarque» usan el id fijo del embarque. Si el embarque ya no existe, avisa «Ese embarque ya no existe: otro equipo lo quitó o lo unió.».
- **4. Amarillo en el packing list y en el informe de cierre.** El PDF del packing list (totales y tabla por cliente), el informe de cierre, la pantalla de Embarque y su PDF cuentan Rojo, Verde, Blanco y **Amarillo**, con una sola función (`byCat`), así que las categorías siempre suman las piezas vivas.
- **5. El PDF de un informe de cierre es el del embarque que se cerró**, aunque haya dos embarques con el mismo nombre. El informe guarda el id fijo del embarque; los informes viejos se siguen buscando por nombre.
- **6. Aviso de cajas de más.** Si dos tablets guardan la última caja de un cliente casi al mismo tiempo y queda una de más, el embarque muestra en rojo «HXH tiene 3 cajas y la orden pide 2 · Resolver ›», que lleva a la vista completa de ese cliente para quitarla.
- **7. La copia de cada equipo ya no se borra con muchas fotos.** Vive en IndexedDB en vez de `localStorage` (cientos de MB en vez de 5): con 45 fotos se guarda completa. Las tablets que ya tenían copia la pasan solas al abrir. Si el navegador no deja guardarla, sale «No se pudo guardar la copia de este equipo» y lo capturado se sigue subiendo.
- **8. Se quitó la subida que no revisaba choques.** Si la base no encuentra la función que revisa choques, el cambio queda pendiente con el aviso «No se pudo subir» en vez de pisar lo de otros equipos.
- **9. «Anular reversa» ya no deja la existencia en negativo** («No se puede anular la reversa: dejaría existencia negativa.») y el mensaje usa el número corto del movimiento.
- **10. La Entrada usa una sola regla en las dos pantallas.** La vista completa y Modo piso crean el lote con la misma función (`addLot`) y la misma revisión (`lotErr`). En la vista completa, −50 kg en una talla ahora marca «No puede ser negativo.» en vez de guardar otro total. Cambio de texto: si falta el lote, la vista completa dice «Escribe el lote.» (antes «Escribe el lote de recepción.»).
- **11. Se borró código que ya no se usaba** (pantallas y botones de versiones anteriores, migraciones ya aplicadas y contadores viejos).
- **12. La prueba de rendimiento mide la base compartida** y falla si guardar una caja o recibir un cambio de otro equipo se vuelve lento.

### Pruebas
- Nuevas verificaciones en `sincronizacion_t.py` (embarque que se recorre mientras escribes, copia en IndexedDB con 45 fotos, paso de la copia vieja, memoria llena, base sin `push`), `pdf_t.py` (Amarillo, informes con el mismo nombre), `avisos_t.py` (cajas de más), `correcciones_t.py` (anular reversa), `entradas_t.py` (Entrada única), `e2e.py` («Unir» con id fijo) y `rendimiento_t.py` (límites).
- `inicio_t.py` revisa la versión 1.6.0 (en la 1.5.1 se quedó revisando 1.5.0 y fallaba).
- 20 grupos, 1156 verificaciones, TODO BIEN; `rendimiento_t.py` TODO BIEN.

## 1.5.1 · 15 de octubre de 2026

### Corregido (segunda auditoría `/ponytail-audit`, puntos 1 y 2)
- **Un registro con valores sin sentido ya no descompone pantallas en todas las tablets.** Antes, una orden con un consignatario que no existe (por ejemplo, el 99) hacía fallar Empaque, la orden y «Empacar cajas» de Modo piso, y una orden con la fecha guardada como número tumbaba el Panel, Órdenes y Empaque. Ahora lo que llega de la base compartida se revisa con las mismas reglas que un respaldo: solo ciudades y consignatarios que existen, mínimo 1 caja por línea, fechas que son fechas, cajas con piezas y con categoría Rojo/Verde/Blanco/Amarillo, movimientos de una talla y tipo válidos y lecturas de temperatura con fecha y tanque. Lo que no se puede usar se ignora en ese equipo (no se sube ni se borra). Lo válido llega exactamente igual que antes (se comprobó con un año de datos: 19,394 registros, cero diferencias).
- **Si una pantalla llega a fallar, la tablet sigue sincronizando.** Antes dejaba de bajar y subir cambios hasta recargar, aunque ya se hubiera borrado el registro malo.
- **Al corregir un registro viejo que se arregló al bajarlo, ya no sale «otro equipo lo cambió».** La app se da cuenta de que en la base está lo mismo, solo escrito distinto, vuelve a subirlo y la base queda arreglada.
- **Cambiar lo mismo dos veces seguidas con internet lento ya no pierde el segundo cambio.** Antes, por ejemplo, tallas 1 y luego tallas 2 en el mismo embarque: quedaba la 1 y salía «No se guardó tu cambio: otro equipo lo cambió antes» aunque nadie más lo había tocado. Ahora queda la 2 y no sale aviso. Si de verdad otro equipo lo cambió antes, gana la base como siempre (y el aviso sale una sola vez).

### Pruebas
- `sincronizacion_t.py` +13 verificaciones: registros con valores sin sentido (A y Modo piso recorren sus pantallas sin fallar, la orden se corrige y se sube sin aviso falso) e internet lento (dos cambios seguidos). `supabase_falso.py` tiene un interruptor `/__lento` (cada subida tarda 2 s). Las pruebas nuevas fallan con la v1.5.0 y pasan con la v1.5.1. 20 grupos, 1114 verificaciones, TODO BIEN.

## 1.5.0 · 14 de octubre de 2026

### Corregido (auditoría `/ponytail-audit`)
- **Seguridad:** los números que llegan de la base compartida (temperaturas, kg por caja, desperdicio, conteo final, vivas, peso de componentes) ahora solo aceptan números. Antes aceptaban texto, y una cuenta de piso podía esconder código en una «temperatura» que corría en la pantalla del Administrador (sobre todo en el tablero de tanques, que es lo primero de Entrada). Se revisó con la base de prueba.
- **Panel:** la tarjeta «En tanques» ya no suma los lotes cerrados; cuenta solo lo que sigue en tanque, igual que el tablero de tanques. Antes crecía para siempre.
- **Empaque:** si cambias de pestaña de lote con cajas escritas sin guardar, ya no se van al otro lote: la app avisa «Primero guarda las cajas del lote …, luego cambia de lote».

### Cambiado (decisiones del cliente)
- **Peso bruto 19.6 kg por caja en todos lados** (hielera 1.4 + gel 1.5 + producto 16 + caja de cartón 0.7). La orden usaba 20 kg; ahora dice lo mismo que el embarque. Ejemplo: 3 cajas = 58.8 kg bruto.
- **La categoría de la caja es su talla**, con los colores de talla: Blanco 491-610, Rojo 611-850, Verde 851-1220 y **Amarillo 1221-UP (nuevo)**. Amarillo aparece en el teclado de Empaque, en «Poner a todas las vacías», en el embarque, en el packing list y en el PDF.
- **Empaque: el lote ya no aparece en cada caja.** Se escoge una vez en **pestañas por lote** arriba de las cajas (como las pestañas de Chrome); en tablet y computadora se quedan a la vista al bajar. Para corregir el lote de una caja guardada, se toca la caja y se cambia junto a «Actualizar caja».
- **La barra de arriba dice dónde estás**, también en tablet y computadora (antes solo en celular). En Empaque agrega el cliente y el lote: «Empaque · LHD · Lote WLRCO051026A».
- **Tablero de tanques en Entrada, como el plano del piso.** Arriba de la tabla, un mapa con los tanques donde están en la planta: T1 a T4 a la derecha (de arriba abajo), T6 a la altura de T3 y T5 a la altura de T4 a la izquierda; arriba a la izquierda, el total en tanques y los colores de talla. Cada tanque muestra sus kg, una barra con los colores de talla, cuántos lotes tiene y la temperatura del agua. Al tocar un tanque, abajo sale su detalle: kg de cada talla, sus lotes (proveedor y días en tanque; al tocar uno se abre) y la última temperatura de agua, superficie y producto (al tocarla lleva a Temperatura). Los tanques sin lotes dicen «Vacío». Cuenta los lotes abiertos con existencia; un lote cerrado ya no aparece. Con la base compartida se actualiza solo cuando otro equipo captura algo («● En vivo»). No muestra qué tan lleno está cada tanque porque falta la capacidad.
- **Ícono de Entrada = una langosta** (la misma del ícono de la app, en blanco) en el menú, la barra de arriba y el Modo piso. Embarque se queda con el camión.
- Teclado de Empaque: en tablet horizontal y computadora las 4 categorías van en 2×2, más grandes para tocar con guantes.
- **Empaque (vista completa): las cajas son tarjetas como en Modo piso** (Caja N, número grande, «piezas», categoría y estado; las completadas con ✓ verde).
- **El teclado se abre y se cierra.** Abierto es la herramienta principal: las tarjetas ya no repiten los botones de categoría, solo muestran la que elegiste. La **X** redonda en la esquina del teclado lo cierra: cada tarjeta trae sus 4 botones de talla y se escribe con el teclado de la tablet. Un **botón flotante con el dibujo de un teclado numérico** (encima de «Guardar cajas», a la derecha) lo vuelve a abrir. Cada equipo recuerda cómo lo dejaste.

### Pruebas
- `e2e.py` (peso bruto), `teclado_t.py` (Amarillo, 4 botones a la vista, sin lote en las filas), `titulo_t.py` (título en todos los tamaños, cliente y lote en Empaque), abrir y cerrar el teclado, `tanques_t.py` (nueva: tablero de tanques) y 3 verificaciones «en vivo» en `sincronizacion_t.py`. 20 grupos, 1101 verificaciones, TODO BIEN.

## 1.4.1 · 14 de octubre de 2026

### Corregido (base compartida)
- **Un equipo que estuvo sin internet ya no deshace lo que guardó otro.** Antes, si piso capturaba algo de un embarque o un lote sin internet y mientras tanto el Administrador lo cerraba, al volver la conexión el embarque o el lote se reabría en todos los equipos. Ahora, si otro equipo cambió lo mismo antes, se queda lo de la base y el equipo que llegó tarde ve «No se guardó tu cambio: otro equipo lo cambió antes. Revisa y vuelve a capturarlo si hace falta.»
- **Consulta ya no borra lo pendiente de otro usuario.** Si piso capturaba sin internet, cerraba sesión y luego entraba alguien de Consulta en esa tablet, lo pendiente se perdía. Ahora espera y se sube cuando vuelve a entrar un Administrador o Piso.

- **Si la base rechaza lo que sube un equipo, ese equipo sigue recibiendo lo de los demás.** Antes se quedaba con datos viejos hasta borrar el navegador. Un texto con un carácter invisible «nulo» (por ejemplo, copiado de un PDF) ya no traba la subida: se limpia solo.

### Corregido (auditoría completa con `/ponytail-audit`)
- **Seguridad: una cuenta de piso ya no puede meter código en la pantalla de otro usuario.** Antes, alguien con la contraseña de piso podía guardar directo en la base un nombre de embarque con código escondido; al abrir Embarques, ese código corría en la pantalla del Administrador y se llevaba su sesión. Ahora todo lo que llega de la base se revisa igual que un respaldo.
- **Fotos más ligeras:** se guardan a 800 px (antes 1280), así caben el doble en cada equipo antes de llenar su memoria. Se siguen viendo bien en la tablet.
- **Aviso «Existencia negativa»** (solo Administrador): si dos equipos registran salidas del mismo lote al mismo tiempo y la existencia queda debajo de cero, aparece un aviso rojo con «Ver lote ›» para revertir la que sobra.
- **La app ya no maneja contraseñas.** Las revisa solo Supabase. Se quitó el cálculo de huellas de contraseña, la lista de contraseñas fáciles y el aviso de «contraseña de prueba», que solo servían en el modo de pruebas. Los respaldos ya no llevan contraseñas.

### Base de datos (ya aplicado en `propesa_bc`)
- Función `public.push` (`20261014b_sin_pisar.sql`): guarda un cambio solo si nadie cambió ese registro antes.
- **Historial** `app_records_hist` (`20261014c_historial.sql`): cada cambio o borrado guarda cómo estaba antes, para poder recuperarlo. Solo lo ve el Administrador. Cómo recuperar: `docs/SUPABASE.md` §7.
- Función `usuarios` versión 2: se quitó un paso repetido al eliminar un usuario (la base ya borraba su perfil).
- **Por aplicar:** `20261014d_quitar_tablas_viejas.sql` borra las 9 tablas vacías del primer esquema. Supabase pide confirmar los borrados. *(Aplicada el 15/oct/2026, ver 1.7.1.)*

### Pruebas
- `sincronizacion_t.py`: 27 verificaciones nuevas (76 en total). 19 grupos, 972 verificaciones, TODO BIEN.

## 1.4.0 · 14 de octubre de 2026

### Agregado: base compartida (Supabase)
- **Todos los equipos y todas las cuentas ven la misma información.** Entradas, movimientos, órdenes, cajas, embarques, informes de cierre, temperatura, notas y fotos se guardan en la base compartida del proyecto `propesa_bc` de Supabase. Antes cada tablet tenía sus propios datos.
- **Usuarios reales:** cada persona entra con su correo y contraseña de Supabase. El Administrador da de alta, cambia y elimina usuarios desde Administración, igual que antes (ahora quedan en la base y sirven en cualquier equipo). Si todavía no hay Administrador, la app muestra la Configuración inicial y lo crea en la base.
- **Se actualiza solo:** cada pocos segundos la app trae lo que capturaron los demás. Si estás escribiendo en un campo, espera a que termines para no borrarte nada.
- **Sin internet se sigue trabajando:** lo que captures se guarda en el equipo y se sube solo cuando regresa la conexión. Mientras tanto aparece el aviso rojo «Sin conexión: lo último que capturaste está guardado solo en este equipo» con «Reintentar ahora».
- Al entrar por primera vez en un equipo aparece «Descargando los datos compartidos…» hasta que llega todo.

### Cambiado
- **Administración → Datos y respaldo:** dice cuándo fue la última actualización con la base y si hay cambios pendientes. «Restaurar respaldo» reemplaza los datos de **todos** los equipos (los usuarios no cambian). «Borrar todos los datos» borra en todos los equipos y conserva los usuarios.
- **Datos viejos de cada tablet:** lo que cada equipo tenía antes **no se mezcla** con la base compartida. En Administración aparece «Datos viejos de este equipo» para descargarlos (y subirlos con «Restaurar respaldo» si hacen falta) o borrarlos.
- La Configuración inicial ya no ofrece restaurar un respaldo (eso ahora se hace en Administración, ya con sesión).
- Los números internos de cajas, movimientos, órdenes, notas y lecturas ya no son contadores de cada tablet (chocaban entre equipos). En la tabla de movimientos de un lote, la columna # ahora cuenta 1, 2, 3… dentro de ese lote.

### Seguridad
- Solo ve datos quien tiene perfil en la plataforma; una cuenta creada fuera de la app no ve nada. **Consulta** no puede escribir (lo bloquea la base, no solo la pantalla). Los perfiles solo los cambia el Administrador.
- La CSP de `vercel.json` permite conectarse únicamente a `https://lktqwmfmdhusscudgflo.supabase.co`.

### Pruebas
- `pruebas/sincronizacion_t.py` (nueva, 49 verificaciones) con un Supabase de mentira (`pruebas/supabase_falso.py`) y hasta 6 navegadores a la vez: configuración inicial, acceso, entradas y órdenes simultáneas, empaque en un equipo y embarque en otro, notas, mismo orden de embarques, sin internet y de regreso, borrar, sesión vencida, consulta sin escritura, piso, alta de usuarios, equipo nuevo, borrar todo, restaurar respaldo, cerrar sesión, y que no haya escrituras de ida y vuelta.
- Las pruebas de pantallas corren en modo local (`index.html?modo=local`, solo en `localhost`). 19 grupos, 953 verificaciones, TODO BIEN.
- Con un año de datos y CPU 4× más lenta: guardar una caja ≈ 85 ms más el dibujo; recibir un cambio de otro equipo ≈ 80 ms.

## 1.3.0 · 13 de octubre de 2026

### Agregado
- **Teclado numérico fijo en Empaque**, en la vista completa y en Modo piso, en tablet, computadora y celular. Pedido del cliente: capturar las piezas de cada caja sin que aparezca y desaparezca el teclado de la tablet.
  - Tablet horizontal y computadora: el teclado va a la derecha de las cajas. Tablet vertical y celular: va abajo y se queda fijo mientras bajas por las cajas.
  - Se toca la caja (o empieza sola en la primera vacía), se escriben las piezas y se toca **Rojo / Verde / Blanco**.
  - **Modo piso:** la categoría guarda la caja y el teclado pasa solo a la siguiente vacía. Las tarjetas ahora son compactas (número grande y categoría) para que quepan junto al teclado; los botones de categoría y «Quitar caja» están en el teclado.
  - **Vista completa:** la categoría marca la fila y pasa a la siguiente; al terminar se toca «Guardar cajas», que ahora va pegado al teclado. Al abrir un cliente, la pantalla baja sola para que se vea el teclado completo.
  - **Corregir:** al tocar una caja guardada, el teclado la abre («Corrigiendo»); el primer número reemplaza al anterior y la categoría guarda la corrección.
  - Botones «‹ Caja anterior» y «Siguiente caja ›». «Siguiente caja» también guarda la caja si ya tenía piezas y categoría (por ejemplo, después de «Poner a todas las vacías»).
  - ⌫ borra un número; «Borrar» deja la caja vacía. Máximo 4 cifras por caja, para evitar errores de dedo (no hay un máximo de piezas por caja).
  - El teclado de la tablet ya no aparece en estos campos. Un teclado físico (computadora) sigue escribiendo normal.
- Al recargar, el teclado regresa a la misma caja.

### Sin cambios
- Reglas de guardado, validaciones, numeración, lotes, PDF y datos. Consulta y embarques cerrados no muestran teclado.

### Pruebas
- `pruebas/teclado_t.py` (nueva, 135 verificaciones). `cajas_auto_t.py`, `estados_caja_t.py`, `recarga_t.py` y `rendimiento_t.py` ahora tocan las categorías en el teclado. 18 grupos, 904 verificaciones, TODO BIEN.

## 1.2.5 · 13 de octubre de 2026

### Cambiado
- **Recargar la página ya no cierra la sesión.** Después de un refresh (o si la tablet cierra el navegador), la app vuelve a la misma pantalla en la que estabas, con lo que estabas escribiendo: el formulario de Entrada a medias, la línea de una orden, una nota sin guardar, las piezas y la categoría de las cajas en Empaque (vista completa y Modo piso) y la hoja de entradas de piso.
- La sesión se cierra sola después de **12 horas sin usar la app**, o cuando tocas «Cerrar sesión» (eso también borra lo que estaba a medias).
- Las fotos de una nota que todavía no se guarda no se conservan al recargar (pesan demasiado para la memoria del equipo); el texto de la nota sí.

### Pruebas
- `pruebas/recarga_t.py` (nueva). `estados_caja_t.py` ahora comprueba que, tras recargar, sigues dentro y en la misma pantalla.

## 1.2.4 · 13 de octubre de 2026

### Cambiado
- **Ícono de la app = una langosta.** La pestaña del navegador, el ícono de «Agregar a pantalla de inicio» (tablet y celular) y el de la app instalada ahora son una langosta roja sobre azul marino. El logo de PROPESA dentro de la app no cambia.
- Los enlaces a los íconos llevan `?v=2` para que los equipos tomen el ícono nuevo. En una tablet que ya tenía la app agregada a la pantalla de inicio puede tardar hasta un día; si no cambia, se quita y se vuelve a agregar.

## 1.2.3 · 13 de octubre de 2026

### Agregado
- **En celular, la barra de arriba dice en qué sección estás.** Junto al botón ☰ aparece el ícono y el nombre de la pantalla (Panel, Entrada, Órdenes, Empaque, Embarque, Mortalidad final, Temperatura o Administración), con el mismo ícono del menú. Los nombres largos se recortan con «…» en lugar de partir la barra.
- En tablet y computadora no cambia nada: ahí ya se ve el menú lateral con la sección marcada.

### Pruebas
- `pruebas/titulo_t.py` (145 verificaciones: 12 pantallas, 390 px claro, 360 px oscuro con texto de 20 px, y que no aparezca en 820 y 1440). 16 grupos, 717 verificaciones, TODO BIEN.

## 1.2.2 · 13 de octubre de 2026

### Cambiado (Empaque → «Cajas de …»)
- **Ya no se confunde el número de caja con las langostas.** Cada fila dice «Caja 3» a la izquierda y el conteo con su unidad a la derecha: «12 piezas ›». El campo de captura trae la palabra «piezas» dentro, a la derecha del número. El encabezado de la columna dice «Caja».
- Filas al estilo de una lista de iOS (referencia que compartió el usuario): título a la izquierda, valor a la derecha, separadores finos y, en tablet vertical y celular, la lista dentro de un recuadro con esquinas redondas. Las cajas completadas caben en una línea («Caja 3 · ● Rojo · 12 piezas ›») con el lote abajo en gris.
- En la caja completada, la flecha › indica que se toca para corregir (se quitó la palabra «Editar» pegada al número).
- **Barra de abajo flotante**, como cápsula con esquinas redondas y sombra suave, con el resumen, la barra delgada y «Guardar cajas».
- En esta pantalla los avisos salen arriba, para no tapar la barra ni las cajas de abajo.

### Sin cambios
- Datos, reglas, validaciones, guardado, avance y PDF. Modo piso igual.

### Pruebas
- `estados_caja_t.py` revisa «Caja N» / «N piezas» en cada fila y que el aviso no tape la barra (143). 15 grupos, 572 verificaciones, TODO BIEN.

## 1.2.1 · 13 de octubre de 2026

### Cambiado (solo presentación de Empaque → «Cajas de …», vista completa)
- **Estados más discretos:** Pendiente, En captura, ✔ Completada, Editando y ⚠ Incompleta ya no son pastillas de color; son texto pequeño con un indicador (círculo, medio círculo, palomita, punto). La caja completada se nota por la palomita, el texto verde tenue y un tinte verde suave en la fila.
- **Rojo / Verde / Blanco** ahora es un control segmentado compacto: las tres opciones del mismo tamaño, con punto de color pequeño; la elegida lleva fondo claro y borde de acento (sin el azul lleno). Siguen midiendo 44 px de alto para tocar con guantes.
- **Lotes:** en lugar de pastillas grandes, un selector horizontal con el lote arriba y «Tanque · kg» abajo; el elegido lleva borde y línea de acento. En celular se desliza de lado.
- **Tabla:** separadores finos en lugar de renglones alternados, encabezados en una sola línea, números alineados a la derecha. En las cajas completadas, el número de piezas es un botón discreto «Editar 20» (mismo ancho que el campo); tocar la fila también la abre.
- **Fila en corrección:** marco delgado de acento y botones más compactos (Actualizar caja N, Cancelar con borde, Quitar caja en gris).
- **Barra de abajo:** «✔ N completadas · N pendientes» y «N % completado», una barra delgada que avanza con las cajas guardadas y el botón Guardar a la derecha con **tamaño fijo** (ya no crece). Al 100 % dice «✔ N de N cajas completadas». Los avisos ahora salen arriba de la barra y no la tapan; al saltar a un campo, la barra no lo cubre.
- **Pantallas angostas:** en tablet vertical cada caja ocupa dos renglones (número · piezas · categoría / lote) y en celular una columna, según el ancho real de la tarjeta y el tamaño de letra. Sin desplazamiento lateral en 390, 641, 820, 1024, 1180 y 1440 px, también con letra de 20 px (salvo el selector de lotes, que se desliza a propósito).
- Aviso «✔ Esta línea ya tiene todas sus cajas» como texto verde, sin pastilla.

### Sin cambios
- Mismos datos, reglas, validaciones, cálculo de avance, guardado y PDF. Modo piso igual que en la 1.2.0.

### Pruebas
- `pruebas/estados_caja_t.py` ahora con 137 verificaciones (barra delgada, botón de tamaño fijo, aviso que no tapa la barra, categorías del mismo tamaño). 15 grupos, 566 verificaciones, TODO BIEN.

## 1.2.0 · 13 de octubre de 2026

### Agregado
- **Empaque: cada caja muestra en qué va.** En la tabla de cajas (vista completa) cada fila lleva su estado con ícono y texto: **Pendiente** (gris), **En captura** (cian, ya escribiste algo pero falta guardar), **✔ Completada** (verde) y **Editando** (azul, con marco). Una caja solo queda «Completada» cuando se guardó con piezas, categoría y lote; tocar un color ya no basta.
- **Las cajas guardadas se quedan en la misma tabla**, en verde, arriba de las que faltan. Ya no hay una segunda tabla abajo con las mismas cajas.
- **Corregir una caja completada:** toca la fila o «Editar». Se abre con sus valores (piezas, categoría y, si hay varios lotes, lote) y abajo aparecen «Actualizar caja N», «Cancelar» y «Quitar caja». Enter actualiza y Esc cancela. Se corrige la misma caja (mismo número), nunca se crea otra. Si dejas las piezas vacías, la caja pasa a «⚠ Incompleta» y no se guarda hasta que esté bien; lo guardado no se pierde.
- **Barra de avance abajo:** «✔ N completadas · N pendientes · N % completado» y el botón Guardar crece con el avance real (al 0 % tiene su tamaño mínimo; al 100 % llena el espacio y dice «✔ N de N cajas completadas»). El ancho sale de las cajas guardadas y crece suave desde el valor anterior, sin mover el resto de la pantalla.
- El botón dice cuántas cajas va a guardar («Guardar 3 cajas») en lugar de «Guardar cajas (3)», para no confundirlo con las que faltan. Si hay una caja en corrección, «Guardar» también la guarda.
- **Modo piso:** las cajas guardadas dicen «✔ Completada» con borde verde; al tocar una para corregirla dice «Editando» con borde azul; una caja que empezaste y no se ha guardado se marca en cian. Arriba: «Completadas N de N» y «N pendientes · N % completado».

### Corregido
- En celular con texto «Muy grande», los botones de lote de Empaque ya no se salen de la pantalla.

### Sin cambios
- Datos: no hay campos nuevos en `ST` (completada = caja guardada), así que no hay migración y el estado se conserva al recargar. Mismas reglas, numeración de cajas, PDF y packing list. Quitar sigue pidiendo confirmación.

### Pruebas
- `pruebas/estados_caja_t.py` (119 verificaciones, 390/820/1440 px, tema claro y oscuro, Modo piso y rol consulta). `inicio_t.py` revisa la versión 1.2.0. 15 grupos, 548 verificaciones, TODO BIEN. La tabla de cajas mide lo mismo que antes en 641, 820, 1024 y 1440 px (también con texto de 20 px).

## 1.1.2 · 13 de octubre de 2026

### Cambiado
- **El PDF del Plan de embarques ahora trae el dibujo del camión**, igual al de la pantalla Embarque: cola y cabina, las 10 celdas con las hieleras de cada una y el color de cada embarque. Debajo va la lista de colores con el nombre de cada embarque abierto. Si la carga no cabe, el PDF muestra el aviso rojo con cuántas hieleras sobran; si no hay embarques abiertos, dice que el camión está vacío.
- Es el mismo PDF de «Descargar PDF» y de «Enviar por correo».
- El acomodo de las hieleras se calcula en un solo lugar para la pantalla y el PDF, así que siempre coinciden.

### Pruebas
- `pruebas/pdf_t.py` revisa que el Plan de embarques traiga el camión (11 verificaciones). `inicio_t.py` revisa la versión 1.1.2. 14 grupos, 429 verificaciones, TODO BIEN.

## 1.1.1 · 13 de octubre de 2026

### Corregido
- **Tabla de Entrada más fácil de leer.** Los encabezados de las 4 tallas ya no se parten en pedazos: cada uno muestra el rango principal arriba (0-650, 651-850, 851-1250, 1251-UP) y el secundario abajo (491-610, 611-850, 851-1220, 1221-UP), con el punto de color a un lado. Las columnas de talla y sus kilos van centradas.
- Los demás encabezados ya no se cortan palabra por palabra: «Kg por caja / en tanque», «T°F / tanque», «T°F / producto» y «Kg / desperdicio» van en dos renglones fijos; el resto en uno. Encabezados alineados abajo y números alineados a la derecha.
- Si la tabla no cabe, se desliza de lado dentro de su tarjeta (la página y el menú no se mueven). No se achicó la letra.
- Solo cambió la presentación: textos, datos, cálculos y el PDF son los mismos.

### Pruebas
- `pruebas/tabla_entrada_t.py` (45 verificaciones). 14 grupos, 427 verificaciones, TODO BIEN.

## 1.1.0 · 13 de octubre de 2026

### Cambiado
- **Modo piso → Registrar entrada ahora es una hoja de captura.** Ya no se abre un asistente por cada entrada: todas las entradas se ven y se editan en una sola pantalla, una fila por lote (proveedor, tanque, lote, kg de las 4 tallas y kg total). «+ Agregar entrada» crea una fila nueva al instante y pone el cursor en su primer campo.
- Temperaturas, kg por caja en tanque, desperdicio, fecha y hora quedan en «Más» de cada fila (el botón muestra cuántos datos tiene llenos).
- **Guardar entradas** guarda cada fila por separado: las que tienen errores se quedan en rojo con el mensaje junto al campo y las demás se guardan. Un doble toque no duplica lotes. Cada fila muestra su estado: Vacía, Sin guardar, ⚠ Revisar o ✔ Guardada; las guardadas se quedan en pantalla, bloqueadas.
- Aviso rojo «N entradas tienen datos por corregir · Revisar ›» que lleva al primer campo con error. Tab o Enter pasan al siguiente campo; Enter en el último campo crea otra fila.
- Encabezados de la tabla fijos al bajar; en celular, en tablet vertical y con texto «Muy grande» cada fila se vuelve tarjeta.
- Lo capturado sin guardar se conserva al ir a Inicio o cambiar de modo; el botón «Registrar entrada» del Inicio avisa «N sin guardar».
- Las reglas de guardado son las mismas de la Entrada de la vista completa (proveedor, tanque, lote único, al menos una talla con kg, fecha). Nuevo: una talla con kg negativos se marca en rojo en lugar de ignorarse.

### Pruebas
- `pruebas/entradas_t.py` (58 verificaciones) y `piso_t.py` actualizado. 13 grupos, 382 verificaciones, TODO BIEN. Lighthouse accesibilidad 100 en la nueva pantalla.

## Sin publicar (documentación, 12/oct)

### Documentación
- `CLAUDE.md`, `AGENTS.md` y carpeta `docs/` con todo el contexto del proyecto (producto, UX, marca, arquitectura, datos, decisiones, roadmap, pruebas, seguridad, Supabase, flujo de trabajo, historial) y `docs/referencias/` con los formatos en papel.
- `.claude/settings.json` registra el plugin agent-skills para Claude Code.
- La app (`index.html`) no cambió.

## 1.0.0 · 12 de octubre de 2026

Primera versión para uso diario.

### Nuevo
- **Configuración inicial:** un equipo nuevo pide crear la cuenta del Administrador; ya no vienen usuarios de ejemplo.
- **Temperatura:** bitácora real por tanque (agua, superficie, producto en °F) con fecha, hora y quién capturó.
- **Informes de cierre** en Administración, con PDF para descargar o enviar por correo.
- **Borrar los datos de este equipo** (confirmación escribiendo BORRAR).
- Versión visible en el menú del perfil.
- Encabezados de seguridad en Vercel: CSP, HSTS, Permissions-Policy, COOP; `index.html` sin caché para que las actualizaciones lleguen al recargar.

### Cambiado
- Se quitaron todos los textos, datos y botones de demostración.
- Lista ampliada de contraseñas prohibidas por ser fáciles de adivinar.
- Accesibilidad: Lighthouse 100 en las 14 pantallas (contraste del botón rojo, encabezados de tabla, etiquetas en el conteo final, orden de títulos).

### Incluye lo construido antes
Flujo Entrada → Órdenes → Empaque → Embarque → Mortalidad final; Modo piso con tarjetas que se guardan solas; avisos que llevan al lugar del problema; PDF de cada paso; ajustes de tema y tamaño de texto; menú del perfil; respaldo y restauración con limpieza de datos; rendimiento probado con un año de datos.
