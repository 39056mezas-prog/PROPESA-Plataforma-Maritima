"""v1.25.0 · Pedidos del usuario del 27/oct/2026 (después de probar la v1.24.0 con sus Excel):
1. Una orden puede llevar hieleras de lotes de OTRA maquila en el mismo empaque; al cerrar, los kg salen del tanque de esa maquila,
   y reabrir los regresa. El lote de David enseña en qué orden de PROPESA va.
2. Panel general: tablero de tanques con todas las maquilas juntas.
3. Entrada repartida en dos tanques: kg EXACTOS de cada talla en el otro tanque (vista completa y Modo piso).
4. Camión compartido: embarques abiertos de varias maquilas en un camión; «Camión nuevo» con un solo embarque ya no «no hace nada».
5. Arreglos de la prueba con los Excel: fecha en las salidas (el Balance las cuenta), todos los envíos en «vivas al llegar», aviso y
   corrección del código de lote mal escrito, cajas de 15 kg en el PDF de Envíos, «Cambio de talla» para la salida incompleta.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/v125_t.py"""
import os, re
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',role:'piso',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
def login(pg, em):
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")
def entrada(pg, lot, kz, tank='T1', t2=None, z2=None, fecha='20/10/2026', prov='1'):
    pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.wait_for_timeout(100)
    pg.fill('#fd', fecha); pg.fill('#fh', '12:00'); pg.select_option('#fo', prov); pg.select_option('#ft', tank)
    pg.fill('#ftt', '58'); pg.fill('#ftp', '59'); pg.fill('#fl', lot); pg.fill('#fkb', '36'); pg.fill('#fdes', '0')
    for i, v in enumerate(kz): pg.fill(f'#fk{i}', str(v))
    if t2:
        pg.select_option('#ft2', t2)
        for i, v in (z2 or {}).items(): pg.fill(f'#fk2z{i}', str(v))
    pg.click('[data-a=sv]'); pg.wait_for_timeout(150)
def orden(pg, etd, city, z):
    pg.evaluate("go('ordenes')"); pg.fill('#no_etd', etd); pg.click('[data-oa=new]'); pg.wait_for_timeout(100)
    pg.select_option('#ol_city', city)
    for i, v in enumerate(z): pg.fill(f'#ol_z{i}', str(v))
    pg.click('[data-oa=ln]'); pg.wait_for_timeout(150)
