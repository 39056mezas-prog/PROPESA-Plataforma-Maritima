"""Cambiar de modo sin perder lo escrito (v1.8.2).
Modo piso → vista completa estando en «Registrar entradas»: te quedas en la misma hoja con las mismas filas.
Vista completa → Modo piso con el formulario de Entrada a medio llenar: lo escrito pasa como fila de la hoja.
Empacar ↔ Empacar del mismo cliente. Si sales de la hoja, Entrada avisa que hay entradas sin guardar.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/cambio_modo_t.py"""
from playwright.sync_api import sync_playwright
import os, sys
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
V = "[V.v,V.id==null?'':String(V.id),PISO]"
def toggle(pg):
    """El interruptor de Modo piso que ve el usuario: en piso, el del encabezado; en la vista completa, el del menú lateral
    (en celular primero se abre el menú ☰)."""
    if pg.evaluate("PISO"): pg.click('.phd [data-mode]')
    else:
        if pg.viewport_size['width'] < 700: pg.click('.mb'); pg.wait_for_timeout(200)
        pg.click('.sb [data-mode]')
    pg.wait_for_timeout(1000)

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","1")}', seed); pg.reload()
        pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'admin123'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
        pg.evaluate("setPiso(true);go('pent')"); pg.wait_for_timeout(150)
        # dos filas a medio llenar en Modo piso
        pg.select_option('[data-pr="1:origin"]', '1'); pg.select_option('[data-pr="1:tank"]', 'T2'); pg.fill('[data-pr="1:lot"]', 'wlrmodo1'); pg.fill('[data-pr="1:k0"]', '25')
        pg.fill('[data-pr="1:tempT"]', '57.5')
        pg.click('[data-pa=add]'); pg.select_option('[data-pr="2:origin"]', '2'); pg.fill('[data-pr="2:lot"]', 'wlrmodo2')
        toggle(pg)
        chk(pg.evaluate(V) == ['pent', '', False] and pg.locator('.sb').count() == 1, f'{vw} apagar Modo piso en «Registrar entradas» → misma hoja en la vista completa')
        vals = pg.evaluate("[...['1:origin','1:tank','1:lot','1:k0','1:tempT','2:origin','2:lot']].map(k=>document.querySelector(`[data-pr=\"${k}\"]`).value)")
        chk(vals == ['1', 'T2', 'WLRMODO1', '25', '57.5', '2', 'WLRMODO2'], f'{vw} con las mismas filas y datos: {vals}')
        chk(pg.is_visible('[data-pr="1:tempT"]'), f'{vw} «Más» de la fila 1 sigue abierto como lo dejaste')
        chk(pg.locator('.back[data-go=recepcion]').count() == 1, f'{vw} en la vista completa la hoja tiene «‹ Volver a Entrada»')
        # salir a Entrada: aviso con enlace de regreso
        pg.click('.back[data-go=recepcion]'); tx = pg.inner_text('#app')
        chk('tienes 2 entradas sin guardar' in tx.lower(), f'{vw} Entrada avisa las 2 entradas sin guardar')
        pg.click('[data-go=pent] >> text=Terminar'); chk(pg.evaluate(V)[0] == 'pent' and pg.input_value('[data-pr="2:lot"]') == 'WLRMODO2', f'{vw} «Terminar de capturarlas» regresa a la hoja con lo escrito')
        # volver a prender Modo piso: misma hoja
        toggle(pg); chk(pg.evaluate(V) == ['pent', '', True] and pg.input_value('[data-pr="1:lot"]') == 'WLRMODO1', f'{vw} prender Modo piso de nuevo → la misma hoja')
        # terminar y guardar la fila 1 en la vista completa
        toggle(pg)
        pg.fill('[data-pr="1:tempP"]', '58'); pg.fill('[data-pr="1:kgbox"]', '18'); pg.fill('[data-pr="1:desp"]', '0'); pg.click('[data-pa="rm:2"]'); pg.click('[data-pa="rmy:2"]')
        pg.click('[data-pa=save]'); pg.wait_for_timeout(150)
        r = pg.evaluate("(R_('WLRMODO1')||{})")
        chk(r.get('tank') == 'T2' and r.get('tempT') == 57.5 and r.get('tempP') == '58' and r.get('kgbox') == 18 and r.get('desp') == 0 and pg.evaluate("bal('WLRMODO1')") == 25000, f'{vw} se guarda en la vista completa con todo lo que se escribió en Modo piso')
        # vista completa → Modo piso con el formulario de Entrada a medio llenar
        pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.select_option('#fo', '3'); pg.select_option('#ft', 'T5'); pg.fill('#fl', 'wlrmodo3'); pg.fill('#fk2', '40'); pg.fill('#ftt', '59')
        toggle(pg)
        u = pg.evaluate("PEN.cur")
        chk(pg.evaluate(V)[0] == 'pent' and pg.evaluate("PISO"), f'{vw} prender Modo piso con el formulario a medio llenar → «Registrar entradas»')
        vals = pg.evaluate(f"['origin','tank','lot','k2','tempT'].map(k=>document.querySelector(`[data-pr=\"{u}:${{k}}\"]`).value)")
        chk(vals == ['3', 'T5', 'WLRMODO3', '40', '59'], f'{vw} lo escrito pasa como fila de la hoja: {vals}')
        # sin nada escrito en Entrada: Modo piso abre su inicio, como antes
        pg.evaluate("PEN0();setPiso(false);go('recepcion')"); toggle(pg); chk(pg.evaluate(V) == ['piso', '', True], f'{vw} Entrada sin nada escrito → inicio de Modo piso')
        # Empacar ↔ Empacar del mismo cliente
        k = pg.evaluate("(()=>{const o=ST.OR[0],l=o.lines[0];return o.id+'.'+l.id})()")
        pg.evaluate(f"go('pemp:{k}')"); toggle(pg); chk(pg.evaluate(V) == ['empacar', k, False], f'{vw} Empacar en Modo piso → Empacar del mismo cliente en la vista completa')
        toggle(pg); chk(pg.evaluate(V) == ['pemp', k, True], f'{vw} y de regreso')
        # botón de atrás después de cambiar de modo: regresa al modo anterior
        pg.go_back(wait_until='commit'); pg.wait_for_timeout(250); chk(pg.evaluate(V) == ['empacar', k, False], f'{vw} atrás regresa a la vista completa')
        pg.close()
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
