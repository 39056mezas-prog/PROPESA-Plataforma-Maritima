"""v1.43.2 · Borrador de recepción: se crea al tocar «+ Nueva recepción», se guarda solo mientras se escribe
(ST.RB → registro RB/<id> en la base), sobrevive a salir y recargar, se sigue desde la lista «Recepciones sin terminar»,
«Cancelar» no lo borra, «Descartar» pide confirmación y lo quita, y guardar la recepción lo quita.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/v1432_t.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recep import recibir
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS
def entrar(pg):
    pg.goto(BASE); pg.evaluate(FIX); pg.reload()
    pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(250)
with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(viewport={'width': 1280, 'height': 900}); pg = c.new_page()
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('dialog', lambda d: d.accept())
    entrar(pg)
    pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.wait_for_timeout(200)
    chk(pg.evaluate("ST.RB.length") == 1, 'al tocar «+ Nueva recepción» se crea el borrador')
    chk(pg.evaluate("V.id").startswith('d-'), 'la pantalla abre el borrador (ruta d-…)')
    rid = pg.evaluate("ST.RB[0].id")
    # escribe kg y talla, y un dato de la recepción
    pg.click('#tn_k1'); pg.keyboard.type('350'); pg.keyboard.press('r'); pg.wait_for_timeout(100)
    pg.fill('#rt_fl', 'WLRCO010126')
    pg.wait_for_timeout(500)
    chk(pg.evaluate("ST.RB[0].tn['1'] && ST.RB[0].tn['1'].g") == '350', 'los kg de la tina se guardan en el borrador mientras se escriben')
    chk(pg.evaluate("ST.RB[0].h.rt_fl") == 'WLRCO010126', 'el lote escrito también queda en el borrador')
    chk(any(k.startswith('RB/') for k in pg.evaluate("[...encodeST().keys()]")), 'el borrador viaja a la base (RB/<id>)')
    # salir sin guardar y recargar: el borrador sigue
    pg.evaluate("go('recepcion')"); pg.wait_for_timeout(150)
    chk(pg.locator('.rbdr').count() == 1 and 'Seguir' in pg.inner_text('.rbdr'), 'la lista «Recepciones sin terminar» aparece en Recepción')
    pg.reload(); pg.wait_for_timeout(300)
    chk(pg.evaluate("ST.RB.length") == 1, 'el borrador sobrevive a recargar la página')
    pg.click('.rbdr [data-go]'); pg.wait_for_timeout(200)
    chk(pg.evaluate("document.getElementById('tn_k1') && document.getElementById('tn_k1').value") == '350', 'Seguir ›: la tina 1 trae sus 350 kg')
    chk(pg.evaluate("document.getElementById('rt_fl') && document.getElementById('rt_fl').value") == 'WLRCO010126', 'Seguir ›: el lote sigue escrito')
    # Cancelar no borra el borrador
    pg.click('[data-rt=cancel]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("ST.RB.length") == 1, 'Cancelar no borra el borrador')
    # Descartar pide confirmación y lo quita
    pg.click('[data-rbdel]'); pg.wait_for_timeout(200)
    chk(pg.evaluate("ST.RB.length") == 0 and pg.locator('.rbdr').count() == 0, 'Descartar quita el borrador y su tarjeta')
    # guardar la recepción quita el borrador
    pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.wait_for_timeout(200)
    chk(pg.evaluate("ST.RB.length") == 1, 'nueva recepción crea otro borrador')
    recibir(pg, 'WLRCO010126', pv='1', kz=[40], tank='T1', fecha='01/01/2026', nuevo=False)
    chk(pg.evaluate("ST.RB.length") == 0, 'al guardar la recepción, el borrador desaparece')
    chk(pg.evaluate("ST.R.some(r=>r.lot==='WLRCO010126')"), 'la recepción sí quedó guardada')
    c.close()
    b.close()
print('ERRORES JS:', errs or 'ninguno')
if errs: fails.append('error js')
print('TODO BIEN' if not fails else f'FALLAS: {len(fails)}')
sys.exit(1 if fails else 0)
