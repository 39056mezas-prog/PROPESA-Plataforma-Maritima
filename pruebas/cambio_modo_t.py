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
        pg.evaluate("setPiso(false);go('inicio')"); pg.wait_for_timeout(150)  # v1.43.0: la hoja de varias recepciones ya no existe
        # v1.42.0 · vista completa → Modo piso con la recepción por tinas a medio llenar: es la misma pantalla y no se pierde nada
        pg.evaluate("RT=null;go('rtin')"); pg.select_option('#rt_fo', '3'); pg.fill('#rt_fl', 'wlrmodo3'); tn = pg.evaluate('RT.act'); pg.fill(f'#tn_k{tn}', '40')
        toggle(pg)
        chk(pg.evaluate(V)[0] == 'rtin' and pg.evaluate("PISO"), f'{vw} prender Modo piso a media recepción → la misma recepción por tinas')
        vals = [pg.input_value('#rt_fo'), pg.input_value('#rt_fl').upper(), pg.input_value(f'#tn_k{tn}')]
        chk(vals == ['3', 'WLRMODO3', '40'], f'{vw} lo escrito sigue ahí: {vals}')
        toggle(pg); chk(pg.evaluate(V)[0] == 'rtin' and not pg.evaluate("PISO") and pg.input_value(f'#tn_k{tn}') == '40', f'{vw} y de regreso a la vista completa, igual')
        pg.evaluate("RT=null")
        # sin nada escrito en Entrada: Modo piso abre su inicio, como antes
        pg.evaluate("setPiso(false);go('recepcion')"); toggle(pg); chk(pg.evaluate(V) == ['piso', '', True], f'{vw} Entrada sin nada escrito → inicio de Modo piso')
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
