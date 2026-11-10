# DICCIONARIO.md · Las palabras de la app

Pedido del usuario (8/nov/2026, v1.42.0): «estructura nuestro propio diccionario y terminología». Estas son las palabras que usan las pantallas, los PDF, los avisos y los documentos. Si agregas una pantalla o un texto, usa estas palabras y no sus sinónimos.

| Palabra | Qué es | No decir |
|---|---|---|
| **Recepción** | El primer paso del flujo: cuando llega la langosta del proveedor y se pesa por tinas. Antes se llamaba «Entrada». | Entrada |
| **Lote de recepción** (o **lote**) | Lo que llegó de un proveedor en una recepción. Código `WLR` + clave del proveedor + fecha `ddmmaa` (ej. `WLRCO081126`); la app lo propone. | — |
| **Lote sin recepción** | Lote que se empezó a empacar antes de registrar su recepción. Se completa con «Completar ›». | Lote sin entrada |
| **Tanque** | T1 a T6. Cada uno tiene 30 tinas. | — |
| **Tina** | Recipiente numerado dentro de un tanque. T1 = tinas 1–30, T2 = 31–60, T3 = 61–90, T4 = 91–120, T5 = 121–150, T6 = 151–180. **Una tina = un lote y una talla.** Se dice «tanque 6, tina 140». | Canasta, caja (en el tanque) |
| **Kg en tina** | El peso exacto que se escribió para esa tina (ej. 34.95 kg). Baja cuando se saca para empacar; en 0 kg la tina queda libre. | Kg por caja |
| **Talla** | La categoría por peso de cada maquila (nombre, rango y color propios). Ej. Chica 491-610 g. | — |
| **Langosta viva** | Lo que va en tinas. | — |
| **Langosta muerta** | Se pesa aparte; se descuenta y se regresa al proveedor. No va en tinas. | — |
| **Langosta débil** | Se pesa aparte. No va en tinas. | — |
| **Rechazo** | Se pesa aparte. No va en tinas. | — |
| **Despatada** | Langosta sin patas; se pesa aparte (no está en el teclado de tallas de las tinas). Se puede empacar y vender. | Destapada |
| **Temperatura del tanque** | Un número en °F por cada tanque usado en la recepción. | Rangos «59-62» |
| **Temperatura del producto** | Dos números en °F: mínima y máxima. | Un rango en una casilla |
| **Hora inicial / hora final** | Cuándo empezó y terminó la recepción. | — |
| **Hielera** | Solo en **Empaque**: la caja que se manda al cliente (16 kg netos). | Caja |
| **Formato de recepción** | El PDF de una recepción, como el Formato 02 de papel. | Formato de entrada |

## En el código

| Pantalla | Ruta | Palabras clave |
|---|---|---|
| Recepción (lista y tablero de tanques) | `recepcion` | — |
| Recepción por tinas (nueva o editar; la misma en Modo piso) | `rtin`, `rtin:<lote>` | `RT` (borrador), `R.tn`, `ST.TS` |

Las claves internas viejas (`ent`, `nt:'Entrada'`, `entrada` en nombres de funciones) se quedan como están: cambiarlas rompería los datos guardados. Lo que se ve en pantalla sí dice «Recepción».
