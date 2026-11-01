# PRUEBAS.md · Cómo se prueba

## 1. Correr todo

Requisitos: Python 3, Playwright (`pip install playwright`) y Chromium (`python3 -m playwright install chromium`).

```bash
sh pruebas/correr_todo.sh
```

Levanta un servidor en el puerto 8765, corre **55 grupos (2,793 verificaciones el 27/oct/2026, v1.24.0)**; antes corría 38 grupos y termina con **«TODO BIEN»** (2050 verificaciones en la v1.13.2; la v1.13.3 cambia solo `pesos_t`; la v1.14.0 agrega `camiones_t`; la v1.15.0 agrega `colores_t`, 39 grupos; la v1.16.0 agrega `historial_t`, 40 grupos). Las pruebas de pantallas usan el **modo local** (`index.html?modo=local`): datos solo en el navegador, como antes de la base compartida. `sincronizacion_t.py` levanta su propio Supabase de mentira (`pruebas/supabase_falso.py`, puerto 8790). **Ninguna prueba toca la base real.** Cada registro queda en `/tmp/propesa_<prueba>.log`; una línea que empieza con `FAIL` marca el grupo como fallido.

Para correr una sola: `python3 -m http.server 8765 &` y luego `python3 -I pruebas/<archivo>.py`. Desde la v1.7.0 **todas usan `?modo=local` por omisión** (antes, corridas sueltas intentaban entrar a la base real y no probaban nada); `sincronizacion_t.py` usa su propio Supabase de mentira. `accesibilidad.mjs` también usa el modo local y mide las 15 pantallas (todas en 100 el 15/oct/2026). `vistas_t.py` ya tiene verificaciones (nada se sale de la pantalla en 390, 820 y 1440 px) y está en `correr_todo.sh`. `BASE` (variable de entorno) cambia la URL, por ejemplo para probar la versión publicada.

## 2. Qué cubre cada archivo

