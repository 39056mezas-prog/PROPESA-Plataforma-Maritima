# ROADMAP.md · Lo que sigue

Estado: **v1.4.0** con base compartida (todos los equipos ven lo mismo). Pregunta antes de implementar cualquier punto que dependa de una **pregunta abierta**.

## 1. Preguntas abiertas (contestarlas con el usuario)

| # | Pregunta | Afecta |
|---|---|---|
| 1 | ~~Peso bruto~~ **Resuelto 14/oct:** 19.6 kg en todos lados | Órdenes, Embarque |
| 2 | **Resuelto 14/oct: la categoría es la talla** (Blanco/Rojo/Verde/Amarillo). Antes: **Categorías:** la app usa Rojo/Verde/Blanco por caja; el packing list en papel muestra R/V/A y D (despatada) ligadas a la talla. ¿La categoría es en realidad la talla? ¿Existe «Azul»? | Empaque, modelo de datos |
| 3 | **Resuelto 14/oct: no descuenta**, salidas a mano. Antes: **Inventario:** empacar no descuenta kilos del tanque. ¿Debe descontar? Exige capturar la talla (y quizá el peso) de cada caja | Existencias, Mortalidad |
| 4 | **Resuelto 14/oct: resta del total del lote.** Antes: **Desperdicio:** ¿resta existencia o es informativo? | Existencias |
| 5 | **Varios tanques por lote** (en papel «1/2», «3 y 1»). Hoy es uno | Entrada |
| 6 | **Lotes mezclados en un envío:** ya se permite al empacar; ¿se necesita verlo por envío? | Embarque |
| 7 | **Cajas = hieleras:** ¿siempre? | Embarque |
| 8 | **Mortalidad:** ¿la definición actual es la que usan? El papel reporta % mortalidad y temperatura de arribo por envío | Mortalidad |
| 9 | **Encabezado del packing list** (placas, chofer, teléfono, horas, temperaturas, tanque): ¿se captura? | Órdenes/Embarque, PDF |
| 10 | **Color de tape** por consignatario | Embarque |
| 11 | **Temperatura:** ¿quién captura, cada cuánto, qué alertas? (almacenaje 57.7–62.2 °F; transporte 48–49 °F) | Temperatura |
| 12 | Órdenes de fechas distintas en un embarque: ¿se permite y cómo se factura? | Embarque |
| 13 | ¿Versión en inglés o chino para los socios? | Todo |
| 14 | **Logo oficial:** subir el archivo para reemplazar la recreación | Marca |
| 15 | Modo piso: ¿«Cerrar embarque» y «Conteo final» necesitan su propio asistente paso a paso? | Modo piso |
| 16 | Supabase: remitente y dominio del correo con PDF; (ver `SUPABASE.md` §6; fotos en Storage desde la v1.8.0; tablas viejas quitadas el 15/oct) | Base compartida |
| 17 | **Capacidad de cada tanque** (kg o cajas): para mostrar en el tablero de Entrada qué tan lleno está cada uno | Entrada |

## 2. Prioridades

### P0 · Validar con el piso
- [ ] Probar el flujo completo con el compañero de piso usando el manual de usuario.
- [ ] Contestar las preguntas 1–4 (cambian el modelo de datos).
- [ ] Subir el logo original y fotos reales de pantallas/papel.
- [ ] Actualizar la hoja de una página del proceso (aún describe el flujo viejo).

### P1 · Datos compartidos (cuando el usuario lo autorice)
- [ ] IDs estables (UUID) con migración → requisito para sincronizar.
- [ ] Conectar Supabase: Auth, tablas, RLS, Realtime (ver `SUPABASE.md`). Agregar tabla de temperatura.
- [x] Fotos a Supabase Storage (v1.8.0).
- [ ] Correo real con el PDF (Edge Function + Resend/SMTP).
- [ ] Importar datos históricos (PDF/Excel y respaldos de las tablets).
- [ ] Bitácora de auditoría.

### P2 · Procesos que siguen en papel
- [ ] Formato 02 · Control de pesos y tallas (pesos por tina 1–180, totales, cajas completas/incompletas).
- [ ] Encabezado del packing list y PDF con formato oficial.
- [ ] Alertas de temperatura fuera de rango (la captura ya existe).
- [ ] Control de envío: % mortalidad y temperatura de arribo por envío.
- [ ] Editar/eliminar órdenes completas; reordenar el packing list.
- [ ] Descontar kilos al empacar (según pregunta 3) y conciliación.
- [ ] Reportes: mortalidad por proveedor/mes, productividad de empaque, existencias por tanque.

### P3 · Calidad
- [ ] PWA sin conexión (service worker).
- [ ] Código de barras/QR para lote y cajas; impresión de etiquetas.
- [ ] CI en GitHub que corra `pruebas/correr_todo.sh`.
- [ ] Guardado más ligero (`save()` reescribe todo): archivar cerrados / IndexedDB.
- [ ] Prueba de usabilidad con guantes y poca luz.
- [ ] Otros idiomas.

## 3. Hecho (ya no pendiente)
- Pruebas automáticas en el repositorio (`pruebas/`, 322 verificaciones).
- Captura de temperatura por tanque.
- Contraseñas con hash; sin usuarios en el código.
- PDF de cada paso; respaldo y restauración validada.
- Rendimiento con un año de datos; accesibilidad Lighthouse 100.
