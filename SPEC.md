# Spec: Panel de Ajustes (Configuración) — PROPESA

> Estado: **aprobado e implementado** · 12/oct/2026 · decisiones: se quitan los botones A A A; solo Oscuro/Claro (sin elección sigue al equipo); 15 px inicial; preferencias por equipo.
> **Cambio 12/oct (después de usarlo):** (1) al abrir Ajustes la pantalla de atrás ya no se oscurece y se sigue viendo; en celular el panel es una hoja desde abajo (máx. 66% de alto). (2) El tamaño del texto vuelve a **3 tamaños** —Normal 15 px, Grande 17 px, Muy grande 20 px— pero con deslizador; los valores guardados se ajustan al más cercano. Los criterios 4 y el comportamiento del deslizador de abajo quedan así reemplazados.
> Fuente: `PROPESA_Settings_Panel_Instructions.md` + revisión del código actual de `index.html`.

## Supuestos (corrígelos antes de aprobar)

1. **Un solo panel para todos:** Administrador, Encargado de piso y Consulta ven el mismo botón **Ajustes**, en la vista completa y también en Modo piso.
2. **Preferencias por equipo, no por usuario:** se guardan en el navegador de cada tablet o computadora (`localStorage`), igual que hoy se guarda el tamaño de letra. Si dos personas usan la misma tablet, comparten tema y tamaño.
3. **El tamaño por defecto es 15 px, no 14 px:** el texto base actual de la app mide **15 px** (`body{font:15px …}`). Para no cambiar cómo se ve hoy, el valor inicial del deslizador será 15 px. El rango sigue siendo 12–20 px, de 1 en 1.
4. **El primer uso respeta el sistema:** hoy el tema sigue al equipo (oscuro si el equipo está en oscuro). Hasta que alguien elija en Ajustes, se mantiene así. El selector muestra marcado el tema que se está viendo en ese momento.
5. **Los botones "A A A" del encabezado desaparecen:** hoy hay tres botones de tamaño de letra. El deslizador los reemplaza para no tener dos controles que hacen lo mismo. Lo que ya estaba guardado se respeta: normal → 15 px, grande → 17 px, muy grande → 20 px.
6. **Ajustes no se guarda en la nube:** cuando exista Supabase, esto sigue siendo una preferencia del equipo.

## Objetivo

Que cualquier persona pueda poner la app **en oscuro o en claro** y **agrandar o achicar el texto** desde un solo lugar, con un panel ordenado al estilo de Configuración de iOS, sin perder lo que está capturando.

**Usuarios:**
- Personal de piso: lee la tablet de lejos o con poca luz, con guantes.
- Administrador: usa computadora.
- Consulta: puede entrar desde el celular.

**Historias:**
- Como encargado de piso, quiero agrandar el texto para leer la tablet a un brazo de distancia.
- Como administrador, quiero modo claro en la oficina y oscuro en la planta.
- Como cualquier usuario, quiero que mi elección siga ahí al recargar o al volver a entrar.

## Alcance

**Sí incluye:**
- Botón **Ajustes** (ícono de engrane + texto "Ajustes" si cabe) arriba a la derecha, junto al nombre del usuario. Va en la vista completa y en Modo piso.
- Panel lateral derecho de 380 px en computadora y tablet; en celular ocupa toda la pantalla.
- Grupo **Apariencia** → **Tema**: control segmentado `Oscuro` / `Claro`.
- Grupo **Accesibilidad** → **Tamaño del texto**: deslizador de 12 a 20 px con el valor visible ("15 px"), y los extremos marcados `Pequeño` y `Grande`. Abajo, un renglón de ejemplo que se actualiza en vivo.
- Persistencia y carga temprana sin parpadeo del tema equivocado.

**No incluye:**
- Otros ajustes (idioma, notificaciones, etc.).
- Preferencias por usuario.
- Cambios de diseño en otras pantallas, aparte de lo necesario para que el texto escale bien.

## Comportamiento