def empacar(pg, lot_btn, cats):
    pg.locator('.pklb', has_text=lot_btn).first.click(); pg.wait_for_timeout(80)
    for k in cats:
        fid = pg.evaluate("()=>{const e=[...document.querySelectorAll('input.pkc')].find(x=>x.value==='');return e?e.id:''}")
        pg.fill('#' + fid, '28'); pg.click(f'#{fid.replace("pk_c", "pkr")} [data-pk$=":{k}"]'); pg.wait_for_timeout(60)
    b = pg.locator('.pkn')
    if b.count() and re.match(r'Guardar \d', b.first.inner_text()): b.first.click(); pg.wait_for_timeout(100)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1)")

    # ---------- 3. entrada repartida: kg exactos por talla en el otro tanque
    entrada(pg, 'WLRCO201026', [100, 50, 20, 10], 'T1', 'T2', {0: 30, 1: 61})
    chk(pg.locator('.er', has_text='Mediana: en el otro tanque no puede haber más de lo que entró').count() > 0, 'no deja poner en el otro tanque más de lo que entró de una talla')
    pg.fill('#fk2z1', '0'); pg.fill('#fk2z2', '20'); pg.fill('#fk2z3', '10'); pg.click('[data-a=sv]'); pg.wait_for_timeout(150)
    dz = pg.evaluate("(d=>({t1:[S.map(z=>d[z].T1||0)],t2:[S.map(z=>d[z].T2||0)]}))(tqDistZ('WLRCO201026'))")
    chk(dz['t2'][0][:4] == [30000, 0, 20000, 10000] and dz['t1'][0][:4] == [70000, 50000, 0, 0], f'T2 tiene exactamente Chica 30 · Grande 20 · Jumbo 10 y T1 lo demás ({dz})')
    chk(pg.evaluate("(ST.TQ||[]).find(x=>x.lot==='WLRCO201026').z['851-1220']") == 20, 'el traslado de la entrada guarda los kg por talla (z)')
    pg.evaluate("go('recepcion');TQSEL='T2';render()"); t = pg.inner_text('.tqc')
    chk('60.0 kg' in t and '20.0' in t, 'el tablero de Entrada enseña en T2 lo capturado (60 kg, 20 de Grande)')
    pg.evaluate("go('lote:WLRCO201026')"); t = pg.inner_text('#tqc')
    chk('Chica 30.0' in t and 'Grande 20.0' in t and 'Mediana 50.0' in t, 'el lote enseña las tallas de cada tanque')
    # traslado viejo (solo kg) sigue repartiendo en proporción
    pg.evaluate("tqAdd('WLRCO201026','T1','T3',12);save()")
    t3 = pg.evaluate("S.map(z=>(tqDistZ('WLRCO201026')[z].T3||0))")
    chk(sum(t3) == 12000 and t3[0] > 0 and t3[1] > 0 and t3[2] == 0, f'un traslado sin tallas reparte en la proporción de lo que hay en ese tanque ({t3})')
    # Modo piso: hoja de entradas con kg por talla del otro tanque
    pg.evaluate("go('pent')"); pg.wait_for_timeout(150)
    chk(pg.locator('[data-pr$=":k2z0"]').count() > 0 and pg.locator('[data-pr$=":k2t"]').count() == 0, 'Modo piso: la entrada pide kg de cada talla para el otro tanque')
    pg.evaluate("go('inicio')")

    # ---------- 5. código de lote mal escrito: aviso y se puede corregir
    entrada(pg, 'WLRCOO51026', [40, 10, 0, 0], 'T1', fecha='05/10/2026')
    pg.evaluate("go('lote:WLRCOO51026')"); t = pg.inner_text('main')
    chk('no tiene la forma WLR + clave + fecha' in t and 'letra O' in t, 'avisa del código WLRCOO51026 (letra O en lugar de cero)')
    pg.click('#lotav [data-a=el]'); pg.wait_for_timeout(100)
    chk(pg.locator('#fl').is_enabled(), 'el código del lote se puede corregir mientras no tenga hieleras')
    pg.fill('#fl', 'WLRCO051026'); pg.click('[data-a=sv]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("!!R_('WLRCO051026')&&!R_('WLRCOO51026')&&bal('WLRCO051026')===50000&&!ST.L.some(x=>x.lot==='WLRCOO51026')"), 'al corregirlo se cambian la entrada y sus movimientos (50 kg en WLRCO051026)')
    chk(pg.evaluate("lotWarn(R_('WLRCO051026')).length") == 0, 'con el código corregido ya no avisa')
    entrada(pg, 'WLREM051026', [10, 0, 0, 0], 'T1', fecha='05/10/2026')
    chk(pg.evaluate("lotWarn(R_('WLREM051026')).some(w=>/clave del proveedor \\(CO\\)/.test(w.t))"), 'avisa si el código no lleva la clave del proveedor')

    # ---------- 1. orden con hieleras de otra maquila
    pg.evaluate("mqSet(3)")  # David
    entrada(pg, 'WLRDA131026', [200, 100, 0, 0], 'T4')
    chk(pg.evaluate("bal('WLRDA131026')") == 300000, 'David: lote WLRDA131026 con 300 kg')
    pg.evaluate("mqSet(1)")
    orden(pg, '16/10/2026', 'HKG', [2, 2, 0, 0])
    pg.evaluate("go('empaque')"); pg.locator('[data-go^="empacar:"]').first.click(); pg.wait_for_timeout(150)
    chk(pg.locator('.pklx .pklb.pkx', has_text='WLRDA131026').count() == 1 and 'maquila david' in pg.inner_text('.pklx').lower(), 'Empaque: los lotes de David salen aparte, con «Maquila David»')
    chk(pg.evaluate("PKD.lot") is None or not str(pg.evaluate("PKD.lot")).endswith('@3'), 'un lote de otra maquila nunca se elige solo')
    empacar(pg, 'WLRDA131026', ['B', 'R'])
    empacar(pg, 'WLRCO201026', ['B', 'R'])
    chk(pg.evaluate("ST.B['WLRDA131026@3'].length") == 2 and pg.evaluate("ST.B['WLRCO201026'].length") == 2, 'se empacaron 2 hieleras de David y 2 de PROPESA en la misma orden')
    pg.evaluate("go('emb:0')"); t = pg.inner_text('#emb_lotes')
    chk('WLRDA131026 · David' in t and 'WLRCO201026' in t, 'el embarque enseña «Por lote» con el lote de David y su maquila')
    pg.evaluate("ST.OR.forEach(o=>{o.f={...(o.f||{}),hf:'08:00',re:'Ana',ev:'S',pl:'X',ch:'X',tel:'0',tp:'48',to:'T1',tq:'T1'}});save();render()")
    pg.click('[data-a=cp]'); pg.wait_for_timeout(200)
    chk(pg.evaluate("ST.P[0].closed&&!ST.P[0].sf"), 'el embarque cierra sin «salida incompleta»')
    chk(pg.evaluate("bal('WLRCO201026')") == 180000 - 32000 - 12000 + 12000, 'PROPESA: salieron 32 kg de su lote')
    chk(pg.evaluate("STX[3].L.filter(x=>x.type==='SALIDA_EMBARQUE').reduce((a,x)=>a+x.m,0)") == -32000, 'David: salieron 32 kg de SU tanque (16 Chica + 16 Mediana)')
    chk(pg.evaluate("bal('WLRDA131026@3','491-610')") == 184000, 'la existencia del lote de David baja a 184 kg de Chica')
    pg.evaluate("mqSet(3);go('lote:WLRDA131026')"); t = pg.inner_text('main')
    chk('En órdenes de otra maquila' in t and 'HKG' in t and 'ya salió del tanque' in t, 'el lote de David dice en qué embarque de PROPESA va')
    chk('PROPESA · HKG' in t, 'la salida en el lote de David dice de qué maquila y embarque fue')
    pg.evaluate("mqSet(1);go('emb:0')"); pg.click('[data-a=op]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("STX[3].L.filter(x=>x.type==='SALIDA_EMBARQUE').length") == 0, 'reabrir regresa los kg al tanque de David')
    pg.click('[data-a=cp]'); pg.wait_for_timeout(150)
    # enlace al lote de otra maquila
    pg.evaluate("go('lote:WLRDA131026@3')"); pg.wait_for_timeout(100)
    chk(pg.evaluate("MQ") == 3 and pg.evaluate("V.id") == 'WLRDA131026', 'tocar el lote de David lleva a la maquila David')
    pg.evaluate("mqSet(1)")
    # respaldo: las hieleras de otra maquila sobreviven a cleanST
    chk(pg.evaluate("(cleanST(JSON.parse(JSON.stringify(mqDump())),true).B['WLRDA131026@3']||[]).length") == 2, 'el respaldo conserva las hieleras de otra maquila')
    # PDF del embarque y de envíos con el nombre de la maquila
    s = pg.evaluate("(async()=>{const d=await pdfMake('emb',0);let s='';d.u8.forEach(c=>s+=String.fromCharCode(c));return s})()")
    chk('WLRDA131026 \\267 David' in s or 'WLRDA131026 · David' in s or 'David' in s, 'el PDF del embarque nombra el lote de David')

    # ---------- 4. camión compartido entre maquilas
    orden(pg, '20/10/2026', 'PVG', [3, 0, 0, 0])
    pg.evaluate("mqSet(2)")  # Abel
    orden(pg, '20/10/2026', 'XMN', [5, 0, 0, 0])
    pg.evaluate("go('embarques')"); pg.wait_for_timeout(150); t = pg.inner_text('main')
    chk('PROPESA' in t and 'Abel' in pg.inner_text('.tcard') or 'PROPESA' in pg.inner_text('.tcard'), 'Abel ve en su camión el embarque abierto de PROPESA')
    chk(pg.evaluate("truckPlan('').TP.length") == 2, 'un solo camión lleva los embarques de las dos maquilas')
    u = pg.evaluate("ST.P.find(p=>!p.closed).u")
    pg.select_option(f'select[data-tk="{u}"]', '+'); pg.wait_for_timeout(150)
    chk(pg.evaluate("trucks().length") == 2, '«Camión nuevo» con dos embarques: ahora hay 2 camiones')
    t = pg.locator('.ttab').count()
    chk(t == 2, 'se dibujan los 2 camiones (v1.26.0: en pestañas)')
    pg.click('#ttab_1'); pg.wait_for_timeout(100)
    uP = pg.evaluate("STX[1].P.find(p=>!p.closed).u")
    tk2 = pg.evaluate(f"ST.P.find(p=>p.u==='{u}').tk")
    pg.select_option(f'select[data-tk="{uP}"]', tk2); pg.wait_for_timeout(150)
    chk(pg.evaluate(f"STX[1].P.find(p=>p.u==='{uP}').tk") == tk2 and pg.evaluate("trucks().length") == 1, 'el embarque de PROPESA se pasa al camión del de Abel (se guarda en PROPESA)')
    opt = pg.evaluate(f"[...document.querySelector('select[data-tk=\"{uP}\"]').options].map(o=>o.textContent+'|'+o.disabled)")
    chk(any('Camión nuevo|false' == o for o in opt), 'con dos embarques en el camión, «Camión nuevo» sí se puede')
    pg.evaluate("mqSet(1);go('embarques')"); pg.wait_for_timeout(100)
    chk(pg.evaluate("truckPlan(trucks()[0]).TP.length") == 2 and 'varias maquilas' in pg.inner_text('.tcard'), 'PROPESA ve el mismo camión con los dos embarques')
    pg.evaluate("mqSet(2)"); pg.evaluate("go('embarques')")
    u1 = pg.evaluate("ST.P.find(p=>!p.closed).u")
    pg.evaluate("mqSet(1)")

    # ---------- 2. Panel general: tanques juntos
    pg.evaluate("go('general')"); pg.wait_for_timeout(150)
    chk(pg.locator('.tqgen [data-tq=T4]').count() == 1, 'el Panel general tiene el tablero de tanques')
    pg.click('.tqgen [data-tq=T4]'); pg.wait_for_timeout(100); t = pg.inner_text('.tqgen .tqc')
    chk('David' in t and 'WLRDA131026' in t, 'al tocar T4 sale lo de David con su lote')
    pg.click('.tqgen [data-tq=T1]'); pg.wait_for_timeout(100); t = pg.inner_text('.tqgen .tqc')
    chk('PROPESA' in t and 'Chica' in t, 'T1 enseña PROPESA con sus tallas')
    tot = pg.evaluate("TK.reduce((a,t)=>a+0,0)")
    for w in (390, 820):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.wait_for_timeout(100)
        chk(not overflow(pg), f'Panel general sin desbordes a {w} px')
    pg.set_viewport_size({'width': 1440, 'height': 900})

    # ---------- 5. fecha en salidas y Balance
    pg.evaluate("mqSet(1);go('lote:WLRCO051026')"); pg.wait_for_timeout(100)
    chk(pg.input_value('#mvd') != '', 'el movimiento trae la fecha (hoy de inicio)')
    pg.select_option('#ty', 'CONGELACION'); pg.select_option('#sz', '491-610'); pg.fill('#kg', '5'); pg.fill('#mvd', '06/10/2026'); pg.fill('#mvn', 'Folio 1'); pg.click('[data-a=mv]'); pg.wait_for_timeout(100)
    chk(pg.evaluate("mvISO(ST.L.filter(x=>x.type==='CONGELACION').pop().t)") == '2026-10-06', 'la salida para congelar queda con su fecha (06/10/2026)')
    bal_ = pg.evaluate("hjBal(hjP('2026-10-01|2026-10-10|'))")
    chk(abs(bal_['con'] - 5) < 1e-9, 'el Balance del 1 al 10 de octubre cuenta los 5 kg para congelar')
    pg.fill('#kg', '1'); pg.fill('#mvd', '01/01/2099'); pg.click('[data-a=mv]'); pg.wait_for_timeout(100)
    chk('después de hoy' in pg.inner_text('main'), 'no deja una fecha futura')

    # ---------- 5. Cambio de talla para la salida incompleta
    orden(pg, '21/10/2026', 'PVG', [0, 0, 2, 0])
    pg.evaluate("(o=>go('empacar:'+o.id+'.'+o.lines[0].id))(ST.OR.find(o=>o.etd==='2026-10-21'))"); pg.wait_for_timeout(150)
    empacar(pg, 'WLRCO051026', ['V', 'V'])
    i = pg.evaluate("ST.P.findIndex(p=>!p.closed&&p.n.includes('21/10'))")
    pg.evaluate(f"ST.OR.forEach(o=>{{o.f={{...(o.f||{{}}),hf:'08:00',re:'Ana',ev:'S',pl:'X',ch:'X',tel:'0',tp:'48',to:'T1',tq:'T1'}}}});save();go('emb:{i}')"); pg.click('[data-a=cp]'); pg.wait_for_timeout(150)
    chk(pg.evaluate(f"(ST.P[{i}].sf||[]).reduce((a,x)=>a+x[2],0)") == 32000, 'sin Grande en el lote: salida incompleta de 32 kg')
    pg.evaluate("go('lote:WLRCO051026')"); pg.wait_for_timeout(100)
    chk(pg.locator('details.rcz[open]').count() == 1 and 'faltaron 32.00 kg de Grande' in pg.inner_text('.rcz'), 'el lote abre «Cambio de talla» y dice lo que faltó')
    pg.select_option('#rz_de', '491-610'); pg.select_option('#rz_a', '851-1220'); pg.fill('#rz_kg', '32'); pg.click('[data-a=rcz]'); pg.wait_for_timeout(100)
    chk(pg.evaluate("bal('WLRCO051026','851-1220')") == 32000 and pg.evaluate("bal('WLRCO051026')") == 45000, 'pasaron 32 kg de Chica a Grande; el total del lote no cambió')
    pg.evaluate(f"go('emb:{i}')"); pg.click(f'[data-sfa]'); pg.wait_for_timeout(150)
    chk(pg.evaluate(f"!ST.P[{i}].sf") and pg.evaluate("bal('WLRCO051026','851-1220')") == 0, '«Volver a descontar» ya saca todo: sin salida incompleta')

    # ---------- 5. vivas al llegar: todos los envíos
    n = pg.evaluate("for(let k=0;k<35;k++)ST.P.push({u:uidS(),n:'PVG · X · '+k,z0:'',col:'#000',exp:0,h:1,z:[],c:[],alive:null,closed:true});save();ST.P.filter(p=>p.closed).length")
    pg.evaluate("go('cierre')"); pg.wait_for_timeout(150)
    chk(pg.locator('table.arrt tbody tr').count() >= n, f'Revisión enseña todos los envíos cerrados ({n}), no solo 30')

    # ---------- 5. PDF de Envíos con cajas de 15 kg (Abel)
    s = pg.evaluate("(()=>{const xs=[{kg:1500000,cajas:100},{kg:750000,cajas:50}];const kps=[...new Set(xs.map(x=>Math.round(x.kg/x.cajas/1000)))];return kps})()")
    chk(s == [15], 'Abel: las cajas se cuentan de 15 kg')
    # ---------- 6. Temperatura: rangos INTERNOS sacados del Excel (29/oct): agua y producto
    chk([pg.evaluate(f"tZv({v},'a').n") for v in (55, 58.2, 61, 63, 64.5)] == ['Óptimo', 'Normal', 'Advertencia', 'Alerta', 'Crítico'], 'agua: 55 óptimo, 58.2 normal, 61 advertencia, 63 alerta, 64.5 crítico')
    chk([pg.evaluate(f"tZv({v},'p').n") for v in (59, 62, 65, 67, 69)] == ['Óptimo', 'Normal', 'Advertencia', 'Alerta', 'Crítico'], 'producto: 59 óptimo, 62 normal, 65 advertencia, 67 alerta, 69 crítico')
    chk(pg.evaluate("[tOut(62,'a'),tOut(62.1,'a'),tOut('60-63','a'),tOut(66,'p'),tOut(66.5,'p'),tAdv(61,'a')]") == [False, True, True, False, True, True], 'rojo: agua arriba de 62 (también en un rango 60-63), producto arriba de 66; 61 en agua es advertencia')
    pg.evaluate("go('temperatura')"); pg.wait_for_timeout(100)
    chk(pg.locator('details.tzc').count() == 1 and 'Crítico' in pg.text_content('details.tzc') and 'Referencia de la industria' in pg.text_content('details.tzc'), 'Temperatura enseña la tabla de rangos')
    pg.fill('#tq_a', '63'); pg.fill('#tq_s', '58'); pg.click('[data-a=tq]'); pg.wait_for_timeout(150)
    chk('ALERTA' in pg.inner_text('#toast'), 'al guardar 63 °F de agua avisa ALERTA')
    chk(pg.locator('#tq_tbl .tqout.tz-est').count() >= 1 and pg.locator('.alb', has_text='Alerta o Crítico').count() == 1, 'la lectura sale marcada y arriba el aviso rojo')
    s = pg.evaluate("(async()=>{const d=await pdfMake('temp','');let s='';d.u8.forEach(c=>s+=String.fromCharCode(c));return s})()")
    chk('Alerta' in s and 'Referencia' not in s and 'interno' in s, 'el PDF de temperatura marca la zona con los rangos internos')
    # ---------- 7. Despatada = merma en Mortalidad final (28/oct)
    entrada(pg, 'WLRCO221026', [100, 0, 0, 0, 10], 'T1', fecha='22/10/2026')
    chk(pg.evaluate("espK('WLRCO221026')") == 100000, 'esperado para el conteo final = sin despatada (100 kg)')
    pg.evaluate("go('cierre')"); pg.fill('[data-fin="WLRCO221026"]', '95'); pg.press('[data-fin="WLRCO221026"]', 'Tab'); pg.wait_for_timeout(150)
    c = pg.evaluate("calc('WLRCO221026')")
    chk(c['dead'] == 5000 and c['desp'] == 10000 and c['mer'] == 15000 and abs(c['pm'] - 15000 / 110000 * 100) < 1e-9, f'merma = 5 kg muertos + 10 kg despatada = 15 kg de 110 ({c["pm"]:.2f}%)')
    row = pg.locator('tr', has_text='WLRCO221026').first.inner_text()
    chk('10.00' in row and '15.00 kg' in row and '13.64%' in row, 'Mortalidad final enseña despatada 10 y merma total 15 kg · 13.64%')
    pg.evaluate("go('lote:WLRCO221026')"); chk('Merma total 15.00 kg' in pg.inner_text('main'), 'el lote enseña la merma total')
    for w in (390, 820):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.evaluate("go('cierre')"); pg.wait_for_timeout(100); chk(not overflow(pg), f'Mortalidad final sin desbordes a {w} px')
        pg.evaluate("go('temperatura')"); pg.wait_for_timeout(100); chk(not overflow(pg), f'Temperatura sin desbordes a {w} px')
    pg.set_viewport_size({'width': 1440, 'height': 900})
    # ---------- 8. La orden ya no pide despatada (29/oct); Empaque sí ofrece Gris
    pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '29/10/2026'); pg.click('[data-oa=new]'); pg.wait_for_timeout(100)
    chk(pg.locator('#ol_z4').count() == 0 and pg.locator('#ol_z3').count() == 1 and 'Despatada' not in pg.inner_text('#ol_f'), 'la orden no pide hieleras de Despatada')
    chk(not errs, f'sin errores en la consola {errs}')
    b.close()
print(f'\n{len(fails)} fallas' if fails else '\nTODO BIEN')
