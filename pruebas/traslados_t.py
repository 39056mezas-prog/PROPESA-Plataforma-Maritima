"""v1.19.0 · Lotes en varios tanques y traslados entre tanques (pedido del usuario, 26/oct/2026; en el Excel «1/2», «57.6/60.3»,
«34 Y 36» y existencias que pasan kilos de un tanque a otro).
- Entrada (vista completa y hoja de Modo piso): «Otro tanque», sus kg, su temperatura y sus kg por caja. Validaciones.
- El tablero de tanques reparte los kg de cada lote (con sus tallas en proporción); la tabla de Entrada y sus PDF dicen «1/2», «58/60.3».
- La temperatura del otro tanque sale en Temperatura.
- En el lote: «Pasar a otro tanque» (kg o todo), lista de traslados, «Deshacer» (Administrador). Las salidas salen primero del principal.
- Panel general y hoja de existencia por tanque; se comparte (TQ/<id>, con prefijo en otra maquila) y sobrevive a un respaldo.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/traslados_t.py"""
import os, json
from playwright.sync_api import sync_playwright
PLEG = "Object.setPrototypeOf(FOLD,new Proxy({},{get:(t,k)=>typeof k=='string'?true:undefined}));render()"  # v1.34.0: en esta prueba todos los plegables quedan abiertos
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
OUT = os.environ.get('OUT', '/tmp/propesa-pruebas'); os.makedirs(OUT, exist_ok=True)
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',role:'piso',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
def login(pg, em):
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200); pg.evaluate(PLEG)
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")
DIST = "l=>Object.fromEntries(Object.entries(tqDist(l)).map(([t,g])=>[t,g/1000]))"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1);FOLD['ent-tq']=true;FOLD['ent-t2']=true;go('recepcion')")
    def entrada(code, t2='', k2='', tt2='', kb2=''):
        pg.click('[data-a=nf]'); pg.fill('#fl', code); pg.select_option('#fo', '2'); pg.select_option('#ft', 'T1'); pg.fill('#fkb', '34'); pg.fill('#ftt', '57.6'); pg.fill('#ftp', '48-62'); pg.fill('#fdes', '0')
        pg.fill('#fk0', '800'); pg.fill('#fk1', '200')
        if t2: pg.select_option('#ft2', t2)
        pg.fill('#fk2z0', k2); pg.fill('#ftt2', tt2); pg.fill('#fkb2', kb2); pg.click('[data-a=sv]'); pg.wait_for_timeout(120)  # v1.25.0: kg por talla
    entrada('WLREM190926', 'T1', '300')
    chk('distinto' in pg.inner_text('.panel') and pg.input_value('#fl') == 'WLREM190926', 'el otro tanque no puede ser el mismo (y se conserva lo escrito)')
    pg.select_option('#ft2', 'T2'); pg.fill('#fk2z0', '900'); pg.click('[data-a=sv]'); pg.wait_for_timeout(100)
    chk('más de lo que entró (800.00 kg)' in pg.inner_text('.panel'), 'los kg de una talla en el otro tanque no pueden pasar de lo que entró')
    pg.fill('#fk2z0', '800'); pg.fill('#fk2z1', '200'); pg.click('[data-a=sv]'); pg.wait_for_timeout(100)
    chk('No puede irse todo' in pg.inner_text('.panel'), 'no puede irse todo al otro tanque')
    pg.fill('#fk2z0', '240'); pg.fill('#fk2z1', '60'); pg.fill('#ftt2', '60.3'); pg.fill('#fkb2', '36'); pg.click('[data-a=sv]'); pg.wait_for_timeout(150)
    chk(pg.evaluate(DIST, 'WLREM190926') == {'T1': 700, 'T2': 300}, 'entrada repartida: T1 700 kg y T2 300 kg')
    pg.evaluate("FOLD['ent-tq']=true;go('recepcion')"); pg.wait_for_timeout(100)
    row = pg.locator('table.ent tbody tr', has_text='WLREM190926').inner_text()
    chk('1/2' in row and '57.6/60.3' in row and '34/36' in row, f'la tabla de Entrada dice tanque 1/2, 57.6/60.3 °F y 34/36 kg por caja: {row!r}')
    pg.evaluate("FOLD['ent-tq']=true;render()"); pg.click('[data-tq=T2]'); pg.wait_for_timeout(100)
    t = pg.inner_text('.tqc'); chk('300.0 kg' in t and 'WLREM190926' in t and '300.0 kg aquí' in t, 'el tablero: T2 con 300 kg de ese lote')
    chk(pg.evaluate("[tqZ('WLREM190926','T2','491-610'),tqZ('WLREM190926','T2','611-850')]") == [240000, 60000], 'T2 tiene exactamente lo capturado por talla (240 + 60)')
    pg.evaluate("go('temperatura')"); pg.wait_for_timeout(100)
    chk('60.3' in pg.inner_text('main'), 'la temperatura del otro tanque (60.3 °F) sale en Temperatura')
    # traslados en el lote
    pg.evaluate("go('lote:WLREM190926')"); pg.wait_for_timeout(100)
    chk(pg.locator('#tqc').count() == 1 and 'T1 (principal) · 700.0 kg' in pg.inner_text('#tqc'), 'el lote muestra sus tanques')
    pg.select_option('#tq_de', 'T1'); pg.select_option('#tq_a', 'T4'); pg.fill('#tq_kg', '900'); pg.click('[data-a=tqmv]'); pg.wait_for_timeout(80)
    chk('hay 700.00 kg' in pg.inner_text('#app .fer') and pg.input_value('#tq_kg') == '900', 'no deja pasar más de lo que hay (y conserva lo escrito)')
    pg.fill('#tq_kg', '200'); pg.fill('#tq_n', 'para envío del 25'); pg.click('[data-a=tqmv]'); pg.wait_for_timeout(100)
    chk(pg.evaluate(DIST, 'WLREM190926') == {'T1': 500, 'T2': 300, 'T4': 200}, 'pasa 200 kg de T1 a T4')
    pg.select_option('#tq_de', 'T2'); pg.select_option('#tq_a', 'T4'); pg.fill('#tq_kg', ''); pg.click('[data-a=tqmv]'); pg.wait_for_timeout(100)
    chk(pg.evaluate(DIST, 'WLREM190926') == {'T1': 500, 'T2': 0, 'T4': 500}, 'sin kg pasa todo lo de T2 a T4')
    chk('para envío del 25' in pg.inner_text('#tqc'), 'la lista de traslados con su nota')
    pg.evaluate("post('CONGELACION','WLREM190926','491-610',-100);save();render()")
    chk(pg.evaluate(DIST, 'WLREM190926') == {'T1': 400, 'T2': 0, 'T4': 500}, 'una salida de 100 kg sale del tanque principal')
    pg.locator('#tqc [data-tqx]').first.click(); pg.wait_for_timeout(100)
    chk(pg.evaluate(DIST, 'WLREM190926') == {'T1': 400, 'T2': 300, 'T4': 200}, '«Deshacer» el último traslado regresa los 300 kg a T2')
    # Panel general, PDF
    pg.evaluate("go('general')"); pg.wait_for_timeout(100)
    rows = pg.eval_on_selector_all('.mqt tbody tr', 'e=>e.map(x=>x.innerText)')
    chk(any(r.startswith('T4') and '200' in r for r in rows) and any(r.startswith('T2') and '300' in r for r in rows), 'Panel general: T2 300 kg y T4 200 kg')
    t = pg.evaluate("(async()=>{const d=await pdfMake('hexi','');let s='';for(const b of d.u8)s+=String.fromCharCode(b);return s})()")
    chk(t.count('(WLREM190926)') == 3, 'la hoja de existencia trae un renglón por tanque del lote (3)')
    # compartir y respaldo
    w = json.loads(pg.evaluate("JSON.stringify([...encodeAll()].filter(([k])=>k.startsWith('TQ/')).map(([k,v])=>v[1]))"))
    chk(len(w) == 2 and {x['a'] for x in w} == {'T2', 'T4'} and any(x.get('tt') == 60.3 and x.get('kb') == 36 for x in w), 'los traslados viajan como TQ/<id> (con temperatura y kg por caja)')
    c = json.loads(pg.evaluate("JSON.stringify(cleanST(mqDump()).TQ)")); d = pg.evaluate("decodeST(new Map([...encodeST()].map(([k,v])=>[k,v[1]]))).TQ.length")
    chk(len(c) == 2 and d == 2, 'sobreviven a un respaldo y a decodeST')
    chk(pg.evaluate("WN.TQ({id:1,lot:'X',de:'T1',a:'T1',kg:5})") is None and pg.evaluate("WN.TQ({id:1,lot:'X',de:'T1',a:'T9',kg:5})") is None, 'traslados sin sentido se ignoran')
    pg.evaluate("mqSet(2);ST.R=[];render()"); pg.evaluate("FOLD['ent-tq']=true;go('recepcion')")
    entrada('WLRCO170926', 'T3', '100')
    chk([k for k in pg.evaluate("[...encodeAll().keys()]") if 'TQ/' in k and k.startswith('q2:')].__len__() == 1, "en Abel el traslado va como 'q2:TQ/…'")
    pg.evaluate("mqSet(1);render()")
    # hoja de Modo piso
    pg.evaluate("setPiso(true);go('pent')"); pg.wait_for_timeout(150)
    pg.select_option('[data-pr="1:origin"]', index=1); pg.select_option('[data-pr="1:tank"]', 'T5'); pg.fill('[data-pr="1:lot"]', 'WLRLE051026')
    pg.fill('[data-pr="1:k0"]', '1000'); pg.fill('[data-pr="1:tempT"]', '63.9'); pg.fill('[data-pr="1:tempP"]', '57-62'); pg.fill('[data-pr="1:kgbox"]', '34'); pg.fill('[data-pr="1:desp"]', '0')
    pg.evaluate("document.querySelector('[data-pt2=\"1\"]').open=true")  # v1.39.0: «otro tanque» va plegado
    pg.select_option('[data-pr="1:t2"]', 'T6'); pg.fill('[data-pr="1:k2z0"]', '2000'); pg.click('#pn_save'); pg.wait_for_timeout(150)
    chk('más de lo que entró' in pg.inner_text('#pd_1') and pg.evaluate("!R_('WLRLE051026')"), 'Modo piso: kg del otro tanque mayores a lo que entró no se guardan')
    pg.fill('[data-pr="1:k2z0"]', '400'); pg.fill('[data-pr="1:tt2"]', '57'); pg.click('#pn_save'); pg.wait_for_timeout(150)
    chk(pg.evaluate(DIST, 'WLRLE051026') == {'T5': 600, 'T6': 400}, 'Modo piso: entrada repartida T5 600 y T6 400')
    for w_, h_ in [(820, 1180), (390, 844)]:
        pg.set_viewport_size({'width': w_, 'height': h_}); pg.wait_for_timeout(120); chk(not overflow(pg), f'hoja de Modo piso sin scroll de lado en {w_} px')
        pg.evaluate("setPiso(false);go('lote:WLREM190926')"); pg.wait_for_timeout(120); chk(not overflow(pg), f'lote con traslados sin scroll de lado en {w_} px')
        pg.evaluate("form={t:'lot'};FOLD['ent-tq']=true;go('recepcion');form={t:'lot'};render()"); pg.wait_for_timeout(120); chk(not overflow(pg), f'Entrada con otro tanque sin scroll de lado en {w_} px')
        pg.screenshot(path=os.path.join(OUT, f'traslados_{w_}.png'), full_page=True); pg.evaluate("setPiso(true);go('pent')")
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
