# Cambios

## 1.32.0 · 3 de noviembre de 2026

Pedido del usuario (3/nov): «que mi pantalla de inicio de sesión se vea como esta» (captura de otra plataforma: marca con una vista previa de la app y el formulario). Después pidió: tanques con canastas pero no tan llenos, las canastas como las de verdad, los filtros y todo como en la plataforma, el lado blanco en azul, quitar «Plataforma marítima» del acceso y un botón para iniciar sesión en vez de desplazarse, con el correo y la contraseña saliendo de lado.

### Cambiado
- **Nuevo acceso.** Toda la pantalla: logo, «Cada lote de langosta, de la entrada al embarque.», el flujo Entrada → Órdenes → Empaque → Embarque, el botón blanco **«Iniciar sesión»** y una vista previa de Panel general que se sale por la orilla. Sin desplazarse en ningún tamaño.
- **El formulario sale de lado** (cajón azul a la derecha; en celular ocupa toda la pantalla): «Iniciar sesión», «Bienvenido de nuevo…», Correo, Contraseña, Entrar (blanco), qué hacer si olvidaste la contraseña y la versión. Se guarda con ✕, Escape o tocando afuera. Llegar a un campo con el teclado o el administrador de contraseñas también lo abre. Si hay un aviso (sesión cerrada) ya sale abierto.
- **La planta de la vista previa es el mismo dibujo de «Planta en 3D»** (`t3Inner`): tanques, filtros con barandal amarillo, paredes, cortinas, letreros y placas TANQUE 1–6, con 142 canastas de muestra fijas (T5 vacío) y la cámara quieta. Es un dibujo: no usa datos, no se puede tocar y el lector de pantalla lo ignora. No cambia el estado de la planta real.
- **Ojo para ver la contraseña** (también en Configuración inicial, uno por campo).
- Configuración inicial usa la misma pantalla, con el formulario ya abierto (botón «Crear Administrador»).
- Sin «Plataforma marítima» en el acceso (ahora «Acceso por rol» / «Primer uso»).

### Pruebas
- Nueva `acceso_t.py` (botón y cajón de lado, sin desplazarse, dibujo real de la planta, canastas, ojo, Enter, tamaños 390/820/1180/1440, texto «Muy grande», tema oscuro, Configuración inicial). `inicio_t.py`: versión 1.32.0.

## 1.31.4 · 3 de noviembre de 2026

Pedido del usuario (3/nov): el sitio público vive en `propesa.org` y su botón «Iniciar sesión» manda a la plataforma en `app.propesa.org`.

### Cambiado
- **Vista previa al compartir el link:** ahora apunta a `https://app.propesa.org/` (antes `https://propesa.org/`, que pasa a ser el sitio público).

### Pruebas
- `vista_previa_t.py`: espera `app.propesa.org`. `inicio_t.py`: versión 1.31.4.

## 1.31.3 · 3 de noviembre de 2026

Pedido del usuario (3/nov): «dentro de los tanques, si selecciono un lote, que se guarden los demás para poder ver qué lote es el que seleccioné; y que toda la caja cambie de color para que resalte».

### Cambiado
- **Tanques en 3D · tocar una canasta:** se guardan (dejan de verse) las canastas de los demás lotes del tanque y las del lote elegido se pintan completas de azul (con su listón de talla encima). Solo quedan los letreros de ese lote y de su maquila.
- La tarjeta de la canasta trae **«Ver todas las canastas»** para volver a ver todo (también ✕, tocar otro tanque o «Ver toda la planta»).
- Si en un lugar hay varias capas de canastas, la caja se queda y se pinta cuando alguna de sus capas es del lote elegido.

### Pruebas
- `tanques3d_t.py`: se guardan los demás lotes (también con dos lotes en el mismo tanque), color de la canasta elegida, letreros, «Ver todas las canastas». `inicio_t.py`: versión 1.31.3.

## 1.31.2 · 3 de noviembre de 2026

Pedido del usuario (3/nov): «lo del andén de recepción y de selección y lavado no me gustó que sean anuncios flotantes; ponlo en la pared y que no se mueva».

### Cambiado
- **Tanques en 3D:** «ANDÉN DE RECEPCIÓN» y «SELECCIÓN Y LAVADO» ahora son letreros pegados a la pared, a la izquierda de su cortina (como en las fotos de la planta). Ya no flotan ni giran con la cámara; se esconden con su pared cuando la pared estorba la vista.

### Pruebas
- `tanques3d_t.py`: los dos letreros van en la pared, no en la capa de letreros. `inicio_t.py`: versión 1.31.2.

## 1.31.1 · 3 de noviembre de 2026

Pedido del usuario (3/nov): «en el panel general el tanque 3D sea lo primero que se muestre».

### Cambiado
- **Panel general:** la planta en 3D va hasta arriba, justo debajo del título, antes de los totales, la tabla por maquila y el tablero de tanques. El tablero plano y su detalle siguen donde estaban.

### Pruebas
- `tanques3d_t.py`: el 3D está arriba de los totales y las tablas del Panel general. `inicio_t.py`: versión 1.31.1.

## 1.31.0 · 2 de noviembre de 2026

Pedido del usuario (2/nov): «un tablero de tanques en 3D como mi piso real, con las cajas adentro, y que al tocar un tanque la cámara se acerque». Plan, fotos y decisiones en el proyecto (`claude/PLAN_TANQUES_3D.md`); prototipo aprobado el 2/nov.

### Agregado
- **Planta en 3D** arriba del tablero de tanques, en **Entrada** (la maquila abierta) y en **Panel general** (todas las maquilas). El tablero plano y su detalle siguen abajo igual.
- La planta como es: T1–T4 en una columna con su filtro elevado (plataforma blanca, barandal amarillo) en el extremo este; T6 y T5 junto a T3 y T4; T5 con filtro al oeste y T6 sin filtro; área de recepción con «Andén de recepción» y «Selección y lavado».
- **Canastas** en cada tanque, calculadas: kg de cada talla de cada lote ÷ «kg por caja en tanque» del lote. Llevan el **listón del color de la talla de su maquila** (si una maquila tiene su talla y color, sale con ese color). Incompleta = borde punteado. Lote que pasó los días de su proveedor = borde rojo; último día = ámbar. Si en un lugar hay más de una capa, se ve una caja más alta.
- Encima de cada tanque: canastas, kg y **días del lote más viejo**.
- **Tocar un tanque:** la cámara se acerca, elige ese tanque en el tablero de abajo (mismo detalle de siempre) y enseña un letrero por maquila y uno por lote con sus días. «‹ Ver toda la planta» (o Esc) regresa.
- **Tocar una canasta:** lote, maquila (en Panel general), talla, kg, proveedor y días en tanque, y «Abrir lote ›». Se marcan las demás canastas de ese lote.
- **Mover la vista:** un dedo gira e inclina; dos dedos mueven y acercan; con mouse, rueda y clic derecho; botones de 48 px ⟲ ⟳ + − ⌂.
- «Ocultar 3D» / «Ver tanques en 3D» (se recuerda en cada equipo).
- Lote sin «kg por caja en tanque»: aviso rojo «… no tiene kg por caja en tanque · Completar ›» que lleva al lote.

