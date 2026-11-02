"""v1.29.0 (pedidos del usuario, 1/nov/2026).
1. Crear orden: si antes se dejó «Editar» abierto en otra orden, la orden nueva ya no se queda sin formulario de destino.
2. Hoja de empaque: hora en 12 h con a. m./p. m. (se guarda en 24 h), placas en MAYÚSCULAS al escribir, tanques de origen
   para tocar, y al completarla se cierra en una tarjeta corta («Ver o corregir hoja» la abre otra vez).
3. El aviso de arriba sale debajo de la barra de arriba (no encima).
4. Solo con el teclado: número → letra del color (R, V, B, A) → Enter guarda y pasa a la siguiente hielera (vista completa y Modo piso).
5. Conteo de piezas empacadas (Empaque y la orden).
6. Embarque: «Mover hieleras» se hace en el dibujo del camión (ya no hay otra cuadrícula abajo).
7. Cambiar el consignatario de una línea ya empacada; sus hieleras se van al embarque del nuevo. Atajos desde Empaque y la hoja.
8. (v1.28.1) Si el equipo cerró la memoria (iPad al dormir), se abre otra vez y se guarda: ya no sale «memoria llena» falso.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v129_t.py"""
from playwright.sync_api import sync_playwright
import os, json
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, piso):
    pg.goto(BASE); pg.evaluate('([s,p])=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso",p);localStorage.setItem("propesa-kp","1")}', [seed, piso]); pg.reload()
    pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'admin123'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def nueva(pg, n):
    return pg.evaluate("n=>{const o={id:uidN(),etd:dLoc(),lines:[{id:1,city:'HKG',cons:0,boxes:n,kp:16,tar:0,cc:0}],sh:{}};ST.OR.push(o);syncShip(o,'HKG',0);save();return o.id}", n)
