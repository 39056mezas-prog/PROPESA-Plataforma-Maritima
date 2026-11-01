"""v1.19.0 · Precios de compra: solo el Administrador, también en la base (pedido del usuario, 26/oct/2026: «solo administración
puede ver»). El precio viaja en su propio registro ('$/<lote>', con prefijo de maquila en otra maquila); la base solo se lo da y
se lo deja escribir al Administrador (supabase/migrations/20261026_precios.sql; aquí, el Supabase de mentira en el puerto 8795).
- El registro del lote ya no trae el precio. Piso y Consulta no lo reciben aunque lo pidan directo, y no lo pueden escribir.
- Piso cambia el lote y el precio sigue intacto en la base. Otro Administrador sí lo ve. Funciona igual en otra maquila.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/precios_t.py"""
import os, sys, json, time, subprocess, urllib.request
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.environ.get('APP', 'http://localhost:8765/index.html')
MOCK = 'http://127.0.0.1:8795'
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def until(pg, js, t=15):
    end = time.time() + t
    while time.time() < end:
        try:
            if pg.evaluate(js): return True
        except Exception: pass
        time.sleep(0.25)
    return False
def mock(path, post=False):
    r = urllib.request.urlopen(urllib.request.Request(MOCK + path, data=b'{}' if post else None, method='POST' if post else 'GET'))
    return json.loads(r.read() or b'null')
srv = subprocess.Popen([sys.executable, '-I', os.path.join(ROOT, 'pruebas', 'supabase_falso.py'), '8795'])
for _ in range(50):
    try: mock('/__reset', True); break
    except Exception: time.sleep(0.1)
INIT = "window.PROPESA_SB={url:'%s',key:'clave-publica-de-prueba'};try{localStorage.setItem('propesa-kp','0')}catch(e){}" % MOCK
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        def device(name, em, pw):
            ctx = b.new_context(viewport={'width': 1180, 'height': 820}); ctx.add_init_script(INIT); q = ctx.new_page()
            q.on('pageerror', lambda e: errs.append(name + ' JS ' + str(e))); q.on('dialog', lambda d: d.accept()); q.goto(APP)
            q.fill('#le', em); q.fill('#lp', pw); q.click('[data-a=lg]'); until(q, "!!me&&!!document.querySelector('.sb,.pshell')"); return ctx, q
        ca, A = device('A', 'admin@propesa.mx', 'clave-admin1'); cp, P = device('P', 'piso@propesa.mx', 'clave-piso1'); cc, C = device('C', 'consulta@propesa.mx', 'clave-ver1')
        cb, B = device('B', 'admin2@propesa.mx', 'clave-admin2')
        A.evaluate("mqSet(1);go('recepcion')"); A.click('[data-a=nf]'); A.fill('#fl', 'WLRCO261026'); A.select_option('#fo', '1'); A.fill('#fkb', '36'); A.fill('#ftt', '58'); A.fill('#ftp', '59'); A.fill('#fdes', '0'); A.fill('#fk0', '500'); A.fill('#fk4', '10'); A.click('[data-a=sv]'); A.wait_for_timeout(200)
        A.fill('#pr_u', '43'); A.fill('#pr_d', '25'); A.select_option('#pr_f', 'F'); A.click('[data-a=prs]')
        chk(until(A, "outN()==0"), 'A sube el lote y su precio')
        recs = mock('/__estado')['recs']
        chk('$/WLRCO261026' in recs and recs['$/WLRCO261026']['v'] == {'lot': 'WLRCO261026', 'u': 43, 'd': 25, 'f': 'F'}, 'el precio va en su propio registro $/WLRCO261026')
        chk('pr' not in recs['R/WLRCO261026']['v'], 'el registro del lote ya no trae el precio')
        chk(until(B, "R_('WLRCO261026')&&R_('WLRCO261026').pr&&R_('WLRCO261026').pr.u==43"), 'otro Administrador recibe el precio')
        chk(until(P, "!!R_('WLRCO261026')") and P.evaluate("R_('WLRCO261026').pr") is None, 'Piso recibe el lote pero no el precio')
        chk(until(C, "!!R_('WLRCO261026')") and C.evaluate("R_('WLRCO261026').pr") is None, 'Consulta tampoco recibe el precio')
        raw = P.evaluate("""async()=>{const t=JSON.parse(localStorage.getItem('propesa-sb')).at;const r=await fetch(PROPESA_SB.url+'/rest/v1/rpc/pull',{method:'POST',headers:{apikey:'k',Authorization:'Bearer '+t,'Content-Type':'application/json'},body:JSON.stringify({since:0,lim:1000})});return (await r.json()).map(x=>x.k)}""")
        chk(not any(k.startswith('$/') for k in raw), 'Piso no lo recibe ni pidiéndolo directo a la base')
        st = P.evaluate("""async()=>{const t=JSON.parse(localStorage.getItem('propesa-sb')).at;const r=await fetch(PROPESA_SB.url+'/rest/v1/rpc/push',{method:'POST',headers:{apikey:'k',Authorization:'Bearer '+t,'Content-Type':'application/json'},body:JSON.stringify({rows:[{k:'$/WLRCO261026',v:{lot:'WLRCO261026',u:1}}]})});return r.status}""")
        chk(st == 403 and mock('/__estado')['recs']['$/WLRCO261026']['v']['u'] == 43, 'Piso no puede escribir un precio (403) y el precio sigue en 43')
        # Piso cambia el lote: el precio no se toca
        P.evaluate("R_('WLRCO261026').kgbox=38;save()"); chk(until(P, "outN()==0"), 'Piso sube un cambio del lote')
        recs = mock('/__estado')['recs']
        chk(recs['R/WLRCO261026']['v']['kgbox'] == 38 and recs['$/WLRCO261026']['v']['u'] == 43, 'el cambio de Piso llega y el precio sigue intacto')
        chk(until(A, "R_('WLRCO261026').kgbox==38") and A.evaluate("R_('WLRCO261026').pr.u") == 43, 'en el Administrador el lote cambia y conserva su precio')
        # otra maquila
        A.evaluate("mqSet(2);render()"); A.evaluate("go('recepcion')"); A.click('[data-a=nf]'); A.fill('#fl', 'WLRCO261026'); A.select_option('#fo', '1'); A.fill('#fkb', '36'); A.fill('#ftt', '58'); A.fill('#ftp', '59'); A.fill('#fdes', '0'); A.fill('#fk0', '200'); A.click('[data-a=sv]'); A.wait_for_timeout(200)
        A.fill('#pr_u', '40'); A.click('[data-a=prs]'); chk(until(A, "outN()==0"), 'precio en Abel')
        recs = mock('/__estado')['recs']
        chk('q2:$/WLRCO261026' in recs and recs['q2:$/WLRCO261026']['v']['u'] == 40, "en Abel el precio va como 'q2:$/WLRCO261026'")
        P.evaluate("mqSet(2);render()"); chk(until(P, "!!R_('WLRCO261026')") and P.evaluate("R_('WLRCO261026').pr") is None, 'Piso en Abel tampoco ve el precio')
        # borrar el lote borra su precio
        A.evaluate("ST.R=ST.R.filter(r=>r.lot!=='WLRCO261026');ST.L=ST.L.filter(x=>x.lot!=='WLRCO261026');delete ST.B['WLRCO261026'];save()"); chk(until(A, "outN()==0"), 'A elimina el lote de Abel')
        chk(mock('/__estado')['recs']['q2:$/WLRCO261026']['v'] is None, 'al eliminar el lote se borra su precio')
        for c in (ca, cp, cc, cb): c.close()
        b.close()
finally:
    srv.terminate()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
