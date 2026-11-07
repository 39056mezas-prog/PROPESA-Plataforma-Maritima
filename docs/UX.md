# UX.md · Cómo debe sentirse la plataforma

## 1. Para quién diseñamos

Un empleado de piso, de pie, moviéndose, con guantes o manos mojadas, con poca luz, que mira la tablet un segundo. Debe entender al instante:

1. ¿Dónde estoy?
2. ¿Qué estoy haciendo?
3. ¿Qué necesita mi atención?
4. ¿Qué ya está completo?
5. ¿Hay un problema?

El usuario lo resume así: que sea **tan fácil como la caja de McDonald's** (ver `docs/referencias/investigacion_mcdonalds.txt`).

## 2. Principios (de la investigación de McDonald's)

| Principio | En PROPESA |
|---|---|
| **Cero fricción** | Cada acción es un botón grande al frente. Nada de menús anidados ni buscar. Flujo lineal. |
| **Rejilla densa y fija** | Botones grandes en lugares que no se mueven, para crear memoria muscular. Las cajas de Modo piso tienen lugar fijo (`b.ps`). |
| **Revelación progresiva** | Solo se muestra lo del paso actual: cliente → lote → cajas. Si hay un solo lote, se salta ese paso. |
| **A prueba de errores (poka-yoke)** | El sistema no deja avanzar sin lo necesario y explica qué falta. No se pueden empacar más cajas de las pedidas, ni un conteo mayor a lo esperado. |
| **Se entiende sin leer** | Íconos + colores constantes (ROJO / VERDE / BLANCO; colores de talla) + texto corto. |

## 3. Reglas de interacción

- **Los avisos rojos llevan a donde se resuelven.** Chip, tarjeta o renglón de alerta = botón: «Faltan N · Empacar ›», «Sin líneas · Agregar ›», «Resolver ›». Si el problema es un campo, se hace scroll, se enfoca y se resalta (`data-jump`). Toda notificación nueva debe seguir esta regla.
- **Corregir tiene que ser fácil.** Una caja guardada se queda en pantalla. En Modo piso queda con ✔ Completada y borde verde, y se edita ahí mismo o se quita (con confirmación). En la vista completa queda en verde en la misma tabla; tocarla o «Editar» la reabre con sus valores («Actualizar caja N», «Cancelar», «Quitar caja»). Nada desaparece después de guardar.
- **Cada caja dice en qué va** (indicador + texto pequeño, sin pastillas de color): Pendiente (gris, círculo vacío) · En captura (círculo a medias, cian) · ✔ Completada (verde tenue, fila con tinte verde suave) · Editando (punto cian y marco delgado) · ⚠ Incompleta (rojo, al corregir). Completada = guardada con piezas, categoría y lote; tocar un color no basta.
- **El avance va arriba y quieto (v1.13.1, pedido del usuario: no le gustaba que flotara debajo del teclado):** «✔ N completadas · N pendientes · N % completado» y una barra delgada (cian) que avanza con las cajas guardadas, justo debajo de «Hieleras de …». Abajo, junto al teclado, solo queda «Guardar hieleras». El botón Guardar **no** cambia de tamaño (se probó en la v1.2.0 y se cambió en la v1.2.1 por pedido del usuario). Los avisos (toast) salen arriba de la pantalla.
- **Empaque, estilo sobrio (v1.2.1, pedido del usuario):** referencia iOS para la tabla de cajas: separadores finos, Rojo/Verde/Blanco como control segmentado compacto (mismo tamaño, seleccionado = fondo claro con borde de acento, sin azul saturado), lotes como selector horizontal (se desliza de lado en celular), números alineados a la derecha. Cada fila es como una celda de lista de iOS (v1.2.2): a la izquierda «Caja N» con su estado, a la derecha el valor con su unidad («12 piezas ›»; el campo dice «piezas» dentro), para que el número de caja y el conteo no se confundan. La barra de abajo es una cápsula flotante (bordes redondos y sombra suave) y los avisos salen arriba en esta pantalla. En esta pantalla el número de pendientes va en gris, no en rojo: el rojo queda para errores y la categoría Rojo. Solo aplica a la tarjeta de cajas (`.pkx`); el Modo piso conserva sus botones grandes.
- **Teclado fijo en Empaque (v1.3.0, pedido del cliente):** en la vista completa y en Modo piso hay un teclado numérico siempre visible (botones de 48 px o más) con las categorías debajo de los números (o a un lado en pantallas angostas). El teclado de la tablet ya no aparece (`inputmode="none"`), así no tapa las cajas; un teclado físico sigue funcionando. En la vista completa la categoría marca la fila y pasa a la siguiente; se guardan todas con «Guardar cajas», que va pegado al teclado. Al abrir un cliente la pantalla baja sola lo justo para ver el teclado completo.
- **Se guarda solo cuando se puede.** En Modo piso cada caja se guarda al tener piezas y categoría (`peTry`), sin botón «Guardar». Si otro equipo ocupa el lugar donde estás escribiendo, lo escrito pasa al siguiente lugar libre y se avisa; nunca se cambia una hielera que no tocaste (v1.38.1).
- **Varias cosas a la vez.** Los empleados anotan varias cajas a la vez: se muestran todas las cajas pendientes del cliente, no una por una. «Poner a todas las vacías» aplica una categoría de un toque.
- **Los formularios no borran lo escrito** cuando hay un error: se marca el campo en rojo, se enfoca y se explica.
- **Confirmar solo lo destructivo:** quitar caja, eliminar lote, restaurar respaldo, borrar datos (este último exige escribir BORRAR).
- **El logo siempre regresa al inicio**, en cualquier modo.
- **Cambiar de modo** con un interruptor tipo iOS y una transición suave (sin animación si el equipo pide movimiento reducido).
- **Listas cortas:** solo lo abierto o reciente (lotes 30 días, órdenes y embarques 14, temperatura 7) con «Ver historial».
- **Mensajes:** un toast breve al guardar; nunca «Guardado» si el guardado falló (aviso rojo fijo con «Descargar respaldo» y «Reintentar»).

