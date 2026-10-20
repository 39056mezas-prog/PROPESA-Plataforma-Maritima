"""v1.12.0 · Pedidos del usuario del 18/oct/2026:
- Mortalidad sin «Revisión aparte / se calcula sola / no es un paso del flujo».
- Embarque: «Editar pesos» ahí mismo (Administrador).
- Ventana para instalar la app.
- Orden: tallas primero y el total sale solo; sin tallas se escribe el total; tarimas y cartón aparte; aviso «Falta el destino»; nueva orden en el encabezado.
- Fechas y horas escritas (sin calendario ni reloj), con «Hoy» / «Ahora»; hora inicial del Formato 06 con «Ahora».
- Empaque (vista completa): cada hielera se completa sola; al terminar se cierra el teclado y sale «Listo».
- Entrada: «+ Agregar proveedor…» ahí mismo (Administrador); sin «Quitar guardadas de la lista»; «Más datos» abierto desde el principio.
- Empacar sin lote y conectarlo después; sin CSV; sin «Eliminar orden» en Modo piso.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v112_t.py"""
from playwright.sync_api import sync_playwright
import os, sys, re
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em='admin@propesa.mx', pw='admin123', piso='0', kp='0'):
    pg.goto(BASE); pg.evaluate('([s,p,k])=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso",p);localStorage.setItem("propesa-kp",k)}', [seed, piso, kp]); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def pdf_text(pg, k, arg):
    raw = pg.evaluate(f"(async()=>{{const d=await pdfMake('{k}','{arg}');return Array.from(d.u8).map(c=>String.fromCharCode(c)).join('')}})()")
    return ' '.join(re.findall(r'\(((?:[^()\\]|\\.)*)\)\s*Tj', raw))
def nueva_orden(pg, n=3, z=True):
    zz = f",z:[{n},0,0,0]" if z else ''
    return pg.evaluate(f"(()=>{{const o={{id:uidN(),etd:'2026-10-20',lines:[{{id:1,city:'PVG',cons:0,boxes:{n}{zz},kp:16,tar:0,cc:0}}],sh:{{}}}};ST.OR.push(o);syncShip(o,'PVG',0);save();return o.id}})()")
