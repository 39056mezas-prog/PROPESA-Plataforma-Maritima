"""v1.15.0 · Color de cada consignatario (pedido del usuario, 23/oct/2026: cada comprador tiene su color, el de su tape).
- Administración → Consignatarios: un selector de color por consignatario, solo el Administrador lo cambia.
- Al cambiarlo, sus embarques abiertos toman ese color (Embarque, camión, PDF); los cerrados conservan el suyo.
- Los embarques nuevos de ese consignatario nacen con su color.
- Se comparte entre equipos (WN / encodeST / decodeST: registro C/colores) y sobrevive a un respaldo (cleanST); colores malos se ignoran.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/colores_t.py"""
from playwright.sync_api import sync_playwright
import os
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em='admin@propesa.mx', pw='admin123'):
    pg.goto(BASE); pg.evaluate('([s])=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0");localStorage.setItem("propesa-kp","0")}', [seed]); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def pick(pg, i, v):  # lo mismo que hace el selector de color al cerrarse
    pg.evaluate("([i,v])=>{const x=document.querySelector(`[data-cc=\"${i}\"]`);x.value=v;x.dispatchEvent(new Event('change',{bubbles:true}))}", [i, v]); pg.wait_for_timeout(80)

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1440, 900), (820, 1180), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg)
        # dos embarques abiertos de YISHUNHAI (cons 0) y XIAMEN (cons 1), y uno cerrado de YISHUNHAI
        ix = pg.evaluate("""(()=>{const o={id:uidN(),etd:'2026-10-20',lines:[{id:1,city:'PVG',cons:0,boxes:5},{id:2,city:'PVG',cons:1,boxes:2}],sh:{}};ST.OR.push(o);syncShip(o,'PVG',0);syncShip(o,'PVG',1);
          const c={id:uidN(),etd:'2026-10-10',lines:[{id:1,city:'SZX',cons:0,boxes:3}],sh:{}};ST.OR.push(c);syncShip(c,'SZX',0);const k=c.sh['SZX|0'];ST.P[k].closed=true;ST.P[k].col='#123456';
          save();return{a:o.sh['PVG|0'],b:o.sh['PVG|1'],c:k}})()""")
        col_b = pg.evaluate(f"ST.P[{ix['b']}].col")
        pg.evaluate("go('admin:cat')"); pg.wait_for_timeout(80)
        chk(pg.locator('#conss').count() == 1, f'{vw} Administración tiene la tarjeta Consignatarios')
        chk(pg.locator('#conss [data-cc]').count() == pg.evaluate('CONS.length'), f'{vw} un selector de color por consignatario')
        chk(pg.inner_text('#conss').count('Sin elegir') == pg.evaluate('CONS.length'), f'{vw} sin colores elegidos dice «Sin elegir»')
        bx = pg.locator('#conss [data-cc="0"]').bounding_box()
        chk(bx and bx['width'] >= 44 and bx['height'] >= 44, f'{vw} el selector mide 44 px o más: {bx}')
        chk(pg.locator('#conss [data-cc="0"]').get_attribute('aria-label') == 'Color de YISHUNHAI', f'{vw} el selector dice de quién es')
        chk(not pg.evaluate("document.documentElement.scrollWidth>innerWidth+1"), f'{vw} sin scroll de lado')
        pick(pg, 0, '#E03131')
        chk(pg.evaluate("ST.CC") == {'0': '#e03131'}, f'{vw} se guarda el color: {pg.evaluate("ST.CC")}')
        chk(pg.evaluate(f"ST.P[{ix['a']}].col") == '#e03131', f'{vw} el embarque abierto de YISHUNHAI toma su color')
        chk(pg.evaluate(f"ST.P[{ix['b']}].col") == col_b, f'{vw} el de XIAMEN no cambia')
        chk(pg.evaluate(f"ST.P[{ix['c']}].col") == '#123456', f'{vw} el embarque cerrado conserva su color')
        chk('Color de YISHUNHAI guardado' in pg.inner_text('#toast'), f'{vw} avisa que se guardó')
        chk(pg.input_value('#conss [data-cc="0"]') == '#e03131' and pg.inner_text('#conss').count('Sin elegir') == pg.evaluate('CONS.length') - 1, f'{vw} la tarjeta muestra el color elegido')
        # embarque nuevo de YISHUNHAI nace con su color
        nc = pg.evaluate("(()=>{const o={id:uidN(),etd:'2026-10-22',lines:[{id:1,city:'HKG',cons:0,boxes:1}],sh:{}};ST.OR.push(o);syncShip(o,'HKG',0);return ST.P[o.sh['HKG|0']].col})()")
        chk(nc == '#e03131', f'{vw} un embarque nuevo del consignatario nace con su color: {nc}')
        # se ve en Embarque
        pg.evaluate("go('embarques')"); pg.wait_for_timeout(80)
        chk(pg.evaluate("[...document.querySelectorAll('.bp')].some(e=>e.style.getPropertyValue('--c')=='#e03131')"), f'{vw} Embarque pinta la tarjeta con ese color')
        # compartir: encode → decode y valores malos
        rt = pg.evaluate("(()=>{const m=encodeST(),c=m.get('C/colores');return{c:c&&c[1],d:decodeST(new Map([...m].map(([k,v])=>[k,v[1]]))).CC,bad:WN.C({0:'red',1:'#00ff00',99:'#111111',x:'#222222','__proto__':'#333333'})}})()")
        chk(rt['c'] == {'0': '#e03131'} and rt['d'] == {'0': '#e03131'}, f'{vw} viaja como C/colores y regresa igual: {rt["c"]} {rt["d"]}')
        chk(rt['bad'] == {'1': '#00ff00'}, f'{vw} colores o consignatarios que no existen se ignoran: {rt["bad"]}')
        cl = pg.evaluate("[cleanST({...JSON.parse(JSON.stringify(ST)),CC:{0:'#abcdef',2:'javascript:x'}}).CC, 'CC' in cleanST({...JSON.parse(JSON.stringify(ST)),CC:null})]")
        chk(cl == [{'0': '#abcdef'}, False], f'{vw} el respaldo conserva los colores buenos: {cl}')
        pg.close()
    # Piso no puede cambiarlo
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg)
    pg.evaluate("me={...me,role:'piso'};go('admin:cat')"); pg.wait_for_timeout(80)
    if pg.locator('[data-cc]').count():
        pick(pg, 0, '#000000')
    chk(not pg.evaluate("ST.CC&&ST.CC[0]=='#000000'"), 'otro rol que no sea Administrador no cambia colores')
    chk(not errs, f'sin errores en la página {errs}')
    b.close()
print('FALLAS:', len(fails)) if fails else print('TODO BIEN')
