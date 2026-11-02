"""v1.19.0 · Precio de compra y «Hojas para imprimir» (pedido del usuario, 26/oct/2026).
- Precio de compra en el lote (solo el Administrador): USD por kg, USD por kg de despatada, factura y nota; total en dólares
  (kg sin despatada × precio + kg de despatada × precio de despatada). Se comparte y sobrevive a un respaldo.
- «Hojas para imprimir» (menú → Revisión): periodo, existencia física y un PDF por hoja del Excel (Recepción, Envíos, Existencia,
  Congelación, Precio de compra —solo el Administrador— y Balance). Todos se arman sin errores. Sin desbordes en 390/820/1440 px.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/hojas_t.py"""
import os, json
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
OUT = os.environ.get('OUT', '/tmp/propesa-pruebas'); os.makedirs(OUT, exist_ok=True)
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',role:'piso',notify:true},{id:3,name:'Dirección',email:'ver@propesa.mx',role:'consulta',notify:false}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
def login(pg, em):
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900}, accept_downloads=True)
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1)")
    pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.fill('#fl', 'WLREM190926'); pg.select_option('#fo', '2'); pg.fill('#fkb', '36'); pg.fill('#ftt', '58'); pg.fill('#ftp', '59'); pg.fill('#fdes', '0')
    for i, v in enumerate([1575.65, 527.95, 59.55, 7.6, 6.1]): pg.fill(f'#fk{i}', str(v))
    pg.click('[data-a=sv]'); pg.wait_for_timeout(150)
    chk(pg.locator('#prc').count() == 1, 'el Administrador ve «Precio de compra» en el lote')
    pg.fill('#pr_u', '-3'); pg.click('[data-a=prs]'); pg.wait_for_timeout(80)
    chk('Revisa el precio' in pg.inner_text('#pr_m') and pg.input_value('#pr_u') == '-3', 'un precio negativo no se guarda y se conserva lo escrito')
    pg.fill('#pr_u', '42'); pg.fill('#pr_d', '25'); pg.select_option('#pr_f', 'F'); pg.fill('#pr_n', '76.25 kg recuperada'); pg.click('[data-a=prs]'); pg.wait_for_timeout(100)
    chk(pg.evaluate("R_('WLREM190926').pr") == {'u': 42, 'd': 25, 'f': 'F', 'nt': '76.25 kg recuperada'}, 'guarda precio, despatada, factura y nota')
    chk(abs(pg.evaluate("prUSD('WLREM190926')") - round(2170.75 * 42 + 6.1 * 25, 2)) < 0.01, 'total = 2,170.75 kg × 42 + 6.1 kg × 25 = 91,324.00 USD')
    chk('91,324.00' in pg.inner_text('#prc'), 'el lote muestra el total en dólares')
    w = json.loads(pg.evaluate("JSON.stringify(encodeST().get('$/WLREM190926')[1])")); r_ = json.loads(pg.evaluate("JSON.stringify(WN.R(R_('WLREM190926')))")); c = json.loads(pg.evaluate("JSON.stringify(cleanST(mqDump()).R[0])"))
    chk(w['u'] == 42 and w['lot'] == 'WLREM190926' and 'pr' not in r_ and c['pr']['f'] == 'F', 'el precio viaja en su propio registro ($/<lote>, solo el Administrador) y sobrevive a un respaldo')
    # hojas para imprimir
    pg.locator('.sb [data-go=hojas]').click(); pg.wait_for_timeout(150)
    chk(pg.locator('.hjr').count() == 6, 'Hojas para imprimir: 6 hojas para el Administrador')
    pg.fill('#hj_d0', '01/09/2026'); pg.locator('#hj_d0').dispatch_event('change'); pg.fill('#hj_f', '2100'); pg.locator('#hj_f').dispatch_event('change'); pg.wait_for_timeout(150)
    a = pg.locator('.hjr [data-pdf^="dl:hbal:"]').get_attribute('data-pdf')
    chk(a.startswith('dl:hbal:2026-09-01|') and a.endswith('|2100'), f'el periodo y la existencia física van en el PDF ({a})')
    for k in ['hrec', 'henv', 'hexi', 'hcon', 'hpre', 'hbal']:
        with pg.expect_download() as dl: pg.locator(f'.hjr [data-pdf^="dl:{k}:"]').click()
        d = dl.value; fp = os.path.join(OUT, d.suggested_filename); d.save_as(fp)
        chk(open(fp, 'rb').read(5) == b'%PDF-' and os.path.getsize(fp) > 1500, f'PDF {k}: {d.suggested_filename}')
    pg.evaluate("mqSet(2);go('hojas')"); pg.wait_for_timeout(100)
    with pg.expect_download() as dl: pg.locator('.hjr [data-pdf^="dl:hrec:"]').click()
    chk('_Abel_' in dl.value.suggested_filename and 'Maquila: <b>Abel' in pg.inner_html('main'), 'en Abel, la pantalla y el archivo dicen la maquila')
    for w_, h_ in [(820, 1180), (390, 844)]:
        pg.set_viewport_size({'width': w_, 'height': h_}); pg.evaluate("go('hojas')"); pg.wait_for_timeout(120)
        chk(not overflow(pg), f'Hojas para imprimir sin scroll de lado en {w_} px'); pg.screenshot(path=os.path.join(OUT, f'hojas_{w_}.png'), full_page=True)
    pg.evaluate("mqSet(1);me=null;render()"); pg.set_viewport_size({'width': 1440, 'height': 900}); login(pg, 'ver@propesa.mx')
    pg.evaluate("go('lote:WLREM190926')"); pg.wait_for_timeout(100)
    chk(pg.locator('#prc').count() == 0, 'Consulta no ve el precio de compra')
    pg.evaluate("go('hojas')"); pg.wait_for_timeout(100)
    chk(pg.locator('.hjr').count() == 0 and pg.locator('.cli').count() == 1, 'Consulta (solo inventario, v1.30.0) no ve las hojas')
    r = pg.evaluate("(async()=>{try{await pdfMake('hpre','');return 'armó'}catch(e){return e.message}})()")
    chk('Solo el Administrador' in r, 'el PDF de precios no se arma para otro rol')
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
