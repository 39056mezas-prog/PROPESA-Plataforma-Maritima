"""v1.19.0 · Salidas que no son embarque (pedido del usuario, 26/oct/2026): para congelar, basura (descompuesta), a recuperación y
débil, con nota o folio. Restan del tanque, salen en el lote, en Mortalidad final (totales por tipo y lista) y en su PDF; la
mortalidad del lote no las cuenta como muertas; se pueden revertir; se comparten (WN/cleanST con nt). Solo el Administrador.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/salidas_t.py"""
import os, json
from playwright.sync_api import sync_playwright
ABRIR = "document.querySelectorAll('details.fold').forEach(d=>FOLD[d.dataset.fold]=true);render()"  # v1.34.0: abre los plegables (tanques, notas, precio, movimientos)
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
OUT = os.environ.get('OUT', '/tmp/propesa-pruebas'); os.makedirs(OUT, exist_ok=True)
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',role:'piso',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
def login(pg, em):
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")
def salida(pg, ty, sz, kg, nt=''):
    pg.evaluate(ABRIR); pg.select_option('#ty', ty); pg.select_option('#sz', sz); pg.fill('#kg', str(kg)); pg.fill('#mvn', nt); pg.click('[data-a=mv]'); pg.wait_for_timeout(120)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1)")
    pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.fill('#fl', 'WLRCO191026'); pg.select_option('#fo', '1'); pg.fill('#fkb', '36'); pg.fill('#ftt', '58'); pg.fill('#ftp', '59'); pg.fill('#fdes', '0')
    for i, v in enumerate([500, 200, 0, 0, 30]): pg.fill(f'#fk{i}', str(v))
    pg.click('[data-a=sv]'); pg.wait_for_timeout(150)
    opts = pg.eval_on_selector_all('#ty option', 'e=>e.map(o=>o.textContent)')
    chk(opts == ['Elige el tipo', 'Salida a embarque (solo para corregir)', 'Para congelar', 'Basura (descompuesta)', 'A recuperación', 'Débil', 'Entrada'], 'el lote ofrece los tipos de salida del Excel: %s' % opts)
    salida(pg, 'CONGELACION', '491-610', 18.5, 'Folio 0344')
    salida(pg, 'BASURA', '491-610', 3.05)
    salida(pg, 'RECUPERACION', '611-850', 20.6, 'sorteo')
    salida(pg, 'DEBIL', 'desp', 5)
    chk(pg.evaluate("bal('WLRCO191026','491-610')") == 478450 and pg.evaluate("bal('WLRCO191026','611-850')") == 179400 and pg.evaluate("bal('WLRCO191026','desp')") == 25000, 'las salidas restan del tanque por talla')
    t = pg.inner_text('main')
    chk('Para congelar' in t and 'Folio 0344' in t and 'Basura (descompuesta)' in t and 'A recuperación' in t, 'la tabla del lote dice el tipo y la nota')
    salida(pg, 'BASURA', '491-610', 9999)
    chk('Existencia insuficiente' in pg.inner_text('main') and pg.input_value('#kg') == '9999', 'no deja sacar más de lo que hay y conserva lo escrito')
    # mortalidad: no cuenta las salidas
    pg.evaluate("R_('WLRCO191026').final=650;save();render()")
    c = pg.evaluate("calc('WLRCO191026')")
    # v1.25.0: el esperado no incluye la despatada (25 kg en tanque); la despatada recibida (30 kg) se suma como merma
    chk(c['ex'] == 657850 and c['dead'] == 7850 and c['desp'] == 30000 and c['mer'] == 37850, f'mortalidad = esperado sin despatada (ya sin congelación, basura, recuperación ni débil) − contado = 7.85 kg; merma con despatada 37.85 kg ({c})')
    pg.evaluate("go('cierre')"); pg.wait_for_timeout(100)
    t = pg.inner_text('#salidas')
    chk('Para congelar' in t and '18.50 kg' in t and '3.05 kg' in t and '20.60 kg' in t and '5.00 kg' in t and 'Folio 0344' in t, 'Mortalidad final: totales por tipo y lista con folio')
    r = pg.evaluate("(async()=>{try{const d=await pdfMake('mort');return !!d&&d.u8.length>1000}catch(e){return String(e)}})()")
    chk(r is True, f'PDF de mortalidad con las salidas ({r})')
    # revertir
    pg.evaluate("go('lote:WLRCO191026')"); pg.wait_for_timeout(100)
    pg.locator('tr', has_text='Para congelar').locator('[data-r]').first.click(); pg.wait_for_timeout(100)
    chk(pg.evaluate("bal('WLRCO191026','491-610')") == 496950, 'revertir la congelación regresa los 18.5 kg')
    # compartir y respaldo
    w = pg.evaluate("JSON.stringify(WN.L(ST.L.find(x=>x.type=='RECUPERACION')))")
    chk(json.loads(w)['nt'] == 'sorteo' and json.loads(w)['type'] == 'RECUPERACION', 'el movimiento viaja con su tipo y su nota')
    c2 = pg.evaluate("cleanST(mqDump()).L.filter(x=>['CONGELACION','BASURA','RECUPERACION','DEBIL'].includes(x.type)).length")
    chk(c2 == 4, 'el respaldo conserva las 4 salidas')
    chk(pg.evaluate("WN.L({id:1,t:'x',type:'OTRA',lot:'L',size:'491-610',m:-1})") is None, 'un tipo que no existe se ignora')
    for w_, h_ in [(820, 1180), (390, 844)]:
        pg.set_viewport_size({'width': w_, 'height': h_})
        for r_ in ['lote:WLRCO191026', 'cierre']:
            pg.evaluate(f"go('{r_}')"); pg.wait_for_timeout(120); chk(not overflow(pg), f'{r_} sin scroll de lado en {w_} px')
        pg.screenshot(path=os.path.join(OUT, f'salidas_{w_}.png'), full_page=True)
    # Encargado de piso no registra salidas
    pg.evaluate("me=null;setPiso(false);render()"); login(pg, 'piso@propesa.mx'); pg.evaluate("setPiso(false);go('lote:WLRCO191026')"); pg.wait_for_timeout(100)
    chk(pg.locator('#ty').count() == 0, 'el Encargado de piso no registra salidas (solo el Administrador)')
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
