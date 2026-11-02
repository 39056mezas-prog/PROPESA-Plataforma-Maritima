"""v1.13.0 · Cuenta Cliente (compradores de fuera) y salida automática al cerrar un embarque.
1) Modo local: disponibilidad = tanques − lo pedido que no sale; cerrar el embarque saca las hieleras del tanque y reabrir las regresa;
   la pantalla del Cliente está en inglés, sin menú y sin proveedor ni lote; sin desbordes en 390/820/1440 px, claro y oscuro.
2) Base de mentira: el Cliente solo recibe la hoja 'D/disp' y su propio perfil, la ve cambiar en vivo y no sube nada;
   dos Administradores a la vez no se pisan la hoja ni ven avisos de choque.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/disponible_t.py"""
import os, sys, json, time, subprocess, urllib.request
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
APP = BASE.split('?')[0]
MOCK = 'http://127.0.0.1:8792'
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
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',role:'piso',notify:true},{id:4,name:'Compras Shanghai',email:'compras@cliente.cn',role:'cliente',notify:false,mq:[1]}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
def login(pg, em, pw='x'):
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]')
def new_lot(pg, code, kgs):
    pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.fill('#fl', code); pg.select_option('#fo', '1'); pg.fill('#fkb', '18'); pg.fill('#ftt', '58'); pg.fill('#ftp', '59-61'); pg.fill('#fdes', '0')
    for i, v in enumerate(kgs): pg.fill(f'#fk{i}', str(v))
    pg.click('[data-a=sv]'); pg.wait_for_timeout(150)
