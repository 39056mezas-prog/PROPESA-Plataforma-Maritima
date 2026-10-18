# HISTORIAL.md · Bitácora completa del proyecto

> Registro cronológico de todas las rondas de trabajo (antes `PROYECTO_PROPESA.md`). Las secciones 0–15 son la foto del proyecto al inicio; las rondas con fecha van al final, de la más vieja a la más nueva.
> **La información vigente está en los demás archivos de `docs/`.** Si algo de aquí los contradice, valen ellos y el código. Agrega cada ronda nueva al final.

---

## 0. Cómo usar este archivo

1. Abre una conversación nueva (o un proyecto de Claude) y sube **este .md** y **`index.html`** (el código es la fuente de verdad; está dentro de `propesa-plataforma.zip`).
2. Pega un primer mensaje como este:

   > Lee `PROYECTO_PROPESA.md` e `index.html`. Vamos a seguir con la plataforma PROPESA. Antes de cambiar nada, dime en 5 líneas qué entendiste del proceso y qué tarea del To-do vamos a atacar. No cambies el flujo ni los textos sin confirmármelo.

3. Pide **un cambio a la vez**, con una prueba al final. Los cambios grandes se validan primero con el equipo de piso (ver sección 9).
4. Después de cada sesión actualiza las secciones **4 (Estado)**, **12 (Decisiones abiertas)** y **13 (To-do)** de este archivo.

---

## 1. Qué es PROPESA y qué hace la plataforma

- **Empresa:** Proveedor del Pescador S.A. de C.V. (PROPESA), Ensenada, B.C. Langosta roja viva en almacenaje húmedo (tanques) y exportación por vía aérea a China.
- **Objetivo de la plataforma:** seguir cada lote de langosta desde que entra hasta que se envía y se calcula su mortalidad, en una tablet, por personal de piso con poca experiencia técnica (manos mojadas o con guantes, poca luz).
- **Principio de diseño:** quien mire la pantalla debe entender **dónde está, qué sigue y qué falta**.

### Flujo final (decidido por el usuario)

**Entrada → Órdenes → Empaque → Embarque → Mortalidad final**

| # | Paso | Qué se hace | Quién |
|---|---|---|---|
| 1 | **Entrada** | Se captura el formato de recepción del lote: fecha, hora, proveedor, tanque, temperaturas, lote (mayúsculas automáticas), kg por caja en tanque, kg por talla, kg total, kg desperdicio. | Administrador |
| 2 | **Órdenes** | Pedido de un empaque: ciudad destino → consignatario → cliente final → cajas. | Administrador |
| 3 | **Empaque** | Al empacar cada pedido se cuentan las langostas de cada caja (lote, piezas vivas, categoría). La caja se numera ahí. | Administrador y encargado de piso |
| 4 | **Embarque** | Un embarque puede juntar varias órdenes (mismo destino y consignatario). Por cada consignación: tallas, peso bruto, plan de carga, cierre del empaque e informe por correo. | Administrador |
| 5 | **Mortalidad final** | Conteo final por lote y langostas vivas al llegar; se calcula la pérdida. | Administrador y piso (captura); admin cierra |

**Hecho clave del negocio (corregido por el usuario):** en los tanques las cajas **no se numeran ni se cuentan**. Solo se conocen los **kilos por talla** del lote. El conteo de piezas por caja se hace **al empacar cada pedido**.

### Glosario

- **Lote:** una entrada de producto. Código tipo `WLRCO170926` = `WLR` (langosta roja) + proveedor (`CO` Cooperativa/SCPP Ensenada, `EM` Emancipación, `LE` Leyes de Reforma) + fecha `ddmmyy`. *(Inferido de los PDFs; confirmar.)*
- **Tallas (gramos):** 491-610, 611-850, 851-1220, 1221-UP. En el papel también aparecen como 0-650, 651-850, 851-1250, 1251-UP.
- **Caja / hielera:** en la plataforma se tratan como lo mismo. Una caja lleva 16 kg netos y 20 kg brutos (según la orden a proveedor).
- **Consignatario:** a quién se factura en China (lista oficial de 7).
- **Cliente final:** código de 3 letras (HXH, ZSM, ZYX, RSK, LHD, HSF, HYG, HJX, LMD, MXH). Una orden a PVG se reparte entre varios clientes.
- **Consignación:** en la plataforma, cada grupo (orden + ciudad + consignatario) genera una consignación en Embarque, llamada p. ej. `PVG · YISHUNHAI · 07/10`.
- **ETD:** fecha de empaque/salida de la orden.
- **PVG / HKG / XMN / SZX / CAN / SIN:** Shanghái, Hong Kong, Xiamen, Shenzhen, Guangzhou, Singapur.

---

## 2. Documentos de origen (los PDFs que dio el usuario)

| Documento | Qué contiene | ¿Ya está en la plataforma? |
|---|---|---|
| `PROPESA_Control_Recepcion.pdf` | Registro de control de recepción y tallas (fecha, hora, proveedor, tanque, T°F tanque, T°F producto, lote, kg por caja, kg por talla, total, desperdicio) | **Sí**: es el formulario de Entrada |
| `control_de_pesos_y_tallas.pdf` (Formato 02, FL 003) | Pesos por tina (1-180), totales por talla, cajas completas/incompletas, observaciones, temperatura 57.7–62.2 °F | **No** |
| `Recepcion_Variedades.pdf` | Registro de envío/logística: fecha, destino, consignatario, color de tape, proveedor, tanque, temperaturas, lotes mezclados, kg por talla, cajas, % mortalidad, temp. de arribo | **No** (solo se calcula mortalidad) |
| `orden_a_proveedor.pdf` | Orden con ETD, cliente, destino, cajas por cliente, cajas total por destino, peso neto y bruto | **Sí**: base del módulo Órdenes |
| `tabla_logistica.pdf` | Registro por cliente y destino (PVG, XMN, HKG) con cantidad de cajas y kg neto | Parcial (no se cargó) |
| `lista_de_consignatarios.pdf` | Lista oficial de 7 consignatarios con dirección, contacto y USCI | **Sí** (constante `CONS`) |
| `packing_list.pdf` (Formato 06) | Packing list por caja: número, piezas vivas, cliente; encabezado con placas, chofer, horas, temperaturas, peso bruto | Parcial (packing list sí; encabezado no) |
| Fotos | Tanques, langostas, pesaje, tarima (ya no están en la demo) | Solo como "Fotos y notas" |

Los nombres chinos de los clientes vienen ocultos (■■■) en los PDFs.

---

## 3. Estructura del proyecto

```
propesa-plataforma/
├── index.html              ← TODA la aplicación (HTML + CSS + JS, ~100 KB, sin dependencias)
├── manifest.webmanifest    ← "Agregar a pantalla de inicio" en tablet
├── favicon.svg · icon-192.png · icon-512.png · apple-touch-icon.png
├── vercel.json             ← encabezados de seguridad y caché
├── .gitignore
└── README.md               ← flujo, primer uso, despliegue, pruebas y vuelta atrás
├── CHANGELOG.md            ← cambios por versión
```

- **Sin build, sin npm.** Se abre con doble clic o con `python3 -m http.server`.
- **Despliegue:** GitHub + Vercel (Framework Preset: *Other*, sin comando de compilación ni carpeta de salida).
- **Archivo suelto:** `PROPESA_Plataforma_maritima.html` es la misma app en un solo archivo.

---

## 4. Estado actual (qué funciona y qué falta)

**Funciona (todo en el navegador):**
- Acceso con 3 usuarios y 3 roles.
- Entrada: formulario con los campos del formato en papel, tabla igual al formato, detalle de lote, edición y eliminación.
- Órdenes: crear orden, agregar/eliminar líneas, totales netos/brutos, avance de empaque, packing list y descarga CSV.
- Empaque: agregar cajas por cliente (lote, piezas, categoría), numeración automática, quitar cajas, bloqueo si el empaque está cerrado.
- Embarque: consignaciones creadas por las órdenes, plano de camión dinámico (210 hieleras), distribución por talla editable, peso bruto calculado, avisos, cierre con informe (PDF en Administración → Informes de cierre).
- Mortalidad final: conteo final por lote, cierre de lote, langostas vivas por envío, gráficas.
- Fotos y notas (hasta 6 por nota, cámara o galería) en Entrada, lote, Empaque, Embarque, Mortalidad final y Temperatura.
- Panel con "Tu siguiente paso", totales, tablero de lotes y actividad.
- Accesibilidad básica: foco visible, saltar al contenido, tamaño de letra (3 botones A), objetivos táctiles grandes, menú lateral que se oculta en teléfono.
- Los formularios **conservan lo escrito** si hay un error.

**Límites de la v1.0 / no existe todavía:**
- **Los datos viven solo en `localStorage` de cada navegador.** Nada se comparte entre dispositivos (respaldo `.json` para pasarlos).
- Usuarios creados en la app (Configuración inicial + Administración); contraseñas con hash SHA-256, validadas en el navegador (no es seguridad de servidor).
- «Enviar por correo» = menú de compartir / `mailto:`; no hay servidor de correo.
- **Temperatura:** bitácora real `ST.T` (ya no hay datos de ejemplo).
- No hay captura de: Formato 02 (pesos por tina), encabezado del packing list (placas, chofer, horas), color de tape, temperatura de arribo.
- El logo es una **recreación en SVG** (no el archivo original).

La plataforma **inicia vacía y sin usuarios**: pide crear el Administrador (`setupView`). «Borrar los datos de este equipo» (Administración, escribir BORRAR) la regresa a ese punto.

---

## 5. Arquitectura técnica

### Patrón general
- **Una sola página** con JavaScript vanilla. Render por plantillas de texto (`` `...${x}...` ``) que se escriben en `#app.innerHTML`.
- Estado global `ST` (objeto). `render()` vuelve a dibujar todo; `save()` guarda `ST` en `localStorage` con la clave **`propesa-v4`**. El tamaño de letra se guarda aparte en `propesa-z`.
- `go('ruta:parámetro')` cambia de página (`V = {v, id}`) y llama a `render()`.
- `E()` escapa texto antes de ponerlo en HTML. **Usar siempre `E()` con texto del usuario.**

### Rutas (`PG`) y paso del menú (`STEP`)
`inicio, recepcion, lote:<lote>, ordenes, orden:<id>, empaque, empacar:<ordenId>.<lineaId>, embarques, emb:<índice>, cierre, temperatura, admin, buscar:<texto>`

| Paso del menú | Rutas |
|---|---|
| 1 Entrada | `recepcion`, `lote` |
| 2 Órdenes | `ordenes`, `orden` |
| 3 Empaque | `empaque`, `empacar` |
| 4 Embarque | `embarques`, `emb` |
| 5 Mortalidad final | `cierre` |

*Los nombres internos de ruta no se cambiaron (p. ej. `recepcion` y `cierre`); solo cambiaron los textos visibles.*

### Eventos
Un manejador de clic principal usa atributos `data-*`: `data-go` (navegar), `data-a` (acciones: `sv`, `nf`, `el`, `dl`, `mv`, `cl`, `su`…). Hay manejadores propios (se registran con `document.addEventListener`) para: notas y fotos (`data-ev`), órdenes (`data-oa`), empaque (`data-pk`), tamaño de letra (`data-z`), tallas del embarque (`data-zs`).

### Funciones clave
`render, go, save, load, seed, migratePK, cleanOrders` · páginas: `inicio, recepcion, lote, ordenes, orden, empaque, empacar, embarques, emb, cierre, temperatura, admin` · lógica: `post` (movimientos), `bal` (existencia en gramos), `calc` (mortalidad por lote), `gross` (peso bruto), `shipFor / syncShip` (consignaciones desde órdenes), `ordAssigned / ordBoxes / ordTot / ordAsg`, `shipIssues / shipAlert` (alertas), `closeP / closeLot`, `saveLot / saveU` (formularios), `renderKeep / fail` (conservan lo escrito), `evid` (fotos y notas), `truck` (plano del camión), `nxt` (siguiente paso), `iconize` (convierte ⚠ ✔ ✕ ☰ ● en íconos SVG).

### Constantes
`KGN=16` kg netos/caja · `KGB=20` kg brutos/caja · `S` tallas · `SL` etiquetas de talla del formato · `TK` tanques T1–T6 · `RC` categorías · `CONS` consignatarios · `PORTS` ciudades · `CLI0` códigos de cliente · `STG` etapas del lote · `ROLE` · `PAL`/`XC` colores.

### Convenciones
- Los kilos se guardan en **gramos** (`m`), se muestran en kg con `f()`.
- Fechas: `rdate` ISO (`YYYY-MM-DD`) y `date` en `dd/mm/aaaa`. Las órdenes usan `etd` ISO.
- Cualquier cambio de estructura de datos debe traer **migración** con una bandera (`PK`, `ORc`, `E0`) para no romper los datos ya guardados en el navegador.
- Mantener la página en un solo archivo hasta tener backend.

---

## 6. Modelo de datos (`ST`)

```js
ST = {
  PK:1, BN:0, ORc:1, E0:1,          // banderas de migración y contador de cajas (BN)
  U:[{id,name,email,pw,role,notify}],// usuarios; role: 'admin' | 'piso' | 'consulta'
  R:[{                              // lotes (entradas)
    id,'R-0121', lot, origin /*proveedor*/, tank, rdate, time, date,
    tempT /*°F tanque*/, tempP /*°F producto, texto/rango*/, kgbox, desp /*kg desperdicio*/,
    final /*kg conteo final|null*/, closed
  }],
  L:[{id,t,type,lot,size,m /*gramos*/,rev,rc}],   // movimientos de existencia por talla (RECEPCION, SALIDA_EMBARQUE…)
  B:{ [lot]:[{ c /*piezas vivas*/, k /*'R'|'V'|'B'*/, d /*índice en P*/, o /*'ordenId.lineaId'*/, seq }] }, // SOLO cajas ya empacadas
  OR:[{ id, etd, lines:[{id,city,cons /*índice en CONS*/,cli,boxes}], sh:{ 'CIUDAD|cons': índiceEnP } }],
  P:[{ n, z0, col, exp, h /*hieleras*/, z:[4 tallas en hieleras], c:[[nombre,kgUnit,cantidad]], alive, closed }], // consignaciones
  O:[{subject,t,…}],                // informes de cierre
  T:[{id,t,tank,a,s,p,by}],         // lecturas de temperatura (°F)
  M:{ [clave]:[{id,t,by,text,ref,imgs:[dataURL]}] } // fotos y notas; claves: 'recepcion','lote:<l>','emp:<oid.lid>','emb:<i>','cierre','temp'
}
```

