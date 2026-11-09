"""v1.19.0 · Maquilas separadas (pedido del usuario, 26/oct/2026).
1) Modo local: el Administrador entra al Panel general; el logo abre «Cambiar de maquila»; cada maquila tiene sus lotes, órdenes y
   embarques (el mismo código de lote puede estar en dos maquilas); lo compartido (proveedores, temperatura) se ve en todas;
   Administración → Maquilas (agregar, renombrar, ocultar); respaldo con todas las maquilas; recargar conserva la maquila;
   Modo piso también cambia de maquila; sin desbordes en 390/820/1440 px, claro y oscuro, texto de 20 px.
2) Base de mentira, dos equipos: lo que A captura en Abel le llega a B solo en Abel (registro con prefijo 'q2:'); PROPESA conserva
   sus claves de siempre; los compradores (D/disp) solo cuentan PROPESA.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/maquilas_t.py"""
import os, sys, json, time, subprocess, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recep import recibir
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
APP = BASE.split('?')[0]
MOCK = 'http://127.0.0.1:8794'
OUT = os.environ.get('OUT', '/tmp/propesa-pruebas'); os.makedirs(OUT, exist_ok=True)
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def until(pg, js, t=12):
    end = time.time() + t
    while time.time() < end:
        try:
            if pg.evaluate(js): return True
        except Exception: pass
        time.sleep(0.25)
    return False
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',role:'piso',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
def login(pg, em, pw='x'):
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def new_lot(pg, code, kgs=(100, 200, 300, 400)):
    recibir(pg, code, pv='1', kz=kgs, tt='58')
def pick(pg, name):  # toca el logo y elige la maquila por nombre
    pg.locator('[data-mq]').first.click(); pg.wait_for_timeout(100)
    pg.locator('#mqmenu [data-mqgo]', has_text=name).first.click(); pg.wait_for_timeout(150)
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")
LOTS = "JSON.stringify(ST.R.map(r=>r.lot))"

srv = subprocess.Popen([sys.executable, '-I', os.path.join(ROOT, 'pruebas', 'supabase_falso.py'), '8794'])
def mock(path, post=False):
    r = urllib.request.urlopen(urllib.request.Request(MOCK + path, data=b'{}' if post else None, method='POST' if post else 'GET'))
    return json.loads(r.read() or b'null')
