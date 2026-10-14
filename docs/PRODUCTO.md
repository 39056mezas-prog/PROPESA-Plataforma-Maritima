# PRODUCTO.md · El negocio y lo que hace la plataforma

## 1. La empresa

**PROPESA** (Proveedor del Pescador S.A. de C.V.), Ensenada, Baja California. Compra langosta roja viva a cooperativas, la guarda en tanques (almacenaje húmedo) y la exporta por avión a China y Singapur.

**Objetivo de la plataforma:** seguir cada lote desde que entra hasta que se envía y se calcula su mortalidad. Quien vea la pantalla debe entender **dónde está, qué sigue y qué falta**.

**Quién la usa:** personal de piso en tablet (varias tablets capturan), el Administrador en computadora o tablet, y gente que solo consulta en computadora o celular. Hay internet casi siempre.

## 2. El flujo (decidido por el usuario; no se cambia sin permiso)

**Entrada → Órdenes → Empaque → Embarque → Mortalidad final**

| # | Paso | Qué se hace | Quién | Ruta interna |
|---|---|---|---|---|
| 1 | **Entrada** | Formato de recepción del lote: fecha, hora, proveedor, tanque (T1–T6), °F tanque, °F producto (puede ser rango «59-62»), lote (mayúsculas automáticas), kg por caja en tanque, kg por talla, kg total (se calcula), kg desperdicio | Admin y Encargado de piso | `recepcion`, `lote:<lote>` |
| 2 | **Órdenes** | Pedido de un empaque: ETD → ciudad destino → consignatario → cliente final → cajas | Admin | `ordenes`, `orden:<id>` |
| 3 | **Empaque** | Se cuentan las langostas de cada caja al empacar: lote, piezas vivas, categoría. La caja se numera ahí | Admin y piso | `empaque`, `empacar:<orden>.<línea>` |
| 4 | **Embarque** | Junta una o varias órdenes con mismo destino y consignatario. Plan de carga del camión, tallas, peso bruto, cierre del empaque e informe | Admin | `embarques`, `emb:<índice>` |
| 5 | **Mortalidad final** | Conteo final por lote (kg) y langostas vivas al llegar; se calcula la pérdida | Captura admin y piso; cierra admin | `cierre` |

Además: **Panel** (`inicio`), **Temperatura** (`temperatura`), **Administración** (`admin`), **Buscar** (`buscar:<texto>`) y **Modo piso** (`piso`, `pemp`, `pent`).

> **Hecho clave (corregido por el usuario):** en los tanques las cajas **no se numeran ni se cuentan**. Del lote solo se conocen los **kilos por talla**. Las piezas por caja se cuentan **al empacar cada pedido**.

## 3. Glosario

| Término | Significado |
|---|---|
| **Lote** | Una entrada de producto. Código tipo `WLRCO170926` = `WLR` (langosta roja) + proveedor (`CO` Cooperativa/SCPP Ensenada, `EM` Emancipación, `LE` Leyes de Reforma) + fecha `ddmmyy`. *Inferido de los PDFs; confirmar.* |
| **Tallas (g)** | 491-610, 611-850, 851-1220, 1221-UP. En papel también: 0-650, 651-850, 851-1250, 1251-UP. Interno: `S`, etiquetas `SL`. |
| **Caja / hielera** | Se tratan como lo mismo. Una caja = **16 kg netos** (`KGN`) y **20 kg brutos** (`KGB`) en la orden. |
| **Categoría** | Rojo / Verde / Blanco por caja (`RC`). |
| **Consignatario** | A quién se factura en destino. Lista oficial de 7 (`CONS`). |
| **Cliente final** | Código de 3 letras: HXH, ZSM, LHD, RSK, HSF, HYG, HJX, ZYX, LMD, MXH (`CLI0`). Una orden a PVG se reparte entre varios. |
| **Consignación / embarque** | Grupo orden(es) + ciudad + consignatario. Nombre tipo `PVG · YISHUNHAI · 12/10 + 13/10`. |
| **ETD** | Fecha de empaque/salida de la orden. |
| **Ciudades** | PVG Shanghái · HKG Hong Kong · XMN Xiamen · SZX Shenzhen · CAN Guangzhou · SIN Singapur (`PORTS`). |
| **Etapas del lote** | En tanque → Con cajas empacadas → Lote cerrado (`STG`). |

### Consignatarios oficiales (`CONS`)

| Clave | Razón social | Ciudades |
|---|---|---|
| YISHUNHAI | Shenzhen Yishunhai Trading Co., Ltd | PVG, SZX, HKG |
| XIAMEN COASTAL | Xiamen Coastal Seafood Supply Chain Co., Ltd | XMN |
| CHAOZHIXIN | Shanghai Chaozhixin Industrial Co., Ltd. | PVG |
| TIAN CHENG | Shanghai Tian Cheng Supply Chain Management Ltd | PVG |
| XINBANG | Guangzhou Xinbang Freight Forwarding Co., Ltd | CAN |
| SEAFOOD ORIGIN | Seafood Origin Pte Ltd | SIN |
| YANTAI | Yantai Bajiaowan Marine Technology Limited Company | todas |

Direcciones, contactos y USCI completos: `index.html` (`CONS`) y `docs/referencias/lista_de_consignatarios.pdf`.

