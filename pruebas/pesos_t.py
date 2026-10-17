"""Peso estándar de la hielera (v1.8.7): uno solo, en Administración, solo el Administrador lo cambia.
Embarque lo muestra sin casillas; Órdenes y PDF lo usan; los embarques cerrados conservan su peso; se guarda en el respaldo.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/pesos_t.py"""
from playwright.sync_api import sync_playwright
import os, sys, json
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
        # sin cambiar nada: los de siempre
        chk(pg.evaluate("[KGN,KGB]") == [16, 19.6], f'{vw} sin configurar: 16 kg netos y 19.6 kg brutos por hielera')
        i = pg.evaluate("ST.P.findIndex(p=>!p.closed&&p.h>0)"); h = pg.evaluate(f"ST.P[{i}].h")
        pg.evaluate(f"go('emb:{i}')"); card = pg.locator('#emb_peso')
        chk(card.locator('input').count() == 0 and 'Se calcula solo' in card.inner_text() and 'Tarimas' not in card.inner_text(), f'{vw} Embarque: el peso se explica y no tiene casillas')
        chk(card.locator('[data-go="admin:pesos"]').count() == 1, f'{vw} el Administrador ve «Cambiar el peso estándar ›»')
        card.locator('[data-go="admin:pesos"]').click(); pg.wait_for_timeout(300)
        chk(pg.evaluate("V.v") == 'admin' and pg.evaluate("document.activeElement.id") == 'pw_h', f'{vw} lleva a Administración → «Peso de la hielera», en el primer campo')
        # validación
        pg.fill('#pw_p', '0'); pg.click('[data-a=pw]'); chk('mayor que 0' in pg.inner_text('#pw_m') and pg.evaluate("!ST.W"), f'{vw} producto en 0 no se guarda')
        pg.fill('#pw_p', 'abc' if False else ''); pg.click('[data-a=pw]'); chk('Revisa' in pg.inner_text('#pw_m'), f'{vw} un campo vacío no se guarda')
        # cerrar un embarque antes de cambiar el estándar: conserva su peso
        j = pg.evaluate(f"ST.P.findIndex((p,k)=>k!={i}&&p.h>0)")
        g_cerrado = None
        if j >= 0:
            pg.evaluate(f"ST.P[{j}].closed=true;save()"); g_cerrado = pg.evaluate(f"gross(ST.P[{j}])")
        # cambiar: producto 16.5, gel 1.2 → 16.5 netos, 1.4+1.2+16.5+0.7 = 19.8 brutos
        pg.evaluate("go('admin:pesos')"); pg.wait_for_timeout(200)
        pg.fill('#pw_p', '16.5'); pg.fill('#pw_g', '1.2')
        chk(pg.inner_text('#pw_tt') == '19.8' and pg.inner_text('#pw_n') == '16.5', f'{vw} el total se ve al escribir: {pg.inner_text("#pw_tt")}')
        pg.click('[data-a=pw]')
        chk(pg.evaluate("ST.W") == {'h': 1.4, 'g': 1.2, 't': 9.9, 'p': 16.5, 'c': 0.7} and pg.evaluate("[KGN,KGB]") == [16.5, 19.8], f'{vw} se guarda: 16.5 kg netos y 19.8 kg brutos')
        chk(abs(pg.evaluate(f"gross(ST.P[{i}])") - round(19.8 * h, 1)) < 0.05, f'{vw} el embarque abierto se recalcula ({h} hieleras × 19.8)')
        if j >= 0: chk(pg.evaluate(f"gross(ST.P[{j}])") == g_cerrado, f'{vw} el embarque cerrado conserva su peso ({g_cerrado} kg)')
        pg.evaluate(f"go('emb:{i}')"); chk(pg.locator('#emb_peso').count() == 1 and f'{round(19.8 * h, 1):.1f}' in pg.inner_text('#emb_peso') and pg.locator('.alk:has-text("Peso bruto")').count() == 0, f'{vw} el embarque muestra 19.8 kg y no hay aviso de discrepancia')
        # embarque cerrado: si después cambia el estándar, conserva el peso con el que se cerró
        g198 = pg.evaluate(f"gross(ST.P[{i}])"); pg.evaluate(f"ST.P[{i}].closed=true;save();go('admin:pesos')"); pg.wait_for_timeout(200)
        pg.fill('#pw_p', '16'); pg.fill('#pw_g', '1.5'); pg.click('[data-a=pw]')
        chk(pg.evaluate("KGB") == 19.6 and pg.evaluate(f"gross(ST.P[{i}])") == g198, f'{vw} embarque cerrado conserva su peso ({g198} kg) aunque el estándar vuelva a 19.6')
        pg.evaluate(f"go('emb:{i}')"); chk('Pesos con los que se cerró' in pg.inner_text('#emb_peso') and pg.locator('#emb_peso [data-go="admin:pesos"]').count() == 0, f'{vw} cerrado: dice que son los pesos del cierre')
        pg.evaluate(f"ST.P[{i}].closed=false;save();render()"); chk(pg.locator('[data-a^="pwfix:"]').count() == 1, f'{vw} al reabrirlo ofrece «Usar el peso estándar»')
        pg.click('[data-a^="pwfix:"]'); chk(abs(pg.evaluate(f"gross(ST.P[{i}])") - round(19.6 * h, 1)) < 0.05 and pg.locator('[data-a^="pwfix:"]').count() == 0, f'{vw} y queda con el estándar actual')
        pg.evaluate("go('admin:pesos')"); pg.wait_for_timeout(200); pg.fill('#pw_p', '16.5'); pg.fill('#pw_g', '1.2'); pg.click('[data-a=pw]')
        o = pg.evaluate("ST.OR.find(o=>o.lines.length).id"); pg.evaluate(f"go('orden:{o}')")
        chk('producto 16.5 kg' in pg.inner_text('#app'), f'{vw} Órdenes (línea de antes) usa el nuevo producto por omisión')
        # se guarda en el respaldo
        bk = json.loads(pg.evaluate("JSON.stringify(cleanST(JSON.parse(JSON.stringify(ST))))"))
        chk(bk.get('W') == {'h': 1.4, 'g': 1.2, 't': 9.9, 'p': 16.5, 'c': 0.7}, f'{vw} el respaldo lleva el peso de la hielera')
        chk(pg.evaluate("(()=>{const e=encodeST();return JSON.stringify(e.get('W/pesos')[1])})()") == json.dumps({'h': 1.4, 'g': 1.2, 't': 9.9, 'p': 16.5, 'c': 0.7}, separators=(',', ':')), f'{vw} se comparte con los demás equipos (registro W/pesos)')
        chk(pg.evaluate("decodeST(new Map([...encodeST()].map(([k,v])=>[k,v[1]]))).W.p") == 16.5, f'{vw} y otro equipo lo lee igual')
        pg.close()
    # Encargado de piso: ve el peso, no lo cambia
    pg = b.new_page(viewport={'width': 1180, 'height': 820}); pg.on('pageerror', lambda e: errs.append(str(e)))
    entrar(pg, 'piso@propesa.mx', 'piso123')
    pg.evaluate("setPiso(false);go('emb:'+ST.P.findIndex(p=>p.h>0))"); pg.wait_for_timeout(150)
    chk(pg.locator('#emb_peso').count() == 1 and pg.locator('#emb_peso input').count() == 0 and pg.locator('[data-go="admin:pesos"]').count() == 0, 'Encargado de piso ve el peso sin poder cambiarlo')
    pg.evaluate("(()=>{const b=document.createElement('button');b.dataset.a='pw';document.getElementById('app').appendChild(b);b.click()})()")
    chk(pg.evaluate("!ST.W"), 'ni forzando el botón puede guardar el peso')
    pg.close(); b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
