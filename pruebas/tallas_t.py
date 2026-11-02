"""v1.19.0 · Tallas de cada maquila y Despatada (pedido del usuario, 26/oct/2026).
- De inicio: Chica, Mediana, Grande, Jumbo y Despatada (gris). La despatada entra al tanque, se pide en la orden, se empaca como
  categoría y sale del tanque al cerrar el embarque.
- Administración → «Tallas de <maquila>»: editar nombre, rango, color (el del tape) y nombre del color; agregar; ocultar. Cada
  maquila tiene las suyas: lo que cambia Abel no cambia PROPESA.
- Las pantallas usan las tallas de la maquila abierta: Entrada, hoja de Modo piso, tablero de tanques, orden, empaque (teclado),
  embarque, PDF; la pantalla de compradores usa los nombres en inglés de PROPESA.
- Se comparte (registro 'Z/tallas' con prefijo de la maquila) y sobrevive a un respaldo. Sin desbordes en 390/820/1440 px.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/tallas_t.py"""
import os, json
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
OUT = os.environ.get('OUT', '/tmp/propesa-pruebas'); os.makedirs(OUT, exist_ok=True)
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',role:'piso',notify:true},{id:4,name:'Compras',email:'compras@cliente.cn',role:'cliente',notify:false,mq:[1]}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
def login(pg, em):
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx')
    pg.evaluate("mqSet(1);go('recepcion')"); pg.wait_for_timeout(100)
    chk(pg.evaluate("TNM") == ['Chica', 'Mediana', 'Grande', 'Jumbo', 'Despatada'], 'de inicio: Chica, Mediana, Grande, Jumbo y Despatada')
    # Entrada con despatada
    pg.click('[data-a=nf]'); chk(pg.locator('#fk4').count() == 1 and 'Despatada' in pg.inner_text('label.sz4'), 'la Entrada pide kg de Despatada')
    pg.fill('#fl', 'WLRCO261026'); pg.select_option('#fo', '1'); pg.fill('#fkb', '36'); pg.fill('#ftt', '58'); pg.fill('#ftp', '59'); pg.fill('#fdes', '0')
    for i, v in enumerate([100, 50, 0, 0, 40]): pg.fill(f'#fk{i}', str(v))
    chk(pg.inner_text('#ftot').startswith('190'), 'el total suma la despatada (190 kg)')
    pg.click('[data-a=sv]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("bal('WLRCO261026','desp')") == 40000, 'la despatada queda en el tanque (40 kg)')
    pg.evaluate("go('recepcion')"); pg.wait_for_timeout(100)
    chk('Despatada' in pg.inner_text('.tqkey') if pg.locator('.tqkey').count() else False, 'el tablero de tanques muestra la talla Despatada')
    # orden con despatada, empaque con su categoría, salida al cerrar
    pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '26/10/2026'); pg.click('[data-oa=new]'); pg.select_option('#ol_city', 'PVG')
    # v1.25.0 (usuario, 29/oct): la despatada es merma: la orden ya no la pide (en Empaque la Gris se agrega como extra, v1.28.0)
    chk(pg.locator('#ol_z4').count() == 0 and pg.locator('#ol_z0').count() == 1, 'la orden ya no pide hieleras de Despatada')
    pg.fill('#ol_n', '2'); pg.fill('#ol_tar', '0'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("ST.OR[0].lines[0].boxes") == 2, 'la orden guarda 2 hieleras (sin tallas)')
    pg.evaluate("go('empaque')"); pg.locator('[data-go^="empacar:"]').first.click(); pg.wait_for_timeout(150)
    # v1.28.0 (usuario, 29/oct): la Gris ya no se elige en el teclado ni en las hieleras; se agrega aparte como extra
    chk(pg.locator('#pkr0 [data-pk="k:0:D"]').count() == 0 and pg.locator('#gxc').count() == 1, 'la hielera ya no ofrece Gris; sale «Hieleras grises · extra»')
    pg.evaluate("localStorage.setItem('propesa-kp','1');KPON=true;render()"); pg.wait_for_timeout(100)
    chk(pg.locator('[data-kp="k:D"]').count() == 0 and pg.locator('[data-kp="k:B"]').count() == 1, 'el teclado de empaque ya no tiene la categoría Gris')
    pg.evaluate("localStorage.setItem('propesa-kp','0');KPON=false;render()"); pg.wait_for_timeout(100)
    pg.fill('#pk_c0', '30'); pg.click('#pkr0 [data-pk="k:0:B"]'); pg.wait_for_timeout(100)
    pg.fill('#gx_c', '25'); pg.click('[data-gx=add]'); pg.wait_for_timeout(100)

    chk(pg.evaluate("ST.B['WLRCO261026'].map(b=>b.k).sort().join()") == 'B,D', 'se empacan una hielera Blanco y una Gris')
    pg.evaluate("ST.OR.forEach(o=>{o.f={...(o.f||{}),hf:'08:00',re:'Ana Torres',ev:'S',pl:'X',ch:'X',tel:'0',tp:'48',to:'T1',tq:'T1'}});save();go('emb:0')"); pg.wait_for_timeout(100)
    chk('Despatada' in pg.inner_text('main'), 'el embarque muestra la talla Despatada')
    pg.click('[data-a=cp]'); pg.wait_for_timeout(200)
    chk(pg.evaluate("bal('WLRCO261026','desp')") == 24000 and pg.evaluate("bal('WLRCO261026','491-610')") == 84000, 'al cerrar salen 16 kg de Despatada y 16 de Chica')
    for k_, a_ in [['emb', 0], ['ent', None], ['ord', None]]:
        r_ = pg.evaluate("([k,a])=>{try{const b=pdfMake(k,a);return b&&(b.size||b.length||1)>0}catch(e){return String(e)}}", [k_, a_])
        chk(r_ is True, f'PDF {k_} con Despatada se arma sin errores ({r_})')
    # compradores
    d = json.loads(pg.evaluate("JSON.stringify(WN.D(dispCalc()))"))
    chk(d['n'][4][0] == 'Despatada' and len(d['z']) == 5, 'la hoja de compradores manda los nombres de las tallas (en español desde la v1.30.0)')
    # Administración → Tallas de Abel
    pg.evaluate("mqSet(2);go('admin')"); pg.wait_for_timeout(150)
    chk('Tallas de Abel' in pg.inner_text('#szs'), 'Administración: «Tallas de Abel»')
    pg.click('[data-sza="ed:491-610"]'); pg.fill('#sz_r', '26-32 piezas'); pg.evaluate("document.getElementById('sz_c').value='#8b5a2b'"); pg.fill('#sz_cn', 'Café'); pg.click('[data-sza=sv]'); pg.wait_for_timeout(100)
    chk(pg.evaluate("ST.SZ[0].r") == '26-32 piezas' and pg.evaluate("ST.SZ[0].c") == '#8B5A2B' and pg.evaluate("RC.B[0]") == 'Café', 'Abel: Chica con rango 26-32 piezas y color Café')
    chk(pg.evaluate("STX[1].SZ") is None, 'PROPESA no cambia')
    pg.click('[data-sza=new]'); pg.fill('#sz_n', 'chica'); pg.click('[data-sza=sv]'); pg.wait_for_timeout(80)
    chk('Ya hay una talla' in pg.inner_text('#sz_m') and pg.input_value('#sz_n') == 'chica', 'no deja repetir el nombre y conserva lo escrito')
    pg.fill('#sz_n', 'Débil'); pg.fill('#sz_r', ''); pg.evaluate("document.getElementById('sz_c').value='#7c3aed'"); pg.fill('#sz_cn', 'Morado'); pg.fill('#sz_e', 'Weak'); pg.click('[data-sza=sv]'); pg.wait_for_timeout(100)
    chk(pg.evaluate("TNM.length") == 6 and pg.evaluate("TNM[5]") == 'Débil', 'agrega la talla Débil al final')
    pg.click('[data-sza="off:1221-up"]'); pg.wait_for_timeout(80)
    chk(pg.evaluate("SON.length") == 5 and 3 not in pg.evaluate("SON"), 'oculta Jumbo en Abel')
    k = pg.evaluate("ST.SZ[5].k")
    pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]')
    chk(pg.locator('#fk3').count() == 0 and pg.locator('#fk5').count() == 1 and '26-32 piezas' in pg.inner_text('label.sz0'), 'la Entrada de Abel: sin Jumbo, con Débil y el rango nuevo')
    chk(pg.evaluate("getComputedStyle(document.querySelector('label.sz5 input')).borderTopColor") == 'rgb(124, 58, 237)', 'la casilla de Débil lleva su color')
    pg.fill('#fl', 'WLRCO261026'); pg.select_option('#fo', '1'); pg.fill('#fkb', '36'); pg.fill('#ftt', '58'); pg.fill('#ftp', '59'); pg.fill('#fdes', '0'); pg.fill('#fk0', '20'); pg.fill('#fk5', '-1'); pg.click('[data-a=sv]'); pg.wait_for_timeout(100)
    chk(pg.evaluate("ST.R.length") == 0 and pg.evaluate("document.activeElement.id") == 'fk5', 'un error en la talla nueva lleva a su casilla')
    pg.fill('#fk5', '12'); pg.click('[data-a=sv]'); pg.wait_for_timeout(100)
    chk(pg.evaluate(f"bal('WLRCO261026','{k}')") == 12000, 'Abel guarda 12 kg de Débil')
    # hoja de Modo piso
    pg.evaluate("setPiso(true);go('pent')"); pg.wait_for_timeout(150)
    hs = pg.eval_on_selector_all('.pnt-t thead th', 'e=>e.map(x=>x.innerText)')
    chk(any('26-32 PIEZAS' in h for h in hs) and any('DÉBIL' in h.upper() for h in hs) and not any('1221' in h for h in hs), 'la hoja de Modo piso usa las tallas de Abel')
    for w in (820, 390):
        pg.set_viewport_size({'width': w, 'height': 1000}); pg.wait_for_timeout(150)
        chk(not overflow(pg), f'hoja de Modo piso sin scroll de lado en {w} px'); pg.screenshot(path=os.path.join(OUT, f'tallas_pent_{w}.png'))
    pg.set_viewport_size({'width': 1440, 'height': 900}); pg.evaluate("setPiso(false);go('inicio')")
    # cambio de maquila: PROPESA conserva las suyas
    pg.evaluate("mqSet(1);render()"); chk(pg.evaluate("TNM.length") == 5 and pg.evaluate("RC.B[0]") == 'Blanco', 'al volver a PROPESA regresan sus tallas')
    pg.evaluate("mqSet(2);render()"); chk(pg.evaluate("TNM.length") == 6, 'y en Abel las suyas')
    # registros y respaldo
    keys = pg.evaluate("[...encodeAll().keys()].filter(k=>k.includes('Z/'))")
    chk(keys == ['q2:Z/tallas'], "se comparte como 'q2:Z/tallas' (solo Abel tiene tallas propias)")
    dump = pg.evaluate("JSON.stringify(mqDump())"); c = json.loads(pg.evaluate("JSON.stringify(cleanST(JSON.parse(%s)))" % json.dumps(dump)))
    chk(len(c['SZ']) == 6 and c['SZ'][5]['n'] == 'Débil', 'el respaldo conserva las tallas')
    rt = pg.evaluate("(()=>{const m=encodeST(2),d=decodeST(new Map([...m].map(([k,v])=>[k,v[1]])));return d.SZ.map(x=>x.n)})()")
    chk(rt[5] == 'Débil', 'decodeST trae las tallas')
    chk(pg.evaluate("WN.Z({l:[{id:'x<',k:'1',n:''}]})") is None, 'tallas con datos malos se ignoran')
    # vistas
    for w, h, theme, fs in [(1440, 900, 'light', 17), (820, 1180, 'dark', 20), (390, 844, 'light', 20)]:
        pg.set_viewport_size({'width': w, 'height': h}); pg.evaluate(f"localStorage.setItem('propesa-theme','{theme}');localStorage.setItem('propesa-fs','{fs}');applyPrefs&&applyPrefs()")
        for r in ['admin', 'recepcion', 'empaque']:
            pg.evaluate(f"go('{r}')"); pg.wait_for_timeout(120); chk(not overflow(pg), f'{r} sin scroll de lado en {w} px ({theme}, {fs} px)')
        pg.evaluate("go('admin')"); pg.locator('#szs').scroll_into_view_if_needed(); pg.screenshot(path=os.path.join(OUT, f'tallas_admin_{w}.png'))
    # comprador
    pg.evaluate("mqSet(1);me=null;render()"); login(pg, 'compras@cliente.cn')
    t = pg.inner_text('body'); chk('Despatada' in t and 'Chica' in t and 'Broken legs' not in t, 'el comprador ve las tallas en español (v1.30.0)')
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
