"""v1.11.0 · Proveedores de una lista y empacar de un lote sin entrada (pedidos del usuario, 17/oct/2026).
- El proveedor se elige de una lista (vista completa y hoja de entradas de Modo piso); la app propone el lote WLR + clave + ddmmyy.
- Administración → Proveedores: agregar, editar (nombre, clave, RFC, permiso de pesca), ocultar, pasar nombres escritos a mano.
- Empaque (vista completa y Modo piso): «+ Lote sin entrada» (lote, proveedor, tanque); queda «Sin entrada · Completar ›»; no cuenta
  en tanques ni en mortalidad; al capturar su entrada se completa y conserva sus hieleras.
- Se comparte entre equipos (WN / encodeST / decodeST) y sobrevive a un respaldo (cleanST).
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/proveedores_t.py"""
from playwright.sync_api import sync_playwright
import os, sys, re, json
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em='admin@propesa.mx', pw='admin123', piso='0'):
    pg.goto(BASE); pg.evaluate('([s,p])=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso",p);localStorage.setItem("propesa-kp","0")}', [seed, piso]); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def pdf_text(pg, k, arg):
    raw = pg.evaluate(f"(async()=>{{const d=await pdfMake('{k}','{arg}');return Array.from(d.u8).map(c=>String.fromCharCode(c)).join('')}})()")
    return ' '.join(re.findall(r'\(((?:[^()\\]|\\.)*)\)\s*Tj', raw)).replace('\\(', '(').replace('\\)', ')')
def toast(pg): return pg.inner_text('#toast') if pg.locator('#toast').is_visible() else ''
def entrada(pg, pv, fecha, extra=None):
    pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.fill('#fd', fecha); pg.select_option('#fo', str(pv))
    for k, v in {'#fh': '08:15', '#ftt': '58', '#ftp': '52-60', '#fkb': '34', '#fdes': '0', '#fk0': '100', '#fk1': '20'}.items(): pg.fill(k, v)
    if extra: extra()
    pg.click('[data-a=sv]'); pg.wait_for_timeout(120)
def nueva_orden(pg, n=5):
    return pg.evaluate(f"(()=>{{const o={{id:uidN(),etd:'2026-10-20',lines:[{{id:1,city:'PVG',cons:0,boxes:{n}}},{{id:2,city:'PVG',cons:1,boxes:2}}],sh:{{}}}};ST.OR.push(o);syncShip(o,'PVG',0);syncShip(o,'PVG',1);save();return o.id}})()")
