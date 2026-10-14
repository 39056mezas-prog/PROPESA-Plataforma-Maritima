# Cambios

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
