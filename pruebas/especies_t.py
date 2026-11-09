"""v1.18.0 · Especies (pedido del usuario, 23/oct/2026: «en entradas un dato "especie"… en el PDF… diferentes especies en los tanques»).
- Administración → Especies (solo Administrador): Langosta Roja de inicio; agregar, editar (nombre y nombre en inglés) y ocultar.
- Entrada (vista completa y hoja de Modo piso) pide la especie; se ve en la tabla, el lote y el tablero de tanques.
- Tanques y la hoja de compradores separan kilos por especie y talla. Lo pedido solo resta de los totales por talla.
- PDF de Entrada con columna Especie; Hoja de empaque (Formato 06) con la especie de los lotes empacados.
- Se comparte entre equipos (WN / encodeST / decodeST) y sobrevive a un respaldo (cleanST). Los lotes de antes = Langosta Roja.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/especies_t.py"""
from playwright.sync_api import sync_playwright
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from recep import recibir
import os, re, json, tempfile
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
OUT = os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-'); os.makedirs(OUT, exist_ok=True)
seed = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')))
seed['U'].append({'id': 4, 'name': 'Compras Shanghai', 'email': 'compras@cliente.cn', 'pw': 'x', 'role': 'cliente', 'notify': False, 'mq': [1]})  # usuario SOLO para pruebas
seed = json.dumps(seed)
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em='admin@propesa.mx', pw='admin123'):
    pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0");localStorage.setItem("propesa-kp","0")}', seed); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def pdf_text(pg, k, arg):
    raw = pg.evaluate(f"(async()=>{{const d=await pdfMake('{k}','{arg}');return Array.from(d.u8).map(c=>String.fromCharCode(c)).join('')}})()")
    return ' '.join(re.findall(r'\(((?:[^()\\]|\\.)*)\)\s*Tj', raw)).replace('\\(', '(').replace('\\)', ')')
def sin_desborde(pg): return not pg.evaluate("document.documentElement.scrollWidth>innerWidth+1")
def entrada(pg, lot, tank, sp_txt, kgs=(100, 20, 0, 0)):
    sp = pg.evaluate(f"(esAll().find(e=>e.n=={sp_txt!r})||{{}}).id") if sp_txt else None  # v1.42.0: recepción por tinas
    recibir(pg, lot, pv='1', kz=kgs, tank=tank, fecha='23/10/2026', hora='08:15', sp=sp)
