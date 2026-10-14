# PRUEBAS.md · Cómo se prueba

## 1. Correr todo

Requisitos: Python 3, Playwright (`pip install playwright`) y Chromium (`python3 -m playwright install chromium`).

```bash
sh pruebas/correr_todo.sh
```

Levanta un servidor en el puerto 8765, corre 18 grupos y termina con **«TODO BIEN»** (904 verificaciones en la v1.3.0). Cada registro queda en `/tmp/propesa_<prueba>.log`; una línea que empieza con `FAIL` marca el grupo como fallido.

Para correr una sola: `python3 -m http.server 8765 &` y luego `python3 -I pruebas/<archivo>.py`. `BASE` (variable de entorno) cambia la URL, por ejemplo para probar la versión publicada.

## 2. Qué cubre cada archivo

| Archivo | Cubre | Verif. |
|---|---|---|
| `inicio_t.py` | Configuración inicial, ningún rastro de demo en pantalla, versión, temperatura, Informes de cierre, borrar datos | 20 |
| `csp_t.py` | Cabeceras de `vercel.json` aplicadas: la app funciona sin violaciones de CSP (fotos, PDF, respaldo, Ajustes) | 13 |
| `e2e.py` | Flujo completo Entrada → Órdenes → Empaque → Embarque → Mortalidad | 30 |
| `ajustes_t.py` | Panel de Ajustes (tema, 3 tamaños, foco, sin desbordes a 390/820/1440 px, sin almacenamiento) | 101 |
| `menu_t.py` | Menú del perfil y botón Ajustes | 36 |
| `correcciones_t.py` | Correcciones del /review (guardado fallido, contraseñas, fechas, respaldo seguro, embarque cerrado, ids de lote) | 27 |
| `piso_t.py` | Modo piso: empacar y registrar entrada | 21 |
| `entradas_t.py` | Modo piso: hoja de varias entradas (agregar, validar por fila, guardar parcial, sin duplicar, Enter, quitar, borradores, vistas 390/820/1180/1440, texto 20 px, tema oscuro) | 58 |
| `cajas_auto_t.py` | Cajas que se guardan solas, quedan grises y se editan | 24 |
| `interruptor_t.py` | Interruptor iOS, logo → inicio, admin no entra a piso | 16 |
| `avisos_t.py` | Avisos rojos que llevan a donde se resuelven | 26 |
| `pdf_t.py` | PDF de cada paso (archivo válido); el Plan de embarques trae el camión | 11 |
| `botones_t.py` | Pulsa todos los botones de todas las pantallas buscando errores de JavaScript | 1 |
| `tabla_entrada_t.py` | Tabla de Entrada: tallas en dos renglones, sin números partidos, punto de color alineado, encabezados sin cortes de más, desplazamiento dentro de la tarjeta (390/820/1440, texto 20 px, tema oscuro) | 45 |
| `estados_caja_t.py` | Empaque: estado de cada caja (Pendiente / En captura / ✔ Completada / Editando / ⚠ Incompleta), solo color no completa, doble toque no duplica, reabrir y corregir la misma caja (Actualizar, Cancelar, Enter, Esc, Quitar), barra delgada que marca el avance real (0 → 25 → 100 %) con el botón Guardar de tamaño fijo, resumen completadas/pendientes/%, el aviso no tapa la barra, Rojo/Verde/Blanco del mismo tamaño y ≥44 px, sin pastillas de estado, cada fila dice «Caja N» y «N piezas», el aviso sale arriba de la barra, recarga, Modo piso, rol consulta (390/820/1440) | 143 |
| `titulo_t.py` | Celular: la barra de arriba dice la sección actual (ícono + nombre, sin «Paso N de 5») en las 12 pantallas, en un solo renglón con ☰ y los botones, sin desbordes (390, 360 con 20 px); en 820 y 1440 no aparece | 145 |
| `recarga_t.py` | Recargar no cierra la sesión: se conservan pantalla y borradores (formulario de Entrada, línea de orden, nota, búsqueda, Empaque de piso con piezas y categoría, hoja de entradas de piso); cerrar sesión borra todo; sesión vencida y usuario eliminado piden entrar; datos raros en `propesa-ui` no rompen (1180 y 390 px) |
| `teclado_t.py` | Teclado fijo de Empaque. Modo piso (1180, 820 oscuro, 390): números, ⌫, Borrar, máximo 4 cifras, la categoría guarda y pasa a la siguiente, corregir una caja guardada (el primer número reemplaza), categoría primero + «Siguiente caja», «Caja anterior», teclado físico, «Quitar caja» con confirmación, letra de 20 px sin cortes. Vista completa (1440, 1180 oscuro, 820, 390): teclado y «Guardar cajas» a la vista al entrar, la categoría marca la fila y avanza, guardar, corregir una caja guardada. iPad simulado (táctil): tocar teclado y cajas, sin selección de texto. Consulta y embarque cerrado sin teclado |

Extras (no están en `correr_todo.sh`):
- `rendimiento_t.py` — genera un año de datos y mide tiempos de pantalla y de guardado (CPU normal y 4× más lenta).
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
