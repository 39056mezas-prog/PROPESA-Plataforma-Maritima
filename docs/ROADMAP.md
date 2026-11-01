# ROADMAP.md · Lo que sigue

Estado: **v1.20.0** (26/oct/2026), con base compartida en Supabase desde la v1.4.0 (todos los equipos ven lo mismo) y rol Cliente desde la v1.13.0. Pregunta antes de implementar cualquier punto que dependa de una **pregunta abierta**.

> **Revisado el 22/oct/2026 contra el código.** Este archivo se había quedado en la v1.4.0 y todavía marcaba como pendientes cosas que ya funcionan (base compartida, ids estables, historial de cambios, editar/eliminar órdenes, salida de kilos al cerrar el embarque). Si algo de aquí contradice `index.html` o `SUPABASE.md`, gana el código.

## 1. Preguntas abiertas (contestarlas con el usuario)

| # | Pregunta | Afecta |
|---|---|---|
| 1 | ~~Peso bruto~~ **Resuelto 14/oct:** 19.6 kg en todos lados | Órdenes, Embarque |
| 2 | **Resuelto 14/oct: la categoría es la talla** (Blanco/Rojo/Verde/Amarillo). | Empaque, modelo de datos |
| 3 | **Resuelto.** 14/oct: empacar una hielera **no** descuenta. 22/oct (v1.13.0): **al cerrar el embarque** sale sola una «Salida a embarque» por lote y talla; reabrir la regresa. Ya no hay que registrar la salida a mano | Existencias, Mortalidad |
| 4 | **Resuelto 14/oct: resta del total del lote.** | Existencias |
| 5 | ~~Varios tanques por lote~~ **Resuelto 26/oct (v1.19.0)** | Entrada |
| 6 | ~~Lotes mezclados en un envío~~ **Resuelto 26/oct (v1.21.0):** cada envío dice cuánto lleva de cada lote, en pantalla, PDF y correo | Embarque |
| 7 | **Resuelto 17/oct: se dicen «hieleras»** en toda la app. | Embarque |
| 8 | **Mortalidad:** ¿la definición actual es la que usan? El papel reporta % mortalidad y temperatura de arribo por envío | Mortalidad |
| 9 | **Resuelto 17/oct (v1.9.0): hoja de empaque (Formato 06) en cada orden.** 26/oct: cerrar con la hoja incompleta **solo pregunta** (decisión del usuario) | Órdenes/Embarque, PDF |
| 10 | ~~Color de tape~~ **Resuelto 23/oct (v1.15.0):** color por consignatario (26/oct: sin tape por envío, decisión del usuario) | Embarque |
| 11 | **Abierta (17/oct, v1.10.1; 26/oct: sigue sin rango por decisión del usuario).** Falta el rango normal en °F y si es el mismo para flotante, superficie y producto, para volver a marcar en rojo (`TRNG`). Referencia del papel: almacenaje 57.7–62.2 °F; transporte 48–49 °F | Temperatura |
| 12 | ~~Órdenes de fechas distintas en un embarque~~ **Resuelto 26/oct:** se permiten, sin aviso. Falta solo cómo se factura, si llega a importar | Embarque |
| 13 | ¿Versión en inglés o chino para los socios? **22/oct: la pantalla del comprador (rol Cliente) va en inglés.** Falta: acceso y ventana de instalar en inglés, y si se quiere chino | Todo |
| 14 | **Logo oficial:** subir el archivo para reemplazar la recreación | Marca |
| 15 | ~~Paso a paso en Modo piso~~ **Resuelto 26/oct (v1.21.0):** «Cerrar embarque» y «Conteo final» van paso a paso | Modo piso |
| 16 | **Correo con PDF:** ¿desde qué dirección sale (p. ej. `informes@propesa.org`)? ¿Resend o el SMTP que ya tengan? Hace falta verificar el dominio `propesa.org` en el servicio de correo (registros DNS) | Base compartida |
| 17 | **Capacidad de cada tanque** (kg o hieleras, T1–T6): para mostrar en el tablero de Entrada qué tan lleno está cada uno | Entrada |
| 19 | ~~Precios en la base~~ **Resuelto 26/oct:** solo el Administrador, también en la base (`20261026_precios.sql`) | Seguridad |
| 20 | ~~PDF de otras maquilas~~ **Resuelto 26/oct:** conservan el logo de PROPESA | PDF |
| 21 | ~~Balance de Luis Arce~~ **Resuelto 26/oct:** la fórmula del balance de PROPESA (cuenta despatada y congelados); el Excel de Luis Arce tenía el error | Hojas |
| 22 | ~~Lote en varios tanques~~ **Resuelto 26/oct (v1.19.0):** otro tanque en la entrada y traslados en el lote | Entrada |
| 18 | ~~Especie en las órdenes~~ **Resuelto 26/oct (v1.20.0):** cada orden lleva su especie; empaque y compradores la usan | Órdenes, compradores |