R = lambda pg, l: pg.evaluate(f"(R_('{l}')||{{}}).sp")

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg)
        # ---------- 1. Administración → Especies ----------
        pg.evaluate("go('admin:cat')"); card = pg.locator('#esps')
        chk(card.count() == 1 and 'Langosta Roja' in card.inner_text() and 'Red lobster' in card.inner_text(), f'{vw} Administración → Especies con Langosta Roja de inicio')
        chk(pg.evaluate("ST.ES===undefined"), 'sin cambios no se crea la lista (se usa la de inicio)')
        pg.click('[data-esa="off:1"]'); chk(pg.evaluate("ST.ES===undefined||!ST.ES[0].off"), 'no se puede ocultar la única especie')
        pg.click('[data-esa=new]'); pg.click('[data-esa=sv]'); chk('Escribe el nombre' in pg.inner_text('#app .fer'), 'nombre obligatorio (v1.36.0: junto al campo)')
        pg.fill('#es_n', 'langosta roja'); pg.click('[data-esa=sv]'); chk('Ya hay una especie' in pg.inner_text('#app .fer'), 'no se repite el nombre')
        pg.fill('#es_n', 'Langosta Azul'); pg.fill('#es_e', 'Blue lobster'); pg.click('[data-esa=sv]'); pg.wait_for_timeout(100)
        es = pg.evaluate("ST.ES")
        chk(len(es) == 2 and es[0]['id'] == 1 and es[1]['n'] == 'Langosta Azul' and es[1]['en'] == 'Blue lobster', f'especie agregada {es}')
        az = es[1]['id']
        pg.click(f'[data-esa="ed:{az}"]'); pg.fill('#es_e', 'Blue spiny lobster'); pg.click('[data-esa=sv]'); pg.wait_for_timeout(80)
        chk(pg.evaluate("ST.ES[1].en") == 'Blue spiny lobster', 'se edita el nombre en inglés')
        pg.click(f'[data-esa="ed:{az}"]'); pg.fill('#es_e', 'Blue lobster'); pg.click('[data-esa=sv]'); pg.wait_for_timeout(80)
        hs = pg.evaluate("[...document.querySelectorAll('#esps .btn')].map(e=>Math.round(e.getBoundingClientRect().height))")
        chk(min(hs) >= 44, f'botones de 44 px o más {hs}'); chk(sin_desborde(pg), f'{vw} Administración sin desborde')
        pg.screenshot(path=f'{OUT}/esp_admin_{vw[0]}.png', full_page=True)

        # ---------- 2. Entrada en la vista completa ----------
        pg.evaluate("RT=null;go('rtin')")
        ops = pg.evaluate("[...document.querySelectorAll('#rt_sp option')].map(o=>o.textContent)")
        chk(ops == ['Langosta Roja', 'Langosta Azul'] and pg.input_value('#rt_sp') == '1', f'la entrada pide la especie (Langosta Roja de inicio) {ops}')
        pg.evaluate("RT=null")
        entrada(pg, 'WLRAZ231026', 'T1', 'Langosta Azul', (40, 10, 0, 0))
        chk(R(pg, 'WLRAZ231026') == az, 'el lote guarda la especie elegida')
        entrada(pg, 'WLRRO231026', 'T2', None)
        chk(R(pg, 'WLRRO231026') == 1, 'sin cambiarla queda Langosta Roja')
        chk(R(pg, 'WLRCO051026A') is None and pg.evaluate("esOf(R_('WLRCO051026A')).n") == 'Langosta Roja', 'los lotes de antes son Langosta Roja')
        pg.evaluate("go('lote:WLRAZ231026')"); chk('Langosta Azul' in pg.inner_text('.cd.head'), 'el lote dice su especie')
        pg.click('[data-a=el]'); chk(pg.input_value('#rt_sp') == str(az), 'Editar trae la especie'); pg.select_option('#rt_sp', '1'); pg.click('[data-rt=sv]'); pg.wait_for_timeout(100)
        chk(R(pg, 'WLRAZ231026') == 1, 'se puede corregir la especie'); pg.click('[data-a=el]'); pg.select_option('#rt_sp', str(az)); pg.click('[data-rt=sv]'); pg.wait_for_timeout(100)
        pg.evaluate("FOLD['ent-tq']=true;go('recepcion')"); t = pg.inner_text('table.ent')
        chk('Langosta Azul' in t and 'Langosta Roja' in t, 'la tabla de Entrada muestra la especie de cada lote')

        # ---------- 3. Tanques por especie ----------
        pg.evaluate("FOLD['ent-tq']=true;TQSEL='T1';render()"); det = pg.inner_text('.tqc')
        hh = pg.evaluate("[...document.querySelectorAll('.tqc .tqsp')].map(e=>e.textContent)")
        k_az = pg.evaluate("bal('WLRAZ231026')"); k_ro = pg.evaluate("ST.R.filter(r=>r.tank=='T1'&&esOf(r).id==1&&!r.closed).reduce((a,r)=>a+Math.max(0,bal(r.lot)),0)")
        chk(len(hh) == 2 and hh[0].startswith('Langosta Roja') and hh[1].startswith('Langosta Azul') and '50.0 kg' in hh[1], f'el tanque separa kilos por especie {hh}')
        chk(pg.locator('.tqc .tqsz').count() == 2, 'una lista de tallas por especie')
        chk('Langosta Azul' in pg.inner_text('.tqspt') and 'Langosta Roja' in pg.inner_text('.tqspt'), 'arriba: kilos de cada especie en todos los tanques')
        pg.evaluate("TQSEL='T2';render()"); hh = pg.evaluate("[...document.querySelectorAll('.tqc .tqsp')].map(e=>e.textContent)")
        chk(hh == ['Langosta Roja'], f'con una sola especie, solo su nombre {hh}')
        chk(sin_desborde(pg), f'{vw} Entrada sin desborde'); pg.evaluate("FOLD['ent-tq']=true;TQSEL='T1';render()"); pg.screenshot(path=f'{OUT}/esp_tanques_{vw[0]}.png', full_page=True)

        # ---------- 4. Hoja de entradas (Modo piso) ----------
        pg.evaluate("PEN=null;setPiso(true);go('pent')")
        sel = '[data-pr="1:sp"]'
        chk(pg.locator(sel).count() == 1 and pg.input_value(sel) == '1', 'la hoja de Modo piso pide la especie (Langosta Roja de inicio)')
        hs = pg.evaluate(f"document.querySelector('{sel}').getBoundingClientRect().height"); chk(hs >= 44, f'selector de especie de 44 px o más ({hs})')
        pg.select_option('[data-pr="1:origin"]', '1'); pg.select_option('[data-pr="1:tank"]', 'T3'); pg.select_option(sel, str(az))
        pg.fill('[data-pr="1:lot"]', 'WLRPISO231026'); pg.fill('[data-pr="1:k0"]', '30')
        for k, v in {'tempT': '58', 'tempP': '60', 'kgbox': '18', 'desp': '0'}.items(): pg.fill(f'[data-pr="1:{k}"]', v)
        pg.screenshot(path=f'{OUT}/esp_piso_{vw[0]}.png', full_page=True)
        chk(sin_desborde(pg), f'{vw} hoja de Modo piso sin desborde')
        pg.click('[data-pa=save]'); pg.wait_for_timeout(120)
        chk(R(pg, 'WLRPISO231026') == az, 'Modo piso guarda la especie')
        chk(pg.evaluate("document.querySelector('[data-pr=\"1:sp\"]').disabled"), 'guardada, la especie ya no se cambia en la hoja')
        pg.evaluate("setPiso(false);FOLD['ent-tq']=true;go('recepcion')")

        # ---------- 5. PDF de Entrada y Hoja de empaque ----------
        tx = pdf_text(pg, 'ent', '')
        chk('Especie' in tx and 'Langosta Azul' in tx and 'Langosta Roja' in tx, 'el PDF de Entrada trae la columna Especie')
        oid = pg.evaluate("""(()=>{const o={id:uidN(),etd:'2026-10-24',lines:[{id:1,city:'PVG',cons:0,boxes:2}],sh:{}};ST.OR.push(o);syncShip(o,'PVG',0);
          const d=o.sh['PVG|0'];['WLRAZ231026','WLRRO231026'].forEach((l,i)=>ST.B[l].push({c:20,k:'B',d,o:o.id+'.1',seq:uidN(),ps:i+1}));save();return o.id})()""")
        chk(pg.evaluate(f"f6Esp(ST.OR.find(o=>o.id=={oid}))") == 'Langosta Azul, Langosta Roja', 'la hoja de empaque toma la especie de los lotes empacados')
        chk('Especie: Langosta Azul, Langosta Roja' in pg.evaluate(f"f6Txt(ST.OR.find(o=>o.id=={oid}))"), 'y sale en el texto del correo')
        tx = pdf_text(pg, 'ord', str(oid)); chk('Langosta Azul' in tx, 'y en el PDF de la orden')
        pg.evaluate(f"go('orden:{oid}')"); chk('Langosta Azul' in pg.inner_text('#app'), 'y en la hoja de la pantalla')
        chk(pg.evaluate("f6Esp({lines:[],sh:{}})") == 'Langosta Roja', 'sin hieleras empacadas dice Langosta Roja')

        # ---------- 6. Compradores: kilos por especie ----------
        d = pg.evaluate("WN.D(dispCalc())")
        chk([x[0] for x in d['s']] == ['Langosta Roja', 'Langosta Azul'], f'la hoja de compradores separa por especie (en español desde la v1.30.0) {[x[0] for x in d["s"]]}')
        ks = pg.evaluate("Math.round(ST.R.filter(r=>!r.closed&&bal(r.lot)>0).reduce((a,r)=>a+S.reduce((b,z)=>b+Math.max(0,bal(r.lot,z)),0),0))")
        chk(abs(sum(sum(x[1]) for x in d['s']) - ks) <= 1, f'los kilos por especie suman lo que hay en tanques ({ks} g)')
        chk(pg.evaluate("JSON.stringify(WN.D({...dispCalc(),s:[['<b>x</b>',[1,2,3,4]],[5,[1]],'z']}).s)") == '[["bx/b",[1,2,3,4]]]', 'lo que llega de la base se limpia (WN.D)')
        pg.evaluate("signOut()"); pg.fill('#le', 'compras@cliente.cn'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
        t = pg.inner_text('#app')
        chk('En tanques por especie' in t and 'Langosta Azul' in t and 'Langosta Roja' in t, 'el comprador ve las especies')
        chk('Blue lobster' not in t and 'WLR' not in t and 'Tanque' not in t, 'en español, sin lotes ni tanques')
        chk(sin_desborde(pg), f'{vw} pantalla del comprador sin desborde'); pg.screenshot(path=f'{OUT}/esp_cliente_{vw[0]}.png', full_page=True)
        pg.evaluate("signOut()"); pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'admin123'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)

        # ---------- 7. Se comparte y sobrevive a un respaldo ----------
        rec = pg.evaluate("Object.fromEntries([...encodeST()].filter(([k])=>k.startsWith('E/')||k=='R/WLRAZ231026').map(([k,v])=>[k,v[1]]))")
        chk(f'E/{az}' in rec and rec[f'E/{az}']['n'] == 'Langosta Azul' and 'E/1' in rec and rec['R/WLRAZ231026'].get('sp') == az, 'viaja como registros E/<id> y el lote con su sp')
        rt = pg.evaluate("(()=>{const d=decodeST(new Map([...encodeST()].map(([k,v])=>[k,v[1]])));return [d.ES.map(x=>x.n),d.R.find(r=>r.lot=='WLRAZ231026').sp]})()")
        chk(rt == [['Langosta Roja', 'Langosta Azul'], az], f'otro equipo lo arma igual {rt}')
        ck = pg.evaluate("(()=>{const c=cleanST(JSON.parse(JSON.stringify({...ST,ES:[...ST.ES,{id:0,n:'x'},{id:9,n:''},{id:77,n:'Lan<g>osta',en:'a&b'}]})));return [c.ES.map(x=>x.n),c.R.find(r=>r.lot=='WLRAZ231026').sp,c.ES[2].en]})()")
        chk(ck == [['Langosta Roja', 'Langosta Azul', 'Langosta'], az, 'ab'], f'el respaldo conserva especies y limpia lo malo {ck}')
        chk(pg.evaluate("WN.E({id:5,n:'  Camarón   azul ',en:null,off:1})") == {'id': 5, 'n': 'Camarón azul', 'en': '', 'off': True}, 'WN.E limpia lo que llega de la base')

        # ---------- 8. Ocultar y otros roles ----------
        pg.evaluate("go('admin:cat')"); pg.click(f'[data-esa="off:{az}"]'); pg.wait_for_timeout(80)
        pg.evaluate("RT=null;go('rtin')")
        chk(pg.evaluate("[...document.querySelectorAll('#rt_sp option')].map(o=>o.textContent)") == ['Langosta Roja'], 'una especie oculta ya no se ofrece')
        pg.evaluate("RT=null;go('lote:WLRAZ231026')"); pg.click('[data-a=el]')
        chk(pg.input_value('#rt_sp') == str(az), 'pero el lote que la tiene la conserva al editar'); pg.evaluate("RT=null;go('recepcion')")
        pg.evaluate("go('admin:cat')"); pg.click(f'[data-esa="off:{az}"]'); pg.wait_for_timeout(80)
        pg.evaluate("signOut()"); pg.fill('#le', 'consulta@propesa.mx'); pg.fill('#lp', 'ver123'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
        pg.evaluate("go('admin:cat')")
        chk(pg.locator('[data-esa]').count() == 0 and pg.locator('.cli').count() == 1, 'Consulta (solo inventario) no cambia especies')
        pg.close()
    # tema oscuro, texto «Muy grande»
    pg = b.new_page(viewport={'width': 820, 'height': 1000}, color_scheme='dark'); pg.on('pageerror', lambda e: errs.append(str(e)))
    entrar(pg); pg.evaluate("localStorage.setItem('propesa-fs','20')"); pg.reload(); pg.wait_for_timeout(200)
    pg.evaluate("ST.ES=[...ES0,{id:2,n:'Langosta Azul',en:'Blue lobster'}];ST.R[1].sp=2;save();FOLD['ent-tq']=true;go('recepcion')")
    chk(sin_desborde(pg), '820 px, oscuro y texto 20 px: Entrada sin desborde'); pg.screenshot(path=f'{OUT}/esp_oscuro_820.png', full_page=True)
    pg.evaluate("PEN=null;setPiso(true);go('pent')"); chk(sin_desborde(pg), '820 px, oscuro y texto 20 px: hoja de Modo piso sin desborde'); pg.screenshot(path=f'{OUT}/esp_piso_oscuro_820.png', full_page=True)
    b.close()
print('ERRS', errs)
if errs: print('FAIL errores en la página')
