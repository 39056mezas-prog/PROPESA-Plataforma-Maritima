# v1.53.0 / v1.55.0 · Planta 3D fuera del inicio de Modo piso: botón «Tanques» con su propio panel, que desde la v1.55.0 es como el Centro de operaciones; la planta en un plegable (Centro y panel).
# Correr: python3 -I pruebas/v153_t.py → «TODO BIEN».
import os, sys, subprocess, time, socket
from playwright.sync_api import sync_playwright

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('PORT_V153', '8794'))
OUT = os.environ.get('SALIDA', '/tmp/v153_t')
os.makedirs(OUT, exist_ok=True)
def libre(p):
    with socket.socket() as s:
        return s.connect_ex(('127.0.0.1', p)) != 0
srv = None
if libre(PORT):
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT)], cwd=RAIZ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
MAL = []
def ok(c, t):
    print(('  ✔ ' if c else '  ✘ ') + t)
    if not c: MAL.append(t)

SEED = r"""
ST.U=[{id:1,name:'Admin',email:'admin@propesa.org',role:'admin',notify:true}];me=ST.U[0];
const l='LT1';ST.R.push({id:'R-'+uidS(),lot:l,origin:'Proveedor X',tank:'T1',rdate:dLoc(),time:'08:00',date:fd(dLoc()),tn:[[1,S[1],120000]],final:null,closed:false});ST.B[l]=[];post('RECEPCION',l,S[1],120);
save();"""
TQ = "document.querySelectorAll('.ct3, .tqm, .t3v').length"

with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    for w in (390, 768, 1024):
        print(f'· {w} px')
        pg = b.new_page(viewport={'width': w, 'height': 900}, has_touch=True)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(f'http://127.0.0.1:{PORT}/index.html?modo=local'); pg.wait_for_timeout(500)
        pg.evaluate(SEED); pg.evaluate("setPiso(true);go('piso')"); pg.wait_for_timeout(400)
        ok(pg.evaluate(TQ) == 0, 'Inicio de Modo piso sin planta ni tanques')
        gos = pg.evaluate("[...document.querySelectorAll('.pg .pt')].map(x=>x.dataset.go)")
        ok(gos[-2:] == ['temperatura', 'ptq'], f'«Tanques» va después de Temperatura ({gos})')
        ok('1 lote' in pg.locator('.pt[data-go="ptq"]').inner_text(), 'El botón dice cuántos lotes hay')
        ok(pg.evaluate("document.documentElement.scrollWidth-innerWidth") <= 1, 'Sin desborde en el inicio')
        pg.screenshot(path=f'{OUT}/piso_{w}.png', full_page=True)
        pg.click('.pt[data-go="ptq"]'); pg.wait_for_timeout(500)
        ok(pg.evaluate('V.v') == 'ptq' and 'Tanques' in pg.locator('.ptit').inner_text(), 'Abre su propio panel «Tanques»')
        ok(pg.locator('.ctk').count() == 4 and pg.locator('details[data-fold="ct-inv"]').count() == 1 and pg.locator('details[data-fold="ct-lot"]').count() == 1, 'Es como el Centro: 4 números, planta, inventario y plegables')
        gs = pg.evaluate("[...document.querySelectorAll('.ctk')].map(x=>x.dataset.go)")
        ok(gs[1:] == ['rtin', 'pemp', 'pcer'], f'Recibido → Registrar recepción, Hieleras → Empacar, Embarques → Cerrar embarque ({gs})')
        ok(pg.locator('[data-mqgo="general"]').count() == 0, 'Sin «Todas las maquilas» en Modo piso')
        ok(pg.locator('details[data-fold="ct-planta"][open]').count() == 1 and pg.evaluate("document.querySelectorAll('.tqm').length") == 6, 'La planta viene abierta con los 6 tanques')
        ok(pg.evaluate("document.querySelectorAll('.t3v').length") == 1, 'Trae la planta 3D')
        ok(pg.evaluate("document.documentElement.scrollWidth-innerWidth") <= 1, 'Sin desborde en el panel')
        pg.screenshot(path=f'{OUT}/ptq_{w}.png')
        pg.locator('details[data-fold="ct-planta"] > summary').click(); pg.wait_for_timeout(200)
        pg.evaluate("render()"); pg.wait_for_timeout(200)
        ok(pg.evaluate(TQ) == 0, 'Plegada: no se arma la planta')
        pg.locator('details[data-fold="ct-planta"] > summary').click(); pg.wait_for_timeout(400)
        ok(pg.evaluate("document.querySelectorAll('.tqm').length") == 6, 'Al abrirla otra vez regresa')
        pg.locator('.phd .back, .phd [data-back], .phd button').first.click(); pg.wait_for_timeout(400)
        ok(pg.evaluate('V.v') == 'piso', '«‹ Atrás» regresa al inicio de Modo piso')
        pg.evaluate("go('ptq');switchMode(false)"); pg.wait_for_timeout(500)
        ok(pg.evaluate('V.v') == 'inicio' and not pg.evaluate('PISO'), 'Al apagar Modo piso desde Tanques va al Centro')
        print('  Centro de operaciones')
        ok(pg.locator('details[data-fold="ct-planta"][open]').count() == 1 and pg.evaluate("document.querySelectorAll('.tqm').length") == 6, 'La planta viene abierta en un plegable')
        pg.locator('details[data-fold="ct-planta"] > summary').click(); pg.wait_for_timeout(200)
        pg.evaluate("render()"); pg.wait_for_timeout(200)
        ok(pg.evaluate(TQ) == 0, 'Se puede plegar y se queda plegada')
        ok(pg.evaluate("document.documentElement.scrollWidth-innerWidth") <= 1, 'Sin desborde en el Centro')
        pg.screenshot(path=f'{OUT}/centro_plegado_{w}.png')
        pg.close()
    ok(not errs, 'Sin errores de JavaScript' + (': ' + '; '.join(errs) if errs else ''))
    b.close()
if srv: srv.terminate()
print('TODO BIEN' if not MAL else f'FALLAS: {len(MAL)}')
sys.exit(1 if MAL else 0)
