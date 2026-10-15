"""Prueba PROPESA (titulo_t): en celular, la barra de arriba dice en qué sección estás (ícono + nombre).
En tablet y computadora no aparece (ahí se ve el menú lateral). Uso: python3 -m http.server 8765 y luego python3 -I pruebas/titulo_t.py"""
import json,os,shutil,tempfile
from playwright.sync_api import sync_playwright
BASE=os.environ.get('BASE','http://localhost:8765/index.html')
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
S=open(T+'seed.json').read();errs=[]
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
EXP=[('inicio','Panel',None),('recepcion','Entrada',1),('lote:WLRCO051026A','Entrada',1),('ordenes','Órdenes',2),('orden:1','Órdenes',2),('empaque','Empaque',3),('empacar:1.1','Empaque',3),
     ('embarques','Embarque',4),('emb:0','Embarque',4),('cierre','Mortalidad final',5),('temperatura','Temperatura',None),('admin','Administración',None)]
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,sch,fs in [(390,'light',None),(360,'dark','20'),(820,'light',None),(1440,'dark',None)]:
        tag=f'{w}{" 20px" if fs else ""}'
        pg=b.new_page(viewport={'width':w,'height':800},color_scheme=sch);pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',S)
        if fs:pg.evaluate("f=>localStorage.setItem('propesa-fs',f)",fs)
        pg.reload();pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
        for r,name,step in EXP:
            pg.evaluate(f"go('{r}')")
            vis=pg.evaluate("(()=>{const h=document.querySelector('.hdt');return !!h&&getComputedStyle(h).display!='none'})()")
            txt=pg.inner_text('.hdt') if vis else ''
            if w>700:  # v1.5: también en tablet y computadora, entre el buscador y Ajustes (pedido del usuario)
                ok=pg.evaluate("(()=>{const q=document.querySelector('#sq').getBoundingClientRect(),c=document.querySelector('.usr').getBoundingClientRect(),t=document.querySelector('.hdt').getBoundingClientRect();return t.left>=q.right-1&&t.right<=c.left+1&&Math.abs(t.top+t.height/2-(c.top+c.height/2))<12})()")
                chk(vis and name in txt and ok,f'{tag} {r}: dice «{name}» entre el buscador y Ajustes ({txt!r})')
                chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"),f'{tag} {r}: sin desborde');continue
            chk(vis and name in txt,f'{tag} {r}: dice «{name}» ({txt!r})')
            chk('Paso' not in txt,f'{tag} {r}: solo el nombre, sin «Paso N de 5»')
            chk(pg.locator('.hdt .hdti svg').count()==1,f'{tag} {r}: lleva el ícono del menú')
            one=pg.evaluate("(()=>{const a=document.querySelector('.mb').getBoundingClientRect(),c=document.querySelector('.usr').getBoundingClientRect(),t=document.querySelector('.hdt').getBoundingClientRect();return Math.abs(a.top-c.top)<4&&t.right<=c.left+1&&t.left>=a.right-1})()")
            chk(one,f'{tag} {r}: ☰, título y botones en un solo renglón, sin encimarse')
            chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"),f'{tag} {r}: sin desborde')
        # en Empaque dice el cliente y el lote que se está empacando
        key=pg.evaluate("(ST.OR.push({id:99,etd:'2026-10-14',lines:[{id:1,city:'HKG',cons:0,cli:'LHD',boxes:2}],sh:{}}),save(),'99.1')");pg.evaluate(f"go('empacar:{key}')");lt=pg.evaluate("lots().filter(z=>!R_(z).closed)[0]")
        if pg.locator('.pklb').count():pg.click(f'.pklb[data-pk="lot:{lt}"]')
        sub=pg.inner_text('#hdsub') if pg.locator('#hdsub').count() else ''
        chk(f'Lote {lt}' in sub and pg.evaluate(f"ST.OR.find(o=>o.id=={key.split('.')[0]}).lines.find(l=>l.id=={key.split('.')[1]}).cli") in sub,f'{tag} empacar: la barra dice cliente y lote ({sub!r})')
        pg.close()
    b.close()
chk(not errs,'sin errores '+str(errs))
