"""v1.34.0 · Pantallas más limpias (pedido del usuario, 5/nov/2026: «hay demasiados campos y no se sabe por dónde empezar»).
1. Encabezado corto en cada sección: título (h1), una línea y la acción principal arriba; sin recuadro azul «Formato/Guía»
   ni tarjeta «Archivo de este paso». PDF y correo son botones discretos (no azules).
2. Entrada: «+ Nueva entrada» y la tabla arriba; la planta 3D y el tablero de tanques se abren con «Tanques y planta 3D».
3. Lo secundario se pliega: fotos y notas, y en el lote: tanques, precio de compra y movimientos. Lo abierto se queda abierto.
4. Menú más corto: sin Panel general ni Administración (están en el selector de maquila y en el círculo del perfil).
5. Orden: el desglose del peso bruto se pliega (el total queda a la vista). Mortalidad: sin cuatro gráficas vacías.
Esta prueba NO abre los plegables por su cuenta: revisa que estén cerrados y que se abran con un toque.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v134_t.py"""
from playwright.sync_api import sync_playwright
import os
BASE = 'http://localhost:8765/index.html?modo=local'  # sin variables: esta prueba revisa los plegables tal como los ve el usuario
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em='admin@propesa.mx'):
    pg.goto(BASE); pg.evaluate('([s])=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0");localStorage.setItem("propesa-inst",String(Date.now()))}', [seed]); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(250)
