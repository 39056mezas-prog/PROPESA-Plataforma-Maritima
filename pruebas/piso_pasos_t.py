"""v1.21.0 · Lotes por envío y paso a paso en Modo piso (respuestas del usuario, 26/oct/2026).
- Pregunta 6: cada envío dice cuánto lleva de cada lote (hieleras, langostas, kg de producto, tallas), en la pantalla, en el PDF y en el informe por correo.
- Pregunta 15: en Modo piso, «Cerrar embarque» (3 pasos: hieleras, pendientes, cerrar) y «Conteo final» (2 pasos: kg, confirmar) van paso a paso.
  El piso revisa pero no cierra (solo el Administrador). La hoja de empaque incompleta solo pregunta (pregunta 9). El conteo no acepta más de lo esperado.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/piso_pasos_t.py"""
import os
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Luis Piso',email:'piso@propesa.mx',role:'piso',notify:false}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
A, B_ = 'WLRCO261026', 'WLRCO251026'
def login(pg, em):
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")
def lot(pg, code, kg, d):
    pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.fill('#fl', code); pg.select_option('#fo', '1'); pg.fill('#fd', d); pg.fill('#fkb', '36'); pg.fill('#ftt', '58'); pg.fill('#ftp', '59'); pg.fill('#fdes', '0'); pg.fill('#fk0', kg); pg.click('[data-a=sv]'); pg.wait_for_timeout(150)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    dlg = []; pg.on('dialog', lambda d: (dlg.append(d.message), d.accept()))
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1)")
    lot(pg, A, '200', '26/10/2026'); lot(pg, B_, '150', '25/10/2026')
    chk(pg.evaluate("ST.R.length") == 2, 'dos lotes capturados')
    pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '26/10/2026'); pg.click('[data-oa=new]'); pg.select_option('#ol_city', 'PVG'); pg.fill('#ol_z0', '3'); pg.fill('#ol_tar', '0'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(150)
    pg.evaluate("go('empaque')"); pg.locator('[data-go^="empacar:"]').first.click(); pg.wait_for_timeout(100)
    pg.click(f'[data-pk="lot:{A}"]'); pg.wait_for_timeout(80)
    for _ in range(2): pg.fill('#pk_c0', '28'); pg.click('#pkr0 [data-pk="k:0:B"]'); pg.wait_for_timeout(100)
    pg.click(f'[data-pk="lot:{B_}"]'); pg.wait_for_timeout(80); pg.fill('#pk_c0', '30'); pg.click('#pkr0 [data-pk="k:0:B"]'); pg.wait_for_timeout(100)
    sl = pg.evaluate("shipByLot(0).map(x=>[x.l,x.h,x.c,x.g])")
    chk(len(sl) == 2 and sl[0][0] == B_ and sl[0][1:3] == [1, 30] and sl[1][0] == A and sl[1][1:3] == [2, 56], f'el envío sabe cuánto lleva de cada lote ({sl})')
    # --- pregunta 6: pantalla del embarque y PDF ---
    pg.evaluate("go('emb:0')"); pg.wait_for_timeout(100)
    t = pg.inner_text('#emb_lotes')
    chk(A in t and B_ in t and 'Total' in t and '86' in t, 'el embarque muestra la tabla «Por lote» con su total')
    pg.click(f'#emb_lotes [data-go="lote:{A}"]'); pg.wait_for_timeout(100); chk(pg.evaluate("V.v=='lote'&&V.id") == A, 'el lote de la tabla lleva a su lote')
    r = pg.evaluate("(async()=>{try{const d=await pdfMake('emb',0);return !!d&&d.u8.length>1000}catch(e){return String(e)}})()")
    chk(r is True, f'PDF del embarque con «Por lote» ({r})')
    # --- pregunta 15: Cerrar embarque paso a paso (el piso revisa pero no cierra) ---
    pg.evaluate("me=null;render()"); login(pg, 'piso@propesa.mx'); pg.wait_for_timeout(300)
    chk(pg.locator('.pt[data-go=pcer]').count() == 1 and pg.locator('.pt[data-go=pcon]').count() == 1, 'Inicio de Modo piso: «Cerrar embarque» y «Conteo final» abren su paso a paso')
    pg.click('.pt[data-go=pcer]'); pg.wait_for_timeout(100)
    chk(pg.locator('.pt[data-go^="pcer:"]').count() == 1, 'paso a paso: primero se elige el embarque')
    pg.click('.pt[data-go^="pcer:"]'); pg.wait_for_timeout(100)
    m = pg.inner_text('main'); chk('Paso 1 de 3' in m and 'Revisa las hieleras' in m and A in m and B_ in m and '3 de 3' in m, 'paso 1: hieleras empacadas, langostas, peso y cuánto va de cada lote')
    pg.click('[data-pce="2"]'); pg.wait_for_timeout(100); m = pg.inner_text('main')
    chk('Paso 2 de 3' in m and ('Todo cuadra' in m or 'pendiente' in m) and 'hoja de empaque' in m.lower(), 'paso 2: pendientes y aviso de hoja de empaque incompleta')
    pg.click('[data-pce="3"]'); pg.wait_for_timeout(100); m = pg.inner_text('main')
    chk('Avísale' in m and 'Administrador' in m and pg.locator('[data-pce=cerrar]').count() == 0, 'paso 3 con el piso: «Avísale al Administrador», no puede cerrar')
    pg.click('[data-pce="2"]'); pg.wait_for_timeout(80); chk('Paso 2 de 3' in pg.inner_text('main'), '«Atrás» regresa al paso anterior')
    for w_, h_ in [(1180, 820), (820, 1180), (390, 844)]:
        pg.set_viewport_size({'width': w_, 'height': h_})
        for s_ in ['1', '2', '3']:
            pg.evaluate(f"PCE.s={s_};render()"); pg.wait_for_timeout(60); chk(not overflow(pg), f'Cerrar embarque paso {s_} sin scroll de lado en {w_} px')
        if w_ == 390:
            pg.evaluate("PREF.fs=20;applyPrefs();render()")
            for s_ in ['1', '2', '3']:
                pg.evaluate(f"PCE.s={s_};render()"); pg.wait_for_timeout(60); chk(not overflow(pg), f'Cerrar embarque paso {s_} con texto «Muy grande» (20 px) sin scroll de lado en 390 px')
            pg.evaluate("PREF.fs=FS_DEF;applyPrefs();render()")
        hs = pg.evaluate("[...document.querySelectorAll('.pnav .pbtn')].map(x=>x.getBoundingClientRect().height)")
        chk(hs and min(hs) >= 56, f'botones de los pasos de 56 px o más en {w_} px ({hs})')
    pg.set_viewport_size({'width': 1440, 'height': 900})
    # --- el Administrador cierra desde el paso a paso ---
    pg.evaluate("me=null;render()"); login(pg, 'admin@propesa.mx'); pg.wait_for_timeout(200)
    if pg.locator('.pt[data-go=pcer]').count() == 0: pg.click('[data-mode=piso]'); pg.wait_for_timeout(900)
    pg.click('.pt[data-go=pcer]'); pg.wait_for_timeout(80); pg.click('.pt[data-go^="pcer:"]'); pg.wait_for_timeout(80)
    pg.click('[data-pce="2"]'); pg.click('[data-pce="3"]'); pg.wait_for_timeout(80)
    chk(pg.locator('[data-pce=cerrar]').count() == 1, 'paso 3 con el Administrador: botón «Cerrar embarque»')
    dlg.clear(); pg.click('[data-pce=cerrar]'); pg.wait_for_timeout(200)
    chk(pg.evaluate("ST.P[0].closed") and 'Embarque cerrado' in pg.inner_text('main'), 'se cierra y queda la pantalla «✔ Embarque cerrado»')
    chk(any('hoja de empaque' in d for d in dlg), 'la hoja de empaque incompleta solo pregunta (pregunta 9)')
    body = pg.evaluate("ST.O[0].body"); chk(f'{A}: 2 hieleras · 56 langostas' in body and f'{B_}: 1 hielera · 30 langostas' in body, 'el informe por correo trae cuánto va de cada lote')
    chk(pg.evaluate("ST.L.filter(m=>m.type=='SALIDA_EMBARQUE').length") == 2, 'al cerrar salieron del tanque los dos lotes')
    pg.click('[data-go=piso]'); pg.wait_for_timeout(80); pg.click('.pt[data-go=pcer]'); pg.wait_for_timeout(80)
    chk('Sin embarques por cerrar' in pg.inner_text('main'), 'sin embarques abiertos: mensaje claro con botón a Inicio')
    # --- Conteo final paso a paso ---
    pg.click('[data-go=piso]'); pg.wait_for_timeout(80); pg.click('.pt[data-go=pcon]'); pg.wait_for_timeout(80)
    chk(pg.locator('.pt[data-go^="pcon:"]').count() == 2, 'Conteo final: primero se elige el lote (los dos por contar)')
    chk(pg.evaluate("getComputedStyle(document.querySelector('.pt .cli')).backgroundImage") == 'none', 'el código del lote en la tarjeta se ve limpio (sin el fondo de la pantalla de compradores)')
    ex = pg.evaluate(f"bal('{A}')/1000")
    pg.click(f'.pt[data-go="pcon:{A}"]'); pg.wait_for_timeout(80); m = pg.inner_text('main')
    chk('Paso 1 de 2' in m and '¿Cuántos kg quedan?' in m and 'Esperado' in m, f'paso 1: kg contados con lo esperado a la vista ({ex} kg)')
    hi = pg.evaluate("document.getElementById('pco_kg').getBoundingClientRect().height"); chk(hi >= 60, f'la casilla de kg mide 60 px o más ({hi})')
    pg.click('[data-pco="2"]'); pg.wait_for_timeout(80); chk('Escribe los kg' in pg.inner_text('#pco_er'), 'sin kg no avanza y dice qué falta')
    pg.fill('#pco_kg', str(ex + 5)); pg.click('[data-pco="2"]'); pg.wait_for_timeout(80)
    chk('no puede ser mayor' in pg.inner_text('#pco_er') and pg.input_value('#pco_kg') == str(ex + 5) and pg.get_attribute('#pco_kg', 'aria-invalid') == 'true', 'más de lo esperado: no avanza, conserva lo escrito y lo marca')
    pg.fill('#pco_kg', '140'); pg.press('#pco_kg', 'Enter'); pg.wait_for_timeout(100); m = pg.inner_text('main')
    chk('Paso 2 de 2' in m and 'Mortalidad' in m and pg.evaluate(f"R_('{A}').final") is None, 'Enter pasa a confirmar; todavía no guarda')
    pg.click('[data-pco="1"]'); pg.wait_for_timeout(80); chk(pg.input_value('#pco_kg') == '140', '«Atrás» conserva los kg')
    pg.click('[data-pco="2"]'); pg.wait_for_timeout(80); pg.click('[data-pco=guardar]'); pg.wait_for_timeout(120)
    c = pg.evaluate(f"calc('{A}')"); chk(pg.evaluate(f"R_('{A}').final") == 140 and 'Conteo guardado' in pg.inner_text('main') and c and f"{c['p']:.2f}%" in pg.inner_text('main'), 'guarda el conteo y muestra la mortalidad del lote')
    chk(pg.locator(f'[data-a=cl][data-lot="{A}"]').count() == 1, 'el Administrador puede cerrar el lote desde ahí')
    pg.click('[data-go=pcon]'); pg.wait_for_timeout(80); chk(pg.locator('.pt[data-go^="pcon:"]').count() == 1, 'el lote contado ya no sale en la lista')
    for w_, h_ in [(1180, 820), (820, 1180), (390, 844)]:
        pg.set_viewport_size({'width': w_, 'height': h_})
        for r_ in ['pcon', f'pcon:{B_}']:
            pg.evaluate(f"go('{r_}')"); pg.wait_for_timeout(80); chk(not overflow(pg), f'{r_} sin scroll de lado en {w_} px')
        pg.fill('#pco_kg', '100'); pg.click('[data-pco="2"]'); pg.wait_for_timeout(80); chk(not overflow(pg), f'confirmar conteo sin scroll de lado en {w_} px')
    pg.evaluate("PREF.fs=20;applyPrefs();render()")
    for r_ in ['pcon', f'pcon:{B_}']:
        pg.evaluate(f"go('{r_}')"); pg.wait_for_timeout(80); chk(not overflow(pg), f'{r_} con texto «Muy grande» (20 px) sin scroll de lado en 390 px')
    pg.fill('#pco_kg', '100'); pg.click('[data-pco="2"]'); pg.wait_for_timeout(80); chk(not overflow(pg), 'confirmar conteo con texto «Muy grande» sin scroll de lado en 390 px')
    pg.evaluate("PREF.fs=FS_DEF;applyPrefs();render()")
    pg.set_viewport_size({'width': 1440, 'height': 900})
    # --- cambiar de modo se queda en la misma cosa ---
    pg.evaluate(f"go('pcon:{B_}')"); pg.wait_for_timeout(80); pg.click('[data-mode=full]'); pg.wait_for_timeout(900)
    chk(pg.evaluate("V.v+':'+V.id") == f'lote:{B_}', 'apagar Modo piso en el conteo de un lote lleva a ese lote')
    pg.evaluate("go('cierre')"); pg.click('[data-mode=piso]'); pg.wait_for_timeout(900); chk(pg.evaluate("V.v") == 'pcon', 'prender Modo piso en Mortalidad final lleva al Conteo final paso a paso')
    pg.evaluate("go('pcer:noexiste')"); pg.wait_for_timeout(80); chk(pg.evaluate("V.v") == 'pcer' and 'Sin embarques por cerrar' in pg.inner_text('main'), 'un embarque que ya no existe regresa a la lista')
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