### Cómo está hecho
- Sin librerías: transformaciones 3D de CSS (`t3View`, `t3Data`, `t3Inner`). Letreros en una capa plana encima, colocados con la misma cámara (`t3Proj`): no se esconden por errores de orden del navegador y se leen nítidos. La cámara se anima con código (respeta «movimiento reducido»).
- Para Android y iPad: ninguna pieza cruza a otra, cada caja dibuja solo los lados que ve la cámara, la profundidad crece con el acercamiento y la escena no se vuelve a armar si no cambió nada.
- Sin cambios en los datos ni en Supabase.

### Pruebas
- Nueva: `tanques3d_t.py`. `rendimiento_t.py` mide Entrada con y sin 3D (un año de datos, CPU 4×: +28 ms; límite +40 ms). Actualizada: `inicio_t.py` (versión 1.31.0).

## 1.30.1 · 2 de noviembre de 2026

Pedidos del usuario (2/nov).

### Arreglado
- **Corregir una hielera ya guardada con el teclado:** la letra del color + Enter ahora sí guarda el color nuevo (en la vista completa se quedaba como estaba). También con piezas nuevas. Vista completa y Modo piso.

### Agregado
- **Hojas para imprimir con vista previa:** cada hoja enseña su primera página tal como sale en el PDF (la dibuja el mismo código). Tocarla la agranda; tocarla otra vez la achica.
- **Paquete de cada orden** (en Hojas para imprimir): «Descargar paquete» baja un .zip con la orden (con su hoja de empaque), el packing list, el informe de cada embarque y el plan de carga del camión mientras el embarque siga abierto.

### Pruebas
- Nueva: `v1301_t.py`. Actualizada: `inicio_t.py` (versión 1.30.1).

## 1.30.0 · 1 de noviembre de 2026

Pedido del usuario (1/nov): «la cuenta de consulta o cliente no debería de mirar información sensitiva; solo es para que puedan ver qué hay y vender, no mis precios ni mis maquilas». Etapa 1 del plan de construcción.

### Cambiado
- **Consulta y Cliente son una sola cuenta: «Solo inventario».** En Administración → Usuarios se elige el rol y las maquilas que ve (una o varias). Entra a «Disponible», **en español**: kilos y hieleras por talla de esas maquilas, **sumados y sin decir de qué maquila son**, y lo recibido en 7 días. No ve ninguna otra pantalla.
- Una cuenta sin maquilas no ve inventario («Pídele al Administrador que te lo asigne»). Una cuenta de Consulta vieja se trata igual.
- Cada maquila tiene su hoja de disponible (antes solo PROPESA).

### Base compartida (aplicada el 1/nov/2026 con permiso del usuario)
- `supabase/migrations/20261101_solo_inventario.sql`: columna `mq` en perfiles; la cuenta de solo inventario solo lee las hojas de sus maquilas y su propio perfil, sin fotos; las cuentas Consulta pasan a Solo inventario con PROPESA. Ensayada en la base real dentro de una transacción que se deshizo: Consulta pasa de leer 279 registros a 1; piso y Administrador sin cambios.

### Pruebas
- Nueva: `v130_t.py` (pantalla, alta con maquilas, suma de dos maquilas, sin datos sensibles, y con la base de mentira: solo le llega la hoja de su maquila). `supabase_falso.py` imita las reglas nuevas. Actualizadas las pruebas que usaban la Consulta vieja.

## 1.29.0 · 1 de noviembre de 2026

Pedidos del usuario después de probar la plataforma (1/nov).

### Arreglado
- **«Crear orden» se quedaba sin formulario.** Si se tocaba «Editar» en una orden y se salía sin guardar ni cancelar, la siguiente orden nueva no enseñaba «Destino y consignatario» (y «Falta el destino · Agregar» no llevaba a nada). Ahora lo abierto en una orden no pasa a otra.
- **El aviso de arriba se encimaba en la barra de arriba** (Modo piso y celular): ahora sale siempre debajo de la barra y encima de todo lo demás.

### Agregado
- **Llenar hieleras solo con el teclado** (vista completa y Modo piso): tocar la hielera → escribir las piezas → la letra del color (**R** Rojo, **V** Verde, **B** Blanco, **A** Amarillo; la primera letra del nombre del color de la maquila) → **Enter** guarda y pasa a la siguiente. La letra solo elige; Enter guarda. Con mouse, cada botón de color enseña su letra.
- **Piezas empacadas:** «55 piezas empacadas» junto a «completadas · pendientes» (Empaque y Modo piso) y en «Lo que falta por empacar» de la orden.
- **Cambiar el consignatario de una línea aunque ya tenga hieleras empacadas** («Editar consignatario u hieleras» en la orden). Las hieleras se van al embarque del nuevo consignatario; no deja poner uno que ya está en la orden ni pasar a un embarque cerrado.
- **Atajos para editar la orden:** «Cambiar consignatario o editar la orden ›» en Empaque y «Cambiar ›» junto al consignatario en la hoja de empaque. En Órdenes el botón dice «Abrir o editar».

### Cambiado
- **Hoja de empaque:**
  - Hora inicial y final en **12 h con a. m./p. m.** («730» se escribe 7:30). Se sigue guardando en 24 h; la tarjeta, el correo y el PDF la enseñan en 12 h.
  - **Placas** en mayúsculas mientras se escriben.
  - **Tanques de origen** se tocan (T1…T6, se pueden varios) en vez de escribirse. La app sigue proponiendo los de los lotes empacados.
  - **Al completarla se cierra** con una animación corta y queda una tarjeta: horas, quién realizó, evaluación y placas, con «✔ Hoja de empaque completa» y «Ver o corregir hoja».
- **Embarque · «Mover hieleras»:** se hace en el camión mismo: el dibujo se vuelve las 10 celdas para tocar (cola a la izquierda, cabina a la derecha) y lo de la celda elegida sale pegado al camión. Ya no sale otra cuadrícula abajo.

### Pruebas
- Nueva: `v129_t.py`. Actualizadas: `hoja_t.py` (hora en 12 h, hoja que se cierra), `inicio_t.py` (versión 1.29.0).

## 1.28.1 · 29 de octubre de 2026 (incluida el 1/nov en la 1.29.0)

