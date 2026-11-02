"""v1.30.0 (pedido del usuario, 1/nov/2026): Consulta y Cliente son una sola cuenta de «solo inventario».
- En español. El Administrador le elige una o varias maquilas; ve el disponible por talla de esas maquilas, sumado, sin decir de cuál.
- No ve precios, maquilas, proveedores, lotes ni ninguna otra pantalla. Sin maquilas asignadas no ve nada.
- Con la base compartida (Supabase de mentira): la base solo le entrega las hojas de sus maquilas ('D/disp', 'q<id>:D/disp').
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v130_t.py"""
from playwright.sync_api import sync_playwright
import os, sys, json, time, subprocess, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
APP = BASE.split('?')[0]
seed = open(os.path.join(ROOT, 'pruebas', 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em):
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
SENS = ['Precio', 'precio', 'Proveedor', 'Cooperativa', 'WLR', 'Tanque', 'YISHUNHAI', 'Maquila', 'PROPESA ', 'David', 'Abel', 'Available', 'Sign out']
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1280, 900), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0")}', seed); pg.reload()
        entrar(pg, 'admin@propesa.mx')
        # datos en una segunda maquila: un lote de David con 50 kg de Mediana
        dav = pg.evaluate("(()=>{const m=mqAll().find(x=>x.n=='David')||mqAll()[1];return m.id})()")
        tot1 = pg.evaluate("(()=>{const d=WN.D(dispCalc());return d.z.reduce((a,v)=>a+v,0)-d.u})()")
        pg.evaluate(f"mqSet({dav});ST.R.push({{lot:'WLRDA011126A',rdate:dLoc(),time:'08:00',origin:'Cooperativa',tank:'T2',sp:ST.ES?undefined:undefined}});ST.L.push({{id:uidN(),lot:'WLRDA011126A',type:'RECEPCION',size:S[1],m:50000,t:dLoc()}});save();mqSet(1);render()")
        tot2 = pg.evaluate(f"(()=>{{let r;withST(STX[{dav}],()=>{{const d=WN.D(dispCalc());r=d.z.reduce((a,v)=>a+v,0)-d.u}});return r}})()")
        chk(tot1 > 0 and tot2 == 50000, f'{vw} hay inventario en PROPESA ({tot1} g) y en David ({tot2} g)')
        # alta de la cuenta
        pg.evaluate("go('admin')"); pg.click('[data-a=nu]')
        opts = pg.eval_on_selector_all('#ur option', 'o=>o.map(x=>x.textContent)')
        chk('Solo inventario' in opts and 'Consulta' not in opts and 'Cliente (comprador)' not in opts, f'{vw} el rol se llama «Solo inventario» y ya no hay Consulta ni Cliente: {opts}')
        chk(pg.locator('#umq').is_hidden(), f'{vw} las maquilas no salen para otros roles')
        pg.select_option('#ur', 'cliente'); chk(pg.locator('#umq').is_visible() and pg.locator('#umq input').count() >= 2, f'{vw} con «Solo inventario» salen las maquilas para elegir')
        pg.fill('#un', 'Comprador Uno'); pg.fill('#ue', 'compra1@propesa.mx'); pg.fill('#up', 'Clave-segura-1'); pg.click('[data-a=su]')
        chk('al menos una maquila' in pg.inner_text('#app') and pg.input_value('#un') == 'Comprador Uno', f'{vw} sin maquila no se guarda y no borra lo escrito')
        pg.check(f'#umq input[value="{dav}"]'); pg.click('[data-a=su]'); pg.wait_for_timeout(100)
        u = pg.evaluate("ST.U.find(u=>u.email=='compra1@propesa.mx')")
        chk(u and u['role'] == 'cliente' and u['mq'] == [dav], f'{vw} se guarda con solo David: {u}')
        chk('David' in pg.inner_text('table.lf'), f'{vw} la lista de usuarios dice qué maquilas ve')
        # otra cuenta con las dos maquilas
        pg.click('[data-a=nu]'); pg.select_option('#ur', 'cliente'); pg.fill('#un', 'Comprador Dos'); pg.fill('#ue', 'compra2@propesa.mx'); pg.fill('#up', 'Clave-segura-2')
        pg.check('#umq input[value="1"]'); pg.check(f'#umq input[value="{dav}"]'); pg.click('[data-a=su]'); pg.wait_for_timeout(100)
        pg.evaluate("signOut()"); pg.wait_for_timeout(150)
        # entra la cuenta de solo David
        entrar(pg, 'compra1@propesa.mx'); tx = pg.inner_text('#app')
        chk('Disponible' in tx and 'Total disponible' in tx and 'Cerrar sesión' in tx, f'{vw} entra a «Disponible», en español')
        chk('50 kg' in tx and pg.evaluate("dispLocal().z.reduce((a,v)=>a+v,0)") == 50000, f'{vw} solo ve los 50 kg de su maquila')
        chk(not [w for w in SENS if w in tx], f'{vw} sin datos sensibles ni nombre de maquila: {[w for w in SENS if w in tx]}')
        pg.evaluate("go('recepcion')"); chk(pg.locator('.cli').count() == 1 and pg.locator('.sb').count() == 0, f'{vw} no puede ir a otra pantalla')
        pg.evaluate("signOut()"); pg.wait_for_timeout(150)
        # entra la de dos maquilas: suma sin decir de cuál
        entrar(pg, 'compra2@propesa.mx'); tx = pg.inner_text('#app')
        s2 = pg.evaluate("(()=>{const d=dispLocal();return d.z.reduce((a,v)=>a+v,0)-d.u})()")
        chk(s2 == tot1 + 50000, f'{vw} con dos maquilas suma las dos: {s2} = {tot1} + 50000')
        chk(not [w for w in SENS if w in tx], f'{vw} tampoco dice las maquilas')
        pg.evaluate("signOut()"); pg.wait_for_timeout(150)
        # una cuenta «consulta» vieja sin maquilas no ve nada
        entrar(pg, 'consulta@propesa.mx'); tx = pg.inner_text('#app')
        chk('no tiene inventario asignado' in tx and pg.locator('.sb').count() == 0, f'{vw} una cuenta de Consulta vieja ya no ve la operación')
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{vw} sin scroll de lado')
        pg.close()

    # ---------- con la base compartida (Supabase de mentira) ----------
    MOCK = 'http://127.0.0.1:8791'
    def mock(path, post=False):
        r = urllib.request.urlopen(urllib.request.Request(MOCK + path, data=b'{}' if post else None, method='POST' if post else 'GET'))
        return json.loads(r.read() or b'null')
    srv = subprocess.Popen([sys.executable, '-I', os.path.join(ROOT, 'pruebas', 'supabase_falso.py'), '8791'])
    try:
        for _ in range(50):
            try: mock('/__reset', True); break
            except Exception: time.sleep(0.1)
        INIT = "window.PROPESA_SB={url:'%s',key:'clave-publica-de-prueba'}" % MOCK
        def device(name):
            ctx = b.new_context(viewport={'width': 1180, 'height': 820}); ctx.add_init_script(INIT)
            pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(name + ' JS ' + str(e))); pg.goto(APP); return pg
        def until(pg, js, t=12):
            end = time.time() + t
            while time.time() < end:
                try:
                    if pg.evaluate(js): return True
                except Exception: pass
                time.sleep(0.25)
            return False
        A = device('A'); A.fill('#le', 'admin@propesa.mx'); A.fill('#lp', 'clave-admin1'); A.click('[data-a=lg]')
        chk(until(A, "!!me&&me.role=='admin'&&SYNC_FIRST"), 'nube: el Administrador entra')
        A.evaluate("ST.R.push({lot:'WLRCO011126A',rdate:dLoc(),time:'08:00',origin:'Cooperativa',tank:'T1'});ST.L.push({id:uidN(),lot:'WLRCO011126A',type:'RECEPCION',size:S[1],m:70000,t:dLoc()});save()")
        dav = A.evaluate("mqAll()[1].id")
        A.evaluate(f"mqSet({dav});ST.R.push({{lot:'WLRDA011126A',rdate:dLoc(),time:'08:00',origin:'Cooperativa',tank:'T2'}});ST.L.push({{id:uidN(),lot:'WLRDA011126A',type:'RECEPCION',size:S[1],m:30000,t:dLoc()}});save();mqSet(1)")
        chk(until(A, f"outN()==0&&!!SYNC_OK") and until(A, "true", 3), 'nube: se suben las hojas de las dos maquilas')
        recs = mock('/__estado')['recs']
        chk('D/disp' in recs and f'q{dav}:D/disp' in recs, f'nube: hay una hoja por maquila: {[k for k in recs if "D/disp" in k]}')
        # la cuenta de consulta que ya existía: el Administrador le pone solo David
        A.evaluate("go('admin')"); cid = [u for u in mock('/__estado')['users'] if u['email'] == 'consulta@propesa.mx'][0]['id']
        A.click(f'[data-eu="{cid}"]'); chk(A.input_value('#ur') == 'cliente' and A.locator('#umq').is_visible(), 'nube: una cuenta de Consulta se abre como «Solo inventario»')
        A.check(f'#umq input[value="{dav}"]'); A.click('[data-a=su]')
        chk(until(A, f"(ST.U.find(u=>u.email=='consulta@propesa.mx')||{{}}).role=='cliente'") and [u for u in mock('/__estado')['users'] if u['id'] == cid][0]['mq'] == [dav], 'nube: queda como «Solo inventario» con David guardado en su perfil')
        C = device('C'); C.fill('#le', 'consulta@propesa.mx'); C.fill('#lp', 'clave-ver1'); C.click('[data-a=lg]')
        chk(until(C, "!!document.querySelector('.cli')&&!!DISP"), 'nube: entra a «Disponible»')
        chk(C.evaluate("Object.keys(DSH)") == [f'q{dav}:D/disp'] and C.evaluate("DISP.z.reduce((a,v)=>a+v,0)") == 30000, f'nube: la base solo le entrega la hoja de David: {C.evaluate("Object.keys(DSH)")}')
        chk(C.evaluate("ST.R.length") == 0, 'nube: no le llega ningún lote')
        tx = C.inner_text('#app'); chk('30 kg' in tx and not [w for w in SENS if w in tx], 'nube: ve 30 kg sin datos sensibles')
        w = mock('/__estado')['writes']; time.sleep(3); chk(mock('/__estado')['writes'] == w, 'nube: no escribe nada')
        # si la versión nueva se publica antes de aplicar la actualización de la base, nadie se queda fuera
        mock('/__reset', True); mock('/__sin_mq', True)
        Z = device('Z'); Z.fill('#le', 'admin@propesa.mx'); Z.fill('#lp', 'clave-admin1'); Z.click('[data-a=lg]')
        chk(until(Z, "!!me&&me.role=='admin'&&!!document.querySelector('.sb')&&NO_MQ"), 'nube sin la columna mq: el Administrador entra igual')
    finally:
        srv.terminate()
    b.close()
chk(not errs, f'sin errores de JavaScript {errs}')
print('\n' + ('TODO BIEN' if not fails else f'{len(fails)} FALLAS')); raise SystemExit(1 if fails else 0)