---

## 7. Reglas de negocio implementadas

- **Existencia por lote** = suma de movimientos (`L`). La entrada crea un movimiento `RECEPCION` por talla. La salida a embarque se registra como movimiento **manual** en la página del lote. *Empacar una caja NO descuenta kilos.*
- **Kg total de entrada** = suma de las 4 tallas (solo lectura, se calcula). **Desperdicio** es un dato informativo; no resta existencia.
- **Orden:** neto = cajas × 16 kg; bruto = cajas × 20 kg. Una línea no admite más cajas empacadas que las pedidas.
- **Consignación:** se crea una por (orden + ciudad + consignatario). Sus hieleras = cajas de la orden. Peso bruto = hieleras × (1.4 hielera + 1.5 gel + 16 producto + 0.7 caja de cartón) = **19.6 kg/hielera**.
- **Alertas de embarque (rojo):** peso bruto ≠ formato, tallas ≠ hieleras (con tallas en 0 también avisa), cajas sin cantidad/categoría, sin cajas empacadas.
- **Cerrar empaque (solo admin):** requiere al menos una caja empacada; guarda el informe de cierre (Administración → Informes de cierre, con PDF).
- **Mortalidad por lote:** esperado (existencia) − conteo final, y su %. El conteo final no puede exceder lo esperado. **Por envío:** enviadas − vivas al llegar.
- **Bloqueos:** con el empaque cerrado no se agregan ni quitan cajas de ese destino. No se elimina un lote con cajas empacadas para envíos. No se elimina una línea con cajas.
- **Plano del camión:** 10 celdas (2 filas × 5 columnas) de 15/20/20/25/25 hieleras = 210. Se llena desde la cabina; avisa si se excede.

---

## 8. Roles y permisos

| Acción | Administrador | Encargado de piso | Consulta |
|---|---|---|---|
| Ver todo | Sí | Sí | Sí |
| Empacar cajas, capturar conteos finales (`can('box')`, `can('fin')`) | Sí | Sí | No |
| Fotos y notas | Sí | Sí | No |
| Crear/editar/eliminar entradas y órdenes (`can('lot')`) | Sí | No | No |
| Cerrar empaques y lotes | Sí | No | No |
| Usuarios y administración | Sí | No | No |

Sin usuarios precargados. Las pruebas automáticas crean sus propios usuarios de prueba (solo dentro de `pruebas/`).

---

## 9. Diseño y preferencias del usuario (importante: ya se discutieron)

### Lo que el usuario pidió y se mantiene
- **Logo PROPESA** en el menú lateral y en el acceso; **pequeño** (≈128 px en el menú); **blanco** sobre fondos oscuros.
- **Menú lateral azul marino** con los pasos numerados e íconos de dibujo (no emojis).
- **Campos de captura con relleno blanco**, menús desplegables con flecha propia, números sin flechitas, teclado numérico en tablet, texto seleccionado al tocar.
- **Azul solo en secciones de marca** (menú, encabezado, banner, acceso). Fondo y textos neutros.
- **Pendientes y discrepancias en rojo y llamativos**, con ícono y texto (no solo color).
- **Cierre/Mortalidad final NO va en rojo como faltante** (es el último paso).
- **Colores de consignaciones PVG/HKG parecidos a los originales** (verde azulado, dorado, violeta).
- **Optimizado para tablet:** objetivos táctiles grandes, rejillas que se adaptan, menú fijo en tablet y desplegable en teléfono.
- **Los formularios no deben borrar lo escrito** cuando hay un error.
- Un usuario no técnico debe poder usarla: textos simples, un paso a la vez, mensajes claros.

### Lo que el usuario RECHAZÓ (no volver a hacerlo sin preguntar)
- El **sistema de color semántico oscuro** (cian/verde/ámbar/rojo/morado sobre fondo negro-navy, números gigantes, estados en el menú). Se revirtió por completo.
- La **galería de fotos de lotes en el Panel**. Se revirtió.
- **Cambiar muchas cosas sin validarlas**: el equipo sintió que se trabajaba "sin rumbo".

### Cómo trabajar con este proyecto
1. Confirmar el entendimiento del proceso **antes** de programar.
2. Un cambio a la vez, con prueba (ver sección 10).
3. Validar cambios de flujo con el compañero de piso (existe una hoja de una página con el proceso).
4. No inventar reglas de negocio: si falta un dato, preguntar (sección 12).

---

## 10. Pruebas

No hay suite formal. Se probó con **Playwright (Python)** sirviendo la carpeta con `python3 -m http.server` y recorriendo flujos: login → crear entrada → crear orden → empacar → embarque → mortalidad, además de un barrido de todas las páginas buscando `NaN` o `undefined`.

Pendiente: convertir esas pruebas en un archivo `tests/` dentro del repositorio y correrlas en CI.

---

## 11. Despliegue

```bash
cd propesa-plataforma
git init && git add . && git commit -m "PROPESA plataforma"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/propesa-plataforma.git
git push -u origin main
```

Vercel: <https://vercel.com/new> → importar el repositorio → *Framework: Other* → Deploy. Cada `git push` a `main` vuelve a desplegar. Sin variables de entorno por ahora.

---

## 12. Decisiones abiertas (preguntar al usuario antes de implementar)

1. **Peso bruto:** la orden usa **20 kg/caja** y la consignación calcula **19.6 kg/hielera**. ¿Con cuál se trabaja y cómo se compone?
2. **Categorías:** la app usa Rojo/Verde/Blanco por caja; el packing list en papel muestra R/V/A y D (despatada) ligadas a la talla. ¿La categoría debe ser en realidad la **talla**? ¿Existe "Azul"?
3. **Inventario:** empacar no descuenta kilos del tanque. ¿Debe descontar? Eso exige capturar la **talla** (y quizá el peso real) de cada caja.
4. **Desperdicio:** ¿resta de la existencia o es solo informativo?
5. **Varios tanques por lote** (en el papel aparecen "1/2", "3 y 1"). Hoy es un solo tanque.
6. **Lotes mezclados en un envío** (en el papel un envío lleva 2-3 lotes): ya se permite al empacar; ¿se necesita verlo por envío?
7. **Cajas = hieleras:** ¿siempre equivalen?
8. **Mortalidad:** ¿la definición actual (esperado − conteo final por lote; enviadas − vivas por envío) es la que usan? El papel reporta "% mortalidad" y "temperatura de arribo" por envío.
9. **Encabezado del packing list:** placas, chofer, teléfono, horas, temperatura del producto, tanque y temperatura. ¿Se captura en la plataforma?
10. **Color de tape** por consignatario (aparece en el control de envío).
11. **Temperatura:** ¿quién captura, cada cuánto y con qué alertas? (rango de almacenamiento visto: 57.7–62.2 °F; transporte 48–49 °F).
12. **Pedidos de varios días hacia la misma ciudad y consignatario:** RESUELTO en parte (oct 2026): se pueden unir varias órdenes en un embarque (`shipLinks`, `moveGroup`, `dropShip`). Pendiente confirmar si se unen órdenes de fechas distintas y cómo se factura.
13. **Idioma:** ¿se necesita versión en inglés/chino para los socios?
14. **Logo oficial:** subir el archivo original para reemplazar la recreación.

---

## 13. To-do priorizado

### P0 · Antes de programar más
- [ ] Probar el flujo completo con el compañero de piso (usar la hoja de una página y el manual).
- [ ] Contestar las decisiones abiertas 1–4 (afectan el modelo de datos).
- [ ] Subir el logo original y fotos de pantalla/papel reales para ajustar textos.

### P1 · Convertirla en una herramienta real (sin esto no se puede usar en producción)
- [ ] **Backend y datos compartidos** (recomendado: Supabase — Postgres + Auth + Storage). Pasar `ST` a tablas: `lotes`, `movimientos`, `ordenes`, `lineas_orden`, `cajas`, `consignaciones`, `usuarios`, `notas`, `fotos`.
- [ ] **Inicio de sesión real** (Supabase Auth) y permisos por rol con políticas de seguridad en la base (RLS). Quitar contraseñas del código.
- [ ] **Fotos** a almacenamiento (hoy son base64 en el navegador).
- [ ] **Correo real** del informe de empaque (p. ej. Resend o SendGrid) en lugar del simulado.
- [ ] **Importar** los datos históricos de los PDFs/Excel (recepciones y envíos ya registrados).
- [ ] **Respaldo y registro de auditoría** (quién cambió qué y cuándo).

### P2 · Funciones del proceso que aún están en papel
- [ ] **Formato 02 · Control de pesos y tallas:** captura por tina (1–180), totales por talla, cajas completas e incompletas, observaciones, temperatura.
- [ ] **Encabezado del packing list** (placas, chofer, horas, temperaturas, peso bruto) y exportarlo a **PDF/Excel** con el formato oficial.
- [ ] **Temperatura:** captura de lecturas por tanque, con alertas fuera de rango.
- [ ] **Control de recepción y envío** (el registro por envío con % mortalidad y temperatura de arribo).
- [ ] **Editar/eliminar órdenes completas**, editar cajas ya empacadas y reordenar el packing list.
- [ ] **Descontar kilos al empacar** (según decisión 3) y conciliación de existencias.
- [ ] Alertas: lote sin movimiento, empaque con peso fuera de tolerancia, tallas que no suman.
- [ ] Reportes: mortalidad por proveedor/mes, productividad de empaque, existencias por tanque.

### P3 · Calidad y experiencia
- [ ] **Modo sin conexión** (PWA con service worker) para zonas con mala señal.
- [ ] Escaneo de código de barras/QR para lote y cajas; impresión de etiquetas.
- [ ] Pruebas automáticas (carpeta `tests/`) y CI en GitHub.
- [ ] Separar el código en módulos (cuando haya backend) o migrar a un framework solo si se justifica.
- [ ] Prueba de usabilidad con personal de piso (guantes, poca luz) y ajuste de tamaños.
- [ ] Auditoría de accesibilidad con lector de pantalla y contraste real en tablet.
- [ ] Versión en otros idiomas.

---

## 14. Historial resumido (para no repetir errores)

1. Se partió de un HTML ya funcional de PROPESA (lotes, cajas, envíos y mortalidad) y se le agregó logo, menú lateral, paleta del logo y campos blancos.
2. Se quitó el exceso de azul, se restauraron colores de PVG/HKG y se hicieron alertas rojas.
3. Se optimizó para tablet, se agregaron íconos de dibujo, fotos y notas, y la barra "contando el lote".
4. Se pulió con la guía de diseño Impeccable (contraste, íconos, sin franjas laterales). Un rediseño oscuro con colores semánticos fue **rechazado** y revertido.
5. Se agregó el módulo de **Órdenes** (consignatarios, clientes finales, packing list).
6. Se vació toda la demo (inicio desde cero) y se hizo dinámico el plano del camión.
7. **Cambio de modelo (el más importante):** se eliminaron las cajas numeradas en tanque; las langostas se cuentan en **Empaque**. Se renombró el flujo a *Entrada → Órdenes → Empaque → Embarque → Mortalidad final* y se rehizo la **Entrada** con los campos del formato en papel.
8. Se escribieron un manual de usuario y una hoja de una página (la hoja de una página **aún describe el flujo viejo**; actualizar).

---

## 15. Prompts útiles para continuar

- "Lee `PROYECTO_PROPESA.md` e `index.html`. Resume el flujo y dime qué entendiste antes de tocar código."
- "Vamos con la decisión abierta #3: propón las opciones para descontar kilos al empacar, con pros y contras, sin implementar todavía."
- "Implementa solo el encabezado del packing list (placas, chofer, horas, temperaturas) en la página de la orden, con migración de datos y una prueba de punta a punta."
- "Diseña el esquema de base de datos en Supabase para el modelo de la sección 6 y muéstrame las tablas antes de crearlas."
- "Actualiza el manual de usuario y este archivo con lo que cambió hoy."

---

*Última actualización: octubre 2026 · versión de la plataforma: 1.0.0 con flujo Entrada → Órdenes → Empaque → Embarque → Mortalidad final.*

## Cambios de la ronda del 10/oct/2026
- Lote de recepción se escribe en MAYÚSCULAS en vivo; el campo de Entrada ahora se llama **Kg por caja en tanque** (clave interna `kgbox`).
- **Empaque:** una fila por cada caja que falta (piezas vivas, categoría, lote), se guardan todas a la vez (`pkGrid`, `data-pk="addall"`); solo notas, sin fotos (`evid(key,title,1)`).
- **Embarque con varias órdenes:** `o.sh['CIUDAD|cons']` puede apuntar al mismo índice de `ST.P`; `syncShipIdx` suma hieleras de todas las órdenes; `moveGroup` une/separa (mueve también `b.d` de las cajas); `dropShip` borra embarques vacíos y reindexa. UI: «Unir» en la orden, «Agregar otra orden»/«Separar» en el embarque. El nombre del embarque junta las fechas (`PVG · YISHUNHAI · 12/10 + 13/10`).
- Ícono de Embarque = el de Recepción (camión). Entrada y Embarque hoy se ven iguales.
- Bug corregido: las notas de Empaque y Embarque no se guardaban (la clave con `:` se cortaba en `data-ev`).