def ir(pg, r): pg.evaluate(f"go('{r}')"); pg.wait_for_timeout(200)
def abierto(pg, f): return pg.evaluate(f"(document.querySelector('[data-fold=\"{f}\"]')||{{}}).open===true")
LISTAS = ['recepcion', 'ordenes', 'empaque', 'embarques', 'cierre', 'hojas', 'temperatura', 'inicio']
with sync_playwright() as p:
    b = p.chromium.launch()
    for W, H in [(1440, 900), (1180, 820), (820, 1180), (390, 844)]:
        pg = b.new_page(viewport={'width': W, 'height': H}); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg)
        # ---------- 1. encabezado corto ----------
        for r in LISTAS:
            ir(pg, r)
            chk(pg.locator('main .gd').count() == 0 and 'Archivo de este paso' not in pg.inner_text('main'), f'{W} {r}: sin recuadro azul ni «Archivo de este paso»')
            chk(pg.locator('main h1').count() == 1, f'{W} {r}: un solo título')
            chk(pg.locator('main .pdfb .btn:not(.q)').count() == 0, f'{W} {r}: PDF y correo son botones discretos')
            chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{W} {r}: sin scroll de lado')
        # ---------- 2. Entrada ----------
        ir(pg, 'recepcion')
        nf = pg.locator('.pgh [data-a=nf]')
        chk(nf.count() == 1 and nf.bounding_box()['y'] < 260, f'{W} Entrada: «+ Nueva entrada» va en el encabezado, a la vista ({nf.bounding_box()["y"] if nf.count() else "—"} px)')
        chk(pg.evaluate("(()=>{const t=document.querySelector('table.ent'),f=document.querySelector('[data-fold=\"ent-tq\"]');return !!t&&!!f&&(t.compareDocumentPosition(f)&4)>0})()"), f'{W} Entrada: la tabla va antes de los tanques')
        chk(not abierto(pg, 'ent-tq') and pg.locator('.t3v').count() == 0 and pg.locator('.tqd').count() == 0, f'{W} Entrada: la planta 3D y el tablero no se arman hasta abrirlos')
        chk('kg en 2 lotes' in pg.inner_text('[data-fold="ent-tq"] summary'), f'{W} Entrada: el plegable dice cuántos kg y lotes hay')
        pg.click('[data-fold="ent-tq"] summary'); pg.wait_for_timeout(400)
        chk(abierto(pg, 'ent-tq') and pg.locator('.tqd').count() == 1, f'{W} Entrada: un toque abre los tanques')
        ir(pg, 'ordenes'); ir(pg, 'recepcion'); chk(abierto(pg, 'ent-tq'), f'{W} Entrada: al volver siguen abiertos')
        pg.click('.pgh [data-a=nf]'); pg.wait_for_timeout(200); chk(pg.locator('#rt_fl').count() == 1 and pg.evaluate('V.v') == 'rtin', f'{W} Recepción: «+ Nueva recepción» abre la recepción por tinas')
        # ---------- 4. menú ----------
        if W < 700: pg.click('.mb'); pg.wait_for_timeout(150)
        chk(pg.locator('.sb [data-go=general]').count() == 0 and pg.locator('.sb [data-go=admin]').count() == 0, f'{W} menú: sin Panel general ni Administración')
        chk(pg.locator('.sb .fs[data-go]').count() == 8, f'{W} menú: 8 secciones (v1.39.0: Formatos y Panel = Centro de operaciones; v1.41.0: «Instalar app» aparte) ({pg.locator(".sb .fs[data-go]").count()})')
        chk('Elige qué llenar' not in pg.inner_text('.sb') and 'Resumen' not in pg.inner_text('.sb') and '7/7 hieleras' in pg.inner_text('.sb'), f'{W} menú: sin subtítulos de relleno, con los conteos')
        pg.click('.sb [data-mq]'); pg.click('#mqmenu [data-mqgo="general"]'); pg.wait_for_timeout(250)
        chk(pg.evaluate('V.v') == 'general', f'{W} el Panel general se abre desde el selector de maquila')
        if W < 700 and pg.locator('.sb.op, .sb.on').count(): pg.keyboard.press('Escape')
        pg.click('[data-avatar]'); chk(pg.locator('[data-pm=users]').count() == 1, f'{W} Administración sigue en el círculo del perfil'); pg.keyboard.press('Escape')
        # ---------- 3. lote ----------
        ir(pg, 'lote:WLRCO051026A')
        for f in ['lot-tq:WLRCO051026A', 'lot-pr:WLRCO051026A', 'lot-mv:WLRCO051026A', 'ev:lote:WLRCO051026A']:
            chk(pg.locator(f'[data-fold="{f}"]').count() == 1 and not abierto(pg, f), f'{W} lote: «{f.split(":")[0]}» empieza cerrado')
        chk('T1 (principal) · 925.8 kg' in pg.inner_text('[data-fold="lot-tq:WLRCO051026A"] summary'), f'{W} lote: el tanque se lee sin abrir')
        chk(pg.locator('[data-fin]').is_visible(), f'{W} lote: el conteo final sigue a la vista')
        pg.click('[data-fold="lot-pr:WLRCO051026A"] summary'); pg.wait_for_timeout(100)
        pg.fill('#pr_u', '-3'); pg.click('[data-a=prs]'); pg.wait_for_timeout(150)
        chk(abierto(pg, 'lot-pr:WLRCO051026A') and pg.locator('#pr_u').is_visible(), f'{W} lote: con un error el precio sigue abierto')
        pg.click('[data-fold="ev:lote:WLRCO051026A"] summary'); pg.fill('#ntx', 'nota v134'); pg.evaluate('render()'); pg.wait_for_timeout(100)
        chk(abierto(pg, 'ev:lote:WLRCO051026A') and pg.input_value('#ntx') == 'nota v134', f'{W} notas: lo escrito no se pierde ni se cierra al redibujar')
        pg.click('[data-ev^=save]'); pg.wait_for_timeout(150); chk('1 nota' in pg.inner_text('[data-fold="ev:lote:WLRCO051026A"] summary'), f'{W} notas: la cuenta sale en el plegable')
        # teclado: el resumen se enfoca y Enter abre
        pg.focus('[data-fold="lot-mv:WLRCO051026A"] summary'); pg.keyboard.press('Enter'); pg.wait_for_timeout(100)
        chk(abierto(pg, 'lot-mv:WLRCO051026A') and pg.locator('#ty').is_visible(), f'{W} lote: con teclado (Enter) se abren los movimientos')
        # ---------- 5. orden y mortalidad ----------
        ir(pg, 'orden:1')
        chk(pg.locator('[data-fold^="pb:1"]').count() == 3 and pg.locator('details[data-fold^="pb:1"][open]').count() == 0, f'{W} orden: desglose del peso bruto plegado (por cliente y total)')
        chk('98.0 kg' in pg.inner_text('[data-fold="pb:1"] summary'), f'{W} orden: el total del peso bruto se lee sin abrir')
        ir(pg, 'cierre')
        chk(pg.locator('main .cols').count() == 0 and 'Sin datos' not in pg.inner_text('main'), f'{W} Mortalidad: sin cuatro gráficas vacías')
        chk(not abierto(pg, 'mort-calc') and '(enviadas − vivas)' in pg.text_content('[data-fold="mort-calc"]'), f'{W} Mortalidad: «¿Cómo se calcula?» plegado')
        ir(pg, 'temperatura')
        chk(pg.evaluate("(()=>{const n=document.querySelector('.tqn'),z=document.querySelector('.tzc');return !!n&&!!z&&(n.compareDocumentPosition(z)&4)>0})()"), f'{W} Temperatura: «Nueva lectura» antes de los rangos')
        pg.close()
    b.close()
chk(not errs, f'sin errores de JavaScript {errs[:3]}')
print('TODO BIEN' if not fails else f'{len(fails)} FALLAS')
