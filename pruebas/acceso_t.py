"""v1.32.0–v1.32.1 · Pantalla de acceso: marca con vista previa de la app y botón «Iniciar sesión»; el formulario sale de lado. Uso: python3 -I pruebas/acceso_t.py"""
import os, sys, re, json
from playwright.sync_api import sync_playwright
import os,re
# v1.39.0: la versión sale del CHANGELOG (la de arriba) y debe ser la misma que APPV en index.html
_R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER=re.search(r'^## (\d+\.\d+\.\d+)',open(os.path.join(_R,'CHANGELOG.md'),encoding='utf8').read(),re.M).group(1)
assert "APPV='"+VER+"'" in open(os.path.join(_R,'index.html'),encoding='utf8').read(),'APPV en index.html no es la versión del CHANGELOG '+VER

BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local'); fails = []; errs = []  # modo local: nunca toca la base real
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
DEMO = re.compile(r'demo|simulad|sistema real|admin123|piso123|Ana Torres|Luis Meza|Q-22|provisional', re.I)
U = {'PK': 1, 'BN': 0, 'L': [], 'N': 0, 'R': [], 'B': {}, 'P': [], 'O': [], 'M': {}, 'OR': [], 'ORc': 1, 'E0': 1,
     'U': [{'id': 7, 'name': 'Jefe de planta', 'email': 'jefe@x.mx', 'role': 'admin', 'notify': True}]}
