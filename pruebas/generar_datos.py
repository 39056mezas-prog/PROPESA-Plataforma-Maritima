"""Prueba PROPESA (generar_datos). Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/generar_datos.py"""
import json
from playwright.sync_api import sync_playwright
import os,shutil,tempfile
BASE=os.environ.get('BASE','http://localhost:8765/index.html')
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
FIX="localStorage.clear();localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',pw:'admin123',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',pw:'piso123',role:'piso',notify:true},{id:3,name:'Dirección',email:'consulta@propesa.mx',pw:'ver123',role:'consulta',notify:false}]}))"  # usuarios SOLO para pruebas

with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1180,'height':820})
    pg.goto(BASE);pg.evaluate(FIX);pg.reload()
    pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
    for lot,o in [('WLRCO051026A','SCPP Ensenada SCL'),('WLRCO061026B','Pescadores del Sur')]:
        pg.click('.sb [data-go=recepcion]');pg.click('[data-a=nf]');pg.fill('#fl',lot.lower());pg.fill('#fo',o)
        pg.fill('#ftt','58.5');pg.fill('#ftp','59-62');pg.fill('#fkb','18')
        for i,v in enumerate([120.5,300,410.25,95]):pg.fill(f'#fk{i}',str(v))
        pg.fill('#fdes','4.2');pg.click('[data-a=sv]')
    for etd,rows in [('2026-10-12',[('HXH',3),('ZSM',2)]),('2026-10-13',[('RSK',2)])]:
        pg.click('.sb [data-go=ordenes]');pg.fill('#no_etd',etd);pg.click('[data-oa=new]')
        for cli,n in rows:
            pg.select_option('#ol_city','PVG');pg.fill('#ol_cli',cli);pg.fill('#ol_n',str(n));pg.click('[data-oa=ln]')
    pg.click('[data-sh^=join]')
    pg.click('.sb [data-go=empaque]')
    for _ in range(8):
        btns=pg.locator('[data-go^="empacar:"]:has-text("Empacar"), [data-go^="empacar:"]:has-text("Seguir")')
        if btns.count()==0:break
        btns.first.click()
        pg.click('[data-pk^="lot:"] >> nth=0')
        for r in range(pg.locator('.pkrow').count()):
            pg.fill(f'#pk_c{r}',str(18+r*3));pg.click(f'#pkr{r} [data-pk^="k:"] >> nth={r%3}')
        pg.click('[data-pk=addall]');pg.wait_for_timeout(80)
        pg.fill('#ntx','Caja con 2 piezas débiles, revisar al llegar.');pg.click('[data-ev^=save]')
        pg.click('.sb [data-go=empaque]')
    open(T+'seed.json','w').write(pg.evaluate("localStorage.getItem('propesa-v4')"))
    b.close()
print(len(open(T+'seed.json').read()))
