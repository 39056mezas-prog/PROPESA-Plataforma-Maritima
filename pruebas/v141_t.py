"""v1.41.0 · Planta 3D ligera en celular y app instalable (pedido del usuario, 7/nov/2026: «el 3D es muy pesado, cuando está abierto
rompe todo lo demás en el celular; quiero poder descargar la app»).
- La planta es UN lienzo (canvas) del tamaño del recuadro, sin capas CSS 3D; en celular los botones de la cámara van en fila abajo
  y la planta se encuadra arriba de ellos; tocar con el dedo un tanque lo acerca.
- «Instalar app» a la vista: en el menú (si no está instalada) y en la pantalla de acceso; el manifiesto lleva id y descripción.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/v141_t.py"""
import os, json
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
LOT = ("([lot,tank,kz,kb,dias,pv])=>{const r=dLoc(new Date(Date.now()-dias*864e5));"
       "addLot({lot,origin:pvBy(pv).n,pv,sp:1,tank,rdate:r,time:'09:00',tempT:'58',tempP:'59',kgbox:String(kb),desp:'0',"
       "k0:String(kz[0]||''),k1:String(kz[1]||''),k2:String(kz[2]||''),k3:String(kz[3]||'')});save()}")
m = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'manifest.webmanifest')))
chk(m.get('id') == '/' and m.get('display') == 'standalone' and m.get('description') and any(i['sizes'] == '512x512' for i in m['icons']), 'manifiesto: id, standalone, descripción e ícono de 512')
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw, vh, sch in [(390, 844, 'light'), (360, 740, 'dark'), (768, 1024, 'light')]:
        c = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=3, is_mobile=True, has_touch=True, color_scheme=sch)
        pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        tag = f'{vw}px {sch}'
        pg.goto(BASE); pg.evaluate(FIX); pg.reload(); pg.wait_for_timeout(300)
        chk(pg.locator('.auin [data-pm=inst]').count() == 1, f'{tag}: acceso con «Instalar la app en este equipo»')
        pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(300)
        pg.evaluate(LOT, ['WLRCO211026', 'T1', [400, 300, 300, 200], 30, 0, 1]); pg.evaluate(LOT, ['WLREM301026', 'T3', [170, 100, 0, 0], 34, 3, 2])
        pg.evaluate("go('inicio')"); pg.wait_for_timeout(700)
        chk(pg.locator('.t3v canvas.t3cv').count() == 1 and pg.locator('.t3w, .t3f').count() == 0, f'{tag}: el 3D es un solo lienzo')
        cw = pg.evaluate("(()=>{const c=document.querySelector('.t3cv'),v=document.querySelector('.t3v');return [c.width,c.height,v.clientWidth,v.clientHeight]})()")
        chk(cw[0] <= cw[2] * 2 + 1 and cw[1] <= cw[3] * 2 + 1 and cw[0] > 0, f'{tag}: el lienzo no pasa de 2× aunque la pantalla sea 3× ({cw})')
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{tag}: sin desbordes')
        chk(pg.evaluate("T3.H.filter(h=>h.k!=null).length") == pg.evaluate("T3.M.O.filter(o=>o.C).reduce((s,o)=>s+o.C.length,0)") and pg.evaluate("T3.H.filter(h=>h.k==null).length") == 6, f'{tag}: se dibujan los 6 tanques y solo las tinas con langosta (v1.42.1)')
        # la planta completa queda dentro del recuadro libre de botones
        inside = pg.evaluate("""(()=>{const v=document.querySelector('.t3v'),A=t3Area(v),pr=t3Pr(T3,v.clientWidth,v.clientHeight),P=T3P;let ok=true;
          for(const X of [0,P.W])for(const Y of [0,P.D])for(const Z of [0,300]){const q=pr(X,Y,Z);if(q[0]<A.x0-2||q[0]>A.x1+2||q[1]<A.y0-2||q[1]>A.y1+2)ok=false}return ok})()""")
        chk(inside, f'{tag}: toda la planta se ve, centrada y sin quedar debajo de los botones')
        if vw < 700:
            row = pg.evaluate("(()=>{const c=document.querySelector('.t3ctl'),v=document.querySelector('.t3v').getBoundingClientRect(),r=c.getBoundingClientRect();return r.width>r.height&&r.bottom<=v.bottom&&r.bottom>v.bottom-70})()")
            chk(row, f'{tag}: botones de la cámara en fila abajo')
        pg.locator('.t3v').scroll_into_view_if_needed(); pg.wait_for_timeout(100)
        sp = pg.evaluate("t3Spot('T1')")
        if sp: pg.touchscreen.tap(sp['x'], sp['y'])
        pg.wait_for_timeout(900)
        chk(pg.evaluate("T3.zoom&&TQSEL==='T1'"), f'{tag}: tocar con el dedo el agua de T1 lo acerca')
        chk(pg.locator('.tqd').count() == 1 and pg.evaluate("document.querySelector('.tqd').getBoundingClientRect().height") > 50, f'{tag}: el resto de la página (tablero de tanques) sigue ahí')
        if vw < 700: pg.click('.mb'); pg.wait_for_timeout(300)
        chk(pg.locator('.sb [data-pm=inst]').count() == 1, f'{tag}: «Instalar app» en el menú')
        pg.locator('.sb [data-pm=inst]').click(); pg.wait_for_timeout(300)
        chk(pg.locator('#inst').count() == 1 and 'Instala la app PROPESA' in pg.inner_text('#inst'), f'{tag}: «Instalar app» abre la ventana con los pasos')
        c.close()
    # ya instalada: no se ofrece
    c = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    pg = c.new_page(); pg.add_init_script("const _mm=window.matchMedia;window.matchMedia=q=>q.includes('standalone')?{matches:true,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}}:_mm.call(window,q)")
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); pg.wait_for_timeout(300)
    chk(pg.locator('[data-pm=inst]').count() == 0, 'app ya instalada: no ofrece instalarla en el acceso')
    pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(300)
    chk(pg.locator('.sb [data-pm=inst]').count() == 0, 'app ya instalada: no sale en el menú')
    c.close(); b.close()
print('Errores JS:', errs if errs else 'ninguno')
print('RESULTADO:', 'TODO BIEN' if not fails and not errs else f'{len(fails)} fallas')
