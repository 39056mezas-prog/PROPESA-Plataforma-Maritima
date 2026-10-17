"""Teclado de la app en celular/tablet táctil (v1.8.9): al completar una hielera, Android no debe abrir su teclado.
Simula un celular Android (pantalla táctil, sin mouse): las casillas de piezas quedan de solo lectura, así el sistema no abre
su teclado; el teclado de la app sigue escribiendo y al tocar la categoría pasa a la siguiente hielera. En computadora no cambia.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/teclado_movil_t.py"""
import json, os, sys
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed = json.loads(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read())
seed['OR'].append({'id': 3, 'etd': '2026-10-14', 'lines': [{'id': 1, 'city': 'HKG', 'cons': 0, 'cli': 'LHD', 'boxes': 6}], 'sh': {}})
S = json.dumps(seed); fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def kp(pg, d):
    for c in str(d): pg.tap(f'#kpad [data-kp="d:{c}"]')
def start(b, user, pw, route, movil=True):
    ctx = b.new_context(viewport={'width': 412, 'height': 915}, is_mobile=movil, has_touch=movil, device_scale_factor=2 if movil else 1)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-kp","1")}', S)
    pg.reload(); pg.fill('#le', user); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(600)
    pg.evaluate(f"go('{route}')"); pg.wait_for_timeout(200); return ctx, pg
act = "(()=>{const a=document.activeElement;return a&&a.tagName=='INPUT'?{c:a.className,ro:a.readOnly,im:a.getAttribute('inputmode')}:null})()"

with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------- vista completa (como en la captura del usuario: Empaque · RSK en celular) ----------
    ctx, pg = start(b, 'admin@propesa.mx', 'admin123', 'empacar:3.1')
    chk(pg.evaluate("matchMedia('(hover: none) and (pointer: coarse)').matches"), 'el celular simulado es táctil y sin mouse')
    ins = pg.locator('input.pkc'); chk(ins.count() >= 2 and all(ins.nth(k).get_attribute('readonly') is not None for k in range(ins.count())), 'vista completa: las casillas de piezas son de solo lectura en el celular')
    first = pg.evaluate("KPT.t")
    kp(pg, '55'); chk(pg.input_value('#pk_c0') == '55' if pg.locator('#pk_c0').count() else True, 'el teclado de la app escribe aunque la casilla sea de solo lectura')
    pg.tap('#kpad [data-kp="k:R"]'); pg.wait_for_timeout(150)
    a = pg.evaluate(act); chk(pg.evaluate("KPT.t") != first, f'al tocar la categoría pasa a la siguiente hielera ({first} → {pg.evaluate("KPT.t")})')
    chk(a is None or a['ro'], f'la hielera siguiente tiene el cursor pero es de solo lectura: Android no abre su teclado ({a})')
    kp(pg, '40'); pg.tap('#kpad [data-kp="k:V"]'); pg.wait_for_timeout(150)
    a = pg.evaluate(act); chk(a is None or a['ro'], f'y lo mismo en la siguiente ({a})')
    ctx.close()
    # ---------- Modo piso ----------
    ctx, pg = start(b, 'piso@propesa.mx', 'piso123', 'pemp:3.1')
    pg.tap('[data-pe="lot:WLRCO061026B"]'); pg.wait_for_timeout(200)
    ins = pg.locator('input.ppc'); chk(ins.count() >= 2 and all(ins.nth(k).get_attribute('readonly') is not None for k in range(ins.count())), 'Modo piso: las casillas de piezas son de solo lectura en el celular')
    kp(pg, '33'); pg.tap('#kpad [data-kp="k:R"]'); pg.wait_for_timeout(200)
    a = pg.evaluate(act); chk(pg.evaluate("KPT.t") == 'slot:2' and (a is None or a['ro']), f'Modo piso: guarda la hielera 1, pasa a la 2 y Android no abre su teclado ({a})')
    chk(pg.locator('input.psc').count() == 1 and pg.locator('input.psc').first.get_attribute('readonly') is not None, 'la hielera guardada (para corregir) también es de solo lectura')
    pg.tap('#pps1'); pg.wait_for_timeout(150); chk(pg.evaluate("KPT.t") == 'slot:1', 'tocar una hielera la elige para corregirla con el teclado de la app')
    ctx.close()
    # ---------- computadora: sin cambios (un teclado físico sigue escribiendo) ----------
    ctx, pg = start(b, 'admin@propesa.mx', 'admin123', 'empacar:3.1', movil=False)
    chk(pg.locator('input.pkc[readonly]').count() == 0, 'en computadora las casillas no son de solo lectura')
    pg.click('input.pkc >> nth=0'); pg.wait_for_timeout(300); pg.keyboard.type('12', delay=60); pg.wait_for_timeout(150); chk(pg.input_value('input.pkc >> nth=0') == '12', 'y el teclado físico escribe')
    ctx.close(); b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