def toast(pg): return pg.inner_text('#toast') if pg.locator('#toast').count() else ''
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------- 1.28.1: la memoria del equipo con la conexión cerrada (iPad al dormir) ----------
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto(BASE); pg.wait_for_timeout(300)
    r = pg.evaluate("async()=>{try{await idbPut('prueba',1);const db=await idb();db.close();await idbPut('prueba',2);return 'ok '+await idbGet('prueba')}catch(e){return 'error: '+e.message}}")
    chk(r == 'ok 2', f'v1.28.1: con la conexión cerrada se abre otra y sí se guarda ({r})')
    pg.close()
    # ---------- 1. crear orden después de dejar «Editar» abierto en otra ----------
    pg = b.new_page(viewport={'width': 1280, 'height': 900}); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, '0')
    old = pg.evaluate("ST.OR.find(o=>o.lines.length).id"); pg.evaluate(f"go('orden:{old}')"); pg.click('[data-oa^="el:"]')
    pg.evaluate("go('ordenes')"); pg.click('[data-oa=new]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("V.v") == 'orden' and pg.locator('#ol_city').count() == 1 and pg.locator('#ol_n').count() == 1, 'orden nueva: sale el formulario de destino aunque se dejó «Editar» abierto en otra')
    pg.evaluate("OA.ed=1;render()"); chk(pg.locator('#ol_city').count() == 1, 'un «Editar» de otra orden guardado en el equipo no esconde el formulario')
    chk('Abrir o editar' in (pg.evaluate("go('ordenes')") or pg.inner_text('.ordl')), 'en Órdenes el botón dice «Abrir o editar»')
    pg.close()

    for piso, vw in [('0', (1280, 900)), ('0', (390, 844)), ('1', (820, 1180))]:
        tag = f'{"piso" if piso == "1" else "completa"} {vw}'
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, piso)
        oid = nueva(pg, 3); O = f"ST.OR.find(o=>o.id=={oid})"; L = f"{O}.lines[0]"
        if piso == '1': pg.evaluate(f"PE.lot=openLots()[0];go('pemp:{oid}.1')")
        else: pg.evaluate(f"go('empacar:{oid}.1')"); pg.evaluate("PKD.lot=openLots()[0];render()")
        pg.wait_for_timeout(150)
        # ---------- 4. solo con el teclado ----------
        chk(pg.evaluate("JSON.stringify(kpLet())") == json.dumps({"r": "R", "v": "V", "b": "B", "a": "A"}, separators=(',', ':')), f'{tag} letras: R Rojo, V Verde, B Blanco, A Amarillo')
        pg.click('[data-kps="1"]' if piso == '1' else '#pk_c0'); pg.wait_for_timeout(80)
        pg.keyboard.type('25'); pg.keyboard.press('r'); pg.wait_for_timeout(50)
        chk(pg.evaluate("kpCat()") == 'R' and pg.get_attribute('#kpad [data-kp="k:R"]', 'aria-pressed') == 'true' and pg.evaluate(f"ordPk({O},{L}).length") == 0, f'{tag} la letra elige el color sin guardar todavía')
        pg.keyboard.press('v'); chk(pg.evaluate("kpCat()") == 'V', f'{tag} otra letra cambia el color')
        pg.keyboard.press('r'); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
        chk(pg.evaluate(f"JSON.stringify(ordPk({O},{L}).map(x=>[x.b.c,x.b.k]))") == '[[25,"R"]]', f'{tag} Enter guarda la hielera 1 con 25 Rojo')
        pg.keyboard.type('30'); pg.keyboard.press('v'); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
        chk(pg.evaluate(f"ordPk({O},{L}).length") == 2, f'{tag} sin tocar la pantalla pasa a la siguiente y guarda la hielera 2')
        pg.keyboard.type('5'); pg.keyboard.press('Enter'); pg.wait_for_timeout(150)
        chk(pg.evaluate(f"ordPk({O},{L}).length") == 2, f'{tag} Enter sin color no guarda')
        pg.keyboard.press('x'); chk(pg.evaluate("kpCat()") in ('', None), f'{tag} una letra que no es color no hace nada')
        # ---------- 5. conteo de piezas ----------
        chk('55' in pg.inner_text('#pkpz') and 'piezas empacadas' in pg.inner_text('#pkpz'), f'{tag} cuenta 55 piezas empacadas: {pg.inner_text("#pkpz")}')
        # ---------- 3. aviso debajo de la barra de arriba ----------
        pg.evaluate("toast('✔ prueba')"); top, hb = pg.evaluate("[document.getElementById('toast').getBoundingClientRect().top,document.querySelector('main').getBoundingClientRect().top]")
        chk(top >= hb, f'{tag} el aviso sale debajo de la barra de arriba ({top} ≥ {hb})')
        pg.keyboard.press('Backspace'); pg.keyboard.type('12'); pg.keyboard.press('b'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
        chk(pg.evaluate(f"ordPk({O},{L}).length") == 3, f'{tag} la tercera completa la línea')
        # ---------- 2. hoja de empaque ----------
        chk(pg.locator('#f6card #f6_hi_ap').count() == 1, f'{tag} hora inicial con a. m./p. m.')
        pg.fill('#f6_hi', ''); pg.type('#f6_hi', '730'); chk(pg.input_value('#f6_hi') == '7:30', f'{tag} «730» se escribe 7:30')
        pg.select_option('#f6_hi_ap', 'pm'); pg.fill('#f6_hf', ''); pg.type('#f6_hf', '1215'); pg.select_option('#f6_hf_ap', 'am')
        chk(pg.input_value('#f6_hf') == '12:15', f'{tag} «1215» se escribe 12:15')
        pg.fill('#f6_pl', ''); pg.type('#f6_pl', 'zry68f3'); chk(pg.input_value('#f6_pl') == 'ZRY68F3', f'{tag} las placas se ponen en mayúsculas al escribir')
        pg.fill('#f6_ch', 'Juan P.'); pg.fill('#f6_tel', '646-294-1282'); pg.fill('#f6_tp', '48 °F')
        if not pg.input_value('#f6_tq'): pg.fill('#f6_tq', 'T1 - 50 °F')
        chk(pg.locator('#f6_to .f6tk').count() >= 6 and pg.locator('#f6_to input').count() == 0, f'{tag} tanques de origen: botones para tocar, no casilla')
        t0 = pg.evaluate(f"{O}.f.to||''")
        pg.click(f'[data-f6="to:{oid}:T4"]'); pg.wait_for_timeout(100)
        chk('T4' in pg.evaluate(f"{O}.f.to") and pg.get_attribute(f'[data-f6="to:{oid}:T4"]', 'aria-pressed') == 'true', f'{tag} tocar T4 lo agrega: {pg.evaluate(O + ".f.to")}')
        pg.click(f'[data-f6="to:{oid}:T4"]'); pg.wait_for_timeout(100)
        chk('T4' not in pg.evaluate(f"{O}.f.to"), f'{tag} tocarlo otra vez lo quita')
        if not t0: pg.click(f'[data-f6="to:{oid}:T1"]'); pg.wait_for_timeout(100)
        f = pg.evaluate(f"{O}.f"); chk(f.get('hi') == '19:30' and f.get('hf') == '00:15' and f.get('pl') == 'ZRY68F3', f'{tag} se guarda en 24 h: {f.get("hi")} / {f.get("hf")}')
        chk(pg.locator('#f6card.f6c').count() == 0, f'{tag} con datos faltantes la hoja sigue abierta')
        pg.click(f'[data-f6="ev:{oid}:S"]'); pg.wait_for_timeout(700)
        chk(pg.locator('#f6card.f6c').count() == 1 and pg.locator('#f6_pl').count() == 0, f'{tag} al completarla la hoja se cierra en una tarjeta corta')
        chk('7:30 p. m. a 12:15 a. m.' in pg.inner_text('#f6card'), f'{tag} la tarjeta dice las horas en 12 h: {pg.inner_text("#f6card")[:120]}')
        pg.evaluate("render()"); chk(pg.locator('#f6card.f6in').count() == 0, f'{tag} la animación sale una sola vez')
        pg.click(f'[data-f6="op:{oid}"]'); pg.wait_for_timeout(150)
        chk(pg.locator('#f6_pl').count() == 1 and pg.input_value('#f6_hi') == '7:30' and pg.input_value('#f6_hi_ap') == 'pm', f'{tag} «Ver o corregir hoja» la abre con lo guardado')
        chk('7:30 p. m.' in pg.evaluate(f"f6Txt({O})"), f'{tag} el texto del correo/PDF lleva 12 h')
        pg.close()

    # ---------- 6. mover hieleras dentro del camión ----------
    for vw in [(1280, 900), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, '0')
        pg.evaluate("()=>{[30,12].forEach((h,n)=>{const i=newShip();Object.assign(ST.P[i],{n:'HKG · PRUEBA'+n+' · 20/10',h,col:['#0583c3','#e5484d'][n]})});save();go('embarques')}"); pg.wait_for_timeout(100)
        chk(pg.locator('#tk_1 svg').count() == 1 and pg.locator('#tk_1 .tcel').count() == 0, f'{vw} sin «Mover hieleras» se ve el dibujo')
        pg.click('#tk_1 [data-ta^="ed:"]'); pg.wait_for_timeout(80)
        chk(pg.locator('#tk_1 .ttk .tcel').count() == 10 and pg.locator('#tk_1 svg').count() == 0 and pg.locator('#tk_1 .ttk .ttb').count() == 1, f'{vw} con «Mover hieleras» el camión mismo tiene las 10 celdas (cola y cabina)')
        pg.click('#tk_1 [data-tc$=":4"]'); y_tr, y_sel = pg.evaluate("[document.querySelector('#tk_1 .ttk').getBoundingClientRect().bottom,document.querySelector('#tk_1 .tsel').getBoundingClientRect().top]")
        chk(0 <= y_sel - y_tr < 40, f'{vw} lo de la celda elegida sale pegado al camión')
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{vw} sin scroll de lado')
        pg.close()

    # ---------- 7. cambiar consignatario de una línea ya empacada ----------
    pg = b.new_page(viewport={'width': 1280, 'height': 900}); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, '0')
    oid = nueva(pg, 4); O = f"ST.OR.find(o=>o.id=={oid})"; L = f"{O}.lines[0]"
    pg.evaluate(f"go('empacar:{oid}.1')"); pg.evaluate("PKD.lot=openLots()[0];render()"); pg.wait_for_timeout(100)
    pg.click('#pk_c0')
    for n, l in [('25', 'r'), ('30', 'v')]:
        pg.keyboard.type(n); pg.keyboard.press(l); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    nP = pg.evaluate("ST.P.length"); nc = pg.evaluate("consFor('HKG').map(([c,i])=>i).find(i=>i!=0)")
    chk(pg.locator('[data-edl]').count() >= 1, 'Empaque tiene «Cambiar consignatario o editar la orden»')
    pg.click('[data-edl]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("V.v") == 'orden' and pg.locator('#le_cons').count() == 1, 'el atajo abre la orden con la línea en «Editar» y el consignatario para cambiar')
    pg.select_option('#le_cons', str(nc)); pg.click('[data-oa^="sl:"]'); pg.wait_for_timeout(150)
    r = pg.evaluate(f"(()=>{{const o={O},j=o.sh['HKG|{nc}'];return {{cons:o.lines[0].cons,keys:Object.keys(o.sh),d:ordPk(o,o.lines[0]).map(x=>x.b.d),j,n:ST.P.length,bx:boxesOf(j).length,h:ST.P[j].h,nm:ST.P[j].n}}}})()")
    chk(r['cons'] == nc and r['keys'] == [f'HKG|{nc}'] and r['d'] == [r['j'], r['j']] and r['bx'] == 2 and r['h'] == 4 and r['n'] == nP, f'las 2 hieleras empacadas se van al embarque del nuevo y el viejo se quita: {r}')
    chk('ahora va a' in toast(pg), 'avisa a quién va ahora')
    # a uno que ya está en la orden: no
    pg.evaluate(f"{O}.lines.push({{id:2,city:'HKG',cons:0,boxes:1,kp:16,tar:0,cc:0}});syncShip({O},'HKG',0);save();render()")
    pg.click('[data-oa="el:1"]'); pg.select_option('#le_cons', '0'); pg.click('[data-oa="sl:1"]'); pg.wait_for_timeout(100)
    chk('ya está en esta orden' in toast(pg) and pg.evaluate(f"{L}.cons") == nc, 'no deja poner un consignatario que ya está en la orden')
    pg.click('[data-oa=no]')
    chk(pg.locator('#f6card [data-go^="orden:"],#f6card [data-edl]').count() >= 1 or pg.locator('#f6card').count() == 0, 'la hoja tiene «Cambiar ›» junto al consignatario')
    pg.close()
    b.close()
chk(not errs, f'sin errores de JavaScript {errs}')
print('\n' + ('TODO BIEN' if not fails else f'{len(fails)} FALLAS')); raise SystemExit(1 if fails else 0)