def new_order(pg, etd, n):  # n hieleras, todas chicas (491-610)
    pg.evaluate("go('ordenes')"); pg.fill('#no_etd', etd); pg.click('[data-oa=new]')
    pg.select_option('#ol_city', 'PVG'); pg.fill('#ol_n', str(n)); pg.fill('#ol_z0', str(n)); pg.fill('#ol_tar', '0'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(150)
def pack_all(pg):  # todas las hieleras de la primera línea, categoría Blanco (= talla chica)
    pg.evaluate("go('empaque')"); pg.locator('[data-go^="empacar:"]').first.click()
    for r in range(pg.locator('.pkrow').count()):
        pg.fill('#pk_c0', str(20 + r)); pg.click('#pkr0 [data-pk="k:0:B"]'); pg.wait_for_timeout(80)
def close_ship(pg):
    pg.evaluate("ST.OR.forEach(o=>{o.f={...(o.f||{}),hf:'08:00',re:'Ana Torres',ev:'S',pl:'ZRY68F3',ch:'Chofer',tel:'646-000-0000',tp:'48 °F',to:'T1',tq:'T1 - 50 °F'}});save();go('emb:0')")
    pg.click('[data-a=cp]'); pg.wait_for_timeout(200)
D = "JSON.stringify(WN.D(dispCalc()))"
SAL = "ST.L.filter(m=>m.type=='SALIDA_EMBARQUE').map(m=>[m.lot,m.size,m.m,m.rc])"

srv = subprocess.Popen([sys.executable, '-I', os.path.join(ROOT, 'pruebas', 'supabase_falso.py'), '8792'])
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
        pg = b.new_page(viewport={'width': 1180, 'height': 820})
        pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
        pg.on('dialog', lambda d: d.accept())
        pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx')
        new_lot(pg, 'WLRCO221026', (100, 200, 300, 400))
        chk(json.loads(pg.evaluate(D))['z'] == [100000, 200000, 300000, 400000, 0], 'sin órdenes, disponible = lo que hay en tanques por talla')
        new_order(pg, '2026-10-22', 2)
        d = json.loads(pg.evaluate(D))
        chk(d['z'] == [68000, 200000, 300000, 400000, 0] and d['u'] == 0, 'una orden de 2 hieleras chicas aparta 32 kg de la talla 491-610: %s' % d['z'])
        chk(len(d['e']) == 1 and d['e'][0][1] == [100000, 200000, 300000, 400000, 0], 'la entrada de hoy sale en «recibido» con sus kg por talla')
        pk = json.loads(pg.evaluate(D)); pack_all(pg)
        chk(json.loads(pg.evaluate(D)) == pk, 'empacar no cambia la disponibilidad (ya estaba apartado por la orden)')
        close_ship(pg)
        chk(pg.evaluate("ST.P[0].closed"), 'embarque cerrado')
        s = pg.evaluate(SAL); u = pg.evaluate("ST.P[0].u")
        chk(s == [['WLRCO221026', '491-610', -32000, 'E/' + u]], 'al cerrar, la salida se registra sola: 32 kg de 491-610, marcada con el embarque: %s' % s)
        chk(pg.evaluate("bal('WLRCO221026','491-610')") == 68000, 'el tablero de tanques baja a 68 kg en 491-610')
        chk('Salieron 32.0 kg de los tanques' in pg.inner_text('#toast'), 'el aviso dice cuántos kg salieron: ' + pg.inner_text('#toast'))
        chk(json.loads(pg.evaluate(D))['z'][0] == 68000, 'después de cerrar no se descuenta dos veces (68 kg)')
        pg.click('[data-a=op]'); pg.wait_for_timeout(150)
        chk(pg.evaluate(SAL) == [] and pg.evaluate("bal('WLRCO221026','491-610')") == 100000, 'reabrir regresa los 32 kg al tanque')
        chk(json.loads(pg.evaluate(D))['z'][0] == 68000, 'reabierto, la orden vuelve a apartar: sigue 68 kg disponible')
        close_ship(pg)
        chk(len(pg.evaluate(SAL)) == 1 and pg.evaluate("bal('WLRCO221026','491-610')") == 68000, 'cerrar otra vez saca una sola vez')
        # nunca deja un lote en negativo: lote con 10 kg y 2 hieleras (32 kg)
        pg.evaluate("go('admin')")
        chk(pg.locator('#ur').count() == 0 and 'Solo inventario:' in pg.inner_text('#app'), 'Administración explica la cuenta de solo inventario')
        pg.click('[data-a=nu]'); chk('cliente' in pg.evaluate("[...document.querySelectorAll('#ur option')].map(o=>o.value)"), 'el Administrador puede dar de alta una cuenta Cliente'); pg.click('[data-a=cu]')
        pg.evaluate("ST.R.find(r=>r.lot=='WLRCO221026').closed=true;save()")
        new_lot(pg, 'WLRLE221026', (10, 0, 0, 0)); new_order(pg, '2026-10-23', 2); pack_all(pg)
        pg.evaluate("ST.OR.forEach(o=>{o.f={...(o.f||{}),hf:'08:00',re:'Ana Torres',ev:'S',pl:'ZRY68F3',ch:'Chofer',tel:'646-000-0000',tp:'48 °F',to:'T1',tq:'T1 - 50 °F'}});save();go('emb:'+(ST.P.length-1))")
        pg.click('[data-a=cp]'); pg.wait_for_timeout(200)
        chk(pg.evaluate("bal('WLRLE221026','491-610')") == 0 and pg.evaluate("bal('WLRCO221026','491-610')") == 68000, 'si salen más kg de los que hay, el lote queda en 0 (no negativo) y el lote cerrado no se toca')
        dd = json.loads(pg.evaluate(D))
        chk(all(v >= 0 for v in dd['z']) and dd['z'][0] == 0, 'la disponibilidad nunca es negativa: %s' % dd['z'])
        # orden sin tallas: solo resta del total
        pg.evaluate("ST.R.find(r=>r.lot=='WLRLE221026').closed=true;save()")
        new_lot(pg, 'WLREM221026', (50, 50, 50, 50))
        pg.evaluate("const o=ST.OR[ST.OR.length-1];o.lines.push({id:uidN(),city:'PVG',cons:2,boxes:1});save()")
        dd = json.loads(pg.evaluate(D))
        chk(dd['u'] == 16000 and dd['z'] == [50000, 50000, 50000, 50000, 0], 'una línea sin tallas va como «reservado» (16 kg) sin tocar las tallas')
        # --- pantalla del Cliente
        pg.evaluate("signOut()"); login(pg, 'compras@cliente.cn')
        chk(until(pg, "!!document.querySelector('.cli')"), 'la cuenta Cliente entra directo a su pantalla')
        t = pg.inner_text('#app')
        chk(pg.locator('.sb,.pshell,[data-avatar],#sq').count() == 0, 'sin menú, sin buscador y sin Ajustes')
        chk(all(x in t for x in ('Disponible', 'Chica', 'Mediana', 'Grande', 'Jumbo', 'Total disponible', 'Recibido en los últimos 7 días', 'Cerrar sesión')), 'en español (v1.30.0): tallas, total y lo recibido en la semana')
        chk('50 kg' in t and '≈ 3 hieleras de 15 kg' in t and 'Apartado, todavía sin talla' in t and '184 kg' in t, 'kg por talla, hieleras de 15 kg, reservado y total (4 × 50 − 16 = 184 kg)')
        chk(pg.get_attribute('.cli', 'lang') is None, 'la pantalla ya no se marca en inglés (v1.30.0)')
        for bad in ('WLR', 'SCPP', 'Ensenada SCL', 'Tanque', 'PVG', 'YISHUNHAI', 'Ana Torres', 'Entrada', 'Órdenes'):
            chk(bad not in t, 'no muestra «%s»' % bad)
        chk('NaN' not in t and 'undefined' not in t, 'sin NaN ni undefined')
        for w in (390, 820, 1440):
            for sch in ('light', 'dark'):
                pg.set_viewport_size({'width': w, 'height': 900}); pg.emulate_media(color_scheme=sch); pg.wait_for_timeout(80)
                chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'sin desborde a %d px, tema %s' % (w, sch))
                pg.screenshot(path=f'{OUT}/cliente_{w}_{sch}.png', full_page=True)
        pg.evaluate("document.documentElement.style.setProperty('--app-font-size','20px')"); pg.set_viewport_size({'width': 390, 'height': 900})
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'sin desborde a 390 px con texto «Muy grande»')
        chk(pg.evaluate("Math.min(...[...document.querySelectorAll('.cli button')].map(b=>b.getBoundingClientRect().height))") >= 44, 'botón «Sign out» de 44 px o más')
        pg.click('[data-a=lo]'); chk(until(pg, "!!document.getElementById('le')"), '«Sign out» cierra la sesión')
        pg.close()

        # ---------------- 2) base de mentira ----------------
        INIT = "window.PROPESA_SB={url:'%s',key:'clave-publica-de-prueba'};try{localStorage.setItem('propesa-kp','0')}catch(e){}" % MOCK
        def device(name):
            ctx = b.new_context(viewport={'width': 1180, 'height': 820}); ctx.add_init_script(INIT); pg = ctx.new_page()
            pg.on('pageerror', lambda e: errs.append(name + ' JS ' + str(e))); pg.on('dialog', lambda d: d.accept())
            toasts = []; pg.expose_function('_toast', lambda t: toasts.append(str(t)))
            pg.goto(APP); pg.evaluate("const T=toast;window.toast=t=>{window._toast(t);T(t)}"); return ctx, pg, toasts
        ca, A, ta = device('A'); cb, B, tb = device('B')
        login(A, 'admin@propesa.mx', 'clave-admin1'); chk(until(A, "!!me&&!!document.querySelector('.sb')"), 'A: entra el Administrador')
        A.evaluate("go('admin')"); A.click('[data-a=nu]'); A.fill('#un', 'Compras Shanghai'); A.fill('#ue', 'compras@cliente.cn'); A.fill('#up', 'Compras-2026'); A.select_option('#ur', 'cliente'); A.check('#umq input[value="1"]'); A.click('[data-a=su]')
        chk(until(A, "ST.U.some(u=>u.role=='cliente')"), 'A: alta de la cuenta Cliente con la función usuarios')
        login(B, 'admin2@propesa.mx', 'clave-admin2'); chk(until(B, "!!me&&!!document.querySelector('.sb')"), 'B: entra el segundo Administrador')
        new_lot(A, 'WLRCO221026', (100, 200, 300, 400))
        chk(until(A, "!outN()") and mock('/__estado')['recs'].get('D/disp', {}).get('v', {}).get('z') == [100000, 200000, 300000, 400000, 0], 'la base recibe la hoja D/disp con los kg por talla')
        dv = json.dumps(mock('/__estado')['recs']['D/disp']['v'])
        chk(all(x not in dv for x in ('WLR', 'SCPP', 'T1', 'origin', 'lot')), 'la hoja no lleva proveedor, lote ni tanque')
        chk(until(B, "ST.R.length==1"), 'B recibe la entrada de A')
        new_lot(B, 'WLREM221026', (10, 10, 10, 10)); new_order(A, '2026-10-22', 2)
        chk(until(A, "!outN()&&ST.R.length==2") and until(B, "!outN()&&ST.OR.length==1"), 'A y B capturan casi a la vez y se ponen al día')
        time.sleep(1.5)
        chk(until(A, "JSON.stringify(WN.D(dispCalc()))==JSON.stringify(WN.D(%s))" % json.dumps(mock('/__estado')['recs']['D/disp']['v'])) and mock('/__estado')['recs']['D/disp']['v']['z'] == [78000, 210000, 310000, 410000, 0], 'la hoja de la base cuadra con lo que calcula cada equipo (110 − 32, 210, 310, 410 kg)')
        chk(not any('otro equipo' in t for t in ta + tb), 'sin avisos de «otro equipo lo cambió antes» por la hoja')
        w0 = mock('/__estado')['writes']; time.sleep(6)
        chk(mock('/__estado')['writes'] == w0, 'sin cambios nuevos, nadie reescribe la hoja (no hay ida y vuelta)')
        # --- el comprador
        cc, C, tc = device('C')
        login(C, 'compras@cliente.cn', 'Compras-2026')
        chk(until(C, "!!document.querySelector('.cli')&&document.body.innerText.includes('Total disponible')"), 'C: el comprador entra a «Disponible»')
        chk(until(C, "document.body.innerText.includes('78 kg')&&document.body.innerText.includes('En vivo · último cambio hace un momento')"), 'C: ve 78 kg chicos y «En vivo · último cambio hace un momento»')
        chk(C.evaluate("ST.R.length+ST.OR.length+ST.P.length+ST.L.length") == 0, 'C: no baja lotes, órdenes, embarques ni movimientos')
        r = C.evaluate("sbPost('/rest/v1/rpc/pull',{since:0,lim:2000}).then(a=>a.map(x=>x.k))")
        chk(r == ['D/disp'], 'C: pidiendo todo a la base, solo recibe D/disp: %s' % r)
        r = C.evaluate("sbFetch('/rest/v1/profiles?select=id,name,email,role').then(x=>x.json()).then(a=>a.map(u=>u.email))")
        chk(r == ['compras@cliente.cn'], 'C: solo ve su propio perfil (no los correos del personal): %s' % r)
        r = C.evaluate("sbPost('/rest/v1/rpc/push',{rows:[{k:'R/X',v:{lot:'X'}}]}).then(()=>'ok',e=>e.status)")
        chk(r == 403, 'C: la base no le deja escribir (%s)' % r)
        new_lot(A, 'WLRLE221026', (0, 0, 0, 50))
        chk(until(C, "document.body.innerText.includes('460 kg')", 15), 'C: en vivo, la entrada nueva de Jumbo aparece sola (410 + 50 = 460 kg)')
        C.click('[data-a=lo]'); chk(until(C, "!!document.getElementById('le')"), 'C: «Sign out» regresa al acceso')
        for c in (ca, cb, cc): c.close()
        b.close()
finally:
    srv.terminate()
for e in errs: print('FAIL ' + e)
print('\n%d fallas' % (len(fails) + len(errs)))
sys.exit(1 if fails or errs else 0)
