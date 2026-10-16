"""Prueba PROPESA (pdf_t). Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/pdf_t.py"""
import json,sys,os
from playwright.sync_api import sync_playwright
import os,shutil,tempfile
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
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
    pg.on('dialog',lambda d:d.accept());pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:m.type=='error' and errs.append(m.text))
    pg.goto(BASE);pg.evaluate('s=>localStorage.setItem("propesa-v4",s)',seed);pg.reload()
    pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
    # make shipment have alive + sizes for richer report
    pg.evaluate("ST.P[0].z=[2,2,2,1];ST.P[0].alive=100;save()")
    # auditoría #4: orden 2 con una caja Roja y una Amarilla (10 piezas cada una)
    pg.evaluate("(()=>{const b=ST.B.WLRCO051026A;b[0].c=10;b[0].k='R';b[1].c=10;b[1].k='A';save()})()")
    pg.evaluate("go('orden:2')")
    with pg.expect_download() as d: pg.locator('[data-pdf^="dl:ord"]').first.click()
    with pg.expect_download() as d2: pg.evaluate("go('empacar:2.1')"); pg.locator('[data-pdf^="dl:emp"]').first.click()
    raw=open(d2.value.path(),'rb').read()
    print(('PASS' if b'(Amarillo)' in raw else 'FAIL'),'el packing list trae la columna y el total de Amarillo')
    ok=pg.evaluate("ST.OR.every(o=>{const bx=ordBoxes(o).map(x=>x.b),c=byCat(bx);return Object.values(c).reduce((a,v)=>a+v,0)===bx.reduce((a,b)=>a+b.c,0)})&&byCat(ST.B.WLRCO051026A.slice(0,2)).A===10")
    print(('PASS' if ok else 'FAIL'),'en el packing list las piezas por categoría suman las piezas vivas (con Amarillo)')
    pg.evaluate("go('emb:0')"); pg.click('[data-a=cp]'); pg.wait_for_timeout(300)
    body=pg.evaluate("ST.O[0]&&ST.O[0].body||''"); import re as _re
    m=_re.search(r'Langostas: (\d+) \(([^)]*)\)',body); parts=[int(x) for x in _re.findall(r'(\d+)',m.group(2))] if m else []
    print(('PASS' if m and 'Amarillo 10' in m.group(2) and sum(parts)==int(m.group(1)) else 'FAIL'),'el informe de cierre cuenta Amarillo y sus categorías suman las langostas:',m and m.group(0))
    pg.evaluate("ST.P[0].closed=false;ST.O=[];save()")
    # auditoría #5: dos embarques con el mismo nombre; el PDF del informe es el del embarque que se cerró
    u1=pg.evaluate("(()=>{const p0=ST.P[0];ST.P.push({...p0,u:uidS(),h:1,z:[1,0,0,0],c:p0.c.map(x=>x.slice()),alive:null,closed:false});ST.B.WLRCO051026A[2].d=1;save();return ST.P[1].u})()")
    pg.evaluate("go('emb:1')"); pg.click('[data-a=cp]'); pg.wait_for_timeout(300)
    print(('PASS' if pg.evaluate("ST.O[0].pu")==u1 and pg.evaluate("ST.P[0].n===ST.P[1].n") else 'FAIL'),'el informe guarda el id fijo del embarque (los dos embarques se llaman igual)')
    pg.evaluate("ST.O.push({u:uidS(),subject:'Informe viejo',t:now(),to:[],body:'x',pn:ST.P[0].n,att:'x.pdf'});save();go('admin')")
    at=pg.evaluate("[...document.querySelectorAll('[data-pdf^=\"dl:emb\"]')].map(b=>b.dataset.pdf)")
    print(('PASS' if at==['dl:embu:'+u1,'dl:embn:'+pg.evaluate('ST.P[0].n')] else 'FAIL'),'Administración: el PDF del informe busca por id fijo; los informes viejos, por nombre',at)
    pg.evaluate("document.querySelectorAll('#app details').forEach(d=>d.open=true)")
    with pg.expect_download() as d3: pg.locator(f'[data-pdf="dl:embu:{u1}"]').click()
    raw=open(d3.value.path(),'rb').read()
    print(('PASS' if raw[:5]==b'%PDF-' and b'(Cerrado)' in raw else 'FAIL'),'el PDF que sale es el del embarque cerrado')
    pg.evaluate("(()=>{ST.B.WLRCO051026A[2].d=0;ST.P.splice(1,1);ST.O=[];save()})()")
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
