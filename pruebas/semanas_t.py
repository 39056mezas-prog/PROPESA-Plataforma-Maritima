# v1.51.0 · «Semanas»: cada semana con sus recepciones, órdenes, embarques y correos (modo local, sin internet ni base real).
# Correr:  python3 -I pruebas/semanas_t.py  → debe terminar en «TODO BIEN».
import os, sys, subprocess, time, socket
from playwright.sync_api import sync_playwright

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('PORT_SEMANAS', '8792'))
OUT = os.environ.get('SALIDA', '/tmp/semanas_t')
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

# Esta semana: un lote con su correo, una orden con su embarque abierto y un correo que no salió.
# Hace 3 semanas: un lote. Hace 10 semanas: un lote (queda en «Ver historial»). Un correo de temperatura (sin lote ni orden).
SEED = r"""
ST.U=[{id:1,name:'Admin',email:'admin@propesa.org',role:'admin',notify:true}];me=ST.U[0];
const hoy=dLoc(),dd=n=>wkAdd(hoy,n),tx=d=>fd(d).slice(0,6)+d.slice(2,4)+', 09:00';
const lot=(l,d)=>{ST.R.push({id:'R-'+uidS(),lot:l,origin:'Proveedor X',tank:'T1',rdate:d,time:'08:00',date:fd(d),tn:[[1,S[1],30000]],final:null,closed:false});ST.B[l]=[];post('RECEPCION',l,S[1],30)};
lot('LHOY',hoy);lot('LANT',dd(-21));lot('LVIEJO',dd(-70));
const o={id:uidN(),etd:hoy,lines:[{id:1,city:'PVG',cons:0,boxes:3,kp:16}],sh:{}};ST.OR.push(o);
const i=shipFor(o,'PVG',0);ST.B.LHOY.push({c:10,k:'R',d:i,o:o.id+'.1',seq:uidN()});syncShipIdx(i);
const m=(ev,t,rf,ok,fs)=>ST.O.unshift({u:uidS(),ev,t,by:'Admin',subject:'x',to:['a@propesa.org'],body:'',cc:[],ar:ok?'conectandoensenada@gmail.com':'',fs,pk:[],rf,ok:ok?1:0,...(ok?{}:{er:'Sin internet'})});
m('rec',now(),['l:LHOY'],1,['Formato 02 · lote LHOY']);
m('ord',now(),['o:'+o.id],0,['Orden de empaque']);
m('temp',now(),[],1,['Monitoreo de temperatura']);
m('rec',tx(dd(-21)),['l:LANT'],1,['Formato 02 · lote LANT']);
save();window.__o=o.id;window.__i=i;go('semanas');"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 900})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{PORT}/index.html?modo=local')
    pg.wait_for_timeout(600)
    pg.evaluate(SEED)
    pg.wait_for_timeout(300)

    print('1 · Menú y pantalla')
    ok(pg.locator('aside [data-go="semanas"]').count() == 1, 'El menú trae «Semanas»')
    ok(pg.locator('aside [data-go="semanas"][aria-current="page"]').count() == 1, 'Queda marcado al abrirla')
    ok(pg.locator('h1', has_text='Semanas').count() == 1, 'Título «Semanas»')
    w = pg.evaluate("wkAll().map(w=>w.m)")
    cm = pg.evaluate("wkMon(dLoc())")
    ok(pg.locator('.wkl details.fold').count() == 2, 'Se ven 2 semanas (esta y la de hace 3); la de hace 10 no')
    ok(len(w) == 3, 'Hay 3 semanas con datos')
    ok(pg.evaluate("wkNo('2026-11-19')") == 47 and pg.evaluate("wkNo('2026-01-01')") == 1 and pg.evaluate("wkNo('2027-01-01')") == 53, 'Número de semana (ISO) correcto')
    ok(pg.evaluate("wkMon('2026-11-22')") == '2026-11-16' and pg.evaluate("wkMon('2026-11-16')") == '2026-11-16', 'La semana empieza en lunes')

    print('2 · Esta semana')
    cur = pg.locator(f'details[data-fold="wk:{cm}"]')
    ok(cur.get_attribute('open') is not None, 'Esta semana viene abierta')
    t = cur.inner_text()
    ok('Esta semana' in t and '1 recepción' in t and '1 orden' in t and '1 embarque' in t and '3 correos' in t, 'El resumen cuenta lo de la semana')
    ok('3 pendientes' in t, 'Dice 3 pendientes (embarque abierto, orden incompleta y correo que no salió)')
    ok(cur.locator(f'.wkp [data-go="emb:{pg.evaluate("window.__i")}"]').count() == 1, 'Embarque abierto lleva a cerrarlo')
    ok(cur.locator(f'.wkp [data-go="orden:{pg.evaluate("window.__o")}"]').count() == 2, 'Orden incompleta y correo que no salió llevan a la orden')
    ok(cur.locator('tr[data-row="lote:LHOY"]').count() == 1, 'Recepción LHOY en la tabla')
    h = cur.locator('tr[data-row="lote:LHOY"] a.lnk').get_attribute('href')
    ok(h and 'authuser=conectandoensenada%40gmail.com' in h and 'PROPESA%20lote%20LHOY' in h, 'El lote tiene «Ver en Gmail ›» a su correo')
    ok('no salió' in cur.locator(f'tr[data-row="orden:{pg.evaluate("window.__o")}"]').inner_text(), 'La orden dice que su correo no salió')
    ok('Monitoreo de temperatura' in cur.locator('table.wkt').last.inner_text(), '«Otros correos» trae el de temperatura')
    g = cur.locator('a.btn.q', has_text='Correos de la semana en Gmail').get_attribute('href')
    nx = pg.evaluate(f"wkAdd('{cm}',7)").replace('-', '/')
    ok(g and ('after%3A' + cm.replace('-', '%2F')) in g and ('before%3A' + nx.replace('/', '%2F')) in g, 'Gmail de la semana busca de lunes a domingo')
    pg.screenshot(path=f'{OUT}/semanas_1280.png', full_page=True)

    print('3 · Semana anterior (plegada) y historial')
    old = pg.locator(f'details[data-fold="wk:{pg.evaluate(f"wkAdd(\'{cm}\',-21)")}"]')
    ok(old.get_attribute('open') is None, 'La semana sin pendientes viene cerrada')
    ok('Sin pendientes' in old.inner_text(), 'Dice «Sin pendientes»')
    old.locator('summary').click()
    pg.wait_for_timeout(300)
    old = pg.locator(f'details[data-fold="wk:{pg.evaluate(f"wkAdd(\'{cm}\',-21)")}"]')
    ok(old.locator('tr[data-row="lote:LANT"]').count() == 1, 'Al abrirla enseña su lote')
    pg.click('[data-hist="sem"]')
    pg.wait_for_timeout(300)
    ok(pg.locator('.wkl details.fold').count() == 3, '«Ver historial» enseña la semana de hace 10')

    print('4 · Lleva a donde se resuelve')
    pg.locator(f'details[data-fold="wk:{cm}"] tr[data-row="lote:LHOY"] td').first.click()
    pg.wait_for_timeout(300)
    ok(pg.evaluate('V.v') == 'lote' and pg.evaluate('V.id') == 'LHOY', 'Tocar la fila abre el lote')
    pg.evaluate("go('semanas')"); pg.wait_for_timeout(200)
    pg.locator(f'details[data-fold="wk:{cm}"] [data-wkhj]').click()
    pg.wait_for_timeout(300)
    ok(pg.evaluate('V.v') == 'hojas' and pg.evaluate('HJ.d0') == pg.evaluate(f"fd('{cm}')") and pg.evaluate('HJ.d1') == pg.evaluate(f"fd(wkAdd('{cm}',6))"), '«Hojas de esta semana» abre las hojas con lunes a domingo')

    print('5 · Sin correo de archivo no sale Gmail')
    pg.evaluate("ST.NE=ST.NE||{};ST.NE.arch={e:'',on:false};go('semanas')"); pg.wait_for_timeout(200)
    ok(pg.locator('.wkl a[href*="mail.google.com"]').count() == 0, 'Sin archivo no hay enlaces a Gmail')
    pg.evaluate("delete ST.NE.arch;go('semanas')"); pg.wait_for_timeout(200)

    print('6 · Anchos, letra grande y tema oscuro')
    for wd in (390, 768, 820, 1440):
        pg.set_viewport_size({'width': wd, 'height': 900}); pg.wait_for_timeout(200)
        ov = pg.evaluate("document.documentElement.scrollWidth-innerWidth")
        ok(ov <= 1, f'{wd} px sin desborde ({ov})')
    pg.set_viewport_size({'width': 390, 'height': 900})
    pg.screenshot(path=f'{OUT}/semanas_390.png', full_page=True)
    pg.evaluate("document.documentElement.style.fontSize='20px';render()"); pg.wait_for_timeout(200)
    ov = pg.evaluate("document.documentElement.scrollWidth-innerWidth")
    ok(ov <= 1, f'390 px con letra «Muy grande» sin desborde ({ov})')
    pg.screenshot(path=f'{OUT}/semanas_390_grande.png', full_page=True)
    pg.evaluate("document.documentElement.style.fontSize='';document.documentElement.dataset.theme='dark';render()")
    pg.set_viewport_size({'width': 768, 'height': 1000}); pg.wait_for_timeout(200)
    pg.screenshot(path=f'{OUT}/semanas_768_oscuro.png', full_page=True)

    ok(not errs, 'Sin errores de JavaScript' + (': ' + '; '.join(errs) if errs else ''))
    b.close()

if srv: srv.terminate()
print('TODO BIEN' if not MAL else f'FALLAS: {len(MAL)}')
sys.exit(1 if MAL else 0)