## 4. Reglas de negocio implementadas

- **Existencia por lote** = suma de movimientos (`L`, en gramos). La entrada crea un movimiento `RECEPCION` por talla. La salida a embarque es un movimiento manual en la página del lote. **Empacar una caja NO descuenta kilos** (pregunta abierta).
- **Kg total de entrada** = suma de las 4 tallas (solo lectura). **Desperdicio** es informativo; no resta existencia.
- **Lote:** fecha, proveedor y lote obligatorios; el lote no se repite; al menos una talla con kilos. ID interno `R-0121` con contador que solo crece (`ST.RN`).
- **Orden:** neto = cajas × 16 kg; bruto = cajas × 20 kg. Una línea no admite más cajas empacadas que las pedidas. No se elimina una línea con cajas. No se agregan líneas a un destino cuyo embarque está cerrado.
- **Consignación:** una por (orden + ciudad + consignatario); varias órdenes pueden unirse en un embarque («Unir», «Agregar otra orden», «Separar»). Hieleras = suma de cajas de sus órdenes. Peso bruto = hieleras × (1.4 hielera + 1.5 gel + 16 producto + 0.7 cartón) = **19.6 kg/hielera**.
- **Plan de carga:** 10 celdas (2 × 5) de 15/20/20/25/25 hieleras = **210** por camión; se llena desde la cabina; avisa si se excede. Solo cuenta embarques abiertos.
- **Alertas de embarque (rojo):** peso bruto ≠ formato; tallas ≠ hieleras (también con tallas en 0); cajas sin cantidad o categoría; sin cajas empacadas. Cada una con «Resolver ›».
- **Cerrar empaque (solo admin):** requiere al menos una caja; guarda el informe en Administración → Informes de cierre (con PDF). Después, las cajas de ese destino quedan bloqueadas.
- **Mortalidad por lote:** esperado (existencia) − conteo final, y su %. El conteo final no puede exceder lo esperado. **Por envío:** enviadas − vivas al llegar.
- **Temperatura:** lecturas por tanque en °F (agua, superficie, producto), 20–110, al menos un valor; se guarda quién capturó. Rango visto en papel: almacenamiento 57.7–62.2 °F, transporte 48–49 °F.
- **Fotos y notas:** hasta 6 fotos por nota en Entrada, lote, Embarque, Mortalidad final y Temperatura. En Empaque solo notas. Cada quien borra sus notas; el admin, cualquiera.
- **PDF de cada paso:** Entrada, Órdenes, Empaque, Embarque y Mortalidad final. El mismo PDF se descarga y se manda por correo.

## 5. Roles y permisos

Función `can(a)`: el admin puede todo; el Encargado de piso puede `box`, `fin` y `ent`.

| Acción | Administrador | Encargado de piso | Consulta |
|---|---|---|---|
| Ver todo | Sí | Sí | Sí |
| Registrar entradas (`ent`) | Sí | Sí | No |
| Editar o eliminar lotes, crear órdenes (`lot`) | Sí | No | No |
| Movimientos manuales de inventario y reversas (`mv`) | Sí | No | No |
| Empacar cajas (`box`) y capturar conteos/temperaturas (`fin`) | Sí | Sí | No |
| Fotos y notas | Sí | Sí | No |
| Cerrar empaques y lotes | Sí | No | No |
| Usuarios, respaldo, borrar datos | Sí | No | No |

- Al entrar, el **admin va a la vista completa** y el **Encargado de piso a Modo piso**. El admin puede prender Modo piso con el interruptor.
- No se puede dejar la plataforma sin Administrador.
- **Primer uso:** sin usuarios, la app pide crear el Administrador (Configuración inicial) o restaurar un respaldo.

## 6. Documentos en papel que reemplaza (en `docs/referencias/`)

| PDF | Contenido | En la plataforma |
|---|---|---|
| `PROPESA_Control_Recepcion.pdf` | Control de recepción y tallas | **Sí**: formulario de Entrada |
| `orden_a_proveedor.pdf` | ETD, cliente, destino, cajas, pesos | **Sí**: Órdenes |
| `lista_de_consignatarios.pdf` | 7 consignatarios con dirección, contacto, USCI | **Sí**: `CONS` |
| `packing_list.pdf` (Formato 06) | Cajas con piezas vivas y cliente; encabezado con placas, chofer, horas, temperaturas, peso bruto | Parcial: packing list sí, encabezado no |
| `tabla_logistica.pdf` | Cajas y kg neto por cliente y destino | Parcial |
| `control_de_pesos_y_tallas.pdf` (Formato 02) | Pesos por tina (1–180), totales por talla, cajas completas/incompletas | **No** |
| `Recepcion_Variedades.pdf` | Control de envío: color de tape, lotes mezclados, % mortalidad, temperatura de arribo | **No** (solo se calcula mortalidad) |

Los nombres chinos de los clientes vienen ocultos (■■■) en los PDFs.

## 7. Límites de la versión 1.0

- Cada equipo guarda sus propios datos (navegador). Se pasan con respaldo `.json`. La base compartida (Supabase) está preparada, no conectada.
- El inicio de sesión se valida en el mismo equipo (SHA-256); no es seguridad de servidor.
- «Enviar por correo» usa el menú de compartir o `mailto:`; no hay servidor de correo.
- El logo es una recreación en SVG.
