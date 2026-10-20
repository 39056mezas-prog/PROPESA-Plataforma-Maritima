"""Prueba PROPESA (teclado_t): teclado numérico fijo en Empaque (Modo piso y vista completa).
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/teclado_t.py"""
import json,os,tempfile
from playwright.sync_api import sync_playwright
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True);T=OUT.rstrip('/')+'/'
seed=json.loads(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos','seed.json')).read())
seed['OR'].append({'id':3,'etd':'2026-10-14','lines':[{'id':1,'city':'HKG','cons':0,'cli':'LHD','boxes':6}],'sh':{}})
S=json.dumps(seed);errs=[]
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
def boxes(pg):
    st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"));return sorted([(x.get('ps'),x['c'],x['k']) for v in st['B'].values() for x in v if x['o']=='3.1'],key=lambda x:(x[0] or 0,x[1]))
def kp(pg,d):
    for c in str(d):pg.click(f'#kpad [data-kp="d:{c}"]')
def cat(pg,q):pg.click(f'#kpad [data-kp="k:{q}"]');pg.wait_for_timeout(60)
def disp(pg):return pg.inner_text('#kpv')
def inview(pg,sel):
    return pg.evaluate("""s=>{const r=document.querySelector(s).getBoundingClientRect();return r.top>=0&&r.left>=0&&r.bottom<=innerHeight+1&&r.right<=innerWidth+1}""",sel)
def start(b,vw,user,pw,route,scheme='light',fs=None):
    pg=b.new_page(viewport={'width':vw[0],'height':vw[1]},color_scheme=scheme);pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',S)
    if fs:pg.evaluate(f"localStorage.setItem('propesa-fs','{fs}')")
    pg.reload();pg.fill('#le',user);pg.fill('#lp',pw);pg.click('[data-a=lg]');pg.wait_for_timeout(700)
    pg.evaluate(f"go('{route}')");return pg
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---------- Modo piso ----------
    for vw,scheme in [((1180,820),'light'),((820,1180),'dark'),((390,844),'light')]:
        w=vw[0];pg=start(b,vw,'piso@propesa.mx','piso123','pemp:3.1',scheme)
        pg.click('[data-pe="lot:WLRCO061026B"]')
        chk(pg.locator('#kpad').count()==1 and inview(pg,'#kpad [data-kp="k:A"]'),f'{w} piso: teclado en pantalla con las categorías a la vista')
        chk(pg.get_attribute('.ppc[data-slot="1"]','inputmode')=='none',f'{w} piso: el teclado de la tablet no aparece (inputmode none)')
        chk(pg.evaluate('KPT.t')=='slot:1' and pg.locator('#pps1.kpon').count()==1 and 'Hielera 1' in pg.inner_text('#kpt'),f'{w} piso: empieza en la hielera 1, resaltada')
        kp(pg,'123');chk(disp(pg)=='123' and pg.input_value('.ppc[data-slot="1"]')=='123',f'{w} piso: los números van a la hielera y al recuadro')
        pg.click('#kpad [data-kp=bk]');chk(disp(pg)=='12',f'{w} piso: ⌫ borra un número')
        pg.click('#kpad [data-kp=clr]');chk(disp(pg)=='—' and pg.input_value('.ppc[data-slot="1"]')=='',f'{w} piso: Borrar deja vacío')
        kp(pg,'12345');chk(disp(pg)=='1234',f'{w} piso: máximo 4 números (evita errores de dedo)')
        pg.click('#kpad [data-kp=clr]');kp(pg,'0');kp(pg,'9');chk(disp(pg)=='9',f'{w} piso: un 0 al inicio se reemplaza')
        chk('Falta categoría' in pg.inner_text('#pps1'),f'{w} piso: la tarjeta dice «Falta categoría»')
        cat(pg,'R');chk(boxes(pg)==[(1,9,'R')],f'{w} piso: tocar la categoría guarda la hielera {boxes(pg)}')
        chk(pg.evaluate('KPT.t')=='slot:2' and pg.locator('#pps2.kpon').count()==1 and disp(pg)=='—',f'{w} piso: pasa sola a la hielera 2')
        kp(pg,'11');cat(pg,'V');kp(pg,'8');cat(pg,'B')
        chk(boxes(pg)==[(1,9,'R'),(2,11,'V'),(3,8,'B')] and pg.evaluate('KPT.t')=='slot:4',f'{w} piso: tres hieleras seguidas sin tocar la pantalla de las hieleras')
        chk(pg.locator('#kpad [data-kp="k:A"]').inner_text().strip()=='Amarillo',f'{w} piso: cuarta categoría Amarillo (1221-UP)')
        # corregir la hielera 2: tocarla, escribir (reemplaza) y categoría
        pg.click('#pps2 .pbn');chk('Corrigiendo' in pg.inner_text('#kps') and disp(pg)=='11',f'{w} piso: al tocar una hielera guardada el teclado la corrige')
        chk(pg.locator('#kpad [data-kp="k:V"][aria-pressed=true]').count()==1,f'{w} piso: marca la categoría que ya tenía')
        kp(pg,'7');chk(disp(pg)=='7',f'{w} piso: el primer número reemplaza el valor anterior')
        cat(pg,'A');chk((2,7,'A') in boxes(pg) and len(boxes(pg))==3,f'{w} piso: corrección guardada como Amarillo sin crear otra hielera {boxes(pg)}')
        chk(pg.evaluate('KPT.t')=='slot:4',f'{w} piso: después de corregir vuelve a la siguiente vacía')
        # categoría primero, luego piezas, luego «Siguiente hielera»
        cat(pg,'V');chk(len(boxes(pg))==3 and pg.locator('#pps4.ip').count()==1,f'{w} piso: solo categoría no guarda (queda en captura)')
        kp(pg,'15');pg.click('#kpad [data-kp=next]');chk((4,15,'V') in boxes(pg) and pg.evaluate('KPT.t')=='slot:5',f'{w} piso: «Siguiente hielera» guarda la que estaba lista')
        pg.click('#kpad [data-kp=prev]');chk(pg.evaluate('KPT.t')=='slot:4',f'{w} piso: «Hielera anterior»')
        # teclado físico sin campo enfocado
        pg.click('#pps5 .pbn');pg.evaluate("document.activeElement&&document.activeElement.blur()");pg.keyboard.type('21');pg.wait_for_timeout(50);d=disp(pg);chk(d=='21',f'{w} piso: un teclado físico también escribe en la hielera activa ({d}, {pg.evaluate("KPT.t")}, foco: {pg.evaluate("document.activeElement.className||document.activeElement.tagName")})')
        pg.keyboard.press('Backspace');pg.wait_for_timeout(50);d=disp(pg);chk(d=='2',f'{w} piso: Backspace del teclado físico ({d}, {pg.evaluate("KPT.t")}, foco: {pg.evaluate("document.activeElement.className||document.activeElement.tagName")}, campo: {pg.evaluate("kpEl()&&kpEl().value")})')
        # quitar una hielera guardada desde el teclado
        pg.click('#pps1 .pbn');pg.click('#kpad [data-pe^="cf:"]');chk(pg.locator('#kpad [data-pe^="rm:"]').count()==1,f'{w} piso: «Quitar hielera» pide confirmación')
        pg.click('#kpad [data-pe^="rm:"]');chk(all(x[0]!=1 for x in boxes(pg)) and pg.locator('#pps1.sv').count()==0,f'{w} piso: hielera quitada, el lugar 1 queda libre')
        pg.screenshot(path=T+f'tec_piso_{w}.png')
        chk(pg.locator('#pps6 .pbn').count()==1 and pg.locator('[data-kp=next]').count()==1,f'{w} piso: tarjetas y botones completos')
        ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth");chk(ov==0,f'{w} piso: sin desborde')
        pg.close()
    # letra muy grande (20 px)
    for vw in [(1180,820),(390,844)]:
        pg=start(b,vw,'piso@propesa.mx','piso123','pemp:3.1',fs=20);pg.click('[data-pe="lot:WLRCO061026B"]')
        ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
        cut=pg.evaluate("[...document.querySelectorAll('#kpad button')].filter(b=>b.scrollWidth>b.clientWidth+1).map(b=>b.textContent)")
        chk(ov==0 and not cut and inview(pg,'#kpad [data-kp="k:A"]'),f'{vw[0]} piso letra 20 px: sin desborde ni botones cortados {cut}');pg.screenshot(path=T+f'tec_piso20_{vw[0]}.png');pg.close()
    # ---------- iPad simulado (pantalla táctil, sin mouse) ----------
    ctx=b.new_context(viewport={'width':820,'height':1180},has_touch=True,is_mobile=True,device_scale_factor=2)
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',S);pg.reload()
    pg.fill('#le','piso@propesa.mx');pg.fill('#lp','piso123');pg.tap('[data-a=lg]');pg.wait_for_timeout(700);pg.evaluate("go('pemp:3.1')")
    pg.tap('[data-pe="lot:WLRCO061026B"]')
    chk(pg.evaluate("matchMedia('(pointer: coarse)').matches"),'iPad: pantalla táctil')
    for c in '14':pg.tap(f'#kpad [data-kp="d:{c}"]')
    pg.tap('#kpad [data-kp="k:V"]');pg.wait_for_timeout(80)
    chk(boxes(pg)==[(1,14,'V')] and pg.evaluate('KPT.t')=='slot:2','iPad: tocando el teclado se guarda la hielera y pasa a la 2')
    pg.tap('#pps1 .pbn');pg.wait_for_timeout(80)
    chk(pg.evaluate("String(getSelection())")=='' and pg.evaluate('KPT.t')=='slot:1','iPad: tocar una hielera guardada no selecciona el texto (sin menú Copiar/Pegar)')
    for c in '16':pg.tap(f'#kpad [data-kp="d:{c}"]')
    pg.tap('#kpad [data-kp="k:V"]');pg.wait_for_timeout(80)
    chk(boxes(pg)==[(1,16,'V')],'iPad: corrección con el teclado '+str(boxes(pg)))
    ctx.close()
    # ---------- Vista completa ----------
    for vw,scheme in [((1440,900),'light'),((1180,820),'dark'),((820,1180),'light'),((390,844),'light')]:
        w=vw[0];pg=start(b,vw,'admin@propesa.mx','admin123','empacar:3.1',scheme)
        pg.click('[data-pk="lot:WLRCO061026B"]')
        chk(pg.locator('#kpad').count()==1 and inview(pg,'#kpad [data-kp="k:A"]') and inview(pg,'[data-pk=addall]'),f'{w} completa: teclado y «Guardar hieleras» a la vista')
        chk(pg.evaluate('KPT.t')=='row:0' and pg.locator('#pkr0.kpon').count()==1,f'{w} completa: empieza en la primera fila')
        chk(pg.locator('.pklots .pklb').count()>1 and pg.locator('#app .pkrow select').count()==0 and pg.locator('#app .pkrow .pklv').count()==0,f'{w} completa: hay varios lotes y ninguna hielera nueva pide ni repite el lote')
        # v1.12.0: con piezas y categoría la hielera se completa sola (antes esperaba a «Guardar hieleras»)
        kp(pg,'10');cat(pg,'R');chk([(c,k) for _,c,k in boxes(pg)]==[(10,'R')],f'{w} completa: con piezas y categoría la hielera se completa sola {boxes(pg)}')
        chk(pg.evaluate('KPT.t')=='row:0' and 'Hielera 2' in pg.inner_text('#kpt'),f'{w} completa: el teclado pasa a la siguiente hielera vacía (Hielera 2)')
        kp(pg,'12');cat(pg,'V');chk([(c,k) for _,c,k in boxes(pg)]==[(10,'R'),(12,'V')],f'{w} completa: la segunda también {boxes(pg)}')
        chk(pg.evaluate('KPT.t')=='row:0' and 'Hielera 3' in pg.inner_text('#kpt'),f'{w} completa: sigue en la primera hielera vacía (Hielera 3)')
        # corregir una hielera guardada
        seq=pg.evaluate("ST.B['WLRCO061026B'].find(b=>b.o=='3.1'&&b.c==12).seq")
        pg.click(f'#pkd{seq} .pked');chk(pg.evaluate('KPT.t')=='ed' and disp(pg)=='12' and 'Corrigiendo' in pg.inner_text('#kps'),f'{w} completa: tocar una hielera guardada la abre en el teclado')
        kp(pg,'13');cat(pg,'B');chk((13,'B') in [(c,k) for _,c,k in boxes(pg)] and len(boxes(pg))==2,f'{w} completa: categoría guarda la corrección {boxes(pg)}')
        chk(pg.locator('#pk_e').count()==0 and pg.evaluate('KPT.t')=='row:0',f'{w} completa: después de corregir vuelve a la primera vacía')
        chk(len([1 for x in pg.evaluate("ST.B['WLRCO061026B']") if x['o']=='3.1'])==2,f'{w} completa: las hieleras se guardaron en el lote elegido arriba')
        otro=pg.get_attribute('.pklb[aria-pressed=false] >> nth=0','data-pk');pg.click(f'[data-pk="{otro}"]')
        kp(pg,'9');cat(pg,'A');pg.click('[data-pk=addall]');ol=otro.split(':',1)[1]
        chk(any(x['o']=='3.1' and x['c']==9 and x['k']=='A' for x in pg.evaluate(f"ST.B[{json.dumps(ol)}]")),f'{w} completa: al cambiar el lote arriba, la siguiente hielera va a ese lote ({ol})')
        pg.screenshot(path=T+f'tec_full_{w}.png')
        # abrir y cerrar el teclado: abierto, las filas no repiten las categorías; cerrado, cada fila trae las suyas
        chk(pg.evaluate("[...document.querySelectorAll('#app .pkrow .seg button')].filter(b=>b.offsetParent&&b.getAttribute('aria-pressed')!='true').length")==0,f'{w} completa: con el teclado abierto las filas no repiten las categorías')
        pg.click('[data-kpo="0"]');chk(pg.locator('#kpad').count()==0 and pg.evaluate("[...document.querySelectorAll('#app .pkrow .seg button')].filter(b=>b.offsetParent).length")>=4 and pg.get_attribute('#pk_c0','inputmode')=='numeric',f'{w} completa: «Cerrar teclado» lo quita, cada fila trae sus categorías y el teclado de la tablet')
        chk(pg.evaluate("localStorage.getItem('propesa-kp')")=='0' and pg.locator('[data-kpo="1"]').count()==1,f'{w} completa: se recuerda cerrado y aparece «Abrir teclado»')
        pg.click('[data-kpo="1"]');chk(pg.locator('#kpad').count()==1,f'{w} completa: «Abrir teclado» lo regresa')
        ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth");chk(ov==0,f'{w} completa: sin desborde')
        pg.close()
    # consulta: sin teclado
    pg=start(b,(1180,820),'consulta@propesa.mx','ver123','empacar:1.1');chk(pg.locator('#kpad').count()==0,'consulta: sin teclado');pg.close()
    # embarque cerrado: sin teclado en piso
    pg=start(b,(1180,820),'admin@propesa.mx','admin123','inicio');pg.evaluate("ST.P[0].closed=true;save();setPiso(true);go('pemp:1.1')")
    if pg.locator('[data-pe^="lot:"]').count():pg.click('[data-pe^="lot:"] >> nth=0')
    chk(pg.locator('#kpad').count()==0 and 'cerr' in pg.inner_text('#app').lower(),'embarque cerrado: piso sin teclado (solo ver)');pg.close()
    b.close()
chk(not errs,'sin errores de JavaScript '+str(errs[:3]))
print('capturas en',OUT)