## 2. Prioridades

### P0 · Validar con el piso
- [ ] Probar el flujo completo con el compañero de piso usando el manual de usuario.
- [x] Contestar las preguntas 1–4 (resueltas 14/oct; la 3 se completó el 22/oct).
- [ ] Subir el logo original y fotos reales de pantallas/papel.
- [ ] Actualizar la hoja de una página del proceso (aún describe el flujo viejo).

### P1 · Datos compartidos
- [x] IDs estables (`uidN` / `uidS`) con migración (v1.4.0).
- [x] Supabase conectado: Auth (correo y contraseña), registros `app_records`, RLS por rol, sincronización cada 4 s con `pull`/`push` sin pisar cambios (v1.4.0–v1.4.1). Lecturas de temperatura incluidas (`T/<id>`). Se usa consulta cada 4 s en vez de Realtime; cambiar a Realtime no es necesario mientras esto funcione.
- [x] Fotos a Supabase Storage (v1.8.0).
- [x] Rol Cliente con RLS propia (v1.13.0).
- [x] **Historial de cambios en la base** (`app_records_hist`, v1.4.1): guarda quién cambió o borró cada registro y cómo estaba. Hoy se consulta con SQL (`SUPABASE.md` §7).
- [x] **Pantalla del historial** (v1.16.0): Administración → «Historial de cambios», últimos 30 días (se borra solo).
- [ ] Botón para regresar un registro a su versión anterior desde la pantalla (hoy: se ve el valor viejo y se vuelve a capturar, o SQL, `SUPABASE.md` §7).
- [ ] Correo real con el PDF (Edge Function + Resend/SMTP) → **bloqueado por la pregunta 16** y por la cuenta del servicio de correo.
- [ ] Importar datos históricos (PDF/Excel y respaldos de las tablets) → **falta que el usuario comparta los archivos**. Los respaldos `.json` de una tablet ya se pueden restaurar desde la app.

### P2 · Procesos que siguen en papel
- [ ] Formato 02 · Control de pesos y tallas (pesos por tina 1–180, totales, cajas completas/incompletas).
- [x] Encabezado del packing list (hoja de empaque, v1.9.0).
- [ ] Alertas de temperatura fuera de rango (la captura ya existe) → **bloqueado por la pregunta 11**.
- [x] Control de envío: % mortalidad del cliente y temperatura de arribo (v1.19.0).
- [x] Hojas del Excel de Martha en PDF (v1.19.0).
- [x] Editar y eliminar órdenes completas (`editar_orden_t`, `eliminar_orden_t`).
- [ ] Reordenar el packing list.
- [x] Salida de kilos al cerrar el embarque (v1.13.0, pregunta 3).
- [ ] Reportes: mortalidad por proveedor/mes, productividad de empaque, existencias por tanque.
- [ ] Ocupación de cada tanque en el tablero → **bloqueado por la pregunta 17**.

### P3 · Calidad
- [ ] PWA sin conexión. `sw.js` (v1.12.0) solo deja instalar la app; no guarda nada para usar sin internet. La captura sin internet sí funciona una vez abierta la app (se sube al volver).
- [ ] Código de barras/QR para lote y cajas; impresión de etiquetas.
- [ ] CI en GitHub que corra `pruebas/correr_todo.sh`.
- [ ] Guardado más ligero (`save()` reescribe todo): archivar cerrados / IndexedDB.
- [ ] Prueba de usabilidad con guantes y poca luz.
- [ ] Otros idiomas (ver pregunta 13).

## 3. Hecho (ya no pendiente)
- Pruebas automáticas en el repositorio (`pruebas/`, 38 grupos; `correr_todo.sh` termina en «TODO BIEN»).
- Base compartida en Supabase con reglas por rol, historial de cambios y fotos.
- Dominio propio **propesa.org**; la vista previa al compartir el link apunta ahí (v1.13.2).
- Captura de temperatura por tanque.
- Contraseñas en Supabase Auth; sin usuarios en el código.
- PDF de cada paso; respaldo y restauración validada.
- Rendimiento con un año de datos; accesibilidad Lighthouse 100.
