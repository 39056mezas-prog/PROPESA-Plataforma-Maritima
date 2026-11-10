"""Administración → Historial de cambios (v1.16.0): quién, cuándo y qué valor cambió, últimos 30 días.
Usa el Supabase de mentira (pruebas/supabase_falso.py), que guarda la versión anterior como el trigger real.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/historial_t.py"""
import os, sys, json, time, subprocess, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recep import recibir
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.environ.get('APP', 'http://localhost:8765/index.html')
MOCK = 'http://127.0.0.1:8793'
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def mock(path, post=False):
    r = urllib.request.urlopen(urllib.request.Request(MOCK + path, data=b'{}' if post else None, method='POST' if post else 'GET'))
    return json.loads(r.read() or b'null')
def until(pg, js, t=12):
    end = time.time() + t
    while time.time() < end:
        try:
            if pg.evaluate(js): return True
        except Exception: pass
        time.sleep(0.25)
    return False
def login(pg, em, pw):
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]')
    return until(pg, "!!me&&!!document.querySelector('.sb,.pshell,[data-avatar]')")
def new_lot(pg, code):
    recibir(pg, code, pv='1', kz=['100']*4, tt='58')
ROWS = "[...document.querySelectorAll('#hist tbody tr')].map(t=>[...t.cells].map(c=>c.innerText.trim()))"

srv = subprocess.Popen([sys.executable, '-I', os.path.join(ROOT, 'pruebas', 'supabase_falso.py'), '8793'])
for _ in range(50):
    try: mock('/__reset', True); break
    except Exception: time.sleep(0.1)
INIT = "window.PROPESA_SB={url:'%s',key:'clave-publica-de-prueba'};try{localStorage.setItem('propesa-kp','0')}catch(e){}" % MOCK
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        def device(name):
            ctx = b.new_context(viewport={'width': 1440, 'height': 900}); ctx.add_init_script(INIT); pg = ctx.new_page()
            pg.on('pageerror', lambda e: errs.append(name + ' JS ' + str(e))); pg.on('dialog', lambda d: d.accept())
            pg.goto(APP); return ctx, pg
        cp, P = device('Piso'); ca, A = device('Admin')
        chk(login(P, 'piso@propesa.mx', 'clave-piso1'), 'entra Piso')
        new_lot(P, 'WLRHIS231026')
        chk(until(P, "!outN()"), 'Piso sube su entrada')
        chk(login(A, 'admin@propesa.mx', 'clave-admin1'), 'entra el Administrador')
        chk(until(A, "ST.R.some(r=>r.lot=='WLRHIS231026')"), 'el Administrador recibe la entrada de Piso')
        A.evaluate("ST.R.find(r=>r.lot=='WLRHIS231026').tpx=61;save()")
        A.evaluate("ST.T=[{id:uidN(),t:'2026-10-23T08:00',tank:'T1',a:58,s:57,p:59,by:'Ana Torres'}];save()")
        chk(until(A, "!outN()"), 'sube el cambio y una lectura de temperatura')
        A.evaluate("ST.T=[];save()"); chk(until(A, "!outN()"), 'borra la lectura')

        A.evaluate("go('admin:dat')")
        chk(A.locator('#hist').count() == 1 and 'Historial de cambios' in A.inner_text('#hist'), 'Administración tiene «Historial de cambios»')
        chk(A.locator('#hist table').count() == 0, 'no pide nada a la base hasta tocar el botón')
        A.click('[data-hc]'); chk(until(A, "!!document.querySelector('#hist table')"), '«Ver cambios recientes» carga la lista')
        r = A.evaluate(ROWS); print(r)
        txt = json.dumps(r, ensure_ascii=False)
        chk(r and r[0][1] == 'Ana Torres' and r[0][2].startswith('Borró') and 'Temperatura · T1' in r[0][2], 'lo más reciente arriba: Ana Torres borró la lectura de T1')
        chk(any(x[1] == 'Ana Torres' and x[2] == 'Cambió Lote WLRHIS231026' and 'Temp. producto máx.: 60 → 61' in x[3] for x in r), 'Cambió Lote …: «Temp. producto máx.: 60 → 61», con quién')
        chk(any(x[1] == 'Luis Meza' and x[2] == 'Creó Lote WLRHIS231026' for x in r), 'Creó Lote …: lo hizo Luis Meza (Piso)')
        chk(all(len(x) == 4 and x[0] for x in r), 'cada renglón trae cuándo, quién, qué y el cambio')
        chk('D/disp' not in txt and 'disp' not in txt.lower(), 'la hoja de disponibilidad (la calcula la app) no sale en la lista')
        chk(A.inner_text('[data-hc]') == 'Actualizar', 'el botón cambia a «Actualizar»')
        chk(A.evaluate("hcLbl('B/1',{lot:'X'})") == 'Hielera · lote X' and A.evaluate("hcDiff({c:20,k:'R'},{c:21,k:'R'},'B')") == ['Piezas vivas: 20 → 21'], 'hieleras: «Piezas vivas: 20 → 21»')
        chk(A.evaluate("hcDiff({c:[]},{c:[[1,2,3]]},'P')")[0].startswith('Conceptos de peso'), 'en embarques el mismo campo se llama distinto')
        chk(A.evaluate("hcVal('x'.repeat(80)).length") == 60, 'los valores largos se recortan')

        r = P.evaluate("sbPost('/rest/v1/rpc/cambios',{lim:200})"); chk(r == [], 'Piso pidiéndolo directo a la base no recibe nada')

        A.route('**/rest/v1/rpc/cambios', lambda rt: rt.abort()); A.click('[data-hc]')
        chk(until(A, "document.querySelector('#hist .er')&&document.querySelector('#hist .er').innerText.includes('No hay conexión')"), 'sin internet: aviso claro')
        A.unroute('**/rest/v1/rpc/cambios'); A.click('[data-hc]'); chk(until(A, "!!document.querySelector('#hist table')&&!document.querySelector('#hist .er')"), 'con internet otra vez vuelve a cargar')

        for w in (1440, 820, 390):
            A.set_viewport_size({'width': w, 'height': 900}); A.evaluate("document.documentElement.style.setProperty('--app-font-size','20px');render()")
            chk(A.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{w} px con texto «Muy grande»: sin desborde de la página')
        chk(A.evaluate("document.querySelector('[data-hc]').getBoundingClientRect().height") >= 44, 'botón de 44 px o más')
        A.evaluate("document.documentElement.dataset.theme='dark'"); chk(A.locator('#hist table').is_visible(), 'tema oscuro: se ve la lista')
        A.evaluate("document.getElementById('hist').scrollIntoView()"); A.screenshot(path='/tmp/propesa_historial.png')

        cl = b.new_context(); L = cl.new_page(); L.on('pageerror', lambda e: errs.append('local JS ' + str(e)))
        L.goto(APP + '?modo=local'); L.evaluate("localStorage.setItem('propesa-v4',JSON.stringify({E0:1,RN:120,R:[],L:[],B:{},OR:[],P:[],O:[],M:{},T:[],U:[{id:1,name:'Ana',email:'a@a.mx',role:'admin',notify:true}]}))")
        chk(L.evaluate("!CLOUD&&histCard()===''"), 'sin base compartida (modo local) no se muestra')
        for c in (cp, ca, cl): c.close()
        b.close()
finally:
    srv.terminate()
for e in errs: print('FAIL ' + e)
print('\n%d fallas' % (len(fails) + len(errs)))
sys.exit(1 if fails or errs else 0)
