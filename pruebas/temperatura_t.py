"""Temperatura conectada con Entrada y Mortalidad final aparte (v1.8.4).
- Las temperaturas de cada entrada salen solas en Temperatura, en el tablero de tanques y en el lote; se actualizan al
  editar o eliminar el lote. Las lecturas manuales siguen; filtro por tanque; «Registrar» preselecciona el tanque.
- Mortalidad final ya no es el paso 5: está en «Revisión», el Panel no manda ahí y Embarque no tiene «Siguiente».
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/temperatura_t.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recep import recibir
from playwright.sync_api import sync_playwright
import os, sys
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
PLEG = "Object.setPrototypeOf(FOLD,new Proxy({},{get:(t,k)=>typeof k=='string'?true:undefined}));render()"  # v1.35.0: hoja de empaque, peso del embarque y temperatura del lote van plegados; aquí quedan abiertos
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

import datetime as _dt
_y=_dt.date.today()-_dt.timedelta(days=1);AYER=_y.isoformat();AYER_MX=_y.strftime('%d/%m/%Y')  # antes 16/10/2026 fijo: salía de la lista de 7 días

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('dialog', lambda d: d.accept())
        pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0")}', seed); pg.reload()
        pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'admin123'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200); pg.evaluate(PLEG)
        # --- nueva entrada en T6 con temperaturas
        pg.evaluate("FOLD['ent-tq']=true");  recibir(pg, 'wlrtemp1', pv='1', kz=[0, '200'], tank='T6', fecha=AYER, hora='07:40', tt='57.3')
        chk(pg.evaluate("!!R_('WLRTEMP1')") and pg.evaluate("ST.T.length") == 0, f'{vw} se guarda la entrada (sin copiar nada a las lecturas)')
        # Temperatura la muestra sola
        pg.evaluate("go('temperatura')"); tx = pg.inner_text('#app')
        chk('Recepción · WLRTEMP1' in tx and '57.3 °F' in tx and 'mín 57 · máx 60 °F' in tx and AYER_MX in tx and '07:40' in tx, f'{vw} Temperatura muestra la de la entrada (agua, producto, fecha y hora, lote)')
        chk(pg.locator('tr.tqent [data-tqdel]').count() == 0, f'{vw} la de la entrada no se elimina desde Temperatura (se corrige en el lote)')
        pg.click('button.lnk:has-text("Recepción · WLRTEMP1")'); chk(pg.evaluate("V.v") == 'lote' and pg.evaluate("V.id") == 'WLRTEMP1', f'{vw} «Entrada · lote» abre el lote')
        # el lote muestra la temperatura de su tanque
        tx = pg.inner_text('#app'); chk('Temperatura de T6' in tx and 'desde la recepción' in tx and 'Recepción de este lote' in tx, f'{vw} el lote muestra la temperatura de su tanque')
        # lectura manual desde el lote: el tanque ya viene elegido
        pg.click('[data-go="temperatura:T6"] >> text=Registrar lectura'); chk(pg.evaluate("V.v") == 'temperatura' and pg.input_value('#tq_t') == 'T6', f'{vw} «+ Registrar lectura» abre Temperatura con el tanque 6 elegido')
        chk(pg.evaluate("TFIL") == 'T6' and pg.locator('[data-tqf="T6"][aria-pressed=true]').count() == 1, f'{vw} y la lista filtrada en el tanque 6')
        pg.fill('#tq_d', AYER); pg.fill('#tq_h', '12:10'); pg.fill('#tq_a', '56.1'); pg.fill('#tq_s', '55.9'); pg.click('[data-a=tq]')
        chk(pg.evaluate("ST.T.length") == 1 and 'Lectura · Ana Torres' in pg.inner_text('#app'), f'{vw} la lectura manual se sigue guardando (para seguimiento)')
        rows = pg.evaluate("[...document.querySelectorAll('#tq_tbl tbody tr')].map(r=>r.innerText)")
        chk(len(rows) >= 2 and '12:10' in rows[0] and 'WLRTEMP1' in rows[1], f'{vw} lista en orden: la más reciente arriba')
        pg.click('[data-tqf="T1"]'); chk('WLRTEMP1' not in pg.inner_text('#tq_tbl tbody'), f'{vw} filtro por tanque: en el tanque 1 no sale la del 6')
        pg.click('[data-tqf=""]'); chk('WLRTEMP1' in pg.inner_text('#tq_tbl tbody'), f'{vw} «Todos» las vuelve a mostrar')
        # tablero de tanques: la última del T6 (la lectura de las 12:10)
        pg.evaluate("TQSEL='T6';FOLD['ent-tq']=true;go('recepcion')"); tq = pg.inner_text('.tqd')
        chk('56.1' in tq and '12:10' in tq, f'{vw} el tablero del tanque 6 muestra la última temperatura (lectura 12:10): {tq[-120:]!r}')
        pg.evaluate("ST.T=[];save();render()"); tq = pg.inner_text('.tqd')
        chk('57.3' in tq and 'recepción WLRTEMP1' in tq, f'{vw} sin lecturas, el tablero muestra la de la recepción')
        chk('Flotante 57.3°' in pg.inner_text('[data-tq="T6"]'), f'{vw} y el mapa del tanque 6 también')
        # editar el lote cambia la temperatura sola
        pg.evaluate("go('lote:WLRTEMP1')"); pg.click('[data-a=el]'); pg.fill('#rt_ttT6', '55.5'); pg.click('[data-rt=sv]'); pg.wait_for_timeout(100)
        pg.evaluate("go('temperatura')"); chk('55.5 °F' in pg.inner_text('#tq_tbl tbody') and '57.3 °F' not in pg.inner_text('#tq_tbl tbody'), f'{vw} al editar el lote, Temperatura se actualiza sola')
        # eliminar el lote la quita
        pg.evaluate("go('lote:WLRTEMP1')"); pg.click('[data-a=dl]'); pg.click('[data-a=dl2]'); pg.wait_for_timeout(100)
        pg.evaluate("go('temperatura')"); chk('WLRTEMP1' not in pg.inner_text('#app'), f'{vw} al eliminar el lote, su temperatura se quita')
        # --- Mortalidad final aparte
        side = pg.evaluate("[...document.querySelectorAll('.sb .fs em')].map(e=>e.textContent).join(',')")
        chk(side == '', f'{vw} el menú ya no lleva números (v1.33.0, la app no obliga un orden): {side!r}')
        chk(pg.locator('.sb h4:has-text("Revisión") + [data-go=cierre]').count() == 1 and 'calcula sola' not in pg.inner_text('.sb [data-go=cierre]').lower(), f'{vw} Mortalidad final está aparte, en «Revisión», y dice que se calcula sola')
        pg.evaluate("go('cierre')"); chk('Revisión aparte' not in pg.inner_text('.pgh') and 'No es un paso' not in pg.inner_text('.pgh') and pg.locator('.pgh [data-go]').count() == 0, f'{vw} su pantalla dice «Revisión aparte» y no empuja a otro paso')
        chk(pg.locator('[data-fin]').count() >= 1, f'{vw} ahí se sigue pudiendo capturar el conteo final')
        pg.evaluate("go('embarques')"); chk('mortalidad' not in pg.inner_text('.pgh').lower(), f'{vw} Embarque ya no tiene «Siguiente: mortalidad final»')
        pg.evaluate("ST.OR.forEach(o=>o.lines.forEach(l=>{}));ST.P.forEach(p=>p.closed=true);save();go('inicio')")
        chk(pg.evaluate("nxt()[1]") != 'cierre' and 'mortalidad' not in pg.inner_text('.pgh').lower(), f'{vw} el Panel no manda a Mortalidad final: {pg.evaluate("nxt()[2]")}')
        chk('Paso' not in pg.evaluate("guide(4,'x','y','','')") and '<h1>x</h1>' in pg.evaluate("guide(4,'x','y','','')"), f'{vw} el encabezado no dice «Paso N de 4»; solo título y una línea (v1.34.0)')
        pg.close()
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
