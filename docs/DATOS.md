# DATOS.md · Modelo de datos

Todo vive en el objeto global `ST`, guardado completo en `localStorage['propesa-v4']`. El usuario en sesión (`me`) no va dentro de `ST`: desde la v1.2.5 se guarda aparte en `propesa-ses` (solo su id y la hora de vencimiento) y la pantalla con los borradores en `propesa-ui` (ver `ARQUITECTURA.md` §9).

## 1. Forma de `ST`

```js
ST = {
  // banderas de migración y contadores
  PK:1, ORc:1, E0:1,          // migraciones ya aplicadas
  BN: 0,                      // contador de cajas (seq), solo crece
  N:  0,                      // contador de movimientos
  RN: 120,                    // contador de lotes (id 'R-0121'), solo crece

  U: [{ id, name, email, role /* 'admin'|'piso'|'consulta' */, notify /* recibe informes */,
        pwh /* SHA-256 de 'propesa:'+id+':'+contraseña */, dflt /* contraseña débil heredada */ }],

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
- **IDs:** lotes con `ST.RN` y cajas con `ST.BN`, que solo crecen. Órdenes y líneas con `max+1`. Embarques por **índice** en `ST.P` (`b.d`, `o.sh`). *Para Supabase hay que pasar todo a UUID (ver `SUPABASE.md`).*
- **Existencia de un lote** = suma de `L` por talla (`bal`). Empacar no descuenta.
- **Embarque con varias órdenes:** varias entradas de `o.sh` apuntan al mismo índice de `P`; `syncShipIdx` suma hieleras; `moveGroup` une/separa y mueve `b.d`; `dropShip` borra embarques vacíos y **reindexa** (actualiza `b.d` y `o.sh`).

## 3. Cambiar la estructura (obligatorio)

1. Agrega el campo con un valor por defecto que no rompa datos viejos.
2. Si hay que transformar datos existentes, crea una migración con su bandera (como `PK`, `ORc`, `E0`) y llámala al cargar.
3. Agrega el campo a **`cleanST()`** con su validación (tipo, rango, longitud). Lo que no esté en `cleanST` se pierde al restaurar un respaldo.
4. Agrega una prueba en `pruebas/` con datos viejos y nuevos.
5. Documenta aquí.

## 4. Respaldo

- **Descargar respaldo** (Administración) = `ST` completo en `.json`.
- **Restaurar**: pide confirmación, pasa por `cleanST()` (descarta código, imágenes no válidas, índices fuera de rango, duplicados; exige al menos un Administrador) y reemplaza todo lo del equipo.
- Desde la Configuración inicial también se puede restaurar.
- **Borrar los datos de este equipo**: escribir BORRAR → `ST = seed()`.
- Ejemplos válidos: `pruebas/datos/backup.json` (con usuarios de prueba, solo para pruebas) y `pruebas/datos/seed.json`.

## 5. Tamaño

Con un año de datos sin fotos: ~2.2 MB. El límite de `localStorage` ronda 5 MB por sitio; las fotos (base64, se reducen con `shrink`) son lo que más lo llena. Si `save()` falla aparece el aviso rojo con «Descargar respaldo».
