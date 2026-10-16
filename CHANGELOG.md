# Cambios

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
