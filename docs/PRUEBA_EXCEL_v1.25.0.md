# Prueba con los Excel reales por la pantalla · v1.25.0 · 29/oct/2026

Se capturaron los dos Excel (`RECEPCION_Y_ENVIOS_LANGOSTA_2026-27_martha.xlsx` y `RECEPCIONES_DE_LANGOSTA_2026-2027.xlsx`) **tecleando en la app**, como lo haría Martha (Administradora), en modo local (sin tocar la base real): Administración → catálogos; Entrada; Órdenes → hoja de empaque → Empaque hielera por hielera → Embarque → Cerrar; salidas en el lote con su fecha; Revisión → % del cliente y arribo; precio por lote; salidas incompletas con «Cambio de talla» + «Volver a descontar».
Los envíos que en el Excel no traen tallas **no se capturaron** (decisión del usuario): PROPESA 15–26/oct, 10/oct ×3 y 16/oct «TODO DAVID»; Abel 19 y 24/oct.

## Resultado
| Maquila | Recibido (Excel = app) | Envíos capturados | Notas |
|---|---|---|---|
| PROPESA | **49,928.95 kg** (48 lotes) | 34 envíos, 2,350 hieleras, 37,600 kg | Incluye 2 órdenes del 13/oct con 105 hieleras de lotes de **David** (orden mixta) |
| Abel | **19,430.55 kg** (24 lotes) | 17 envíos, **1,028 cajas de 15 kg** (PDF ya cuenta ÷ 15) | |
| David | **5,679.25 kg** (3 lotes) | — (sus 105 hieleras salieron en órdenes de PROPESA; su tanque bajó 1,680 kg) | |
| Luis Arce | **6,010.45 kg** (2 lotes) | 2 envíos, 350 hieleras | |

- **Balance 17–27 sep (PROPESA): 88.27 kg a favor** ✔ (recibido 17,249.00 · salidas 13,406.68 = envíos 13,312.00 + congelar 85.61 + basura 9.07 · existencia física 3,930.59). En la v1.24.0 daba −6.41 porque las salidas quedaban con la fecha de hoy.
- Salidas para congelar/basura/recuperación con su fecha: PROPESA 85.61 / 9.07; Abel 193.18 / 133.50; David 598.16 / 110.25 / recuperación 171.95; Luis Arce congelar 27.20 · recuperación 382.30.
- **Cambio de talla** (resorteo) para las salidas incompletas: PROPESA 206.43 kg, Abel 61.10 kg, Luis Arce 0.60 kg. Quedan sin descontar PROPESA 72.32 kg y Abel 489.35 kg (389.85 en HKG 15/oct): esos lotes ya no tenían kilos en **ninguna** talla. Es decir, el Excel manda de esos lotes más de lo que se recibió de ellos (vienen de otros lotes que el Excel no anota).
- **Temperaturas con los rangos internos:** agua en rojo 1 de 86 lecturas de entrada, en ámbar 9; producto en rojo 9 de 77, en ámbar 9. (Las entradas del 15–24/oct no traen temperatura en el Excel: se capturaron 59 °F.)

## Datos del Excel que conviene revisar (no son errores de la app)
1. WLRCO220926 está con fecha **22/06/2026** (debe ser 22/09): la app avisa y se corrigió con «Corregir». Sin corregir, el balance de septiembre no lo cuenta.
2. 21 entradas con hora de madrugada (01:00–04:20): ¿son de la tarde (13:00–16:20)? La app avisa en cada lote.
3. Luis Arce 21/oct: se mandaron 150 cajas (2,400 kg) con 2,379.1 kg en tanque, y además se anotan 350.9 kg de recuperación del mismo lote → no alcanzan los kilos (faltaron 25.1 kg al registrar la recuperación).
4. Las entradas repartidas en dos tanques («1./2», «3 Y 1») no dicen cuántos kg van en cada tanque: se capturaron a la mitad de cada talla. Desde la v1.25.0 la app pide los kg exactos por talla.