## 3b. Herramienta de formatos (v1.33.0)

- La vista completa abre en **Formatos** («¿Qué formato vas a llenar?»): tarjetas que abren cada formato directo, solo las que el rol puede llenar. Sin orden fijo; el menú no lleva números y las guías dicen «Formato».
- Lo que falta (lote sin entrada) es recordatorio gris, no alarma.
- **Empaque en iPad:** teclado a un lado de las hieleras (desde 34rem de ancho del área); las hieleras siempre se ven. Las teclas cuentan al levantar el dedo.
- **Eliminar orden** arriba junto al título y también con hieleras (confirmación con cuántas). **Entrada:** Ver · Editar · Eliminar en cada fila.

## 3c. Pantallas limpias (v1.34.0, pedido del usuario: «demasiados campos, no se sabe por dónde empezar»)

- **Cada sección empieza en lo que se hace:** título, una línea y la acción principal arriba a la derecha (`guide()`). Nada de recuadros azules con explicaciones largas ni etiquetas «Formato/Guía».
- **Una sola acción azul por pantalla.** PDF y correo son botones discretos (`.btn.q`).
- **Lo secundario se pliega** (`fold()`): fotos y notas, tanques y planta 3D en Entrada, tanques, precio y movimientos del lote, desglose del peso bruto, «¿Cómo se calcula?». El resumen del plegable dice lo importante sin abrirlo (kg, total, número de notas). Lo abierto se queda abierto mientras se usa; una nota con algo escrito sin guardar se abre sola.
- **Nada vacío que ocupe pantalla:** sin gráficas «Sin datos»; una línea basta.
- Al agregar algo nuevo a una sección: si no es lo que la mayoría viene a hacer ahí, va plegado.

## 3d. Detalles ordenados (v1.35.0, pedido del usuario con /impeccable layout)

