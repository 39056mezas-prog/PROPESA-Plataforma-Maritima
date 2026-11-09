import sys
"""v1.22.0 · PDF a color por talla (pedido del usuario, 26/oct/2026):
«quiero que en los pdf salga el color respectivo de cada talla y también gramaje… determinado a cada maquila… que toda la tabla sea de cada color».
- Cada PDF con tallas trae la leyenda: color, nombre, gramaje y nombre del color, de la maquila abierta.
- Las columnas de talla (y de categoría) llevan el encabezado del color y la columna teñida; las celdas de talla/categoría van del color.
- En otra maquila con tallas propias (Abel: Chica café «26-32 piezas», Débil morada) el PDF usa las de Abel; PROPESA no cambia.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/pdf_tallas_t.py"""
import os, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recep import recibir
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
OUT = os.environ.get('OUT', '/tmp/propesa-pruebas'); os.makedirs(OUT, exist_ok=True)
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
def login(pg, em):
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def rg(h):
    h = h.lstrip('#'); return ' '.join(f'{int(h[i:i+2], 16) / 255:.3f}' for i in (0, 2, 4)) + ' rg'
PDFS = [('ent', None), ('ord', None), ('emp', None), ('emb', 0), ('hrec', '01/10/2026|31/10/2026|'), ('henv', '01/10/2026|31/10/2026|'), ('hexi', None), ('hcon', '01/10/2026|31/10/2026|')]
def pdf(pg, k, a):
    return pg.evaluate("([k,a])=>(async()=>{try{const d=await pdfMake(k,a);let s='';d.u8.forEach(c=>s+=String.fromCharCode(c));return s}catch(e){return 'ERR '+e}})()", [k, a])
def flow(pg, lot, pfx):
    recibir(pg, lot, pv='1', kz=['200', '120'], fecha='26/10/2026', tt='58')
    pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '26/10/2026'); pg.click('[data-oa=new]'); pg.select_option('#ol_city', 'PVG'); pg.fill('#ol_z0', '1'); pg.fill('#ol_z1', '1'); pg.fill('#ol_tar', '0'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(150)
    pg.evaluate("go('empaque')"); pg.locator('[data-go^="empacar:"]').first.click(); pg.wait_for_timeout(100)
    k0, k1 = pg.evaluate("TKEY[0]"), pg.evaluate("TKEY[1]")
    pg.fill('#pk_c0', '28'); pg.click(f'#pkr0 [data-pk="k:0:{k0}"]'); pg.wait_for_timeout(100)
    pg.fill('#pk_c0', '24'); pg.click(f'#pkr0 [data-pk="k:0:{k1}"]'); pg.wait_for_timeout(100)
    pg.evaluate(f"post('CONGELACION','{lot}',S[0],-2,0,null,'folio 1');save()")
    pg.evaluate("ST.OR.forEach(o=>{o.f={...(o.f||{}),hf:'08:00',re:'Ana Torres',ev:'S',pl:'X',ch:'X',tel:'0',tp:'48',to:'T1',tq:'T1'}});save();go('emb:0')"); pg.click('[data-a=cp]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("ST.P[0]&&ST.P[0].closed"), f'{pfx}: entrada, orden, empaque, congelación y embarque cerrado')
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1)")
    flow(pg, 'WLRCO261026', 'PROPESA')
    red, wht, grn = rg('#E5484D'), rg('#FFFFFF'), rg('#30A46C')
    for k, a in PDFS:
        s = pdf(pg, k, a)
        ok = not s.startswith('ERR') and len(s) > 1000
        chk(ok, f'PROPESA: PDF {k} se genera ({s[:60] if not ok else len(s)})')
        if not ok: continue
        open(os.path.join(OUT, f'tallas_{k}.pdf'), 'wb').write(s.encode('latin-1'))
        chk('(TALLAS' in s and '(Chica)' in s and '(491-610 g)' in s and '(Mediana)' in s and '(611-850 g)' in s and '(Despatada)' in s and '(Sin gramaje)' in s, f'PROPESA {k}: leyenda con nombre y gramaje de cada talla')
        chk(red in s, f'PROPESA {k}: lleva el rojo de Mediana')
    # tinte de columna: el motor pinta la columna de Mediana con su color claro
    t = pg.evaluate("pdfTint('#E5484D',.22)"); s = pdf(pg, 'ent', None)
    chk(rg(t) in s, f'Entrada: la columna de Mediana va teñida de rojo claro ({t})')
    t2 = pg.evaluate("pdfTint('#E5484D',.45)"); chk(rg(t2) in s, 'Entrada: el total de Mediana va en un rojo un poco más fuerte')
    s = pdf(pg, 'emb', 0); chk(pg.evaluate("RC.R[1]") == '#E5484D' and rg('#E5484D') in s, 'Embarque: la categoría Rojo va de su color en el detalle por hielera')
    # --- Abel con tallas propias ---
    pg.evaluate("mqSet(2);go('admin:cat')"); pg.wait_for_timeout(150)
    pg.click('[data-sza="ed:491-610"]'); pg.fill('#sz_r', '26-32 piezas'); pg.evaluate("document.getElementById('sz_c').value='#8b5a2b'"); pg.fill('#sz_cn', 'Café'); pg.click('[data-sza=sv]'); pg.wait_for_timeout(100)
    pg.click('[data-sza="ed:611-850"]'); pg.fill('#sz_r', '600-900'); pg.click('[data-sza=sv]'); pg.wait_for_timeout(100)
    chk(pg.evaluate("ST.SZ[0].c") == '#8B5A2B' and pg.evaluate("ST.SZ[1].r") == '600-900', 'Abel: Chica café «26-32 piezas» y Mediana 600-900')
    flow(pg, 'WLRAB261026', 'Abel')
    brown = rg('#8B5A2B')
    for k, a in PDFS:
        s = pdf(pg, k, a)
        if s.startswith('ERR'): chk(False, f'Abel: PDF {k} ({s[:80]})'); continue
        open(os.path.join(OUT, f'tallas_abel_{k}.pdf'), 'wb').write(s.encode('latin-1'))
        chk('MAQUILA ABEL' in s and '(26-32 piezas)' in s and '(600-900 g)' in s and '(Caf' in s and brown in s and '(491-610 g)' not in s, f'Abel {k}: leyenda y colores de Abel (café, 26-32 piezas, 600-900 g)')
    s = pdf(pg, 'emb', 0); chk('(MAQUILA)' in s and '(ABEL)' in s and '(MAQUILA ABEL)' in s, 'v1.23.0: el nombre de la maquila va en grande arriba (ABEL) y en el encabezado de las demás páginas (MAQUILA ABEL)')
    pg.evaluate("mqSet(1);render()"); s = pdf(pg, 'ent', None)
    chk('(491-610 g)' in s and brown not in s, 'PROPESA sigue con sus tallas y colores')
    chk('(MAQUILA)' in s and '(PROPESA)' in s, 'v1.23.0: en PROPESA también dice la maquila en grande')
    # una maquila sin rango en una talla: «Sin gramaje»; un rango de piezas no lleva «g»
    chk(pg.evaluate("szGr('26-32 piezas')") == '26-32 piezas' and pg.evaluate("szGr('1221-up')") == '1221-UP g' and pg.evaluate("szGr('491-610')") == '491-610 g', 'gramaje: solo los rangos de números llevan «g»')
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
