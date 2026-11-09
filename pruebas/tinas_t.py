"""v1.42.0 · Recepción por tinas (pedido del usuario, 8/nov/2026).
- 6 tanques × 30 tinas con número fijo (T1 = 1–30 … T6 = 151–180); cada tina guarda sus kg exactos y su talla (de su maquila).
- Se capturan como las hieleras: tocar la tina, escribir kg, tocar la talla → ✔ Lista y pasa a la siguiente; Enter repite la talla.
- Una tina = un lote y una talla; ocupada no se puede usar (tampoco por otra maquila); en 30 el tanque está lleno.
- Muerta, débil, rechazo y despatada van aparte (la despatada cuenta como inventario, sin tina). Temperaturas: un número por casilla.
- Al empacar, la app avisa que falta decir de qué tinas salió; sugiere tinas y al guardar se vacían. Pasar de una tina a otra.
- 3D: 30 tinas por tanque; tocar una tina dice tina, tanque, kg, talla, lote y maquila. Formato de recepción en PDF.
- Se comparte entre equipos (R.tn y TS/<id>) y sobrevive a un respaldo.
- Calendario en las fechas (flatpickr) y teclado de números en todas las casillas de números.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/tinas_t.py"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recep import recibir
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','%s');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))"  # usuarios SOLO para pruebas
def entrar(pg, kp='0'):
    pg.goto(BASE); pg.evaluate(FIX % (kp, USERS)); pg.reload()
    pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(250)
J = lambda pg, x: pg.evaluate(x)
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------- 1 · captura en computadora (sin teclado de la app) ----------
    c = b.new_context(viewport={'width': 1280, 'height': 900}); pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    entrar(pg)
    J(pg, "go('recepcion')"); pg.click('[data-a=nf]'); pg.wait_for_timeout(200)
    chk(J(pg, "V.v") == 'rtin' and pg.locator('#tngrid .tnt').count() == 30, 'Nueva recepción abre la pantalla por tinas con las 30 tinas de T1')
    chk([pg.inner_text(f'[data-rt="tk:{t}"] b') for t in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']] == ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'], 'botones de los 6 tanques')
    chk(pg.locator('#tnt1 b').inner_text() == 'Tina 1' and pg.locator('#tnt30 b').inner_text() == 'Tina 30', 'T1 = tinas 1 a 30')
    pg.click('[data-rt="tk:T6"]'); pg.wait_for_timeout(80)
    chk(pg.locator('#tnt151').count() == 1 and pg.locator('#tnt180').count() == 1, 'T6 = tinas 151 a 180')
    pg.click('[data-rt="tk:T1"]'); pg.wait_for_timeout(80)
    zs = J(pg, "rtZs().map(i=>S[i])")
    chk('desp' not in zs and pg.locator('[data-rt^="z:"]').count() == len(zs), 'la despatada no está entre las tallas de tina (va aparte)')
    chk(pg.locator('#rt_dp').count() == 1, 'casilla «Langosta despatada (kg)» aparte')
    chk(all(pg.get_attribute(f'#{i}', 'inputmode') == 'decimal' for i in ['tn_k1', 'rt_mu', 'rt_db', 'rt_rz', 'rt_tpn', 'rt_tpx']), 'kg y temperaturas abren el teclado de números')
    pg.select_option('#rt_fo', '1'); pg.fill('#rt_fl', 'wlrco081126a')
    pg.click('#tnt1'); pg.fill('#tn_k1', '34.95'); pg.click('[data-rt="z:0"]'); pg.wait_for_timeout(50)
    chk(J(pg, "RT.act") == 2 and 'is-done' in pg.get_attribute('#tnt1', 'class'), 'tina 1 ✔ Lista y pasa sola a la tina 2')
    pg.fill('#tn_k2', '34.7'); pg.press('#tn_k2', 'Enter'); pg.wait_for_timeout(50)
    chk(J(pg, "RT.tn[2].z") == J(pg, "S[0]") and J(pg, "RT.act") == 3, 'Enter repite la talla anterior y pasa a la siguiente')
    pg.fill('#tn_k3', '2'); pg.press('#tn_k3', 'Enter'); pg.fill('#tn_k4', '36.6'); pg.click('[data-rt="z:1"]'); pg.wait_for_timeout(50)
    pg.fill('#tn_k5', '20'); pg.wait_for_timeout(30)
    s = pg.inner_text('#rtsum')
    chk('3' in s and '71.65' in s and '36.6' in s and 'T1: 4 de 30 tinas' in s, 'resumen en vivo por talla (tinas y kg) y tinas del tanque')
    # errores junto al campo
    pg.fill('#tn_k5', ''); pg.click('[data-rt=sv]'); pg.wait_for_timeout(80)
    chk('Temperatura de T1' in pg.inner_text('#app') and J(pg, "document.activeElement.id") == 'rt_ttT1', 'falta la temperatura de T1: lo dice y pone el cursor ahí')
    pg.fill('#rt_ttT1', '57.6'); pg.fill('#rt_tpn', '62.2'); pg.fill('#rt_tpx', '57.7'); pg.click('[data-rt=sv]'); pg.wait_for_timeout(80)
    chk('mínima no puede ser mayor' in pg.inner_text('#app'), 'temperatura del producto: mínima y máxima, cada una un número')
    pg.fill('#rt_tpn', '57.7'); pg.fill('#rt_tpx', '62.2'); pg.fill('#rt_mu', '21.45'); pg.fill('#rt_dp', '8.45'); pg.fill('#rt_rz', 'diez')
    pg.click('[data-rt=sv]'); pg.wait_for_timeout(80)
    chk('rechazo' in pg.inner_text('#app') and J(pg, "document.activeElement.id") == 'rt_rz', 'rechazo con letras: avisa junto al campo')
    pg.fill('#rt_rz', ''); pg.click('[data-rt=sv]'); pg.wait_for_timeout(250)
    r = J(pg, "R_('WLRCO081126A')")
    chk(J(pg, "V.v+':'+V.id") == 'lote:WLRCO081126A', 'guardar lleva al lote')
    chk(r and r['tn'] == [[1, J(pg, 'S[0]'), 34950], [2, J(pg, 'S[0]'), 34700], [3, J(pg, 'S[0]'), 2000], [4, J(pg, 'S[1]'), 36600]], f'cada tina con sus gramos exactos y su talla ({r and r.get("tn")})')
    chk(r['mu'] == 21.45 and r['tts'] == {'T1': 57.6} and r['tpn'] == 57.7 and r['tpx'] == 62.2 and r['tank'] == 'T1' and r['kgbox'] is None, 'muerta, temperatura por tanque y producto mínima/máxima guardadas')
    chk(J(pg, "bal('WLRCO081126A')") == 108250 + 8450 and J(pg, "rcv('WLRCO081126A','desp')") == 8450, 'inventario = tinas + despatada aparte')
    chk(J(pg, "JSON.stringify(tqDistZ('WLRCO081126A'))") == json.dumps({J(pg, 'S[0]'): {'T1': 71650}, J(pg, 'S[1]'): {'T1': 36600}, J(pg, 'S[2]'): {}, J(pg, 'S[3]'): {}, 'desp': {}}, separators=(',', ':')), 'el tanque cuenta lo que hay en sus tinas')
    t = pg.inner_text('#app')
    chk('4 tinas' in t and 'Temp. T1 57.6 °F' in t and 'mín 57.7 · máx 62.2' in t and 'Muerta 21.45 kg' in t, 'el lote enseña tinas, temperaturas separadas y muerta')
    chk(pg.locator('.fold[data-fold="lot-tn:WLRCO081126A"]').count() == 1, 'el lote tiene su plegable «Tinas»')
    # ---------- 2 · ocupadas, otra maquila y tanque lleno ----------
    recibir(pg, 'WLREM081126B', pv='2', kz=[0, 0, 0, 2], tank='T1')
    r2 = J(pg, "R_('WLREM081126B')")
    chk(r2 and r2['tn'][0][0] == 5, f'la siguiente recepción empieza en la primera tina libre (5): {r2 and r2["tn"]}')
    J(pg, "go('rtin')"); pg.wait_for_timeout(100)
    chk('tnocc' in pg.get_attribute('#tnt1', 'class') and pg.locator('#tn_k1').count() == 0 and 'WLRCO081126A' in pg.inner_text('#tnt1'), 'tina ocupada: dice qué lote tiene y no se puede escribir')
    chk(J(pg, "RT.act") == 6, 'empieza en la primera tina libre')
    # llenar T2 con otra maquila
    J(pg, "mqSet(2);render()"); pg.wait_for_timeout(100)
    recibir(pg, 'WLRAB081126', pv='1', kz=[30 * 34], tank='T2', por=34)
    chk(J(pg, "R_('WLRAB081126').tn.length") == 30 and J(pg, "R_('WLRAB081126').tn[29][0]") == 60, 'la otra maquila llena T2 (tinas 31–60)')
    J(pg, "mqSet(1);render()"); pg.wait_for_timeout(100)
    J(pg, "RT=null;go('rtin')"); pg.wait_for_timeout(100)
    chk('Lleno' in pg.inner_text('[data-rt="tk:T2"]'), 'T2 lleno con las tinas de otra maquila')
    pg.click('[data-rt="tk:T2"]'); pg.wait_for_timeout(80)
    chk(pg.locator('#tngrid .tnocc').count() == 30 and 'Abel' in pg.inner_text('#tnt31') or 'Maquila' in pg.inner_text('#tnt31') or J(pg, "mqName(2)") in pg.inner_text('#tnt31'), 'las tinas de otra maquila salen ocupadas con su maquila')
    # dos equipos: la tina se ocupó mientras se capturaba
    pg.click('[data-rt="tk:T3"]'); pg.wait_for_timeout(60); pg.select_option('#rt_fo', '1'); pg.fill('#rt_fl', 'WLRCO091126')
    pg.fill('#tn_k61', '30'); pg.click('[data-rt="z:0"]'); pg.fill('#rt_ttT3', '58'); pg.fill('#rt_tpn', '57'); pg.fill('#rt_tpx', '60')
    J(pg, "(()=>{const r=R_('WLREM081126B');r.tn.push([61,r.tn[0][1],5000]);save()})()")
    pg.click('[data-rt=sv]'); pg.wait_for_timeout(100)
    chk('ya tiene langosta' in pg.inner_text('#app') and J(pg, "R_('WLRCO091126')") is None, 'si otro equipo ocupó la tina, no guarda y lo dice')
    J(pg, "RT=null;msg='';go('recepcion')")
    # ---------- 3 · empacar → sacar de tinas ----------
    J(pg, """(()=>{const o={id:uidN(),etd:dLoc(),lines:[{id:1,city:'PVG',cons:0,boxes:2,z:[2,0,0,0]}],sh:{}};ST.OR.push(o);const si=shipFor(o,'PVG',0);
      ST.B['WLRCO081126A'].push({c:20,k:TKEY[0],d:si,o:o.id+'.1',seq:uidN()},{c:20,k:TKEY[0],d:si,o:o.id+'.1',seq:uidN()});save()})()""")
    p0 = J(pg, "tnPend('WLRCO081126A')")
    chk(p0['t'] > 0 and abs(p0['t'] - 2 * J(pg, 'pesoStd().p') * 1000) < 1, f'al empacar 2 hieleras, faltan {p0["t"]} g por sacar de tinas')
    chk(any('Sacar de tinas' in x['ti'] for x in J(pg, "ntFalta()")), 'la campana avisa «Sacar de tinas»')
    J(pg, "go('lote:WLRCO081126A')"); pg.wait_for_timeout(100)
    chk(pg.locator('#tnpend').count() == 1, 'el lote dice que faltan tinas por sacar')
    pg.click('#tnpend [data-tns=open]'); pg.wait_for_timeout(100)
    sug = J(pg, "TNS.sac")
    chk(sug.get('3') == '2' and sum(float(v) for v in sug.values()) == 2 * J(pg, 'pesoStd().p'), f'sugiere primero la tina con menos kg: {sug}')
    pg.click('[data-tns=sv]'); pg.wait_for_timeout(150)
    chk(J(pg, "tnPend('WLRCO081126A').t") == 0 and J(pg, "tnNow(R_('WLRCO081126A')).get(3).g") == 0, 'al guardar ya no falta nada y la tina 3 queda vacía (libre)')
    chk(J(pg, "tnOcc().has(3)") is False, 'la tina vacía queda libre para otra recepción')
    # pasar a otra tina
    pg.click('[data-tnp=open]'); pg.wait_for_timeout(80); pg.select_option('#tnp_n', '4'); pg.wait_for_timeout(80)
    pg.fill('#tnp_g', '10'); pg.select_option('#tnp_a', '150'); pg.click('[data-tnp=sv]'); pg.wait_for_timeout(100)
    m = J(pg, "(()=>{const m=tnNow(R_('WLRCO081126A'));return [m.get(4).g,m.get(150).g,m.get(150).z===S[1]]})()")
    chk(m == [26600, 10000, True], f'pasar 10 kg de la tina 4 a la 150 (misma talla): {m}')
    chk(J(pg, "JSON.stringify(tqDist('WLRCO081126A'))").find('"T5":10000') >= 0, 'el kilo pasado cuenta en el tanque nuevo (T5)')
    # ---------- 4 · se comparte y sobrevive al respaldo ----------
    enc = J(pg, "(()=>{const m=encodeST();return [...m.keys()].filter(k=>k.startsWith('TS/')).length+':'+JSON.stringify(m.get('R/WLRCO081126A')[1].tn)})()")
    chk(enc.startswith(f'{J(pg, "ST.TS.length")}:') and '34950' in enc, 'salidas de tina viajan como TS/<id> y las tinas dentro del lote')
    rt = J(pg, "(()=>{const d=decodeST([...encodeST()].map(([k,v])=>[k,JSON.parse(v[0])]));return JSON.stringify([d.TS.length,R_('WLRCO081126A').tn.length,d.R.find(r=>r.lot==='WLRCO081126A').tts])})()")
    chk(rt == f'[{J(pg, "ST.TS.length")},4,{{"T1":57.6}}]', f'otro equipo lo arma igual ({rt})')
    cl = J(pg, "(()=>{const d=cleanST(JSON.parse(JSON.stringify(ST)),true);return [d.TS.length,d.R.find(r=>r.lot==='WLRCO081126A').tn.length,d.R.find(r=>r.lot==='WLRCO081126A').mu]})()")
    chk(cl == [J(pg, "ST.TS.length"), 4, 21.45], 'un respaldo restaurado conserva tinas y salidas')
    chk(J(pg, "tnClean([[1,'491-610',100],[1,'491-610',5],[181,'x',3],[2,'<b>',3]])") == [[1, '491-610', 100]], 'tinas repetidas, fuera de 1–180 o con texto raro se descartan')
    # ---------- 5 · 3D y PDF ----------
    J(pg, "go('inicio')"); pg.wait_for_timeout(700)
    chk(J(pg, "T3.M.O.filter(o=>o.C).every(o=>o.C.length===30)"), '3D: cada tanque tiene sus 30 tinas')
    chk(J(pg, "T3.M.O.find(o=>o.tk==='T1').C.filter(c=>c.o).length") == 4, '3D: T1 con 4 tinas ocupadas (1, 2, 4 y la 5 del otro lote)')
    pg.locator('.t3v').scroll_into_view_if_needed(); sp = J(pg, "t3Spot('T1')"); pg.mouse.click(sp['x'], sp['y']); pg.wait_for_timeout(900)
    sp = J(pg, "t3Spot('T1',0)"); pg.mouse.click(sp['x'], sp['y']); pg.wait_for_timeout(200)
    pk = pg.inner_text('.t3pick') if pg.locator('.t3pick').count() else ''
    chk('Tina 1 · T1' in pk and '34.95 kg' in pk and 'WLRCO081126A' in pk, f'3D: tocar la tina 1 dice tina, tanque, kg, talla y lote ({pk!r})')
    pdf = J(pg, "pdfRecepcion('WLRCO081126A').then(d=>[d.name,d.u8.length])")
    chk(pdf[0].startswith('PROPESA_Recepcion_WLRCO081126A') and pdf[1] > 3000, f'formato de recepción en PDF ({pdf})')
    chk(J(pg, "document.querySelectorAll('input[type=number]:not([inputmode])').length") == 0, 'ninguna casilla de números sin su teclado de números')
    c.close()
    # ---------- 6 · celular con el teclado de la app ----------
    c = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True); pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    entrar(pg, '1'); J(pg, "go('rtin')"); pg.wait_for_timeout(200)
    chk(pg.locator('#tnpad').count() == 1 and pg.get_attribute('#tn_k1', 'readonly') is not None, 'celular: teclado de la app y las casillas no abren el teclado del teléfono')
    for ch in '34.95': pg.tap(f'#tnpad [data-tnk="d:{ch}"]')
    chk(pg.input_value('#tn_k1') == '34.95' and pg.inner_text('#tnpv') == '34.95' and pg.inner_text('#tnpdt') == 'Tina 1', 'el teclado escribe 34.95 (con punto) en la tina 1')
    pg.tap('#tnpad [data-tnk="z:0"]'); pg.wait_for_timeout(60)
    for ch in '2': pg.tap(f'#tnpad [data-tnk="d:{ch}"]')
    pg.tap('#tnpad [data-tnk=next]'); pg.wait_for_timeout(60)
    chk(J(pg, "RT.tn[1].z===S[0]&&RT.tn[2].g==='2'&&RT.tn[2].z===S[0]&&RT.act===3"), '«Siguiente» repite la talla y pasa a la tina 3')
    chk(J(pg, "document.documentElement.scrollWidth<=innerWidth"), 'celular: sin desbordes')
    # calendario
    pg.tap('#rt_fd'); pg.wait_for_timeout(300)
    chk(J(pg, "!!document.querySelector('.flatpickr-calendar.open .flatpickr-monthDropdown-months')"), 'fecha: al tocarla sale el calendario con el mes')
    pg.locator('.flatpickr-calendar.open .flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)').nth(2).tap(); pg.wait_for_timeout(200)
    chk(pg.input_value('#rt_fd').startswith('03/') and not J(pg, "!!document.querySelector('.flatpickr-calendar.open')"), f'al escoger el día se escribe dd/mm/aaaa y el calendario se va ({pg.input_value("#rt_fd")})')
    pg.fill('#rt_fd', ''); pg.focus('#rt_fd'); pg.keyboard.type('07112026'); pg.keyboard.press('Escape')
    chk(pg.input_value('#rt_fd') == '07/11/2026', 'también se puede escribir: las diagonales salen solas')
    c.close(); b.close()
print('Errores JS:', errs if errs else 'ninguno')
print('RESULTADO:', 'TODO BIEN' if not fails and not errs else f'{len(fails)} fallas')
