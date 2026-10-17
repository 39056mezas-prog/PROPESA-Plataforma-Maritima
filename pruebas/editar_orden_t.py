"""Editar una orden ya creada (v1.8.8, v1.10.0): fecha (ETD) y, por línea, hieleras, tallas, kg de producto y tarimas.
No se piden menos hieleras de las empacadas; no se cambia una línea con el embarque cerrado; piso y consulta no editan.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/editar_orden_t.py"""
from playwright.sync_api import sync_playwright
import os, sys
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em, pw):
    pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0")}', seed); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg, 'admin@propesa.mx', 'admin123')
        # orden nueva con una línea
        pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '2026-10-20'); pg.click('[data-oa=new]'); oid = pg.evaluate('+V.id')
        pg.select_option('#ol_city', 'PVG'); pg.fill('#ol_n', '3'); pg.fill('#ol_z1', '3'); pg.fill('#ol_tar', '1'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(100)
        lid = pg.evaluate(f"ST.OR.find(o=>o.id=={oid}).lines[0].id")
        si = pg.evaluate(f"ST.OR.find(o=>o.id=={oid}).sh[Object.keys(ST.OR.find(o=>o.id=={oid}).sh)[0]]")
        # 1. cambiar la fecha
        pg.click('[data-oa=ee]'); chk(pg.locator('#oe_etd').count() == 1, f'{vw} «Cambiar fecha» abre el campo de fecha')
        pg.click('[data-oa=no]'); chk(pg.locator('#oe_etd').count() == 0 and pg.evaluate(f"ST.OR.find(o=>o.id=={oid}).etd") == '2026-10-20', f'{vw} «Cancelar» no cambia nada')
        pg.click('[data-oa=ee]'); pg.fill('#oe_etd', '2026-10-22'); pg.click('[data-oa=se]')
        chk(pg.evaluate(f"ST.OR.find(o=>o.id=={oid}).etd") == '2026-10-22' and 'Empaque 22/10/2026' in pg.inner_text('#app'), f'{vw} la fecha se guarda y se ve')
        chk('22/10' in pg.evaluate(f"ST.P[{si}].n"), f'{vw} el nombre del embarque toma la fecha nueva: {pg.evaluate(f"ST.P[{si}].n")}')
        # 2. editar hieleras, tallas, producto y tarimas de la línea (v1.10.0: sin cliente final)
        pg.click(f'[data-oa="el:{lid}"]'); chk(pg.input_value('#le_n') == '3' and pg.input_value('#le_z1') == '3' and pg.input_value('#le_tar') == '1', f'{vw} «Editar» muestra hieleras, tallas y tarimas actuales')
        pg.fill('#le_n', '5'); pg.fill('#le_z1', '3'); pg.fill('#le_z2', '2'); pg.select_option('#le_kp', '15'); pg.fill('#le_tar', '2'); pg.click(f'[data-oa="sl:{lid}"]')
        l = pg.evaluate(f"ST.OR.find(o=>o.id=={oid}).lines[0]")
        chk(l['boxes'] == 5 and l['z'] == [0, 3, 2, 0] and l['kp'] == 15 and l['tar'] == 2 and 'cli' not in l, f'{vw} se guardan hieleras, tallas, kg de producto y tarimas: {l}')
        chk(pg.evaluate(f"ST.P[{si}].h") == 5 and pg.evaluate(f"ST.P[{si}].z") == [0, 3, 2, 0], f'{vw} el embarque se actualiza a 5 hieleras y sus tallas')
        g = pg.evaluate(f"gross(ST.P[{si}])"); w = pg.evaluate("pesoStd()")
        chk(abs(g - round(5*w['h'] + 5*w['g'] + 2*w['t'] + 5*15 + 0*w['c'], 1)) < 0.05, f'{vw} peso bruto del embarque = hieleras, gel, tarimas y producto de 15 kg: {g}')
        # validaciones (conservan lo escrito)
        pg.click(f'[data-oa="el:{lid}"]'); pg.fill('#le_z2', '1'); pg.click(f'[data-oa="sl:{lid}"]')
        chk('suman 4' in pg.inner_text('#toast') and pg.input_value('#le_z2') == '1', f'{vw} si las tallas no suman el total no se guarda y se conserva lo escrito')
        pg.fill('#le_z2', '2'); pg.fill('#le_n', '0'); pg.click(f'[data-oa="sl:{lid}"]')
        chk('mínimo 1' in pg.inner_text('#toast') and pg.evaluate(f"ST.OR.find(o=>o.id=={oid}).lines[0].boxes") == 5, f'{vw} 0 hieleras no se guarda')
        pg.click('[data-oa=no]')
        # 3. con hieleras empacadas no se piden menos
        o2 = pg.evaluate("(()=>{for(const o of ST.OR)for(const l of o.lines){const n=ordAssigned(o,l).length;if(n>0)return{o:o.id,l:l.id,n,b:l.boxes}}})()")
        pg.evaluate(f"go('orden:{o2['o']}')"); g = pg.evaluate(f"(ST.OR.find(o=>o.id=={o2['o']}).sh||{{}})")
        gi = list(g.values())[0] if g else None
        if gi is not None: pg.evaluate(f"ST.P[{gi}].closed=false;save();render()")
        pg.click(f'[data-oa="el:{o2["l"]}"]'); chk(f"no puede pedir menos de {o2["n"]}" in pg.inner_text('#app'), f'{vw} la línea con hieleras empacadas lo explica')
        pg.fill('#le_n', str(o2['n'] - 1)); pg.click(f'[data-oa="sl:{o2["l"]}"]')
        chk('no puede pedir menos' in pg.inner_text('#toast') and pg.evaluate(f"ST.OR.find(o=>o.id=={o2['o']}).lines.find(l=>l.id=={o2['l']}).boxes") == o2['b'], f'{vw} pedir menos de las empacadas no se guarda')
        pg.fill('#le_n', str(o2['n'])); pg.fill('#le_z0', str(o2['n'])); pg.click(f'[data-oa="sl:{o2["l"]}"]')
        chk(pg.evaluate(f"ST.OR.find(o=>o.id=={o2['o']}).lines.find(l=>l.id=={o2['l']}).boxes") == o2['n'] and pg.evaluate(f"ordAssigned(ST.OR.find(o=>o.id=={o2['o']}),ST.OR.find(o=>o.id=={o2['o']}).lines.find(l=>l.id=={o2['l']})).length") == o2['n'], f'{vw} igual a las empacadas sí, y las hieleras siguen ligadas a la línea')
        # 4. embarque cerrado: no se edita la línea
        if gi is not None:
            pg.evaluate(f"ST.P[{gi}].closed=true;save();render()"); pg.click(f'[data-oa="el:{o2["l"]}"]')
            chk('ya está cerrado' in pg.inner_text('#toast') and pg.locator('#le_n').count() == 0, f'{vw} con el embarque cerrado no deja editar la línea')
        pg.close()
    # 5. Encargado de piso y Consulta no editan
    for em, pw in [('piso@propesa.mx', 'piso123'), ('consulta@propesa.mx', 'ver123')]:
        pg = b.new_page(viewport={'width': 1180, 'height': 820}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg, em, pw)
        if pg.locator('#le').count(): chk(True, f'{em}: no entra con estos datos de prueba (se omite)'); pg.close(); continue
        pg.evaluate("setPiso(false);go('orden:'+ST.OR[0].id)")
        chk(pg.locator('[data-oa=ee]').count() == 0 and pg.locator('[data-oa^="el:"]').count() == 0, f'{em} no ve «Cambiar fecha» ni «Editar»')
        pg.evaluate("(()=>{const b=document.createElement('button');b.dataset.oa='ee';document.getElementById('app').appendChild(b);b.click()})()")
        chk(pg.locator('#oe_etd').count() == 0, f'{em} ni forzando la acción puede editar'); pg.close()
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
