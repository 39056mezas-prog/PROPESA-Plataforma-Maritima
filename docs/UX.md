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
- **El avance se ve abajo:** «✔ N completadas · N pendientes · N % completado» y una barra delgada (cian) que avanza con las cajas guardadas. El botón Guardar **no** cambia de tamaño (se probó en la v1.2.0 y se cambió en la v1.2.1 por pedido del usuario). Los avisos (toast) salen arriba de esa barra.
- **Empaque, estilo sobrio (v1.2.1, pedido del usuario):** referencia iOS para la tabla de cajas: separadores finos, Rojo/Verde/Blanco como control segmentado compacto (mismo tamaño, seleccionado = fondo claro con borde de acento, sin azul saturado), lotes como selector horizontal (se desliza de lado en celular), números alineados a la derecha. Cada fila es como una celda de lista de iOS (v1.2.2): a la izquierda «Caja N» con su estado, a la derecha el valor con su unidad («12 piezas ›»; el campo dice «piezas» dentro), para que el número de caja y el conteo no se confundan. La barra de abajo es una cápsula flotante (bordes redondos y sombra suave) y los avisos salen arriba en esta pantalla. En esta pantalla el número de pendientes va en gris, no en rojo: el rojo queda para errores y la categoría Rojo. Solo aplica a la tarjeta de cajas (`.pkx`); el Modo piso conserva sus botones grandes.
- **Teclado fijo en Empaque (v1.3.0, pedido del cliente):** en la vista completa y en Modo piso hay un teclado numérico siempre visible (botones de 48 px o más) con las categorías debajo de los números (o a un lado en pantallas angostas). El teclado de la tablet ya no aparece (`inputmode="none"`), así no tapa las cajas; un teclado físico sigue funcionando. En la vista completa la categoría marca la fila y pasa a la siguiente; se guardan todas con «Guardar cajas», que va pegado al teclado. Al abrir un cliente la pantalla baja sola lo justo para ver el teclado completo.
- **Se guarda solo cuando se puede.** En Modo piso cada caja se guarda al tener piezas y categoría (`peTry`), sin botón «Guardar».
- **Varias cosas a la vez.** Los empleados anotan varias cajas a la vez: se muestran todas las cajas pendientes del cliente, no una por una. «Poner a todas las vacías» aplica una categoría de un toque.
- **Los formularios no borran lo escrito** cuando hay un error: se marca el campo en rojo, se enfoca y se explica.
- **Confirmar solo lo destructivo:** quitar caja, eliminar lote, restaurar respaldo, borrar datos (este último exige escribir BORRAR).
- **El logo siempre regresa al inicio**, en cualquier modo.
- **Cambiar de modo** con un interruptor tipo iOS y una transición suave (sin animación si el equipo pide movimiento reducido).
- **Listas cortas:** solo lo abierto o reciente (lotes 30 días, órdenes y embarques 14, temperatura 7) con «Ver historial».
- **Mensajes:** un toast breve al guardar; nunca «Guardado» si el guardado falló (aviso rojo fijo con «Descargar respaldo» y «Reintentar»).

## 4. Modo piso

Pantalla de botones grandes para el Encargado de piso (entra directo); el admin lo activa con el interruptor «Modo piso».

| Botón | Flujo |
|---|---|
| **Empacar cajas** | Cliente → lote (se salta si hay uno) → una tarjeta por cada caja del cliente y el **teclado fijo** (v1.3.0): a la derecha en tablet horizontal y computadora, abajo en tablet vertical y celular. Se escriben las piezas en el teclado y se toca ROJO/VERDE/BLANCO: la caja se guarda sola, queda con ✔ Completada (borde verde) y el teclado pasa a la siguiente vacía. Tocar una caja guardada la abre en el teclado («Corrigiendo»; el primer número reemplaza al anterior y la categoría guarda la corrección); «Quitar caja» está en el teclado, con confirmación. La caja activa va en cian. |
| **Registrar entrada** | Hoja de captura: una fila por lote (proveedor, tanque, lote, kg de las 4 tallas, total) y «Más» para temperaturas, kg por caja, desperdicio, fecha y hora. **Desde la v1.8.2 todos son obligatorios**: si la fila ya tiene algo y falta alguno, el botón dice «Más · Faltan N» en rojo. La hoja existe también en la vista completa: al apagar Modo piso estando aquí, te quedas en la misma hoja con las mismas filas. «+ Agregar entrada», «Guardar entradas» guarda cada fila por separado; errores junto al campo; estados Vacía / Sin guardar / ⚠ Revisar / ✔ Guardada. En pantallas angostas o con texto «Muy grande», cada fila es una tarjeta. |
| **Cerrar embarque** | Abre la pantalla normal sin menú. |
| **Conteo final** | Abre la pantalla normal sin menú. |

Estilo iOS: encabezado translúcido con desenfoque, título grande, tarjetas con degradado, cuadros de ícono, buena vista en tema oscuro.

## 5. Vista completa

- Menú lateral navy fijo en tablet y computadora; en celular se oculta y se abre con ☰. Pasos numerados con íconos.
- En celular (menú escondido), la barra de arriba dice dónde estás: junto a ☰ va el ícono y el nombre de la sección («Empaque», «Panel», «Temperatura»…), igual que en el menú. Solo el nombre: el usuario pidió quitar «Paso 3 de 5» (13/oct).
- Barra superior: buscador, botón **Ajustes** (siempre visible, por accesibilidad) y círculo con la inicial del usuario.
- Menú del círculo: nombre, correo, rol, **Administración** (solo admin), **Cerrar sesión** y la versión. **Ajustes no se mueve al menú**: se queda en la barra.
- **Ajustes:** panel que **deja ver la pantalla de atrás** (translúcido, sin oscurecer; en celular, hoja desde abajo de máx. 66 % de alto). Tema claro/oscuro/del equipo y tamaño de texto con **deslizador de 3 tamaños** (Normal, Grande, Muy grande). Esc, ✕ o tocar fuera lo cierran; el foco regresa al botón. Abrirlo no borra lo que se estaba capturando.
- Panel: «Tu siguiente paso», totales, tablero de lotes por etapa, avance de órdenes, actividad reciente.
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
- Colores de consignaciones parecidos a los originales.
- Optimizada para tablet; se adapta a computadora y celular.
- El admin **no** entra en Modo piso automáticamente.
- Un usuario no técnico debe poder usarla: textos simples, un paso a la vez.

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