## Ronda del 10/oct/2026 (tarde): PDF, vistas y plan de sincronización
**Decisiones del usuario:** la copia web será **Supabase** (**no conectar la cuenta todavía**); capturan **varias tablets** y además hay gente que **solo consulta** (computadora o celular, la vista debe adaptarse); hay internet **casi siempre**; el archivo final de cada paso es un **PDF**, y **ese mismo PDF es el que se manda por correo**.

**Hecho:**
- Generador de PDF propio (`PdfRep`, `pdfEntrada/Ordenes/Empaque/Embarque/Embarques/Mort`; Helvetica WinAnsi con métricas reales, logo en JPEG, tablas con encabezado repetido, paginación). Botones `data-pdf="dl|mail:<tipo>:<arg>"` en cada paso (`pdfBar`). `Enviar por correo` usa Web Share con archivo (tablet/celular) y, si no existe, descarga + `mailto:` con los usuarios marcados «Recibe informes».
- El correo simulado del cierre trae `pn` (nombre del embarque) y `att` (nombre del PDF); Administración permite descargar ese PDF.
- Vistas: revisadas a 390, 820 y 1440 px; en celular las filas de Empaque se vuelven tarjetas.
- Administración → «Datos y respaldo»: respaldo y restauración `.json`.
- `supabase/schema.sql`: tablas con UUID, RLS por rol (admin/piso/consulta), realtime y bucket privado `reportes`. **No se ha aplicado.**

### Sincronización (pendiente, requiere conectar la cuenta)
Hoy cada tablet tiene sus propios datos. Para compartir hay que cambiar antes el modelo de la app:
1. **IDs estables:** hoy los embarques se identifican por su posición en `ST.P`, las órdenes/líneas con `max+1` y las cajas con `++BN`; dos tablets chocarían. Pasar a UUID (o `Date.now()+aleatorio`) y que `b.d` y `o.sh` apunten a ids, no a índices.
2. **Local primero:** seguir guardando en localStorage y mandar los cambios a una cola; subirlos cuando haya internet (casi siempre) y marcar «pendiente de sincronizar».
3. **Conflictos:** cajas, movimientos y notas solo se agregan (no chocan); órdenes, embarques y lotes se editan por campo con «último cambio gana» y `updated_at`.
4. **Usuarios reales:** reemplazar los usuarios demo (contraseña en claro) por Supabase Auth + tabla `profiles`.
5. **Vista de consulta:** la misma página, en solo lectura, con Realtime.
6. **Correo con PDF:** al cerrar un embarque, subir el PDF al bucket `reportes` y mandarlo con una Edge Function (Resend o SMTP) a los usuarios con «Recibe informes». Hace falta decidir remitente/dominio.
**Preguntas abiertas:** ¿quién puede editar una orden ya empacada? ¿Se permite capturar sin internet y sincronizar después (ya se asume que sí)? ¿Dominio y remitente del correo? ¿Los de consulta entran con correo y contraseña?

## Paleta de color (10/oct/2026)
Se aplicó `PROPESA_Color_System_Refinement.md` solo como cambio de colores (sin tocar layout ni lógica). Tokens nuevos en `:root`: `--brand-navy #0B1D59`, `--brand-blue #087DBA`, `--brand-cyan #16A6D1`, `--ok/--okb/--okf` (verde de éxito). Tema oscuro: `--bg #111827`, `--cd #1C2638`, `--ln #2D3B50`, `--ink #F1F5F9`, `--mut #A9B7CA`, `--in #243249`, `--hl #2D3B50`. `--ac` (botones, chips seleccionados) pasó de turquesa a azul océano; el verde de «Completa» ya no usa el color de marca; progreso, línea de tiempo e íconos de notas usan cian; el item activo del menú lleva una barra cian sobre un navy más claro (`#1B3680`). El encabezado, que era blanco fijo, ahora es pizarra en tema oscuro. Contrastes medidos: texto principal 13.9:1 sobre tarjeta, secundario 7.5:1, blanco sobre azul 4.5:1, cian sobre tarjeta 5.4:1, verde 6.7:1. Rojo/ámbar/verde se dejaron como estados, no como marca. Pendiente: el logo (`LGP`) conserva sus azules originales (`#0a2373`, `#0583c3`), que difieren un poco de los tokens.

