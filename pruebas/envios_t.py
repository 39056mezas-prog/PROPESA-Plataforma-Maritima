import sys
"""v1.19.0 · Temperatura de arribo y % de mortalidad del cliente (pedido del usuario, 26/oct/2026).
- El embarque toma el color de su consignatario (el tape por envío se quitó a pedido del usuario: el color es el del consignatario).
- En «Langostas vivas al llegar»: % mortalidad que reporta el cliente y temperatura de arribo (también con el embarque cerrado).
- v1.24.0: se capturan en Revisión → Mortalidad final, ya no en el embarque (el embarque solo avisa y lleva ahí).
- Salen en el embarque, en Mortalidad final (tabla y gráfica por envío), en el PDF del embarque y en el de mortalidad.
- Se comparten (WN.P) y sobreviven a un respaldo. Consulta no los cambia.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/envios_t.py"""
import os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recep import recibir
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
OUT = os.environ.get('OUT', '/tmp/propesa-pruebas'); os.makedirs(OUT, exist_ok=True)
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:3,name:'Dirección',email:'ver@propesa.mx',role:'consulta',notify:false}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
def login(pg, em):
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1)")
    recibir(pg, 'WLRCO261026', pv='1', kz=['200'], tt='58')
    pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '26/10/2026'); pg.click('[data-oa=new]'); pg.select_option('#ol_city', 'PVG'); pg.fill('#ol_z0', '2'); pg.fill('#ol_tar', '0'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(120)
    pg.evaluate("ST.CC={0:'#2563eb'};syncShipIdx(0);save();go('emb:0')"); pg.wait_for_timeout(100)
    chk(pg.evaluate("ST.P[0].col") == '#2563eb' and pg.locator('#emb_tp').count() == 0, 'el envío toma el color de su consignatario; ya no hay tape por envío')
    # empacar y cerrar
    pg.evaluate("go('empaque')"); pg.locator('[data-go^=\"empacar:\"]').first.click()
    for _ in range(2): pg.fill('#pk_c0', '28'); pg.click('#pkr0 [data-pk="k:0:B"]'); pg.wait_for_timeout(80)
    pg.evaluate("ST.OR.forEach(o=>{o.f={...(o.f||{}),hf:'08:00',re:'Ana Torres',ev:'S',pl:'X',ch:'X',tel:'0',tp:'48',to:'T1',tq:'T1'}});save();go('emb:0')"); pg.click('[data-a=cp]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("ST.P[0].closed"), 'embarque cerrado')
    chk(pg.locator('main [data-alive],main [data-mc],main [data-tar]').count() == 0 and 'se capturan en Revisión' in pg.inner_text('main'), 'v1.24.0: el embarque ya no captura lo de la llegada; avisa que va en Revisión')
    pg.click('main .arrn [data-go=cierre]'); pg.wait_for_timeout(250)
    chk(pg.evaluate("V.v") == 'cierre' and pg.locator('#envcli [data-alive]').count() == 1, '«Ir a Mortalidad final ›» lleva a la tabla de llegada')
    pg.fill('[data-mc]', '9.88'); pg.locator('[data-mc]').dispatch_event('change'); pg.wait_for_timeout(100)
    pg.click('[data-tar]'); chk(pg.evaluate("document.activeElement&&document.activeElement.dataset.tar!=null"), 'tocar la temperatura de arribo no la cierra (antes se volvía a dibujar)')
    pg.fill('[data-tar]', '6-8 °C'); pg.locator('[data-tar]').dispatch_event('change'); pg.wait_for_timeout(100)
    chk(pg.evaluate("ST.P[0].mc") == 9.88 and pg.evaluate("ST.P[0].ta") == '6-8 °C', 'cerrado, se captura el % del cliente (9.88) y la temperatura de arribo')
    pg.fill('[data-mc]', '120'); pg.locator('[data-mc]').dispatch_event('change'); pg.wait_for_timeout(100)
    chk(pg.evaluate("ST.P[0].mc") == 9.88, 'un % fuera de 0–100 no se guarda')
    pg.fill('[data-alive]', '50'); pg.locator('[data-alive]').dispatch_event('change'); pg.wait_for_timeout(100)
    chk(pg.evaluate("ST.P[0].alive") == 50 and '6 de 56' in pg.inner_text('#envcli'), 'vivas al llegar en Revisión: 50 de 56 → mortalidad 6')
    pg.fill('[data-alive]', ''); pg.locator('[data-alive]').dispatch_event('change'); pg.wait_for_timeout(100)
    pg.evaluate("go('cierre')"); pg.wait_for_timeout(100)
    t = pg.inner_text('#envcli') + ' '.join(pg.eval_on_selector_all('#envcli input', 'e=>e.map(x=>x.value)')); chk('9.88' in t and '6-8 °C' in t, 'Mortalidad final: tabla de envíos con % del cliente y temperatura de arribo')
    chk('9.88% (cliente)' in pg.inner_text('main'), 'la gráfica por envío usa el % del cliente si no hay conteo')
    for k_, a_ in [['emb', 0], ['mort', None]]:
        r = pg.evaluate("([k,a])=>(async()=>{try{const d=await pdfMake(k,a);return !!d&&d.u8.length>1000}catch(e){return String(e)}})()", [k_, a_])
        chk(r is True, f'PDF {k_} con arribo y % del cliente ({r})')
    w = json.loads(pg.evaluate("JSON.stringify(WN.P(ST.P[0]))")); c = json.loads(pg.evaluate("JSON.stringify(cleanST(mqDump()).P[0])"))
    chk(w['mc'] == 9.88 and w['ta'] == '6-8 °C' and c['mc'] == 9.88 and c['ta'] == '6-8 °C' and 'tp' not in w, 'se comparten y sobreviven a un respaldo')
    for w_, h_ in [(820, 1180), (390, 844)]:
        pg.set_viewport_size({'width': w_, 'height': h_})
        for r_ in ['emb:0', 'cierre']:
            pg.evaluate(f"go('{r_}')"); pg.wait_for_timeout(120); chk(not overflow(pg), f'{r_} sin scroll de lado en {w_} px')
    pg.evaluate("me=null;render()"); login(pg, 'ver@propesa.mx'); pg.evaluate("go('cierre')"); pg.wait_for_timeout(100)
    chk(pg.locator('[data-mc],[data-tar],[data-alive]').count() == 0 and pg.locator('.cli').count() == 1, 'Consulta (solo inventario, v1.30.0) ni los ve')
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