def sin_desborde(pg): return not pg.evaluate("document.documentElement.scrollWidth>innerWidth+1")
def toast(pg): return pg.inner_text('#toast') if pg.locator('#toast').is_visible() else ''

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg)
        # ---------- 1. Mortalidad ----------
        pg.evaluate("setPiso(false);go('cierre')"); t = pg.inner_text('#app')
        chk('Revisión aparte' not in t and 'No es un paso' not in t and 'se calcula sola' not in t.lower(), f'{vw} Mortalidad sin «Revisión aparte / se calcula sola»')
        menu = pg.evaluate("document.querySelector('.sb [data-go=cierre]')?.innerText||''")
        chk('calcula sola' not in menu.lower() and 'lotes cerrados' in menu, f'{vw} el menú dice solo los lotes cerrados: {menu!r}')
        chk('Revisión aparte' not in pdf_text(pg, 'mort', ''), f'{vw} el PDF tampoco')
        # ---------- 2. Fechas y horas escritas ----------
        for v in ['recepcion', 'ordenes', 'temperatura']:
            pg.evaluate(f"go('{v}')")
            if v == 'recepcion': pg.click('[data-a=nf]')
            chk(pg.locator('#app input[type=date],#app input[type=time]').count() == 0, f'{vw} {v}: sin calendario ni reloj del teléfono')
        pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]')
        pg.fill('#fd', ''); pg.click('#fd'); pg.keyboard.type('22092026'); chk(pg.input_value('#fd') == '22/09/2026', f'{vw} la fecha se escribe con números y se ponen solas las diagonales: {pg.input_value("#fd")}')
        pg.fill('#fh', ''); pg.click('#fh'); pg.keyboard.type('1350'); chk(pg.input_value('#fh') == '13:50', f'{vw} la hora se escribe con números: {pg.input_value("#fh")}')
        pg.click('[data-dtn=fd]'); hoy = pg.evaluate("fd(dLoc())"); chk(pg.input_value('#fd') == hoy, f'{vw} «Hoy» pone la fecha de hoy')
        pg.fill('#fd', '31/02/2026'); pg.select_option('#fo', '1')
        for k, v in {'#ftt': '58', '#ftp': '55-60', '#fkb': '34', '#fdes': '0', '#fk0': '100'}.items(): pg.fill(k, v)
        pg.click('[data-a=sv]'); pg.wait_for_timeout(80)
        chk('Escribe la fecha de recepción así' in pg.inner_text('#app') and pg.input_value('#fk0') == '100', f'{vw} una fecha que no existe no se guarda y se conserva lo escrito')
        pg.fill('#fd', '22/09/2026'); pg.fill('#fl', 'WLRCOV112'); pg.click('[data-a=sv]'); pg.wait_for_timeout(100)
        r = pg.evaluate("R_('WLRCOV112')"); chk(r and r['rdate'] == '2026-09-22' and r['time'] == '13:50', f'{vw} se guarda igual que antes: {r and (r["rdate"], r["time"])}')
        pg.evaluate("go('temperatura')"); pg.fill('#tq_d', '17/10/2026'); pg.fill('#tq_h', '0630'); pg.fill('#tq_a', '52'); pg.click('[data-a=tq]'); pg.wait_for_timeout(80)
        chk(pg.evaluate("ST.T.some(x=>x.t=='2026-10-17T06:30')"), f'{vw} temperatura con fecha y hora escritas')
        # ---------- 3. Órdenes ----------
        pg.evaluate("go('ordenes')")
        chk(pg.locator('.ordh #no_etd').count() == 1 and pg.locator('.ordl').count() == 1, f'{vw} «Nueva orden» va en el encabezado y las órdenes en su propia tarjeta')
        pg.fill('#no_etd', '20/10/2026'); pg.click('[data-oa=new]'); oid = pg.evaluate('+V.id'); O = f"ST.OR.find(o=>o.id=={oid})"
        chk(pg.evaluate(f"{O}.etd") == '2026-10-20', f'{vw} la orden se crea con la fecha escrita')
        chk('Falta el destino' in pg.inner_text('#app') and 'Sin líneas' not in pg.inner_text('#app'), f'{vw} el aviso dice «Falta el destino»')
        ys = pg.evaluate("['ol_z0','ol_z3','ol_n','ol_kp','ol_tar','ol_cc'].map(i=>document.getElementById(i).getBoundingClientRect().top)")
        chk(ys[0] <= ys[2] and ys[2] < ys[3] + 1 and ys[4] >= ys[2], f'{vw} primero las tallas y el total; después producto, tarimas y cartón: {ys}')
        chk(pg.locator('.lnemp #ol_tar').count() == 1 and pg.locator('.lnemp #ol_cc').count() == 1, f'{vw} tarimas y cartón van en su propio apartado')
        pg.fill('#ol_z0', '10'); pg.fill('#ol_z1', '5')
        chk(pg.input_value('#ol_n') == '15' and pg.evaluate("document.getElementById('ol_n').readOnly"), f'{vw} el total sale solo de las tallas: {pg.input_value("#ol_n")}')
        pg.fill('#ol_z1', ''); chk(pg.input_value('#ol_n') == '10', f'{vw} y se actualiza al cambiarlas')
        pg.fill('#ol_z1', '5'); pg.fill('#ol_tar', '1'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(80)
        l = pg.evaluate(f"{O}.lines[0]"); chk(l['boxes'] == 15 and l['z'] == [10, 5, 0, 0], f'{vw} la línea guarda total 15 y sus tallas: {l}')
        # sin tallas: se escribe el total
        o2 = pg.evaluate("(()=>{const o={id:uidN(),etd:'2026-10-21',lines:[],sh:{}};ST.OR.push(o);save();return o.id})()"); pg.evaluate(f"go('orden:{o2}')")
        chk(not pg.evaluate("document.getElementById('ol_n').readOnly"), f'{vw} sin tallas el total se puede escribir')
        pg.fill('#ol_n', '4'); pg.fill('#ol_tar', '0'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(80)
        l2 = pg.evaluate(f"ST.OR.find(o=>o.id=={o2}).lines[0]"); chk(l2 and l2['boxes'] == 4 and 'z' not in l2, f'{vw} se guarda una línea sin tallas (tallas opcionales): {l2}')
        si = pg.evaluate(f"ST.OR.find(o=>o.id=={o2}).sh['PVG|0']")
        chk(not any('tallas' in x for x in pg.evaluate(f"shipIssues({si}).map(x=>x.t)")), f'{vw} el embarque no avisa de tallas mientras se empaca')
        pg.evaluate(f"go('empacar:{o2}.1')"); pg.evaluate("PKD.lot='WLRCO051026A'")
        pg.fill('#pk_c0', '25'); pg.click('#pkr0 [data-pk="k:0:R"]'); pg.wait_for_timeout(100)
        chk(pg.evaluate(f"ST.P[{si}].z") == [0, 1, 0, 0], f'{vw} sin tallas pedidas, el embarque toma las tallas de lo empacado: {pg.evaluate(f"ST.P[{si}].z")}')
        chk(sin_desborde(pg), f'{vw} sin desborde')
        # ---------- 4. Empaque: se completan solas y «Listo» ----------
        o3 = nueva_orden(pg, 3); pg.evaluate(f"go('empacar:{o3}.1')"); pg.click('[data-pk="lot:WLRCO051026A"]')
        pg.fill('#pk_c0', '30'); pg.click('#pkr0 [data-pk="k:0:B"]'); pg.wait_for_timeout(100)
        chk(len(pg.evaluate(f"ordBoxes(ST.OR.find(o=>o.id=={o3}))")) == 1 and '1 completada' in pg.inner_text('#app'), f'{vw} con piezas y categoría la hielera queda completada sola')
        for _ in range(2): pg.fill('#pk_c0', '29'); pg.click('#pkr0 [data-pk="k:0:B"]'); pg.wait_for_timeout(100)
        chk(len(pg.evaluate(f"ordBoxes(ST.OR.find(o=>o.id=={o3}))")) == 3, f'{vw} las 3 hieleras quedan guardadas')
        chk(pg.locator('#pkfin.pop').count() == 1 and 'Listo' in toast(pg), f'{vw} al terminar sale «Listo» con animación')
        chk(pg.locator('#kpad').count() == 0 and pg.locator('.pkrow').count() == 0, f'{vw} ya no quedan filas en captura')
        # sin CSV
        pg.evaluate(f"go('orden:{o3}')"); chk(pg.locator('[data-oa=csv]').count() == 0 and pg.evaluate("typeof ordCsv") == 'undefined', f'{vw} ya no está «Descargar packing list (CSV)»')
        # Formato 06: hora inicial con «Ahora»
        chk(pg.locator('#f6_hi[data-dt=h]').count() == 1 and pg.locator('[data-dtn=f6_hi]').count() == 1, f'{vw} la hora inicial es una casilla de texto con «Ahora»')
        pg.fill('#f6_hi', ''); pg.click('[data-dtn=f6_hi]'); pg.click(f'[data-f6="sv:{o3}"]'); pg.wait_for_timeout(80)
        chk(re.match(r'^\d{2}:\d{2}$', pg.evaluate(f"(ST.OR.find(o=>o.id=={o3}).f||{{}}).hi||''") or ''), f'{vw} «Ahora» pone la hora y se guarda')
        # ---------- 5. Embarque: editar pesos ahí mismo ----------
        si3 = pg.evaluate(f"ST.OR.find(o=>o.id=={o3}).sh['PVG|0']"); pg.evaluate(f"go('emb:{si3}')")
        chk(pg.locator('#emb_peso [data-a=ewp]').count() == 1, f'{vw} Embarque tiene «Editar pesos»')
        pg.click('#emb_peso [data-a=ewp]'); chk(pg.locator('#emb_peso #pw_t').count() == 1, f'{vw} se abren los pesos (hielera, gel, tarima, producto, cartón)')
        pg.fill('#pw_t', '10.5'); pg.click('#emb_peso [data-a=pw]'); pg.wait_for_timeout(80)
        chk(pg.evaluate("pesoStd().t") == 10.5 and pg.locator('#emb_peso #pw_t').count() == 0, f'{vw} se guardan y se cierra')
        pg.evaluate("ST.W={h:1.4,g:1.5,t:9.9,p:16,c:0.7};pesosSync();save()")
        # ---------- 6. Entrada: proveedor nuevo ahí mismo ----------
        pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.fill('#fk0', '123'); pg.fill('#fd', '18/10/2026')
        chk('+ Agregar proveedor' in pg.inner_text('#fo'), f'{vw} la lista de proveedores trae «+ Agregar proveedor…»')
        pg.select_option('#fo', '__new'); pg.wait_for_timeout(80)
        chk(pg.locator('#npv').count() == 1 and pg.input_value('#fk0') == '123', f'{vw} se abre «Nuevo proveedor» sin perder lo escrito')
        pg.fill('#np_n', 'SCPP Bahía Tortugas'); pg.fill('#np_k', 'bt'); pg.click('[data-npv=sv]'); pg.wait_for_timeout(100)
        chk(pg.locator('#npv').count() == 0 and pg.evaluate("pvBy(document.getElementById('fo').value)?.k") == 'BT' and pg.input_value('#fl') == 'WLRBT181026' and pg.input_value('#fk0') == '123', f'{vw} queda elegido, propone su lote y conserva lo escrito')
        pg.click('[data-a=nf]')
        # hoja de entradas: datos extra abiertos, sin «Quitar guardadas»
        pg.evaluate("PEN=null;go('pent')"); pg.wait_for_timeout(80)
        chk(pg.is_visible('[data-pr="1:tempT"]') and 'Más datos' in pg.inner_text('[data-pa="more:1"]'), f'{vw} los datos extra se ven desde el principio')
        pg.select_option('[data-pr="1:origin"]', '__new'); pg.wait_for_timeout(80)
        pg.fill('#np_n', 'SCPP Isla Cedros'); pg.fill('#np_k', 'IC'); pg.click('[data-npv=sv]'); pg.wait_for_timeout(100)
        chk(pg.evaluate("pvBy(penR(1).d.origin)?.k") == "IC", f'{vw} en la hoja también se agrega y queda elegido')
        pg.select_option('[data-pr="1:tank"]', 'T2'); pg.fill('[data-pr="1:k0"]', '50')
        for k, v in {'tempT': '58', 'tempP': '55', 'kgbox': '34', 'desp': '0'}.items(): pg.fill(f'[data-pr="1:{k}"]', v)
        pg.click('[data-pa=save]'); pg.wait_for_timeout(100)
        chk('Guardada' in pg.inner_text('#ps_1') and pg.locator('[data-pa=clear]').count() == 0, f'{vw} después de guardar no está «Quitar guardadas de la lista»')
        # ---------- 7. Empacar sin lote y conectarlo después ----------
        o4 = nueva_orden(pg, 2); pg.evaluate(f"go('empacar:{o4}.1')")
        pg.click('[data-nea=sl]'); pg.wait_for_timeout(100)
        sl = pg.evaluate("PKD.lot"); r = pg.evaluate(f"R_('{sl}')")
        chk(sl == 'SIN-LOTE-2010' and r.get('sl') and r.get('ne'), f'{vw} «Empacar sin lote» crea {sl}')
        chk('Sin lote' in pg.inner_text(f'[data-pk="lot:{sl}"]'), f'{vw} su botón dice «Sin lote»')
        for _ in range(2): pg.fill('#pk_c0', '28'); pg.click('#pkr0 [data-pk="k:0:B"]'); pg.wait_for_timeout(100)
        chk(len(pg.evaluate(f"ST.B['{sl}']")) == 2, f'{vw} se empacan sin lote')
        chk(sl in ' '.join(pg.evaluate(f"f6Lots(ST.OR.find(o=>o.id=={o4}))")), f'{vw} la hoja de empaque lo muestra')
        pg.evaluate("go('recepcion')"); chk('Hieleras sin lote' in pg.inner_text('#app'), f'{vw} Entrada lo marca')
        pg.click(f'.neb [data-go="lote:{sl}"]'); pg.wait_for_timeout(80)
        chk(pg.locator('#nejoin #nj_l').count() == 1, f'{vw} su página tiene «Conectar con su entrada»')
        pg.select_option('#nj_l', 'WLRCOV112'); pg.click(f'[data-nej="{sl}"]'); pg.wait_for_timeout(100)
        chk(not pg.evaluate(f"!!R_('{sl}')") and len(pg.evaluate("ST.B['WLRCOV112']")) == 2 and pg.evaluate(f"f6Lots(ST.OR.find(o=>o.id=={o4}))") == ['WLRCOV112'], f'{vw} al conectar, las hieleras pasan al lote y el provisional desaparece')
        # ---------- 8. Modo piso: sin «Eliminar orden» ----------
        o5 = pg.evaluate("(()=>{const o={id:uidN(),etd:'2026-10-22',lines:[],sh:{}};ST.OR.push(o);save();return o.id})()")
        pg.evaluate(f"go('orden:{o5}')"); chk(pg.locator('[data-oa=dco]').count() == 1, f'{vw} en la vista completa sí está «Eliminar orden»')
        pg.evaluate(f"setPiso(true);go('orden:{o5}')"); chk(pg.locator('[data-oa=dco]').count() == 0, f'{vw} en Modo piso no')
        pg.evaluate("setPiso(false)")
        pg.close()
    # ---------- 9. Teclado de la app en celular: completar y cerrar ----------
    pg = b.new_page(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); pg.on('pageerror', lambda e: errs.append(str(e)))
    entrar(pg, kp='1'); o6 = nueva_orden(pg, 2); pg.evaluate(f"go('empacar:{o6}.1')"); pg.click('[data-pk="lot:WLRCO051026A"]'); pg.wait_for_timeout(100)
    for _ in range(2):
        for d in ['2', '9']: pg.click(f'#kpad [data-kp="d:{d}"]')
        pg.click('#kpad [data-kp="k:B"]'); pg.wait_for_timeout(120)
    n = len(pg.evaluate(f"ordBoxes(ST.OR.find(o=>o.id=={o6}))"))
    chk(n == 2, f'celular con teclado de la app: las 2 hieleras quedan completadas ({n})')
    chk(pg.locator('#kpad').count() == 0 and pg.locator('#pkfin').is_visible(), 'al terminar se cierra el teclado y se ve «Listo»')
    pg.close()
    # ---------- 10. Ventana para instalar la app ----------
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg)
    pg.evaluate("window.__p=0;const e=new Event('beforeinstallprompt');e.prompt=()=>{window.__p++;return Promise.resolve()};e.userChoice=Promise.resolve({outcome:'accepted'});window.dispatchEvent(e)")
    chk(pg.locator('#inst').is_visible() and 'Instala la app PROPESA' in pg.inner_text('#inst'), 'al entrar ofrece instalar la app')
    pg.click('[data-inst=si]'); pg.wait_for_timeout(80); chk(pg.evaluate("window.__p") == 1 and pg.locator('#inst').count() == 0, '«Instalar» abre la instalación del teléfono')
    pg.evaluate("const e=new Event('beforeinstallprompt');e.prompt=()=>Promise.resolve();e.userChoice=Promise.resolve({outcome:'dismissed'});window.dispatchEvent(e)")
    pg.click('[data-inst=no]'); pg.evaluate("const e=new Event('beforeinstallprompt');window.dispatchEvent(e)")
    chk(pg.locator('#inst').count() == 0, '«Ahora no»: no vuelve a salir en 7 días')
    pg.evaluate("localStorage.removeItem('propesa-inst');instShow(true)"); chk('Agregar a inicio' in pg.inner_text('#inst'), 'en iPhone dice cómo agregarla a inicio')
    pg.close()
    # ---------- 11. Encargado de piso: no agrega proveedores; sí empaca sin lote ----------
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, 'piso@propesa.mx', 'piso123', '1')
    pg.evaluate("PEN=null;go('pent')"); chk('Agregar proveedor' not in pg.inner_text('[data-pr="1:origin"]'), 'piso: no ve «+ Agregar proveedor…»')
    o7 = nueva_orden(pg, 2); pg.evaluate(f"PE.lot=null;go('pemp:{o7}.1')"); pg.wait_for_timeout(80)
    chk(pg.locator('[data-nea=sl]').count() == 1, 'piso: puede «Empacar sin lote»')
    pg.close(); b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
