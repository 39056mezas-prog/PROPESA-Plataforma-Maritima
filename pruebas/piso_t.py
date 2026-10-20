"""Prueba PROPESA (piso_t). Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/piso_t.py"""
import json
from playwright.sync_api import sync_playwright
import os,shutil,tempfile
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
FIX="localStorage.clear();localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',pw:'admin123',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',pw:'piso123',role:'piso',notify:true},{id:3,name:'Dirección',email:'consulta@propesa.mx',pw:'ver123',role:'consulta',notify:false}]}))"  # usuarios SOLO para pruebas

seed=open(T+'seed.json').read();errs=[];ok=[]
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw,sch in [((1180,820),'dark'),((390,844),'light')]:
        pg=b.new_page(viewport={'width':vw[0],'height':vw[1]},color_scheme=sch);pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',seed);pg.reload()
        pg.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('propesa-v4'));s.OR.push({id:3,etd:'2026-10-14',lines:[{id:1,city:'HKG',cons:0,cli:'ABC',boxes:3}],sh:{}});localStorage.setItem('propesa-v4',JSON.stringify(s))})()")
        pg.reload();pg.fill('#le','piso@propesa.mx');pg.fill('#lp','piso123');pg.click('[data-a=lg]')
        chk(pg.locator('.pt.p1').count()==1,f'{vw[0]} piso role lands on piso home')
        pg.screenshot(path=T+f'p_{vw[0]}_home.png')
        # entrada
        pg.click('.pt.p2')
        chk(pg.locator('tr.per').count()==1,'hoja de entradas con una fila')
        pg.click('[data-pa=save]',force=True);chk(pg.locator('tr.per').count()==1,'guardar sin datos no hace nada')
        pg.select_option('[data-pr="1:origin"]','1');pg.select_option('[data-pr="1:tank"]','T3')
        pg.click('[data-pr="1:lot"]');pg.keyboard.type('nuevo123');chk(pg.input_value('[data-pr="1:lot"]')=='NUEVO123','uppercase lot')
        pg.fill('[data-pr="1:tempT"]','57');pg.fill('[data-pr="1:tempP"]','58');pg.fill('[data-pr="1:kgbox"]','18');pg.fill('[data-pr="1:desp"]','0')
        pg.fill('[data-pr="1:k1"]','100.5');pg.fill('[data-pr="1:k3"]','20');pg.screenshot(path=T+f'p_{vw[0]}_kilos.png');pg.click('[data-pa=save]')
        st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
        r=[x for x in st['R'] if x['lot']=='NUEVO123']
        chk(len(r)==1 and r[0]['tank']=='T3' and r[0]['tempT']==57,'lot saved '+str(r[:1]))
        chk(sum(x['m'] for x in st['L'] if x['lot']=='NUEVO123')==120500,'kg movements')
        chk(pg.locator('[data-pa=clear]').count()==0,'v1.12.0: ya no está «Quitar guardadas de la lista»')
        pg.click('[data-go=piso]');pg.click('.pt.p3 >> nth=0');chk('Embarque' in pg.inner_text('#app'),'embarques wrapped');pg.screenshot(path=T+f'p_{vw[0]}_emb.png')
        ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth");chk(ov==0,'no overflow')
        pg.close()
    # admin toggle
    pg=b.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',seed);pg.reload()
    pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
    chk(pg.locator('.sb').count()==1,'admin full view');pg.click('[data-mode=piso]');pg.wait_for_timeout(900);chk(pg.locator('.pt.p1').count()==1,'admin enters piso');pg.click('[data-mode=full]');pg.wait_for_timeout(900);chk(pg.locator('.sb').count()==1,'admin exits')
    pg.evaluate("go('recepcion')");pg.click('[data-a=nf]');pg.screenshot(path=T+'p_form_sizes.png')
    # el código del lote se ve completo en «¿De qué lote sacas las langostas?», sea del largo que sea (15/oct/2026)
    for vw in (390,820,1180,1440):
        pg.set_viewport_size({'width':vw,'height':900})
        pg.evaluate("(()=>{if(!R_('WLRLE151026LARGO2')){const r={...ST.R[1],id:'R-0999',lot:'WLRLE151026LARGO2'};ST.R.push(r);ST.B[r.lot]=[];post('RECEPCION',r.lot,S[0],50,0,r.id)}const o=ST.OR[0],l=o.lines[0];for(const k in ST.B)ST.B[k]=ST.B[k].filter(b=>b.o!==o.id+'.'+l.id);save();PE={rows:{}};setPiso(true);go('pemp:'+o.id+'.'+l.id)})()");pg.wait_for_timeout(150)
        cut=pg.evaluate("[...document.querySelectorAll('.pk2')].filter(c=>{const t=c.querySelector('.cli');return t.scrollWidth>c.clientWidth||t.getBoundingClientRect().right>c.getBoundingClientRect().right+1}).length")
        n=pg.locator('.pk2').count();chk(n>=3 and cut==0,f'{vw} px: los {n} lotes se ven completos en su tarjeta')
    pg.evaluate("setPiso(false)")
    b.close()
print('ERRS',errs)
