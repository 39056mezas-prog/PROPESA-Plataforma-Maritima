"""Prueba PROPESA (botones_t). Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/botones_t.py"""
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
pages=['inicio','recepcion','lote:WLRCO051026A','lote:WLRCO061026B','ordenes','orden:1','orden:2','empaque','empacar:1.1','empacar:2.1','embarques','emb:0','cierre','temperatura','admin']
found=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw in [(390,844),(1180,820)]:
        pg=b.new_page(viewport={'width':vw[0],'height':vw[1]});last={'a':''}
        pg.on('pageerror',lambda e:found.append((vw[0],last['a'],str(e))));pg.on('dialog',lambda d:d.dismiss())
        pg.goto(BASE);pg.evaluate('s=>localStorage.setItem("propesa-v4",s)',seed);pg.reload()
        pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
        for route in pages:
            pg.evaluate('s=>{localStorage.setItem("propesa-v4",s);ST=JSON.parse(s)}',seed);pg.evaluate(f"go('{route}')")
            n=pg.evaluate("document.querySelectorAll('main button, main [data-go]').length")
            for i in range(n):
                pg.evaluate('s=>{localStorage.setItem("propesa-v4",s);ST=JSON.parse(s)}',seed);pg.evaluate(f"go('{route}')")
                # open forms first for richer state
                els=pg.query_selector_all('main button, main [data-go]')
                if i>=len(els):break
                el=els[i];lab=(el.get_attribute('data-a') or el.get_attribute('data-oa') or el.get_attribute('data-go') or el.get_attribute('data-pk') or el.get_attribute('data-sh') or el.get_attribute('data-pdf') or el.inner_text()[:25])
                if lab in ('lo','rst') or (el.get_attribute('data-pdf') or '').startswith('mail'):continue
                last['a']=f'{route} -> {lab}'
                try:
                    if el.is_visible() and el.is_enabled(): el.click(timeout=1500)
                    # second-level: click every button again once in new view
                    els2=pg.query_selector_all('main button[data-a], main button[data-oa], main button[data-sh]')
                    for e2 in els2[:12]:
                        l2=e2.get_attribute('data-a') or e2.get_attribute('data-oa') or e2.get_attribute('data-sh')
                        if l2 in ('lo','rst'):continue
                        last['a']=f'{route} -> {lab} -> {l2}'
                        try:
                            if e2.is_visible() and e2.is_enabled():e2.click(timeout=1000)
                        except Exception:pass
                except Exception as ex:pass
    b.close()
seen=set()
for f in found:
    if f[2] in seen and len(seen)>15:continue
    seen.add(f[2]);print(f)
print('total',len(found))
print(('PASS' if not found else 'FAIL')+' ningún botón produce errores de JavaScript')