### Arreglado
- **Aviso falso «No se pudo guardar la copia de este equipo · La memoria del navegador está llena».** La memoria no estaba llena: el navegador (sobre todo el iPad al dormir o quedar en segundo plano) cierra su conexión con la memoria del equipo y la app seguía usando la conexión cerrada. Ahora abre una nueva y vuelve a guardar. El aviso solo sale si de verdad no se puede guardar.
- Prueba en `v129_t.py`: con la 1.28.0 falla («The database connection is closing») y ahora pasa.

## 1.28.0 · 29 de octubre de 2026

Pedido del usuario (29/oct): quitar la gris del teclado de Empaque y tener otro lugar para agregar hieleras grises, como extra.

### Cambiado
- **La categoría Gris (despatada) ya no se elige al empacar:** salió del teclado, de los botones de cada hielera y de «Poner a todas las vacías» (vista completa y Modo piso). Sigue existiendo en Entrada, tanques, Mortalidad final y precios.

### Agregado
- **Hieleras grises · extra**, abajo de las hieleras del cliente (vista completa y Modo piso): se escriben las piezas y «+ Agregar hielera gris». Sale del lote elegido arriba. Quitar pide confirmación.
  - **No cuentan para las hieleras pedidas:** la línea sigue «1 de 4» y se completa sin ellas; en Modo piso no ocupan lugar. En «Hieleras por talla» sale «+ 1 hielera gris extra».
  - **Sí van con el cliente:** en el packing list (con su número de hielera), en las hieleras, tallas y peso bruto del embarque (con el mismo peso por hielera de la línea), y sus kilos salen del tanque (despatada) al cerrar el embarque.
- Ojo: una hielera gris empacada antes de esta versión ahora cuenta como extra (si una línea la usaba como pedida, vuelve a decir que falta 1).

### Pruebas
- Nueva: `v128_t.py`. Actualizada: `inicio_t.py` (versión 1.28.0).

## 1.27.1 · 29 de octubre de 2026

Pedido del usuario (29/oct): «Hieleras por talla» más visual y colorido, y que diga qué falta empacar.

### Cambiado
- **Hieleras por talla** (al empacar y en la orden) ya no es una tabla de «Pedidas / Empacadas»:
  - Arriba, un aviso grande: «Faltan 3 hieleras por empacar · Empaca: 1 Chica · 1 Grande · 1 Jumbo», con una ficha del color de cada talla, el conteo «1 de 4 empacadas» y una barra de avance pintada por talla. Azul mientras falta, verde con «✔ Ya están todas las tallas», rojo si hay hieleras de más (y aun así dice lo que falta).
  - Una tarjeta por talla, teñida con su color: nombre, gramaje, «1 de 1» y «Falta N», «✔ Lista» o «⚠ De más +N». Un cuadrito por hielera: lleno con ✓ = empacada, punteado = falta, rojo con + = de más. Con más de 24 hieleras en una talla se ve una barra.
  - Usa los colores de talla de cada maquila (Administración → Tallas). Claro y oscuro; en celular se esconde el gramaje.

### Pruebas
- Nueva: `v1271_t.py`. Actualizada: `inicio_t.py` (versión 1.27.1).

## 1.27.0 · 29 de octubre de 2026

Pedidos de la junta con el usuario (29/oct). «Cooperativa» = maquila: tallas y colores por maquila (Administración → Tallas), Mortalidad final aparte por maquila, el Panel general con todas y «+ Nuevo consignatario» **ya existían**; no se tocaron.

### Agregado
- **Lo más viejo primero en Empaque.** Los lotes salen del más viejo al más nuevo (por fecha de entrada) y el primero con kilos queda elegido, con «Más viejo · usar primero». Se puede cambiar. En Modo piso se sigue preguntando «¿De qué lote sacas las langostas?», con el más viejo primero y marcado «usar primero».
- **Días máximos en tanque por proveedor** (Administración → Proveedores; vacío = sin límite). Si un lote los pasa: aviso rojo en el lote con «Ir a Empaque», notificación, y en Empaque sale antes que los demás con «⚠ 5 días · aguanta 3». En su último día dice «Último día en tanque» y también va primero.
- **Orden variada:** en la línea de la orden, «Repartir tallas: lo más viejo primero» llena las hieleras por talla con lo más viejo de los tanques (descuenta lo que otras órdenes ya pidieron). Se pueden cambiar antes de guardar. Si no alcanza, dice cuántas sí.
- **Máximo 35 langostas por hielera**: no se guarda una hielera con más (vista completa, Modo piso y al corregir; avisa al guardar).

### Pruebas
- Nueva: `v127_t.py`. Actualizadas: `cajas_auto_t.py` (40 y 50 piezas → 34 y 35), `estados_caja_t.py` (corregir a 34 piezas), `teclado_movil_t.py` (55 → 25 piezas), `inicio_t.py` (versión 1.27.0).

## 1.26.0 · 29 de octubre de 2026

Dos pedidos del usuario: los camiones en pestañas con su propio PDF y una campana de notificaciones.

### Agregado
- **Camiones en pestañas.** Con dos camiones o más, arriba del plan de carga sale una pestaña por camión (como las del navegador): se ve un camión a la vez, con sus consignaciones abiertas y **su propio PDF** («PDF del Camión 2», archivo `Plan_de_carga_Camion_2`). «Pasar a → Camión nuevo» abre la pestaña del camión nuevo. Con un solo camión, la pantalla y el PDF quedan como antes. Los embarques cerrados siguen abajo, fuera de las pestañas.
- **Notificaciones (campana con contador)** en el encabezado, en la vista completa y en Modo piso. Trae, de la maquila abierta:
  - **Falta capturar o resolver:** entradas con fecha, hora o código por revisar; existencia negativa (Administrador); órdenes sin líneas o con hieleras por empacar; pendientes de cada embarque (peso, tallas, hoja de empaque, salida incompleta…); embarques ya empacados que falta cerrar. No se descartan: se quitan solos al resolverlos.
  - **Recientes · 7 días:** entradas y órdenes nuevas, y embarques cerrados.
  - Tocar una lleva a donde se resuelve. Lo reciente queda visto al tocarlo o con «Marcar todo como visto» (se guarda en el equipo, por usuario). El contador = pendientes + recientes sin ver.

### Pruebas
- Nueva: `v126_t.py`. Actualizadas: `camiones_t.py` y `v125_t.py` (un camión a la vez, en pestañas), `inicio_t.py` (versión 1.26.0).

## 1.25.0 · 27–28 de octubre de 2026

Prueba de la v1.24.0 con los Excel de Martha **capturados por la pantalla** (77 recepciones, 54 envíos con 3,728 hieleras una por una, 62 salidas) y pedidos del usuario.

