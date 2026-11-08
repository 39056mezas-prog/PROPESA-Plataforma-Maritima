"""v1.33.0 (pedidos del usuario, 5/nov/2026).
1. Las tallas (851-1220 g) no se vuelven teléfono en iOS: format-detection.
2. La vista completa abre en «Formatos» (desde la v1.39.0, el Centro de operaciones; las secciones están en el menú) (herramienta, sin orden fijo), solo con lo que el rol puede llenar; menú sin números ni «Siguiente paso».
3. iPad: «Instalar app» en el menú del perfil dice los pasos (Compartir → Agregar a inicio).
4. iPad: en Empaque el teclado va a un lado de las hieleras (horizontal y vertical); cada toque cuenta una vez; corregir una hielera
   completada abre el teclado aunque se haya cerrado; embarque cerrado → se reabre con confirmación.
5. Entrada: «Editar» y «Eliminar» en cada fila.  6. Packing list con peso bruto.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v133_t.py"""
from playwright.sync_api import sync_playwright
import os
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
IPAD = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15'
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em='admin@propesa.mx', kp='1'):
    pg.goto(BASE); pg.evaluate('([s,k])=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0");localStorage.setItem("propesa-kp",k);localStorage.setItem("propesa-inst",String(Date.now()))}', [seed, kp]); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(250)
