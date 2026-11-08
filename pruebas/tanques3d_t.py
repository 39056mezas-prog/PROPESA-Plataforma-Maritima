"""v1.31.0 · Tanques en 3D (pedido del usuario, 2/nov/2026) en Entrada y en Panel general.
Canastas = kg de cada talla ÷ kg por caja en tanque (incompleta punteada); listón con el color de la talla de SU maquila (Abel con
Jumbo morado); días en tanque y borde rojo al pasar los días del proveedor; lote sin kg por caja: aviso rojo que lleva al lote;
tocar el agua acerca la cámara y elige el mismo tanque del tablero plano; tocar una canasta enseña su lote; arrastrar gira sin abrir
nada; botones de cámara; «Ocultar 3D» se recuerda; letreros encima (capa plana) y sin desbordes en 390/820/1440, claro y oscuro.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/tanques3d_t.py"""
import os
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',role:'piso',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
LOT = ("([lot,tank,kz,kb,dias,pv])=>{const r=dLoc(new Date(Date.now()-dias*864e5));"
       "addLot({lot,origin:pvBy(pv).n,pv,sp:1,tank,rdate:r,time:'09:00',tempT:'58',tempP:'59',kgbox:String(kb),desp:'0',"
       "k0:String(kz[0]||''),k1:String(kz[1]||''),k2:String(kz[2]||''),k3:String(kz[3]||'')});save()}")
def setup(pg):
    pg.goto(BASE); pg.evaluate(FIX); pg.reload()
    pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(250)
    # PROPESA: proveedor 1 aguanta 10 días; un lote de 12 días en T3 (340 kg Chica = 10 canastas, 85 kg Mediana = 2.5 → 3, una incompleta)
    pg.evaluate("ST.PV=PV0.map(x=>({...x}));ST.PV[0].dm=10;save()")
    pg.evaluate(LOT, ['WLRCO211026', 'T3', [340, 85, 0, 0], 34, 12, 1])
    pg.evaluate(LOT, ['WLREM301026', 'T1', [170, 0, 0, 0], 34, 3, 2])
    pg.evaluate(LOT, ['WLRLE311026', 'T2', [100, 0, 0, 0], 34, 2, 3])
    pg.evaluate("ST.R.find(r=>r.lot==='WLRLE311026').kgbox=null;save()")  # lote viejo sin kg por caja
    # Abel: su Jumbo es morado (tallas propias); 68 kg de Jumbo en T3 = 2 canastas
    pg.evaluate("mqSet(2);ST.SZ=SZ0.map(q=>({...q}));ST.SZ[3].c='#7242F5';szSync();save()")
    pg.evaluate(LOT, ['WLRCO011126', 'T3', [0, 0, 0, 68], 34, 1, 1])
    pg.evaluate("mqSet(1);FOLD['ent-tq']=true;go('recepcion')"); pg.wait_for_timeout(250)