### Agregado
- **Una orden con hieleras de varias maquilas.** En Empaque salen aparte los lotes «De otra maquila» (con «MAQUILA DAVID»). Al cerrar el embarque los kg salen del tanque de esa maquila (y reabrir los regresa). El lote de la otra maquila enseña «En órdenes de otra maquila»; tocarlo entra a su maquila.
- **Panel general: tanques de todas las maquilas juntas** (mapa T1–T6; al tocar un tanque, cada maquila con sus tallas y lotes).
- **Otro tanque con kg exactos por talla** en la entrada (vista completa y Modo piso). Ya no se reparte solo.
- **Camión compartido entre maquilas**: el plan de carga junta los embarques abiertos de todas; «Pasar a» funciona entre maquilas.
- **Fecha en las salidas** (congelar, basura, recuperación, débil): el Balance de un periodo pasado ya las cuenta.
- **Cambio de talla** en el lote (resorteo en el tanque) para resolver la «salida incompleta»; luego «Volver a descontar».
- **Aviso de código de lote mal escrito** (p. ej. WLRCOO51026 o sin la clave del proveedor) y se puede corregir el código mientras el lote no tenga hieleras.
- **Rangos de temperatura internos** (28–29/oct), sacados de las temperaturas del Excel. **Agua:** Óptimo hasta 57 · Normal 57.1–60 · Advertencia 60.1–62 · Alerta 62.1–64 · Crítico más de 64 °F. **Producto:** Óptimo hasta 60 · Normal 60.1–63 · Advertencia 63.1–66 · Alerta 66.1–68 · Crítico más de 68 °F. Advertencia en ámbar; Alerta y Crítico en rojo con aviso. En Temperatura (con la tabla, y la de la industria como referencia), tablero de tanques, al guardar entrada o lectura y en el PDF.
- **La orden ya no pide hieleras de Despatada** (29/oct): es merma. En Empaque se sigue pudiendo marcar una hielera Gris; las órdenes viejas que la pedían la siguen enseñando.
- **Despatada = merma** en Mortalidad final (28/oct): esperado para el conteo final sin despatada; merma = mortalidad + despatada recibida, en % de lo recibido (lote, tabla, gráficas, Modo piso y PDF).

### Corregido
- «Camión nuevo» con un solo embarque no hacía nada: ahora sale apagado («va solo»).
- «Langostas vivas al llegar» solo enseñaba los últimos 30 envíos: ahora todos.
- PDF de Envíos de Abel contaba cajas ÷ 16: ahora con el kg de producto (÷ 15).

### Pruebas
- Nueva: `v125_t.py`. Actualizadas: `traslados_t.py` (kg por talla), `avisos_entrada_t.py` (aviso de código), `inicio_t.py` (versión 1.25.0), `ordenes_t.py` y `temperatura_t.py` (rangos), `salidas_t.py` (esperado sin despatada). **56 grupos, ~2,860 verificaciones, TODO BIEN** (`fotos_t` a veces falla en la corrida completa por tiempos de la base de mentira; sola pasa).
- Prueba con los Excel por la pantalla en la v1.25.0: `docs/PRUEBA_EXCEL_v1.25.0.md` (balance 17–27 sep = 88.27 a favor).

## 1.24.0 · 27 de octubre de 2026

Cinco pedidos del usuario: logotipo de cada maquila, vivas al llegar en Revisión, ver qué falta por empacar, juntar/separar embarques claro y los colores de las consignaciones.

### Agregado
- **Logotipo de cada maquila.** Emblema con sus iniciales (Abel: hexágono ámbar «A»; David: círculo turquesa «D»; Luis Arce: escudo lila «LA»; una maquila nueva toma el siguiente) + «MAQUILA» + el nombre. Va en el menú (con una franja de su color arriba), en el encabezado de Modo piso, en el celular (barra de arriba; tocarlo cambia de maquila), en «Cambiar de maquila», en el Panel general y en Administración → Maquilas. PROPESA conserva su logo.
- **Lo que falta por empacar.** La orden tiene arriba «Lo que falta por empacar»: cada consignatario con lo que falta por talla (p. ej. «Falta: 1 Chica · 3 Mediana · 1 Grande · 1 Jumbo») y su botón para empacar; «✔ Todo empacado» cuando ya está. Órdenes y Empaque también dicen lo que falta por talla en cada renglón.

### Cambiado
- **Langostas vivas al llegar al destino** (con el % que reporta el cliente y la temperatura de arribo) se captura en **Revisión → Mortalidad final**, un renglón por envío. El embarque ya no lo captura: avisa y lleva ahí («Ir a Mortalidad final ›»).
- **Juntar y separar embarques en un solo lugar: el embarque.** «Órdenes en este embarque» tiene «Sacar de este embarque» en cada orden y «Puedes juntar aquí» con las órdenes del mismo destino y consignatario. Antes de cambiar nada enseña **Ahora → Así queda** (hieleras y nombre de cada embarque) con «Sí, juntar / Sí, sacarla» o «Cancelar»; después dice qué pasó y deja **Deshacer** (y «Ver el embarque nuevo ›»). La orden ya no tiene selector ni «Unir»: dice en qué embarque va y lleva a él.

### Corregido
- **Los colores de las consignaciones no coincidían con Administración.** Sin color elegido, cada embarque tomaba un color por turno (dos del mismo consignatario podían salir distintos) y Administración enseñaba otro. Ahora el color se toma siempre del consignatario, el mismo que enseña Administración, en Embarque, el plan del camión, Modo piso y Revisión; también en los embarques cerrados y cuando otro equipo cambia el color.
- Tocar el campo «Temperatura de arribo» volvía a dibujar la pantalla y lo cerraba.

### Pruebas
- **55 grupos, 2,793 verificaciones, TODO BIEN.** Nueva: `v124_t.py`. Actualizadas: `e2e.py`, `envios_t.py`, `maquilas_t.py`, `sincronizacion_t.py`, `generar_datos.py`. `inicio_t.py` revisa la versión 1.24.0.

## 1.23.0 · 26 de octubre de 2026

Pedido del usuario: «necesito que el nombre de la maquila esté en grande y que sea claro distinguir».

### Cambiado
- **PDF: la maquila en grande.** Debajo del logo, una banda azul marino con «MAQUILA» y el nombre en letras grandes (PROPESA, ABEL, DAVID, LUIS ARCE) y «Datos solo de esta maquila». En las demás páginas, «MAQUILA ABEL» en una etiqueta azul arriba a la derecha. Ya no va escondido en el subtítulo.
- Formato 06 (hoja de empaque) en el PDF: las columnas de talla también van a color.

### Pruebas
- `pdf_tallas_t.py` revisa la banda; `excel_reales_t.py` busca «MAQUILA ABEL». `inicio_t.py` revisa la versión 1.23.0. **54 grupos, 2,722 verificaciones, TODO BIEN.**

## 1.22.0 · 26 de octubre de 2026

