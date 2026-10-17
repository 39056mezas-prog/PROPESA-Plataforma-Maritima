"""Prueba PROPESA (cajas_auto_t). Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/cajas_auto_t.py"""
import json
from playwright.sync_api import sync_playwright
import os,shutil,tempfile
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
FIX="localStorage.clear();localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',pw:'admin123',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',pw:'piso123',role:'piso',notify:true},{id:3,name:'Dirección',email:'consulta@propesa.mx',pw:'ver123',role:'consulta',notify:false}]}))"  # usuarios SOLO para pruebas

seed=json.loads(open(T+'seed.json').read())
seed['OR'].append({'id':3,'etd':'2026-10-13','lines':[{'id':1,'city':'HKG','cons':0,'cli':'ABC','boxes':5}],'sh':{}})
S=json.dumps(seed);errs=[]
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
def tap(pg,no):pg.click(f'#pps{no} .pbn')  # tocar la tarjeta: la vuelve la hielera activa del teclado
def kp(pg,digits):
    for d in str(digits):pg.click(f'#kpad [data-kp="d:{d}"]')
def boxes(pg):
    st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"));return sorted([(x.get('ps'),x['c'],x['k']) for v in st['B'].values() for x in v if x['o']=='3.1'])
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw,sch in [((1180,820),'dark'),((390,844),'light')]:
        pg=b.new_page(viewport={'width':vw[0],'height':vw[1]},color_scheme=sch);pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',S);pg.reload()
        pg.fill('#le','piso@propesa.mx');pg.fill('#lp','piso123');pg.click('[data-a=lg]');pg.wait_for_timeout(700)
        pg.evaluate("syncShip(ST.OR[2],'HKG',0);save();go('pemp:3.1')")
        if pg.locator('[data-pe^="lot:"]').count():pg.click('[data-pe^="lot:"] >> nth=0')
        chk(pg.locator('.pbx').count()==5,'5 cards')
        # card 1: pieces then category -> autosave
        tap(pg,1);kp(pg,20);pg.click('#kpad [data-kp="k:R"]')
        chk(boxes(pg)==[(1,20,'R')],'card1 autosaved '+str(boxes(pg)))
        chk(pg.locator('#pps1.sv').count()==1 and pg.locator('.pbx').count()==5,'card1 stays on screen faded')
        # card 3 first: category then pieces + Enter
        tap(pg,3);pg.click('#kpad [data-kp="k:V"]');chk(len(boxes(pg))==1,'solo categoría no guarda')
        kp(pg,33);pg.click('#kpad [data-kp=next]')
        chk((3,33,'V') in boxes(pg),'card3 (categoría primero) se guarda al pasar a la siguiente, keeps slot '+str(boxes(pg)))
        # "all" blanco then type pieces on 2 and 4
        pg.click('[data-pe="all:B"]');pg.fill('.ppc[data-slot="2"]','12');pg.press('.ppc[data-slot="2"]','Enter')
        chk((2,12,'B') in boxes(pg),'all-category + pieces saves')
        # edit saved card 1 pieces and category
        tap(pg,1);kp(pg,25);pg.click('#kpad [data-kp="k:V"]')
        chk((1,25,'V') in boxes(pg),'edit saved card in place '+str(boxes(pg)))
        # invalid edit
        pg.fill('#pps2 .psc','');pg.press('#pps2 .psc','Tab');chk((2,12,'B') in boxes(pg),'empty edit rejected')
        # remove card 3
        tap(pg,3);pg.click('#kpad [data-pe^="cf:"]');pg.click('#kpad [data-pe^="rm:"]');print('after rm',pg.evaluate('JSON.stringify(PE.rows)'),pg.evaluate('document.querySelector(".ppc[data-slot=\\"3\\"]").value'),pg.evaluate('document.querySelector(".ppc[data-slot=\\"3\\"]").getAttribute("value")'));chk(all(x[0]!=3 for x in boxes(pg)) and pg.locator('#pps3.sv').count()==0,'remove frees slot 3')
        tap(pg,3);pg.click('#kpad [data-kp="k:R"]');print('after R',boxes(pg),pg.evaluate('JSON.stringify(PE.rows)'),pg.locator('.ppc').count())
        for no,c in [(3,30),(4,40),(5,50)]:
            pg.fill(f'.ppc[data-slot="{no}"]',str(c));pg.press(f'.ppc[data-slot="{no}"]','Enter')
        chk(len(boxes(pg))==5,'5 saved '+str(boxes(pg)))
        chk(pg.locator('.pdone').count()==1 and pg.locator('.pbx.sv').count()==5,'done banner + cards still visible')
        pg.screenshot(path=T+f'a_{vw[0]}_done.png',full_page=True)
        # full view still consistent
        pg.evaluate("go('empacar:3.1')");chk('5 de 5' in pg.inner_text('#app'),'full view sees 5')
        ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth");chk(ov==0,'no overflow')
        pg.close()
    b.close()
print('ERRS',errs)
