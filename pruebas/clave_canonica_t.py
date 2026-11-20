# v1.55.2 · Auditoría de seguridad (F1): una clave con dos marcas de maquila («q1:q1:P/…») no entra a la app sin limpiar.
# Antes, la revisión WN no la reconocía (la dejaba pasar tal cual) pero decodeST la armaba como envío o precio: una cuenta de piso
# podía meter código que corría en la pantalla del Administrador o inventar un precio de compra. Correr: python3 -I pruebas/clave_canonica_t.py → «TODO BIEN».
# Abre la app como archivo (modo local, v1.55.1): no necesita servidor ni toca la base real. CHROME=/ruta/a/chrome para usar otro navegador.
import os, sys
from playwright.sync_api import sync_playwright
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'file://' + os.path.join(RAIZ, 'index.html')
SEED = r"""if(!ST.T)ST.T=[];SHW=encodeAll();ST.U=[{id:1,name:'Admin',email:'admin@propesa.org',role:'admin',notify:true}];me=ST.U[0];
ST.R.push({id:'R-1',lot:'LT1',origin:'Proveedor X',tank:'T1',rdate:dLoc(),time:'08:00',date:fd(dLoc()),final:null,closed:false});ST.B['LT1']=[];save();SHW=encodeAll();go('inicio')"""
PAY = '<img src=x onerror="window.__X=(window.__X||0)+1">'
ENV = lambda n: {'u': 'zz0001', 'n': n, 'z0': '', 'col': '#123456', 'exp': 0, 'h': 0, 'z': [0, 0, 0, 0], 'c': [], 'alive': None, 'closed': False}
bad = []; errs = []
def ok(c, t):
    print(('  ✔ ' if c else '  ✘ ') + t)
    if not c: bad.append(t)
with sync_playwright() as p:
    b = p.chromium.launch(**({'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {}))
    def nueva():
        pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(500); pg.evaluate(SEED); pg.wait_for_timeout(300); return pg
    for k in ['q1:q1:P/zz0001', 'q2:q1:P/zz0001', 'q01:P/zz0001', 'p/zz0001']:
        pg = nueva()
        pg.evaluate("rw=>{applyRows([rw]);render()}", {'k': k, 'v': ENV(PAY)}); pg.evaluate("go('emb:0')"); pg.wait_for_timeout(300)
        ok(pg.evaluate("(ST.P||[]).length==0&&!Object.values(STX).some(s=>s&&s.P&&s.P.length)"), f'{k}: se ignora (no crea envío en ninguna maquila)')
        ok(pg.evaluate("window.__X||0")==0, f'{k}: no corre código')
        pg.close()
    pg = nueva()
    pg.evaluate("rw=>{applyRows([rw]);render()}", {'k': 'P/zz0001', 'v': ENV('Envío 7 <b>')}); pg.evaluate("go('emb:0')"); pg.wait_for_timeout(300)
    ok(pg.evaluate("ST.P.length==1&&ST.P[0].n")=='Envío 7 b', 'P/zz0001 (clave normal): el envío llega, limpio')
    pg.close()
    pg = nueva()
    pg.evaluate("rw=>applyRows([rw])", {'k': 'q1:q1:$/LT1', 'v': {'lot': 'LT1', 'u': 99, 'nt': 'inventado'}})
    ok(pg.evaluate("(ST.R.find(r=>r.lot==='LT1')||{}).pr||null") is None, 'q1:q1:$/LT1: no se vuelve el precio del lote')
    pg.evaluate("rw=>applyRows([rw])", {'k': '$/LT1', 'v': {'lot': 'LT1', 'u': 12.5}})
    ok((pg.evaluate("(ST.R.find(r=>r.lot==='LT1')||{}).pr||null") or {}).get('u') == 12.5, '$/LT1 (clave normal): el precio sí llega')
    pg.close()
    ok(not errs, 'Sin errores JS ' + ';'.join(errs[:3]))
    b.close()
print('TODO BIEN' if not bad else 'FALLAS'); sys.exit(1 if bad else 0)
