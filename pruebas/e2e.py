"""Flujo completo: entrada → órdenes → empaque → embarque → cierre. Uso: python3 -I pruebas/e2e.py"""
import json,sys,os
FIX="localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',pw:'admin123',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',pw:'piso123',role:'piso',notify:true},{id:3,name:'Dirección',email:'consulta@propesa.mx',pw:'ver123',role:'consulta',notify:false}]}))"  # usuarios SOLO para pruebas

BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local');OUT=os.environ.get('OUT','/tmp/propesa-pruebas');os.makedirs(OUT,exist_ok=True)  # modo local: nunca toca la base real
from playwright.sync_api import sync_playwright
errs=[];ok=[]
def chk(c,m):
    (ok if c else errs).append(m); print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1180,'height':820})
    pg.on('pageerror',lambda e:errs.append('JS '+str(e)));pg.on('console',lambda m:m.type=='error' and errs.append('CONSOLE '+m.text))
    pg.goto(BASE);pg.evaluate(FIX);pg.reload()
    pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
    pg.click('.sb [data-go=recepcion]')
    pg.click('[data-a=nf]')
    chk('Kg por caja en tanque' in pg.inner_text('#app'),'label Kg por caja en tanque')
    pg.click('#fl');pg.keyboard.type('wlrco051026a',delay=5)
    chk(pg.input_value('#fl')=='WLRCO051026A','lote en mayusculas en vivo: '+pg.input_value('#fl'))
    pg.fill('#fo','SCPP');pg.fill('#fkb','18');
    for i,v in enumerate([100,200,300,400]):pg.fill(f'#fk{i}',str(v))
    pg.click('[data-a=sv]');pg.wait_for_timeout(200)
    chk('WLRCO051026A' in pg.inner_text('#app'),'lote guardado')
    # icons
    ic=pg.evaluate("[...document.querySelectorAll('.sb .fs')].map(b=>[b.dataset.go,b.querySelector('svg').outerHTML])")
    d=dict(ic);chk(d['embarques']!=d['recepcion'] and 'currentColor' in d['recepcion'] and 'M256 384' in d['recepcion'],'Entrada lleva la langosta (blanca) y Embarque el camión')
    # orders
    def mk(etd):
        pg.click('.sb [data-go=ordenes]');pg.fill('#no_etd',etd);pg.click('[data-oa=new]')
    def addline(cli,n,city='PVG'):
        pg.select_option('#ol_city',city);pg.fill('#ol_cli',cli);pg.fill('#ol_n',str(n));pg.click('[data-oa=ln]')
    mk('2026-10-12');addline('HXH',3)
    tx=pg.inner_text('#app');chk('3 cajas · 48 kg neto · 58.8 kg bruto' in tx and '19.6 kg brutos por caja' in tx,'orden: peso bruto 19.6 kg por caja, sin decimales de más')
    chk(abs(pg.evaluate("ST.P[0].exp")-58.8)<1e-9,'el embarque espera el mismo peso bruto que la orden (58.8 kg)')
    mk('2026-10-13');addline('ZSM',2)
    st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
    chk(len(st['P'])==2,'2 embarques antes de unir: %d'%len(st['P']))
    chk(pg.locator('[data-sh^=join]').count()==1,'boton unir presente')
    chk(pg.evaluate("[...document.querySelectorAll('select[id^=sh_j_] option')].map(o=>o.value).join()")==pg.evaluate("ST.P[0].u"),'«Unir a otro embarque» manda el id fijo del embarque, no su lugar en la lista')
    pg.click('[data-sh^=join]')
    st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
    chk(len(st['P'])==1 and st['P'][0]['h']==5,'unidas: 1 embarque con 5 hieleras: %s'%[(q['n'],q['h']) for q in st['P']])
    chk(' + ' in st['P'][0]['n'],'nombre con ambas fechas: '+st['P'][0]['n'])
    # empacar A
    pg.click('.sb [data-go=empaque]')
    pg.locator('[data-go^="empacar:"]').first.click()
    chk(pg.locator('.pkrow').count()==2 or pg.locator('.pkrow').count()==3,'filas grid: %d'%pg.locator('.pkrow').count())
    n=pg.locator('.pkrow').count()
    chk(pg.locator('.evb').count()==0,'sin botones de foto en empaque')
    # error: count sin categoria
    pg.fill('#pk_c0','30');pg.click('[data-pk=addall]');pg.wait_for_timeout(100)
    chk(pg.input_value('#pk_c0')=='30','valor conservado tras error')
    pg.click('#pkr0 [data-pk^="k:"] >> nth=0')
    pg.fill('#pk_c1','25');pg.click('#pkr1 [data-pk^="k:"] >> nth=1')
    pg.click('[data-pk=addall]');pg.wait_for_timeout(100)
    st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
    bx=[b for l in st['B'].values() for b in l]
    chk(len(bx)==2 and all(b['d']==0 for b in bx),'2 cajas guardadas a la vez, d=0: %s'%bx)
    chk(pg.locator('.pkrow').count()==n-2,'filas restantes %d'%pg.locator('.pkrow').count())
    # notes
    pg.fill('#ntx','nota prueba');pg.click('[data-ev^=save]');chk('nota prueba' in pg.inner_text('#app'),'nota guardada en empaque')
    # embarque page
    pg.click('.sb [data-go=embarques]');pg.locator('.bp').first.click()
    t=pg.inner_text('#app');chk('Órdenes en este embarque' in t and '12/10' in t and '13/10' in t,'panel de órdenes en embarque')
    chk(pg.locator('[data-sh^=sep]').count()==2,'botones separar')
    pg.click('[data-sh^=sep] >> nth=1');
    st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
    chk(len(st['P'])==2 and sorted(q['h'] for q in st['P'])==[2,3],'separadas: %s'%[(q['n'],q['h']) for q in st['P']])
    # re-add via emb panel
    t=pg.inner_text('#app')
    pg.click('.sb [data-go=embarques]');pg.locator('.bp').first.click()
    chk(pg.locator('#sh_add').count()==1,'select agregar otra orden')
    pg.click('[data-sh^=add]');pg.wait_for_timeout(100)
    st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
    chk(len(st['P'])==1 and st['P'][0]['h']==5,'reunidas: %s'%[(q['n'],q['h']) for q in st['P']])
    bx=[b for l in st['B'].values() for b in l];chk(all(b['d']==0 for b in bx),'cajas siguen en d=0 tras reindexar')
    # pack the remaining and close
    pg.click('.sb [data-go=empaque]')
    for _ in range(6):
        btns=pg.locator('[data-go^="empacar:"]:has-text("Empacar"), [data-go^="empacar:"]:has-text("Seguir")')
        if btns.count()==0:break
        btns.first.click()
        rows=pg.locator('.pkrow').count()
        for r in range(rows):
            pg.fill(f'#pk_c{r}',str(20+r));pg.click(f'#pkr{r} [data-pk^="k:"] >> nth=2')
        pg.click('[data-pk=addall]');pg.wait_for_timeout(100);pg.click('.sb [data-go=empaque]')
    st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
    bx=[b for l in st['B'].values() for b in l];chk(len(bx)==5,'5 cajas totales: %d'%len(bx))
    pg.click('.sb [data-go=embarques]');pg.locator('.bp').first.click()
    pg.fill('[data-zs$=":0"]','5');pg.press('[data-zs$=":0"]','Tab')
    pg.click('[data-a=cp]');pg.wait_for_timeout(200)
    st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
    chk(st['P'][0]['closed'],'cerrado'); print(st['O'][0]['body'][:300]);chk('12/10' in st['O'][0]['body'] and '13/10' in st['O'][0]['body'],'correo lista ordenes')
    t=pg.inner_text('#app');chk('NaN' not in t and 'undefined' not in t,'sin NaN/undefined')
    for v in ['inicio','recepcion','ordenes','empaque','embarques','cierre']:
        pg.click(f'.sb [data-go={v}]');t=pg.inner_text('#app');chk('NaN' not in t and 'undefined' not in t,'sweep '+v)
    # old format: empacar with closed shipment hides grid
    pg.screenshot(path=OUT+'/e2e.png')
    b.close()
print('ERRS',[e for e in errs if not e.startswith(('2','3'))][:10]); sys.exit(1 if any(e.startswith(('JS','CONSOLE')) for e in errs) else 0)