for _ in range(50):
    try: mock('/__reset', True); break
    except Exception: time.sleep(0.1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        # ---------------- 1) modo local ----------------
        pg = b.new_page(viewport={'width': 1440, 'height': 900})
        pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
        pg.on('dialog', lambda d: d.accept())
        pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx')
        chk(pg.evaluate("V.v") == 'inicio', 'el Administrador entra al Centro de operaciones (v1.39.0)')
        pg.click('.sb [data-mq]'); pg.click('#mqmenu [data-mqgo="general"]'); pg.wait_for_timeout(150); chk(pg.evaluate("V.v") == 'general' and 'Panel general' in pg.inner_text('main') and pg.locator('.sb [data-go=general]').count() == 0, 'el Panel general se abre desde el selector de maquila (v1.34.0: ya no va en el menú)')
        chk(pg.locator('.sb button.mqn').inner_text().startswith('Todas las maquilas'), 'en el Panel general el logo dice «Todas las maquilas»')
        txt = pg.inner_text('main')
        chk(all(n in txt for n in ['PROPESA', 'Abel', 'David', 'Luis Arce']), 'el Panel general enseña las 4 maquilas')
        pg.locator('.sb [data-mq]').click(); pg.wait_for_timeout(100)
        items = pg.eval_on_selector_all('#mqmenu [data-mqgo]', 'e=>e.map(x=>x.innerText.split("\\n")[1]||x.innerText)')
        chk(pg.locator('#mqmenu .pmbox').is_visible() and len(items) == 5, 'el logo abre «Cambiar de maquila» con Panel general y 4 maquilas')
        hs = pg.eval_on_selector_all('#mqmenu [data-mqgo]', 'e=>e.map(x=>x.getBoundingClientRect().height)')
        chk(min(hs) >= 44, 'opciones del menú de 44 px o más')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(80)
        chk(pg.locator('#mqmenu').is_hidden(), 'Esc cierra el menú')
        pick(pg, 'PROPESA'); chk(pg.evaluate("V.v") == 'inicio' and pg.evaluate("MQ") == 1, 'elegir PROPESA abre su Panel')
        chk('PROPESA' in pg.locator('.sb button.mqn').inner_text(), 'el logo dice en qué maquila estás')
        chk(pg.locator('.sb .lgb svg').count() >= 1 and pg.locator('.sb .mqlt').count() == 0, 'en PROPESA el menú lleva el logo de PROPESA')
        new_lot(pg, 'WLRCO170926', (500, 100, 0, 0))
        pick(pg, 'Abel'); chk(pg.evaluate("MQ") == 2 and pg.evaluate("ST.R.length") == 0, 'Abel empieza sin lotes (no ve los de PROPESA)')
        new_lot(pg, 'WLRCO170926', (300, 0, 0, 0))
        chk(pg.locator('.sb .mqlt b').inner_text() == 'Abel' and pg.locator('.sb .lgb .mqb').count() == 1, 'en Abel su logotipo (emblema + «MAQUILA Abel») va en lugar del logo de PROPESA')
        chk(pg.evaluate(LOTS) == '["WLRCO170926"]' and abs(pg.evaluate("bal('WLRCO170926')") - 300000) < 1, 'Abel acepta el mismo código de lote con sus propios kilos')
        chk(pg.evaluate("STX[1].R.length") == 1 and pg.evaluate("STX[1].L.filter(x=>x.type=='RECEPCION').reduce((a,x)=>a+x.m,0)") == 600000, 'PROPESA conserva su lote y sus 600 kg')
        # proveedores y temperatura compartidos
        pg.evaluate("ST.T.push({id:uidN(),t:'2026-10-26T08:00',tank:'T2',a:57,s:null,p:null,by:'Ana Torres'});save()")
        pick(pg, 'David'); chk(pg.evaluate("ST.T.some(x=>x.tank=='T2'&&x.a==57)"), 'la temperatura de los tanques es la misma en todas las maquilas')
        chk(pg.evaluate("ST.R.length") == 0 and pg.evaluate("ST.OR.length") == 0, 'David tampoco ve lotes ni órdenes de otras')
        # Panel general suma todo
        pg.evaluate("go('general')"); pg.wait_for_timeout(100)
        chk(pg.locator('.sb .lgb svg').count() >= 1 and pg.locator('.sb .mqlt').count() == 0, 'en el Panel general vuelve el logo de PROPESA')
        rows = pg.eval_on_selector_all('.mqt tbody tr', 'e=>e.map(x=>x.innerText)')
        chk(any('PROPESA' in r and '600' in r for r in rows) and any('Abel' in r and '300' in r for r in rows) and any('Total' in r and '900' in r for r in rows), 'Panel general: PROPESA 600, Abel 300, total 900 kg')
        chk(any(r.startswith('T1') for r in rows), 'Panel general: tabla de tanques con las maquilas en columnas')
        pg.locator('.mqt [data-mqgo="2"]').click(); pg.wait_for_timeout(100)
        chk(pg.evaluate("MQ") == 2 and pg.evaluate("V.v") == 'inicio', '«Entrar ›» abre esa maquila')
        # recargar conserva
        pg.reload(); pg.wait_for_timeout(400)
        chk(pg.evaluate("MQ") == 2 and pg.evaluate(LOTS) == '["WLRCO170926"]' and pg.evaluate("STX[1]&&STX[1].R.length") == 1, 'recargar conserva la maquila abierta y los datos de todas')
        # v1.40.0: Administración ya no tiene pestaña Maquilas (usuario: «no agregar ni quitar maquilas», «quítame toda esa pestaña»)
        pg.evaluate("go('admin:mq')"); pg.wait_for_timeout(100)
        chk(pg.locator('[data-adt=mq]').count() == 0 and pg.locator('#mqs').count() == 0 and pg.locator('[data-mqa]').count() == 0, 'Administración ya no tiene pestaña Maquilas (ni agregar ni ocultar)')
        chk('+ Nueva maquila' not in pg.inner_text('#app'), 'ya no hay «+ Nueva maquila»')
        pg.evaluate("ST.MQL=mqAll().map(q=>({...q})).concat([{id:uidN(),n:'Cooperativa Norte',off:true}]);save();render()")  # alta a mano en la base
        pg.locator('.sb [data-mq]').click(); pg.wait_for_timeout(80)
        chk('Cooperativa Norte' not in pg.inner_text('#mqmenu'), 'una maquila oculta (en la base) no sale en el menú')
        pg.keyboard.press('Escape')
        # respaldo con todas las maquilas
        dump = pg.evaluate("JSON.stringify(mqDump())")
        pg.evaluate("ST.R=[];ST.L=[];ST.B={};STX={};save()")
        pg.evaluate("go('admin:dat')"); pg.wait_for_timeout(80)  # v1.35.0: el respaldo está en «Informes y respaldo»
        with pg.expect_file_chooser() as fc: pg.locator('input[data-bk=up]').first.evaluate('e=>e.click()')
        fp = os.path.join(OUT, 'mq_respaldo.json'); open(fp, 'w').write(dump); fc.value.set_files(fp); pg.wait_for_timeout(300)
        chk(pg.evaluate("MQ") == 2 and pg.evaluate(LOTS) == '["WLRCO170926"]' and pg.evaluate("STX[1]&&STX[1].R[0].lot") == 'WLRCO170926', 'restaurar un respaldo regresa todas las maquilas')
        chk(pg.evaluate("(()=>{const d=JSON.parse(%s);return !!d._X&&d._MQ==2})()" % json.dumps(dump)), 'el respaldo trae las otras maquilas (_X) y la abierta (_MQ)')
        # Modo piso cambia de maquila (Encargado de piso no tiene Panel general)
        pg.evaluate("me=null;render()"); pg.wait_for_timeout(100); login(pg, 'piso@propesa.mx')
        chk(pg.evaluate("PISO") and pg.evaluate("V.v") == 'piso', 'el Encargado de piso entra a Modo piso')
        pg.locator('.phd [data-mq]').click(); pg.wait_for_timeout(80)
        chk('Panel general' not in pg.inner_text('#mqmenu'), 'Modo piso: el menú no ofrece el Panel general')
        chk(pg.locator('.phd .mqlt b').inner_text() == 'Abel', 'Modo piso: en Abel el encabezado lleva su logotipo en lugar del logo')
        pg.locator('#mqmenu [data-mqgo="1"]').click(); pg.wait_for_timeout(120)
        chk(pg.evaluate("MQ") == 1 and pg.evaluate("V.v") == 'piso' and 'PROPESA' in pg.locator('.phd .mqn').inner_text(), 'en Modo piso se cambia a PROPESA y el encabezado lo dice')
        pg.evaluate("go('general')"); pg.wait_for_timeout(80)
        chk(pg.evaluate("V.v") != 'general', 'el Encargado de piso no puede abrir el Panel general')
        # vistas
        pg.evaluate("me=null;setPiso(false);render()"); login(pg, 'admin@propesa.mx')
        for w, h, theme, fs in [(1440, 900, 'light', 17), (820, 1180, 'dark', 20), (390, 844, 'light', 20)]:
            pg.set_viewport_size({'width': w, 'height': h}); pg.evaluate(f"localStorage.setItem('propesa-theme','{theme}');localStorage.setItem('propesa-fs','{fs}');applyPrefs&&applyPrefs()")
            pg.evaluate("go('general')"); pg.wait_for_timeout(150)
            chk(not overflow(pg), f'Panel general sin scroll de lado en {w} px ({theme}, {fs} px)')
            pg.screenshot(path=os.path.join(OUT, f'mq_general_{w}.png'))
            if w == 390: pg.click('[data-sb="1"]'); pg.wait_for_timeout(150)
            pg.locator('.sb [data-mq]').click(); pg.wait_for_timeout(100)
            bx = pg.locator('#mqmenu .pmbox').bounding_box()
            chk(bx and bx['x'] >= 0 and bx['x'] + bx['width'] <= w + 1, f'el menú de maquilas cabe en {w} px')
            pg.screenshot(path=os.path.join(OUT, f'mq_menu_{w}.png')); pg.keyboard.press('Escape')
            pg.evaluate("go('admin:cat')"); pg.wait_for_timeout(100); chk(not overflow(pg), f'Administración sin scroll de lado en {w} px')
        pg.close()

        # ---------------- 2) base de mentira, dos equipos ----------------
        INIT = "window.PROPESA_SB={url:'%s',key:'clave-publica-de-prueba'};try{localStorage.setItem('propesa-kp','0')}catch(e){}" % MOCK
        def device(name):
            ctx = b.new_context(viewport={'width': 1180, 'height': 820}); ctx.add_init_script(INIT); q = ctx.new_page()
            q.on('pageerror', lambda e: errs.append(name + ' JS ' + str(e))); q.on('dialog', lambda d: d.accept()); q.goto(APP); return ctx, q
        ca, A = device('A'); cb, B = device('B')
        for q, em, pw in [(A, 'admin@propesa.mx', 'clave-admin1'), (B, 'admin2@propesa.mx', 'clave-admin2')]:
            q.fill('#le', em); q.fill('#lp', pw); q.click('[data-a=lg]'); until(q, "!!me&&!!document.querySelector('.sb')")
        chk(A.evaluate("V.v") == 'inicio', 'base compartida: el Administrador entra al Centro de operaciones (v1.39.0)')
        pick(A, 'PROPESA'); new_lot(A, 'WLRCO200926', (100, 0, 0, 0))
        pick(A, 'Abel'); new_lot(A, 'WLRCO200926', (250, 0, 0, 0))
        chk(until(A, "outN()==0", 15), 'A sube sus cambios')
        keys = [k for k in mock('/__estado')['records'] if 'WLRCO200926' in k] if 'records' in mock('/__estado') else None
        if keys is None:
            st = mock('/__estado'); keys = [k for k in json.dumps(st).split('"') if 'WLRCO200926' in k and '/' in k]
        chk('R/WLRCO200926' in keys and 'q2:R/WLRCO200926' in keys, "en la base: PROPESA con su clave de siempre y Abel con prefijo 'q2:'")
        chk(until(B, "STX[2]&&STX[2].R.some(r=>r.lot=='WLRCO200926')||MQ==2&&ST.R.some(r=>r.lot=='WLRCO200926')", 15), 'el lote de Abel le llega a B')
        pick(B, 'PROPESA')
        chk(B.evaluate("ST.R.length") == 1 and abs(B.evaluate("bal('WLRCO200926')") - 100000) < 1, 'en B, PROPESA ve solo su lote de 100 kg')
        pick(B, 'Abel')
        chk(B.evaluate("ST.R.length") == 1 and abs(B.evaluate("bal('WLRCO200926')") - 250000) < 1, 'en B, Abel ve solo su lote de 250 kg')
        disp = mock('/__estado')
        chk(until(A, "(()=>{const d=SHW.get('D/disp');return d&&d[1].z[0]==100000})()", 10), 'compradores: la hoja D/disp solo cuenta PROPESA (100 kg, no 350)')
        # cambio en Abel desde B llega a A aunque A esté en PROPESA
        pick(A, 'PROPESA'); new_lot(B, 'WLRCO210926', (40, 0, 0, 0))
        chk(until(A, "!!STX[2]&&STX[2].R.some(r=>r.lot=='WLRCO210926')", 15) and A.evaluate("ST.R.every(r=>r.lot!='WLRCO210926')"), 'lo nuevo de Abel le llega a A sin mezclarse con PROPESA')
        A.reload(); until(A, "!!me", 10); A.wait_for_timeout(600)
        chk(A.evaluate("STX[2]&&STX[2].R.length") == 2 or A.evaluate("MQ==2&&ST.R.length==2"), 'al recargar, la copia del equipo conserva las otras maquilas')
        ca.close(); cb.close()
        b.close()
finally:
    srv.terminate()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
