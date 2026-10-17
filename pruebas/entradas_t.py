"""Prueba PROPESA (entradas_t): hoja de varias entradas en Modo piso.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/entradas_t.py"""
import json
from playwright.sync_api import sync_playwright
import os,shutil,tempfile
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
seed=open(T+'seed.json').read();errs=[]
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
def st(pg):return json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
def login(pg,vw,sch='light',fs=None):
    pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',seed)
    if fs:pg.evaluate(f"localStorage.setItem('propesa-fs','{fs}')")
    pg.reload();pg.fill('#le','piso@propesa.mx');pg.fill('#lp','piso123');pg.click('[data-a=lg]');pg.click('.pt.p2')
EXTRA={'tempT':'58','tempP':'59-61','kgbox':'18','desp':'0'}
def extra(pg,u,vals=EXTRA):
    """v1.8.2: los datos de «Más» son obligatorios: los llena abriendo «Más» y lo deja como estaba."""
    was=pg.evaluate(f"!!(PEN.rows.find(r=>r.u=={u})||{{}}).open")
    if not was:pg.click(f'[data-pa="more:{u}"]')
    for k,v in vals.items():pg.fill(f'[data-pr="{u}:{k}"]',v)
    if not was:pg.click(f'[data-pa="more:{u}"]')
def fill_row(pg,u,prov,tank,lot,kgs,more=True):
    pg.fill(f'[data-pr="{u}:origin"]',prov)
    if tank:pg.select_option(f'[data-pr="{u}:tank"]',tank)
    pg.fill(f'[data-pr="{u}:lot"]',lot)
    for i,k in enumerate(kgs):
        if k!='':pg.fill(f'[data-pr="{u}:k{i}"]',str(k))
    if more:extra(pg,u)
