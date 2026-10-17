"""Prueba PROPESA (avisos_t). Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/avisos_t.py"""
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
seed['OR'].append({'id':3,'etd':'2026-10-13','lines':[{'id':1,'city':'HKG','cons':0,'cli':'ABC','boxes':25}],'sh':{}})
seed['OR'].append({'id':4,'etd':'2026-10-10','lines':[],'sh':{}})
S=json.dumps(seed);errs=[]
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch()
    for piso in [False,True]:
        pg=b.new_page(viewport={'width':1180,'height':820},color_scheme='dark');pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',S);pg.reload()
        pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
        pg.evaluate(f"syncShip(ST.OR[2],'HKG',0);save();setPiso({str(piso).lower()});go('inicio')")
        E='pemp:' if piso else 'empacar:'
        def at():return pg.evaluate("V.v+(V.id?':'+V.id:'')")
        # panel order table
        pg.click("button.chipb:has-text('Faltan 25')");chk(at()==E+'3.1',f'piso={piso} panel Faltan -> {at()}')
        pg.evaluate("go('inicio')");pg.click("button.chipb:has-text('Sin líneas')");chk(at()=='orden:4','panel Sin líneas -> '+at())
        pg.click("button.chipb:has-text('Sin líneas')");pg.wait_for_timeout(500);chk(pg.evaluate("document.activeElement.id")=='ol_cli','on order page jumps to add-line field')
        # KPI cards
        pg.evaluate("go('inicio')");pg.click('.kpl >> nth=0');chk(at().startswith(E) or at().startswith('orden:'),'KPI hieleras -> '+at())
        pg.evaluate("go('inicio')");pg.click('.kpl >> nth=1');chk(at().startswith('emb:'),'KPI empaques -> '+at())
        # empaque per-line chip
        pg.evaluate("go('empaque')");pg.click("td button.chipb:has-text('Faltan 25')");chk(at()==E+'3.1','empaque line chip -> '+at())
        pg.evaluate("go('orden:3')");pg.click("td button.chipb");chk(at()==E+'3.1','orden line chip -> '+at())
        # shipment alerts: HKG shipment index
        i=pg.evaluate("ST.P.findIndex(p=>p.n.startsWith('HKG'))");pg.evaluate(f"ST.P[{i}].c[0][1]=1.5;save();go('emb:{i}')")
        n=pg.locator('.alk').count();chk(n>=3,f'{n} alert items clickable')
        hs=pg.evaluate("[...document.querySelectorAll('#app .alk,#app .chipb')].filter(e=>e.offsetParent).map(e=>Math.round(e.getBoundingClientRect().height))")
        chk(hs and min(hs)>=44,f'avisos y chips rojos miden 44 px o más para tocar con guantes (auditoría #19): {sorted(set(hs))}')
        pg.click(".alk:has-text('tallas')");pg.wait_for_timeout(500);chk((pg.evaluate("document.activeElement.dataset.zs") or '').startswith(pg.evaluate(f"ST.P[{i}].u")+':'),'tallas alert focuses size input')
        pg.click(".alk:has-text('Peso bruto')");pg.wait_for_timeout(500);chk((pg.evaluate("document.activeElement.dataset.a") or '').startswith('pwfix:'),'v1.8.7: el aviso de peso lleva a «Usar el peso estándar»')
        pg.click('[data-a^="pwfix:"]');chk(pg.locator(".alk:has-text('Peso bruto')").count()==0 and pg.evaluate(f"ST.P[{i}].c[0][1]")==1.4,'al usar el peso estándar el aviso desaparece')
        pg.click("button.chipb:has-text('NO SUMA')");pg.wait_for_timeout(500);chk((pg.evaluate("document.activeElement.dataset.zs") or '')!='','NO SUMA chip focuses')
        pg.click(".alk:has-text('No hay hieleras')");chk(at()==E+'3.1','no boxes alert -> '+at())
        pg.evaluate(f"go('emb:{i}')");pg.click("td button.chipb");chk(at()==E+'3.1','ordsInShip chip -> '+at())
        # auditoría #6: dos tablets guardan el último lugar a la vez y queda una hielera de más
        pg.evaluate("ST.B.WLRCO051026A.push({c:15,k:'R',d:0,o:'1.1',seq:uidN()});save();go('emb:0')")
        chk(pg.locator(".alk:has-text('HXH tiene 4 hieleras y la orden pide 3')").count()==1,f'piso={piso} aviso rojo «HXH tiene 4 hieleras y la orden pide 3»')
        pg.click(".alk:has-text('HXH tiene 4 hieleras')");chk(at()=='empacar:1.1','el aviso lleva a la vista completa de ese cliente -> '+at())
        chk(pg.evaluate("ordAssigned(ST.OR[0],ST.OR[0].lines[0]).length")==4 and pg.locator('#app').inner_text().count('15')>=1,'ahí se ve la hielera de más')
        pg.evaluate("(()=>{ST.B.WLRCO051026A.pop();save();go('emb:0')})()")
        chk(pg.locator(".alk:has-text('hieleras y la orden pide')").count()==0,'al quitarla, el aviso se va')
        pg.evaluate(f"go('emb:{i}')");pg.screenshot(path=T+f'l_{piso}_emb.png')
        pg.evaluate("go('inicio')");pg.screenshot(path=T+f'l_{piso}_inicio.png')
        pg.close()
    b.close()
print('ERRS',errs)
