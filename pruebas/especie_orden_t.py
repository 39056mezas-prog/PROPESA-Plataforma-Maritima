"""v1.20.0 · Especie en cada orden (decisión del usuario, 26/oct/2026: «Sí, en cada orden»).
- Con más de una especie, la orden nueva pide la especie; las órdenes de antes son Langosta Roja (especie 1).
- Al empacar (vista completa y Modo piso) solo salen los lotes abiertos de esa especie; los lotes sin entrada que se crean al
  empacar toman la especie de la orden y no se puede elegir uno de otra especie.
- La especie se cambia en la orden mientras no tenga hieleras empacadas.
- La hoja de los compradores resta lo pedido de su especie (con tallas y sin tallas).
- Viaja a los otros equipos (WN.OR), sobrevive a un respaldo (cleanST) y sale en el PDF de órdenes y en la hoja de empaque.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/especie_orden_t.py"""
import os, json, re
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
def lot(pg, l, sp, k0, tk='T1'):
    pg.evaluate("""([l,sp,k0,tk])=>{addLot({lot:l,origin:'SCPP Ensenada SCL',pv:1,sp,tank:tk,rdate:'2026-10-25',time:'09:00',tempT:58,tempP:'60',kgbox:36,desp:0,k0,k1:0,k2:0,k3:0,k4:0});save()}""", [l, sp, k0, tk])
