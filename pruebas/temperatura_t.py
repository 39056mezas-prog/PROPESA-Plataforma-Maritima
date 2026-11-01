"""Temperatura conectada con Entrada y Mortalidad final aparte (v1.8.4).
- Las temperaturas de cada entrada salen solas en Temperatura, en el tablero de tanques y en el lote; se actualizan al
  editar o eliminar el lote. Las lecturas manuales siguen; filtro por tanque; «Registrar» preselecciona el tanque.
- Mortalidad final ya no es el paso 5: está en «Revisión», el Panel no manda ahí y Embarque no tiene «Siguiente».
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/temperatura_t.py"""
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
        # --- nueva entrada en T6 con temperaturas
        pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]')
        pg.fill('#fl', 'wlrtemp1'); pg.select_option('#fo', '1'); pg.select_option('#ft', 'T6'); pg.fill('#fd', '2026-10-16'); pg.fill('#fh', '07:40')
        pg.fill('#ftt', '57.3'); pg.fill('#ftp', '58-60'); pg.fill('#fkb', '18'); pg.fill('#fdes', '0'); pg.fill('#fk1', '200'); pg.click('[data-a=sv]'); pg.wait_for_timeout(150)
        chk(pg.evaluate("!!R_('WLRTEMP1')") and pg.evaluate("ST.T.length") == 0, f'{vw} se guarda la entrada (sin copiar nada a las lecturas)')
        # Temperatura la muestra sola
        pg.evaluate("go('temperatura')"); tx = pg.inner_text('#app')
        chk('Entrada · WLRTEMP1' in tx and '57.3 °F' in tx and '58-60 °F' in tx and '16/10/2026' in tx and '07:40' in tx, f'{vw} Temperatura muestra la de la entrada (agua, producto, fecha y hora, lote)')
        chk(pg.locator('tr.tqent [data-tqdel]').count() == 0, f'{vw} la de la entrada no se elimina desde Temperatura (se corrige en el lote)')
        pg.click('button.lnk:has-text("Entrada · WLRTEMP1")'); chk(pg.evaluate("V.v") == 'lote' and pg.evaluate("V.id") == 'WLRTEMP1', f'{vw} «Entrada · lote» abre el lote')
        # el lote muestra la temperatura de su tanque
        tx = pg.inner_text('#app'); chk('Temperatura del tanque 6 desde la entrada' in tx and 'Entrada de este lote' in tx, f'{vw} el lote muestra la temperatura de su tanque')
        # lectura manual desde el lote: el tanque ya viene elegido
        pg.click('[data-go="temperatura:T6"] >> text=Registrar lectura'); chk(pg.evaluate("V.v") == 'temperatura' and pg.input_value('#tq_t') == 'T6', f'{vw} «+ Registrar lectura» abre Temperatura con el tanque 6 elegido')
        chk(pg.evaluate("TFIL") == 'T6' and pg.locator('[data-tqf="T6"][aria-pressed=true]').count() == 1, f'{vw} y la lista filtrada en el tanque 6')
        pg.fill('#tq_d', '2026-10-16'); pg.fill('#tq_h', '12:10'); pg.fill('#tq_a', '56.1'); pg.fill('#tq_s', '55.9'); pg.click('[data-a=tq]')
        chk(pg.evaluate("ST.T.length") == 1 and 'Lectura · Ana Torres' in pg.inner_text('#app'), f'{vw} la lectura manual se sigue guardando (para seguimiento)')
        rows = pg.evaluate("[...document.querySelectorAll('#app tbody tr')].map(r=>r.innerText)")
        chk(len(rows) >= 2 and '12:10' in rows[0] and 'WLRTEMP1' in rows[1], f'{vw} lista en orden: la más reciente arriba')
        pg.click('[data-tqf="T1"]'); chk('WLRTEMP1' not in pg.inner_text('#app tbody'), f'{vw} filtro por tanque: en el tanque 1 no sale la del 6')
        pg.click('[data-tqf=""]'); chk('WLRTEMP1' in pg.inner_text('#app tbody'), f'{vw} «Todos» las vuelve a mostrar')
        # tablero de tanques: la última del T6 (la lectura de las 12:10)
        pg.evaluate("TQSEL='T6';go('recepcion')"); tq = pg.inner_text('.tqd')
        chk('56.1' in tq and '12:10' in tq, f'{vw} el tablero del tanque 6 muestra la última temperatura (lectura 12:10): {tq[-120:]!r}')
        pg.evaluate("ST.T=[];save();render()"); tq = pg.inner_text('.tqd')
        chk('57.3' in tq and 'entrada WLRTEMP1' in tq, f'{vw} sin lecturas, el tablero muestra la de la entrada')
        chk('Flotante 57.3°' in pg.inner_text('[data-tq="T6"]'), f'{vw} y el mapa del tanque 6 también')
        # editar el lote cambia la temperatura sola
        pg.evaluate("go('lote:WLRTEMP1')"); pg.click('[data-a=el]'); pg.fill('#ftt', '55.5'); pg.click('[data-a=sv]'); pg.wait_for_timeout(100)
        pg.evaluate("go('temperatura')"); chk('55.5 °F' in pg.inner_text('#app tbody') and '57.3 °F' not in pg.inner_text('#app tbody'), f'{vw} al editar el lote, Temperatura se actualiza sola')
        # eliminar el lote la quita
        pg.evaluate("go('lote:WLRTEMP1')"); pg.click('[data-a=dl]'); pg.click('[data-a=dl2]'); pg.wait_for_timeout(100)
        pg.evaluate("go('temperatura')"); chk('WLRTEMP1' not in pg.inner_text('#app'), f'{vw} al eliminar el lote, su temperatura se quita')
        # --- Mortalidad final aparte
        side = pg.evaluate("[...document.querySelectorAll('.sb .fs em')].map(e=>e.textContent).join(',')")
        chk(side == '1,2,3,4', f'{vw} el menú tiene 4 pasos numerados: {side}')
        chk(pg.locator('.sb h4:has-text("Revisión") + [data-go=cierre]').count() == 1 and 'calcula sola' not in pg.inner_text('.sb [data-go=cierre]').lower(), f'{vw} Mortalidad final está aparte, en «Revisión», y dice que se calcula sola')
        pg.evaluate("go('cierre')"); chk('Revisión aparte' not in pg.inner_text('.gd') and 'No es un paso' not in pg.inner_text('.gd') and pg.locator('.gd [data-go]').count() == 0, f'{vw} su pantalla dice «Revisión aparte» y no empuja a otro paso')
        chk(pg.locator('[data-fin]').count() >= 1, f'{vw} ahí se sigue pudiendo capturar el conteo final')
        pg.evaluate("go('embarques')"); chk('mortalidad' not in pg.inner_text('.gd').lower(), f'{vw} Embarque ya no tiene «Siguiente: mortalidad final»')
        pg.evaluate("ST.OR.forEach(o=>o.lines.forEach(l=>{}));ST.P.forEach(p=>p.closed=true);save();go('inicio')")
        chk(pg.evaluate("nxt()[1]") != 'cierre' and 'mortalidad' not in pg.inner_text('.gd').lower(), f'{vw} el Panel no manda a Mortalidad final: {pg.evaluate("nxt()[2]")}')
        chk('Paso' in pg.evaluate("guide(4,'x','y','','')") and 'de 4' in pg.evaluate("guide(4,'x','y','','')"), f'{vw} las guías dicen «Paso N de 4»')
        pg.close()
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
