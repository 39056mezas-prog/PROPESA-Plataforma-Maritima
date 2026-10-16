"""Prueba PROPESA (interruptor_t). Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/interruptor_t.py"""
from playwright.sync_api import sync_playwright
import os,shutil,tempfile
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
FIX="localStorage.clear();localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',pw:'admin123',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',pw:'piso123',role:'piso',notify:true},{id:3,name:'Dirección',email:'consulta@propesa.mx',pw:'ver123',role:'consulta',notify:false}]}))"  # usuarios SOLO para pruebas

seed=open(T+'seed.json').read();errs=[]
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw,sch in [((1180,820),'dark'),((1180,820),'light'),((390,844),'dark')]:
        pg=b.new_page(viewport={'width':vw[0],'height':vw[1]},color_scheme=sch);pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',seed);pg.reload()
        pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
        pg.evaluate("go('cierre')")
        if vw[0]<700:pg.click('.mb')
        pg.click('.sb .lgb');chk(pg.evaluate('V.v')=='inicio',f'{vw} {sch} admin logo -> inicio')
        if vw[0]<700:pg.click('.mb')
        pg.screenshot(path=T+f'i_{vw[0]}_{sch}_full.png')
        pg.click('.sb [data-mode=piso]');pg.wait_for_timeout(150)
        chk(pg.locator('.sb [data-mode=piso]').get_attribute('aria-checked')=='true','switch flips on immediately')
        pg.wait_for_timeout(900);chk(pg.locator('.pt.p1').count()==1,'piso mode active after animation')
        pg.screenshot(path=T+f'i_{vw[0]}_{sch}_piso.png')
        pg.click('.pt.p2');pg.click('.phd .lgb');chk(pg.evaluate('V.v')=='piso','piso logo -> piso inicio')
        pg.click('.phd [data-mode=full]');pg.wait_for_timeout(1100);chk(pg.locator('.sb').count()==1 and pg.evaluate('V.v')=='inicio','switch off -> full view')
        pg.close()
    # piso role: logo -> piso home, no switch
    pg=b.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',seed);pg.reload()
    pg.fill('#le','piso@propesa.mx');pg.fill('#lp','piso123');pg.click('[data-a=lg]');pg.click('.pt.p1');pg.click('.phd .lgb')
    chk(pg.evaluate('V.v')=='piso' and pg.locator('[data-mode]').count()==0,'piso role: logo home, no switch')
    b.close()
print('ERRS',errs)
