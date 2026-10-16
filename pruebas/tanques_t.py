"""Prueba PROPESA (tanques_t): tablero de tanques en Entrada (v1.5.0).
Mapa del piso (T1–T4 a la derecha, T6 y T5 a la izquierda) con kg, tallas y agua; al tocar un tanque sale su detalle; vacíos dicen «Vacío»;
tocar un lote abre el lote; un lote cerrado ya no cuenta; sin desbordes en celular ni con texto de 20 px.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/tanques_t.py"""
import os
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
SEED = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json'), encoding='utf-8').read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
PREP = ("ST.R[1].tank='T3';ST.T=[{id:1,t:dLoc()+'T09:15',tank:'T1',a:60.1,s:59.8,p:58.9,by:'Ana'},"
        "{id:2,t:'2026-10-01T07:00',tank:'T1',a:50,s:50,p:50,by:'Ana'},{id:3,t:'2026-10-12T17:40',tank:'T3',a:61,s:null,p:59.5,by:'Luis'}];save();go('recepcion')")
det = lambda pg: pg.inner_text('.tqd .tqc')
POS = "Object.fromEntries([...document.querySelectorAll('.tqm')].map(b=>{const r=b.getBoundingClientRect();return [b.dataset.tq,[r.left,r.top,r.right]]}))"
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw, sch, fs in [(1440, 'light', None), (820, 'dark', None), (390, 'light', None), (390, 'dark', '20')]:
        tag = f'{vw}px {sch}' + (f' texto {fs}px' if fs else '')
        pg = b.new_page(viewport={'width': vw, 'height': 900}, color_scheme=sch)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}', SEED)
        if fs: pg.evaluate("f=>localStorage.setItem('propesa-fs',f)", fs)
        pg.reload(); pg.fill('#le', 'admin@propesa.mx'); pg.click('[data-a=lg]'); pg.wait_for_timeout(300)
        pg.evaluate("TQSEL=null;" + PREP); pg.wait_for_timeout(200)
        chk(pg.locator('.tqmap .tqm').count() == 6, f'{tag}: el mapa tiene los 6 tanques')
        P = pg.evaluate(POS)
        right = all(P[t][0] > P['T6'][2] - 1 for t in ('T1', 'T2', 'T3', 'T4')) and P['T5'][0] < P['T1'][0]
        chk(right and P['T1'][1] < P['T2'][1] < P['T3'][1] < P['T4'][1], f'{tag}: T1–T4 a la derecha, de arriba abajo; T5 y T6 a la izquierda')
        chk(abs(P['T6'][1] - P['T3'][1]) < 4 and abs(P['T5'][1] - P['T4'][1]) < 4, f'{tag}: T6 a la altura de T3 y T5 a la altura de T4 (como el piso)')
        exp = pg.evaluate("f(ST.R.filter(r=>r.tank=='T1'&&!r.closed).reduce((a,r)=>a+bal(r.lot),0),1)")
        chk(pg.get_attribute('[data-tq=T1]', 'aria-pressed') == 'true' and 'Tanque 1' in det(pg) and exp + ' kg' in det(pg), f'{tag}: abre con el primer tanque con producto (T1, {exp} kg)')
        chk(exp + ' kg' in pg.inner_text('[data-tq=T1]') and 'Agua 60.1°' in pg.inner_text('[data-tq=T1]'), f'{tag}: en el mapa T1 dice sus kg y el agua más reciente')
        chk(pg.evaluate("[...document.querySelectorAll('.tqd .tqc .tqsz b')].reduce((a,e)=>a+ +e.textContent,0).toFixed(1)") == exp, f'{tag}: las 4 tallas del detalle suman el total')
        chk('60.1°' in det(pg) and 'Hoy 09:15' in det(pg) and '50°' not in det(pg), f'{tag}: el detalle muestra la lectura más reciente')
        pg.click('[data-tq=T2]'); chk(pg.get_attribute('[data-tq=T2]', 'aria-pressed') == 'true' and 'Vacío' in det(pg) and 'Sin lectura' in det(pg), f'{tag}: tocar T2 (vacío) muestra «Vacío» y «Sin lectura»')
        pg.click('[data-tq=T3]'); d3 = det(pg)
        chk('WLRCO061026B' in d3 and 'Pescadores del Sur' in d3 and '—' in d3, f'{tag}: tocar T3 muestra su lote, proveedor y «—» si falta un dato')
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth") and pg.evaluate("[...document.querySelectorAll('.tqm,.tqc')].every(c=>c.scrollWidth<=c.clientWidth+1)"), f'{tag}: sin desbordes')
        pg.click('.tqd .tqlot'); chk(pg.evaluate("V.v=='lote'&&V.id=='WLRCO061026B'"), f'{tag}: tocar el lote abre su página')
        pg.evaluate("go('recepcion')"); chk(pg.get_attribute('[data-tq=T3]', 'aria-pressed') == 'true', f'{tag}: al volver sigue seleccionado T3')
        pg.click('.tqd .tqtp'); chk(pg.evaluate("V.v") == 'temperatura', f'{tag}: tocar la temperatura lleva a Temperatura')
        pg.evaluate("R_('WLRCO061026B').closed=true;save();go('recepcion')")
        chk('Vacío' in pg.inner_text('[data-tq=T3]') and 'WLRCO061026B' not in det(pg), f'{tag}: un lote cerrado ya no aparece en su tanque')
        pg.evaluate("go('inicio')")
        pan=pg.evaluate("[...document.querySelectorAll('.g4 .kp')].map(k=>k.innerText).find(t=>t.includes('En tanques'))")
        chk('926 kg' in pan.replace('\n',' '), f'{tag}: «En tanques» del Panel cuenta solo lotes abiertos, igual que el mapa (no los cerrados): {pan.splitlines()}')
        pg.close()
    b.close()
chk(not errs, 'sin errores de JavaScript ' + str(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} fallas')