- **Arriba lo que se hace o se corrige; abajo lo de consulta.** Orden: consignatarios → peso total → Hoja de empaque → packing list. Embarque: avisos → hieleras y tallas → órdenes → peso → indicaciones → notas. Lote: avisos → conteo final y cierre → trazabilidad y existencia → plegables.
- **Las acciones de la pantalla van juntas en el encabezado** (PDF, correo, eliminar), una sola vez. La confirmación de eliminar sale ahí mismo.
- **Un formulario largo que no siempre se llena se pliega con su estado en el renglón** («⚠ Faltan 8 datos», «137.2 kg de peso bruto», «Ninguna», «2 lecturas · última 58.5 °F»). Se abre solo cuando es lo que toca (la hoja de empaque con todas las hieleras listas; el peso si no cuadra con la orden).
- **Un aviso rojo abre el plegable** donde está lo que hay que corregir (`data-jump` / `data-jumpto` abren el `details` antes de bajar).
- **Administración en pestañas:** Usuarios · Maquilas · Catálogos · Informes y respaldo. Una pantalla con más de 4 secciones independientes va en pestañas, no seguidas.

## 3e. Textos de los formularios (v1.36.0, /impeccable clarify, el usuario aprobó todo)

- **El error va junto a su campo:** renglón propio debajo del campo, con ícono, que se queda hasta corregir (escribir en el campo lo quita) y se anuncia (`role="alert"`, `aria-describedby`). Nunca en un aviso flotante que se va, ni repetido en otro formulario de la misma pantalla. Los avisos flotantes quedan para lo que no es de un campo (guardado, conexión, «No se puede: el embarque está cerrado»).
- **Una palabra por cosa:** la talla es «Chica · 491-610» (nombre + rango + punto de color) en todas las pantallas; los rangos del papel (0-650…) solo en el PDF del formato. El tanque es «T1». En Empaque la categoría sigue siendo el color (teclado R, V, B, A).
- **Nada peligroso viene elegido:** tipo de movimiento («Salida a embarque» dice «solo para corregir»), rol del usuario nuevo, a. m./p. m. sin hora.
- **Ejemplos con «Ej.»** para que no parezcan datos escritos. Un «0» que sí es el valor por omisión (tallas, tarimas, cajas) se queda.
- **Lo que pide un campo se ve antes de fallar:** «(0 si no hubo)», «(mínimo 8)», «(opcional)».
- **Confirmar dice qué se borra** y el botón dice la acción («Eliminar nota», «Eliminar de la orden»), nunca «Sí / No».
- **Errores técnicos:** qué falló y qué hacer; el detalle técnico, si va, al final entre paréntesis.

## 4. Modo piso

Pantalla de botones grandes para el Encargado de piso (entra directo); el admin lo activa con el interruptor «Modo piso».

| Botón | Flujo |
|---|---|
| **Empacar cajas** | Cliente → lote (se salta si hay uno) → una tarjeta por cada caja del cliente y el **teclado fijo** (v1.3.0): a la derecha en tablet horizontal y computadora, abajo en tablet vertical y celular. Se escriben las piezas en el teclado y se toca ROJO/VERDE/BLANCO: la caja se guarda sola, queda con ✔ Completada (borde verde) y el teclado pasa a la siguiente vacía. Tocar una caja guardada la abre en el teclado («Corrigiendo»; el primer número reemplaza al anterior y la categoría guarda la corrección); «Quitar caja» está en el teclado, con confirmación. La caja activa va en cian. |
| **Registrar entrada** | Hoja de captura: una fila por lote (proveedor y debajo la especie —v1.18.0—, tanque, lote, kg de las 4 tallas, total) y «Más» para temperaturas, kg por caja, desperdicio, fecha y hora. **Desde la v1.8.2 todos son obligatorios**: si la fila ya tiene algo y falta alguno, el botón dice «Más · Faltan N» en rojo. La hoja existe también en la vista completa: al apagar Modo piso estando aquí, te quedas en la misma hoja con las mismas filas. «+ Agregar entrada», «Guardar entradas» guarda cada fila por separado; errores junto al campo; estados Vacía / Sin guardar / ⚠ Revisar / ✔ Guardada. En pantallas angostas o con texto «Muy grande», cada fila es una tarjeta. |
| **Cerrar embarque** | Paso a paso (v1.21.0): elegir el embarque → 1. revisar las hieleras (empacadas de pedidas, langostas, peso y cuánto va de cada lote) → 2. pendientes, cada uno con su botón a donde se corrige (la hoja de empaque incompleta no impide cerrar) → 3. «Cerrar embarque» (solo el Administrador; el piso ve «Avísale al Administrador»). Al cerrar: «✔ Embarque cerrado» con «Cerrar otro embarque». |
| **Conteo final** | Paso a paso (v1.21.0): elegir el lote (solo los que faltan por contar, con lo esperado) → 1. kg contados en una casilla grande (Enter avanza; no acepta más de lo esperado y conserva lo escrito) → 2. confirmar con la mortalidad calculada → «✔ Conteo guardado» con «Contar otro lote» y «Corregir» (el Administrador también «Cerrar lote»). |
| **Temperatura** (v1.17.0) | Abre la pantalla normal de Temperatura sin menú. Dice cuántas lecturas van hoy (incluye las de las entradas). Es el quinto botón: en tablet y computadora va a todo lo ancho. En Modo piso las casillas y botones de «Nueva lectura» miden 60 px (v1.17.1). |

