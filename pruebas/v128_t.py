"""v1.28.0 (pedido del usuario, 29/oct/2026: «quitar gris del teclado; otro lugar para agregar hieleras grises, pero extra»).
1. La categoría gris (despatada) ya no sale en el teclado, en los botones de cada hielera ni en «Poner a todas» (vista completa y Modo piso).
2. «Hieleras grises · extra»: se agregan aparte; van con el cliente (packing list, hieleras y peso del embarque, tallas del embarque)
   pero no cuentan para las hieleras pedidas (la línea sigue «1 de 4», se completa sin ellas).
3. No se guarda sin piezas ni con más de 35; quitar pide confirmación.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v128_t.py"""
from playwright.sync_api import sync_playwright
import os
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, piso):
    pg.goto(BASE); pg.evaluate('([s,p])=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso",p);localStorage.setItem("propesa-kp","1")}', [seed, piso]); pg.reload()
    pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'admin123'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
NUEVA = "()=>{const o={id:uidN(),etd:dLoc(),lines:[{id:1,city:'HKG',cons:0,boxes:4,z:[1,1,1,1,0],kp:16,tar:0,cc:0}],sh:{}};ST.OR.push(o);syncShip(o,'HKG',0);save();return o.id}"
def toast(pg): return pg.inner_text('#toast') if pg.locator('#toast').count() else ''
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        # ---------- vista completa ----------
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg, '0'); oid = pg.evaluate(NUEVA); D = pg.evaluate("gxK()")
        chk(D == 'D', f'{vw} la gris es la categoría {D}')
        pg.evaluate(f"go('empacar:{oid}.1')"); pg.evaluate("PKD.lot=openLots()[0];render()"); pg.wait_for_timeout(100)
        chk(pg.locator(f'[data-pk="k:0:{D}"]').count() == 0 and pg.locator('[data-pk="k:0:R"]').count() == 1, f'{vw} los botones de la hielera ya no traen Gris')
        chk(pg.locator('#kpad').count() == 1 and pg.locator(f'#kpad [data-kp="k:{D}"]').count() == 0 and pg.locator('#kpad [data-kp="k:R"]').count() == 1, f'{vw} el teclado ya no trae Gris')
        chk(pg.locator('#gxc').count() == 1 and 'Hieleras grises · extra' in pg.inner_text('#gxc'), f'{vw} sale el lugar aparte para las grises')
        sh = pg.evaluate(f"ST.OR.find(o=>o.id=={oid}).sh['HKG|0']"); g0 = pg.evaluate(f"gross(ST.P[{sh}])")
        # sin piezas / más de 35: no se guarda y no borra lo escrito
        pg.click('[data-gx=add]'); chk('Escribe las piezas' in toast(pg) and pg.evaluate(f"ordAssigned(ST.OR.find(o=>o.id=={oid}),ST.OR.find(o=>o.id=={oid}).lines[0]).length") == 0, f'{vw} sin piezas no se agrega')
        pg.fill('#gx_c', '36'); pg.click('[data-gx=add]'); chk('35' in toast(pg) and pg.input_value('#gx_c') == '36', f'{vw} con 36 no se guarda y no borra lo escrito')
        pg.fill('#gx_c', '20'); pg.click('[data-gx=add]'); pg.wait_for_timeout(100)
        O = f"ST.OR.find(o=>o.id=={oid})"; L = f"{O}.lines[0]"
        chk(pg.evaluate(f"ordGx({O},{L}).length") == 1 and pg.evaluate(f"ordPk({O},{L}).length") == 0 and pg.evaluate(f"ordGx({O},{L})[0].b.c") == 20, f'{vw} se guarda 1 hielera gris de 20 piezas y no cuenta como pedida')
        chk('Hielera 1' in pg.inner_text('#gxc') and '20 piezas' in pg.inner_text('#gxc'), f'{vw} la gris sale en la lista de extras')
        chk('Faltan 4 hieleras' in pg.inner_text('.zsum') and '1 hielera gris extra' in pg.inner_text('.zsum'), f'{vw} por talla: siguen faltando 4 y avisa la gris extra')
        chk(pg.locator('.pkdn').count() == 0, f'{vw} la gris no sale entre las hieleras pedidas')
        P = f"ST.P[{sh}]"; h, z, g1 = pg.evaluate(f"{P}.h"), pg.evaluate(f"{P}.z"), pg.evaluate(f"gross({P})")
        chk(h == 5 and z[4] == 1 and sum(z) == 5 and abs(g1 - g0 - (1.4 + 1.5 + 16)) < 0.05 if pg.evaluate("ST.W&&ST.W.h")==1.4 else h == 5 and z[4] == 1 and g1 > g0, f'{vw} el embarque cuenta 5 hieleras, 1 gris en tallas y sube el peso bruto: {h} {z} {g0}→{g1}')
        chk(pg.evaluate(f"shipIssues({sh}).map(x=>x.t).join('|')").find('deberían sumar') < 0, f'{vw} sin aviso de tallas que no suman')
        # completar las 4 pedidas: la línea queda completa con la gris aparte
        for k in ['B', 'R', 'V', 'A']:
            pg.evaluate(f"PKD.rows[0]={{c:'25',k:'{k}'}};pkAutoV(0)"); pg.wait_for_timeout(100)  # con el teclado abierto
        chk(pg.evaluate(f"ordPk({O},{L}).length") == 4 and 'Ya están todas las tallas' in pg.inner_text('.zsum') and pg.locator('#pkfin').count() == 1, f'{vw} 4 de 4 completas con la gris extra aparte')
        chk(pg.evaluate(f"ordBoxes({O}).length") == 5, f'{vw} el packing list lleva las 5 hieleras')
        # quitar con confirmación
        seq = pg.evaluate(f"ordGx({O},{L})[0].b.seq"); pg.click(f'[data-gx="cf:{seq}"]'); chk('¿Quitar?' in pg.inner_text('#gxc'), f'{vw} quitar pregunta primero')
        pg.click(f'[data-gx="rm:{seq}"]'); pg.wait_for_timeout(80)
        chk(pg.evaluate(f"ordGx({O},{L}).length") == 0 and pg.evaluate(f"{P}.h") == 4, f'{vw} quitada: el embarque regresa a 4 hieleras')
        pg.close()
        # ---------- Modo piso ----------
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg, '1'); oid = pg.evaluate(NUEVA); O = f"ST.OR.find(o=>o.id=={oid})"; L = f"{O}.lines[0]"
        pg.evaluate(f"PE.lot=openLots()[0];go('pemp:{oid}.1')"); pg.wait_for_timeout(150)
        chk(pg.locator('.pbx').count() == 4, f'{vw} piso: 4 lugares de hielera')
        chk(pg.locator(f'[data-pe="all:{D}"]').count() == 0 and pg.locator('[data-pe="all:R"]').count() == 1, f'{vw} piso: «Poner a todas» ya no trae Gris')
        chk(pg.locator(f'#kpad [data-kp="k:{D}"]').count() == 0, f'{vw} piso: el teclado ya no trae Gris')
        pg.fill('#gx_c', '18'); pg.click('[data-gx=add]'); pg.wait_for_timeout(120)
        chk(pg.evaluate(f"ordGx({O},{L}).length") == 1 and pg.locator('.pbx').count() == 4 and pg.locator('.pbx.sv').count() == 0, f'{vw} piso: la gris se agrega aparte y no ocupa un lugar')
        chk('0' in pg.inner_text('.pkn2 b') and '18 piezas' in pg.inner_text('#gxc'), f'{vw} piso: siguen 0 completadas y la gris sale en extras')
        pg.close()
    b.close()
chk(not errs, f'sin errores de JavaScript {errs}')
print('\n' + ('TODO BIEN' if not fails else f'{len(fails)} FALLAS')); raise SystemExit(1 if fails else 0)