def sin_desborde(pg): return not pg.evaluate("document.documentElement.scrollWidth>innerWidth+1")

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg)
        # ---------- 1. Entrada: proveedor de una lista y lote propuesto ----------
        pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]')
        chk(pg.evaluate("document.getElementById('fo').tagName") == 'SELECT', f'{vw} el proveedor se elige de una lista')
        ops = pg.evaluate("[...document.querySelectorAll('#fo option')].map(o=>o.textContent)")
        chk(ops == ['Elige proveedor', 'SCPP Ensenada SCL', 'SCPP Emancipación SC de RL', 'SCPP Leyes de Reforma'], f'{vw} la lista trae los 3 proveedores de hoy: {ops}')
        pg.fill('#fd', '2026-09-22'); pg.select_option('#fo', '1')
        chk(pg.input_value('#fl') == 'WLRCO220926', f'{vw} Ensenada + 22/09/26 propone WLRCO220926: {pg.input_value("#fl")}')
        pg.select_option('#fo', '2'); chk(pg.input_value('#fl') == 'WLREM220926', f'{vw} al cambiar a Emancipación cambia a WLREM220926')
        pg.fill('#fd', '2026-10-05'); chk(pg.input_value('#fl') == 'WLREM051026', f'{vw} al cambiar la fecha cambia a WLREM051026')
        pg.fill('#fl', 'WLREM051026X'); pg.select_option('#fo', '3')
        chk(pg.input_value('#fl') == 'WLREM051026X', f'{vw} si el lote se corrigió a mano, ya no se cambia solo')
        pg.fill('#fl', ''); pg.select_option('#fo', '3'); chk(pg.input_value('#fl') == 'WLRLE051026', f'{vw} borrado el lote, vuelve a proponer: WLRLE051026')
        pg.click('#fl'); pg.keyboard.type('wlrle051026b'); chk(pg.input_value('#fl') == 'WLRLE051026B', f'{vw} al tocar el lote propuesto y escribir, se reemplaza (no se pega al final): {pg.input_value("#fl")}')
        pg.select_option('#fo', ''); pg.click('[data-a=sv]'); pg.wait_for_timeout(80)
        chk('Elige el proveedor' in pg.inner_text('#app'), f'{vw} sin proveedor no se guarda y lo dice')
        pg.click('[data-a=nf]')
        entrada(pg, 1, '2026-09-22')
        r = pg.evaluate("R_('WLRCO220926')")
        chk(r and r['pv'] == 1 and r['origin'] == 'SCPP Ensenada SCL', f'{vw} el lote guarda el proveedor (id y nombre): {r and (r.get("pv"), r["origin"])}')
        pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.fill('#fd', '2026-09-22'); pg.select_option('#fo', '1')
        chk(pg.input_value('#fl') == 'WLRCO220926B', f'{vw} si ya existe, propone el siguiente: {pg.input_value("#fl")}')
        pg.click('[data-a=nf]')
        # editar un lote de antes con nombre escrito a mano
        pg.evaluate("go('lote:WLRCO061026B')"); pg.click('[data-a=el]')
        sel = pg.evaluate("(e=>e.options[e.selectedIndex].textContent)(document.getElementById('fo'))")
        chk(sel == 'Pescadores del Sur', f'{vw} al editar un lote de antes se conserva su nombre, sin textos de más: {sel}')
        pg.click('[data-a=sv]'); pg.wait_for_timeout(80)
        chk(pg.evaluate("R_('WLRCO061026B').origin") == 'Pescadores del Sur' and pg.evaluate("R_('WLRCO061026B').pv") is None, f'{vw} guardar sin cambiarlo no lo pierde')
        pg.evaluate("go('lote:WLRCO051026A')"); pg.click('[data-a=el]')
        chk(pg.input_value('#fo') == '1', f'{vw} un lote de antes con el nombre exacto de la lista sale con ese proveedor')
        pg.click('[data-a=nf]') if pg.locator('[data-a=nf]').count() else None
        # ---------- 2. Hoja de entradas (Modo piso) ----------
        pg.evaluate("PEN=null;go('pent')"); pg.wait_for_timeout(80)
        chk(pg.evaluate("document.querySelector('[data-pr=\"1:origin\"]').tagName") == 'SELECT', f'{vw} en la hoja de entradas el proveedor también es una lista')
        pg.select_option('[data-pr="1:origin"]', '3')
        hoy = pg.evaluate("dLoc()"); esp = 'WLRLE' + hoy[8:10] + hoy[5:7] + hoy[2:4]
        chk(pg.input_value('[data-pr="1:lot"]') == esp, f'{vw} la hoja propone el lote con la fecha de hoy: {pg.input_value("[data-pr=\'1:lot\']")}')
        pg.click('[data-pr="1:lot"]'); pg.keyboard.type('x'); chk(pg.input_value('[data-pr="1:lot"]') == 'X', f'{vw} en la hoja también: tocar el lote propuesto y escribir lo reemplaza')
        pg.fill('[data-pr="1:lot"]', ''); pg.select_option('[data-pr="1:origin"]', '1'); pg.select_option('[data-pr="1:origin"]', '3'); chk(pg.input_value('[data-pr="1:lot"]') == esp, f'{vw} borrado, vuelve a proponer')
        pg.select_option('[data-pr="1:tank"]', 'T2'); pg.fill('[data-pr="1:k0"]', '300')
        pg.click('[data-pr="1:k0"]'); pg.evaluate("penR(1).open=true;render()")
        for k, v in {'tempT': '58', 'tempP': '55-60', 'kgbox': '34', 'desp': '0'}.items(): pg.fill(f'[data-pr="1:{k}"]', v)
        pg.click('[data-pa=save]'); pg.wait_for_timeout(120)
        r = pg.evaluate(f"R_('{esp}')")
        chk(r and r.get('pv') == 3 and r['origin'] == 'SCPP Leyes de Reforma', f'{vw} la hoja guarda proveedor de la lista: {r and (r.get("pv"), r["origin"])}')
        chk(pg.input_value('[data-pr="1:origin"]') == '3', f'{vw} la fila guardada sigue mostrando su proveedor')
        pg.evaluate("go('recepcion')")
        # ---------- 3. Administración → Proveedores ----------
        pg.evaluate("go('admin')"); t = pg.inner_text('#provs')
        chk('SCPP Ensenada SCL' in t and 'CO' in t and 'RFC' in t and 'Permiso de pesca' in t, f'{vw} Administración tiene la lista de proveedores')
        chk('escrito' not in t.lower() and 'de antes' not in t and 'Solo el Administrador' not in t, f'{vw} sin textos sobre lotes de antes ni avisos de más')
        pg.click('[data-pva=new]'); pg.fill('#pv_n', 'SCPP Bahía Tortugas'); pg.fill('#pv_k', 'CO'); pg.click('[data-pva=sv]'); pg.wait_for_timeout(80)
        chk('ya es de SCPP Ensenada SCL' in pg.inner_text('#provs') and pg.input_value('#pv_n') == 'SCPP Bahía Tortugas', f'{vw} una clave repetida se rechaza y se conserva lo escrito')
        pg.fill('#pv_k', 'bt'); pg.fill('#pv_r', 'XYZ'); pg.click('[data-pva=sv]'); pg.wait_for_timeout(80)
        chk('Revisa el RFC' in pg.inner_text('#provs'), f'{vw} un RFC mal escrito se rechaza')
        pg.fill('#pv_r', 'SBT850101AB1'); pg.fill('#pv_p', 'PPF/DGOPA-123/26'); pg.click('[data-pva=sv]'); pg.wait_for_timeout(80)
        pv = pg.evaluate("ST.PV.find(p=>p.k=='BT')")
        chk(pv and pv['n'] == 'SCPP Bahía Tortugas' and pv['rfc'] == 'SBT850101AB1' and pv['per'] == 'PPF/DGOPA-123/26' and len(pg.evaluate("ST.PV")) == 4, f'{vw} proveedor nuevo con clave, RFC y permiso: {pv}')
        bt = pv['id']
        pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]')
        chk('SCPP Bahía Tortugas' in pg.inner_text('#fo'), f'{vw} el proveedor nuevo sale en la Entrada'); pg.fill('#fd', '2026-10-17'); pg.select_option('#fo', str(bt))
        chk(pg.input_value('#fl') == 'WLRBT171026', f'{vw} con su clave propone WLRBT171026'); pg.click('[data-a=nf]')
        # editar nombre: los lotes con ese proveedor se actualizan
        pg.evaluate("go('admin')"); pg.click('[data-pva="ed:1"]'); pg.fill('#pv_n', 'SCPP Ensenada SCL de RL'); pg.click('[data-pva=sv]'); pg.wait_for_timeout(80)
        chk(pg.evaluate("R_('WLRCO220926').origin") == 'SCPP Ensenada SCL de RL' and pg.evaluate("R_('WLRCO051026A').origin") == 'SCPP Ensenada SCL de RL', f'{vw} al cambiar el nombre, sus lotes (también los de antes con el mismo nombre) se actualizan')
        # un lote de antes se pasa a un proveedor de la lista editándolo
        pg.evaluate("go('lote:WLRCO061026B')"); pg.click('[data-a=el]'); pg.select_option('#fo', str(bt)); pg.click('[data-a=sv]'); pg.wait_for_timeout(80)
        chk(pg.evaluate("R_('WLRCO061026B').pv") == bt and pg.evaluate("R_('WLRCO061026B').origin") == 'SCPP Bahía Tortugas', f'{vw} al editar un lote de antes se le puede poner un proveedor de la lista')
        pg.evaluate("go('admin')")
        # ocultar
        pg.click(f'[data-pva="off:{bt}"]'); pg.wait_for_timeout(60)
        pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]')
        chk('Bahía Tortugas' not in pg.inner_text('#fo'), f'{vw} un proveedor oculto ya no sale para lotes nuevos'); pg.click('[data-a=nf]')
        pg.evaluate("go('lote:WLRCO061026B')"); pg.click('[data-a=el]')
        chk(pg.input_value('#fo') == str(bt), f'{vw} pero sus lotes lo siguen mostrando al editarlos'); pg.click('[data-a=nf]') if pg.locator('#fo').count() and pg.locator('[data-a=nf]').count() else None
        pg.evaluate("go('admin')")
        for i in [1, 2]: pg.click(f'[data-pva="off:{i}"]'); pg.wait_for_timeout(40)
        pg.click('[data-pva="off:3"]'); pg.wait_for_timeout(60)
        chk('al menos un proveedor' in toast(pg) and len(pg.evaluate("pvOn()")) == 1, f'{vw} no se puede ocultar el último proveedor')
        for i in [1, 2, bt]: pg.click(f'[data-pva="off:{i}"]'); pg.wait_for_timeout(40)
        chk(sin_desborde(pg), f'{vw} Administración sin desborde horizontal')
        # ---------- 4. Empacar de un lote sin entrada (vista completa) ----------
        oid = nueva_orden(pg); pg.evaluate(f"go('empacar:{oid}.1')"); pg.wait_for_timeout(80)
        chk(pg.locator('[data-nea=open]').count() == 1, f'{vw} Empaque ofrece «+ Lote sin entrada»')
        pg.click('[data-nea=open]'); pg.click('[data-nea=sv]'); pg.wait_for_timeout(60)
        chk('Escribe el lote' in pg.inner_text('#ne_m'), f'{vw} sin lote lo dice')
        pg.fill('#ne_l', 'wlrco300926'); chk(pg.input_value('#ne_l') == 'WLRCO300926', f'{vw} el lote se escribe en mayúsculas')
        pg.click('[data-nea=sv]'); pg.wait_for_timeout(60); chk('Elige el proveedor' in pg.inner_text('#ne_m'), f'{vw} pide proveedor')
        pg.select_option('#ne_p', '1'); pg.click('[data-nea=sv]'); pg.wait_for_timeout(60); chk('Elige el tanque' in pg.inner_text('#ne_m'), f'{vw} pide tanque')
        pg.select_option('#ne_t', 'T3'); pg.click('[data-nea=sv]'); pg.wait_for_timeout(100)
        r = pg.evaluate("R_('WLRCO300926')")
        chk(r and r.get('ne') and r['tank'] == 'T3' and r.get('pv') == 1 and pg.evaluate("rcv('WLRCO300926')") == 0, f'{vw} se crea el lote sin entrada, sin kilos: {r and (r.get("ne"), r["tank"], r.get("pv"))}')
        chk(pg.evaluate("PKD.lot") == 'WLRCO300926' and 'Sin entrada' in pg.inner_text('[data-pk="lot:WLRCO300926"]'), f'{vw} queda elegido para empacar y su botón dice «Sin entrada»')
        for r_ in range(2): pg.fill(f'#pk_c{r_}', str(29 + r_)); pg.click(f'#pkr{r_} [data-pk="k:{r_}:B"]')
        pg.click('[data-pk=addall]'); pg.wait_for_timeout(120)
        chk(len(pg.evaluate("ST.B['WLRCO300926']")) == 2, f'{vw} se empacan hieleras de ese lote')
        chk(sin_desborde(pg), f'{vw} Empaque sin desborde horizontal')
        # un lote que ya existe: se elige
        pg.evaluate(f"go('empacar:{oid}.2')"); pg.click('[data-nea=open]'); pg.fill('#ne_l', 'WLRCO051026A'); pg.click('[data-nea=sv]'); pg.wait_for_timeout(80)
        chk(pg.evaluate("PKD.lot") == 'WLRCO051026A' and not pg.evaluate("R_('WLRCO051026A').ne"), f'{vw} si el lote ya existe, solo se elige')
        # avisos y exclusiones
        pg.evaluate("go('recepcion')"); t = pg.inner_text('#app')
        chk('Lote WLRCO300926 · sin entrada' in t and 'tablero' not in pg.inner_text('.neb') and pg.locator('[data-ne="WLRCO300926"]').count() >= 1, f'{vw} Entrada avisa en amarillo con «Completar entrada ›»')
        chk('WLRCO300926' not in pg.inner_text('.tqd'), f'{vw} no aparece en el tablero de tanques')
        pg.evaluate("go('cierre')"); chk('WLRCO300926' not in pg.inner_text('#app'), f'{vw} no aparece en Mortalidad final')
        chk('WLRCO300926' not in pdf_text(pg, 'mort', ''), f'{vw} ni en el PDF de mortalidad')
        tx = pdf_text(pg, 'ent', '')
        chk('sin entrada' not in tx.lower() and 'WLRCO300926' not in tx and 'SBT850101AB1' in tx and 'PPF/DGOPA-123/26' in tx, f'{vw} el PDF de Entrada no menciona el lote sin entrada y trae RFC y permiso de los proveedores')
        pg.evaluate("go('lote:WLRCO300926')"); t = pg.inner_text('#app')
        chk('sin entrada' in t and 'mortalidad hasta' not in t and pg.locator('[data-fin="WLRCO300926"][disabled]').count() == 1, f'{vw} la página del lote lo marca y no pide conteo final')
        # completar la entrada
        pg.click('[data-ne="WLRCO300926"] >> nth=0'); pg.wait_for_timeout(100)
        chk(pg.input_value('#fl') == 'WLRCO300926' and pg.evaluate("document.getElementById('fl').disabled") and pg.input_value('#fo') == '1' and pg.input_value('#ft') == 'T3', f'{vw} «Completar» abre la Entrada con lote, proveedor y tanque')
        chk('Entrada del lote WLRCO300926' in pg.inner_text('#app'), f'{vw} el formulario dice de qué lote es la entrada')
        pg.fill('#fd', '2026-09-30'); pg.fill('#fh', '13:50')
        chk(pg.input_value('#fl') == 'WLRCO300926', f'{vw} cambiar la fecha no cambia el lote que se completa')
        for k, v in {'#ftt': '59.4', '#ftp': '55.2-60.1', '#fkb': '34', '#fdes': '0', '#fk0': '740.35', '#fk1': '223.6', '#fk2': '36.15', '#fk3': '10.25'}.items(): pg.fill(k, v)
        pg.click('[data-a=sv]'); pg.wait_for_timeout(120)
        r = pg.evaluate("R_('WLRCO300926')")
        chk(not r.get('ne') and r['rdate'] == '2026-09-30' and abs(pg.evaluate("rcv('WLRCO300926')") / 1000 - 1010.35) < 0.001 and len(pg.evaluate("ST.B['WLRCO300926']")) == 2, f'{vw} al completar: ya tiene entrada (1010.35 kg) y conserva sus 2 hieleras')
        chk(pg.evaluate("ST.R.filter(r=>r.lot=='WLRCO300926').length") == 1, f'{vw} no se duplica el lote')
        pg.evaluate("go('recepcion')"); chk('sin entrada' not in pg.inner_text('#app'), f'{vw} el aviso amarillo desaparece')
        pg.close()
    # ---------- 5. Modo piso: Encargado de piso ----------
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg, 'piso@propesa.mx', 'piso123', '1')
        oid = nueva_orden(pg); pg.evaluate(f"PE.lot=null;go('pemp:{oid}.1')"); pg.wait_for_timeout(100)
        chk('¿De qué lote' in pg.inner_text('#app') and pg.locator('[data-nea=open]').count() == 1, f'{vw} piso: al elegir lote está «+ Lote sin entrada»')
        pg.click('[data-nea=open]'); pg.fill('#ne_l', 'WLREM300926'); pg.select_option('#ne_p', '2'); pg.select_option('#ne_t', 'T1'); pg.click('[data-nea=sv]'); pg.wait_for_timeout(120)
        chk(pg.evaluate("PE.lot") == 'WLREM300926' and pg.locator('.ppc').count() >= 1 and pg.evaluate("R_('WLREM300926').ne"), f'{vw} piso: crea el lote sin entrada y pasa a empacar')
        chk(sin_desborde(pg), f'{vw} piso: sin desborde horizontal')
        pg.evaluate("go('lote:WLREM300926')"); pg.click('[data-ne="WLREM300926"] >> nth=0'); pg.wait_for_timeout(120)
        row = pg.evaluate("PEN.rows.find(r=>r.d.lot=='WLREM300926')")
        chk(pg.evaluate("V.v") == 'pent' and row and row['d']['origin'] == '2' and row['d']['tank'] == 'T1', f'{vw} piso: «Completar» abre la hoja de entradas con el lote listo')
        pg.close()
    # ---------- 6. Consulta no crea lotes sin entrada ----------
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, 'consulta@propesa.mx', 'ver123')
    pg.evaluate("ST.R.push({id:'R-0999',lot:'WLRZZ010126',origin:'SCPP Ensenada SCL',tank:'T1',rdate:'',time:'',date:'',tempT:null,tempP:'',kgbox:null,desp:null,final:null,closed:false,pv:1,ne:true});ST.B['WLRZZ010126']=[];setPiso(false)")
    oid = nueva_orden(pg); pg.evaluate(f"go('empacar:{oid}.1')")
    chk(pg.locator('[data-nea]').count() == 0, 'consulta: no ve «+ Lote sin entrada»')
    pg.evaluate("go('recepcion')"); chk('sin entrada' in pg.inner_text('#app') and pg.locator('[data-ne]').count() == 0, 'consulta: ve el aviso pero sin botón para completar')
    pg.evaluate("go('admin')"); chk(pg.locator('[data-pva]').count() == 0, 'consulta: no edita proveedores')
    pg.close()
    # ---------- 6b. Sin textos de «todavía no», versiones viejas o lotes escritos a mano (pedido del usuario, 17/oct) ----------
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto(BASE)
    pg.evaluate("localStorage.clear();localStorage.setItem('propesa-piso','0');localStorage.setItem('propesa-v4',JSON.stringify({L:[],R:[],B:{},P:[],O:[],M:{},OR:[],E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true}]}))"); pg.reload()
    pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'admin123'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
    malos = []
    for v in ['inicio', 'recepcion', 'ordenes', 'empaque', 'embarques', 'cierre', 'temperatura', 'admin']:
        pg.evaluate(f"go('{v}')"); t = pg.inner_text('#app')
        malos += [f'{v}: {w}' for w in ['Todavía no hay', 'Aún no hay', 'versión anterior', 'escrito a mano', 'de antes', 'todavía.'] if w in t]
    chk(not malos, f'pantallas vacías sin «todavía no», versiones viejas ni lotes escritos a mano: {malos}')
    pg.close()
    # ---------- 7. Datos: se comparten y sobreviven a un respaldo ----------
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg)
    r = pg.evaluate("""(()=>{ST.PV=PV0.map(p=>({...p}));ST.PV.push({id:9007,n:'Nuevo <b>',k:'nx',rfc:'abc',per:'P-1'});
      ST.R.push({id:'R-0998',lot:'WLRNE010126',origin:'SCPP Ensenada SCL',tank:'T2',rdate:'',time:'',date:'',tempT:null,tempP:'',kgbox:null,desp:null,final:null,closed:false,pv:1,ne:true});ST.B['WLRNE010126']=[];
      const enc=encodeST(),src=new Map([...enc].map(([k,[,o]])=>[k,o])),dec=decodeST(src),cl=cleanST({...ST},true);
      return{v:[...enc.keys()].filter(k=>k.startsWith('V/')).length,rv:enc.get('R/WLRNE010126')[1],dpv:dec.PV,dr:dec.R.find(x=>x.lot=='WLRNE010126'),cpv:cl.PV,cr:cl.R.find(x=>x.lot=='WLRNE010126'),old:enc.get('R/WLRCO051026A')[1],bad:WN.V({id:5,n:'',k:'X'})}})()""")
    chk(r['v'] == 4 and r['rv'].get('ne') is True and r['rv'].get('pv') == 1, f'proveedores y lotes sin entrada se suben como registros (V/…, R/…): {r["v"]}')
    chk(r['dpv'] and len(r['dpv']) == 4 and r['dr'].get('ne') and r['dr'].get('pv') == 1, 'otro equipo los arma igual (decodeST)')
    chk(r['cpv'] and r['cpv'][3]['k'] == 'NX' and r['cpv'][3]['rfc'] == 'ABC' and r['cr'].get('ne') and r['cr'].get('pv') == 1, 'sobreviven a un respaldo (cleanST) y se limpian')
    chk('ne' not in r['old'] and 'pv' not in r['old'], 'un lote de antes se sube igual que antes (sin campos nuevos)')
    chk(r['bad'] is None, 'un proveedor sin nombre se ignora')
    pg.close(); b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