| Archivo | Cubre | Verif. |
|---|---|---|
| `inicio_t.py` | Configuración inicial, ningún rastro de demo en pantalla, versión, temperatura, Informes de cierre, borrar datos | 20 |
| `csp_t.py` | Cabeceras de `vercel.json` aplicadas: la app funciona sin violaciones de CSP (fotos, PDF, respaldo, Ajustes) | 13 |
| `e2e.py` | Flujo completo Entrada → Órdenes → Empaque → Embarque → Mortalidad | 30 |
| `ajustes_t.py` | Panel de Ajustes (tema, 3 tamaños, foco, sin desbordes a 390/820/1440 px, sin almacenamiento) | 101 |
| `menu_t.py` | Menú del perfil y botón Ajustes | 36 |
| `correcciones_t.py` | Correcciones del /review (guardado fallido, acceso sin contraseñas en la app, fechas, respaldo seguro, embarque cerrado, ids de lote) | 19 |
| `piso_t.py` | Modo piso: empacar, registrar entrada y Temperatura (v1.17.0–1.17.1) | 42 |
| `entradas_t.py` | Modo piso: hoja de varias entradas (agregar, validar por fila, guardar parcial, sin duplicar, Enter, quitar, borradores, vistas 390/820/1180/1440, texto 20 px, tema oscuro) | 58 |
| `cajas_auto_t.py` | Cajas que se guardan solas, quedan grises y se editan | 24 |
| `interruptor_t.py` | Interruptor iOS, logo → inicio, admin no entra a piso | 16 |
| `avisos_t.py` | Avisos rojos que llevan a donde se resuelven | 26 |
| `pdf_t.py` | PDF de cada paso (archivo válido); el Plan de embarques trae el camión | 11 |
| `botones_t.py` | Pulsa todos los botones de todas las pantallas buscando errores de JavaScript | 1 |
| `tabla_entrada_t.py` | Tabla de Entrada: tallas en dos renglones, sin números partidos, punto de color alineado, encabezados sin cortes de más, desplazamiento dentro de la tarjeta (390/820/1440, texto 20 px, tema oscuro) | 45 |
| `tanques_t.py` | Tablero de tanques en Entrada como el plano del piso: posiciones (T1–T4 derecha, T6 junto a T3, T5 junto a T4), kg totales y por talla, agua en el mapa, detalle al tocar, «Vacío», lote/temperatura llevan a su pantalla, lote cerrado fuera, sin desbordes (390 px, 20 px, claro y oscuro). En vivo: `sincronizacion_t.py` | 57 |
| `estados_caja_t.py` | Empaque: estado de cada caja (Pendiente / En captura / ✔ Completada / Editando / ⚠ Incompleta), solo color no completa, doble toque no duplica, reabrir y corregir la misma caja (Actualizar, Cancelar, Enter, Esc, Quitar), barra delgada que marca el avance real (0 → 25 → 100 %) con el botón Guardar de tamaño fijo, resumen completadas/pendientes/%, el aviso no tapa la barra, Rojo/Verde/Blanco del mismo tamaño y ≥44 px, sin pastillas de estado, cada fila dice «Caja N» y «N piezas», el aviso sale arriba de la barra, recarga, Modo piso, rol consulta (390/820/1440) | 143 |
| `titulo_t.py` | Celular: la barra de arriba dice la sección actual (ícono + nombre, sin «Paso N de 5») en las 12 pantallas, en un solo renglón con ☰ y los botones, sin desbordes (390, 360 con 20 px); en 820 y 1440 no aparece | 145 |
| `recarga_t.py` | Recargar no cierra la sesión: se conservan pantalla y borradores (formulario de Entrada, línea de orden, nota, búsqueda, Empaque de piso con piezas y categoría, hoja de entradas de piso); cerrar sesión borra todo; sesión vencida y usuario eliminado piden entrar; datos raros en `propesa-ui` no rompen (1180 y 390 px) |
| `teclado_t.py` | Teclado fijo de Empaque. Modo piso (1180, 820 oscuro, 390): números, ⌫, Borrar, máximo 4 cifras, la categoría guarda y pasa a la siguiente, corregir una caja guardada (el primer número reemplaza), categoría primero + «Siguiente caja», «Caja anterior», teclado físico, «Quitar caja» con confirmación, letra de 20 px sin cortes. Vista completa (1440, 1180 oscuro, 820, 390): teclado y «Guardar cajas» a la vista al entrar, la categoría marca la fila y avanza, guardar, corregir una caja guardada. iPad simulado (táctil): tocar teclado y cajas, sin selección de texto. Consulta y embarque cerrado sin teclado |
| `sincronizacion_t.py` | Base compartida con varios navegadores a la vez: configuración inicial en la base, acceso y error de contraseña, entradas y órdenes simultáneas, empaque en un equipo y embarque en otro, notas, mismo orden de embarques, datos idénticos, sin internet y de regreso, borrar, token vencido, consulta no escribe y vuelve a lo de la base, piso, alta de usuario y acceso desde otro equipo, recargar, equipo nuevo, borrar todo, restaurar respaldo, sin NaN, cerrar sesión, sin escrituras de ida y vuelta | 76 |
| `fotos_t.py` | Fotos en el espacio de archivos (v1.8.0), con su propio Supabase de mentira (puerto 8791) y varios navegadores: la nota guarda referencias; ningún registro trae fotos dentro; otro equipo las baja una sola vez y las sigue viendo sin poder bajarlas; sin internet la foto espera (también al recargar) y se sube antes que la nota; Consulta las ve; fotos viejas dentro de una nota se pasan solas; con el espacio de archivos caído la nota se sube y la foto después; foto rechazada se quita y avisa; eliminar la nota borra los archivos; ya no existe «Borrar todos los datos» (v1.8.5) |
| `despierta_t.py` | Tarea diaria de Vercel (`api/despierta.js`, v1.8.0) con Node contra el Supabase de mentira (puerto 8792): consulta y responde 200, sin caché, `CRON_SECRET` (401 sin clave, 200 con ella), 502 si la base no responde; misma base y llave que `index.html`; `vercel.json` la corre una vez al día |
| `atras_t.py` | Botón de atrás (v1.8.1), en 1180 y 390 px: cada pantalla nueva entra al historial; atrás y adelante recorren pantallas; redibujar no agrega pasos; atrás cierra primero Ajustes, menú del perfil, foto en grande y menú lateral del celular; Modo piso y regreso a la vista completa; lote que ya no existe → Entrada; sin sesión no abre pantallas |
| `cambio_modo_t.py` | Cambiar de modo sin perder lo escrito (v1.8.2), en 1180 y 390 px: hoja de entradas de piso → misma hoja en la vista completa con las mismas filas, aviso en Entrada y «Terminar», regreso a piso, guardar desde la vista completa con todo; formulario de Entrada a medio llenar → fila de la hoja; Empacar ↔ Empacar; atrás después de cambiar |
| `eliminar_orden_t.py` | Eliminar una orden (v1.8.3), en 1180 y 390 px: orden vacía con confirmación y «No»; orden con líneas sin cajas se va con su embarque vacío y sus notas; las demás órdenes y cajas siguen bien; con cajas empacadas no hay botón ni se borra forzando la acción; piso y consulta no ven el botón |
| `vista_previa_t.py` | Vista previa al compartir el link (v1.8.6): etiquetas `og:`/`twitter:` completas, imagen con dirección https, `og-image.png` de 1200×630 y menos de 300 KB, descripción sin Mortalidad final; dominio `propesa.org` y nada de `vercel.app` en el encabezado (v1.13.2); íconos del manifiesto existen y miden lo que dicen, hay 1024 px `any` y `maskable`, mismo `?v=`; pantalla de carga con el logo en el HTML que se quita sola |
| `pesos_t.py` | Peso estándar de la caja (v1.8.7), en 1180 y 390 px: valores de siempre sin configurar; Embarque sin casillas y con «Editar pesos» (v1.13.3: Administración ya no tiene la tarjeta); validación; total en vivo; guardar recalcula embarques abiertos y Órdenes; cerrado conserva su peso y al reabrirlo «Usar el peso estándar»; respaldo y registro `W/pesos`; Encargado de piso no puede |
| `camiones_t.py` | Varios camiones y acomodo a mano (v1.14.0), en 1180, 820 y 390 px: el automático igual que antes (300 combinaciones), «Camión nuevo» y regresar, intercambiar celdas, dividir una tarima, avisos de faltan/sobran/capacidad, celdas de 44 px o más, cerrados aparte, Consulta sin controles, `tk`/`ly` en `WN`/`cleanST`/`decodeST`, PDF con dos camiones |
| `v126_t.py` | Camiones en pestañas y notificaciones (v1.26.0), en 1440, 820 y 390 px: sin pestañas con un camión; «Camión nuevo» abre su pestaña; cada pestaña con sus consignaciones y su PDF (solo su camión); teclado; 48 px; campana con contador, panel que cabe, Escape/✕/«atrás» lo cierran, orden nueva sin ver → vista al tocarla, entrada de madrugada lleva al lote, «Marcar todo como visto», embarque cerrado como terminado, tema oscuro, Modo piso |
| `v128_t.py` | v1.28.0, en 1180 y 390 px: sin Gris en el teclado, en los botones de cada hielera ni en «Poner a todas» (vista completa y Modo piso); «Hieleras grises · extra»: valida piezas (1–35, no borra lo escrito), no cuenta para las pedidas, no ocupa lugar en piso, suma al embarque (hieleras, tallas, peso bruto) y al packing list; quitar con confirmación. |
| `v1271_t.py` | v1.27.1, en 1180 px claro y 390 px oscuro: Hieleras por talla visual: «Faltan N hieleras por empacar» con una ficha por talla, «✔ Lista» / «Falta N» / «De más +N», un cuadrito por hielera, color de cada talla, aviso rojo con lo de más, «✔ Ya están todas las tallas» y barra con más de 24. |
| `v127_t.py` | v1.27.0, en 1180 y 390 px: lo más viejo primero (orden, elegido, «usar primero», se puede cambiar); 36 no se guarda y 35 sí (vista completa y piso); días máximos del proveedor (0 no, 3 sí, WN.V/cleanST, vacío = sin límite); lote vencido en rojo, en Notificaciones y primero en Empaque; «Último día»; «Repartir tallas» llena y guarda, descuenta otras órdenes y dice si no alcanza |
| `colores_t.py` | Color de cada consignatario (v1.15.0), en 1440, 820 y 390 px: tarjeta en Administración, selector de 44 px o más, abiertos toman el color y cerrados no, embarque nuevo, `C/colores` en `WN`/`encodeST`/`decodeST`/`cleanST`, valores malos ignorados, solo el Administrador |
| `especies_t.py` | Especies (v1.18.0): Administración → Especies, especie en Entrada (vista completa y Modo piso), lotes de antes, tanques y compradores por especie, PDF de Entrada, Formato 06, registros `E/<id>`, respaldo; 1180/390 px y 820 px oscuro con 20 px | 94 |
| `maquilas_t.py` | Maquilas (v1.19.0): Panel general, menú del logo (44 px, Esc), cambiar de maquila, mismo código de lote en dos maquilas, compartido (temperatura), Administración → Maquilas, respaldo con todas, recargar, Modo piso, nombre en lugar del logo; con el Supabase de mentira (puerto 8794) y dos equipos: prefijo `q2:`, sin mezclar, `D/disp` solo PROPESA | 53 |
| `tallas_t.py` | Tallas por maquila y Despatada: entrada, orden, empaque, cierre, compradores, PDF, Administración (editar, agregar, ocultar), hoja de Modo piso, registros `Z/tallas`, respaldo, vistas | 46 |
| `salidas_t.py` | Congelación, basura, recuperación y débil: tipos, nota, existencia, mortalidad, Mortalidad final, PDF, revertir, compartir, permisos | 17 |
| `consignatarios_t.py` | Datos corregidos, Yishunhai a XMN, nuevo consignatario y destino, ocultar, orden, PDF, compartidos, respaldo | 21 |
| `envios_t.py` | % de mortalidad del cliente y temperatura de arribo; el embarque toma el color del consignatario | 15 |
| `hojas_t.py` | Precio de compra y Hojas para imprimir (los 6 PDF, periodo, permisos) | 21 |
| `excel_reales_t.py` | **El Excel de Martha como referencia**: carga sus datos reales (`pruebas/datos/excel_reales.json`) y compara recepciones, envíos, existencia (÷16 y ÷15), peso bruto, balance y temporada con sus fórmulas | 25 |
| `precios_t.py` | Precios solo para el Administrador con el Supabase de mentira (puerto 8795): registro `$/<lote>`, Piso y Consulta no lo reciben ni lo escriben, otra maquila, borrar el lote borra su precio | 16 |
| `traslados_t.py` | Otro tanque en la entrada (vista completa y Modo piso), validaciones, tablero, Temperatura, «Pasar a otro tanque», «Deshacer», salidas del principal, Panel general, hoja de existencia, registros, respaldo, otra maquila, vistas | 30 |
| `avisos_entrada_t.py` | Fecha contra el código del lote y hora de madrugada (lote, Entrada, al guardar, Modo piso, «Corregir ›», «Está bien así», Piso sin botones); salida incompleta al cerrar (motivos, pendiente del embarque, «Volver a descontar», reabrir), registros, respaldo, sin desbordes | 45 |
| `especie_orden_t.py` | Especie en cada orden: selector solo con más de una especie, empaque (vista completa y Modo piso) solo de esa especie, lotes sin entrada con la especie de la orden, cambiar especie sin hieleras, compradores por especie, PDF, hoja de empaque, registros, respaldo, sin desbordes | 34 |
| `historial_t.py` | Historial de cambios (v1.16.0) con el Supabase de mentira (puerto 8793): Piso crea, el Administrador cambia y borra; la lista dice quién, qué y «58 → 60», sin `D/disp`; Piso no recibe filas; sin internet; 1440/820/390 px con 20 px, tema oscuro, botón de 44 px; oculto en modo local |
| `editar_orden_t.py` | Editar una orden (v1.8.8), en 1180 y 390 px: cambiar fecha (y nombre del embarque), cancelar, editar cliente y cajas (embarque se actualiza), validaciones que conservan lo escrito, no menos de las empacadas, embarque cerrado bloquea; piso y consulta no pueden |
| `teclado_movil_t.py` | Teclado de la app en celular (v1.8.9), simulando Android táctil: casillas de piezas de solo lectura (vista completa y Modo piso, nuevas y guardadas), el teclado de la app escribe, al tocar la categoría pasa a la siguiente sin abrir el teclado del sistema; en computadora no son de solo lectura y el teclado físico escribe |
| `v112_t.py` | Pedidos del 18/oct (v1.12.0), en 1180 y 390 px: Mortalidad sin «Revisión aparte / se calcula sola»; sin `type=date/time`, fechas y horas escritas con diagonales y dos puntos solos, «Hoy»/«Ahora», fecha inválida no se guarda; orden con tallas primero y total automático, sin tallas se escribe el total, el embarque toma tallas de lo empacado; hieleras que se completan solas y «Listo» con el teclado cerrado (también con el teclado de la app en celular táctil); sin CSV; hora inicial con «Ahora»; «Editar pesos» en Embarque; proveedor nuevo desde la Entrada y desde la hoja; datos extra abiertos y sin «Quitar guardadas»; empacar sin lote y conectar; sin «Eliminar orden» en Modo piso; ventana para instalar (Instalar, Ahora no, iPhone); Encargado de piso | 109 |
| `disponible_t.py` | Cuenta Cliente y salida automática (v1.13.0). Modo local: disponibilidad por talla (tanques − lo pedido que no sale; empacar no la cambia), al cerrar el embarque sale sola y una sola vez, reabrir la regresa, nunca en negativo, lote cerrado intacto, línea sin tallas como reservado; Administración ofrece el rol; pantalla en inglés sin menú ni datos internos, 390/820/1440 px claro y oscuro, texto de 20 px, «Sign out». Con su propio Supabase de mentira (puerto 8792): alta del Cliente, la base recibe `D/disp` sin proveedor/lote/tanque, dos Administradores a la vez sin choques ni ida y vuelta, el Cliente solo recibe `D/disp` y su perfil, no puede escribir y ve los cambios en vivo | 59 |
| `proveedores_t.py` | Proveedores de una lista y lote sin entrada (v1.11.0), en 1180 y 390 px: lista en Entrada y en la hoja de Modo piso, lote propuesto (WLR + clave + fecha, siguiente letra si existe, no pisa lo escrito a mano, tocarlo lo selecciona), lotes de antes (nombre escrito a mano se conserva; nombre exacto cuenta como el proveedor), Administración (agregar, clave repetida, RFC, permiso, editar nombre actualiza lotes, asignar nombres escritos a mano, ocultar, no ocultar el último), lote sin entrada en Empaque y Modo piso (validaciones, se elige, se empaca, «Sin entrada», fuera de tanques y mortalidad, PDF de Entrada, completar conserva hieleras), Consulta sin botones, pantallas vacías sin «todavía no» ni versiones viejas, se comparte y sobrevive a un respaldo | 128 |
| `temperatura_t.py` | Temperatura conectada y Mortalidad final aparte (v1.8.4), en 1180 y 390 px: la temperatura de una entrada sale sola en Temperatura, el lote y el tablero; editar o eliminar el lote la cambia; lectura manual con tanque preseleccionado; filtro por tanque; orden por fecha; menú con 4 pasos y «Revisión»; Panel y Embarque no mandan a Mortalidad final |

