# v1.54.0 · Inventario fuera del menú: plegable «Inventario» en el Centro de operaciones. Correr: python3 -I pruebas/v154_t.py → «TODO BIEN».
import subprocess,sys,time
from playwright.sync_api import sync_playwright
srv=subprocess.Popen([sys.executable,'-m','http.server','8797'],cwd=__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(.8)
SEED=r"""ST.U=[{id:1,name:'Admin',email:'admin@propesa.org',role:'admin',notify:true}];me=ST.U[0];
const l='LT1';ST.R.push({id:'R-'+uidS(),lot:l,origin:'Proveedor X',tank:'T1',rdate:dLoc(),time:'08:00',date:fd(dLoc()),tn:[[1,S[1],120000]],final:null,closed:false});ST.B[l]=[];post('RECEPCION',l,S[1],120);save();go('inicio')"""
errs=[];bad=[]
def ok(c,t):
    print(('  ✔ ' if c else '  ✘ ')+t)
    if not c: bad.append(t)
with sync_playwright() as p:
    b=p.chromium.launch()
    for w in (1280,768,390):
        pg=b.new_page(viewport={'width':w,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('http://127.0.0.1:8797/index.html?modo=local');pg.wait_for_timeout(500);pg.evaluate(SEED);pg.wait_for_timeout(400)
        ok(pg.locator('aside [data-go="inventario"]').count()==0,f'{w}: sin Inventario en el menú')
        d=pg.locator('details[data-fold="ct-inv"]')
        ok(d.count()==1 and d.get_attribute('open') is None and '120.0 kg' in d.inner_text(),f'{w}: plegable Inventario en el Centro, cerrado, con el total')
        d.locator('summary').click();pg.wait_for_timeout(300)
        ok('Talla' in d.inner_text() and '120.0 kg' in d.inner_text(),f'{w}: abre la tabla por talla y tanque')
        ok(pg.evaluate("document.documentElement.scrollWidth-innerWidth")<=1,f'{w}: sin desborde')
        pg.screenshot(path=f'/tmp/v154_{w}.png',full_page=True)
        pg.evaluate("for(const k in FOLD)delete FOLD[k];go('inventario')");pg.wait_for_timeout(300)
        ok(pg.evaluate('V.v')=='inicio' and pg.locator('details[data-fold="ct-inv"][open]').count()==1,f'{w}: la ruta vieja «inventario» abre el Centro con Inventario abierto')
        pg.close()
    ok(not errs,'Sin errores JS '+';'.join(errs))
srv.terminate();print('TODO BIEN' if not bad else 'FALLAS');sys.exit(1 if bad else 0)