## Ronda del 12/oct/2026: error corregido, colores de talla y Modo piso
- **Bug grave corregido:** las filas de Empaque usaban el atributo `data-r`, el mismo que el botón «Revertir» de movimientos. Tocar el campo de piezas de la caja 2, 3… **revertía un movimiento de recepción** (bajaba el inventario sin avisar) y la caja 1 causaba el error `reading 'lot'`. Ahora es `data-row`, `rev()` valida, y en la página del lote hay **«Anular reversa»** (admin) para deshacer reversas que no se hicieron a propósito.
- **Colores de talla** (`SZC`, `szDot`): 491-610 Blanco · 611-850 Rojo · 851-1220 Verde · 1221-UP Amarillo; borde de 4 px en los campos y punto de color en etiquetas y encabezados.
- **Modo piso** (`PISO`, `pisoShell`, `pisoHome`, `pisoEmp`, `pisoEnt`; rutas `piso`, `pemp[:orden.línea]`, `pent`): inspirado en la investigación de McDonald's (cero fricción, botones grandes, revelación progresiva, a prueba de errores, colores que se reconocen sin leer). El rol piso entra directo; el admin lo activa desde el menú. Preferencia por equipo en `localStorage['propesa-piso']`.
- **Permiso nuevo `ent`:** el Encargado de piso ya puede registrar entradas (editar/eliminar lotes sigue siendo solo del admin).
- Pendiente de validar con el piso: si prefieren capturar caja por caja con teclado (modo piso) o varias filas a la vez (vista completa); si «Cerrar embarque» y «Conteo final» también necesitan su propio flujo paso a paso (hoy abren la pantalla normal sin menú).
- **12/oct (cont.):** el aviso rojo «X de Y cajas empacadas» (orden, Empaque, Panel) ahora es un botón que lleva al primer cliente con cajas pendientes (`pendKey`, `goPend`, `pendChip`); al completar un cliente aparece «Siguiente cliente que falta». El Modo piso ya **no es una caja a la vez**: muestra una tarjeta grande por cada caja pendiente y guarda todas juntas (reutiliza `PKD` y `data-pk="addall"`); «Poner a todas las vacías» (`data-pe="all:K"`, marca `auto`) no obliga a llenar las cajas que siguen vacías. Se quitó el teclado numérico.
- **12/oct (cont. 2):** Modo piso → cada cliente muestra **todas** sus cajas como tarjetas en lugares fijos (`peSlots`, campo nuevo `b.ps` = lugar 1..N del cliente). Una caja se guarda sola cuando tiene piezas y categoría (`peTry`), queda en gris con ✔ y sigue en pantalla: se corrigen piezas (`.psc`, al salir del campo) o categoría (`data-pe="sk:seq:K"`) ahí mismo, o se quita con confirmación (`cf`/`rm`) y el lugar queda libre. Al completar, aparece un aviso arriba y las tarjetas no desaparecen. Ya no hay botón «Guardar cajas» en piso. La vista completa sigue con su tabla + «Guardar cajas».
- **12/oct (cont. 3):** el logo es un botón de inicio en ambos modos (`.lgb`: vista completa → `inicio`, piso → `piso`). El cambio de modo es un interruptor estilo iOS (`.iosrow`/`.iossw`, `role="switch"`, verde #34C759 encendido) en el menú lateral y en el encabezado de piso; al tocarlo, la perilla se desliza y luego toda la pantalla cambia con una transición suave (`switchMode`, View Transitions API; sin animación si el equipo pide movimiento reducido). Encabezado de piso translúcido con desenfoque, título grande y tarjetas con degradado y cuadros de ícono al estilo iOS.
- **12/oct (cont. 4):** al iniciar sesión, el Administrador siempre entra a la vista completa y el Encargado de piso al Modo piso (antes la preferencia del equipo hacía que el admin entrara en piso).
- **12/oct (cont. 5):** todos los avisos rojos llevan a donde se resuelven: chips «Faltan N · Empacar ›» (Panel, Empaque, Orden, Órdenes del embarque → cliente con cajas pendientes; `goLine`, `lineSt(n,t,go)`), «Sin líneas · Agregar ›» para órdenes vacías (antes decía «Faltan 0»), tarjetas KPI rojas del Panel con «Resolver ›», y cada renglón de la alerta del embarque con «Resolver ›» (`shipIssues` ahora devuelve `{t,go|jump}`; `data-jump` hace scroll al campo, lo enfoca y lo resalta). Los chips «NO SUMA» y «DISCREPANCIA» también llevan al campo a corregir.

## Correcciones del /review (12/oct/2026)
1. **Guardado fallido visible:** `save()` devuelve true/false; si la memoria se llena, aparece un aviso rojo fijo con «Descargar respaldo» y «Reintentar guardar», y ningún mensaje dice «Guardado» mientras falle (`SAVE_ERR`, `topBanners`).
2. **Acceso:** se quitaron los botones demo del inicio de sesión; las contraseñas se guardan como hash SHA-256 con el id del usuario (`pwHash`, `migrateUsers`, migración automática de datos viejos); aviso rojo mientras haya contraseñas de prueba; mínimo 6 caracteres; no se puede dejar sin Administrador. *Sigue siendo seguridad del lado del navegador: la protección real requiere Supabase Auth.*
3. **Fechas locales:** `dLoc()` reemplaza `toISOString()` (fecha de recepción, ETD sugerida, nombres de PDF, entrada en Modo piso).
4. **Respaldo seguro:** `E()` escapa también la comilla simple; el tanque se escapa al mostrarse; `cleanST()` revisa campo por campo cualquier respaldo antes de cargarlo (descarta código, imágenes no válidas, índices fuera de rango, respaldos sin administrador).
5. **Embarque cerrado:** ya no se pueden agregar líneas a un destino cuyo embarque está cerrado (aviso para reabrirlo o crear otra orden).
6. **Número de lote:** `newLotId()` con contador `ST.RN` que solo crece.
Pendientes sugeridos por la revisión: mover fotos a IndexedDB, índice de cajas por cliente (rendimiento), dividir `index.html` en módulos, guardar las pruebas automáticas en el repositorio.

## Rendimiento (/webperf, 12/oct/2026)
**Medición:** Lighthouse (lab) 99 celular / 100 computadora en la pantalla de entrada. Con datos simulados de un año (500 lotes, 37,400 cajas, 250 órdenes y embarques) y CPU frenada 4× (≈ tablet): Panel 7,943 → **37 ms**, Empaque 5,669 → **30 ms**, Modo piso 3,223 → **20 ms**, guardar una caja en piso 1,662 → **130 ms**.
**Cambios:**
- Índices por dibujo (`RX`, `rxLine`, `rxShip`, `rxMov`, `rxLinks`, `rxLot`, `rxRvd`): `render()` crea los índices una vez y `ordAssigned`, `boxesOf`, `bal`, `rcv`, `rvd`, `calc`, `shipLinks` y `R_` los usan; fuera del dibujo siguen calculando directo (los manejadores ven siempre datos frescos). Verificado: resultados idénticos al cálculo original con un año de datos. Se corrigió además un cálculo cuadrático en `calc()` (`rvd()` se rehacía por cada movimiento).
- Listas activas (`histList`, `HIST`, `data-hist`): Entrada, Órdenes, Panel, Empaque, Embarque y Mortalidad muestran solo lo abierto o reciente (lotes 30 días, órdenes y embarques 14 días); «Ver historial» abre de 100 en 100. El tablero de lotes muestra 12 por columna. El plan de carga del camión cuenta solo embarques abiertos. Las gráficas de mortalidad muestran los últimos 20.
**Pendiente:** `save()` reescribe todo (≈80 ms en tablet con un año): archivo de cerrados / IndexedDB / Supabase. Fotos a IndexedDB.

## Panel de Ajustes (12/oct/2026, con /spec)
Especificación aprobada en `SPEC.md`, plan en `tasks/plan.md`, pruebas en `pruebas/ajustes_t.py` (88 verificaciones) y `pruebas/e2e.py`.
- Botón **Ajustes** en el encabezado (vista completa y Modo piso); panel lateral `#setp` fuera de `#app` (abrirlo no redibuja ni borra lo capturado), foco atrapado, Esc / ✕ / tocar fuera cierran y el foco regresa al botón.
- **Tema:** `PREF.theme` → `data-theme` en `<html>`; sin elección sigue al equipo; script temprano en `<head>` evita el parpadeo; `color-scheme` por tema.
- **Texto:** `html{font-size:var(--app-font-size)}` (12–20 px, inicial 15); los ~105 `font-size` en px pasaron a `rem`; se quitó el `zoom` y los botones A A A (se migra `propesa-z`); campos de captura ≥16 px; íconos y logo no cambian. Se corrigieron desbordes a 20 px (avisos largos, tarjetas de embarque, selector de consignatario).
- **Ajustes (cambio):** la pantalla de atrás ya no se oscurece al abrir Ajustes (panel translúcido con desenfoque; en celular, hoja desde abajo de máx. 66% de alto). El tamaño del texto vuelve a 3 tamaños con deslizador: Normal 15 · Grande 17 · Muy grande 20 px (`FS_STEPS`, `fsSnap`); los valores guardados se ajustan al más cercano. 100 verificaciones en `pruebas/ajustes_t.py`.
- **Menú de perfil (12/oct):** la barra superior ya solo tiene el buscador y un círculo con la inicial (`avatarBtn`). Al tocarlo abre `#pmenu` (fuera de `#app`): nombre, correo y rol; *Usuarios y permisos* (solo admin → Administración), *Ajustes* y *Cerrar sesión*. Igual en Modo piso. Accesible (role=menu, flechas, Esc, foco de regreso). Pruebas: `pruebas/menu_t.py`.
- **Corrección:** el botón **Ajustes** regresa a la barra (junto al círculo) por accesibilidad; el menú del círculo queda con **Administración** (solo admin: usuarios, permisos, correos y respaldo) y **Cerrar sesión**.

## /ship · versión 1.0.0 (12/oct/2026)
Se preparó la app como versión final con el método /ship del plugin agent-skills (lista previa + revisiones de código, seguridad y pruebas).
- **Sin rastros de demo:** sin usuarios precargados (`seed()` con `U:[]`); primer uso = **Configuración inicial** (`setupView`/`setupSave`, `data-a="s0"`) que crea el Administrador o restaura un respaldo. Se quitaron textos «demo/simulado», la tabla técnica de PostgreSQL y los datos inventados de temperatura. «Restablecer demo» → «Borrar los datos de este equipo» (escribir BORRAR). Versión visible en el menú del perfil (`Versión 1.0.0`).
- **Temperatura real:** `ST.T`, formulario (`saveTemp`, 20–110 °F, al menos un valor), últimos 7 días con `histList('temp')`, admin elimina (`data-tqdel`), `cleanST` valida `T`.
- **Seguridad:** `vercel.json` con CSP (`default-src 'self'`, `object-src 'none'`, `connect-src 'self'`, `base-uri 'none'`…), HSTS, Permissions-Policy (cámara solo propia), COOP, `no-cache` para `index.html`. Verificado en `pruebas/csp_t.py` (sin violaciones; un script externo de prueba sí se bloquea). Lista de contraseñas fáciles prohibidas ampliada.
- **Accesibilidad:** Lighthouse 100 en 14 pantallas (`pruebas/accesibilidad.mjs`): botón rojo #b8321f, `--cor` #c23a26, `<th aria-label="Acciones">`, `aria-label` en conteo final, títulos h2 donde saltaban de h1 a h3.
- **Pruebas:** todo en `pruebas/` con usuarios de prueba propios (`FIX`); `sh pruebas/correr_todo.sh` = 12 grupos, 322 verificaciones, TODO BIEN. Rendimiento con un año de datos sin cambios (Panel 36 ms, guardar caja 138 ms con CPU 4×).
- **Documentos:** README de producción (primer uso, pruebas, actualizar y volver atrás, límites), `CHANGELOG.md`, manual de usuario actualizado (sin usuarios demo; Configuración inicial; Ajustes y menú del perfil; Temperatura; Informes de cierre; sección «Límites de la versión 1.0»).
- **Volver atrás:** Vercel → Deployments → versión anterior → Promote to Production. Respaldo `.json` antes de cada actualización.

## Documentación del repositorio (12/oct/2026)
Se agregaron `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json` (plugin agent-skills) y la carpeta `docs/`: `PRODUCTO`, `UX`, `BRAND`, `ARQUITECTURA`, `DATOS`, `DECISIONES`, `ROADMAP`, `PRUEBAS`, `SEGURIDAD`, `SUPABASE`, `FLUJO_DE_TRABAJO`, este `HISTORIAL` y `referencias/` (formatos en papel y documentos del usuario). Objetivo: que cualquier conversación nueva tenga el mismo contexto que la original.

## Ronda del 13/oct/2026 · v1.1.0: Entrada en Modo piso como hoja de varias entradas
Pedido del usuario: dejar de abrir una ventana por cada Entrada en Modo piso; capturar varias a la vez, con mucha información visible y pocos toques.
- `pisoEnt` reemplaza el asistente de 5 pasos (`PSTEPS`, `penCheck`, `data-pn`) por una tabla editable: `PEN={n,rows:[{u,st,er,open,d}],cf,cur,busy}`; filas con `penRow()`, celdas `data-pr="<u>:<campo>"`, acciones `data-pa` (`add`, `save`, `jump`, `more:u`, `rm:u`, `rmy:u`, `rmn:u`, `clear`).
- Columnas visibles: #/estado, Proveedor (`datalist` con proveedores recientes), Tanque (`select`), Lote (mayúsculas en vivo), 4 tallas con su color, Kg total en vivo, Más/Quitar. En «Más»: temperaturas, kg por caja en tanque, desperdicio, fecha y hora.
- `penSave` valida cada fila con `penVal` (mismas reglas que `saveLot`; además lote repetido dentro de la hoja y kg negativos) y guarda las válidas en un solo `save()`; las inválidas quedan con `aria-invalid` + mensaje (`.perr`, `aria-describedby`). Solo se guardan filas no guardadas → un doble toque no duplica. `penJump` enfoca el primer error (abre «Más» si hace falta).
- `penLive` actualiza estado, total, conteo y aviso sin redibujar (no se pierde el foco). `focusin` resalta la fila actual. Enter avanza; Ctrl/⌘+Enter guarda.
- Diseño: tabla con `thead` fijo (`position:sticky` dentro de `main`); `@container pent (max-width:64rem)` → tarjetas (el umbral en `rem` sigue al tamaño de texto); `34rem` → tarjeta de 2 columnas. Filas guardadas se ven como texto bloqueado.
- `switchMode` ya no borra `PEN` (se conservan los borradores); el mosaico «Registrar entrada» muestra «N sin guardar». No cambió `ST` (sin migración).
- Pruebas: `pruebas/entradas_t.py` (58), `piso_t.py` y `correcciones_t.py` ajustados, `accesibilidad.mjs` incluye `piso_entradas` (100). Versión 1.1.0.

## Ronda del 13/oct/2026 · v1.1.1: tabla de Entrada legible
Pedido del usuario: la tabla de Entrada (vista completa) se veía «apachurrada»; los encabezados de talla se partían en 4-5 renglones (129 px de alto).
- `szHead(i)` (junto a `szDot`) parte `SL[i]` en rango principal (`.szh1`, negritas) y secundario (`.szh2`, gris), con el punto de color a la izquierda ocupando los dos renglones (`.szh-in` en rejilla). Un `<span class="vh"> / </span>` mantiene la lectura «0-650 / 491-610» para lector de pantalla. `SL` no cambió (lo usan el formulario y el PDF).
- La tabla lleva `class="lf ent"`: `min-width:max-content` (las columnas no se comprimen; `.tbl` ya desliza de lado), encabezados `nowrap` y alineados abajo, saltos fijos con `<br>` en «Kg por caja / en tanque», «T°F / tanque», «T°F / producto», «Kg / desperdicio»; columnas numéricas (`.num`) a la derecha; tallas (`th.szh`, `td.szv`) centradas con `min-width:6rem`; anchos mínimos en Proveedor y Etapa. El alto del encabezado bajó de 129 a 66 px.
- Sin cambios en `ST`, reglas, textos ni PDF. Prueba nueva `pruebas/tabla_entrada_t.py` (45). Versión 1.1.1.

## Ronda del 13/oct/2026 · v1.1.2: camión en el PDF del Plan de embarques
Pedido del usuario: al descargar el Plan de embarques, el mismo PDF debe traer el gráfico del camión.
- `truckPlan()` calcula el acomodo (embarques abiertos, capacidades 15/20/20/25/25, celdas, exceso); `truck()` (pantalla) y `pdfEmbarques()` lo usan, así que siempre coinciden.
- `PdfRep` suma figuras vectoriales: `RRECT` (rectángulo redondeado), `CIRC`, `POLY` (con curva); `rgb()` acepta colores de 3 dígitos. Métodos nuevos `R.truck(plan)` (el mismo dibujo de 800×235 escalado al ancho de la hoja, sin imagen) y `R.legend([[color,texto]])`.
- `pdfEmbarques()`: después de los totales va «Plan de carga (embarques abiertos) · N hieleras · kg», el camión, la leyenda y, si aplica, el aviso de exceso o «el camión está vacío»; luego la tabla de embarques como antes.
- Revisado en tres casos (normal, excedido, vacío). Sin cambios en `ST`. Versión 1.1.2.

## Ronda del 13/oct/2026 · v1.2.0: estado de cada caja y barra de avance en Empaque
Pedido del usuario (documento «EMPAQUE: COMPLETED BOX STATES + DYNAMIC PROGRESS»): ver de un vistazo qué cajas ya están, reabrirlas para corregir y que el botón de abajo crezca con el avance real.
- `pkGrid(d,o,l,key,bs,all,room,next,open)` ahora pinta **todas** las cajas de la línea en una sola tabla: primero las guardadas (`tr.pkdn.is-done`, número de packing list), luego las que faltan (`tr.pkrow`, igual que antes). La tabla aparte «Cajas de …» solo queda para quien no puede empacar (consulta o embarque cerrado).
- Estados (`PKS`): Pendiente / En captura (`pkRowSt`: piezas escritas o color tocado) / ✔ Completada (existe en `ST.B`) / Editando / ⚠ Incompleta (`pkEdOk`). Se actualizan en vivo (`pkLive`, `pkEdLive`) sin redibujar. «Completada» se deriva de los datos guardados: sin campos nuevos, sin migración.
- Corrección: `data-pk="ed:<seq>"` (fila o botón «Editar») abre la fila con `PKD.ed`/`PKD.ew`; acciones en un renglón debajo (`tr.pkear`: «Actualizar caja N», «Cancelar», «Quitar caja» con confirmación). `pkUpd()` valida (piezas ≥ 1, categoría, lote, embarque abierto) y cambia la misma caja; si cambia el lote, la mueve de `ST.B[a]` a `ST.B[b]` con el mismo `seq`. «Guardar» también guarda una corrección abierta. Enter = Actualizar, Esc = Cancelar.
- Barra (`.pkb` fija abajo): resumen `#pksum` + `.pktr` (contenedor estable) con el botón `.pkgo` de ancho `calc(min(100%,15rem) + (100% − min(100%,15rem)) × --p)`, donde `--p` = guardadas ÷ pedidas. `PKP` recuerda el último avance; `pkAnim()` (al final de `render0`) pasa de ese valor al nuevo con `transition:width` (sin animación si el equipo pide movimiento reducido). Al 100 % el botón se vuelve la franja verde «✔ N de N cajas completadas».
- Para no ensanchar la tabla en tablet vertical, el estado va bajo el número de caja cuando hay espacio y bajo las piezas cuando no (`.pktw` con `container-type:inline-size`, `@container (max-width:720px)`); en celular las etiquetas de las tarjetas usan clases (`td.pkno/.pkpz/.pkcat/.pklot`) en lugar de `nth-child`. Medido: mismo ancho que la v1.1.2 en 641/820/1024/1440 px, normal y 20 px.
- Modo piso: «Guardada» → «✔ Completada» (`.pdc`) con borde verde; «Editando» (`.pde`) al enfocar una tarjeta guardada; tarjeta empezada `.pbx.ip` (cian, `peLive`); encabezado «Completadas» + «N pendientes · N % completado».
- De paso: `.chain .chip.pk` puede partirse en dos renglones (los lotes se salían a 390 px con texto de 20 px).
- Prueba nueva `pruebas/estados_caja_t.py` (119). Rendimiento con un año de datos: `empacar` 76 ms con CPU 4×. Versión 1.2.0.

## Ronda del 13/oct/2026 · v1.2.1: Empaque con estilo sobrio (referencia iOS)
Pedido del usuario (documento «REFINED iOS-INSPIRED UI FOR EMPAQUE»): menos pastillas y colores, controles compactos, barra de avance delgada con botón de tamaño fijo.
- Todo el estilo nuevo vive bajo `.pkx` (la tarjeta de cajas); tokens locales `--pkac` (acento: #087DBA claro / #16A6D1 oscuro), `--pkat` (texto de acento), `--pksel`, `--pkok`, `--pkin` (ancho del campo de piezas, 7.5rem), `--pkln`. Modo piso y otras pantallas no cambian.
- `PKS` → `<span class="pkst s-pend|s-prog|s-done|s-edit|s-bad">` (indicador con `::before`, ✔/⚠ con `iconize`). `pkSeg(no,sel,act)` arma el segmentado (rejilla de 3 columnas iguales, `min-width:16.5rem`). Lotes: `.pklots` > `.pklb[aria-pressed]` (mismo `data-pk="lot:…"`). Caja completada: `button.pkvb.pked` («Editar» + número) en lugar de número + botón; categoría `.pkcv`, lote `.pklv`.
- Barra: `.pkb` = `.pkprog` (`#pksum` + `.pkbar[role=progressbar] > i` con `width:calc(var(--p)*100%)`) + `.pkgo` de ancho fijo (`min-width:12rem`) o `.pkall` al 100 %. `pkAnim()` además guarda `--pkbh` (alto de la barra) para `body:has(#pkb) #toast` y `main:has(#pkb){scroll-padding-bottom}`.
- Diseño adaptable con container queries sobre `.pktw` en rem (escala con el tamaño de letra): ≤ 47.9375rem → filas de dos renglones en rejilla (número · piezas · categoría / lote, `thead` oculto, el estado bajo las piezas, placeholder «Piezas» visible); ≤ 31.9375rem → una columna. Se quitaron las reglas `.pkt` del `@media(max-width:640px)` (las tarjetas con borde por fila). Sin soporte de container queries, la tabla se desliza de lado.
- Medido sin desbordes en 390/641/820/1024/1180/1440 px, normal y 20 px. Prueba `estados_caja_t.py` → 137. Versión 1.2.1.

## Ronda del 13/oct/2026 · v1.2.2: «Caja N» vs «N piezas» (lista estilo iOS)
Comentario del usuario: en celular no se distinguía el número de caja del conteo de langostas. Compartió una captura de iOS (Atajos → Diccionario: llave a la izquierda, valor a la derecha; barra flotante redondeada).
- `td.pkno` → `<span class="pkcj">Caja N</span>` + estado. Piezas: `<label class="pkf"><input class="pkc|pke"><span class="pku">piezas</span></label>` (el recuadro es la etiqueta; el input interno va sin borde: su regla necesita más especificidad que `input:not([type=checkbox])…` → `.pkx .pkt .pkf input:is(.pkc,.pke):not(.vh):not([type=range]):not([type=file])`). Completada: `button.pkvb.pked` = `<b class="pkv">N</b><span class="pku">piezas</span><span class="pkch">›</span>`. Se quitaron `.pks-a/.pks-b` (el estado siempre va bajo «Caja N») y el placeholder.
- `@container` ≤ 47.9375rem: rejilla `1fr auto` (título | valor), categoría y lote a lo ancho; completadas `1fr auto auto` (título | categoría | valor) con el lote abajo; `tbody` con borde y esquinas de 12 px. ≤ 23.9375rem: completadas en dos columnas (categoría bajo el título).
- `.pkb` flotante: `bottom:12px`, `border-radius:22px`, `--pkfl` / `--pkfs` (fondo y sombra por tema). Toast arriba en Empaque: `pkAnim()` guarda `--pkmt` (borde superior de `main`) y `body:has(#pkb) #toast{top:…}`.
- Prueba `estados_caja_t.py` → 143. Versión 1.2.2.

## Ronda del 13/oct/2026 · v1.2.3: nombre de la sección en la barra del celular
Pedido del usuario (captura del celular): entre ☰ y el engrane, mostrar en qué pestaña está. Primero se puso «Paso N de 5» debajo del nombre; el usuario pidió quitarlo: basta con el nombre.
- `hdTitle(steps,s)` (antes de `PG`) arma `<div class="hdt"><span class="hdti">ícono</span><span class="hdtt"><b>Nombre</b></span></div>` con el ícono y el nombre de `steps` del menú, o `inicio/temperatura/admin/buscar`. Va en `header.hd` después de `.mb`.
- `.hdt` está oculto y solo se muestra en `@media(max-width:700px)` (cuando aparece ☰), con `flex:1 1 0` y `text-overflow:ellipsis` para no partir la barra con letra de 20 px. Cuadro del ícono navy (claro) / azul de marca (oscuro).
- Modo piso no cambia (su encabezado y sus títulos grandes ya dicen dónde estás). Prueba nueva `titulo_t.py` (145). Versión 1.2.3.

## Ronda del 13/oct/2026 · v1.2.4: ícono de langosta
Pedido del usuario: mantener el logo en la app, pero que el favicon y los íconos sean una langosta («porque es de langostas»).
- Langosta original dibujada en SVG (vista de arriba: tenazas, antenas, caparazón, 3 patas por lado, 4 segmentos de cola, abanico), roja `#E8473D` sobre `#0B1D59`, con margen para que no toque las esquinas. Se revisó a 256/128/64/48/32/16 px: a 16 px se lee como la silueta roja con tenazas.
- Se reemplazaron `favicon.svg`, `icon-192.png`, `icon-512.png` y `apple-touch-icon.png` (mismos nombres y tamaños). `?v=2` en los `<link>` de `index.html` y en `manifest.webmanifest` para romper la caché de 1 día de `vercel.json`. Sin cambios de código ni de datos. Versión 1.2.4.

## Ronda del 13/oct/2026 · v1.2.5: recargar sin salir de la sesión
Pedido del usuario: «cuando le hago refresh a la página me saca; quiero que guarde justo donde estaba y los datos que estaba poniendo».
- `propesa-ses` (`{u,exp}`, 12 h desde `LAST_ACT`, el último toque o tecla) y `propesa-ui` (ruta `V`, borradores `form`/`uf`/`PKD`/`PE`/`PEN`/`OD`/`OA`/`HIST`/`ND` sin fotos, scroll y `f` = valores de los campos de `#app` por `#id` o atributos `data-*`).
- `uiSave` / `uiSoon` (tras cada `render()` y cada `input`/`change`/`click`/`keydown`, inmediato en `pagehide` y `visibilitychange`); `uiRestore()` al arrancar en lugar del `render()` final. `me=null` (cerrar sesión, borrar datos) borra ambas claves.
- La sesión vencida se mide desde la última actividad real (no desde el último guardado), para que una tablet olvidada abierta no se quede con la sesión para siempre.
- Prueba nueva `recarga_t.py`; `estados_caja_t.py` actualizado (antes esperaba que recargar pidiera entrar). Versión 1.2.5.
- Mockup del **teclado numérico fijo en Empaque** aprobado por el usuario (captura en iPad horizontal y vertical).

## Ronda del 13/oct/2026 · v1.3.0: teclado numérico fijo en Empaque
Pedido del cliente: «un teclado numérico siempre visible para capturar las langostas de cada caja». Respuestas del usuario: en **todas las vistas**; **no hay máximo** de piezas por caja (por ahora); no entendió la pregunta de «Poner a todas las vacías», así que **se dejó como estaba**.
- Mockup primero (captura de la app real con el teclado inyectado, iPad 1180×820 y 820×1180); el usuario lo aprobó.
- `kpPad(mode)` dibuja el teclado; `KPT.t` es la caja activa (`slot:N` en piso, `row:R` o `ed` en la vista completa). El teclado escribe en el campo de esa caja y dispara `input`, así que `PE.rows` / `PKD.rows` / `PKD.ew` y las reglas de guardado no cambiaron. `kpCatPress`: piso → `peTry(no,true)` (nuevo parámetro `quiet`: dibuja sin mover el foco) o corrección de la caja guardada; vista completa → marca la fila y avanza, o `pkUpd` si se está corrigiendo.
- Campos de piezas con `inputmode="none"` (el teclado de iPad no sale); `pointerdown` en los botones del teclado hace `preventDefault` para no quitar el foco; teclado físico sin foco → `keydown` global escribe en la caja activa.
- Disposición con container queries sobre `.kpwrap`: ≥ 56 rem → teclado a la derecha, `sticky top`, altura de botones `min(4.3rem, (100vh − 26rem)/5)` para que quepa en pantallas bajas; < 56 rem → abajo, `sticky bottom`; < 40 rem → versión compacta con las categorías a un lado de los números. Vista completa: `.kpdock` = teclado + barra «Guardar cajas».
- Modo piso: tarjetas compactas (`.kpp .pbx`: «Caja N», número grande sin recuadro, categoría o «Pendiente»/«Falta categoría», ✔ Completada); se quitaron los botones de categoría y «Quitar» de cada tarjeta (ahora en el teclado). Texto de ayuda nuevo (el del mockup aprobado).
- Errores encontrados y corregidos en el camino: (1) el teclado usaba `data-mode`, que es el atributo del interruptor de Modo piso → tocar una categoría cambiaba de modo; ahora `data-kpm`. (2) La clase `.kpl` ya existía (tarjetas KPI del Panel) → se renombró a `.kpcl`. (3) `scrollIntoView` con margen grande escondía la fila activa en celular → `kpReveal` calcula a mano dejando libre el espacio del teclado. (4) El «seleccionar al enfocar» de los campos numéricos (`select()` en un `setTimeout`) podía robar el foco y, en iPad, mostraría «Copiar/Pegar»: ahora no selecciona en campos `inputmode=none` con pantalla táctil (`selOk`) y solo si el campo sigue enfocado.
- Rendimiento (un año de datos, CPU 4×, misma máquina): guardar una caja en piso ~220 ms (antes ~175 ms; `save()` solo ya son ~135 ms). Se quitó una medición de altura que forzaba un cálculo de página extra y se elige la siguiente caja antes de guardar para dibujar una sola vez.
- Pruebas: `teclado_t.py` nueva (135); ajustadas `cajas_auto_t`, `estados_caja_t`, `recarga_t`, `rendimiento_t`. 18 grupos, 904 verificaciones, TODO BIEN. Versión 1.3.0.

## Ronda del 16/oct/2026 (noche) · v1.8.9: teclado de Android en Empaque
**Pedido del usuario** (captura de un Android con teclado Samsung, Empaque · RSK en vista completa con el teclado de la app abierto): «when I use the keypad on mobile it also opens the android keypad after completing a box».
- Causa: al tocar la categoría, `kpCatPress` → `kpGo`/`focus()` en la siguiente casilla (`.pkc`/`.ppc`); aunque tienen `inputmode="none"`, el teclado de Samsung se abría con el foco puesto por código. Arreglo: `KPRO()` = `(hover: none) and (pointer: coarse)`; en esos equipos `.pkc`/`.pke` (con el teclado de la app abierto) y `.ppc`/`.psc` (Modo piso, embarque abierto) llevan `readonly`. `kpType` cambia `el.value` directo, así que el teclado de la app sigue igual; el foco y el resaltado de la caja activa no cambian. En computadora (mouse) no se pone `readonly`.
- De paso: una prueba con teclado físico perdía el primer número porque escribía antes del `select()` que hace la app al enfocar (`setTimeout 0`); es solo de la prueba (una persona no escribe tan rápido) y ya pasaba en la 1.8.8.
- Pruebas: `teclado_movil_t.py` (13, contexto `is_mobile` + `has_touch`). 31 grupos, TODO BIEN.

## Ronda del 16/oct/2026 (tarde) · v1.8.8: editar una orden ya creada
**Pedido del usuario:** «also make sure you are able to edit an order after creating it». Antes solo se podían agregar líneas y quitar las que no tenían cajas.
- `orden()`: «Cambiar fecha» (`data-oa=ee` → `#oe_etd`, `se`) y «Editar» por línea (`el:<id>` → fila `.oled` a lo ancho con `#le_cli` y `#le_n`, `sl:<id>`). Estado en `OA.etd` / `OA.ed` (se conserva al recargar con `OA`). `se` llama `syncShipIdx` en los embarques de la orden (nombre con la fecha). `sl` limpia el cliente como al agregar (mayúsculas, A-Z0-9, 6), exige ≥ 1 y ≥ cajas ya empacadas, y llama `syncShip`. `el` se niega si el embarque del destino está cerrado. Todo detrás de `can('lot')`. Cambiar destino/consignatario no se hizo: se explica quitar y agregar la línea.
- Pruebas: `editar_orden_t.py` (31, en 1180 y 390 px; piso y consulta no pueden). 30 grupos, 1498 verificaciones, TODO BIEN.

## Ronda del 16/oct/2026 (tarde) · v1.8.7: peso estándar de la caja
**Pedido del usuario:** «no es claro para mí dónde edito cuánto pesa la caja, y todo eso». Se le explicó dónde estaba (tarjeta «Peso bruto: cantidad × peso unitario» al final de cada embarque, con casillas por componente; Órdenes con 16/19.6 fijos; «Kg por caja en tanque» en Entrada, que es otra cosa) y se preguntó: **«No pesan, usan el estándar»** y **«Solo el Administrador»** los cambia.
- `ST.W = {h, g, p, c}` (hielera, gel, producto, caja de cartón; kg). Sin `ST.W` vale `W0` (1.4/1.5/16/0.7). Se comparte como `W/pesos` (`WN.W`, `encodeST`, `decodeST` caso `W`) y va en el respaldo (`cleanST`). `KGN`/`KGB` pasaron de constantes a variables que `pesosSync()` calcula en cada `render()`. `syncShipIdx` arma `p.c` con `stdC(h)`.
- Administración: tarjeta `#pesos` (cuatro campos, total en vivo, `data-a=pw`, solo admin; valida 0–100 y producto > 0); al guardar recalcula los embarques abiertos con hieleras. Ruta `admin:pesos` baja hasta la tarjeta (moviendo solo `main`) y enfoca el primer campo.
- Embarque: «Peso del embarque» sin casillas (se quitó el manejador `data-k/data-j`); cerrado → «Pesos con los que se cerró»; abierto con pesos distintos al estándar → aviso y `pwfix:<i>` (admin). El aviso rojo de peso (`shipIssues`) ahora dice «peso estándar» y el salto enfoca ese botón.
- Pruebas: `pesos_t.py` (39, en 1180 y 390 px, piso no puede); `avisos_t` (el aviso de peso lleva a «Usar el peso estándar»); `sincronizacion_t` (el peso llega a otro equipo). 29 grupos, 1467 verificaciones, TODO BIEN.

## Ronda del 16/oct/2026 (tarde) · v1.8.6: vista previa al compartir el link
**Pedido del usuario** (con captura de la tarjeta de `propesa.vercel.app` sin imagen): «cuando comparto el link de mi deployment no me sale ninguna imagen ni nada. Quiero que por lo menos salga el logo de la empresa».
- La página publicada no tenía ninguna etiqueta `og:` (revisado con WebFetch). Se agregaron `og:*` y `twitter:*` con dirección completa, y `og-image.png` generada con Chromium a partir de `LOGOD` (1200×630, PNG sin pérdida de 175 KB; una versión de 128 colores pesaba 110 KB pero se veía un anillo en el degradado). Descripción sin «mortalidad final».
- En la captura del usuario, el favicon del link todavía era la langosta roja: el sitio publicado aún no tenía la 1.8.1 o el servicio de vista previa la tenía guardada.
- **Después, mismo día:** «make it that if I download the app it has a good loading icon or loading screen. I want the company logo to appear if it's loading… on Android… the icon all pixelated». Chrome en Android pide para la pantalla de inicio un ícono de ~192 dp (≈ 768 px en pantallas xxxhdpi) y el más grande era de 512: lo estiraba. Se agregó `icon-1024.png` (`any` y `maskable`), `?v=4` en todos los íconos y el manifiesto (`theme_color` también `#0B1D59`). Pantalla de carga propia `#boot` dentro del HTML (logo `LOGOD` estático en blanco, tres puntos animados, sin animación con movimiento reducido, `pointer-events:none`); `boot()` ahora envuelve a `boot0()` y siempre llama `bootDone()`, que la desvanece (mínimo 500 ms desde que abre la app instalada; inmediato en el navegador) y la borra.
- Pruebas: `vista_previa_t.py` (28: etiquetas, imagen, íconos del manifiesto con sus medidas reales, pantalla de carga que se quita sola). 28 grupos, TODO BIEN.

## Ronda del 16/oct/2026 (tarde) · v1.8.5: sin «Borrar todos los datos»
**Pedido del usuario** (minutos después de la 1.8.4): «ahora quita completamente el botón de Borrar todos los datos. No quiero que alguien lo pueda hacer; solo lo haría yo manualmente». También: «double check and update my records so my favicon is that new one white lobster one».
- Se quitaron `advCard`, `rstAll`, `rstReady`, `ADV`, `BK_T`, `RST_MSG`, `data-a=rst` y su CSS (`details.adv`, `.advb`, `.advs`, `.okc`). «Datos viejos de este equipo» (solo la copia local anterior a la 1.4.0) se queda. Cómo borrar todo a mano: `SUPABASE.md` §9 (`update app_records set v = null`, para que el borrado llegue a todos los equipos).
- Pruebas: `inicio_t`, `fotos_t`, `sincronizacion_t` revisan que ya no existe.
- Favicon revisado: `favicon.svg`, `icon-192/512.png` y `apple-touch-icon.png` del repositorio son la langosta blanca (los PNG idénticos byte por byte a los que se generaron en la 1.8.1), enlaces y manifiesto en `?v=3`. Registrado en `docs/BRAND.md` y en el documento del proyecto `claude/ESTADO_ACTUAL.md`.

## Ronda del 16/oct/2026 (tarde) · v1.8.4: Temperatura conectada, Mortalidad final aparte y borrado escondido
**Pedidos del usuario (tres mensajes seguidos):** «quiero que el sistema de temperatura esté conectado también con los inputs de las entradas… que se actualice solo y también tener ese input para agregar para tracking»; «la mortalidad final es algo que se calcula al final y es aparte… no quiero que sea parte del proceso a fuerzas»; «no me gustó el botón de Borrar todos los datos… que esté solo como en configuración avanzada, algo más difícil de hacer»; y «revisa que mi favicon sea la langosta blanca y actualiza mis registros».
- **Temperatura:** `tempAll()` combina `ST.T` con las temperaturas de `ST.R` (sin cambiar el modelo de datos ni copiar nada). Temperatura: columna «Origen» (Entrada · lote / Lectura · quién), filtro por tanque (`TFIL`, `data-tqf`), ruta `temperatura:<tanque>` que preselecciona el tanque; las de entrada no se eliminan ahí. Tablero de tanques: `ult` usa `tempAll`; «· Registrar ›». Lote: tarjeta con las lecturas de su tanque desde `rdate` (máx. 8) y «+ Registrar lectura».
- **Mortalidad final:** fuera de `steps` (menú con 4 pasos numerados) y de `STEP`; sección «Revisión» en el menú; `nxt()` ya no manda a `cierre`; Embarque sin botón siguiente; `guide()` «Paso N de 4» y acepta texto («Revisión aparte»); PDF «Revisión aparte · Mortalidad final». Modo piso conserva su mosaico «Conteo final» (es captura, no flujo). Actualizados `CLAUDE.md`, `AGENTS.md`, `PRODUCTO.md`, `README.md`, `DECISIONES.md`.
- **Borrar todos los datos:** `advCard()` dentro de `<details>` cerrado; `rstAll()` exige respaldo descargado en los últimos 15 min (`BK_T`, lo pone el botón de respaldo), BORRAR TODO y la contraseña (re-autentica con Supabase; en modo local no hay contraseña). Se quitaron los `prompt()`.
- `APPV` = una sola constante de versión (Administración decía 1.5.0).
- **Favicon:** verificado en el repo: `favicon.svg` es la langosta blanca (15 partes `#FFFFFF`, nada del rojo `#E8473D`), PNG 192/512/180 blancos, enlaces y manifiesto `?v=3`. No se encontró la dirección del sitio publicado para revisarlo en vivo. Se actualizó el estado en los documentos del proyecto de Claude.
- Pruebas: `temperatura_t.py` (47, en 1180 y 390 px). 27 grupos, 1401 verificaciones, TODO BIEN.

## Ronda del 16/oct/2026 · v1.8.3: eliminar una orden
**Pedido del usuario** (con captura del Panel, dos órdenes del 16/10/2026 sin líneas): «no sé cómo puedo eliminar un empaque que metí por accidente. They just stay there and I can't edit it or find where to remove it».
- No existía: solo `dl` (quitar línea sin cajas). Nuevo al final de `orden()`: tarjeta «Eliminar orden» para quien tiene `can('lot')`; con cajas empacadas solo explica; sin cajas, `dco` → confirmación en línea (`OA.cf='ord'`) → `dlo`. `dlo` vuelve a revisar `ordBoxes(o)`, vacía `o.lines` y llama `syncShip` por cada destino (borra embarques abiertos vacíos y recorre índices), quita `ST.M['emp:<orden>.<línea>']` (y sus fotos con `fotoDel`), saca la orden de `ST.OR`, `save()` y regresa a Órdenes. El registro `OR/<id>` se borra en la base por `syncStage`.
- Pruebas: `eliminar_orden_t.py` (33, en 1180 y 390 px; piso y consulta no ven el botón; con cajas no se puede ni forzando la acción). 26 grupos, TODO BIEN.

## Ronda del 15/oct/2026 (noche) · v1.8.2: datos de Entrada obligatorios y cambiar de modo sin perder nada
**Pedido del usuario:** «sí quiero que sean obligatorios para que no se le olviden al usuario anotarlos» (los de «Más»: temperaturas, kg por caja en tanque, desperdicio, fecha y hora) y «si estoy en modo piso registrando una entrada de langosta y apague el modo piso quiero mantenerme en la misma pestaña con los mismos datos sin perder nada».
- `lotErr` (una sola regla para `saveLot` y `penSave`) ahora pide también hora, temperatura del tanque (20–110 °F, el mismo rango de Temperatura), temperatura del producto (texto, puede ser rango), kg por caja en tanque (> 0) y desperdicio (≥ 0; 0 si no hubo). Solo al crear; la edición de lotes viejos no pasa por `lotErr`. `LOT_F` en el orden del formulario para que el foco vaya al primer dato que falta.
- Modo piso: `penMiss`/`penMc`: si la fila tiene algo y falta alguno de `PND`, el botón dice «Más · Faltan N» en rojo (`.pmx`, `.pmf`, `--cor`) y se actualiza al escribir (`penLive`). Al guardar ya se abría la fila con errores (`PND`).
- Cambio de modo: `modeDest()` decide a dónde ir: `pent` se queda en `pent` (la hoja también se dibuja en la vista completa, con «‹ Volver a Entrada» y `STEP.pent=1`); `pemp[:x]` ↔ `empacar:x`/`empaque`; Entrada con el formulario nuevo a medio llenar → `penFromForm()` pasa lo escrito a una fila. La hoja (`PEN`) ya vivía en memoria; antes solo se perdía de vista porque el cambio iba al inicio. Entrada (vista completa) avisa «Tienes N entradas sin guardar · Terminar de capturarlas ›». `switchMode` quita `sbo` (el menú ☰ del celular se quedaba abierto).
- Pruebas: `cambio_modo_t.py` (29, en 1180 y 390 px); `entradas_t.py` llena los datos de «Más» con `extra()` y prueba «Faltan», rango de temperatura y la vista completa; `e2e`, `correcciones_t`, `sincronizacion_t`, `piso_t` llenan los datos nuevos. 25 grupos, TODO BIEN.

## Ronda del 15/oct/2026 (noche) · v1.8.1: botón de atrás, ícono de langosta blanca y la contraseña de Samuel
**Pedido del usuario:** «si le doy al back button de android que me regrese a la window que estaba, no que me saque de la app»; «el logo de la app y también mi favicon sea como el icono de entrada, una langosta blanca»; y que explicara el botón «Más» de Entrada en Modo piso, sin cambiarlo.
- **Contraseña (antes, misma noche):** el usuario no podía entrar. Las dos cuentas de Administrador (Samuel Meza y Carlos Sandez, creadas el 12/oct desde el panel) **no tenían contraseña** y nunca habían entrado (registros de Supabase: «Invalid login credentials»). Con permiso del usuario se le puso a 39056mezas@gmail.com una contraseña temporal (bcrypt con `extensions.crypt`, verificada) y se le pidió cambiarla en Administración. La de Carlos sigue sin contraseña.
- **Atrás:** `navSync()` al final de `render()` guarda en el historial del navegador `[V.v, V.id, PISO]` (`pushState`; `replaceState` al entrar y al volver con atrás); `popstate` primero cierra lo que esté encima (`navOverlay`: foto, menú lateral `sbo`, Ajustes, menú del perfil) y vuelve a poner la entrada actual; si no, restaura pantalla y modo, limpia como `go()` y pasa por `fixRoute()`. La dirección de la página no cambia. Redibujar la misma pantalla no agrega pasos.
- **Ícono:** `favicon.svg` = langosta de `IC.recepcion` en blanco sobre `#0B1D59` con esquinas redondas; PNG 192/512/180 cuadrados completos con la langosta al 80 % (zona segura), sacados con Chromium; `icon-512` también `maskable`; `?v=3` en enlaces y manifiesto; `background_color` `#0B1D59`.
- **«Más» en Entrada (Modo piso), explicado sin cambios:** cada fila muestra lo que siempre se captura (proveedor, tanque, lote, kg por talla) y «Más» abre lo que no siempre se tiene a la mano (temperaturas, kg por caja en tanque, desperdicio, fecha y hora; fecha y hora ya vienen llenas). Si falta algo obligatorio ahí, la fila se abre sola. El número junto a «Más» dice cuántos de esos datos ya se llenaron.
- Pruebas: `atras_t.py` (41, en 1180 y 390 px). 24 grupos, TODO BIEN.

## Ronda del 15/oct/2026 (noche) · v1.8.0: fotos en Supabase Storage y base despierta en la veda
**Pedido del usuario:** «fix 1. Las fotos todavía viajan dentro de los datos… and fix 2. Antes del 15 de febrero hay que seguir la lista de la veda… I just want it to automatically do itself or just have it the way it is until I connect my own database server».
- **Fotos:** espacio de archivos privado `fotos` en `propesa_bc` (2 MB, solo imágenes; ver con perfil, subir y borrar Administrador y Piso, solo bajo `notas/`; sin regla de cambiar). La nota guarda `sb:notas/<id>/<n>.jpg`. Cola `FQ` en IndexedDB (`fotos-cola`), se sube en `syncNow()` antes de `flush()`; `outN()` la cuenta. Bajada con sesión y copia en IndexedDB (`F/<ruta>`). `fotoMigra` pasa fotos viejas dentro de notas (respaldo restaurado). Foto rechazada (4xx) se quita de su nota con aviso; 5xx o sin internet se reintenta y la nota se sube igual. `fotoDel` al eliminar nota y al borrar todo. Modo local sin cambios. `WN` y `cleanST` aceptan referencias.
- Reglas probadas en la base real dentro de una transacción que se deshizo (`raise exception` al final): el Administrador sube y ve; fuera de `notas/` se rechaza; una cuenta sin perfil y el anónimo no ven ni suben. La prueba con borrado se canceló en la confirmación de Supabase; la regla de borrar no se probó en la base real.
- **Veda:** `api/despierta.js` (Node, sin librerías) + `vercel.json` `crons` diario (`23 17 * * *`, el plan Hobby solo permite una vez al día, ±59 min). Consulta `rpc/has_admin` con la llave publicable (cuenta como uso para Supabase). `CRON_SECRET` opcional. README: la lista de 3 pasos se cambió por «se cuida solo» y cómo comprobarlo. El ambiente de trabajo no llega a supabase.co: la función se probó con el Supabase de mentira.
- Pruebas: `fotos_t.py` (34), `despierta_t.py` (8); el Supabase de mentira imita Storage (subir, bajar con sesión, borrar, duplicado 409, 2 MB, falla 500). 23 grupos, TODO BIEN.
- **Para que funcione hay que subir el zip a GitHub** (Vercel publica la app y la tarea diaria). El espacio de archivos ya está en Supabase.

## Ronda del 15/oct/2026 (tarde) · v1.7.1: verificación de la auditoría y tablas viejas fuera
**Pedido del usuario:** «revisa el zip y asegúrate de que todas las auditorías estén atendidas»; después, «aplicar `20261014d_quitar_tablas_viejas.sql` y la prueba manual con contraseña de 7 caracteres».
- Se revisó el código del zip contra los 20 puntos de las dos auditorías: todos presentes. Sin cambios al código. `correr_todo.sh` 21 grupos, 1197 verificaciones, TODO BIEN; `e2e.py` suelto sin dirección también pasa; `rendimiento_t.py` TODO BIEN; Lighthouse 100 en 15 pantallas. La función `usuarios` publicada (versión 3) es igual a la del repositorio.
- Lighthouse marca, sin bajar la nota, «label-content-name-mismatch» en los botones del mapa de tanques (Entrada) y en el botón de piezas de Empaque. No se tocó (cambia textos de pantalla).
- **Tablas viejas:** se verificó otra vez en `propesa_bc` (0 registros en las 9, ninguna vista ni otra pieza depende de ellas, `nuevo_perfil` vacía). El intento desde el asistente se canceló en la confirmación de Supabase (tercera vez); el usuario la aplicó él mismo. Verificado después: quedan `app_records`, `app_records_hist`, `profiles` (2), funciones `app_records_stamp`, `auth_user_id`, `has_admin`, `my_role`, `pull`, `push`, `solo_admin_cambia_rol`; disparadores `app_records_stamp` y `perfil_rol`. Los avisos de seguridad de Supabase ya no mencionan las tablas viejas.
- La cadena de archivos SQL del repo (schema → 20261014 → b → c → d) se probó en un Postgres 16 local y deja las mismas tablas y funciones, salvo `solo_admin_cambia_rol` / `perfil_rol`, que existían en la base (migraciones del 12/oct) pero no en ningún archivo del repo. Con permiso del usuario se copió de la base a `supabase/migrations/20261012b_solo_admin_cambia_rol.sql` (sin cambiar nada en Supabase). Probado en Postgres 16 local: con ese archivo la cadena deja lo mismo que `propesa_bc`; piso no puede cambiar su rol (rechazado), cambiar su nombre sí pasa, el Administrador y la llave de servicio sí cambian roles.
- Documentos: encabezados de `20261014d` y `schema.sql`, `SUPABASE.md` (con el orden para reconstruir la base), `ROADMAP.md`, `CHANGELOG.md`.
- **Pendiente:** la prueba manual con una contraseña de 7 caracteres en Administración (el usuario la hace el 16/oct).

## Ronda del 15/oct/2026 (tarde) · v1.7.1: código del lote completo en Modo piso
**Pedido del usuario:** «1. sí, mantenlo como tú dices: “Escribe el lote.” 2. El lote sale dependiendo su entrada» (respuesta a lo que se vio de paso en la 1.7.0).
- `.pk2` con `container-type:inline-size` y `.pk2 .cli{font-size:clamp(1.3rem,10cqi,2.6667rem)!important;overflow-wrap:anywhere}`: la letra (antes 40 px fijos, tarjetas de ~240 px) se ajusta al ancho; los códigos largos pasan a otro renglón. En tablet queda en ~21 px con texto normal. Opción no hecha (cambia el acomodo): que las tarjetas se estiren a todo el ancho cuando hay pocos lotes, para que el código salga más grande.
- Después el usuario dijo «sí, publícala»: función `usuarios` publicada en `propesa_bc` como versión 3 (antes versión 2), `verify_jwt:false` como estaba. Se comparó lo publicado con el repositorio: idéntico. No se pudo llamar a la función desde el ambiente de trabajo (sin salida a supabase.co); se pidió al usuario una prueba con una contraseña de 7 caracteres.

## Ronda del 15/oct/2026 (tarde) · v1.7.0: auditoría Parte 2, puntos 13 al 20
**Pedido del usuario:** «continúa hasta completar la auditoría» (después de la 1.6.0). Pausó a media ronda («pause») y luego «continue».
- 13 lista de la veda en el README (Supabase dice que una base pausada se reactiva hasta 1 año después, pero otra página suya dice 90 días: se pide no pasar de 90). También se corrigieron secciones viejas del README (conteo de pruebas, «Límites» de la v1.0).
- 15 y 20 en `supabase/functions/usuarios/index.ts` (`profiles()` cuenta todas las cuentas; `checkPw` 8). El Supabase de mentira hace lo mismo (`/__sin_admins`). Lo publicado en `propesa_bc` (versión 2) es igual al repo anterior; publicarlo queda a decisión del usuario.
- 16 `?modo=local` por omisión en 21 pruebas y en `accesibilidad.mjs` (un primer intento dejó el comentario tragándose el resto de la línea en 5 archivos; se corrigió). Lighthouse ahora mide 15 pantallas reales: acceso y configuración daban 98 (sin región principal) → `role="main"` → 100 en todas.
- 17 sin `opacity:.62` en `.pbx.sv`; token `--plk` (navy en claro, cian en oscuro) para `.plot span`. Contraste medido con script propio.
- 18 script que lista clases del CSS que no aparecen en el resto del archivo, excluye las que se arman con variables (`kc${q}`, `pc${q}`, `sz${i}`); dio las mismas 31 de la auditoría. Comparación de 252 capturas: con animaciones encendidas había diferencias en zonas animadas (también entre dos corridas del mismo código); con animaciones apagadas, 0 diferencias.
- 19 `.chipb` 44 px y `.alk` inline-block de 44 px (se probó alinear la viñeta arriba y se regresó: se veía mejor como antes).
- Visto de paso, sin tocar: en Modo piso, «¿De qué lote sacas las langostas?», el código del lote se corta dentro de su tarjeta en 1180 px.

## Ronda del 15/oct/2026 · v1.6.0: auditoría, puntos 3 al 12
**Pedido del usuario:** «make sure every fix is completed» de `AUDITORIA_PONYTAIL_v1.5.0.md` (después de la 1.5.1 con el 1 y el 2).
- La sesión se reanudó a media ronda: el #3 ya estaba en el código (ids fijos con `pIx`, `ensureIds()` al arrancar) con una prueba que fallaba por suponer la posición exacta del embarque; se cambió a «el embarque nuevo queda antes» y se quitó una línea de depuración.
- #4 `byCat`/`catTxt` (recorren `RC`) en Trazabilidad, `bsum`, Embarque, PDF de Empaque (6 recuadros y columna Amarillo), PDF de Embarque e informe de cierre. #5 `pu` en `ST.O` (`closeP`, `WN.O`, `cleanST`) y `pdfMake('embu')`. #6 aviso en `shipIssues` → `empacar:` (vista completa). #9 revisión de `bal` antes de anular y `mvNo`. #10 `lotErr` + `addLot` (`saveLot` y `penSave`); `penVal` agrega solo «Repetido en la fila».
- #7 IndexedDB: `idb/idbGet/idbPut`, `cacheST` en cadena (`CACHE_W`) con `{st,since}` en un registro, `SINCE` en memoria, `loadCache()` antes de `boot()` (la sesión necesita `ST.U` de la copia), paso de la copia vieja de `localStorage`, aviso `CACHE_ERR`. La cola `OUT` se queda en `localStorage`.
- #8 sin el camino `app_records?on_conflict` (también se quitó del Supabase de mentira, con `/__sin_push`); prueba nueva con `push` respondiendo 404. #11 fuera `hero`, `tl`, `col`/`PAL`, `shipCons`, `data-q`, `pison`/`pisoff`, ramas `k`/`sk` de `data-pe`, `m` en `buscar`, `BN`/`N`/`PK`/`ORc` y `seedM`/`seedOR`/`cleanOrders`/`migratePK`.
- #12: se probó guardar el texto de cada caja en caché (en vez de por lote) y no mejoró en este equipo (el tiempo se va en rearmar los 40 mil registros, no en convertirlos a texto); se dejó como estaba. `rendimiento_t.py` mide stage y apply con límites 200 / 320 ms (CPU 4×); con el caché por lote apagado da 302 / 355 y falla, así que el límite sí detecta.
- Se revisó en 390, 820 y 1440 px, texto Normal y Muy grande, claro y oscuro (Embarque, Administración, lote): sin desbordes. PDF del packing list revisado como imagen.
- Pendiente (de la Parte 2 de la auditoría, no pedida en esta ronda): 13 (veda y pausa de Supabase), 14 (Safari), 15 (`setup` en `usuarios`), 16 (`?modo=local` en las pruebas sueltas), 17 (contraste de cajas guardadas), 18 (CSS sin uso), 19 (avisos de 44 px), 20 (contraseñas de 8).

## Ronda del 15/oct/2026 · v1.5.1: auditoría #2, puntos 1 y 2
**Pedido del usuario:** «read my zip and fix 1 and 2» de `AUDITORIA_PONYTAIL_v1.5.0.md`.
- **1. Registro malo descompone pantallas.** Reproducido con la base de prueba: consignatario 99 (Empaque, orden, «Empacar cajas» de piso), fecha como número o vacía (`fd`/`fs` → Panel, Órdenes, Empaque), 0 cajas (Modo piso: «Invalid array length»). Además, después del error la tablet dejaba de sincronizar (`syncLoop` moría) y seguía rota aunque se borrara el registro. Arreglo: `WN` con las reglas de `cleanST` (`wd` fechas, `wt` texto que nunca es null, `wp` convierte números a texto, `LTYPES`, líneas con ciudad/consignatario válidos y ≥1 caja; `B`, `L`, `T` y `R` sin lote → `null` = se ignoran); `encodeST` salta los `null`; `syncLoop` con `try`. Se comprobó que lo válido no cambia: un año de datos (19,394 registros) normalizado por el `WN` viejo y el nuevo da exactamente lo mismo.
- **Consecuencia que se cuidó:** `OUTB` guarda la versión ya limpia; si `WN` arregla un registro viejo, la base lo tiene distinto y lo rechazaría para siempre. `flush()` ahora, si la base devuelve lo mismo que se esperaba (solo escrito distinto), vuelve a subir una vez con lo que hay de verdad en la base.
- **2. Segundo cambio perdido con internet lento.** Reproducido (tallas 1 → 2 con subida lenta: quedaba 1 y aviso falso). Arreglo en `flush()`: al terminar de subir, si el registro se volvió a cambiar y no hubo choque, `OUTB[k]` = lo que se acaba de subir; si hubo choque de verdad, se descarta también el cambio de en medio (gana la base, un solo aviso).
- **Pruebas:** `sincronizacion_t.py` +13 (registros sin sentido en A y Modo piso, orden arreglada en la base sin aviso falso, internet lento); `supabase_falso.py` `/__lento`. Las nuevas fallan con la v1.5.0. 20 grupos, 1114 verificaciones, TODO BIEN.
- Pendiente de la auditoría: 3 (vivas en otro embarque), 4 (Amarillo en packing list e informe), 5 (PDF de otro embarque) y del 6 al 12.

## Ronda del 14/oct/2026 (tarde) · v1.5.0: decisiones del cliente y Empaque por lote
**Pedido del usuario:** preguntas una por una para entregar (alcance = lo que ya hay; Supabase gratis; cuentas del desarrollador; piloto con papel; 19.6 kg; categoría = talla con Amarillo; empacar no resta; desperdicio resta del total; aviso semanal de respaldo; logo lo pide al cliente). Luego: «no me gusta que en cada caja tienes que elegir de qué lote es» y, con una captura, «dime dónde estoy y el lote que empaco, y pestañas por lote como Chrome».
- Hecho: peso bruto 19.6 (`KGB`, `kb()`); `RC.A` Amarillo (listas `Object.keys(RC)`, estilos, conteos, PDF, columna en Órdenes); teclado 2×2 en pantallas anchas (`--kpk` recalculado para la fila extra); filas de Empaque sin lote (la columna «Lote» se quitó; el selector solo al corregir, en la barra de acciones); pestañas `.pklots` fijas en tablet/computadora; título `.hdt` en todos los tamaños con `#hdsub` (cliente · lote) en `empacar`.
- Nota: mientras se trabajaba, alguien más editó `index.html` y `teclado_t.py` (quitó el selector de lote de las filas nuevas y agregó pruebas); se conservó y se terminó encima.
- Después: «no me gusta que se esté repitiendo el input de categoría… que el keypad sea mi herramienta principal, que se pueda cerrar y abrir» y «quiero que las cajas se miren así» (tarjetas de Modo piso). Hecho con estilos sobre la misma tabla (`.pkx .pktw .pkt` → rejilla de tarjetas; `td.pkno{display:contents}` para ordenar título, número, categoría y estado) sin tocar captura ni guardado; `.pkx.kpo` esconde los botones no elegidos; `kpPad('full')` solo con el teclado abierto; «Cerrar»/«Abrir teclado» (`data-kpo`).
- Otra vez alguien editó en paralelo (`sincronizacion_t.py`, `estados_caja_t.py`: abren Empaque con el teclado cerrado). Se conservó.
- Teclado: X para cerrar (esquina del teclado) y botón flotante con ícono de teclado numérico para abrir (anclado a la barra de «Guardar cajas»). Ícono de Entrada = langosta blanca (silueta de `favicon.svg`); Embarque conserva el camión.
- **Tablero de tanques** en Entrada (`tanques()`, estilos `.tq*`): pedido «quiero ver todos mis tanques y en vivo lo que tienen». Primero se hizo con tarjetas; el usuario mandó un dibujo del piso y quedó como mapa (`.tqmap` con `grid-template-areas`: «leg t1 / leg t2 / t6 t3 / t5 t4») más el detalle del tanque tocado. Prueba nueva `tanques_t.py` (20 grupos) y 3 verificaciones «en vivo» en `sincronizacion_t.py`. Pregunta nueva en el roadmap: capacidad de cada tanque.
- **Auditoría `/ponytail-audit` (tarde):** (1) `WN` ahora valida números con `wnn`/`wn0` — temperaturas, kg, desperdicio, vivas y peso de componentes ya no aceptan texto; un valor con código llegaba al tablero de tanques (primero de Entrada) y se probó el robo de sesión antes y después. (2) `inicio()`: «En tanques» suma solo lotes abiertos (`!R_(l).closed`), igual que el mapa; antes contaba los cerrados (1852 vs 925.8 kg). (3) pestañas de lote en Empaque: con cajas escritas sin guardar, no cambian de lote y avisan. Pruebas: +T/ y números con código en `sincronizacion_t.py`, Panel en `tanques_t.py`, pestaña bloqueada en `estados_caja_t.py`.
- Pendiente: desperdicio que resta del total del lote; aviso semanal de respaldo; aplicar `20261014d_quitar_tablas_viejas.sql`; quitar estilos muertos de la tabla vieja de Empaque; manual y acta de entrega.

## Ronda del 14/oct/2026 · v1.4.1: no pisar cambios de otros equipos
**Pedido del usuario:** después de una revisión de código (plugin ponytail, `/ponytail-review`), «arregla 1 y 2», luego «sí, continúa en propesa_bc, y arregla también 3, 4 y 5».
- **1. Un equipo sin internet ya no deshace lo que guardó otro.** Se reprodujo: piso sin internet captura las vivas de un embarque, el Administrador lo cierra, piso vuelve y el embarque se reabría en todos los equipos. Ahora cada cambio viaja con cómo estaba el registro (`propesa-outb`) y la función nueva `public.push` (`supabase/migrations/20261014b_sin_pisar.sql`) solo lo guarda si la base sigue igual; si no, gana la base y el equipo ve «No se guardó tu cambio: otro equipo lo cambió antes…». Se probó la función en un Postgres 16 local (10 casos). Si la migración no está aplicada, la app sube como la v1.4.0.
- **2. Consulta ya no borra lo pendiente de otro usuario.** Se reprodujo: piso captura sin internet, cierra sesión, entra Consulta en la misma tablet y lo pendiente se borraba. Ahora Consulta no anota ni vacía la cola; lo pendiente se sube cuando vuelve a entrar un Administrador o Piso.
- **Pruebas:** `sincronizacion_t.py` +27 verificaciones (choque de embarque cerrado, aviso, Consulta en la tablet de piso, subida rechazada, carácter nulo, existencia negativa, código escondido, base sin `push`); `correcciones_t.py` e `inicio_t.py` ajustadas al acceso sin contraseñas. 19 grupos, 972 verificaciones. `supabase_falso.py` imita `rpc/push`. Versión 1.4.1.
- **3. Una subida rechazada ya no deja al equipo sin recibir lo de los demás** (`syncNow` baja aunque `flush` falle) y `wp()` quita el carácter nulo que Postgres no acepta en `jsonb`.
- **4. Historial:** tabla `app_records_hist`, la llena el disparador `app_records_stamp` con la versión anterior en cada cambio. Solo Administrador la lee.
- **5.** Función `usuarios` v2 sin el borrado repetido del perfil. Quitar el disparador `al_crear_usuario` (no hace nada) fue cancelado por la base; se dejó.
- **Auditoría (`/ponytail-audit`) y «arregla los 5»:**
  1. Código escondido desde la base (comprobado: una cuenta de piso escribía un embarque con `<img onerror>` y se llevaba la sesión del Administrador). `WN` ahora revisa como `cleanST`: `wi` quita `< > " ' ` & \`, `wcolor` solo colores, `wimg` solo imágenes base64. Prueba que recorre 11 pantallas; falla con la versión anterior.
  2. `shrink()` a 800 px y calidad 0.6 (~120 mil caracteres por foto, antes ~250 mil): caben ~40 fotos en vez de ~20. Pendiente de fondo: fotos a Storage.
  3. Aviso «Existencia negativa» para el Administrador en `topBanners`, con «Ver lote ›». Prueba con dos Administradores (uno sin internet).
  4. Tablas viejas: verificadas vacías; el borrado se canceló en Supabase (pide confirmación). Queda `20261014d_quitar_tablas_viejas.sql` por aplicar.
  5. Se quitó `sha256`, `pwHash`, `PWD0`, `migrateUsers`, el aviso de contraseña de prueba y las contraseñas de `cleanST`. El modo local entra con el correo.
- **Supabase:** migraciones `sin_pisar` e `historial` aplicadas en `propesa_bc` y probadas ahí dentro de una transacción deshecha (0 registros quedaron). Antes se probaron en un Postgres 16 local.

## Ronda del 14/oct/2026 · v1.4.0: base compartida
**Pedido del usuario:** «que toda la información sea centralizada; quiero ver lo mismo en todos los equipos y todas las cuentas. Mientras probábamos, cada equipo tenía sus propios valores». Eligió usar el proyecto de Supabase **`propesa_bc`** (ya tenía aplicado `schema.sql` y dos Administradores creados desde el panel).
- **Supabase:** tabla `app_records` (un registro por lote, movimiento, caja, orden, embarque, informe, lectura y nota; `rev` que solo crece), `pull()`, `has_admin()`, `email` en `profiles`, perfiles ya no se crean solos, «ver» solo con perfil, perfiles solo los cambia el Administrador. Función Edge `usuarios` (alta, cambios, baja y primer Administrador). Se confirmó el correo de los dos Administradores existentes para que puedan entrar. Primer intento de migración con `drop policy` se canceló; se aplicó por partes con `alter policy`.
- **App:** acceso con Supabase Auth; usuarios desde `profiles`; local primero con cola de cambios y descarga cada 4 s; los embarques viajan con id fijo y se traducen a índices; ids que no chocan (`uidN`, `uidS`); avisos «Descargando…» y «Sin conexión»; Administración con estado de la base, respaldo/borrado para todos y «Datos viejos de este equipo». Modo local solo para pruebas (`?modo=local` en localhost).
- **Pruebas:** `sincronizacion_t.py` + `supabase_falso.py` (49). Todo el resto en modo local. 19 grupos, TODO BIEN. El ambiente de trabajo no puede llegar a supabase.co, así que las reglas se probaron con SQL directo en la base (como admin, sin perfil) y la app con el Supabase de mentira.
- **Pendiente:** que el usuario entre con los dos Administradores (si no recuerdan la contraseña, se cambia); desactivar en el panel el registro libre y activar la protección de contraseñas filtradas; fotos a Storage; correo real con PDF.

## Ronda del 17/oct/2026 · v1.9.0: hoja de empaque (Formato 06), indicaciones de carga y «hieleras»
**Pedido del usuario:** los datos del Formato 06 para cada orden (fecha, especie, horas, lotes, destino, consignatario, tanques de origen, placas, chofer, teléfono, peso bruto, temperatura del producto, tanque y temperatura, hieleras por talla, quién realizó, observaciones y connotaciones S/NS/N/D/N/A), «requerido por ley para tenerlo en archivo», y que todo salga en el PDF y el correo. En Empaque el término correcto es «hieleras». Después pidió «observaciones» del embarque y del camión que no se puedan pasar por alto (ej. «ECHAR 2 TARIMAS VACÍAS Y FLEJE»).
**Respuestas del usuario a las preguntas:** una hoja por orden (cada orden va a un solo destino; varios lotes y puede llevar varios consignatarios); las connotaciones son un estándar de monitoreo del empaque que se pide al terminar (un toque en S si todo fue normal); «hieleras» en toda la app; tanques de origen y tanque y temperatura los propone la app.
- **Datos:** `o.f` en cada orden (`hi, hf, re, ev, ob, pl, ch, tel, tp, to, tq`), limpiada por `f6Norm` en `cleanST` y `WN.OR`, copiada en `decodeST`. `p.ob` en cada embarque (hasta 500 letras) en `cleanST` y `WN.P`. No cambia Supabase (viajan dentro de los registros `OR/<id>` y `P/<u>`).
- **Código:** `f6`, `f6Prop`, `f6Miss`, `f6Lock`, `f6Start`, `f6Card`, `f6Chip`, `f6Txt`, `f6Pdf`, `obsBan`, `shipObs`; eventos `data-f6` (guardar y evaluación) y `data-obs` (indicaciones). La hora inicial la pone `f6Start` al guardar la primera hielera (vista completa y Modo piso). `shipIssues` avisa la hoja incompleta; `closeP` pregunta antes de cerrar con la hoja incompleta y agrega la hoja y las indicaciones al correo.
- **Decisión tomada sin preguntar (revisar con el usuario):** cerrar el embarque con la hoja incompleta no se bloquea, solo pregunta; el PDF la marca «FALTAN DATOS DE LA HOJA».
- **Pruebas:** `hoja_t.py` (110). Las pruebas existentes se pasaron a «hieleras».

## Ronda del 17/oct/2026 (2) · v1.10.0: órdenes como la hoja de PROPESA, hieleras de 15 kg y monitoreo de temperatura
**Pedido del usuario:** (1) en el tablero de tanques, cuántas hieleras de 15 kg hay por talla; (2) al crear una orden, por cada destino/consignatario: total de hieleras, cuántas por talla o color, y ahí se confirma el peso bruto (hieleras 1.4 · gel ice 1.5 · tarimas 9.9 · producto 16 · caja de cartón 0.9), similar a su «ORDER LIST»; (3) monitoreo de temperatura de tanques como control interno: fecha, hora, termómetro flotante, superficie del agua, interna del producto.
**Respuestas del usuario:** ya no se capturan clientes finales; lo que cambia por orden es el kg de producto (15 o 16); las tallas pedidas se revisan contra lo empacado (aviso rojo); rango de temperatura «48.4 °C y 56.6 °C» (se tomó como °F: la app mide en °F).
- **Datos:** línea de orden nueva = `{id, city, cons, boxes, z:[B,R,V,A], kp, tar, cc}` (sin `cli`); `lnX` la limpia en `cleanST` y `WN.OR`. Las líneas viejas conservan `cli` y su fórmula (cartón por hielera, sin tarimas). `W.t` (tarima 9.9). Sin cambios en Supabase.
- **Código:** `lnC`, `lnG`, `lnN`, `ordC`, `ordG`, `ordN`, `cMerge`, `lnPz`, `lnZdif`, `zTable`, `pbTable`, `lnForm`, `lnRead`, `lnBlock`, `shipC`, `shipZauto`, `h15`, `TRNG`, `tOut`, `tCell`, `pdfTemp`. Embarque: `p.c` = componentes de sus líneas (sin renglones en 0) y `p.z` = suma de tallas de sus líneas.
- **Decisiones tomadas sin preguntar (revisar con el usuario):** tarimas y cajas de cartón se escriben en cada orden (en su hoja cambian por consignatario); el rango aplica a las tres temperaturas; las temperaturas de entrada (58–60 °F en los datos de prueba) salen en rojo con ese rango.

## Ronda del 17/oct/2026 (3) · v1.10.1
**Pedidos del usuario:** quitar por ahora el rango de temperatura (dejarlo pendiente); la tarima se queda en 9.9 kg; con la cuenta de Consulta entró a Modo piso y no podía salir; regresar «Borrar todos los datos», solo para Administradores y escondido. También aclaró que un embarque puede llevar varias órdenes (ya se puede: «Unir» en la orden y «Agregar otra orden» en el embarque, para el mismo destino y consignatario; el plan del camión junta todos los embarques abiertos).
- `TRNG=null`: `tOut` siempre falso, sin aviso ni textos de rango; con `TRNG=[mín,máx]` vuelve todo.
- `pisoShell`: el interruptor sale para todos menos el Encargado de piso.
- `advCard` / `rstAll` / `BK_T` / `ADV` (como en la v1.8.4): `<details id="adv">` al final de Administración; respaldo en 15 min, BORRAR TODO y contraseña (`sbAuth('password')`); vacía R, L, B, OR, P, O, T, M y borra las fotos; cada registro se sube como borrado.

## Ronda del 17/oct/2026 (4) · v1.11.0: proveedores de una lista y lote sin entrada
**Contexto:** el usuario pidió probar la app con sus documentos reales (fotos de bitácora, Formatos 02 y 06, orden a proveedor, logística, control de envío y lista de consignatarios). Resultado y plan de transición en el proyecto (`PRUEBA_DOCUMENTOS_REALES.md`, `PLAN_TRANSICION_PAPEL_A_PLATAFORMA.md`). Decidió **cambio directo** del papel a la app y **empezar en cero**.
**Pedidos de esta ronda:** (1) el proveedor de una lista; (2) poder empezar un empaque sin entrada.
**Respuestas del usuario:** lista con los proveedores que hay hoy y un lugar en Administración para editarlos o agregar; la app propone el código del lote; solo el Administrador agrega proveedores; además del nombre y la clave se guardan RFC y permiso de pesca. Lote sin entrada: se anotan lote, proveedor y tanque; existe siempre, con aviso «Sin entrada · Completar ›»; lo hacen Administrador y Encargado de piso; no cuenta en mortalidad ni en el tablero.
- **Datos:** `ST.PV = [{id, n, k, rfc, per, off?}]` (sin `ST.PV` se usa `PV0`); registros `V/<id>` (`WN.V = pvClean`, `encodeST`, `decodeST`, `cleanST`). Lotes: `R.pv` (id del proveedor) y `R.ne` (sin entrada), solo cuando existen, así los lotes de antes se suben igual. Sin cambios en Supabase.
- **Código:** `PV0`, `pvAll`, `pvOn`, `pvBy`, `pvMatch` (lote de antes con el nombre exacto), `pvClean`, `lotProp` (WLR + clave + ddmmyy, + B, C…), `pvOpts`, `LPV`, `penD` (la hoja guarda el id del proveedor en `r.d.origin`), `provCard`, eventos `data-pva`; `neZone`, `neFormHtml`, `neSave`, `neBanner`, eventos `data-nea` y `data-ne`; `addLot` completa un lote `ne`; `lotErr` no marca como repetido un lote `ne`; `calc`, `cierre`, `pdfMort`, `pdfEntrada` y el inicio de Modo piso dejan fuera los lotes `ne`; `stc` dice «Sin entrada»; `lotForm` con `form.pre` (completar). Tocar un lote propuesto lo selecciona completo.
- **Corregido:** `ADV` también se toma al tocar el título de «Configuración avanzada» (el evento `toggle` llegaba después de un redibujo inmediato).
- **Decisiones tomadas sin preguntar (revisar con el usuario):** nombres de la lista inicial como en la bitácora («SCPP Leyes de Reforma» por «SCCP LEYES DE REFORMA»); RFC con formato de 12–13 caracteres; un lote sin entrada solo acepta letras, números y guion (3 a 30); si el lote escrito ya existe, se elige en vez de crear otro.
- **Pruebas:** `proveedores_t.py` (128). `ajustes_t`, `menu_t`, `correcciones_t`, `e2e`, `temperatura_t`, `sincronizacion_t`, `piso_t`, `entradas_t`, `cambio_modo_t`, `recarga_t`, `generar_datos` y `accesibilidad.mjs` eligen el proveedor de la lista; `inicio_t` (versión 1.11.0).
- **Pedido a media ronda (17/oct, 23:45):** «No me gusta que dentro de la app mencione indicios de que no está terminada o de los lotes escritos a mano o con la info que no está». Se quitaron de lo nuevo la sección «Nombres escritos a mano», «(escrito a mano, de antes)», los párrafos de explicación del lote sin entrada y el aviso en el PDF de Entrada. El usuario eligió además cambiar en toda la app los vacíos de «Todavía no hay…/Aún no hay…/Sin datos todavía» por textos cortos y quitar «(de una versión anterior)»; no eligió quitar las cajas de guía ni los faltantes de los PDF. Se quedan los mensajes de conexión. Prueba nueva: ninguna pantalla vacía dice «Todavía no hay», «versión anterior» ni «escrito a mano». 34 grupos, 1862 verificaciones, TODO BIEN.
