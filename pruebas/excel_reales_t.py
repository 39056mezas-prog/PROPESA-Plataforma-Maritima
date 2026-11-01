"""v1.19.0 · El Excel de Martha como fuente de verdad (pedido del usuario, 26/oct/2026: «ya tienes sus fórmulas: úsalas para comparar
con mi plataforma»). Carga en la app (modo local) los datos reales de pruebas/datos/excel_reales.json y compara cada número de las
hojas para imprimir con el resultado de las fórmulas del Excel:
 1. Balance 17–27 sep (hoja «LANGOSTA PARA CONGELAR PROPESA», H13:V34): recibido, despatada, envíos, congelación, basura, salidas,
    diferencia física a favor (85.27 kg). Cada recepción: Kg TOTAL = SUM(tallas); cada envío: kg = cajas × 16 y cajas = kg ÷ 16.
 2. Existencia en tanques «PARA ENVIO 14 OCT 26»: Total, kg = SUM; Total, cajas = kg ÷ 16.
 3. Maquila Abel (otra maquila, mismos códigos de lote): «CAJAS DE 15 KG» = kg ÷ 15. Y la existencia del 24/oct, donde el Excel
    tiene SUM(D82:D83) y deja fuera WLRCO211026: la app da el total correcto.
 4. Peso bruto de «Hoja6»: 40 hieleras de 15 kg + 2 tarimas = 735.8 kg.
 5. Maquila Luis Arce: recepción 3,267.75 kg y envío 200 × 16 = 3,200 kg.
 6. Temporada completa (RECEPCIONES!PROPESA): 49,928.95 kg con despatada.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/excel_reales_t.py"""
import os, json
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
X = json.load(open(os.path.join(ROOT, 'pruebas', 'datos', 'excel_reales.json'), encoding='utf-8'))
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def near(a, b, t=0.006): return a is not None and abs(a - b) <= t
USERS = "[{id:1,name:'Martha',email:'admin@propesa.mx',role:'admin',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuario SOLO para pruebas
PV = {'CO': 1, 'EM': 2, 'LE': 3}
def lot(pg, code, date, kz, desp=0, prov=1, tank='T1', time='12:00'):
    d = dict(lot=code, origin=pg.evaluate("id=>pvBy(id)?pvBy(id).n:'Proveedor'", prov), pv=prov, sp=1, tank=tank, rdate=date, time=time or '12:00', tempT='58', tempP='59', kgbox='36', desp='0', **{f'k{i}': v for i, v in enumerate(kz)}, k4=desp)
    er = pg.evaluate("d=>lotErr(d)", d)
    if er: raise Exception(f'{code}: {er}')
    pg.evaluate("d=>{addLot(d);save()}", d)
# un envío del Excel → orden + hieleras empacadas (de cualquier lote con entrada) + embarque cerrado; regresa el índice del embarque
ENV = """([etd,city,cons,z,kp])=>{const id=uidN();ST.OR.push({id,etd,lines:[],sh:{}});const o=ST.OR[ST.OR.length-1];
 const l={id:1,city,cons,boxes:z.reduce((a,b)=>a+b,0),z:S.map((_,i)=>z[i]||0),kp,tar:0,cc:0};o.lines.push(l);const i=shipFor(o,city,cons);
 const lt=ST.R.find(r=>!r.ne).lot;z.forEach((n,t)=>{for(let j=0;j<n;j++)ST.B[lt].push({c:1,k:TKEY[t],d:i,o:o.id+'.1',seq:uidN()})});
 syncShipIdx(i);o.f={hi:'08:00',hf:'10:00',re:'Martha',ev:'S',pl:'X',ch:'X',tel:'0',tp:'48',to:'T1',tq:'T1'};save();closeP(i);return i}"""
