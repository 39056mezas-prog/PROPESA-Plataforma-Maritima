# v1.52.0 · Empaque en tablet y pantallas medianas: hieleras como tarjetas angostas, una junto a otra (1 2 / 3 4 …).
# En celular y computadora grande siguen las columnas de 10 de arriba abajo (v1.48.0). Correr: python3 -I pruebas/v152_t.py → «TODO BIEN».
import os, sys, subprocess, time, socket
from playwright.sync_api import sync_playwright

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('PORT_V152', '8793'))
OUT = os.environ.get('SALIDA', '/tmp/v152_t')
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
const l='LT1';ST.R.push({id:'R-'+uidS(),lot:l,origin:'Proveedor X',tank:'T1',rdate:dLoc(),time:'08:00',date:fd(dLoc()),tn:[[1,S[1],300000]],final:null,closed:false});ST.B[l]=[];post('RECEPCION',l,S[1],300);
const o={id:uidN(),etd:dLoc(),lines:[{id:1,city:'PVG',cons:0,boxes:%d,kp:16}],sh:{}};ST.OR.push(o);shipFor(o,'PVG',0);save();window.__k=o.id+'.1';go('empacar:'+o.id+'.1');"""
# Posición de las tarjetas: ¿la 2 está a la derecha de la 1 (fila) o abajo (columna)?
POS = """(()=>{const r=[...document.querySelectorAll('tbody.pkv10 tr:not(.pkcolh):not(.pkear)')].slice(0,2).map(t=>t.getBoundingClientRect());
 const h=document.querySelector('tbody.pkv10 tr.pkcolh');return {n:r.length,side:r.length==2&&Math.abs(r[0].top-r[1].top)<4&&r[1].left>r[0].left,below:r.length==2&&r[1].top>r[0].top+10,
 w:r.length?r[0].width:0,hw:h?h.getBoundingClientRect().width:0,tw:document.querySelector('tbody.pkv10').getBoundingClientRect().width}})()"""

with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    def page(w, n, touch):
        pg = b.new_page(viewport={'width': w, 'height': 900}, has_touch=touch)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(f'http://127.0.0.1:{PORT}/index.html?modo=local'); pg.wait_for_timeout(500)
        pg.evaluate(SEED % n); pg.wait_for_timeout(600)
        x = pg.locator('[aria-label="Cerrar teclado"]:visible')
        if x.count(): x.first.click(); pg.wait_for_timeout(300)
        return pg

    print('1 · Tablet y pantallas medianas: una junto a otra')
    for w in (768, 820, 1024, 1160, 1280):
        pg = page(w, 8, True); d = pg.evaluate(POS)
        ok(d['side'] and d['w'] < d['tw'] * 0.6, f'{w} px: la hielera 2 va a la derecha de la 1 y la tarjeta es angosta ({int(d["w"])} de {int(d["tw"])} px)')
        ok(abs(d['hw'] - d['tw']) < 2, f'{w} px: el encabezado «1–8» va a todo lo ancho')
        ok(pg.evaluate("document.documentElement.scrollWidth-innerWidth") <= 1, f'{w} px: sin desborde')
        if w == 1024: pg.screenshot(path=f'{OUT}/v152_1024.png')
        pg.close()

    print('2 · Celular y computadora grande: columnas de 10 como antes')
    for w in (390, 1440):
        pg = page(w, 8, w < 1000); d = pg.evaluate(POS)
        ok(d['below'], f'{w} px: la hielera 2 va abajo de la 1')
        pg.close()

    print('3 · Con el teclado abierto y 60 hieleras')
    pg = page(1024, 60, True)
    pg.click('[data-pkkp], .pkkpb') if pg.locator('.pkkpb').count() else None
    pg.wait_for_timeout(300)
    d = pg.evaluate(POS)
    ok(d['side'], 'Con el teclado abierto siguen dos por renglón')
    hs = pg.evaluate("[...document.querySelectorAll('tbody.pkv10 tr.pkcolh')].map(t=>t.textContent.trim())")
    ok(hs == ['1–10', '11–20', '21–30', '31–40', '41–50', '51–60'], 'Un encabezado por cada 10')
    for k in ['1', '2']: pg.locator('.kpk button', has_text=k).first.click()
    pg.locator('.kpc button', has_text='Rojo').first.click(); pg.wait_for_timeout(300)
    for k in ['9']: pg.locator('.kpk button', has_text=k).first.click()
    pg.locator('.kpc button', has_text='Verde').first.click(); pg.wait_for_timeout(300)
    pg.locator('.pkgo, [data-pk="addall"]').first.click(); pg.wait_for_timeout(500)
    bx = pg.evaluate("ordBoxes(ST.OR[0]).map(x=>[x.b.ps!=null?x.b.ps:null,x.b.c,x.b.k])")
    ok(len(bx) == 2 and bx[0][1] == 12 and bx[1][1] == 9, f'El teclado llena la 1 y luego la 2 ({bx})')
    pg.screenshot(path=f'{OUT}/v152_1024_teclado.png')
    pg.close()

    ok(not errs, 'Sin errores de JavaScript' + (': ' + '; '.join(errs) if errs else ''))
    b.close()
if srv: srv.terminate()
print('TODO BIEN' if not MAL else f'FALLAS: {len(MAL)}')
sys.exit(1 if MAL else 0)
