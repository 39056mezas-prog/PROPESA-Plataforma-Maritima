"""Prueba PROPESA (vistas_t). Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/vistas_t.py"""
import json,sys
from playwright.sync_api import sync_playwright
import os,shutil,tempfile
BASE=os.environ.get('BASE','http://localhost:8765/index.html')
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
FIX="localStorage.clear();localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',pw:'admin123',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',pw:'piso123',role:'piso',notify:true},{id:3,name:'Dirección',email:'consulta@propesa.mx',pw:'ver123',role:'consulta',notify:false}]}))"  # usuarios SOLO para pruebas

seed=open(T+'seed.json').read()
sizes={'phone':(390,844),'tablet':(820,1180),'desk':(1440,900)}
pages=['inicio','recepcion','ordenes','orden:1','empaque','empacar:1.1','embarques','emb:0','cierre']
with sync_playwright() as p:
    b=p.chromium.launch()
    for sn,(w,h) in sizes.items():
        pg=b.new_page(viewport={'width':w,'height':h})
        pg.goto(BASE);pg.evaluate('s=>localStorage.setItem("propesa-v4",s)',seed);pg.reload()
        pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
        for pgn in pages:
            pg.evaluate(f"go('{pgn}')");pg.wait_for_timeout(60)
            ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
            ov2=pg.evaluate("(()=>{const m=document.querySelector('main');return m.scrollWidth-m.clientWidth})()")
            print(sn,pgn,'pageOverflow',ov,'mainOverflow',ov2)
            pg.screenshot(path=T+f'r_{sn}_{pgn.replace(":","_")}.png',full_page=False)
        pg.close()
    b.close()