Pedido del usuario: «quiero que en los pdf salga el color respectivo de cada talla y también gramaje… determinado a cada maquila… que toda la tabla sea de cada color respectivo para que sea más visual».

### Agregado
- **Leyenda de tallas en los PDF:** arriba de cada PDF con tallas (Entrada, Órdenes, Packing list, Embarque, Recepción, Envíos, Existencia, Congelación) sale una tarjeta por talla con su color, nombre, gramaje (p. ej. «611-850 g») y nombre del color. Son las tallas de la maquila del PDF: si Abel tiene Chica café de «26-32 piezas», su PDF lo dice así.
- **Tablas a color:** cada columna de talla (y de categoría: Rojo, Verde, Blanco…) lleva el encabezado de su color y toda la columna teñida de ese color; el total, un poco más fuerte. En Órdenes, cada renglón de talla va de su color; en el detalle por hielera y en Congelación, la celda de categoría o talla va de su color.

### Corregido
- El gramaje solo lleva «g» cuando es un rango de números (antes salía «26-32 PIEZAS g»).

### Pruebas
- Nueva: `pdf_tallas_t.py` (PROPESA y Abel con tallas propias). `inicio_t.py` revisa la versión 1.22.0. **54 grupos, 2,720 verificaciones, TODO BIEN.**

## 1.21.0 · 26 de octubre de 2026

Respuestas del usuario a la segunda tanda de preguntas (6, 9, 12 y 15).

### Agregado
- **Lotes por envío.** El embarque tiene la tabla «Por lote»: hieleras, langostas, kg de producto y tallas de cada lote, con total; cada lote lleva a su pantalla. También en el PDF del embarque (sección «Por lote») y en el informe por correo al cerrar.
- **Modo piso · Cerrar embarque paso a paso.** Elegir embarque → revisar hieleras (con lo que va de cada lote) → pendientes (cada uno con su botón) → cerrar. Solo el Administrador cierra; el piso ve «Avísale al Administrador». La hoja de empaque incompleta sigue solo preguntando.
- **Modo piso · Conteo final paso a paso.** Elegir lote (con lo esperado) → kg contados en una casilla grande (Enter avanza; no acepta más de lo esperado) → confirmar con la mortalidad → «✔ Conteo guardado» con «Contar otro lote», «Corregir» y, para el Administrador, «Cerrar lote».
- Cambiar de modo te deja en lo mismo: Embarque ↔ Cerrar embarque, Mortalidad final o un lote ↔ Conteo final.

### Decidido
- Cerrar con la hoja de empaque incompleta **solo pregunta** (pregunta 9). Órdenes de fechas distintas en un embarque: **se permiten sin aviso** (pregunta 12).

### Corregido
- En Modo piso, las tarjetas grandes de cliente y de lote mostraban un recuadro azul detrás del nombre (el estilo de la pantalla de compradores se aplicaba ahí también).

### Pruebas
- Nueva: `piso_pasos_t.py`. `inicio_t.py` revisa la versión 1.21.0.

## 1.20.0 · 26 de octubre de 2026

Respuestas del usuario a las preguntas pendientes («hazme las preguntas para continuar»): balance de Luis Arce igual que el de PROPESA, los tres avisos, sin rango de temperatura por ahora, y especie en cada orden.

### Agregado
- **Aviso: fecha que no cuadra con el código del lote.** Si la fecha de entrada no es la del código (WLR + clave + ddmmyy; p. ej. WLRCO220926 capturado el 22/06), sale en rojo en el lote y en Entrada. El Administrador toca «Corregir ›» (abre la edición) o «Está bien así». También se avisa al guardar (vista completa y hoja de Modo piso); no bloquea.
- **Aviso: hora de madrugada.** Una entrada entre 00:00 y 04:59 pregunta «¿fue a las 13:30?». Mismo lugar y mismos botones. «Está bien así» se recuerda con la fecha u hora aceptada: si se vuelve a cambiar a otra rara, avisa otra vez.
- **Aviso: salida incompleta.** Al cerrar un embarque, lo que no se pudo descontar del tanque (lote sin entrada, lote ya cerrado o sin kilos suficientes) queda anotado y sale como pendiente del embarque, con el lote, la talla, los kg y el motivo; lleva al lote. Después de corregir la entrada, «Volver a descontar del tanque» lo vuelve a intentar sin descontar doble. Reabrir el embarque lo borra. El embarque cerrado con pendiente sigue a la vista en la lista aunque sea viejo.
- **Especie en cada orden.** Con más de una especie, la orden nueva pide la especie (las de antes son Langosta Roja). Al empacar, en la vista completa y en Modo piso, solo salen los lotes abiertos de esa especie; los lotes sin entrada o «sin lote» que se crean al empacar toman la especie de la orden. La especie se cambia en la orden mientras no tenga hieleras. La lista de órdenes, el PDF de órdenes y la hoja de empaque dicen la especie.
- **Hoja de los compradores por especie:** lo pedido (con tallas y sin tallas) ya resta de su especie; antes solo restaba de los totales por talla.

### Decidido
- **Balance de Luis Arce:** se queda la fórmula del balance de PROPESA (cuenta despatada y congelados); la hoja de Luis Arce del Excel tenía el error (pregunta 21).
- **Rango de temperatura:** sigue sin rango por ahora (pregunta 11).

### Datos
- `R.av` (avisos aceptados, `'f:<fecha>'` / `'h:<hora>'`), `P.sf` (lo que faltó descontar: `[lote, talla, gramos, ne|c|b]`, solo en embarques cerrados), `OR.sp` (especie de la orden). Están en `WN`, `cleanST` y `decodeST`. Sin cambios en Supabase.
- `D/disp.s` lleva un tercer dato por especie: lo apartado sin talla.

### Pruebas
- Nuevas: `avisos_entrada_t.py` y `especie_orden_t.py`. `inicio_t.py` revisa la versión 1.20.0. **52 grupos, 2,620 verificaciones, TODO BIEN.**

## 1.19.0 · 26 de octubre de 2026

Pedidos del usuario después de probar la app con los dos Excel que usa Martha (`RECEPCION_Y_ENVIOS_LANGOSTA_2026-27` y `RECEPCIONES_DE_LANGOSTA_2026-2027`).

