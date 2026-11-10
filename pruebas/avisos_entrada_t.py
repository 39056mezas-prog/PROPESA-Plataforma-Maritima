import sys
"""v1.20.0 · Avisos que pidió el usuario (26/oct/2026) después de la prueba con el Excel de Martha:
1. Fecha de entrada que no cuadra con la fecha del código del lote (WLR + clave + ddmmyy).
2. Hora de madrugada (00:00–04:59): «¿fue a las 13:30?».
   Salen en rojo en el lote y en Entrada; el Administrador corrige («Corregir ›» abre la edición) o deja el dato («Está bien así»,
   que se recuerda con la fecha u hora que se aceptó). Se avisa también al guardar.
3. Salida incompleta: al cerrar el embarque, lo que no se pudo descontar del tanque (lote sin entrada, cerrado o sin kilos) queda
   anotado en el embarque, sale como pendiente que lleva al lote, y «Volver a descontar» lo vuelve a intentar.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/avisos_entrada_t.py"""
import os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recep import recibir, TNA_DEF
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
OUT = os.environ.get('OUT', '/tmp/propesa-pruebas'); os.makedirs(OUT, exist_ok=True)
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',role:'piso',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
def login(pg, em):
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")
def lot(pg, l, d, h, k0=100, k1=0):
    pg.evaluate(TNA_DEF); pg.evaluate("""([l,d,h,k0,k1])=>{TNA(addLot({lot:l,origin:'SCPP Ensenada SCL',pv:1,sp:1,tank:'T1',rdate:d,time:h,k0,k1,k2:0,k3:0,k4:0}));save()}""", [l, d, h, k0, k1])
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1)")

    # ---------- 1 y 2. Fecha y hora de la entrada ----------
    chk(pg.evaluate("lotDt('WLRCO220926')") == '2026-09-22' and pg.evaluate("lotDt('WLREM190926B')") == '2026-09-19', 'lee la fecha del código del lote (también con letra al final)')
    chk(pg.evaluate("lotDt('ABC123')") == '' and pg.evaluate("lotDt('WLRCO991326')") == '', 'un código sin fecha válida no se revisa')
    lot(pg, 'WLRCO220926', '2026-06-22', '01:30')          # el caso real del Excel: fecha 22/06 en lugar de 22/09
    lot(pg, 'WLRCO230926', '2026-09-23', '09:15')          # bien
    lot(pg, 'ABC123', '2026-09-23', '10:00')               # sin fecha en el código
    w = pg.evaluate("lotWarn(R_('WLRCO220926')).map(x=>x.t)")
    chk(len(w) == 2 and 'no cuadra' in w[0] and '22/06/2026' in w[0] and '22/09/2026' in w[0], f'avisa la fecha que no cuadra: {w[:1]}')
    chk(len(w) == 2 and '01:30' in w[1] and '13:30' in w[1], f'avisa la hora de madrugada y propone 13:30: {w[1:]}')
    chk(pg.evaluate("lotWarn(R_('WLRCO230926')).length+lotWarn(R_('ABC123')).length") == 0, 'los lotes bien capturados no avisan')
    for hh, ok in [('00:10', True), ('04:59', True), ('05:00', False), ('13:30', False)]:
        pg.evaluate(f"R_('WLRCO230926').time='{hh}'")
        chk((pg.evaluate("lotWarn(R_('WLRCO230926')).length") == 1) == ok, f'{hh} {"sí" if ok else "no"} es de madrugada')
    pg.evaluate("R_('WLRCO230926').time='09:15';save()")
    pg.evaluate("go('recepcion')"); pg.wait_for_timeout(100)
    t = pg.inner_text('main')
    chk('1 recepción con fecha, hora o código por revisar' in t.lower(), 'Entrada avisa en rojo cuántas entradas revisar (v1.25.0: también el código)')
    bt = pg.locator('.alk', has_text='WLRCO220926')
    chk(bt.count() == 1 and 'fecha distinta a la del código y hora de madrugada' in bt.inner_text(), 'el aviso dice qué revisar en cada lote')
    pg.screenshot(path=f'{OUT}/avisos_entrada_1440.png', full_page=True)
    bt.click(); pg.wait_for_timeout(100)
    chk(pg.evaluate("V.v+':'+V.id") == 'lote:WLRCO220926' and pg.locator('#lotav').count() == 1, 'el aviso lleva al lote, que lo muestra arriba')
    chk(pg.locator('#lotav [data-a=el]').count() == 2 and pg.locator('#lotav [data-av]').count() == 2, 'cada aviso tiene «Corregir ›» y «Está bien así»')
    pg.locator('#lotav [data-av$="h:01:30"]').click(); pg.wait_for_timeout(100)
    chk(pg.evaluate("R_('WLRCO220926').av") == ['h:01:30'] and pg.evaluate("lotWarn(R_('WLRCO220926')).length") == 1, '«Está bien así» deja la hora y ya no la avisa')
    chk(pg.evaluate("JSON.stringify(WN.R(R_('WLRCO220926')).av)") == '["h:01:30"]', 'lo que se aceptó viaja a los otros equipos')
    chk(pg.evaluate("cleanST(mqDump()).R.find(r=>r.lot=='WLRCO220926').av") == ['h:01:30'], 'y sobrevive a un respaldo')
    chk(pg.evaluate("cleanST({...mqDump(),R:[{...R_('WLRCO220926'),av:['x','h:1','<b>',5]}]}).R[0].av") is None, 'valores raros en av se ignoran')
    pg.evaluate("R_('WLRCO220926').time='02:00';save();render()")
    chk(pg.evaluate("lotWarn(R_('WLRCO220926')).length") == 2, 'si cambian la hora a otra de madrugada, se vuelve a avisar')
    pg.locator('#lotav [data-a=el]').first.click(); pg.wait_for_timeout(100)
    chk(pg.evaluate("V.v") == 'rtin' and pg.locator('#rt_fd').count() == 1, '«Corregir ›» abre la edición de la recepción (por tinas)')
    pg.fill('#rt_fd', '22/09/2026'); pg.keyboard.press('Escape'); pg.fill('#rt_hi', '14:00'); pg.click('[data-rt=sv]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("lotWarn(R_('WLRCO220926')).length") == 0 and pg.locator('#lotav').count() == 0, 'corregida la fecha y la hora, el aviso se quita')
    pg.evaluate("go('recepcion')"); pg.wait_for_timeout(80)
    chk('por revisar' not in pg.inner_text('main'), 'y Entrada ya no avisa')
    # al guardar una entrada nueva desde el formulario
    recibir(pg, 'WLRCO051026', pv='1', kz=['40'], fecha='06/10/2026', hora='03:15', tt='58')
    ts = pg.inner_text('#toast')
    chk('Recepción guardada' in ts and 'no cuadra' in ts, f'al guardar avisa enseguida: {ts}')
    chk(pg.evaluate("!!R_('WLRCO051026')") and pg.evaluate("lotWarn(R_('WLRCO051026')).length") == 2, 'se guarda igual (el aviso no bloquea)')
    # Modo piso: la misma recepción por tinas (v1.43.0)
    pg.evaluate("RT=null;setPiso(true);go('rtin')"); pg.wait_for_timeout(100)
    recibir(pg, 'WLRCO071026', pv='1', kz=[30], tank='T3', fecha='08/10/2026', nuevo=False)
    ts = pg.inner_text('#toast')
    if pg.evaluate("!!R_('WLRCO071026')") and pg.evaluate("lotWarn(R_('WLRCO071026')).length"):
        chk('no cuadra' in ts or 'madrugada' in ts, f'Modo piso: al guardar avisa la fecha u hora por revisar: {ts}')
    else:
        chk(pg.evaluate("!!R_('WLRCO071026')") and 'por revisar' not in ts, f'Modo piso: sin aviso cuando todo cuadra: {ts}')
    pg.evaluate("setPiso(false)")
    # Encargado de piso ve el aviso pero no lo puede quitar
    pg.evaluate("signOut()"); pg.wait_for_timeout(150); login(pg, 'piso@propesa.mx'); pg.evaluate("setPiso(false);go('lote:WLRCO051026')"); pg.wait_for_timeout(100)
    chk(pg.locator('#lotav').count() == 1 and pg.locator('#lotav [data-av]').count() == 0 and 'Avísale al Administrador' in pg.inner_text('#lotav'), 'Piso ve el aviso y que lo corrige el Administrador')
    pg.evaluate("signOut()"); pg.wait_for_timeout(150); login(pg, 'admin@propesa.mx'); pg.evaluate("setPiso(false)")
    for w_, h_ in [(820, 1180), (390, 844)]:
        pg.set_viewport_size({'width': w_, 'height': h_})
        for r_ in ['recepcion', 'lote:WLRCO051026']:
            pg.evaluate(f"go('{r_}')"); pg.wait_for_timeout(80)
            chk(not overflow(pg), f'{r_} sin desborde en {w_}px')
        pg.screenshot(path=f'{OUT}/avisos_entrada_{w_}.png', full_page=True)
    pg.set_viewport_size({'width': 1440, 'height': 900})

    # ---------- 3. Salida incompleta ----------
    lot(pg, 'WLRCO101026', '2026-10-10', '10:00', k0=20)   # 20 kg de la primera talla; se empacan 2 hieleras de 16 = 32 kg
    pg.evaluate("ST.R.push({id:newLotId(),lot:'WLRXX101026',origin:'SCPP Ensenada SCL',tank:'T2',rdate:'',time:'',date:'',tempT:null,tempP:'',kgbox:null,desp:null,final:null,closed:false,pv:1,ne:true});ST.B['WLRXX101026']=[];save()")
    oid = pg.evaluate("""(()=>{const o={id:uidN(),etd:'2026-10-11',lines:[{id:1,city:'PVG',cons:0,boxes:3,kp:16}],sh:{}};ST.OR.push(o);syncShip(o,'PVG',0);const d=o.sh['PVG|0'],k=TKEY[0];
      ['WLRCO101026','WLRCO101026','WLRXX101026'].forEach((l,i)=>ST.B[l].push({c:20,k,d,o:o.id+'.1',seq:uidN(),ps:i+1}));save();return o.id})()""")
    i = pg.evaluate(f"ST.OR.find(o=>o.id=={oid}).sh['PVG|0']")
    pg.evaluate(f"go('emb:{i}')"); pg.wait_for_timeout(100); pg.evaluate(f"closeP({i})"); pg.wait_for_timeout(150)
    ts = pg.inner_text('#toast')
    chk('Faltó descontar' in ts and '28.0 kg' in ts, f'al cerrar avisa cuánto faltó descontar: {ts}')
    sf = pg.evaluate(f"ST.P[{i}].sf")
    chk(sorted([x[0] + ':' + x[3] + ':' + str(x[2]) for x in sf]) == ['WLRCO101026:b:12000', 'WLRXX101026:ne:16000'], f'queda anotado lote, gramos y motivo: {sf}')
    chk(pg.evaluate("bal('WLRCO101026')") == 0, 'del lote con poco se descuenta lo que había (sin negativos)')
    iss = pg.evaluate(f"shipIssues({i}).filter(x=>/Salida incompleta/.test(x.t)).map(x=>[x.t,x.go])")
    chk(len(iss) == 2 and any('no había tantos kg' in x[0] and x[1] == 'lote:WLRCO101026' for x in iss) and any('no tiene recepción' in x[0] for x in iss), f'sale como pendiente del embarque y lleva al lote: {iss}')
    pg.evaluate("render()"); pg.wait_for_timeout(80)
    chk(pg.locator('[data-sfa]').count() == 1, 'el embarque ofrece «Volver a descontar del tanque»')
    pg.evaluate("go('embarques')"); pg.wait_for_timeout(80)
    chk('alerta' in pg.inner_text('main'), 'el embarque cerrado con pendiente sigue a la vista en la lista, con su alerta')
    chk(pg.evaluate(f"JSON.stringify(WN.P(ST.P[{i}]).sf)") == json.dumps(sf, separators=(',', ':')), 'lo pendiente viaja a los otros equipos')
    chk(len(pg.evaluate(f"cleanST(mqDump()).P[{i}].sf")) == 2, 'y sobrevive a un respaldo')
    chk(pg.evaluate("sfClean([['L','x',5,'zz'],['','x',5,'b'],['L','x',0,'b']])") is None, 'valores raros en sf se ignoran')
    # se corrige la entrada (faltaban kilos) y se vuelve a descontar
    pg.evaluate("post('RECEPCION','WLRCO101026',S[0],15,0,R_('WLRCO101026').id);save()")
    pg.evaluate(f"go('emb:{i}')"); pg.wait_for_timeout(80); pg.click('[data-sfa]'); pg.wait_for_timeout(120)
    sf = pg.evaluate(f"ST.P[{i}].sf")
    chk(sf is not None and len(sf) == 1 and sf[0][3] == 'ne', f'«Volver a descontar» ya descuenta el lote corregido; queda el lote sin entrada: {sf}')
    chk(pg.evaluate("bal('WLRCO101026')") == 3000 and pg.evaluate(f"ST.L.filter(m=>m.rc=='E/'+ST.P[{i}].u).length") == 1, 'sale una sola vez: 35 − 32 = 3 kg en el tanque')
    ts = pg.inner_text('#toast'); chk('todavía falta descontar 16.0 kg' in ts, f'dice lo que todavía falta: {ts}')
    pg.evaluate(f"go('emb:{i}')"); pg.wait_for_timeout(60)
    pg.locator('[data-a=op]').first.click(); pg.wait_for_timeout(100)
    chk(pg.evaluate(f"ST.P[{i}].closed") is False and pg.evaluate(f"ST.P[{i}].sf") is None and pg.evaluate("bal('WLRCO101026')") == 35000, 'reabrir regresa los kg y borra lo pendiente')
    chk(pg.evaluate(f"WN.P({{...ST.P[{i}],sf:[['L','x',5,'b']]}}).sf") is None, 'un embarque abierto no lleva pendiente de salida')
    # un embarque sin faltantes no deja nada anotado
    pg.evaluate(TNA_DEF); pg.evaluate("TNA(addLot({lot:'WLRXX101026',origin:'SCPP Ensenada SCL',pv:1,sp:1,tank:'T2',rdate:'2026-10-10',time:'10:00',k0:50,k1:0,k2:0,k3:0,k4:0}));save()")
    pg.evaluate(f"closeP({i})"); pg.wait_for_timeout(100)
    chk(pg.evaluate(f"ST.P[{i}].sf") is None and pg.evaluate(f"shipIssues({i}).some(x=>/Salida incompleta/.test(x.t))") is False, 'con kilos suficientes no queda nada pendiente')
    chk(not errs, 'sin errores de JavaScript: %s' % errs[:3])
    b.close()
print('\n%d fallas' % len(fails)); [print(' -', f) for f in fails]
raise SystemExit(1 if fails else 0)