Extras (no están en `correr_todo.sh`):
- `rendimiento_t.py` — genera un año de datos y mide tiempos de pantalla y de guardado (CPU normal y 4× más lenta). Desde la v1.6.0 también mide el camino de la base compartida y **falla** si se pasa del límite con CPU 4×: guardar una caja ≤ 200 ms y recibir el cambio de otro equipo ≤ 320 ms (el 15/oct/2026 midió ~90–140 y ~140–190). Ya usa `?modo=local` por omisión.
- `vistas_t.py` — capturas en varios tamaños.
- `generar_datos.py` — crea datos grandes de prueba.
- `accesibilidad.mjs` — Lighthouse (accesibilidad) en 14 pantallas; requiere `npm i lighthouse puppeteer-core` y `CHROME_PATH` si Chromium no está en `/opt/pw-browsers/chromium`. Meta: 100 en todas.

## 3. Datos de prueba

- La app ya **no trae usuarios**. Cada prueba carga su propio estado con la constante `FIX` (en `localStorage`), con usuarios **solo de prueba**:
  `admin@propesa.mx / admin123` (Administrador), `piso@propesa.mx / piso123` (Encargado de piso), `consulta@propesa.mx / ver123` (Consulta).
- `pruebas/datos/backup.json` y `seed.json`: respaldos con esos usuarios y algunos lotes, órdenes y embarques.
- Esos datos nunca deben aparecer en `index.html` (lo vigila `inicio_t.py`).

## 4. Escribir una prueba nueva

- Copia el encabezado de una existente (`chk(cond, mensaje)` imprime `PASS`/`FAIL`; al final `RESULTADO: N fallas`).
- Escucha `pageerror` y errores de consola; un error de JavaScript es una falla.
- Prueba en el tamaño que importa (tablet 820 px, celular 390 px) y con texto «Muy grande».
- Agrégala a la lista de `correr_todo.sh`.

## 5. Antes de entregar

1. `sh pruebas/correr_todo.sh` → TODO BIEN.
2. Revisión de sintaxis (comando en `CLAUDE.md`).
3. Si tocaste la interfaz: `accesibilidad.mjs` → 100.
4. Si tocaste cálculos o listas: `rendimiento_t.py` (Panel < 100 ms con CPU 4×).
