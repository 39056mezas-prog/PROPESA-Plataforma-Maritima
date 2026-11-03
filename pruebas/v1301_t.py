"""v1.30.1 (pedidos del usuario, 2/nov/2026).
1. Corregir una hielera ya guardada con el teclado: letra del color + Enter guarda el color nuevo (antes la vista completa la dejaba igual).
   Vista completa y Modo piso; con y sin cambiar las piezas.
2. Hojas para imprimir: vista previa de la primera página de cada hoja (la dibuja el mismo código del PDF); tocarla la agranda.
3. Paquete de cada orden: un .zip con la orden, el packing list, el informe de cada embarque y el plan de carga.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v1301_t.py"""
from playwright.sync_api import sync_playwright
import os, io, zipfile
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, piso):
    pg.goto(BASE); pg.evaluate('([s,p])=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso",p);localStorage.setItem("propesa-kp","1")}', [seed, piso]); pg.reload()
    pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
NUEVA = "()=>{const o={id:uidN(),etd:dLoc(),lines:[{id:1,city:'HKG',cons:0,boxes:3,kp:16,tar:0,cc:0}],sh:{}};ST.OR.push(o);syncShip(o,'HKG',0);save();return o.id}"
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------- 1. corregir con el teclado ----------
    for piso in ['0', '1']:
        tag = 'piso' if piso == '1' else 'completa'
        pg = b.new_page(viewport={'width': 1280, 'height': 900}); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, piso)
        oid = pg.evaluate(NUEVA); O = f"ST.OR.find(o=>o.id=={oid})"; BX = f"JSON.stringify(ordPk({O},{O}.lines[0]).map(x=>[x.b.c,x.b.k]))"
        if piso == '1': pg.evaluate(f"PE.lot=openLots()[0];go('pemp:{oid}.1')")
        else: pg.evaluate(f"go('empacar:{oid}.1')"); pg.evaluate("PKD.lot=openLots()[0];render()")
        pg.wait_for_timeout(300); pg.click('[data-kps="1"]' if piso == '1' else '#pk_c0'); pg.wait_for_timeout(300)
        for n, l in [('25', 'r'), ('30', 'r')]:
            pg.keyboard.type(n); pg.keyboard.press(l); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
        chk(pg.evaluate(BX) == '[[25,"R"],[30,"R"]]', f'{tag}: dos hieleras guardadas en Rojo')
        abre = lambda no: pg.click(f'[data-kps="{no}"]') if piso == '1' else pg.locator(f'[data-pk="ed:{pg.evaluate(f"ordPk({O},{O}.lines[0])[{no - 1}].b.seq")}"]').first.click()
        # solo la letra + Enter (sin volver a escribir las piezas)
        abre(1); pg.wait_for_timeout(200); pg.keyboard.press('v'); pg.wait_for_timeout(60)
        chk(pg.evaluate("kpCat()") == 'V', f'{tag}: la letra elige Verde en la hielera guardada')
        pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
        chk(pg.evaluate(BX) == '[[25,"V"],[30,"R"]]', f'{tag}: Enter guarda la hielera 1 como Verde: {pg.evaluate(BX)}')
        # piezas nuevas + letra + Enter
        abre(2); pg.wait_for_timeout(200); pg.keyboard.type('20'); pg.keyboard.press('a'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
        chk(pg.evaluate(BX) == '[[25,"V"],[20,"A"]]', f'{tag}: con piezas nuevas también: {pg.evaluate(BX)}')
        chk(pg.evaluate(f"ordPk({O},{O}.lines[0]).length") == 2, f'{tag}: corregir no crea otra hielera')
        pg.close()
    # ---------- 2 y 3. Hojas para imprimir ----------
    for vw in [(1280, 900), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}, accept_downloads=True); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, '0')
        pg.evaluate("go('hojas')")
        n = pg.locator('.hjpv').count()
        ok = False
        for _ in range(40):
            if pg.locator('.hjpv svg').count() == n: ok = True; break
            pg.wait_for_timeout(150)
        chk(n == 6 and ok, f'{vw} cada hoja tiene su vista previa ({pg.locator(".hjpv svg").count()} de {n})')
        chk('Recepción de langosta' in pg.inner_text('[data-hjv="hrec"]') or pg.locator('[data-hjv="hrec"] svg text').count() > 10, f'{vw} la vista previa trae el contenido de la hoja')
        chk(pg.evaluate("document.querySelector('[data-hjv=\"hrec\"] svg').textContent.includes('Recepción de langosta')"), f'{vw} la de Recepción dice «Recepción de langosta»')
        chk(pg.evaluate("PDFSVG") is None, f'{vw} después de armar las vistas previas no queda nada pendiente')
        w0 = pg.evaluate("document.querySelector('[data-hjv=\"hrec\"]').getBoundingClientRect().width")
        pg.click('[data-hjv="hrec"]'); pg.wait_for_timeout(200)
        w1 = pg.evaluate("document.querySelector('[data-hjv=\"hrec\"]').getBoundingClientRect().width")
        chk(w1 > w0 * 1.5 and pg.get_attribute('[data-hjv="hrec"]', 'aria-expanded') == 'true', f'{vw} tocarla la agranda ({w0:.0f} → {w1:.0f} px)')
        pg.click('[data-hjv="hrec"]'); pg.wait_for_timeout(200); chk(pg.get_attribute('[data-hjv="hrec"]', 'aria-expanded') == 'false', f'{vw} tocarla otra vez la achica')
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{vw} sin scroll de lado')
        # paquete
        chk('Paquete de cada orden' in pg.inner_text('#app'), f'{vw} sale «Paquete de cada orden»')
        if pg.locator('[data-hist=hpaq]').count(): pg.click('[data-hist=hpaq]'); pg.wait_for_timeout(150)
        oid = pg.evaluate("ST.OR.slice().sort((a,b)=>a.etd<b.etd?1:-1).find(o=>Object.keys(o.sh||{}).length).id")
        with pg.expect_download() as d: pg.click(f'[data-paq="{oid}"]')
        dl = d.value; z = zipfile.ZipFile(io.BytesIO(open(dl.path(), 'rb').read())); names = z.namelist()
        chk(z.testzip() is None and dl.suggested_filename.startswith('PROPESA_Paquete_Orden_') and dl.suggested_filename.endswith('.zip'), f'{vw} el .zip está bien: {dl.suggested_filename}')
        chk(len(names) >= 3 and all(z.read(x)[:5] == b'%PDF-' for x in names), f'{vw} trae PDF de verdad: {names}')
        chk(any('Ordenes' in x for x in names) and any('Empaque' in x for x in names) and any('Embarque_' in x for x in names), f'{vw} orden, packing list e informe del embarque')
        chk('Paquete descargado' in pg.inner_text('#toast'), f'{vw} avisa que se descargó')
        pg.close()
    b.close()
chk(not errs, f'sin errores de JavaScript {errs}')
print('\n' + ('TODO BIEN' if not fails else f'{len(fails)} FALLAS')); raise SystemExit(1 if fails else 0)