NUEVA = "n=>{const o={id:uidN(),etd:dLoc(),lines:[{id:1,city:'HKG',cons:0,boxes:n,kp:16,tar:0,cc:0}],sh:{}};ST.OR.push(o);syncShip(o,'HKG',0);save();return o.id}"
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------- 1 y 2: tallas, Formatos ----------
    for vw, em in [((1440, 900), 'admin@propesa.mx'), ((390, 844), 'admin@propesa.mx'), ((1180, 820), 'piso@propesa.mx')]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, em)
        if em.startswith('piso'): pg.evaluate("setPiso(false);go(home0())"); pg.wait_for_timeout(150)
        tag = f'{vw[0]} {em[:4]}'
        chk('telephone=no' in (pg.get_attribute('meta[name=format-detection]', 'content') or ''), f'{tag}: sin detección de teléfonos (851-1220 g no es un número para marcar)')
        chk(pg.evaluate('V.v') == 'inicio', f'{tag}: abre en el Centro de operaciones (v1.39.0) ({pg.evaluate("V.v")})')
        t = pg.locator('.sb .fs b').all_inner_texts()
        chk('Entrada' in t and 'Empaque' in t and 'Hojas para imprimir' in t and pg.locator('main .ctl, main .fmg').count() == 0, f'{tag}: cada sección está en el menú, sin cuadrícula repetida en el Centro {t}')
        chk(pg.locator('.sb .fs i em').count() == 0 and 'Siguiente paso' not in pg.inner_text('#app'), f'{tag}: menú sin números ni «Siguiente paso»')
        pg.evaluate("document.querySelector('.sb [data-go=empaque]').click()"); pg.wait_for_timeout(150); chk(pg.evaluate('V.v') == 'empaque', f'{tag}: un formato abre directo')
        chk('Paso 3 de 4' not in pg.inner_text('#app'), f'{tag}: Empaque ya no dice «Paso 3 de 4»')
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{tag}: sin scroll de lado')
        pg.close()
    # ---------- 3: instalar en iPad ----------
    ctx = b.new_context(viewport={'width': 1080, 'height': 810}, has_touch=True, is_mobile=True, user_agent=IPAD)
    ctx.add_init_script("Object.defineProperty(navigator,'platform',{get:()=>'MacIntel'});Object.defineProperty(navigator,'maxTouchPoints',{get:()=>5})")  # iPadOS se presenta como Mac con pantalla táctil
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg)
    pg.click('[data-avatar]'); chk(pg.locator('#pmenu [data-pm=inst]').count() == 1, 'iPad: el menú del perfil trae «Instalar app»')
    pg.click('#pmenu [data-pm=inst]'); pg.wait_for_timeout(100); tx = pg.inner_text('#inst') if pg.locator('#inst').count() else ''
    chk('Compartir' in tx and 'Agregar a inicio' in tx and 'arriba a la derecha' in tx, 'iPad: tocarlo dice los pasos y dónde está Compartir')
    pg.click('[data-inst=no]'); chk(pg.locator('#inst').count() == 0, 'iPad: «Entendido» la cierra')
    # ---------- 4: Empaque en iPad ----------
    for W, H in [(1080, 810), (810, 1080)]:
        pg.set_viewport_size({'width': W, 'height': H})
        oid = pg.evaluate(NUEVA, 6); O = f"ST.OR.find(o=>o.id=={oid})"; BX = f"ordPk({O},{O}.lines[0]).map(x=>x.b.c+x.b.k).join(',')"
        pg.evaluate(f"go('empacar:{oid}.1')"); pg.evaluate("PKD.lot=openLots()[0];render()"); pg.wait_for_timeout(300)
        k = pg.evaluate("(()=>{const a=document.getElementById('kpad').getBoundingClientRect(),g=document.querySelector('.pktw').getBoundingClientRect();return{side:a.left>=g.right-1,gw:g.width}})()")
        chk(k['side'] and k['gw'] > 240, f'iPad {W}×{H}: el teclado va a un lado y las hieleras se ven ({k})')
        for d in '27': pg.tap(f'.kpk [data-kp="d:{d}"]')
        chk(pg.evaluate("document.getElementById('kpv').textContent") == '27', f'iPad {W}×{H}: cada toque escribe una sola vez')
        pg.tap('.kpc [data-kp="k:R"]'); pg.wait_for_timeout(150)
        chk(pg.evaluate(BX) == '27R', f'iPad {W}×{H}: la categoría guarda la hielera ({pg.evaluate(BX)})')
        r = pg.evaluate("(()=>{const e=document.querySelector('#app .kpon'),m=document.querySelector('main').getBoundingClientRect(),r=e.getBoundingClientRect();return r.top>=m.top-1&&r.bottom<=m.bottom+1})()")
        chk(r, f'iPad {W}×{H}: la siguiente hielera queda a la vista')
        # teclado cerrado con ✕ → tocar una completada lo vuelve a abrir
        pg.tap('.kpclose'); pg.wait_for_timeout(150); chk(pg.locator('#kpad').count() == 0, f'iPad {W}×{H}: ✕ cierra el teclado')
        pg.locator('.pkdn.is-done').first.tap(); pg.wait_for_timeout(200)
        chk(pg.locator('#kpad').count() == 1 and pg.evaluate("KPT.t") == 'ed', f'iPad {W}×{H}: tocar una hielera completada abre el teclado para corregirla')
        pg.tap('.kpk [data-kp="d:3"]'); pg.tap('.kpk [data-kp="d:0"]'); pg.tap('.kpc [data-kp="k:V"]'); pg.wait_for_timeout(150)
        chk(pg.evaluate(BX) == '30V', f'iPad {W}×{H}: se corrige con el teclado ({pg.evaluate(BX)})')
    # embarque cerrado → reabrir con confirmación
    pg.evaluate(f"ST.P[{O}.sh['HKG|0']].closed=true;save();render()"); pg.wait_for_timeout(150)
    chk(pg.locator('.pkdn.is-done').count() == 0 and pg.locator('[data-reop]').count() == 1, 'embarque cerrado: las hieleras quedan fijas y sale «Reabrir para corregir»')
    pg.once('dialog', lambda d: d.dismiss()); pg.tap('[data-reop]'); pg.wait_for_timeout(150)
    chk(pg.evaluate(f"ST.P[{O}.sh['HKG|0']].closed"), 'embarque cerrado: «Cancelar» no cambia nada')
    pg.once('dialog', lambda d: d.accept()); pg.tap('[data-reop]'); pg.wait_for_timeout(150)
    chk(not pg.evaluate(f"ST.P[{O}.sh['HKG|0']].closed") and pg.locator('.pkdn.is-done').count() >= 1, 'embarque cerrado: «Aceptar» lo reabre y las hieleras se pueden tocar otra vez')
    # ---------- 6: packing list con peso bruto ----------
    sv = pg.evaluate(f"async()=>{{PDFSVG=[];try{{await pdfMake('emp',{oid});return PDFSVG.map(p=>p.sv.join('')).join('')}}finally{{PDFSVG=null}}}}")
    g = pg.evaluate(f"ordG({O}).toFixed(1)")
    chk('PESO BRUTO' in sv.upper() and g in sv, f'packing list: trae el peso bruto ({g} kg)')
    pg.evaluate(f"go('orden:{oid}')"); chk('kg de peso bruto' in pg.inner_text('#app'), 'la orden: el packing list dice el peso bruto')
    ctx.close()
    # ---------- 5: Entrada con Editar y Eliminar a la vista ----------
    pg = b.new_page(viewport={'width': 1440, 'height': 900}); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg)
    pg.evaluate("go('recepcion')"); n = pg.locator('[data-led^="el:"]').count()
    chk(n >= 1 and pg.locator('[data-led^="dl:"]').count() == n, f'Entrada: cada fila trae Editar y Eliminar ({n})')
    lot = pg.get_attribute('[data-led^="el:"] >> nth=0', 'data-led')[3:]
    pg.click('[data-led^="el:"] >> nth=0'); pg.wait_for_timeout(150)
    chk(pg.evaluate("V.v+':'+V.id") == 'lote:' + lot and pg.evaluate("form&&form.edit") == lot and pg.locator('#fo').count() == 1, 'Editar abre el lote con su formulario')
    pg.evaluate("go('recepcion')"); pg.click('[data-led^="dl:"] >> nth=0'); pg.wait_for_timeout(150)
    chk(pg.locator('[data-a=dl2]').count() == 1, 'Eliminar abre el lote con «Sí, eliminar lote» a la vista')
    pg.close()
    b.close()
chk(not errs, f'sin errores de JavaScript {errs[:3]}')
print('\n' + ('TODO BIEN' if not fails else f'{len(fails)} FALLAS')); raise SystemExit(1 if fails else 0)
