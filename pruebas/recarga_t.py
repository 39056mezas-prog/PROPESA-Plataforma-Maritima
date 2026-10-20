"""Prueba PROPESA (recarga_t): al recargar la página no se cierra la sesión y se conserva la pantalla y lo escrito.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/recarga_t.py"""
import json,os
from playwright.sync_api import sync_playwright
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos','seed.json')).read()
errs=[]
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
def fresh(b,vw=(1180,820)):
    pg=b.new_page(viewport={'width':vw[0],'height':vw[1]});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',seed)
    pg.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('propesa-v4'));s.OR.push({id:3,etd:'2026-10-14',lines:[{id:1,city:'HKG',cons:0,cli:'LHD',boxes:6}],sh:{}});localStorage.setItem('propesa-v4',JSON.stringify(s))})()")
    pg.reload();return pg
def login(pg,u,p):pg.fill('#le',u);pg.fill('#lp',p);pg.click('[data-a=lg]')
def reload(pg):pg.wait_for_timeout(300);pg.reload();pg.wait_for_timeout(200)
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw in [(1180,820),(390,844)]:
        w=vw[0]
        # 1) Administrador: Entrada con el formulario a medias
        pg=fresh(b,vw);login(pg,'admin@propesa.mx','admin123')
        pg.evaluate("go('recepcion')");pg.click('[data-a=nf]');pg.select_option('#fo','1');pg.fill('#fl','');pg.click('#fl');pg.keyboard.type('wlrco131026');pg.fill('#fk1','55.5')
        reload(pg)
        chk(pg.locator('#le').count()==0,f'{w} admin sigue dentro después de recargar')
        chk(pg.locator('#fo').count()==1 and pg.input_value('#fo')=='1',f'{w} el formulario de Entrada sigue abierto con el proveedor')
        chk(pg.input_value('#fl')=='WLRCO131026' and pg.input_value('#fk1')=='55.5',f'{w} se conservan lote y kilos')
        # 2) Orden a medias
        pg.evaluate("go('orden:1')");(pg.locator('[data-oa=add]').count() and pg.click('[data-oa=add]'));pg.fill('#ol_z1','5');pg.fill('#ol_z2','2');reload(pg)
        chk(pg.input_value('#ol_z1')=='5' and pg.input_value('#ol_n')=='7',f'{w} la línea de orden a medias se conserva')
        # 3) Nota sin guardar en un lote
        pg.evaluate("go('lote:WLRCO051026A')");pg.fill('#ntx','revisar tanque 2');reload(pg)
        chk('lote' in pg.evaluate('V.v') and pg.input_value('#ntx')=='revisar tanque 2',f'{w} la nota sin guardar se conserva en la misma pantalla')
        # 4) Búsqueda
        pg.evaluate("go('buscar:HXH')");reload(pg);chk(pg.evaluate('V.v')=='buscar' and pg.evaluate('V.id')=='HXH',f'{w} la búsqueda se conserva')
        # 5) Cerrar sesión borra todo
        pg.evaluate("document.querySelector('[data-a=lo]')?document.querySelector('[data-a=lo]').click():(me=null,render())");reload(pg)
        chk(pg.locator('#le').count()==1,f'{w} después de cerrar sesión, recargar pide entrar')
        chk(pg.evaluate("localStorage.getItem('propesa-ui')") is None,f'{w} al cerrar sesión no quedan borradores')
        # 6) Encargado de piso: Empaque con una hielera a medias
        login(pg,'piso@propesa.mx','piso123');pg.evaluate("go('pemp:3.1')");pg.click('[data-pe="lot:WLRCO061026B"]')
        pg.click('#pps1 .pbn');pg.click('#kpad [data-kp="d:9"]');pg.click('#kpad [data-kp="k:R"]');pg.wait_for_timeout(150)
        pg.click('#pps2 .pbn');pg.click('#kpad [data-kp="d:1"]');pg.click('#kpad [data-kp="d:4"]')
        pg.click('#pps3 .pbn');pg.click('#kpad [data-kp="k:V"]')
        reload(pg)
        chk(pg.evaluate('V.v+":"+V.id')=='pemp:3.1' and pg.locator('.pkh').count()==1,f'{w} piso regresa a la misma pantalla de empaque, con el lote elegido')
        chk(pg.input_value('.ppc[data-slot="2"]')=='14',f'{w} las piezas escritas de la hielera 2 se conservan')
        chk(pg.evaluate("(PE.rows[3]||{}).k")=='V' and pg.evaluate("KPT.t")=='slot:3' and pg.get_attribute('#kpad [data-kp="k:V"]','aria-pressed')=='true',f'{w} la categoría elegida de la hielera 3 y la hielera activa del teclado se conservan')
        st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
        chk(sum(1 for x in st['B']['WLRCO061026B'] if x['o']=='3.1')==1,f'{w} la hielera 1 ya guardada sigue guardada (no se duplica)')
        pg.click('#pps2 .pbn');pg.click('#kpad [data-kp="k:V"]');pg.wait_for_timeout(150)
        st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
        chk(sum(1 for x in st['B']['WLRCO061026B'] if x['o']=='3.1')==2,f'{w} después de recargar se puede seguir empacando')
        # 7) Registrar entradas en piso a medias
        pg.evaluate("go('pent')");pg.select_option('[data-pr="1:origin"]','2');pg.fill('[data-pr="1:lot"]','');pg.click('[data-pr="1:lot"]');pg.keyboard.type('abc9');reload(pg)
        chk(pg.input_value('[data-pr="1:origin"]')=='2' and pg.input_value('[data-pr="1:lot"]')=='ABC9',f'{w} la hoja de entradas de piso se conserva')
        # 8) Sesión vencida o usuario borrado
        pg.evaluate("LAST_ACT=Date.now()-13*36e5;localStorage.setItem('propesa-ses',JSON.stringify({u:2,exp:Date.now()-1000}))");pg.reload()
        chk(pg.locator('#le').count()==1,f'{w} sesión vencida pide entrar')
        login(pg,'piso@propesa.mx','piso123');pg.wait_for_timeout(300)
        pg.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('propesa-v4'));s.U=s.U.filter(u=>u.id!==2);localStorage.setItem('propesa-v4',JSON.stringify(s))})()");pg.reload()
        chk(pg.locator('#le').count()==1,f'{w} usuario eliminado pide entrar')
        # 9) Datos dañados en propesa-ui no rompen la app
        login(pg,'admin@propesa.mx','admin123');pg.wait_for_timeout(300)
        for bad in ['{"u":1,"V":{"v":"orden","id":"999"}}','{"u":1,"V":{"v":"emb","id":"50"}}','{"u":1,"V":{"v":"lote","id":"NOEXISTE"}}','{"u":1,"V":{"v":"pemp","id":"9.9"}}','{"u":1,"V":{"v":"noexiste"}}','no es json',
                    '{"u":1,"V":{"v":"inicio"},"f":{"input[data-x=\\"]\\"]":"1","###":"2"}}']:
            pg.evaluate("v=>localStorage.setItem('propesa-ui',v)",bad);pg.reload();pg.wait_for_timeout(100)
            t=pg.inner_text('body');chk(pg.locator('#le').count()==0 and 'undefined' not in t and 'NaN' not in t,f'{w} propesa-ui raro no rompe ({bad[:40]})')
        pg.close()
    b.close()
chk(not errs,'sin errores de JavaScript '+str(errs[:3]))
