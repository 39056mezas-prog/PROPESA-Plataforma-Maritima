"""Tanques en 3D en Recepción y en Panel general (v1.31.0; desde v1.42.0, por tinas).
Cada tanque dibuja sus 30 tinas; una tina llena lleva el color de su talla (de SU maquila: Abel con Jumbo morado). Letrero por
tanque: «T3 · 13 tinas» (solo las que tiene; v1.43.0), kg y días del más viejo (rojo al pasar los días del proveedor).
Tocar un tanque acerca la cámara y elige el mismo tanque del tablero plano; tocar una tina enseña número, tanque, kg, talla, lote y
maquila; arrastrar gira sin abrir nada; botones de cámara; «Ocultar 3D» se recuerda; sin desbordes en 390/820/1440, claro y oscuro.
La planta es un solo lienzo (canvas, v1.41.0); las tinas se cuentan en el modelo (T3.M) y se tocan con t3Spot.
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
# v1.42.0: lotes por tinas. tn = [[tina, índice de talla, kg]]
LOT = ("([lot,tank,kz,tn,dias,pv])=>{const r=dLoc(new Date(Date.now()-dias*864e5));"
       "addLot({lot,origin:pvBy(pv).n,pv,sp:1,tank,rdate:r,time:'09:00',tempT:'58',tempP:'59',kgbox:'',desp:'0',"
       "k0:String(kz[0]||''),k1:String(kz[1]||''),k2:String(kz[2]||''),k3:String(kz[3]||'')});"
       "if(tn){const x=R_(lot);x.tn=tn.map(([n,i,g])=>[n,S[i],g*1000]);x.tts={[tank]:58}}save()}")
T340 = [[61 + i, 0, 34] for i in range(10)] + [[71, 1, 34], [72, 1, 34], [73, 1, 17]]  # 340 kg Chica (10 tinas) + 85 kg Mediana (3)
def setup(pg):
    pg.goto(BASE); pg.evaluate(FIX); pg.reload()
    pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(250)
    # PROPESA: proveedor 1 aguanta 10 días; un lote de 12 días en T3 (340 kg Chica = 10 canastas, 85 kg Mediana = 2.5 → 3, una incompleta)
    pg.evaluate("ST.PV=PV0.map(x=>({...x}));ST.PV[0].dm=10;save()")
    pg.evaluate(LOT, ['WLRCO211026', 'T3', [340, 85, 0, 0], T340, 12, 1])
    pg.evaluate(LOT, ['WLREM301026', 'T1', [170, 0, 0, 0], [[i, 0, 34] for i in range(1, 6)], 3, 2])
    pg.evaluate(LOT, ['WLRLE311026', 'T2', [100, 0, 0, 0], [[31, 0, 50], [32, 0, 50]], 2, 3])  # 100 kg en 2 tinas de T2
    # Abel: su Jumbo es morado (tallas propias); 68 kg de Jumbo en T3 = 2 canastas
    pg.evaluate("mqSet(2);ST.SZ=SZ0.map(q=>({...q}));ST.SZ[3].c='#7242F5';szSync();save()")
    pg.evaluate(LOT, ['WLRCO011126', 'T3', [0, 0, 0, 68], [[74, 3, 34], [75, 3, 34]], 1, 1])
    pg.evaluate("mqSet(1);FOLD['ent-tq']=true;go('recepcion')"); pg.wait_for_timeout(250)
CR = "((t,q)=>{const o=T3.M.O.find(o=>o.tk===t&&o.C);return o?o.C.filter(c=>c.o&&c.mine&&(!q||c[q])).length:0})"  # tinas llenas que se ven
def cr(pg, t, q=''): return pg.evaluate(CR + "(%r,%r)" % (t, q))
def tap(pg, t, k=None):
    pg.locator('.t3v').scroll_into_view_if_needed(); pg.wait_for_timeout(50)
    sp = pg.evaluate("t3Spot(%r,%s)" % (t, 'null' if k is None else k))
    if not sp: return False
    pg.mouse.click(sp['x'], sp['y']); return True
def px(pg, t, k):  # color del lienzo cerca de la esquina de la canasta k (fuera del listón)
    return pg.evaluate("""((t,k)=>{const v=document.querySelector('.t3v'),cv=v.querySelector('canvas'),c=T3.M.O.find(o=>o.tk===t&&o.C).C.find(c=>c.k===k),
     z=c.lay?T3P.ZW+1+T3P.CH*(c.lay+1):T3P.ZW+T3P.CH,q=t3Pr(T3,v.clientWidth,v.clientHeight)(c.x+6,c.y+48,z),d=cv.width/v.clientWidth,
     p=cv.getContext('2d').getImageData(Math.round(q[0]*d),Math.round(q[1]*d),1,1).data;return [p[0],p[1],p[2]]})(%r,%d)""" % (t, k))
rgb = lambda h: 'rgb(%d, %d, %d)' % tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    setup(pg)
    chk(pg.evaluate("Math.round(bal('WLRCO211026')/1000)") == 425, 'el lote de prueba tiene 425 kg')
    # ---------- Entrada (maquila abierta)
    chk(pg.locator('.t3v').count() == 1 and pg.locator('.tqd .tqmap .tqm').count() == 6, 'Entrada: el 3D va arriba y el tablero plano sigue abajo')
    n3 = cr(pg, 'T3')
    chk(n3 == 13, f'T3: 10 tinas de Chica + 3 de Mediana del lote de PROPESA (hay {n3})')
    chk(cr(pg, 'T1') == 5, 'T1: 5 tinas')
    chk(pg.evaluate("T3.M.O.filter(o=>o.C).every(o=>o.C.every(c=>c.o))") and pg.evaluate("T3.M.O.filter(o=>o.C).reduce((s,o)=>s+o.C.length,0)") == pg.evaluate("tnOcc().size"), 'v1.42.1: solo se dibujan las tinas con langosta (las vacías no salen)')
    cols = pg.evaluate("T3.M.O.find(o=>o.tk==='T3'&&o.C).C.filter(c=>c.o&&c.mine).map(c=>c.o.col.toUpperCase())")
    chk(cols.count('#FFFFFF') == 10 and cols.count('#E5484D') == 3, 'cada tina lleva el color de su talla: 10 blancas (Chica) y 3 rojas (Mediana)')
    chk(pg.evaluate("T3.M.O.find(o=>o.tk==='T3'&&o.C).C.filter(c=>c.o&&!c.mine).length") == 2, 'las 2 tinas de Abel en T3 se ven ocupadas, pero no se cuentan en PROPESA')
    tag = pg.evaluate("[...document.querySelectorAll('.t3tag')].map(e=>e.textContent).find(t=>t.startsWith('T3'))") or ''
    al3 = pg.evaluate("[...document.querySelectorAll('.t3tag')].find(e=>e.textContent.startsWith('T3')).querySelector('.t3al')!==null")
    chk('T3 · 13 tinas' in tag and 'de 30' not in tag and '425 kg' in tag and '12 días' in tag and al3, f'letrero de T3: tinas, kg y días del más viejo, en rojo ({tag})')
    tag2 = pg.evaluate("[...document.querySelectorAll('.t3tag')].map(e=>e.textContent).find(t=>t.startsWith('T2'))") or ''
    chk('T2 · 2 tinas' in tag2 and '100 kg' in tag2 and 'sin tina' not in tag2, f'T2 dice solo sus 2 tinas y sus kg ({tag2})')
    chk(pg.evaluate("T3.labs.filter(l=>l.sg).length") == 6 and pg.locator('.t3lab .t3sign').count() == 0, 'los 6 letreros «TANQUE N» (T6 sin filtro también), dibujados en el lienzo')
    chk(pg.evaluate("T3.M.O.filter(o=>o.pl).length") == 5, '5 filtros (T6 no tiene)')
    chk(pg.locator('.t3v canvas.t3cv').count() == 1 and pg.locator('.t3v [style*=preserve-3d], .t3w, .t3f').count() == 0, 'v1.41.0: un solo lienzo, nada de capas CSS 3D')
    chk(pg.evaluate("(()=>{const c=document.querySelector('.t3cv'),v=document.querySelector('.t3v');return c.width>0&&c.width<=v.clientWidth*2+1&&c.height<=v.clientHeight*2+1})()"), 'v1.41.0: el lienzo mide lo del recuadro (máx. 2× de densidad)')
    chk(pg.evaluate("T3.H.filter(h=>h.k==null).length") == 6, 'v1.41.0: se pueden tocar los 6 tanques')
    s0 = pg.evaluate("T3.s")
    tap(pg, 'T3'); pg.wait_for_timeout(900)
    chk(pg.evaluate("T3.zoom&&TQSEL==='T3'") and pg.evaluate("T3.s") > s0 * 1.5, 'tocar T3 acerca la cámara')
    chk(pg.get_attribute('.tqm[data-tq=T3]', 'aria-pressed') == 'true' and 'Tanque 3' in pg.inner_text('.tqd .tqc'), 'y elige T3 en el tablero de abajo (mismo detalle)')
    chk(pg.locator('.t3lab .t3tag:not(.t3hid)').count() == 0, 'de cerca no salen los letreros de los tanques')
    tap(pg, 'T3', 0); pg.wait_for_timeout(300)
    pk = pg.inner_text('.t3pick') if pg.locator('.t3pick').count() else ''
    chk('Tina 61' in pk and 'T3' in pk and '34 kg' in pk and 'Chica' in pk and 'WLRCO211026' in pk and '12 días en tanque' in pk and 'aguanta 10' in pk, f'tocar una tina: número, tanque, kg, talla, lote y días ({pk!r})')
    chk(cr(pg, 'T3', 'hl') == 13, 'se marcan las 13 tinas de ese lote')
    pg.click('.t3pick [data-t3a=unpick]'); pg.wait_for_timeout(150)
    chk(pg.locator('.t3pick').count() == 0 and cr(pg, 'T3', 'hl') == 0 and cr(pg, 'T3') == 13, 'cerrar la tarjeta quita la marca')
    tap(pg, 'T3', 0); pg.wait_for_timeout(200)
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
    chk(pg.evaluate("T3.H.filter(h=>h.k==null).length") == 6, 'al girar se vuelve a dibujar todo (se siguen pudiendo tocar los 6 tanques)')
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
    n3 = cr(pg, 'T3')
    chk(n3 == 15, f'T3 junta PROPESA (13) y Abel (2): {n3}')
    cols = pg.evaluate("T3.M.O.find(o=>o.tk==='T3'&&o.C).C.filter(c=>c.o).map(c=>c.o.col.toUpperCase())")
    chk(cols.count('#7242F5') == 2, 'las tinas de Abel llevan su Jumbo morado')
    tag = pg.evaluate("[...document.querySelectorAll('.t3tag')].map(e=>e.textContent).find(t=>t.startsWith('T3'))") or ''
    chk('T3 · 15 tinas' in tag and '493 kg' in tag, f'el letrero de T3 suma las dos maquilas ({tag})')
    tap(pg, 'T3'); pg.wait_for_timeout(900)
    tap(pg, 'T3', 14); pg.wait_for_timeout(200)
    pk = pg.inner_text('.t3pick') if pg.locator('.t3pick').count() else ''
    chk('Tina 75' in pk and 'Abel' in pk and 'WLRCO011126' in pk, f'en Panel general la tina dice su maquila ({pk!r})')
    chk(cr(pg, 'T3', 'hl') == 2, 'con el lote de Abel elegido se marcan sus 2 tinas')
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