Estilo iOS: encabezado translúcido con desenfoque, título grande, tarjetas con degradado, cuadros de ícono, buena vista en tema oscuro.

## 5. Vista completa

- Menú lateral navy fijo en tablet y computadora; en celular se oculta y se abre con ☰. Íconos sin números (v1.33.0). Desde la v1.34.0: Formatos, Panel; Operación (Modo piso, Entrada, Órdenes, Empaque, Embarque, Temperatura); Revisión (Mortalidad final, Hojas). Panel general está en el selector de maquila y Administración en el círculo del perfil.
- En celular (menú escondido), la barra de arriba dice dónde estás: junto a ☰ va el ícono y el nombre de la sección («Empaque», «Panel», «Temperatura»…), igual que en el menú. Solo el nombre: el usuario pidió quitar «Paso 3 de 5» (13/oct).
- Administración (v1.35.0): pestañas Usuarios · Maquilas · Catálogos · Informes y respaldo.
- Barra superior: buscador, botón **Ajustes** (siempre visible, por accesibilidad) y círculo con la inicial del usuario.
- Menú del círculo: nombre, correo, rol, **Administración** (solo admin), **Cerrar sesión** y la versión. **Ajustes no se mueve al menú**: se queda en la barra.
- **Ajustes:** panel que **deja ver la pantalla de atrás** (translúcido, sin oscurecer; en celular, hoja desde abajo de máx. 66 % de alto). Tema claro/oscuro/del equipo y tamaño de texto con **deslizador de 3 tamaños** (Normal, Grande, Muy grande). Esc, ✕ o tocar fuera lo cierran; el foco regresa al botón. Abrirlo no borra lo que se estaba capturando.
- Panel: título «Panel» con lo que sigue en una línea y su botón, totales, tablero de lotes por etapa, avance de órdenes, actividad reciente.
- En celular, las filas de Empaque se vuelven tarjetas.

## 6. Accesibilidad (mínimos)

- Lighthouse accesibilidad = 100 en las 14 pantallas (comprobar con `pruebas/accesibilidad.mjs`).
- Contraste AA; estados con ícono y texto, nunca solo color.
- Objetivos táctiles ≥ 44 px (botones 48, Modo piso ~60). Campos ≥ 16 px (evita zoom en iPhone).
- Foco visible, «Saltar al contenido», orden de títulos correcto, encabezados de tabla con texto (`aria-label` si la columna es de acciones), etiquetas en todos los campos.
- Diálogos y menús accesibles: `role`, flechas, Esc, foco atrapado y de regreso.
- Debe verse bien en 390, 820 y 1440 px y con texto de 20 px.
- Teclado numérico en tablet (`inputmode`), texto seleccionado al tocar un campo.

## 7. Lo que el usuario pidió y se mantiene