def abrir(b, w, h, fs=None, theme=None, datos=True):
    pg = b.new_page(viewport={'width': w, 'height': h}); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto(BASE); pg.evaluate('localStorage.clear()')
    if datos: pg.evaluate('d=>localStorage.setItem("propesa-v4",d)', json.dumps(U))
    if fs: pg.evaluate(f'localStorage.setItem("propesa-fs","{fs}")')
    if theme: pg.evaluate(f'localStorage.setItem("propesa-theme","{theme}")')
    pg.reload(); pg.wait_for_selector('#le' if datos else '#s0n'); return pg
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = abrir(b, 1440, 900)
    chk(pg.locator('.au.op').count() == 0 and pg.locator('.auo').is_visible() and 'Iniciar sesión' in pg.inner_text('.auo'), 'abre con la marca, la vista previa y el botón «Iniciar sesión» (el formulario guardado)')
    chk(pg.evaluate("document.querySelector('.aup').getBoundingClientRect().left") >= 1439, 'el correo y la contraseña esperan fuera de la pantalla, a la derecha')
    chk(pg.evaluate("document.documentElement.scrollHeight<=innerHeight+1"), 'sin desplazarse: todo cabe en la pantalla')
    pg.click('.auo')
    tr = pg.evaluate("document.querySelector('.aup').getAnimations().filter(a=>a.transitionProperty=='transform').map(a=>a.effect.getTiming().duration)")
    chk(tr and tr[0] >= 450, f'se ve deslizarse: el cajón tarda medio segundo en llegar ({tr} ms; antes 320 ms y casi todo en el primer cuadro)')
    pg.evaluate("Promise.allSettled(document.getAnimations().map(a=>a.finished))")
    chk(pg.locator('.au.op').count() == 1 and pg.evaluate("Math.round(document.querySelector('.aup').getBoundingClientRect().right)") == 1440 and pg.get_attribute('.auo', 'aria-expanded') == 'true', 'el botón saca el formulario de lado')
    chk(pg.evaluate("document.activeElement.id") == 'le', 'al abrir queda listo para escribir el correo')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(450)
    chk(pg.locator('.au.op').count() == 0 and pg.evaluate("document.activeElement.classList.contains('auo')"), 'Escape lo guarda y regresa al botón')
    pg.click('.auo'); pg.wait_for_timeout(450); pg.click('.auc'); pg.wait_for_timeout(450); chk(pg.locator('.au.op').count() == 0, '✕ lo guarda')
    pg.click('.auo'); pg.wait_for_timeout(450); pg.mouse.click(200, 450); pg.wait_for_timeout(450); chk(pg.locator('.au.op').count() == 0, 'tocar afuera lo guarda')
    pg.focus('#le'); pg.wait_for_timeout(450); chk(pg.locator('.au.op').count() == 1, 'llegar al correo con el teclado (o el administrador de contraseñas) también lo abre')
    # v1.38.3: la planta de la vista previa es una imagen ya dibujada (acceso-planta.png); en CSS 3D eran ~300 capas y en
    # celulares con poca memoria la pantalla se quedaba gris hasta moverla. Las etiquetas y las placas siguen siendo texto.
    pg.wait_for_function("(()=>{const i=document.querySelector('.aum .mkimg');return i&&i.complete&&i.naturalWidth>0})()", timeout=5000)
    chk(pg.locator('.aum .mkimg').count() == 1 and pg.locator('.aum .t3w, .aum .t3f').count() == 0, 'la vista previa usa la imagen de la planta (nada de CSS 3D en el acceso)')
    chk(pg.evaluate("[...document.querySelectorAll('.aum *')].filter(e=>getComputedStyle(e).transformStyle=='preserve-3d').length") == 0, 'sin capas 3D en el acceso')
    chk(pg.locator('.aum .t3sign').count() == 6, 'con las placas TANQUE 1–6')
    box = pg.evaluate("(()=>{const i=document.querySelector('.aum .mkimg').getBoundingClientRect(),p=document.querySelector('.aum .mkp').getBoundingClientRect(),s=[...document.querySelectorAll('.aum .t3sign')].map(e=>e.getBoundingClientRect());return {img:i.width>200&&i.left>=p.left-1&&i.top>=p.top-1&&i.bottom<=p.bottom+1,signs:s.every(r=>r.left>=i.left-2&&r.right<=i.right+2&&r.top>=i.top-2&&r.bottom<=i.bottom+2)}})()")
    chk(box['img'] and box['signs'], f'la imagen queda dentro de la tarjeta y las placas caen sobre ella {box}')
    tags = pg.eval_on_selector_all('.aum .t3tag', 'e=>e.map(x=>x.innerText.split("\\n")[0])')
    chk(len(tags) == 5 and not any('Vacío' in t for t in tags) and any(t.startswith('T1 · ') and t.split(' · ')[1].split(' ')[1] in ('tina','tinas') and 'de 30' not in t for t in tags), f'v1.43.0: cada tanque dice solo sus tinas (sin «de 30»); el vacío (T5) sin etiqueta, solo su letrero; el vacío (T5) sin etiqueta, solo su letrero (v1.38.2) {tags}')
    chk(pg.locator('.t3v').count() == 0, 'no se arma la planta real en el acceso (solo el dibujo)')
    inside = pg.evaluate("(()=>{const a=document.querySelector('.aub').getBoundingClientRect();return [...document.querySelectorAll('.aum .t3tag')].every(e=>{const r=e.getBoundingClientRect();return r.right<=a.right+1&&r.left>=a.left})})()")
    chk(inside, 'todos los letreros de los tanques caben en el panel (nada cortado)')
    chk(pg.evaluate("getComputedStyle(document.querySelector('.aup')).backgroundColor") == 'rgb(255, 255, 255)', 'v1.32.1 · menos azul marino: el cajón del formulario es blanco')
    chk(pg.evaluate("getComputedStyle(document.querySelector('[data-a=lg]')).backgroundColor") == 'rgb(4, 114, 171)', 'botón Entrar azul océano (texto blanco)')
    chk(pg.locator('.aum a,.aum button,.aum input,.aum [tabindex]').count() == 0, 'la vista previa no tiene nada que se pueda enfocar')
    chk(pg.locator('h1').inner_text() == 'Iniciar sesión' and 'acceso por rol' in pg.inner_text('.aui').lower() and 'marítima' not in pg.inner_text('.au').lower(), 'título «Iniciar sesión» y el texto de siempre')
    chk('Versión ' + VER in pg.inner_text('.auft'), 'el pie muestra la versión ' + VER)
    chk(not DEMO.search(pg.inner_text('body')), 'sin rastros de demo en el acceso')
    # ver / ocultar contraseña
    pg.fill('#lp', 'Secreta123'); eye = pg.locator('[data-a=pwv][data-for=lp]')
    chk(eye.get_attribute('aria-label') == 'Mostrar contraseña' and pg.get_attribute('#lp', 'type') == 'password', 'la contraseña empieza oculta')
    eye.click(); chk(pg.get_attribute('#lp', 'type') == 'text' and eye.get_attribute('aria-pressed') == 'true' and eye.get_attribute('aria-label') == 'Ocultar contraseña', 'el ojo muestra la contraseña')
    chk(pg.input_value('#lp') == 'Secreta123' and pg.evaluate("document.activeElement.id") == 'lp', 'no borra lo escrito y regresa al campo')
    eye.click(); chk(pg.get_attribute('#lp', 'type') == 'password', 'el ojo la vuelve a ocultar')
    r = eye.bounding_box(); chk(r['width'] >= 44 and r['height'] >= 44, 'el ojo mide 44 px o más')
    # sigue entrando igual (botón y Enter)
    pg.fill('#le', 'nadie@x.mx'); pg.click('[data-a=lg]'); chk('incorrectos' in pg.inner_text('#lm'), 'correo equivocado: avisa')
    pg.fill('#le', 'jefe@x.mx'); pg.press('#lp', 'Enter'); chk(pg.locator('.sb').count() == 1 and pg.locator('.au').count() == 0, 'con Enter entra a la app')
    pg.close()
    # sin desbordes en los tamaños de siempre y con texto «Muy grande»
    for w, h, fs, th in [(390, 844, None, None), (820, 1180, None, None), (1180, 820, None, 'dark'), (1440, 900, '20', None), (390, 844, '20', 'dark')]:
        pg = abrir(b, w, h, fs, th)
        ov = pg.evaluate("document.documentElement.scrollWidth-innerWidth")
        vis = pg.locator('.aum').is_visible() and pg.locator('.auo').is_visible()
        chk(pg.evaluate("document.documentElement.scrollHeight<=innerHeight+1"), f'{w}×{h}: sin desplazarse')
        chk(ov <= 0, f'{w}×{h} {fs or ""} {th or ""}: sin desborde a lo ancho')
        chk(vis, f'{w}×{h}: vista previa y botón «Iniciar sesión» a la vista')
        bt = pg.locator('[data-a=lg]').bounding_box(); chk(bt['height'] >= 48, f'{w}×{h}: botón Entrar de 48 px o más')
        pg.close()
    # v1.32.1 · desde propesa.org (#entrar) el cajón sale solo, deslizándose, y la dirección queda limpia
    for w, h, th in [(1440, 900, None), (390, 844, 'dark')]:
        pg = b.new_page(viewport={'width': w, 'height': h}); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE); pg.evaluate('localStorage.clear()'); pg.evaluate('d=>localStorage.setItem("propesa-v4",d)', json.dumps(U))
        if th: pg.evaluate(f'localStorage.setItem("propesa-theme","{th}")')
        pg.goto(BASE + '#entrar'); pg.reload(); pg.wait_for_selector('#le')
        pg.wait_for_timeout(1000)
        chk(pg.locator('.au.op').count() == 1 and pg.evaluate("Math.round(document.querySelector('.aup').getBoundingClientRect().right)") == w, f'{w}: luego el cajón sale solo, sin tocar nada')
        chk(pg.evaluate("document.activeElement.id") == 'le', f'{w}: listo para escribir el correo')
        chk('#entrar' not in pg.url, f'{w}: la dirección queda sin #entrar (recargar no lo repite)')
        chk(pg.evaluate("getComputedStyle(document.querySelector('#le')).backgroundColor") == 'rgb(255, 255, 255)' and pg.evaluate("getComputedStyle(document.querySelector('.aui h1')).color") == 'rgb(11, 29, 89)', f'{w} {th or ""}: el cajón blanco se ve igual en tema oscuro')
        pg.fill('#le', 'jefe@x.mx'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); chk(pg.locator('.sb').count() == 1, f'{w}: entra con un solo clic en Entrar')
        pg.close()
    # sin animación de lado si el equipo pide menos movimiento: aparece con un fundido corto y sigue funcionando
    pg = b.new_page(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce'); pg.goto(BASE); pg.evaluate('d=>localStorage.setItem("propesa-v4",d)', json.dumps(U)); pg.reload(); pg.wait_for_selector('#le')
    chk(pg.evaluate("getComputedStyle(document.querySelector('.aup')).pointerEvents") == 'none', 'menos movimiento: el cajón cerrado no estorba los clics')
    pg.focus('#le'); pg.wait_for_timeout(300); chk(pg.locator('.au.op').count() == 1 and pg.evaluate("getComputedStyle(document.querySelector('.aup')).opacity") == '1' and pg.evaluate("getComputedStyle(document.querySelector('.aup')).transform") == 'none', 'menos movimiento: sin deslizarse, aparece y se puede llegar con el teclado')
    pg.close()
    # Configuración inicial usa la misma pantalla
    pg = abrir(b, 1440, 900, datos=False)
    chk(pg.locator('.au.op .aum').count() == 1 and pg.locator('h1').inner_text() == 'Configuración inicial', 'Configuración inicial usa la misma pantalla, con el formulario ya abierto')
    chk(pg.locator('[data-a=pwv]').count() == 2, 'las dos contraseñas traen su ojo')
    pg.fill('#s0n', 'María López'); pg.fill('#s0e', 'maria@propesa.com.mx'); pg.fill('#s0p', 'Langosta2026'); pg.fill('#s0q', 'Langosta2026')
    pg.click('[data-a=pwv][data-for=s0q]'); chk(pg.get_attribute('#s0q', 'type') == 'text' and pg.get_attribute('#s0p', 'type') == 'password', 'cada ojo muestra solo su campo')
    pg.press('#s0q', 'Enter'); chk(pg.locator('.sb').count() == 1, 'crea el Administrador y entra')
    b.close()
print('ERRS', errs); print('RESULTADO:', 'TODO BIEN' if not fails and not errs else f'{len(fails)} fallas'); sys.exit(1 if fails or errs else 0)