| Acción | Resultado |
|---|---|
| Tocar **Ajustes** | Abre el panel. El foco pasa al título del panel. La pantalla de atrás se sigue viendo sin oscurecerse, para ver el cambio en vivo. |
| Tocar Ajustes otra vez, la ✕ (`aria-label="Cerrar configuración"`), **Esc** o fuera del panel | Cierra el panel y regresa el foco al botón Ajustes. |
| Con el panel abierto | La pantalla de atrás **no se vuelve a dibujar**: no se pierde lo que estaba escrito. La tecla Tab no se sale del panel. |
| Elegir `Claro` / `Oscuro` | Cambia **toda la app** al instante: encabezado, menú, tarjetas, tablas, formularios, avisos y Modo piso. |
| Mover el deslizador (con dedo, mouse o flechas del teclado) | El texto de toda la app cambia en vivo. El valor se anuncia a lectores de pantalla (`aria-valuetext="15 píxeles"`). |
| Recargar la página | Se conservan el tema y el tamaño. No hay parpadeo del tema contrario. |
| `localStorage` bloqueado o lleno | Los ajustes funcionan durante la sesión; no hay errores. |

## Enfoque técnico (dentro de la arquitectura actual)

- **Tema:**
  - El CSS ya tiene tokens en `:root` y reglas `:root[data-theme="dark"]` / `:root[data-theme="light"]`.
  - Ajustes solo pone `data-theme` en `<html>`; sin elección guardada, se queda sin atributo y sigue al sistema.
  - Un script mínimo en `<head>` lo aplica antes de pintar, para que no parpadee.
  - Se revisan los colores fijos que solo están pensados para un tema, por ejemplo encabezado, campos y modo piso, para que los dos temas queden completos y legibles.
- **Tamaño del texto:**
  - Hoy se usa `zoom` sobre el área principal, que agranda también íconos y márgenes y no toca el menú ni el encabezado.
  - Se reemplaza por **`html{font-size:var(--app-font-size)}`** (por defecto 15 px).
  - Los ~130 `font-size` fijos en px del CSS se convierten a `rem` en proporción (14px → .9333rem). Así crece **solo el texto**, en toda la app, y los íconos (SVG con ancho fijo) y el logo se quedan igual.
  - Los campos de captura mantienen **mínimo 16 px** para que iOS no haga zoom al tocarlos.
- **Estado:**
  - Una sola fuente de verdad: `PREF={theme:null|'dark'|'light', fs:15}`.
  - Se guarda en `localStorage` con las claves `propesa-theme` y `propesa-fs`.
  - Se migra la clave vieja `propesa-z`.
- **Panel:**
  - Se dibuja fuera de `#app`, en su propio contenedor, para que abrirlo no vuelva a dibujar la pantalla.
  - Usa los mismos tokens de color, radios y el ícono de engrane dibujado igual que los demás (set `IC`).

## Tech Stack

HTML + CSS + JavaScript en un solo archivo (`index.html`), sin librerías ni compilación. Se publica en Vercel como sitio estático.

## Commands

```bash
# Servir localmente
cd propesa-plataforma && python3 -m http.server 8765        # http://localhost:8765

# Revisar sintaxis del JavaScript
python3 -c "import re;s=open('index.html').read();open('/tmp/x.js','w').write(re.findall(r'<script>(.*?)</script>',s,re.S)[-1])" && node --check /tmp/x.js

# Pruebas de punta a punta (Playwright, Python)
python3 -I pruebas/ajustes_t.py        # nuevas, de esta función
python3 -I pruebas/e2e.py              # flujo completo existente
```

## Project Structure

```
propesa-plataforma/
  index.html        → toda la app (CSS en <style>, JS en <script>)
  SPEC.md           → esta especificación
  README.md         → uso y despliegue
  supabase/         → esquema preparado (no aplicado)
  pruebas/          → pruebas Playwright (se agrega en esta función)
```

## Code Style

Se sigue el estilo existente: plantillas de texto que dibujan HTML, acciones por atributos `data-*` con un solo manejador por tipo, colores solo por variables CSS y textos en español.

```js
/* Ajustes: una sola fuente de verdad, guardada por equipo */
const PREF={theme:null,fs:15};
function applyPrefs(){const r=document.documentElement;
  PREF.theme?r.setAttribute('data-theme',PREF.theme):r.removeAttribute('data-theme');
  r.style.setProperty('--app-font-size',PREF.fs+'px')}
document.addEventListener('click',e=>{const x=e.target.closest('[data-set-theme]');if(!x)return;
  PREF.theme=x.dataset.setTheme;applyPrefs();savePrefs();paintSettings()});
```

## Testing Strategy

Se usa Playwright (Python) con Chromium contra el servidor local, en tres tamaños (390, 820 y 1440 px) y con los dos temas.

