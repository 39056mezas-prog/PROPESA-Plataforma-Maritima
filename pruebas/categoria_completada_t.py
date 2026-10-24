"""Prueba PROPESA (categoria_completada_t): en Empaque (vista completa) con el teclado abierto, cada hielera completada sigue
mostrando su categoría (Rojo / Verde / Blanco…), no solo «✔ Completada». Pedido del usuario (22/oct/2026).
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/categoria_completada_t.py"""
import json,os,shutil,tempfile
from playwright.sync_api import sync_playwright
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
seed=json.loads(open(T+'seed.json').read())
seed['OR'].append({'id':3,'etd':'2026-10-13','lines':[{'id':1,'city':'HKG','cons':0,'cli':'ABC','boxes':3}],'sh':{}})
S=json.dumps(seed);errs=[]
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw,sch in [((1440,900),'dark'),((820,1180),'light'),((390,844),'dark')]:
        tag=f'{vw[0]}'
        pg=b.new_page(viewport={'width':vw[0],'height':vw[1]},color_scheme=sch);pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-kp","1")}',S);pg.reload()  # teclado abierto
        pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]');pg.evaluate("syncShip(ST.OR[2],'HKG',0);save();go('empacar:3.1')")
        pg.click('[data-pk^="lot:"] >> nth=0')
        for r,(n,k) in enumerate([(10,'V'),(12,'R')]):
            pg.click(f'#pk_c{r}')  # la hielera activa del teclado
            for d in str(n):pg.click(f'#kpad [data-kp="d:{d}"]')
            pg.click(f'#kpad [data-kp="k:{k}"]');pg.wait_for_timeout(200)
        chk(pg.locator('.pkx.kpo').count()==1,tag+' teclado abierto')
        cv=pg.locator('.pkdn.is-done .pkcv')
        chk(pg.locator('.pkdn.is-done').count()==2,tag+' 2 hieleras completadas')
        chk(cv.count()==2 and all(cv.nth(i).is_visible() for i in range(cv.count())),tag+' la categoría se ve en las completadas')
        chk(cv.nth(0).inner_text().strip()=='Verde' and cv.nth(1).inner_text().strip()=='Rojo',tag+' Verde y Rojo: '+str([cv.nth(i).inner_text() for i in range(cv.count())]))
        # v1.13.1: el avance va arriba de las hieleras y no se mueve al desplazar
        chk(pg.evaluate("document.querySelector('#pkp').getBoundingClientRect().bottom<=document.querySelector('.pkt').getBoundingClientRect().top"),tag+' avance arriba de las hieleras')
        chk('2 completadas' in pg.inner_text('#pksum') and '67% completado' in pg.inner_text('#pksum'),tag+' avance 2 de 3: '+pg.inner_text('#pksum').replace('\n',' '))
        chk(not pg.evaluate("!!document.querySelector('.kpdock #pksum')"),tag+' el avance ya no está junto al teclado')
        rel="document.querySelector('#pkp').getBoundingClientRect().top-document.querySelector('.pkx').getBoundingClientRect().top"  # pegado a su tarjeta, no a la pantalla
        y0=pg.evaluate(rel);pg.mouse.move(200,500);pg.mouse.wheel(0,300);pg.wait_for_timeout(300)
        chk(abs(pg.evaluate(rel)-y0)<1,tag+' el avance se queda en su lugar al desplazar')
        ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth");chk(ov==0,tag+' sin desborde')
        pg.evaluate('scrollTo(0,0)');pg.screenshot(path=T+f'categoria_{tag}.png')
        pg.click('.kpclose');pg.wait_for_timeout(300);pg.screenshot(path=T+f'cerrado_{tag}.png')
        pg.close()
    b.close()
chk(not errs,'sin errores '+str(errs));print('OUT',OUT)
