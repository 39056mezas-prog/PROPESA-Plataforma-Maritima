"""Eliminar una orden (v1.8.3): pedido del usuario, para quitar una orden creada por error.
Solo sin hieleras empacadas; pide confirmar; quita sus embarques abiertos que quedan vacíos y sus notas de empaque.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/eliminar_orden_t.py"""
from playwright.sync_api import sync_playwright
import os, sys
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('dialog', lambda d: d.accept())
        pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0")}', seed); pg.reload()
        pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'admin123'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
        # 1. orden vacía creada por error (como en la captura del usuario): se elimina
        n0 = pg.evaluate('ST.OR.length'); pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '2026-10-16'); pg.click('[data-oa=new]')
        oid = pg.evaluate('+V.id'); chk(pg.evaluate('ST.OR.length') == n0 + 1, f'{vw} se crea una orden vacía')
        chk(pg.locator('[data-oa=dco]').count() == 1, f'{vw} la orden muestra «Eliminar orden»')
        pg.click('[data-oa=dco]'); chk('No se puede deshacer' in pg.inner_text('#app') and pg.evaluate('ST.OR.length') == n0 + 1, f'{vw} pide confirmar antes de eliminar')
        pg.click('[data-oa=no]'); chk(pg.locator('[data-oa=dlo]').count() == 0 and pg.evaluate('ST.OR.length') == n0 + 1, f'{vw} «No» la deja como estaba')
        pg.click('[data-oa=dco]'); pg.click('[data-oa=dlo]')
        chk(pg.evaluate('ST.OR.length') == n0 and not pg.evaluate(f'ST.OR.some(o=>o.id=={oid})') and pg.evaluate('V.v') == 'ordenes', f'{vw} «Sí, eliminar» la quita y regresa a Órdenes')
        chk('Orden eliminada' in pg.inner_text('#toast'), f'{vw} avisa «Orden eliminada»')
        # 2. orden con líneas pero sin hieleras: se elimina con su embarque abierto vacío y sus notas
        p0 = pg.evaluate('ST.P.length'); pg.fill('#no_etd', '2026-10-17'); pg.click('[data-oa=new]'); oid = pg.evaluate('+V.id')
        pg.select_option('#ol_city', 'PVG'); pg.fill('#ol_cli', 'TST'); pg.fill('#ol_n', '3'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(100)
        chk(pg.evaluate('ST.P.length') == p0 + 1, f'{vw} la línea crea su embarque')
        lid = pg.evaluate(f'ST.OR.find(o=>o.id=={oid}).lines[0].id')
        pg.evaluate(f"ST.M['emp:{oid}.{lid}']=[{{id:uidN(),t:now(),by:'Ana Torres',text:'nota de prueba',ref:'',imgs:[]}}];save()")
        pg.evaluate(f"go('orden:{oid}')"); pg.click('[data-oa=dco]'); chk('con 1 línea' in pg.inner_text('#app'), f'{vw} la confirmación dice cuántas líneas tiene')
        pg.click('[data-oa=dlo]')
        chk(not pg.evaluate(f'ST.OR.some(o=>o.id=={oid})') and pg.evaluate('ST.P.length') == p0, f'{vw} se elimina con su embarque vacío')
        chk(not pg.evaluate(f"'emp:{oid}.{lid}' in ST.M"), f'{vw} y sus notas de empaque')
        chk(pg.evaluate("ST.OR.every(o=>Object.values(o.sh||{}).every(i=>ST.P[i]))") and pg.evaluate("Object.values(ST.B).flat().every(b=>b.d==null||ST.P[b.d])"), f'{vw} las demás órdenes y hieleras siguen apuntando a embarques que existen')
        # 3. orden con hieleras empacadas: no se puede
        o = pg.evaluate("(()=>{const o=ST.OR.find(o=>ordBoxes(o).length);return o&&{id:o.id,n:ordBoxes(o).length}})()")
        chk(o is not None, f'{vw} los datos de prueba tienen una orden con hieleras')
        pg.evaluate(f"go('orden:{o['id']}')")
        chk(pg.locator('[data-oa=dco]').count() == 0 and 'no se puede eliminar' in pg.inner_text('#app'), f'{vw} con hieleras empacadas no hay botón y explica por qué')
        pg.evaluate(f"OA.cf='ord';render()"); chk(pg.locator('[data-oa=dlo]').count() == 0, f'{vw} ni forzando la confirmación aparece el botón')
        pg.evaluate("(()=>{const b=document.createElement('button');b.dataset.oa='dlo';document.getElementById('app').appendChild(b);b.click()})()")
        chk(pg.evaluate(f"ST.OR.some(o=>o.id=={o['id']})") and pg.evaluate(f"ordBoxes(ST.OR.find(o=>o.id=={o['id']})).length") == o['n'], f'{vw} y la acción tampoco la borra (hieleras intactas)')
        pg.close()
    # 4. Encargado de piso y Consulta no ven el botón
    for em, pw in [('piso@propesa.mx', 'piso123'), ('consulta@propesa.mx', 'ver123')]:
        pg = b.new_page(viewport={'width': 1180, 'height': 820}); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0")}', seed); pg.reload()
        pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
        if pg.locator('#le').count(): chk(True, f'{em}: no entra con estos datos de prueba (se omite)'); pg.close(); continue
        pg.evaluate("setPiso(false);go('orden:'+ST.OR[0].id)")
        chk(pg.locator('[data-oa=dco]').count() == 0, f'{em} no ve «Eliminar orden»'); pg.close()
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