### Agregado
- **Maquilas separadas.** PROPESA, Abel, David y Luis Arce (lista editable en Administración → Maquilas). Cada maquila tiene sus propios lotes, movimientos, órdenes, hieleras, embarques, informes y notas: **no se mezclan**, y el mismo código de lote puede estar en dos maquilas (16 de los 19 lotes de Abel tienen el código de un lote de PROPESA). Se comparten usuarios, proveedores, especies, consignatarios, destinos, pesos de la hielera y temperatura de los tanques.
- **Cambiar de maquila tocando el logo** (menú y Modo piso). En PROPESA y en el Panel general se ve el logo de PROPESA; **en otra maquila, su nombre va en lugar del logo** (pedido del usuario).
- **Panel general** (solo el Administrador; es a donde entra al iniciar sesión): todas las maquilas juntas (kg en tanques, recibido en 7 días, hieleras empacadas, embarques abiertos, total) y una tabla de tanques con los kg de cada maquila. «Entrar ›» abre cada una.
- **Tallas de cada maquila** (Administración → «Tallas de <maquila>»): nombre, rango (491-610 o «26-32 piezas»), color (el del tape y la categoría de la hielera), nombre del color y nombre en inglés; agregar y ocultar. Entrada, hoja de Modo piso, tablero de tanques, orden, empaque, embarque, PDF y compradores usan las tallas de la maquila abierta.
- **Despatada como talla** (gris): entra al tanque, se pide en la orden, se empaca y sale al cerrar el embarque. «Kg desperdicio» se queda como estaba.
- **Salidas que no son embarque** en cada lote: para congelar, basura (descompuesta), a recuperación y débil, con nota o folio. Restan del tanque y ya no cuentan como mortalidad. Totales y lista en Mortalidad final y en su PDF.
- **Consignatarios y destinos editables** (Administración): nuevo consignatario (clave, razón social, destinos, dirección, contacto, USCI), editar, ocultar; nuevo destino (ej. TPE · Taipéi), editar, ocultar.
- **% de mortalidad que reporta el cliente y temperatura de arribo** en cada embarque (también cerrado). Salen en Mortalidad final y en los PDF.
- **Precio de compra** en cada lote: USD por kg, USD por kg de despatada, facturado o sin factura, nota y total en dólares. **Solo el Administrador, también en la base**: el precio va en su propio registro (`$/<lote>`) y la base no se lo da ni se lo deja escribir a Piso, Consulta ni Cliente (migración `20261026_precios.sql`, **aplicada en `propesa_bc` el 26/oct** con permiso del usuario; comprobado ahí: Piso y Consulta ven los lotes y 0 precios, el Administrador los ve, Piso no puede escribir un precio y sí lo demás).
- **Lotes en varios tanques y traslados**: en la Entrada (vista completa y hoja de Modo piso) «Otro tanque» con sus kg, su temperatura y sus kg por caja (como «1/2», «57.6/60.3», «34/36» del Excel). En el lote, «Pasar a otro tanque» (kg o todo) con lista y «Deshacer». El tablero de tanques, el Panel general y la hoja de existencia reparten los kilos de cada lote por tanque (tallas en proporción); las salidas y los embarques se toman primero del tanque principal.
- **Hojas para imprimir** (menú → Revisión): las hojas del Excel de Martha en PDF, de la maquila abierta y del periodo elegido: Recepción, Envíos, Existencia en tanques por tallas (cajas de 16 y de 15 kg), Congelación y no apta, Precio de compra (solo el Administrador) y Balance (con la existencia física contada).
- Los PDF de otra maquila dicen «Maquila <nombre>» y su archivo lleva el nombre; conservan el logo de PROPESA (decisión del usuario).

### Decidido
- **Sin tape por envío** (se probó y se quitó el mismo día): el color del embarque es el de su consignatario, como en la v1.15.0. Pedido del usuario: «el color ya va con cada consignatario».

### Corregido
- Datos de consignatarios contra la lista en papel: teléfono (+86 13691775559) y código postal (518000) de Yishunhai, USCI de Xinbang (91440101MA9UUJN96Y). Yishunhai también va a XMN (11 envíos del Excel).

### Datos (sin cambios en Supabase)
- Maquilas: `ST` es la maquila abierta (`MQ`); las demás viven en `STX`. Los registros de PROPESA conservan su clave (`R/<lote>`); los de otra maquila llevan prefijo (`q2:R/<lote>`). Nuevos registros compartidos `Q/<id>` (maquilas), `K/<n>` (consignatarios) y `X/<código>` (destinos); por maquila `Z/tallas`. `L.type` acepta `CONGELACION`, `BASURA`, `RECUPERACION`, `DEBIL` y `L.nt`; `P.ta`, `P.mc`; precio en `R.pr` que viaja como `$/<lote>`; traslados `ST.TQ` como `TQ/<id>`. `D/disp` sale solo de PROPESA y trae los nombres de sus tallas (`n`). El respaldo trae todas las maquilas (`_X`, `_MQ`). Detalle en `docs/DATOS.md`.

### Pruebas
- Nuevas: `maquilas_t` (también con dos equipos y el Supabase de mentira), `tallas_t`, `salidas_t`, `consignatarios_t`, `envios_t` (% del cliente y arribo), `hojas_t`, `precios_t` (precios solo para el Administrador, con el Supabase de mentira), `traslados_t` y **`excel_reales_t`**: carga los datos reales del Excel (`pruebas/datos/excel_reales.json`, sin precios) y compara cada número de las hojas con las fórmulas del Excel. **50 grupos, 2,541 verificaciones, TODO BIEN.**
- `ordenes_t` usaba la fecha fija 17/10/2026 (ya fuera de los 7 días): ahora usa ayer. Las pruebas que esperaban 4 tallas ahora esperan 5 (Despatada); las del logo y de atrás siguen el menú de maquilas y el Panel general. `fotos_t` a veces falla dentro de la tanda completa por tiempo (también en la 1.18.0); sola pasa.

## 1.18.0 · 24 de octubre de 2026

### Agregado
- **Especie en cada entrada.** El formulario de Entrada y la hoja de entradas de Modo piso piden la **especie** (Langosta Roja de inicio). En la hoja de Modo piso va debajo del proveedor («Proveedor y especie»). Se ve en la tabla de Entrada, en el lote y en los lotes de cada tanque; se corrige con «Editar». Los lotes de antes son Langosta Roja. Pedido del usuario.
- **Administración → Especies** (solo el Administrador): agregar, editar el nombre y el nombre en inglés (el que ven los compradores) y ocultar. Una especie oculta ya no se ofrece en nuevas entradas; sus lotes la conservan.
- **Kilos por especie.** El tablero de tanques separa los kilos de cada tanque por especie y talla (con sus hieleras de 15 kg) y arriba suma cada especie en todos los tanques. La pantalla de los compradores dice qué especies hay («Live red lobster and blue lobster…») y, con más de una, agrega «In our tanks by species» por talla.
- **PDF:** el Registro de recepción (Entrada) trae la columna «Especie». La Hoja de empaque (Formato 06) toma la especie de los lotes empacados en la orden (antes siempre «Langosta Roja»), en pantalla, PDF y correo.

### Corregido
- La clase de las casillas de temperatura de la v1.17.1 (`tqv`) era la misma que la de «Vacío» en el detalle del tanque y le cambiaba el ancho. Ahora se llama `tqin`.

