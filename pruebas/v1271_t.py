"""v1.27.1 (pedido del usuario, 29/oct/2026: «más visual y colorido, que me diga qué me falta empacar»).
Hieleras por talla: aviso grande con lo que falta (una ficha de color por talla), una tarjeta por talla con su color,
un cuadrito por hielera (lleno = empacada) y «Falta N» / «✔ Lista» / «De más». Con más de 24 hieleras en una talla, barra.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v1271_t.py"""
from playwright.sync_api import sync_playwright
import os
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
NUEVA = "z=>{const o={id:uidN(),etd:'2026-10-21',lines:[{id:1,city:'HKG',cons:0,boxes:z.reduce((a,v)=>a+v,0),z,kp:16,tar:0,cc:0}],sh:{}};ST.OR.push(o);syncShip(o,'HKG',0);save();return o.id}"
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw, cs in [((1180, 820), 'light'), ((390, 844), 'dark')]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}, color_scheme=cs); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0");localStorage.setItem("propesa-kp","0")}', seed); pg.reload()
        pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'admin123'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
        # el caso de la captura del usuario: 1 de cada talla, 1 Mediana empacada
        oid = pg.evaluate(NUEVA, [1, 1, 1, 1])
        pg.evaluate(f"go('empacar:{oid}.1')"); pg.evaluate("PKD.lot=openLots()[0];render()")
        t = pg.inner_text('.zsum'); chk('Faltan 4 hieleras por empacar' in t and pg.locator('.zsum.z-pend .zneed').count() == 4, f'{cs} sin empacar: dice cuántas faltan y una ficha por talla: {t!r}')
        pg.fill('#pk_c0', '25'); pg.click('#pkr0 [data-pk="k:0:R"]'); pg.wait_for_timeout(120)
        t = pg.inner_text('.zsum'); need = pg.eval_on_selector_all('.zsum .zneed', 'e=>e.map(x=>x.innerText.replace(/\\s+/g," ").trim())')
        chk('Faltan 3 hieleras por empacar' in t and need == ['1 Chica', '1 Grande', '1 Jumbo'], f'{cs} con 1 Mediana: faltan 3 y dice cuáles: {need}')
        chk(pg.locator('.zrow').count() == 4 and pg.locator('.zrow.lista').count() == 1 and 'Lista' in pg.inner_text('.zrow.lista .zst'), f'{cs} la Mediana sale «✔ Lista» y las otras «Falta 1»')
        chk(pg.locator('.zrow.falta .zst').all_inner_texts() == ['Falta 1'] * 3, f'{cs} cada talla pendiente dice «Falta 1»')
        chk(pg.locator('.zrow .zcells i.f').count() == 1 and pg.locator('.zrow .zcells i:not(.f):not(.x)').count() == 3, f'{cs} un cuadrito por hielera: 1 lleno, 3 vacíos')
        col = pg.evaluate("[...document.querySelectorAll('.zrow')].map(e=>getComputedStyle(e).borderLeftColor)")
        chk(len(set(col)) == 4, f'{cs} cada talla lleva su color: {col}')
        chk(pg.evaluate("document.querySelector('.zt').scrollWidth<=document.querySelector('.zt').clientWidth+1"), f'{cs} {vw[0]} px sin desborde')
        # de más
        pg.fill('#pk_c0', '25'); pg.click('#pkr0 [data-pk="k:0:R"]'); pg.wait_for_timeout(120)
        t = pg.inner_text('.zsum'); chk(pg.locator('.zsum.z-bad').count() == 1 and 'de más' in t and 'Y faltan' in t and 'De más +1' in pg.inner_text('.zt'), f'{cs} 2 Medianas de 1: aviso rojo «de más» y todavía dice lo que falta')
        chk(pg.locator('.zcells i.x').count() == 1, f'{cs} la hielera de más sale con su cuadrito rojo')
        # completa
        pg.evaluate(f"(()=>{{const o=ST.OR.find(o=>o.id=={oid});o.lines[0].z=[0,2,0,0];o.lines[0].boxes=2;save();render()}})()")
        chk('Ya están todas las tallas' in pg.inner_text('.zsum') and pg.locator('.zsum.z-ok').count() == 1, f'{cs} completa: «✔ Ya están todas las tallas»')
        # muchas hieleras: barra en vez de cuadritos
        o2 = pg.evaluate(NUEVA, [0, 30, 6, 0]); pg.evaluate(f"go('orden:{o2}')"); pg.wait_for_timeout(120)
        chk(pg.locator('.zt .zbar').count() == 1 and pg.locator('.zt .zcells i').count() == 6 and 'Faltan 36 hieleras' in pg.inner_text('.zt'), f'{cs} en la orden: 30 Medianas en barra, 6 Grandes en cuadritos, faltan 36')
        pg.close()
    b.close()
chk(not errs, f'sin errores de JavaScript {errs}')
print('\n' + ('TODO BIEN' if not fails else f'{len(fails)} FALLAS')); raise SystemExit(1 if fails else 0)