- Logo pequeño y blanco en el menú; menú navy con pasos numerados e íconos de dibujo.
- Campos blancos, flechas propias, números sin flechitas.
- Azul solo en secciones de marca; fondo y textos neutros.
- Pendientes y discrepancias en rojo llamativo, con ícono y texto. Mortalidad final no va en rojo como faltante.
- Colores de consignaciones parecidos a los originales; **siempre el del consignatario en Administración** (v1.24.0).
- **Cada maquila con su logotipo** (emblema + «MAQUILA» + nombre) y una franja de su color (v1.24.0).
- **Antes de juntar o separar embarques se enseña cómo queda (Ahora → Así queda) y se puede deshacer** (v1.24.0). Nada de botones que cambian cosas grandes sin decir qué hacen.
- **La orden dice arriba lo que falta por empacar, por talla** (v1.24.0).
- **Cada camión en su pestaña, con su propio PDF**, cuando hay dos o más (v1.26.0). Con uno, como antes.
- **Lo más viejo primero**: en Empaque los lotes salen ordenados y el más viejo ya elegido, con «usar primero»; los que pasaron los días de su proveedor, en rojo y antes que todos (v1.27.0).
- **Llenar hieleras solo con el teclado** (v1.29.0): número → letra del color (R, V, B, A) → Enter guarda y pasa a la siguiente. La letra solo elige; Enter guarda.
- **La hoja de empaque se cierra al completarla** (v1.29.0): queda una tarjeta corta con «Ver o corregir hoja». Horas en 12 h con a. m./p. m.; placas en mayúsculas; tanques de origen se tocan.
- **El aviso (toast) sale debajo de la barra de arriba**, nunca encima (v1.29.0).
- **Mover hieleras en el camión mismo** (v1.29.0), no en otra cuadrícula abajo.
- **Campana de notificaciones con contador**: lo que falta y lo reciente; cada una lleva a donde se resuelve. Lo que falta no se descarta (se quita al resolverlo) (v1.26.0).
- Optimizada para tablet; se adapta a computadora y celular.
- El admin **no** entra en Modo piso automáticamente.
- Un usuario no técnico debe poder usarla: textos simples, un paso a la vez.

### Tanques en 3D (v1.31.0)
- Arriba del tablero de tanques en Entrada y Panel general. El tablero plano sigue abajo y es el que se usa con teclado o lector de pantalla.
- Color de la canasta: **solo la talla** (listón), con los colores de la maquila de esa canasta. La maquila se dice con texto (letrero de cerca, tarjeta de la canasta), nunca con color.
- Un toque elige; arrastrar gira (no abre nada). Botones de cámara de 48 px para guantes.

## 8. Lo que el usuario rechazó (no repetir sin preguntar)

- **Calendario y reloj del teléfono** para fechas y horas (18/oct): tardan, se traban y ya no abren. Se escriben (dd/mm/aaaa, HH:MM) con «Hoy»/«Ahora».
- Botones que **borran avance con un solo toque** («Quitar guardadas de la lista», 18/oct).
- **Descargar CSV** del packing list (no le sirve).
- Esperar a «Guardar hieleras» en la vista completa: cada hielera se completa sola.

- Rediseño oscuro con colores semánticos y números gigantes (revertido).
- Galería de fotos en el Panel (revertida).
- Modo piso de **una caja a la vez** (quiere varias).
- Entrada en Modo piso con **una ventana por entrada** (asistente de pasos); quiere capturar varias a la vez (13/oct).
- Que las cajas guardadas **desaparezcan** de la pantalla.
- Que Ajustes **oscurezca o tape** la pantalla.
- Más de 3 tamaños de texto (se probó un rango 12–20 px; regresó a 3, pero con deslizador).
- Mover el botón de Ajustes al menú del perfil.
- ~~Teclado numérico propio en Modo piso (se quitó el 12/oct).~~ **Regresó el 13/oct a pedido del cliente**, distinto: fijo en pantalla (no aparece y desaparece), en todas las vistas de Empaque. Ver §4 y `HISTORIAL.md` (v1.3.0).
- Cambiar muchas cosas sin validarlas: el equipo sintió que se trabajaba «sin rumbo».
- **Textos que suenan a app sin terminar o a información que falta** (17/oct): «Todavía no hay…», «Aún no hay…», «Sin datos todavía», «(de una versión anterior)», «escrito a mano, de antes», explicaciones largas de lo que falta. Los vacíos se dicen corto («Sin lotes», «Sin lecturas») y los avisos de pendientes solo con lo necesario («Lote X · sin entrada» + botón). Los mensajes de conexión («cambios que todavía no se suben») sí se quedan.