### Decisiones (ver `docs/DECISIONES.md`)
- Las órdenes **no llevan especie**: lo pedido que no ha salido resta de los totales por talla, no de una especie. Los kilos por especie de los compradores son lo que hay en tanques.

### Datos
- `ST.ES` (opcional) = `[{id, n, en, off}]`; sin ella se usa `ES0` (Langosta Roja). `R[].sp` (opcional) = id de la especie; sin `sp` = especie 1. En `cleanST`, `WN.E`/`WN.R`, `encodeST` y `decodeST`; viajan como registros `E/<id>` y dentro de `R/<lote>`. La hoja `D/disp` agrega `s` = [[nombre en inglés, g por talla]]. **Sin cambios en Supabase.**

### Pruebas
- `especies_t.py` (nueva, 94 verificaciones): Administración (agregar, repetido, editar, ocultar, la última no se oculta, Consulta no cambia), Entrada en vista completa y Modo piso, editar la especie, lotes de antes, tablero de tanques por especie, PDF de Entrada, Formato 06 (pantalla, PDF y correo), hoja de compradores y su pantalla, registros compartidos, respaldo, sin desbordes en 1180 y 390 px y en 820 px oscuro con texto de 20 px. `inicio_t` (versión 1.18.0). 41 grupos.
- `entradas_t.py`: Enter en el proveedor pasa a la especie y de ahí al tanque. `temperatura_t.py`: usa la fecha de ayer en vez del 16/10/2026 fijo (desde el 24/oct quedaba fuera de la lista de 7 días y la prueba fallaba también en la versión anterior).

## 1.17.1 · 23 de octubre de 2026

### Cambiado
- **Temperatura en Modo piso con casillas grandes.** En «Nueva lectura», dentro de Modo piso, el tanque, la fecha, la hora, las tres temperaturas, «Hoy», «Ahora» y «Guardar lectura» miden 60 px de alto, con números más grandes y casillas más anchas, para usarlas con guantes. La vista completa se queda igual. Pedido del usuario.

### Pruebas
- `piso_t.py`: en Modo piso todas las casillas y botones de «Nueva lectura» miden 60 px o más y los números 20 px o más; la vista completa conserva sus casillas de 130 px. Revisado en 390, 820 y 1440 px, con texto «Muy grande» y en tema oscuro, sin desbordes. `inicio_t` (versión 1.17.1).

## 1.17.0 · 23 de octubre de 2026

### Agregado
- **Temperatura en Modo piso.** Un quinto botón en el inicio de Modo piso, «Temperatura», con cuántas lecturas van hoy («2 lecturas hoy» / «Sin lecturas hoy»; cuenta también las temperaturas de las entradas). Abre la misma pantalla de Temperatura de siempre dentro del Modo piso (sin menú, con «Inicio»): «Nueva lectura», la tabla de los últimos 7 días, el PDF y las fotos. Mismos permisos que antes: Administrador y Encargado de piso capturan; Consulta solo ve. En tablet y computadora el botón va a todo lo ancho debajo de «Cerrar embarque» y «Conteo final». Pedido del usuario (con `/ponytail ultra`).

### Pruebas
- `piso_t.py`: el botón sale con el conteo de hoy y a todo lo ancho, abre Temperatura dentro de Modo piso, guarda una lectura, sin desborde, en 1180 y 390 px. `inicio_t` (versión 1.17.0). 40 grupos.

## 1.16.0 · 23 de octubre de 2026

### Agregado
- **Historial de cambios en Administración.** Una tarjeta «Historial de cambios» con el botón «Ver cambios recientes»: lista los últimos 200 cambios de los últimos 30 días, lo más nuevo arriba, con **cuándo**, **quién**, **qué** (Creó / Cambió / Borró y qué registro: lote, hielera, orden, embarque, temperatura…) y **el cambio** campo por campo («Temp. tanque: 58 → 60»). Solo el Administrador; solo con la base compartida. No pide nada a la base hasta tocar el botón. Pedido del usuario: «ver quién, cuándo y qué valor se cambió… que no ocupe espacio en la base, memoria corta, para arreglar errores».

### Base compartida
- **Sin tabla nueva:** usa `app_records_hist` (v1.4.1), que ya guardaba cada versión anterior. Migración `supabase/migrations/20261023_historial_corto.sql`: el historial **se borra solo después de 30 días**, la hoja de disponibilidad `D/disp` (la recalcula la app) ya no entra al historial, y la función `cambios(lim)` arma la lista (solo devuelve filas al Administrador). Antes: 114 versiones, 112 kB de una base de 12 MB. **Aplicada en `propesa_bc` el 23/oct** con permiso del usuario (no borró nada: lo más viejo era del 16/oct); revisado ahí que un Administrador recibe la lista (187 cambios) y una cuenta Consulta, ninguno.

### Pruebas
- `historial_t.py` (nueva): con el Supabase de mentira, Piso crea un lote y el Administrador lo cambia y borra una lectura; la lista muestra quién, qué y «58 → 60», sin `D/disp`; Piso no recibe nada aunque lo pida directo; aviso sin internet; 1440/820/390 px con texto de 20 px, tema oscuro, botón de 44 px; no sale en modo local. `supabase_falso.py` guarda versiones anteriores y responde `rpc/cambios`. `inicio_t` (versión 1.16.0). 40 grupos.

## 1.15.0 · 23 de octubre de 2026

### Agregado
- **Color de cada consignatario.** Administración → «Consignatarios»: un selector de color por consignatario (el color de su tape). Al cambiarlo, sus embarques abiertos se pintan de ese color en Embarque, en el plan del camión y en los PDF; los embarques nuevos de ese consignatario nacen con él. Los cerrados conservan su color. Mientras no se elija, todo se ve como antes. Solo el Administrador. Pedido del usuario; resuelve la pregunta abierta 10.

### Datos
- `ST.CC` (opcional) = {índice del consignatario: '#rrggbb'}, en `cleanST`, `WN.C`, `encodeST` y `decodeST`. Se comparte como el registro `C/colores`: sin cambios en Supabase.

### Pruebas
- `colores_t.py` (nueva): tarjeta, selector de 44 px o más, abierto toma el color y cerrado no, embarque nuevo, Embarque lo pinta, viaja como `C/colores`, valores malos se ignoran, respaldo, otro rol no lo cambia; en 1440/820/390. `inicio_t` (versión 1.15.0). 39 grupos.

## 1.14.0 · 23 de octubre de 2026

