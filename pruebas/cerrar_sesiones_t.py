# v1.56.0 · Administración → Usuarios → «Cerrar sesiones» (la función usuarios lo acepta desde la v1.46.0).
# Simula la base compartida sin internet: cada llamada a Supabase la contesta esta prueba. Correr: python3 -I pruebas/cerrar_sesiones_t.py → «TODO BIEN».
# CHROME=/ruta/a/chrome para usar otro navegador.
import json, os, sys
from playwright.sync_api import sync_playwright
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = open(os.path.join(RAIZ, 'index.html'), encoding='utf-8').read()
APP = 'https://app.prueba.test/index.html'
SB = 'https://lktqwmfmdhusscudgflo.supabase.co'
ADM, PISO = '00000000-0000-0000-0000-00000000000a', '00000000-0000-0000-0000-00000000000b'
PERFILES = [{'id': ADM, 'name': 'Admin', 'email': 'admin@propesa.org', 'role': 'admin', 'notify': True, 'mq': []},
            {'id': PISO, 'name': 'Martha <b>', 'email': 'martha@propesa.org', 'role': 'piso', 'notify': False, 'mq': []}]
llamadas = []; falla = {'v': False}
def contesta(route):
    u, req = route.request.url, route.request
    if u.startswith(APP): return route.fulfill(status=200, headers={'Content-Type': 'text/html; charset=utf-8'}, body=HTML)
    if u.startswith(SB + '/functions/v1/usuarios'):
        b = json.loads(req.post_data or '{}'); llamadas.append(b)
        if falla['v']: return route.fulfill(status=400, headers={'Content-Type': 'application/json'}, body=json.dumps({'error': 'Ese usuario ya no existe.'}))
        return route.fulfill(status=200, headers={'Content-Type': 'application/json'}, body=json.dumps({'ok': True, 'sesiones': 2}))
    if u.startswith(SB + '/rest/v1/profiles'): return route.fulfill(status=200, headers={'Content-Type': 'application/json'}, body=json.dumps(PERFILES))
    if u.startswith(SB + '/rest/v1/rpc/'): return route.fulfill(status=200, headers={'Content-Type': 'application/json'}, body='[]')
    if u.startswith(SB): return route.fulfill(status=200, headers={'Content-Type': 'application/json'}, body='[]')
    return route.fulfill(status=404, body='')
bad = []; errs = []
def ok(c, t):
    print(('  ✔ ' if c else '  ✘ ') + t)
    if not c: bad.append(t)
with sync_playwright() as p:
    b = p.chromium.launch(**({'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {}))
    ctx = b.new_context(viewport={'width': 1280, 'height': 900})
    ctx.add_init_script("localStorage.setItem('propesa-sb',JSON.stringify({at:'tk',rt:'rt',exp:Date.now()+36e5,uid:'%s'}))" % ADM)
    ctx.route('**/*', contesta)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(APP); pg.wait_for_timeout(800)
    pg.evaluate("async()=>{SBS={at:'tk',rt:'rt',exp:Date.now()+36e5,uid:'%s'};await loadProfiles();me=ST.U.find(u=>u.id==='%s');render()}" % (ADM, ADM)); pg.wait_for_timeout(300)
    ok(pg.evaluate("CLOUD&&!!me&&me.role=='admin'&&ST.U.length==2"), 'entra como Administrador con la base simulada (perfiles leídos de la base)')
    pg.evaluate("ADT='usr';go('admin')"); pg.wait_for_timeout(400)
    ok(pg.locator(f'[data-cs="{ADM}"]').count() == 0, 'no sale «Cerrar sesiones» en tu propia cuenta')
    btn = pg.locator(f'[data-cs="{PISO}"]')
    ok(btn.count() == 1 and btn.inner_text() == 'Cerrar sesiones', 'sale «Cerrar sesiones» en la cuenta de piso')
    ok(btn.get_attribute('aria-label') == 'Cerrar la sesión de Martha <b> en todos sus equipos', 'el botón dice de quién es (lector de pantalla)')
    fila = pg.locator('tr', has=btn); orden = fila.locator('button').all_inner_texts()
    ok('&lt;b&gt;' in fila.locator('td').first.inner_html(), 'el nombre va escapado en la tabla')
    ok(orden == ['Editar', 'Cerrar sesiones', 'Eliminar'], f'orden de la fila: Editar · Cerrar sesiones · Eliminar ({orden})')
    btn.click(); pg.wait_for_timeout(300)
    si = pg.locator(f'[data-cs2="{PISO}"]')
    ok(si.count() == 1 and si.inner_text() == 'Sí, cerrar sesiones' and not llamadas, 'primero pide confirmar (todavía no llama a la función)')
    si.click(); pg.wait_for_timeout(600)
    ok(llamadas == [{'action': 'cerrar_sesiones', 'id': PISO}], f'llama a la función con la acción y la cuenta correctas ({llamadas})')
    t = pg.locator('#toast').inner_text()
    ok('Martha <b> tendrá que entrar otra vez' in t, f'avisa a quién y qué pasa ({t})')
    ok(pg.locator(f'[data-cs2="{PISO}"]').count() == 0, 'la confirmación se cierra')
    falla['v'] = True; llamadas.clear()
    pg.locator(f'[data-cs="{PISO}"]').click(); pg.wait_for_timeout(200); pg.locator(f'[data-cs2="{PISO}"]').click(); pg.wait_for_timeout(600)
    t = pg.locator('#toast').inner_text()
    ok('No se pudieron cerrar las sesiones: Ese usuario ya no existe.' in t, f'si la función falla, lo dice ({t})')
    ok(not errs, 'Sin errores JS ' + ';'.join(errs[:3]))
    b.close()
print('TODO BIEN' if not bad else 'FALLAS'); sys.exit(1 if bad else 0)