def pdf_txt(pg, k, a):
    return pg.evaluate("([k,a])=>(async()=>{const d=await pdfMake(k,a);let s='';for(const b of d.u8)s+=String.fromCharCode(b);return s})()", [k, a])
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
    # ---------- 1) PROPESA · balance 17–27 sep ----------
    pg.evaluate("mqSet(1)")
    for x in X['rec_sep']:
        lot(pg, x['lot'], x['date'], x['k'], x['desp'], PV[x['pk']], 'T' + (x['tank'].strip('.')[:1] or '1'), x['time'])
        t = pg.evaluate("l=>(rcv(l)-rcv(l,'desp'))/1000", x['lot'])
        if not near(t, sum(x['k'])): chk(False, f"{x['lot']}: Kg TOTAL {t} ≠ Excel SUM(tallas) {sum(x['k'])}")
    chk(True, f"las {len(X['rec_sep'])} recepciones: Kg TOTAL = SUM(K:N) del Excel en cada una")
    # destino y consignatario de Taiwán (se agregan como lo haría el Administrador)
    pg.evaluate("dsOwn().push({c:'TPE',n:'Taipéi'});cnOwn().push({k:'OCEAN SPACE',n:'Ocean Space International Co Ltd',p:['TPE'],a:'',c:'',u:''});save();stSync()")
    def city_cons(e):
        dst, cn = e['dest'].upper(), e['cons'].upper()
        city = 'TPE' if 'TAIWAN' in dst else 'XMN' if 'XMN' in dst else 'PVG' if 'PVG' in dst else dst
        ci = 7 if 'OCEAN' in cn else 1 if 'COASTAL' in cn else 0 if 'YISHUNHAI' in cn else 3 if 'TIANCHEN' in cn else 2
        return city, ci
    bad = []
    for e in X['env_sep']:
        city, ci = city_cons(e); z = [round(v / 16) for v in e['kg']] + [round(e['desp'] / 16)]
        i = pg.evaluate(ENV, [e['date'], city, ci, z, 16])
        r = pg.evaluate("([i,d])=>{const x=hjEnv(hjP(d+'|'+d+'|')).find(y=>y.i===i);return x&&{kz:x.kz.slice(0,4),kg:x.kg,c:x.cajas}}", [i, e['date']])
        if not r or [v / 1000 for v in r['kz']] != e['kg'] or r['kg'] / 1000 != sum(e['kg']) + e['desp'] or r['c'] != e['boxes']: bad.append((e['date'], e['dest'], r))
    chk(not bad, f"los {len(X['env_sep'])} envíos: kg por talla = cajas × 16, Kg TOTAL = SUM y cajas = kg ÷ 16 como el Excel {bad[:2]}")
    for s in X['sal_sep']:
        for ty, kg in (('CONGELACION', s['con']), ('BASURA', s['bas'])):
            if kg: pg.evaluate("([ty,l,kg,d])=>{post(ty,l,'491-610',-kg);ST.L[ST.L.length-1].t=d.slice(8,10)+'/'+d.slice(5,7)+'/'+d.slice(2,4)+', 12:00';save()}", [ty, s['lot'], kg, s['date']])
    bal = pg.evaluate("hjBal(hjP('2026-09-17|2026-09-27|3930.59'))"); B = X['bal_sep']
    # El balance del Excel tiene la recepción del 27/09 (WLREM270926) escrita a mano como 1,270.90; la fórmula de esa recepción
    # (RECEPCION PROPESA!O16 =SUM(K16:N16)) da 1,267.90. La app usa las tallas: 3 kg menos, y la diferencia a favor sube 3 kg.
    I30 = round(B['I30'] - 3.0, 2)
    chk(near(bal['rec'], I30), f"Recepción de langosta {bal['rec']:,.2f} = suma de las fórmulas de cada recepción (el Excel I30 dice {B['I30']:,.2f}: tiene 1,270.90 escrito a mano en vez de 1,267.90 del 27/09)")
    chk(near(bal['desp'], B['J30']), f"Langosta despatada {bal['desp']:.2f} = Excel J30 {B['J30']}")
    chk(near(bal['tr'], I30 + B['J30']), f"Total recibido considerado {bal['tr']:,.2f} = I30 + J30 como la fórmula del Excel (=SUM(I30:J30))")
    chk(near(bal['env'], B['N29']), f"Envíos {bal['env']:.2f} = Excel N29 =SUM(N17:N28) {B['N29']:,}")
    chk(near(bal['con'], B['R24']) and near(bal['bas'], B['S24']), f"Congelación {bal['con']:.2f} y basura {bal['bas']:.2f} = Excel R24 {B['R24']} y S24 {B['S24']}")
    chk(near(bal['ts'], B['V32']), f"Total de salidas {bal['ts']:.2f} = Excel V32 {B['V32']:,.2f}")
    chk(near(bal['dif'], B['V34'] + 3.0), f"Diferencia física a favor {bal['dif']:.2f} = fórmula del Excel V33 − (I33 − V32) con la recepción correcta (el Excel dice {B['V34']} por el 1,270.90)")
    t = pdf_txt(pg, 'hbal', '2026-09-17|2026-09-27|3930.59')
    chk('17,249.00' in t and '13,406.68' in t and '88.27' in t and 'a favor' in t, 'el PDF del balance imprime 17,249.00 · 13,406.68 · 88.27 a favor')
    t = pdf_txt(pg, 'hrec', '2026-09-17|2026-09-27|')
    chk('17189.40' in t and '59.60' in t, 'el PDF de recepción suma 17189.40 kg y 59.60 de despatada (fila Total)')
    t = pdf_txt(pg, 'henv', '2026-09-17|2026-09-27|')
    chk('13312.00' in t and 'OCEAN' in t, 'el PDF de envíos suma 13312.00 kg e incluye el envío a Taiwán')
    t = pdf_txt(pg, 'hcon', '2026-09-17|2026-09-27|')
    chk('85.61' in t and '9.07' in t, 'el PDF de congelación suma 85.61 y 9.07 kg (Excel R24 y S24)')
    # ---------- 2) existencia 14 oct · maquila David ----------
    pg.evaluate("mqSet(3)"); E14 = X['exi_14oct']
    for code, kz in E14['lots']: lot(pg, code if code != 'DAVID' else 'DAVID131026', '2026-10-13', kz)
    tot = pg.evaluate("S.slice(0,4).map(z=>ST.R.reduce((a,r)=>a+Math.max(0,bal(r.lot,z)),0)/1000)")
    T = sum(tot)
    chk(near(tot[0], E14['E83']) and near(tot[1], E14['F83']) and near(T, E14['K83']), f"existencia Total, kg = Excel E83/F83/K83: {tot[0]:.2f} · {tot[1]:.2f} · {T:.2f}")
    chk(near(tot[0] / 16, E14['E84'], 1e-6) and near(tot[1] / 16, E14['F84'], 1e-6) and near(T / 16, E14['K84'], 1e-6), f"Total, cajas = kg ÷ 16 como el Excel (E84 {E14['E84']}, K84 {E14['K84']})")
    t = pdf_txt(pg, 'hexi', '')
    chk('2279.80' in t and '142.49' in t and '101.84' in t, 'el PDF de existencia imprime 2279.80 kg y 142.49 / 101.84 cajas de 16')
    # ---------- 3) maquila Abel · cajas de 15 kg y el error del 24/oct ----------
    pg.evaluate("mqSet(2)"); A = X['abel_15']
    for code, kz in A['lots']: lot(pg, code, '2026-10-05', kz)
    tot = pg.evaluate("S.slice(0,4).map(z=>ST.R.reduce((a,r)=>a+Math.max(0,bal(r.lot,z)),0)/1000)"); T = sum(tot)
    chk(near(T, A['H41']) and near(tot[0], A['D41']), f"Abel: Total, kg {T:.2f} = Excel H41 {A['H41']} (mismos códigos que PROPESA, sin chocar)")
    chk(near(tot[0] / 15, A['D42'], 0.005) and near(T / 15, A['H42'], 0.005), f"Abel: CAJAS DE 15 KG = kg ÷ 15 como el Excel (D42 {A['D42']}, H42 {A['H42']})")
    t = pdf_txt(pg, 'hexi', ''); chk('51.98' in t and 'MAQUILA' in t and 'ABEL' in t, 'el PDF de existencia de Abel dice «MAQUILA ABEL» en grande e imprime 51.98 cajas de 15 kg')
    pg.evaluate("ST.R=[];ST.L=[];ST.B={};save()"); A2 = X['abel_24oct']
    for code, kz in A2['lots']: lot(pg, code, '2026-10-24', kz)
    tot = pg.evaluate("S.slice(0,4).map(z=>ST.R.reduce((a,r)=>a+Math.max(0,bal(r.lot,z)),0)/1000)")
    chk(near(sum(tot), A2['H85']) and near(tot[0], 437.5) and near(tot[1], 390.4), f"Abel 24/oct: la app da Chica {tot[0]:.2f} y Mediana {tot[1]:.2f} (suman {sum(tot):.2f} = H85); el Excel dice {A2['D85_excel']} y {A2['E85_excel']} porque SUM(D82:D83) deja fuera WLRCO211026")
    # ---------- 4) peso bruto de Hoja6 ----------
    H6 = X['hoja6']; g = pg.evaluate("h=>lnG({boxes:h.z.reduce((a,b)=>a+b,0),z:h.z,kp:h.kp,tar:h.tar,cc:0})", H6)
    chk(near(g, H6['L9'], 0.05), f"peso bruto: 40 hieleras de 15 kg + 2 tarimas = {g} kg (Hoja6 L9 {H6['L9']})")
    # ---------- 5) Luis Arce ----------
    pg.evaluate("mqSet(4)"); L = X['luis']; code, d, h, kz, dp = L['rec']; lot(pg, code, d, kz, dp, 1, 'T1', h)
    chk(near(pg.evaluate("l=>(rcv(l)-rcv(l,'desp'))/1000", code), L['O4']), f"Luis Arce: recepción {L['O4']:,} kg = Excel O4 =SUM(K4:N4)")
    i = pg.evaluate(ENV, ['2026-10-09', 'PVG', 0, [L['env_cajas'], 0, 0, 0, 0], 16])
    chk(near(pg.evaluate("i=>hjEnv(hjP('')).find(y=>y.i===i).kg/1000", i), L['D23']), f"Luis Arce: enviado 200 cajas × 16 = {L['D23']:,} kg (Excel D23)")
    # ---------- 6) temporada completa ----------
    pg.evaluate("mqSet(1);ST.R=[];ST.L=[];ST.B={};ST.OR=[];ST.P=[];save()")
    for k, x in enumerate(X['temporada']):
        lot(pg, f"T{k:02d}{x['pk']}{x['date'][8:10]}{x['date'][5:7]}", x['date'], x['k'], x['desp'], PV.get(x['pk'], 1))
    tc = pg.evaluate("ST.R.reduce((a,r)=>a+rcv(r.lot),0)/1000")
    chk(near(tc, X['H57'], 0.01), f"temporada: {tc:,.2f} kg con despatada = RECEPCIONES!H57 {X['H57']:,.2f}")
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