with sync_playwright() as p:
    b=p.chromium.launch()
    # --- Flujo principal en tablet horizontal ---
    pg=b.new_page(viewport={'width':1180,'height':820});pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:m.type=='error' and errs.append(m.text))
    login(pg,(1180,820))
    chk(pg.locator('tr.per').count()==1,'empieza con una fila')
    chk(pg.locator('thead th').count()==10 and pg.locator('thead th').first.is_visible(),'tabla con encabezados visibles')
    chk(pg.is_disabled('[data-pa=save]'),'Guardar deshabilitado sin datos')
    # agregar filas: foco automático en la nueva fila
    pg.click('[data-pa=add]');chk(pg.evaluate("document.activeElement.dataset.pr")=='2:origin','foco en la fila nueva')
    pg.click('[data-pa=add]');pg.click('[data-pa=add]');chk(pg.locator('tr.per').count()==4,'4 filas a la vez')
    fill_row(pg,1,'SCPP Ensenada','T1','wlrco131026a',[10,20,30,40])
    chk(pg.input_value('[data-pr="1:lot"]')=='WLRCO131026A','lote en mayúsculas')
    chk(pg.inner_text('#pt_1')=='100.00','kg total en vivo')
    chk('Sin guardar' in pg.inner_text('#ps_1'),'estado Sin guardar')
    chk(not pg.is_disabled('[data-pa=save]') and '(1)' in pg.inner_text('[data-pa=save]'),'Guardar con conteo')
    # fila 2: sin tanque (inválida); fila 3: lote repetido de la fila 1; fila 4: válida, con detalles
    fill_row(pg,2,'Emancipación','','WLREM131026',[5,'','',''])
    fill_row(pg,3,'Leyes de Reforma','T2','WLRCO131026A',['',15,'',''])
    fill_row(pg,4,'SCPP Ensenada','T4','WLRCO131026B',['','',12.5,''],more=False)
    chk('Faltan 4' in pg.inner_text('[data-pa="more:4"]') and 'pmx' in pg.get_attribute('[data-pa="more:4"]','class'),'v1.8.2: fila con datos y sin los de «Más» → el botón dice «Faltan 4» en rojo')
    pg.click('[data-pa="more:4"]');chk(pg.is_visible('[data-pr="4:tempT"]'),'Más muestra los detalles')
    pg.fill('[data-pr="4:tempT"]','58');pg.fill('[data-pr="4:tempP"]','59-61');pg.fill('[data-pr="4:desp"]','1.2')
    chk('Faltan 1' in pg.inner_text('[data-pa="more:4"]'),'el aviso baja mientras se llenan (falta kg por caja)')
    pg.fill('[data-pr="4:kgbox"]','18')
    chk('· 4' in pg.inner_text('[data-pa="more:4"]') and 'pmx' not in pg.get_attribute('[data-pa="more:4"]','class'),'completos: Más cuenta los datos llenos, sin rojo')
    # el foco y lo escrito se conservan al agregar otra fila
    pg.click('[data-pa=add]');chk(pg.input_value('[data-pr="3:origin"]')=='Leyes de Reforma' and pg.input_value('[data-pr="4:tempT"]')=='58','se conserva lo escrito al agregar')
    chk(pg.locator('tr.per').count()==5,'5 filas')
    pg.screenshot(path=T+'e_1180_antes.png',full_page=True)
    pg.click('[data-pa=save]')
    s=st(pg);lots=[r['lot'] for r in s['R']]
    chk('WLRCO131026A' in lots and 'WLRCO131026B' in lots,'se guardan las filas válidas')
    chk('WLREM131026' not in lots,'la fila inválida no se guarda')
    chk(lots.count('WLRCO131026A')==1,'lote repetido no se duplica')
    r4=[r for r in s['R'] if r['lot']=='WLRCO131026B'][0]
    chk(r4['tank']=='T4' and r4['tempT']==58 and r4['tempP']=='59-61' and r4['desp']==1.2,'detalles guardados')
    chk(sum(x['m'] for x in s['L'] if x['lot']=='WLRCO131026A')==100000,'movimientos por talla')
    chk('Elige el tanque' in pg.inner_text('tr.per[data-pu="2"]'),'error junto al campo (tanque)')
    chk(pg.get_attribute('[data-pr="2:tank"]','aria-invalid')=='true','campo marcado')
    chk('ya existe' in pg.inner_text('tr.per[data-pu="3"]'),'error lote repetido')
    chk(pg.evaluate("document.activeElement.dataset.pr")=='2:tank','foco al primer error')
    chk(pg.locator('#pn_al').count()==1 and 'Revisar' in pg.inner_text('#pn_al'),'aviso rojo con Revisar')
    chk('Guardada' in pg.inner_text('#ps_1') and 'Revisar' in pg.inner_text('#ps_2'),'estados Guardada / Revisar')
    chk(pg.is_disabled('[data-pr="1:lot"]'),'fila guardada queda bloqueada')
    chk(pg.locator('[data-pa="rm:1"]').count()==0,'fila guardada sin Quitar')
    chk(pg.input_value('[data-pr="2:origin"]')=='Emancipación','fila con error conserva lo escrito')
    pg.screenshot(path=T+'e_1180_errores.png',full_page=True)
    # corregir y volver a guardar: no duplica las ya guardadas
    pg.select_option('[data-pr="2:tank"]','T5');chk(pg.locator('#pn_al').count()==1,'aviso sigue por la fila 3')
    pg.fill('[data-pr="3:lot"]','WLRLE131026');chk(pg.locator('#pn_al').count()==0,'aviso desaparece al corregir')
    n0=len(st(pg)['R']);pg.click('[data-pa=save]');pg.click('[data-pa=save]',force=True)
    s=st(pg);chk(len(s['R'])==n0+2,'doble toque no duplica ({}→{})'.format(n0,len(s['R'])))
    chk(pg.is_disabled('[data-pa=save]'),'nada por guardar')
    # Enter avanza; al final crea fila nueva
    pg.click('[data-pr="5:origin"]');pg.keyboard.type('SCPP');pg.keyboard.press('Enter')
    chk(pg.evaluate("document.activeElement.dataset.pr")=='5:tank','Enter pasa al siguiente campo')
    pg.focus('[data-pr="5:k3"]');pg.keyboard.press('Enter');chk(pg.locator('tr.per').count()==6 and pg.evaluate("document.activeElement.dataset.pr")=='6:origin','Enter al final crea fila')
    # Quitar con confirmación
    pg.click('[data-pa="rm:5"]');chk(pg.locator('[data-pa="rmy:5"]').count()==1,'pide confirmar al quitar fila con datos')
    pg.click('[data-pa="rmn:5"]');chk(pg.locator('tr.per[data-pu="5"]').count()==1,'No conserva la fila')
    pg.click('[data-pa="rm:5"]');pg.click('[data-pa="rmy:5"]');chk(pg.locator('tr.per[data-pu="5"]').count()==0,'Quitar elimina la fila')
    pg.click('[data-pa="rm:6"]');chk(pg.locator('tr.per[data-pu="6"]').count()==0,'fila vacía se quita sin preguntar')
    # borrador se conserva al salir y volver
    pg.click('[data-pa=add]');u=pg.evaluate("PEN.rows[PEN.rows.length-1].u");pg.fill(f'[data-pr="{u}:lot"]','borrador1')
    pg.click('.phd [data-go=piso]');chk('1 sin guardar' in pg.inner_text('.pt.p2'),'Inicio avisa borradores')
    pg.click('.pt.p2');chk(pg.input_value(f'[data-pr="{u}:lot"]')=='BORRADOR1','borrador se conserva')
    # fecha vacía abre detalles y marca el campo
    pg.fill(f'[data-pr="{u}:origin"]','X');pg.select_option(f'[data-pr="{u}:tank"]','T6');pg.fill(f'[data-pr="{u}:k0"]','3')
    # v1.8.2: sin los datos de «Más» no se guarda; la fila se abre y marca cada uno
    pg.click('[data-pa=save]');tx=pg.inner_text(f'tr.pdet[data-pu="{u}"]')
    chk(pg.is_visible(f'[data-pr="{u}:tempT"]') and all(m in tx for m in ['temperatura del tanque','temperatura del producto','kg por caja','desperdicio']) and not pg.evaluate("ST.R.some(r=>r.lot=='BORRADOR1')"),'sin temperaturas, kg por caja y desperdicio no se guarda; la fila se abre y marca cada dato')
    extra(pg,u,{'tempT':'150','tempP':'59','kgbox':'18','desp':'0'});pg.click('[data-pa=save]')
    chk('entre 20 y 110' in pg.inner_text(f'tr.pdet[data-pu="{u}"]'),'temperatura fuera de rango (150 °F) marcada')
    extra(pg,u,{'tempT':'58'})
    if not pg.is_visible(f'[data-pr="{u}:rdate"]'):pg.click(f'[data-pa="more:{u}"]')
    pg.fill(f'[data-pr="{u}:rdate"]','');pg.click(f'[data-pa="more:{u}"]');pg.click('[data-pa=save]')
    chk(pg.is_visible(f'[data-pr="{u}:rdate"]') and pg.evaluate("document.activeElement.dataset.pr")==f'{u}:rdate','fecha faltante abre detalles')
    # talla negativa y sin kg
    pg.fill(f'[data-pr="{u}:rdate"]','2026-10-13');pg.fill(f'[data-pr="{u}:k0"]','-2');pg.click('[data-pa=save]')
    chk('negativo' in pg.inner_text(f'tr.per[data-pu="{u}"]'),'talla negativa marcada')
    pg.fill(f'[data-pr="{u}:k0"]','');pg.click('[data-pa=save]');chk('al menos una talla' in pg.inner_text(f'tr.per[data-pu="{u}"]'),'sin kg marcado')
    # auditoría #10: la vista completa usa la misma regla y la misma función que Modo piso para crear lotes
    pg.evaluate("setPiso(false);go('recepcion')");pg.click('[data-a=nf]')
    pg.fill('#fl','wlrneg151026');pg.fill('#fo','SCPP');pg.fill('#fk0','-50');pg.fill('#fk1','100');pg.click('[data-a=sv]')
    chk('Escribe la temperatura del tanque' in pg.inner_text('#app') and pg.evaluate("document.activeElement.id")=='ftt' and pg.input_value('#fk1')=='100','v1.8.2 vista completa: sin temperatura del tanque no guarda, lleva al campo y conserva lo escrito')
    pg.fill('#ftt','58');pg.click('[data-a=sv]');chk('temperatura del producto' in pg.inner_text('#app'),'vista completa: pide la temperatura del producto')
    pg.fill('#ftp','59-61');pg.fill('#fkb','18');pg.fill('#fk0','0');pg.click('[data-a=sv]');chk('desperdicio' in pg.inner_text('#app') and pg.evaluate("document.activeElement.id")=='fdes','vista completa: pide el desperdicio (0 si no hubo)')
    pg.fill('#fk0','-50');pg.fill('#fdes','0');pg.click('[data-a=sv]')
    chk('No puede ser negativo.' in pg.inner_text('#app') and not pg.evaluate("ST.R.some(r=>r.lot=='WLRNEG151026')"),'vista completa: −50 kg en una talla marca «No puede ser negativo» y no guarda (antes guardaba 100 kg)')
    chk(pg.input_value('#fk0')=='-50' and pg.input_value('#fk1')=='100','lo escrito se conserva')
    pg.fill('#fk0','0');pg.click('[data-a=sv]')
    chk(pg.evaluate("bal('WLRNEG151026')")==100000,'al corregirlo se guarda con 100 kg')
    ka=pg.evaluate("Object.keys(R_('WLRNEG151026')).join()");kb=pg.evaluate("Object.keys(R_('WLRCO131026A')).join()")
    chk(ka==kb,'el lote de la vista completa y el de Modo piso tienen los mismos campos')
    chk(pg.evaluate("typeof addLot=='function'&&!/ST\\.R\\.push/.test(saveLot.toString()+penSave.toString())"),'las dos pantallas crean el lote con addLot')
    pg.close()
    # --- Vistas: celular, tablet vertical, computadora, texto muy grande, tema oscuro ---
    for vw,sch,fs in [((390,844),'light',None),((820,1180),'dark',None),((1440,900),'light',None),((1180,820),'dark',20),((820,1180),'light',20)]:
        pg=b.new_page(viewport={'width':vw[0],'height':vw[1]},color_scheme=sch);pg.on('pageerror',lambda e:errs.append(str(e)))
        login(pg,vw,sch,fs);pg.click('[data-pa=add]');pg.click('[data-pa=add]')
        fill_row(pg,1,'SCPP Ensenada','T1','WLRCO131026C',[10,20,30,40]);fill_row(pg,2,'Emancipación','','WLREM131026',[5,'','',''])
        pg.click('[data-pa="more:3"]');pg.click('[data-pa=save]')
        tag=f'{vw[0]}_{sch}'+(f'_fs{fs}' if fs else '')
        ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
        mo=pg.evaluate("(()=>{const m=document.querySelector('main');return m.scrollWidth-m.clientWidth})()")
        chk(ov<=0 and mo<=0,f'{tag} sin desborde ({ov},{mo})')
        card=pg.evaluate("getComputedStyle(document.querySelector('tr.per')).display")
        chk((card=='grid')==(vw[0]<1000 or (fs==20 and vw[0]<1300)),f'{tag} tarjetas={card}')
        small=pg.evaluate("[...document.querySelectorAll('#app .pent button,#app .pent input,#app .pent select')].filter(e=>e.offsetParent&&!e.closest('datalist')).map(e=>e.getBoundingClientRect()).filter(r=>r.height<44).length")
        chk(small==0,f'{tag} objetivos táctiles ≥44 px ({small})')
        pg.screenshot(path=T+f'e_{tag}.png',full_page=False)
        pg.close()
    b.close()
chk(not errs,'sin errores de página '+str(errs[:3]))
print('ERRS',errs)