rgb = lambda h: 'rgb(%d, %d, %d)' % tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    setup(pg)
    chk(pg.evaluate("Math.round(bal('WLRCO211026')/1000)") == 425, 'el lote de prueba tiene 425 kg')
    # ---------- Entrada (maquila abierta)
    chk(pg.locator('.t3v').count() == 1 and pg.locator('.tqd .tqmap .tqm').count() == 6, 'Entrada: el 3D va arriba y el tablero plano sigue abajo')
    n3 = pg.locator('.t3c[data-t3c^="T3:"]:not(.t3s):not(.t3e)').count()
    chk(n3 == 13, f'T3: 340 kg Chica ÷ 34 = 10 canastas + 85 kg Mediana = 3 (hay {n3})')
    chk(pg.locator('.t3c.t3inc[data-t3c^="T3:"]:not(.t3s):not(.t3e)').count() == 1, 'una canasta incompleta (punteada): la de 17 kg')
    chk(pg.locator('.t3c[data-t3c^="T1:"]:not(.t3s):not(.t3e)').count() == 5, 'T1: 170 kg ÷ 34 = 5 canastas')
    cols = pg.evaluate("[...document.querySelectorAll('.t3c[data-t3c^=\"T3:\"] .t3rib')].map(e=>getComputedStyle(e).backgroundColor)")
    chk(cols.count(rgb('#FFFFFF')) == 10 and cols.count(rgb('#E5484D')) == 3, 'listones: 10 blancos (Chica) y 3 rojos (Mediana)')
    chk(pg.locator('.t3c.t3old[data-t3c^="T3:"]:not(.t3s):not(.t3e)').count() == 13, 'el lote de 12 días (aguanta 10) va con borde rojo')
    tag = pg.evaluate("[...document.querySelectorAll('.t3tag')].map(e=>e.textContent).find(t=>t.startsWith('T3'))") or ''
    al3 = pg.evaluate("[...document.querySelectorAll('.t3tag')].find(e=>e.textContent.startsWith('T3')).querySelector('.t3al')!==null")
    chk('13 canastas' in tag and '425 kg' in tag and '12 días' in tag and al3, f'letrero de T3: canastas, kg y días del más viejo ({tag})')
    chk(pg.locator('.t3lab .t3sign').count() == 6, 'los 6 letreros «TANQUE N» (T6 sin filtro también)')
    chk(pg.locator('.t3fil').count() == 5 * 3, '5 filtros (T6 no tiene)')
    chk(pg.locator('.t3w .t3dl').count() == 2 and pg.locator('.t3lab .t3dl').count() == 0, 'v1.31.2: «Andén de recepción» y «Selección y lavado» van pegados a la pared (no flotan)')
    al = pg.inner_text('#main')
    chk('wlrle311026 no tiene kg por caja en tanque' in al.lower(), 'lote sin kg por caja: aviso rojo')
    pg.locator('.alb', has_text='no tiene kg por caja').locator('[data-go="lote:WLRLE311026"]').click(); pg.wait_for_timeout(150)
    chk(pg.evaluate("V.v=='lote'&&V.id=='WLRLE311026'"), 'el aviso lleva al lote para completarlo')
    pg.evaluate("FOLD['ent-tq']=true;go('recepcion')"); pg.wait_for_timeout(200)
    s0 = pg.evaluate("T3.s")
    pg.locator('[data-t3t=T3]').dispatch_event('click'); pg.wait_for_timeout(900)
    chk(pg.evaluate("T3.zoom&&TQSEL==='T3'") and pg.evaluate("T3.s") > s0 * 1.5, 'tocar el agua de T3 acerca la cámara')
    chk(pg.get_attribute('.tqm[data-tq=T3]', 'aria-pressed') == 'true' and 'Tanque 3' in pg.inner_text('.tqd .tqc'), 'y elige T3 en el tablero de abajo (mismo detalle)')
    lt = pg.evaluate("[...document.querySelectorAll('.t3lab .t3lt')].map(e=>e.textContent)")
    chk(any('WLRCO211026 · 12 días' in t for t in lt), f'de cerca: letrero del lote con sus días ({lt})')
    chk(pg.locator('.t3lab .t3tag:not(.t3hid)').count() == 0, 'de cerca no salen los letreros de los otros tanques')
    pg.locator('.t3c[data-t3c="T3:0"]').first.dispatch_event('click'); pg.wait_for_timeout(200)
    pk = pg.inner_text('.t3pick') if pg.locator('.t3pick').count() else ''
    chk('WLRCO211026' in pk and 'Chica' in pk and '34.0 kg' in pk and '12 días en tanque' in pk and 'aguanta 10' in pk, f'tocar una canasta: lote, talla, kg y días ({pk!r})')
    chk(pg.locator('.t3c.t3hl').count() >= 13, 'se marcan las canastas de ese lote')
    chk(pg.locator('.t3c[data-t3c^="T3:"]:not(.t3hl)').count() == 0, 'v1.31.3: las canastas de los demás lotes se guardan')
    chk(pg.evaluate("getComputedStyle(document.querySelector('.t3c.t3hl')).backgroundColor") == 'rgb(22, 166, 209)', 'v1.31.3: toda la canasta elegida cambia de color')
    chk(not any('WLRCO011126' in t for t in pg.evaluate("[...document.querySelectorAll('.t3lab .t3lt')].map(e=>e.textContent)")), 'v1.31.3: solo queda el letrero del lote elegido')
    pg.click('.t3pick [data-t3a=unpick]'); pg.wait_for_timeout(150)
    chk(pg.locator('.t3pick').count() == 0 and pg.locator('.t3c.t3hl').count() == 0 and pg.locator('.t3c[data-t3c^="T3:"]:not(.t3s):not(.t3e)').count() == 13, '«Ver todas las canastas» las vuelve a enseñar')
    pg.locator('.t3c[data-t3c="T3:0"]').first.dispatch_event('click'); pg.wait_for_timeout(200)
    pg.click('.t3pick [data-go]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("V.v=='lote'&&V.id=='WLRCO211026'"), '«Abrir lote» abre el lote')
    pg.evaluate("FOLD['ent-tq']=true;go('recepcion')"); pg.wait_for_timeout(300)
    chk(pg.evaluate("T3.zoom") and pg.locator('.t3back').count() == 1, 'al volver sigue de cerca, con «Ver toda la planta»')
    pg.click('.t3back'); pg.wait_for_timeout(900)
    chk(not pg.evaluate("T3.zoom") and abs(pg.evaluate("T3.s") - s0) < 1e-3, '«Ver toda la planta» regresa la cámara')
    # arrastrar: gira sin abrir nada
    pg.locator('.t3v').scroll_into_view_if_needed(); bx = pg.locator('.t3v').bounding_box(); cx, cy = bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2
    az0 = pg.evaluate("T3.az"); pg.mouse.move(cx, cy); pg.mouse.down()
    for i in range(1, 16): pg.mouse.move(cx + i * 10, cy + i * 2)
    pg.mouse.up(); pg.wait_for_timeout(150)
    chk(abs(pg.evaluate("T3.az") - az0) > 30 and not pg.evaluate("T3.zoom"), 'arrastrar gira la vista y no abre ningún tanque')
    chk(pg.evaluate("document.querySelector('.t3w').dataset.q") == pg.evaluate("(()=>{const q=t3Q();return ''+(+q.s)+(+q.e)})()"), 'al girar a otro cuadrante se vuelven a dibujar los lados que se ven')
    pg.click('[data-t3a=fit]'); pg.wait_for_timeout(900)
    chk(abs(pg.evaluate("T3.az") - 35) < 0.01, '⌂ regresa la vista de siempre')
    pg.click('[data-t3a=r]'); pg.wait_for_timeout(900); chk(abs(pg.evaluate("T3.az") - 80) < 0.01, '⟳ gira 45°')
    s1 = pg.evaluate("T3.s"); pg.click('[data-t3a=in]'); pg.wait_for_timeout(900); chk(pg.evaluate("T3.s") > s1 * 1.3, '+ acerca')
    pg.mouse.move(cx, cy); s2 = pg.evaluate("T3.s"); pg.mouse.wheel(0, 300); pg.wait_for_timeout(100); chk(pg.evaluate("T3.s") < s2, 'la rueda del mouse aleja')
    pg.click('[data-t3a=fit]'); pg.wait_for_timeout(900)
    # ---------- Panel general (todas las maquilas)
    pg.evaluate("go('general')"); pg.wait_for_timeout(300)
    chk(pg.locator('.t3v').count() == 1 and pg.locator('.tqgen [data-tq=T4]').count() == 1, 'Panel general: 3D y tablero de tanques')
    chk(pg.evaluate("(()=>{const v=document.querySelector('.t3v').getBoundingClientRect().top;return document.querySelector('#main .g4').getBoundingClientRect().top<v&&[...document.querySelectorAll('#main table, .tqgen')].every(e=>e.getBoundingClientRect().top>v)})()"), 'v1.39.0: en Panel general van primero los 4 totales, luego el 3D y después las tablas')
    n3 = pg.locator('.t3c[data-t3c^="T3:"]:not(.t3s):not(.t3e)').count()
    chk(n3 == 15, f'T3 junta PROPESA (13) y Abel (2): {n3}')
    cols = pg.evaluate("[...document.querySelectorAll('.t3c[data-t3c^=\"T3:\"] .t3rib')].map(e=>getComputedStyle(e).backgroundColor)")
    chk(cols.count(rgb('#7242F5')) == 2, 'las canastas de Abel llevan su Jumbo morado')
    pg.locator('[data-t3t=T3]').dispatch_event('click'); pg.wait_for_timeout(900)
    mq = pg.evaluate("[...document.querySelectorAll('.t3lab .t3mq')].map(e=>e.textContent)")
    chk(any('PROPESA · 13' in t for t in mq) and any('Abel · 2' in t for t in mq), f'de cerca: letrero de cada maquila ({mq})')
    pg.locator('.t3c[data-t3c="T3:14"]').first.dispatch_event('click'); pg.wait_for_timeout(200)
    pk = pg.inner_text('.t3pick') if pg.locator('.t3pick').count() else ''
    chk('Abel' in pk and 'WLRCO011126' in pk, f'en Panel general la canasta dice su maquila ({pk!r})')
    vis = pg.locator('.t3c[data-t3c^="T3:"]:not(.t3s):not(.t3e)').count(); hl = pg.locator('.t3c.t3hl[data-t3c^="T3:"]:not(.t3s):not(.t3e)').count()
    chk(vis == 2 and hl == 2, f'v1.31.3: con el lote de Abel elegido solo quedan sus 2 canastas, de color (hay {vis}, {hl} de color)')
    lt = pg.evaluate("[...document.querySelectorAll('.t3lab .t3lt')].map(e=>e.textContent)"); mq = pg.evaluate("[...document.querySelectorAll('.t3lab .t3mq')].map(e=>e.textContent)")
    chk(len(lt) == 1 and 'WLRCO011126' in lt[0] and len(mq) == 1 and 'Abel' in mq[0], f'v1.31.3: solo quedan los letreros de ese lote y su maquila ({lt}, {mq})')
    pg.click('.t3pick [data-go]'); pg.wait_for_timeout(200)
    chk(pg.evaluate("V.v=='lote'&&MQ===2"), '«Abrir lote» entra a la maquila del lote')
    pg.evaluate("mqSet(1);FOLD['ent-tq']=true;go('recepcion')"); pg.wait_for_timeout(200)
    # ---------- Ocultar 3D (se recuerda)
    pg.click('[data-t3a=off]'); pg.wait_for_timeout(150)
    chk(pg.locator('.t3v').count() == 0 and pg.evaluate("localStorage.getItem('propesa-3d')") == '0', '«Ocultar 3D» lo quita y se recuerda en el equipo')
    pg.reload(); pg.wait_for_timeout(300); pg.evaluate("FOLD['ent-tq']=true;go('recepcion')"); pg.wait_for_timeout(150)
    chk(pg.locator('.t3v').count() == 0 and pg.locator('[data-t3a=on]').count() == 1, 'después de recargar sigue oculto, con «Ver tanques en 3D»')
    pg.click('[data-t3a=on]'); pg.wait_for_timeout(200); chk(pg.locator('.t3v').count() == 1, '«Ver tanques en 3D» lo regresa')
    pg.close()
    # ---------- tamaños y temas
    for vw, sch in [(1440, 'dark'), (820, 'light'), (820, 'dark'), (390, 'light'), (390, 'dark')]:
        pg = b.new_page(viewport={'width': vw, 'height': 900}, color_scheme=sch, has_touch=vw < 900)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        setup(pg); pg.wait_for_timeout(200)
        tag = f'{vw}px {sch}'
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{tag}: sin desbordes')
        r = pg.locator('.t3v').bounding_box()
        chk(r['width'] <= vw and 280 <= r['height'] <= 600, f'{tag}: el 3D cabe ({int(r["width"])}×{int(r["height"])})')
        ins = pg.evaluate("(()=>{const v=document.querySelector('.t3v').getBoundingClientRect();return [...document.querySelectorAll('.t3lab .t3tag')].filter(e=>!e.closest('[hidden]')).every(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.left>=v.left-40&&r.right<=v.right+40})})()")
        chk(ins, f'{tag}: los letreros de los tanques están dentro del 3D')
        chk('NaN' not in pg.inner_text('.t3v') and 'undefined' not in pg.inner_text('.t3v'), f'{tag}: sin NaN ni undefined')
        pg.close()
    b.close()
print('Errores JS:', errs if errs else 'ninguno')
print('RESULTADO:', 'TODO BIEN' if not fails and not errs else f'{len(fails)} fallas')
