"""v1.35.0 · Pantallas de detalle reorganizadas (pedido del usuario, 5/nov/2026, con /impeccable layout:
«hay demasiados campos y no se sabe por dónde empezar; está difícil encontrar las cosas»). Aprobó: Orden, Embarque, Administración y Lote.
1. Orden: PDF, correo y «Eliminar orden» en el encabezado (una sola vez); consignatarios antes de la hoja; la Hoja de empaque
   plegada con «Faltan N datos» (abierta sola cuando ya están todas las hieleras); el aviso rojo la abre.
2. Embarque: PDF en el encabezado; primero hieleras y tallas, luego órdenes; peso e indicaciones plegados (total a la vista).
3. Administración en pestañas: Usuarios · Catálogos · Informes y respaldo (con teclado: flechas). v1.40.0: sin Maquilas.
4. Lote: el conteo final sube; la temperatura del tanque se pliega.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v135_t.py"""
from playwright.sync_api import sync_playwright
import os
BASE = 'http://localhost:8765/index.html?modo=local'
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em='admin@propesa.mx'):
    pg.goto(BASE); pg.evaluate('([s])=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0");localStorage.setItem("propesa-inst",String(Date.now()))}', [seed]); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(250)
def ir(pg, r): pg.evaluate(f"go('{r}')"); pg.wait_for_timeout(200)
def abierto(pg, f): return pg.evaluate(f"(document.querySelector('[data-fold=\"{f}\"]')||{{}}).open===true")
def antes(pg, a, b): return pg.evaluate(f"(()=>{{const x=document.querySelector('{a}'),y=document.querySelector('{b}');return !!x&&!!y&&(x.compareDocumentPosition(y)&4)>0}})()")
def alto(pg): return pg.evaluate("document.querySelector('main').scrollHeight")
with sync_playwright() as p:
    b = p.chromium.launch()
    for W, H in [(1440, 900), (1180, 820), (820, 1180), (390, 844)]:
        pg = b.new_page(viewport={'width': W, 'height': H}); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg)
        # ---------- 1. Orden ----------
        ir(pg, 'orden:1')
        chk(pg.locator('.ordhd [data-pdf^="dl:ord"]').count() == 1 and pg.locator('.ordhd .pdfb .btn:not(.q)').count() == 0, f'{W} orden: PDF y correo en el encabezado, discretos')
        chk(pg.locator('[data-oa=dco]').count() == 1 and pg.locator('.ordhd [data-oa=dco]').count() == 1, f'{W} orden: «Eliminar orden» una sola vez, arriba')
        chk(pg.locator('main .pdfb').count() == 1, f'{W} orden: no hay otra fila de PDF a media pantalla')
        chk(antes(pg, '.cd .shp', '[data-fold="f6:1"]') and antes(pg, '[data-fold="f6:1"]', '#f6card') , f'{W} orden: los consignatarios van antes de la hoja de empaque')
        chk('Faltan 8 datos' in pg.inner_text('[data-fold="f6:1"] summary'), f'{W} orden: el plegable de la hoja dice cuántos datos faltan')
        chk(abierto(pg, 'f6:1'), f'{W} orden completa con datos faltantes: la hoja se abre sola (es lo que toca)')
        pg.click('[data-fold="f6:1"] summary'); pg.wait_for_timeout(100); chk(not abierto(pg, 'f6:1'), f'{W} orden: un toque la cierra')
        pg.click('.ordhd [data-jump^="#f6_"]'); pg.wait_for_timeout(500)
        chk(abierto(pg, 'f6:1') and pg.evaluate("document.activeElement&&document.activeElement.id.startsWith('f6_')"), f'{W} orden: el aviso rojo abre la hoja y lleva al dato que falta')
        pg.click('.ordhd [data-oa=dco]'); pg.wait_for_timeout(150)
        chk(pg.locator('.ordhd #ord_del [data-oa=dlo]').is_visible(), f'{W} orden: la confirmación de eliminar sale en el encabezado')
        pg.click('#ord_del [data-oa=no]'); pg.wait_for_timeout(100); chk(pg.locator('#ord_del').count() == 0, f'{W} orden: «No» la quita')
        # orden a medias: la hoja empieza cerrada
        pg.evaluate("(()=>{const o=ST.OR.find(x=>x.id==1);o.lines[0].boxes+=2;save()})()"); ir(pg, 'orden:2'); ir(pg, 'orden:1')
        pg.evaluate("delete FOLD['f6:1']"); pg.evaluate('render()'); pg.wait_for_timeout(100)
        chk(not abierto(pg, 'f6:1'), f'{W} orden a medias: la hoja empieza cerrada (primero se empaca)')
        pg.evaluate("(()=>{const o=ST.OR.find(x=>x.id==1);o.lines[0].boxes-=2;save()})()")
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{W} orden: sin scroll de lado')
        # ---------- 2. Embarque ----------
        ir(pg, 'emb:0')
        chk(pg.locator('main .cd.head [data-pdf^="dl:emb"]').count() == 1 and 'Informe de este embarque' not in pg.inner_text('main'), f'{W} embarque: PDF en el encabezado')
        chk(antes(pg, '#emb_tallas', '#ordship'), f'{W} embarque: hieleras y tallas antes que las órdenes')
        u = pg.evaluate('ST.P[0].u')
        chk(not abierto(pg, f'emb-peso:{u}') and '137.2 kg' in pg.inner_text(f'[data-fold="emb-peso:{u}"] summary'), f'{W} embarque: peso plegado con el total a la vista')
        chk(not abierto(pg, f'emb-obs:{u}') and 'Ninguna' in pg.inner_text(f'[data-fold="emb-obs:{u}"] summary'), f'{W} embarque: indicaciones plegadas')
        chk('faltan 8 datos' in pg.inner_text('.alb') and 'hora inicial, hora final' not in pg.inner_text('.alb'), f'{W} embarque: el aviso de la hoja es un renglón corto')
        pg.click(f'[data-fold="emb-obs:{u}"] summary'); pg.fill('#emb_obs', 'Echar 2 tarimas'); pg.click('[data-obs]'); pg.wait_for_timeout(150)
        chk('ECHAR 2 TARIMAS' in pg.inner_text(f'[data-fold="emb-obs:{u}"] summary').upper() and pg.locator('.obsb').count() >= 1, f'{W} embarque: al guardar, el resumen dice la indicación y sale el letrero')
        pg.click('.alk:has-text("Hoja de empaque del 12/10")'); pg.wait_for_timeout(400)
        chk(pg.evaluate('V.v') == 'orden' and abierto(pg, 'f6:1'), f'{W} embarque: «Resolver» de la hoja abre la orden con la hoja abierta')
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{W} embarque: sin scroll de lado')
        # ---------- 3. Administración ----------
        ir(pg, 'admin:usr')
        chk(pg.locator('[role=tablist] [role=tab]').count() == 3 and pg.locator('[role=tab][aria-selected=true]').inner_text() == 'Usuarios', f'{W} admin: 3 pestañas, Usuarios abierta')
        chk(pg.locator('[data-a=nu]').count() == 1 and pg.locator('#szs').count() == 0 and pg.locator('[data-bk=up]').count() == 0, f'{W} admin: en Usuarios no salen catálogos ni respaldo')
        pg.click('[data-adt=cat]'); pg.wait_for_timeout(100)
        chk(all(pg.locator(s).count() == 1 for s in ['#szs', '#provs', '#esps', '#conss']) and pg.locator('[data-a=nu]').count() == 0, f'{W} admin: Catálogos tiene tallas, proveedores, especies y consignatarios')
        chk(pg.locator('#adp .btn:not(.s):not(.q):not(.d):not(.dq)').count() == 0, f'{W} admin: en Catálogos los «+ Nuevo…» no compiten en azul')
        pg.evaluate('render()'); chk(pg.locator('[role=tab][aria-selected=true]').inner_text() == 'Catálogos', f'{W} admin: la pestaña se queda al redibujar')
        pg.focus('[role=tab][aria-selected=true]'); pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(100)
        chk(pg.evaluate("document.activeElement.dataset.adt") == 'dat' and pg.locator('[data-bk=up]').count() >= 1 and 'Informes de cierre' in pg.inner_text('#adp'), f'{W} admin: con flechas pasa a Informes y respaldo')
        chk(pg.locator('[data-adt=mq]').count() == 0, f'{W} admin: sin pestaña Maquilas (v1.40.0)')
        pg.click('[data-avatar]'); pg.click('[data-pm=users]'); pg.wait_for_timeout(150)
        chk(pg.locator('[role=tab][aria-selected=true]').inner_text() == 'Usuarios', f'{W} admin: el círculo del perfil abre Usuarios')
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{W} admin: sin scroll de lado')
        # ---------- 4. Lote ----------
        ir(pg, 'lote:WLRCO051026A')
        chk(antes(pg, '#lot_fin', '.g2') and pg.locator('[data-fin]').is_visible(), f'{W} lote: el conteo final va arriba, a la vista')
        f = 'lot-tmp:WLRCO051026A'
        chk(not abierto(pg, f) and '2 lecturas' in pg.inner_text(f'[data-fold="{f}"] summary'), f'{W} lote: temperatura plegada, dice cuántas lecturas hay')
        pg.click(f'[data-fold="{f}"] summary'); pg.wait_for_timeout(100); chk(abierto(pg, f) and pg.locator(f'[data-fold="{f}"] table').is_visible(), f'{W} lote: un toque abre la temperatura')
        pg.close()
    # tema oscuro y texto «Muy grande»: sin desbordes en las 4 pantallas
    for W in [390, 820]:
        pg = b.new_page(viewport={'width': W, 'height': 900}, color_scheme='dark'); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg)
        pg.evaluate("document.documentElement.style.setProperty('--app-font-size','20px')")
        for r in ['orden:1', 'emb:0', 'admin:usr', 'admin:cat', 'admin:dat', 'lote:WLRCO051026A']:
            ir(pg, r); chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{W} oscuro + texto grande {r}: sin scroll de lado')
        pg.close()
    b.close()
chk(not errs, f'sin errores de JavaScript {errs[:2]}')
print('TODO BIEN' if not fails else f'{len(fails)} FALLAS')
