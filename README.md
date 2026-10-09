# PROPESA · Plataforma marítima

Sitio estático de una sola página (HTML + CSS + JavaScript, sin dependencias ni paso de compilación).
Incluye recepción de lotes, captura de cajas, embarques, cierre y mortalidad, temperatura, y fotos y notas por sección.

## Contenido

| Archivo | Para qué sirve |
|---|---|
| `index.html` | Toda la aplicación |
| `manifest.webmanifest`, `favicon.svg`, `icon-*.png`, `apple-touch-icon.png` | Ícono y opción "Agregar a pantalla de inicio" en tablet |
| `vercel.json` | Configuración de Vercel (encabezados de seguridad y caché) |

## Probar en tu computadora

Abre `index.html` en el navegador, o levanta un servidor local:

```bash
python3 -m http.server 8080
# abre http://localhost:8080
```

## Subir a GitHub

```bash
cd propesa-plataforma
git init
git add .
git commit -m "PROPESA plataforma marítima"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/propesa-plataforma.git
git push -u origin main
```

(Crea antes el repositorio vacío en github.com.)

## Desplegar en Vercel

1. Entra a https://vercel.com/new e importa el repositorio de GitHub.
2. Configuración: **Framework Preset: Other**, sin Build Command, sin Output Directory (se sirve la raíz).
3. Pulsa **Deploy**. Cada `git push` a `main` vuelve a desplegar automáticamente.

También con la CLI: `npx vercel --prod` dentro de la carpeta.

## Flujo de la plataforma

**Entrada → Órdenes → Empaque → Embarque → Mortalidad final**

1. **Entrada:** se captura el formato de recepción (fecha, hora, proveedor, tanque, temperaturas, lote, kg por caja, kg por talla, kg total y kg de desperdicio). Aquí no se cuentan ni se numeran cajas.
2. **Órdenes:** ciudad destino → consignatario (lista oficial, constante `CONS`) → cliente final → cajas. Se usan 16 kg netos y 20 kg brutos por caja (`KGN` y `KGB`).
3. **Empaque:** las langostas se cuentan al empacar cada pedido. Por cada caja se elige el lote, se escriben las piezas vivas y se toca la categoría. Cada caja se numera sola.
4. **Embarque:** cada orden crea su consignación; se revisan peso y tallas y se cierra el empaque.
5. **Mortalidad final:** conteo final por lote y langostas vivas al llegar; el sistema calcula la pérdida.

## Usuarios de demostración

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@propesa.mx | admin123 |
| Encargado de piso | piso@propesa.mx | piso123 |
| Consulta | consulta@propesa.mx | ver123 |

## Importante: esto es una demostración

- Los datos (lotes, cajas, órdenes, notas y fotos) se guardan **en el navegador de cada dispositivo** (`localStorage`). No se comparten entre usuarios ni dispositivos, y se pierden si se borra el almacenamiento del navegador.
- Los usuarios y contraseñas están dentro del código y **cualquiera que abra el sitio puede verlos**. No pongas contraseñas reales.
- El "correo al cerrar empaque" se simula en pantalla; no se envía ningún correo.
- Para uso real hace falta un servidor con base de datos, inicio de sesión seguro, almacenamiento de fotos y envío de correos.
- El logo es una recreación en SVG. Para usar el archivo oficial, reemplaza la función `LG` en `index.html` o súbelo como imagen.

La plataforma inicia **vacía** (sin entradas, cajas, órdenes ni notas); solo vienen los 3 usuarios de demostración. El botón **Administración → Restablecer demo** borra los datos locales y la deja vacía otra vez.
