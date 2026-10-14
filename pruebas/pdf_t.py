"""Prueba PROPESA (pdf_t). Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/pdf_t.py"""
import json,sys,os
from playwright.sync_api import sync_playwright
import os,shutil,tempfile
BASE=os.environ.get('BASE','http://localhost:8765/index.html')
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
FIX="localStorage.clear();localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',pw:'admin123',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',pw:'piso123',role:'piso',notify:true},{id:3,name:'Dirección',email:'consulta@propesa.mx',pw:'ver123',role:'consulta',notify:false}]}))"  # usuarios SOLO para pruebas

seed=open(T+'seed.json').read()
os.makedirs(T+'pdfs',exist_ok=True)
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':1180,'height':820},accept_downloads=True);pg=ctx.new_page()
    pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:m.type=='error' and errs.append(m.text))
    pg.goto(BASE);pg.evaluate('s=>localStorage.setItem("propesa-v4",s)',seed);pg.reload()
    pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
    # make shipment have alive + sizes for richer report
    pg.evaluate("ST.P[0].z=[2,2,2,1];ST.P[0].alive=100;save()")
    for route,sel in [('recepcion','dl:ent'),('ordenes','dl:ord'),('orden:1','dl:ord'),('empaque','dl:emp'),('empacar:1.1','dl:emp'),('embarques','dl:embs'),('emb:0','dl:emb'),('cierre','dl:mort')]:
        pg.evaluate(f"go('{route}')")
        btn=pg.locator(f'[data-pdf^="{sel}"]').first
        with pg.expect_download() as d: btn.click()
        dl=d.value;path=T+'pdfs/'+route.replace(':','_')+'__'+dl.suggested_filename;dl.save_as(path);sz=os.path.getsize(path);ok=sz>2000 and open(path,'rb').read(5)==b'%PDF-';print(('PASS' if ok else 'FAIL'),'PDF',route,sz,dl.suggested_filename)
    # el Plan de embarques trae el dibujo del camión con las hieleras de cada celda
    pe=[f for f in os.listdir(T+'pdfs') if f.startswith('embarques__')][0];raw=open(T+'pdfs/'+pe,'rb').read()
    print(('PASS' if b'Plan de carga' in raw and b'(CABINA)' in raw and b'(COLA \xb7 puertas traseras)' in raw else 'FAIL'),'Plan de embarques trae el camión')
    exp=pg.evaluate("(()=>{const pl=truckPlan();return pl.TP.reduce((a,p)=>a+p.h,0)})()")
    print(('PASS' if exp>0 and f'({exp})'.encode() in raw else 'FAIL'),'el camión del PDF muestra las hieleras de la celda',exp)
    print('ERRS',errs);print(('PASS' if not errs else 'FAIL')+' sin errores de JavaScript al generar PDFs')
    b.close()