### Agregado
- **Varios camiones.** Embarque muestra un plan de carga por camión (Camión 1, Camión 2…). En cada camión, junto a cada consignación, «Pasar a» la cambia de camión o abre un «Camión nuevo» (solo el Administrador). Las consignaciones nuevas llegan al Camión 1. Los datos de antes se ven igual: todo en un solo camión. Pedido del usuario.
- **Mover hieleras dentro del camión.** «Mover hieleras» abre las 10 celdas en botones grandes (cola a la izquierda, cabina a la derecha): tocar una celda y luego otra las intercambia; con una celda elegida se escribe cuántas hieleras de cada consignación lleva, para dividir una tarima. Avisos en rojo si faltan o sobran hieleras de una consignación o si una celda pasa su capacidad, con «Acomodar lo que falta» y «Volver al acomodo automático». Administrador y Encargado de piso. El acomodo automático es el de siempre (desde la cabina).
- **«Embarques cerrados» aparte.** En Embarque, las consignaciones abiertas y las cerradas salen en secciones separadas; las cerradas dejan el camión.
- El PDF del Plan de embarques trae un plan por camión, con sus avisos.

### Datos
- `P[].tk` (camión) y `P[].ly` (hieleras por celda, 10 números), opcionales, en `cleanST`, `WN.P` y `decodeST`. Viajan dentro de `P/<u>`: sin cambios en Supabase.

### Pruebas
- `camiones_t.py` (nueva): el automático da lo mismo que antes (300 combinaciones), camión nuevo y regresar, intercambiar, dividir, avisos, capacidad, celdas de 44 px o más, sin scroll de lado en 1180/820/390, cerrados aparte, Consulta sin controles, datos compartidos y limpios, PDF con dos camiones. `inicio_t` (versión 1.14.0). 38 grupos, TODO BIEN.

## 1.13.3 · 23 de octubre de 2026

### Cambiado
- **Los pesos de la hielera se editan solo en Embarque.** Se quitó la tarjeta «Peso de la hielera» de Administración; ahora se cambian en Embarque → «Peso del embarque» → «Editar pesos» (solo el Administrador), que es donde se usan. El panel ahora muestra el producto por omisión y el total por hielera (se actualiza al escribir) y que aplica a todos los equipos y a los embarques abiertos. Pedido del usuario. Sin cambios en datos ni en cómo se calcula el peso.

### Pruebas
- `pesos_t.py`: Administración ya no tiene la tarjeta; todo se edita desde «Editar pesos» en Embarque. `inicio_t` (versión 1.13.3). 37 grupos, TODO BIEN.

## 1.13.2 · 22 de octubre de 2026

### Corregido
- **Al compartir el link, la vista previa ya apunta a propesa.org.** Las etiquetas `og:url`, `og:image` y `twitter:image` decían `propesa.vercel.app`, así que WhatsApp, Facebook y Slack mandaban a la dirección de Vercel. La imagen (`og-image.png`) es la misma.

### Documentación
- **`docs/ROADMAP.md` puesto al día con el código.** Se había quedado en la v1.4.0 y marcaba como pendientes cosas que ya funcionan: base compartida (Auth, reglas por rol, sincronización), ids estables, historial de cambios en la base, editar y eliminar órdenes, salida de kilos al cerrar el embarque (pregunta 3, resuelta). Quedan como pendientes reales el correo con PDF (pregunta 16), importar datos viejos, la pantalla del historial, las alertas de temperatura (pregunta 11) y la ocupación de tanques (pregunta 17).

### Pruebas
- `vista_previa_t.py`: las etiquetas usan propesa.org y el encabezado ya no menciona `vercel.app`. `inicio_t` (versión 1.13.2).

## 1.13.1 · 22 de octubre de 2026

### Corregido
- **Empaque (vista completa) con el teclado abierto: las hieleras completadas ya muestran su categoría** (● Verde, ● Rojo…) además de «✔ Completada». Antes la categoría se ocultaba en las completadas y solo se veía más abajo. Pedido del usuario.

### Cambiado
- **Empaque (vista completa): el avance «✔ N completadas · N pendientes · N % completado» y su barra van arriba de las hieleras, quietos**, justo debajo de «Hieleras de …». Antes flotaban abajo, debajo del teclado. «Guardar hieleras» se queda abajo. Pedido del usuario.

### Pruebas
- `categoria_completada_t.py` (nueva): con el teclado abierto, dos hieleras completadas muestran Verde y Rojo; el avance está arriba de las hieleras y no se mueve al desplazar; sin desbordes, en 390/820/1440 px. 37 grupos.

## 1.13.0 · 22 de octubre de 2026

Modo para compradores de fuera (China): ven en vivo lo que hay en los tanques para hacer ventas.

### Nuevo
- **Rol «Cliente (comprador)».** El Administrador lo da de alta en Administración como cualquier usuario. Al entrar ve una sola pantalla **en inglés**, sin menú: **Available stock** (kilos por talla Small / Medium / Large / Jumbo, con hieleras de 15 kg aproximadas y el total disponible), **Received in the last 7 days** (kilos recibidos por día y talla) y «Live · last change hace X min». Se actualiza sola cada pocos segundos.
- **Disponible = lo que hay en tanques menos lo pedido que todavía no sale.** Una orden aparta sus hieleras (por talla) hasta que su embarque se cierra. Lo pedido sin tallas sale como «Reserved, size not assigned yet» y solo resta del total.
- **Al cerrar un embarque, sus hieleras salen solas del tanque** (decisión del usuario del 22/oct; antes la salida se registraba a mano). Un movimiento «Salida a embarque» por lote y talla, con los kg de producto de su orden. El aviso dice cuántos kg salieron. **Reabrir** el embarque regresa esos kilos. Nunca deja un lote en negativo; los lotes cerrados o sin entrada no se tocan.

### Seguridad (base compartida)
- **La cuenta Cliente solo puede leer su hoja de disponibilidad.** La base no le entrega proveedores, lotes, tanques, órdenes, consignatarios, notas, fotos ni los datos del personal, aunque los pida directamente. Migración `supabase/migrations/20261022_cliente.sql` y función `usuarios` con el rol nuevo, **aplicadas en `propesa_bc` el 22/oct** con permiso del usuario. Administrador, Piso y Consulta ven lo mismo que antes.
- De paso, el espacio de archivos «reportes» (vacío) ya solo lo ven Administrador, Piso y Consulta; antes lo podía ver cualquier cuenta.

### Pruebas
- `disponible_t.py` (nueva): cálculo de la disponibilidad, salida automática al cerrar y al reabrir, lote que no queda en negativo, línea sin tallas, pantalla en inglés sin datos internos (390/820/1440 px, claro y oscuro, texto de 20 px), y con un Supabase de mentira: el Cliente solo recibe su hoja y su perfil, no puede escribir, ve los cambios en vivo, y dos Administradores a la vez no se pisan la hoja. 36 grupos, 2020 verificaciones, TODO BIEN; rendimiento con un año de datos dentro de los límites.

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
