# DATOS.md · Modelo de datos

Todo vive en el objeto global `ST`. **Desde la v1.4.0 la copia que vale está en la base compartida** (Supabase, `public.app_records`, ver `SUPABASE.md`); cada equipo guarda una copia en `localStorage['propesa-c1']` para trabajar sin internet. En el modo local de pruebas sigue siendo `localStorage['propesa-v4']`. El usuario en sesión (`me`) no va dentro de `ST`: desde la v1.2.5 se guarda aparte en `propesa-ses` (solo su id y la hora de vencimiento) y la pantalla con los borradores en `propesa-ui` (ver `ARQUITECTURA.md` §9).

## 1. Forma de `ST`

```js
ST = {
  // banderas de migración y contadores
  PK:1, ORc:1, E0:1,          // migraciones ya aplicadas
  BN: 0,                      // contador de cajas (seq), solo crece
  N:  0,                      // contador de movimientos
  RN: 120,                    // contador de lotes (id 'R-0121'), solo crece

  U: [{ id, name, email, role /* 'admin'|'piso'|'consulta' */, notify /* recibe informes */ }],  // sin contraseñas (v1.4.1): las guarda Supabase

  R: [{ id /* 'R-0121' */, lot /* 'WLRCO061026B' */, origin /* proveedor */, tank /* 'T1'..'T6' */,
        rdate /* 'YYYY-MM-DD' */, time /* 'HH:MM' */, date /* 'dd/mm/aaaa' */,
        tempT /* °F tanque */, tempP /* °F producto, texto o rango '59-62' */,
        kgbox /* kg por caja en tanque */, desp /* kg desperdicio */,
        final /* kg conteo final | null */, closed }],

  L: [{ id, t, type /* 'RECEPCION'|'SALIDA_EMBARQUE'|'REVERSA' */, lot,
        size /* '491-610'|'611-850'|'851-1220'|'1221-up' */, m /* GRAMOS */, rev /* id revertido */, rc }],

  B: { [lot]: [{ c /* piezas vivas */, k /* 'R'|'V'|'B' */, d /* índice en P */,
                 o /* 'ordenId.lineaId' */, seq /* número de caja */, ps /* lugar 1..N en Modo piso */ }] },
                 // SOLO cajas ya empacadas; en tanque no hay cajas

  OR: [{ id, etd /* 'YYYY-MM-DD' */,
         lines: [{ id, city /* 'PVG'… */, cons /* índice en CONS */, cli /* 'HXH' */, boxes }],
         sh: { 'PVG|0': índiceEnP } }],          // a qué embarque va cada grupo ciudad|consignatario

  P: [{ n /* 'PVG · YISHUNHAI · 12/10 + 13/10' */, z0, col /* color */, exp,
        h /* hieleras */, z: [4 tallas en hieleras], c: [[concepto, kgUnit, cantidad]],
        alive /* vivas al llegar | null */, closed }],   // embarques / consignaciones

  O: [{ subject, t, to: [correos], body, pn /* nombre del embarque */, att /* nombre del PDF */ }], // informes de cierre

  T: [{ id, t /* 'YYYY-MM-DDTHH:MM' */, tank, a /* agua °F */, s /* superficie */, p /* producto */, by }],

  M: { [clave]: [{ id, t, by, text, ref, imgs: [dataURL] }] }
     // claves: 'recepcion', 'lote:<lote>', 'emp:<o.l>', 'emb:<i>', 'cierre', 'temp'
}
```

`seed()` devuelve un `ST` vacío **sin usuarios** (`U:[]`) → la app pide crear el Administrador.

## 2. Convenciones

