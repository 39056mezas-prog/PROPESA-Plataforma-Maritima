"""v1.19.0 · Consignatarios y destinos que agrega el Administrador (pedido del usuario, 26/oct/2026).
- Datos corregidos contra la lista en papel: teléfono y código postal de Yishunhai, USCI de Xinbang. Yishunhai también a XMN.
- Administración → Consignatarios: nuevo (clave, razón social, destinos, dirección, contacto, USCI), editar, ocultar.
- Administración → Destinos: nuevo (TPE · Taipéi), editar el nombre, ocultar. La orden ofrece lo nuevo y no lo oculto.
- Compartidos por todas las maquilas (registros K/<n> y X/<código>), sobreviven a un respaldo; sin desbordes en 390/820/1440 px.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/consignatarios_t.py"""
import os, json
from playwright.sync_api import sync_playwright
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
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1)")
    y = pg.evaluate("CONS[0]"); x = pg.evaluate("CONS[4]")
    chk('13691775559' in y['c'] and '518000' in y['a'] and x['u'] == '91440101MA9UUJN96Y', 'datos corregidos: teléfono y código postal de Yishunhai, USCI de Xinbang')
    chk('XMN' in y['p'], 'Yishunhai también va a XMN')
    pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '26/10/2026'); pg.click('[data-oa=new]'); pg.select_option('#ol_city', 'XMN'); pg.wait_for_timeout(80)
    chk('Shenzhen Yishunhai' in pg.inner_text('#ol_cons'), 'la orden a XMN ofrece Yishunhai')
    # destinos
    pg.evaluate("go('admin')"); pg.wait_for_timeout(100)
    pg.click('[data-dsa=new]'); pg.fill('#ds_c', 'pvg'); pg.fill('#ds_n', 'Otra'); pg.click('[data-dsa=sv]'); pg.wait_for_timeout(80)
    chk('ya existe' in pg.inner_text('#ds_m') and pg.input_value('#ds_n') == 'Otra', 'no deja repetir el código y conserva lo escrito')
    pg.fill('#ds_c', 'tpe'); pg.fill('#ds_n', 'Taipéi'); pg.click('[data-dsa=sv]'); pg.wait_for_timeout(80)
    chk(pg.evaluate("PORTS.TPE") == 'Taipéi', 'agrega el destino TPE · Taipéi')
    pg.click('[data-dsa="off:CAN"]'); pg.wait_for_timeout(80)
    # consignatario nuevo
    pg.click('[data-cna=new]'); pg.fill('#cn_k', 'ocean space'); pg.fill('#cn_n', 'Ocean Space International Co Ltd'); pg.click('[data-cna=sv]'); pg.wait_for_timeout(80)
    chk('al menos un destino' in pg.inner_text('#cn_m') and pg.input_value('#cn_n') == 'Ocean Space International Co Ltd', 'pide al menos un destino y conserva lo escrito')
    pg.check('[data-cnp][value=TPE]'); pg.fill('#cn_c', 'Sr. Lin · +886 2 0000 0000'); pg.click('[data-cna=sv]'); pg.wait_for_timeout(80)
    n = pg.evaluate("CONS.length"); oc = pg.evaluate("CONS[CONS.length-1]")
    chk(n == 8 and oc['k'] == 'OCEAN SPACE' and oc['p'] == ['TPE'], 'agrega OCEAN SPACE con destino TPE')
    pg.click('[data-cna="ed:4"]'); pg.fill('#cn_k', 'YISHUNHAI'); pg.click('[data-cna=sv]'); pg.wait_for_timeout(80)
    chk('Ya hay un consignatario' in pg.inner_text('#cn_m'), 'no deja repetir la clave')
    pg.click('[data-cna=no]'); pg.click('[data-cna="off:2"]'); pg.wait_for_timeout(80)
    # orden con lo nuevo
    pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '26/10/2026'); pg.click('[data-oa=new]'); pg.wait_for_timeout(80)
    cities = pg.eval_on_selector_all('#ol_city option', 'e=>e.map(o=>o.value)')
    chk('TPE' in cities and 'CAN' not in cities, 'la orden ofrece TPE y ya no CAN (oculto)')
    pg.select_option('#ol_city', 'PVG'); pg.wait_for_timeout(80)
    chk('Chaozhixin' not in pg.inner_text('#ol_cons'), 'un consignatario oculto ya no se ofrece')
    pg.select_option('#ol_city', 'TPE'); pg.wait_for_timeout(80); pg.select_option('#ol_cons', str(n - 1)); pg.fill('#ol_z0', '5'); pg.fill('#ol_tar', '0'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(120)
    chk(pg.evaluate("ST.P.some(p=>p.n.startsWith('TPE · OCEAN SPACE'))"), 'el embarque nace como «TPE · OCEAN SPACE · …»')
    r = pg.evaluate("(async()=>{try{const o=ST.OR[ST.OR.length-1];const d=await pdfMake('ord',o.id);return !!d&&d.u8.length>1000}catch(e){return String(e)}})()")
    chk(r is True, f'el PDF de la orden sale con el consignatario nuevo ({r})')
    # todas las maquilas
    pg.evaluate("mqSet(3);render()"); chk(pg.evaluate("PORTS.TPE") == 'Taipéi' and pg.evaluate("CONS.length") == 8, 'David ve los mismos consignatarios y destinos')
    keys = pg.evaluate("[...encodeAll().keys()].filter(k=>/^(K|X)\\//.test(k)).length")
    chk(keys == 8 + 7, 'se comparten sin prefijo de maquila (8 consignatarios + 7 destinos)')
    c = json.loads(pg.evaluate("JSON.stringify(cleanST(mqDump()))"))
    chk(len(c['CN']) == 8 and any(d['c'] == 'TPE' for d in c['DS']), 'el respaldo conserva consignatarios y destinos')
    d = pg.evaluate("decodeST(new Map([...encodeST()].map(([k,v])=>[k,v[1]]))).CN.length")
    chk(d == 8, 'decodeST los trae')
    for w_, h_ in [(820, 1180), (390, 844)]:
        pg.set_viewport_size({'width': w_, 'height': h_}); pg.evaluate("go('admin')"); pg.wait_for_timeout(120)
        pg.click('[data-cna="ed:0"]'); pg.wait_for_timeout(80)
        chk(not overflow(pg), f'Administración con el consignatario abierto sin scroll de lado en {w_} px')
        hs = pg.eval_on_selector_all('.cnp .chk', 'e=>e.map(x=>x.getBoundingClientRect().height)'); chk(min(hs) >= 44, f'casillas de destino de 44 px o más en {w_} px')
        pg.locator('#conss').screenshot(path=os.path.join(OUT, f'cons_{w_}.png')); pg.click('[data-cna=no]')
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
