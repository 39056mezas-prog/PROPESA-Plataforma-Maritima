"""v1.10.0 · Órdenes por destino + consignatario (tallas, kg de producto, tarimas, cajas de cartón y peso bruto), hieleras de 15 kg
en el tablero de tanques y monitoreo de temperatura (fecha, hora, flotante, superficie, producto; rango 48.4–56.6 °F; PDF interno).
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/ordenes_t.py"""
from playwright.sync_api import sync_playwright
import os, sys, re
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em='admin@propesa.mx', pw='admin123'):
    pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0");localStorage.setItem("propesa-kp","0")}', seed); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def pdf_text(pg, k, arg):
    raw = pg.evaluate(f"(async()=>{{const d=await pdfMake('{k}','{arg}');return Array.from(d.u8).map(c=>String.fromCharCode(c)).join('')}})()")
    return ' '.join(re.findall(r'\(((?:[^()\\]|\\.)*)\)\s*Tj', raw))
def linea(pg, n, z, kp='16', tar='0', cc='', cons=0, city='PVG'):
    if pg.locator('[data-oa=add]').count(): pg.click('[data-oa=add]')
    pg.select_option('#ol_city', city); pg.select_option('#ol_cons', index=cons); pg.fill('#ol_n', str(n))
    for i, v in enumerate(z): pg.fill(f'#ol_z{i}', str(v))
    pg.select_option('#ol_kp', kp); pg.fill('#ol_tar', str(tar)); pg.fill('#ol_cc', str(cc)); pg.click('[data-oa=ln]'); pg.wait_for_timeout(80)

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg)
        # 1. tablero de tanques: hieleras de 15 kg por talla
        pg.evaluate("go('recepcion')"); t = pg.inner_text('.tqsz')
        chk('40 hieleras' in t and '16 hieleras + 1.0 kg' in t and '122 hieleras + 21.5 kg sueltos' in t, f'{vw} tanques: hieleras de 15 kg por talla y total')
        # 2. orden con dos consignatarios; pesos como la hoja de PROPESA (cartón 0.9)
        pg.evaluate("ST.W={h:1.4,g:1.5,t:9.9,p:16,c:0.9};pesosSync();save()")
        pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '2026-10-20'); pg.click('[data-oa=new]'); oid = pg.evaluate('+V.id'); O = f"ST.OR.find(o=>o.id=={oid})"
        chk('Cliente' not in pg.inner_text('#ol_f') and pg.locator('#ol_cli').count() == 0, f'{vw} la orden ya no pide cliente final')
        pg.fill('#ol_z1', '76'); pg.fill('#ol_z2', '30')
        chk(pg.input_value('#ol_n') == '106' and '106 hieleras' in pg.inner_text('#ol_zs'), f'{vw} v1.12.0: el total sale solo de las tallas: {pg.input_value("#ol_n")}')
        pg.fill('#ol_z3', '4'); pg.fill('#ol_tar', '6'); chk(pg.input_value('#ol_n') == '110' and '59.4' in pg.inner_text('#ol_pb') and '1760.0' in pg.inner_text('#ol_pb'), f'{vw} la tabla de peso bruto se arma mientras se escribe')
        pg.click('[data-oa=ln]'); pg.wait_for_timeout(80)
        l = pg.evaluate(f"{O}.lines[0]")
        chk(l == {'id': 1, 'city': 'PVG', 'cons': 0, 'boxes': 110, 'z': [0, 76, 30, 4], 'kp': 16, 'tar': 6, 'cc': 0}, f'{vw} se guarda destino, consignatario, total, tallas, producto, tarimas y cartón: {l}')
        chk(pg.evaluate(f"ordG({O})") == 2138.4, f'{vw} peso bruto igual a la hoja: 154 + 165 + 59.4 + 1760 + 0 = 2138.4 ({pg.evaluate(f"ordG({O})")})')
        tx = pg.inner_text('#app'); chk('2138.4 kg de peso bruto' in tx and '1760 kg neto' in tx, f'{vw} la orden muestra el peso bruto y neto')
        # segundo consignatario: producto de 15 kg y cajas de cartón (como «PVG ABEL» de la hoja, con cartón 0.7)
        pg.evaluate("ST.W={h:1.4,g:1.5,t:9.9,p:16,c:0.7};pesosSync();save();render()")
        linea(pg, 50, [0, 30, 16, 4], kp='15', tar=3, cc=50, cons=1)
        l2 = pg.evaluate(f"{O}.lines[1]"); chk(l2['kp'] == 15 and l2['cc'] == 50 and pg.evaluate(f"lnG({O}.lines[1])") == 959.7, f'{vw} 50 hieleras de 15 kg con 50 cajas de cartón = 959.7 kg (como la hoja): {pg.evaluate(f"lnG({O}.lines[1])")}')
        chk(pg.locator('text=Peso bruto de toda la orden').count() == 1, f'{vw} con dos consignatarios aparece el peso bruto de toda la orden')
        linea(pg, 5, [5, 0, 0, 0], cons=1); chk('ya está en esta orden' in pg.inner_text('#toast') and pg.evaluate(f"{O}.lines.length") == 2, f'{vw} el mismo consignatario no se repite en la orden')
        (pg.locator('[data-oa=add]').count() and pg.click('[data-oa=add]')); chk(pg.evaluate("[...document.querySelectorAll('#ol_city option')].map(o=>o.value)") == ['PVG'], f'{vw} cada orden lleva un solo destino: la ciudad queda fija')
        pg.click('[data-oa=no]')
        # el embarque toma tallas y peso de la orden
        si = pg.evaluate(f"{O}.sh['PVG|0']")
        chk(pg.evaluate(f"ST.P[{si}].z") == [0, 76, 30, 4] and abs(pg.evaluate(f"gross(ST.P[{si}])") - pg.evaluate(f"lnG({O}.lines[0])")) < 0.05, f'{vw} el embarque toma tallas y peso bruto de la orden')
        pg.evaluate(f"go('emb:{si}')"); chk(pg.locator('[data-zs]').count() == 0 and 'Vienen de la orden' in pg.inner_text('#emb_tallas'), f'{vw} en Embarque las tallas ya no se capturan')
        chk('Tarimas' in pg.inner_text('#emb_peso') and pg.locator('[data-a^="pwfix:"]').count() == 0, f'{vw} el peso del embarque trae tarimas y no avisa discrepancia')
        # tallas empacadas contra las pedidas
        o2 = pg.evaluate(f"(()=>{{const o={{id:uidN(),etd:'2026-10-21',lines:[{{id:1,city:'HKG',cons:0,boxes:2,z:[0,1,1,0],kp:16,tar:0,cc:0}}],sh:{{}}}};ST.OR.push(o);syncShip(o,'HKG',0);save();return o.id}})()")
        pg.evaluate(f"go('empacar:{o2}.1')"); pg.evaluate("PKD.lot=openLots()[0]")
        chk('Hieleras por talla' in pg.inner_text('#app') and pg.locator('.zt').count() == 1, f'{vw} al empacar se ven las hieleras pedidas por talla')
        for r in range(2): pg.fill('#pk_c0', '25'); pg.click('#pkr0 [data-pk="k:0:R"]'); pg.wait_for_timeout(100)  # v1.12.0: se completan solas
        chk('De más' in pg.inner_text('.zt'), f'{vw} empacar 2 medianas cuando piden 1 avisa «De más»')
        s2 = pg.evaluate(f"ST.OR.find(o=>o.id=={o2}).sh['HKG|0']"); iss = pg.evaluate(f"shipIssues({s2}).map(x=>x.t+'|'+(x.go||''))")
        chk(any('tallas no cuadran' in x and f'empacar:{o2}.1' in x for x in iss), f'{vw} el embarque avisa en rojo y lleva a la línea: {iss}')
        tx = pdf_text(pg, 'ord', oid)
        for s in ['PESO BRUTO', '2138.4', '959.7', 'MEDIANA', 'TARIMAS', 'CAJA DE CART', 'PESO BRUTO DE TODA LA ORDEN']:
            chk(s in tx, f'{vw} el PDF de la orden trae «{s}»')
        # 3. temperatura
        pg.evaluate("go('temperatura')")
        for k in ['Termómetro flotante', 'Superficie del agua', 'Interna del producto']: chk(k in pg.inner_text('#app'), f'{vw} Temperatura pide «{k}»')
        chk(pg.locator('#tq_d[data-dt=d]').count() == 1 and pg.locator('#tq_h[data-dt=h]').count() == 1, f'{vw} fecha y hora por separado (v1.12.0: se escriben)')
        pg.fill('#tq_d', '2026-10-17'); pg.fill('#tq_h', '06:30'); pg.fill('#tq_a', '52.1'); pg.fill('#tq_s', '58.2'); pg.fill('#tq_p', '50'); pg.click('[data-a=tq]')
        chk('Lectura guardada' in pg.inner_text('#toast') and 'rango' not in pg.inner_text('#toast').lower(), f'{vw} rango pendiente: al guardar no habla de rango: {pg.inner_text("#toast")}')
        row = pg.inner_text('#tq_tbl tbody tr >> nth=0')
        chk('17/10/2026' in row and '06:30' in row and '58.2 °F' in row and pg.locator('.tqout').count() == 0, f'{vw} la tabla separa fecha y hora, sin rojos mientras el rango esté pendiente: {row!r}')
        chk(pg.locator('.alb:has-text("fuera de rango")').count() == 0 and 'rango' not in pg.inner_text('#app').lower(), f'{vw} sin aviso de rango en la página')
        tx = pdf_text(pg, 'temp', '')
        for s_ in ['Monitoreo de temperatura', 'flotante', 'Superficie del agua', 'Interna del producto', '58.2']:
            chk(s_.lower() in tx.lower(), f'{vw} el PDF de monitoreo trae «{s_}»')
        chk('rango' not in tx.lower(), f'{vw} el PDF no habla de rango mientras esté pendiente')
        chk(not pg.evaluate("document.documentElement.scrollWidth>innerWidth"), f'{vw} sin desborde horizontal')
        pg.close()
    # datos: las líneas nuevas se comparten y sobreviven a un respaldo; valores raros se descartan; las viejas conservan su cliente
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg)
    r = pg.evaluate("""(()=>{const o={id:9,etd:'2026-10-20',sh:{},lines:[{id:1,city:'PVG',cons:0,boxes:3,z:[1,1,1,0],kp:15,tar:1,cc:3},{id:2,city:'PVG',cons:1,boxes:2,z:[1,'x',1,0],kp:-4,tar:1.5,cc:'2'},{id:3,city:'PVG',cons:2,cli:'HXH',boxes:4}]};
      return{w:WN.OR(o).lines,c:cleanST({...ST,OR:[o]}).OR[0].lines,d:decodeST(new Map([['OR/9',WN.OR(o)]])).OR[0].lines}})()""")
    chk(r['w'][0] == {'id': 1, 'city': 'PVG', 'cons': 0, 'boxes': 3, 'z': [1, 1, 1, 0], 'kp': 15, 'tar': 1, 'cc': 3}, f'la línea nueva se comparte completa: {r["w"][0]}')
    chk(r['w'][1] == {'id': 2, 'city': 'PVG', 'cons': 1, 'boxes': 2}, f'tallas, kg o tarimas raros se descartan: {r["w"][1]}')
    chk(r['w'][2].get('cli') == 'HXH' and r['c'][2].get('cli') == 'HXH' and 'cli' not in r['c'][0], 'la línea vieja conserva su cliente; la nueva no inventa uno')
    chk(r['c'][0] == r['w'][0] and r['d'][0] == r['w'][0], 'sobrevive a un respaldo y a la base compartida')
    chk(pg.evaluate("lnG({id:1,city:'PVG',cons:2,cli:'HXH',boxes:4})") == round(4 * 19.6, 1), 'una línea de antes conserva su peso (19.6 kg por hielera, sin tarimas)')
    pg.close()
    # Pedido 17/oct: con la cuenta de Consulta el usuario entró a Modo piso y no podía salir
    for em, pw in [('consulta@propesa.mx', 'ver123'), ('admin@propesa.mx', 'admin123')]:  # el Encargado de piso se queda en Modo piso (decisión del 12/oct)
        for vw in [(1180, 820), (390, 844)]:
            pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, em, pw)
            if pg.locator('#le').count(): continue
            pg.evaluate("setPiso(false);go('inicio')")
            if pg.locator('.sb [data-mode=piso]').count():
                pg.evaluate("document.querySelector('.sb [data-mode=piso]').click()"); pg.wait_for_timeout(900)
            else: pg.evaluate("switchMode(true)"); pg.wait_for_timeout(900)
            chk(pg.locator('.pshell').count() == 1, f'{em} {vw} entra a Modo piso')
            sw = pg.locator('.phd [data-mode=full]'); vis = sw.count() == 1 and sw.is_visible()
            chk(vis, f'{em} {vw} en Modo piso ve el interruptor para salir')
            if vis:
                h = sw.bounding_box()['height']; chk(h >= 44, f'{em} {vw} el interruptor mide {h:.0f} px (44 o más)')
                sw.click(); pg.wait_for_timeout(1100)
            chk(pg.locator('.sb').count() == 1 and pg.locator('.pshell').count() == 0, f'{em} {vw} sale de Modo piso a la vista completa')
            pg.close()
    # Consulta y piso no agregan destinos
    for em, pw in [('piso@propesa.mx', 'piso123'), ('consulta@propesa.mx', 'ver123')]:
        pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, em, pw)
        if pg.locator('#le').count(): continue
        pg.evaluate("setPiso(false);go('orden:'+ST.OR[0].id)"); chk(pg.locator('#ol_n').count() == 0 and pg.locator('[data-oa=add]').count() == 0, f'{em} no agrega destinos a la orden'); pg.close()
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