- **Kilos en gramos** (`m`); se muestran en kg con `f()`.
- **Fechas:** ISO (`YYYY-MM-DD`) para guardar y comparar; `dd/mm/aaaa` solo para mostrar (`fd()`). Siempre fecha **local** con `dLoc()`; nunca `toISOString()` (da el día equivocado de noche en Tijuana).
- **IDs (v1.4.0):** para que dos equipos no choquen, los ids nuevos no son contadores:
  - `uidN()` = número único basado en la hora (≈ 16 cifras): movimientos (`L.id`), cajas (`b.seq`), órdenes (`OR.id`), notas (`M[].id`), lecturas (`T.id`).
  - `uidS()` = texto que se ordena por fecha: embarques (`P.u`) e informes (`O.u`). Los que venían de antes reciben `legU(i)` (`000000000` + índice) y quedan primero.
  - Lotes: la clave compartida es el **código del lote**; `R.id` ('R-0121') sigue con `ST.RN` solo para mostrarse.
  - Líneas de una orden: `max+1` dentro de su orden (viajan dentro del registro de la orden).
  - Embarques: dentro de la app siguen por **índice** en `ST.P` (`b.d`, `o.sh`, `emb:<i>`); en la base viajan con `P.u` y al armar `ST` se ordenan por `u`, así el índice es el mismo en todos los equipos.
- **Campos internos de la sincronización** (no editarlos a mano): `b._d` y `o._sh` guardan referencias a un embarque que todavía no llega; `ST._orph` guarda registros que todavía no se pueden colocar (por ejemplo, una caja de un lote que aún no llega). `encodeST` los vuelve a subir tal cual para no borrarlos.
- **Existencia de un lote** = suma de `L` por talla (`bal`). Empacar no descuenta.
- **Embarque con varias órdenes:** varias entradas de `o.sh` apuntan al mismo índice de `P`; `syncShipIdx` suma hieleras; `moveGroup` une/separa y mueve `b.d`; `dropShip` borra embarques vacíos y **reindexa** (actualiza `b.d` y `o.sh`).

## 3. Cambiar la estructura (obligatorio)

1. Agrega el campo con un valor por defecto que no rompa datos viejos.
2. Si hay que transformar datos existentes, crea una migración con su bandera (como `PK`, `ORc`, `E0`) y llámala al cargar.
3. Agrega el campo a **`cleanST()`** con su validación (tipo, rango, longitud). Lo que no esté en `cleanST` se pierde al restaurar un respaldo.
4. Agrega una prueba en `pruebas/` con datos viejos y nuevos.
5. Documenta aquí.

## 4. Registros compartidos

`encodeST()` convierte `ST` en registros (`R/<lote>`, `L/<id>`, `B/<seq>`, `OR/<id>`, `P/<u>`, `O/<u>`, `T/<id>`, `M/<id>`) normalizados con `WN` (orden fijo de campos), y `decodeST()` hace lo contrario con un orden que no depende del equipo. `ST.U` no viaja en registros: sale de `profiles`. Si agregas un campo a `ST`, agrégalo también en `WN` (si no, ese campo no se comparte).

## 5. Respaldo

- **Descargar respaldo** (Administración) = `ST` completo en `.json`.
- **Restaurar** (solo Administrador, en Administración): pide confirmación, pasa por `cleanST(d, true)` (descarta código, imágenes no válidas, índices fuera de rango, duplicados; los usuarios del respaldo se ignoran) y **reemplaza los datos de todos los equipos**.
- **Borrar todos los datos**: escribir BORRAR → `ST = {...seed(), U}`; se borra en todos los equipos; los usuarios se conservan.
- **Datos viejos de cada tablet** (antes de la v1.4.0) se quedan en `propesa-v4` sin mezclarse; Administración permite descargarlos o borrarlos.
- En el modo local de pruebas, restaurar y borrar funcionan como antes (solo en ese navegador).
- Ejemplos válidos: `pruebas/datos/backup.json` (con usuarios de prueba, solo para pruebas) y `pruebas/datos/seed.json`.

## 6. Tamaño

Con un año de datos sin fotos: ~2.2 MB. El límite de `localStorage` ronda 5 MB por sitio; las fotos (base64, se reducen con `shrink` a 800 px y calidad 0.6 desde la v1.4.1, ~120 mil caracteres cada una) son lo que más lo llena. Desde la v1.4.0 cada equipo recibe las fotos de todos: caben unas 40 en total; el arreglo de fondo es pasarlas a Supabase Storage (ver `SUPABASE.md` §6). Si `save()` falla aparece el aviso rojo con «Descargar respaldo».