**Nuevas pruebas, `pruebas/ajustes_t.py`:**
- Abrir y cerrar el panel con el botón, con la ✕, con Esc y tocando fuera; el foco regresa a Ajustes.
- Con texto escrito en un formulario, abrir y cerrar Ajustes no lo borra.
- Claro y Oscuro cambian el fondo, las tarjetas, las tablas, el menú, los campos y el Modo piso. Se miden contrastes: texto principal ≥ 4.5:1 en ambos.
- Deslizador: con las flechas del teclado recorre 12…20; el valor visible coincide; el texto del cuerpo, del menú y de las tablas crece en proporción; el ancho de los íconos no cambia.
- Sin desbordes horizontales a 20 px en 390, 820 y 1440 px.
- Al recargar se conservan; con `localStorage` bloqueado no hay errores.
- Primera vez sin preferencia: sigue al sistema y el texto queda en 15 px, igual que hoy.

**Regresión:** se corren las 7 pruebas existentes (flujo completo, Modo piso, cajas automáticas, interruptor iOS, avisos con enlace, correcciones del review, PDF) y el recorrido que toca todos los botones.

## Boundaries

- **Siempre:**
  - Usar los tokens de color existentes.
  - Probar los dos temas y los tres tamaños de pantalla.
  - Mantener los campos de captura en 16 px como mínimo.
  - Correr la regresión completa antes de entregar.
- **Preguntar antes:**
  - Agregar una tercera opción de tema.
  - Guardar preferencias por usuario.
  - Cambiar el diseño de otras pantallas más allá de lo necesario para que el texto escale.
- **Nunca:**
  - Agregar librerías.
  - Cambiar la lógica de negocio.
  - Volver a dibujar la pantalla al abrir el panel.
  - Poner controles que no hagan nada.

## Success Criteria

1. El botón **Ajustes** se ve arriba a la derecha, alineado con los controles del usuario, en la vista completa y en Modo piso, en 390, 820 y 1440 px.
2. El panel abre y cierra con el botón, la ✕, Esc y tocando fuera; el foco regresa a Ajustes.
3. Oscuro y Claro cambian toda la app al instante, con contraste ≥ 4.5:1 en el texto principal de ambos temas.
4. El deslizador tiene 3 paradas (Normal 15 · Grande 17 · Muy grande 20 px), con el tamaño visible y anunciado; el texto escala en toda la app y los íconos y el logo no. *(antes: 12–20 px de 1 en 1)*
5. No hay desbordes horizontales con 20 px en ningún tamaño de pantalla.
6. Las preferencias se conservan al recargar y no hay parpadeo del tema contrario.
7. Abrir Ajustes no borra lo que se estaba capturando.
8. Todas las pruebas existentes siguen pasando.

## Open Questions

1. **¿Quito los botones "A A A" del encabezado?** Mi propuesta es que sí, porque el deslizador los reemplaza.
2. **¿Agrego una tercera opción "Automático (según el equipo)"?** El documento pide solo Oscuro/Claro. Hoy la app sigue al equipo. Mi propuesta: solo dos opciones, y mientras no elijas se sigue al equipo (supuesto 4).
3. **¿Valor inicial de 15 px**, el tamaño real de hoy, o 14 px como dice el documento? Mi propuesta: 15 px, para no cambiar cómo se ve.
4. **¿Las preferencias son por equipo** (mi propuesta) **o por usuario**?

---

# Spec (adición 12/oct): Menú de perfil

**Objetivo:** liberar espacio en la barra de arriba. El nombre, el rol y "Salir" se reemplazan por un **círculo con la inicial del usuario**.

> **Corrección 12/oct:** el botón **Ajustes** se queda en la barra, junto al círculo, por accesibilidad. El menú del círculo solo tiene **Administración** (solo admin) y **Cerrar sesión**.

**Comportamiento:**
- Tocar el círculo abre un menú con:
  - nombre, correo y rol;
  - **Administración** (solo Administrador: usuarios, permisos, correos y respaldo);
  - **Cerrar sesión**.
- Igual en la vista completa y en Modo piso. En Modo piso, el interruptor del Administrador se queda en la barra.
- El menú se cierra al tocar fuera, con Esc o al elegir una opción, y el foco regresa al círculo. Las flechas arriba y abajo recorren las opciones.
- Abrir el menú no vuelve a dibujar la pantalla ni borra lo capturado.

**Criterios de éxito:**
- La barra de arriba muestra el buscador, **Ajustes** y el círculo; ya no muestra rol ni Salir.
- El menú cabe en pantalla en 390 y 1440 px.
- El Encargado de piso no ve "Administración".
- Cerrar sesión funciona desde los dos modos.
- Pruebas en `pruebas/menu_t.py`.