def pdf_text(pg, k, arg=''):
    raw = pg.evaluate(f"(async()=>{{const d=await pdfMake('{k}','{arg}');return Array.from(d.u8).map(c=>String.fromCharCode(c)).join('')}})()")
    return ' '.join(re.findall(r'\(((?:[^()\\]|\\.)*)\)\s*Tj', raw)).replace('\\(', '(').replace('\\)', ')')
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1)")
    # con una sola especie todo se ve como antes
    pg.evaluate("go('ordenes')"); pg.wait_for_timeout(80)
    chk(pg.locator('#no_sp').count() == 0, 'con una sola especie la orden no pregunta la especie')
    chk(pg.evaluate("ordSp({id:1,etd:'2026-10-01',lines:[],sh:{}})") == 1, 'una orden de antes (sin especie) es Langosta Roja')
    pg.evaluate("ST.ES=[...ES0,{id:2,n:'Langosta Azul',en:'Blue lobster'}];save()")
    lot(pg, 'WLRCO251026', 1, 100); lot(pg, 'WLRAZ251026', 2, 50, 'T2')
    pg.evaluate("go('ordenes')"); pg.wait_for_timeout(80)
    chk(pg.locator('#no_sp').count() == 1 and pg.eval_on_selector_all('#no_sp option', 'e=>e.map(o=>o.textContent)') == ['Langosta Roja', 'Langosta Azul'], 'con dos especies, la orden nueva pide la especie')
    pg.fill('#no_etd', '27/10/2026'); pg.select_option('#no_sp', '2'); pg.click('[data-oa=new]'); pg.wait_for_timeout(120)
    o1 = pg.evaluate("ST.OR[ST.OR.length-1].id")
    chk(pg.evaluate(f"ST.OR.find(o=>o.id=={o1}).sp") == 2, 'la orden guarda la especie elegida')
    chk(pg.locator(f'[data-osp="{o1}"]').count() == 1 and 'Langosta Azul' in pg.inner_text(f'[data-osp="{o1}"] option:checked'), 'la orden muestra su especie y se puede cambiar')
    pg.evaluate(f"""(()=>{{const o=ST.OR.find(o=>o.id=={o1});o.lines.push({{id:1,city:'PVG',cons:0,boxes:3,kp:16,z:S.map((_,i)=>i==0?2:0)}});syncShip(o,'PVG',0);save()}})()""")
    chk(pg.evaluate(f"ordLots(ST.OR.find(o=>o.id=={o1}))") == ['WLRAZ251026'], 'al empacar solo se ofrecen los lotes de su especie')
    pg.evaluate(f"go('empacar:{o1}.1')"); pg.wait_for_timeout(100)
    lb = pg.eval_on_selector_all('.pklb b', 'e=>e.map(x=>x.textContent)')
    chk(lb == [] or lb == ['WLRAZ251026'], f'vista completa: botones de lote solo de Langosta Azul {lb}')
    chk(pg.evaluate("PKD.lot") == 'WLRAZ251026', 'con un solo lote de la especie, ya viene elegido')
    pg.evaluate("setPiso(true);PE={key:'',lot:null};go('pemp:%s.1')" % o1); pg.wait_for_timeout(120)
    chk(pg.evaluate("PE.lot") == 'WLRAZ251026', 'Modo piso: elige solo el lote de la especie de la orden')
    pg.evaluate("PE.chg=true;render()"); pg.wait_for_timeout(80)
    ls = pg.eval_on_selector_all('[data-pe^="lot:"]', 'e=>e.map(x=>x.dataset.pe)')
    chk(ls == ['lot:WLRAZ251026'], f'Modo piso: al cambiar de lote solo salen los de esa especie {ls}')
    pg.evaluate("setPiso(false)")
    # lote sin entrada creado al empacar
    pg.evaluate(f"go('empacar:{o1}.1');PKD.ne=true;render()"); pg.wait_for_timeout(80)
    pg.fill('#ne_l', 'WLRAZ261026'); pg.select_option('#ne_p', '1'); pg.select_option('#ne_t', 'T4')
    chk(pg.evaluate("neSave()") == 'WLRAZ261026' and pg.evaluate("R_('WLRAZ261026').sp") == 2, 'el lote sin entrada que se crea al empacar es de la especie de la orden')
    pg.evaluate("PKD.ne=true;render()"); pg.wait_for_timeout(60); pg.fill('#ne_l', 'WLRCO251026')
    chk(pg.evaluate("neSave()") is None and 'langosta roja' in pg.inner_text('#ne_m') and 'langosta azul' in pg.inner_text('#ne_m'), 'no deja empacar de un lote de otra especie: %s' % pg.inner_text('#ne_m'))
    # hoja de los compradores: lo pedido resta de su especie
    d = pg.evaluate("dispCalc()")
    s = {x[0]: x for x in d['s']}
    chk(s['Blue lobster'][1][0] == 50000 - 2 * 16000 and s['Red lobster'][1][0] == 100000, f'lo pedido por talla resta de Langosta Azul y no de la Roja: {d["s"]}')
    chk(len(s['Blue lobster']) == 3 and s['Blue lobster'][2] == 16000, 'la hielera sin talla queda apartada en Langosta Azul')
    chk(d['z'][0] == 150000 - 32000 and d['u'] == 16000, 'los totales por talla siguen igual que antes')
    w = pg.evaluate("WN.D(dispCalc()).s")
    chk(any(len(x) == 3 and x[2] == 16000 for x in w), 'el apartado por especie viaja en la hoja D/disp')
    pg.evaluate("ST.U.push({id:3,name:'Compras',email:'compras@cliente.cn',role:'cliente',notify:false});save();signOut()"); pg.wait_for_timeout(150); login(pg, 'compras@cliente.cn')
    t = pg.inner_text('body')
    chk('Blue lobster' in t and 'already subtracted from each species' in t and '2 kg' in t, 'la pantalla del comprador dice que ya se restó por especie')
    pg.set_viewport_size({'width': 390, 'height': 844}); chk(not overflow(pg), 'pantalla del comprador sin desborde en 390px'); pg.set_viewport_size({'width': 1440, 'height': 900})
    pg.screenshot(path=f'{OUT}/especie_orden_cliente.png', full_page=True)
    pg.evaluate("signOut()"); pg.wait_for_timeout(150); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1)")
    # cambiar la especie
    pg.evaluate(f"go('orden:{o1}')"); pg.wait_for_timeout(80)
    pg.select_option(f'[data-osp="{o1}"]', '1'); pg.wait_for_timeout(120)
    chk(pg.evaluate(f"ST.OR.find(o=>o.id=={o1}).sp") == 1 and pg.evaluate(f"ordLots(ST.OR.find(o=>o.id=={o1}))") == ['WLRCO251026'], 'sin hieleras, la especie se cambia y cambian los lotes que se ofrecen')
    pg.select_option(f'[data-osp="{o1}"]', '2'); pg.wait_for_timeout(120)
    pg.evaluate(f"""(()=>{{const o=ST.OR.find(o=>o.id=={o1});ST.B['WLRAZ251026'].push({{c:20,k:TKEY[0],d:o.sh['PVG|0'],o:o.id+'.1',seq:uidN(),ps:1}});save();render()}})()""")
    pg.wait_for_timeout(80)
    chk(pg.locator(f'[data-osp="{o1}"]').count() == 0 and 'no se cambia' in pg.inner_text('main'), 'con hieleras empacadas ya no se cambia la especie')
    chk(pg.evaluate(f"f6Esp(ST.OR.find(o=>o.id=={o1}))") == 'Langosta Azul', 'la hoja de empaque dice la especie')
    pg.evaluate("ST.OR.push({id:uidN(),etd:'2026-10-28',lines:[],sh:{},sp:2});save()")
    chk(pg.evaluate("f6Esp(ST.OR[ST.OR.length-1])") == 'Langosta Azul', 'sin hieleras, la hoja de empaque toma la especie de la orden')
    tx = pdf_text(pg, 'ord')
    chk('Langosta Azul' in tx, 'el PDF de órdenes dice la especie')
    pg.evaluate("go('ordenes')"); pg.wait_for_timeout(80)
    chk(pg.locator('.ordt tbody tr', has_text='Langosta Azul').count() >= 1, 'la lista de órdenes dice la especie de cada una')
    # compartir y respaldo
    wo = json.loads(pg.evaluate(f"JSON.stringify(WN.OR(ST.OR.find(o=>o.id=={o1})))"))
    chk(wo['sp'] == 2, 'la especie de la orden viaja a los otros equipos')
    chk(pg.evaluate(f"cleanST(mqDump()).OR.find(o=>o.id=={o1}).sp") == 2, 'y sobrevive a un respaldo')
    chk('sp' not in json.loads(pg.evaluate("JSON.stringify(WN.OR({id:5,etd:'2026-10-01',lines:[],sh:{},sp:'x'}))")), 'una especie rara se ignora')
    for w_, h_ in [(820, 1180), (390, 844)]:
        pg.set_viewport_size({'width': w_, 'height': h_})
        for r_ in ['ordenes', f'orden:{o1}', f'empacar:{o1}.1']:
            pg.evaluate(f"go('{r_}')"); pg.wait_for_timeout(80)
            chk(not overflow(pg), f'{r_} sin desborde en {w_}px')
        pg.screenshot(path=f'{OUT}/especie_orden_{w_}.png', full_page=True)
    chk(not errs, 'sin errores de JavaScript: %s' % errs[:3])
    b.close()
print('\n%d fallas' % len(fails)); [print(' -', f) for f in fails]
raise SystemExit(1 if fails else 0)
