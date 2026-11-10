"""v1.26.0 (pedido del usuario, 29/oct/2026).
1. Camiones en pestañas: con dos camiones o más, cada uno es una pestaña con su propio PDF; «Camión nuevo» abre su pestaña.
   Con un solo camión, la pantalla y el PDF quedan como antes (sin pestañas).
2. Notificaciones: campana con contador en el encabezado (vista completa y Modo piso). Lo que falta capturar o resolver
   y lo creado o terminado en 7 días; tocar uno lleva a donde se resuelve. Lo reciente queda visto al tocarlo o con
   «Marcar todo como visto»; lo que falta no se descarta.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v126_t.py"""
from playwright.sync_api import sync_playwright
import os, re
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em, pw):
    pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0")}', seed); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def pdf_text(pg, k, arg):
    raw = pg.evaluate(f"(async()=>{{const d=await pdfMake('{k}','{arg}');return [d.name,Array.from(d.u8).map(c=>String.fromCharCode(c)).join('')]}})()")
    return raw[0], ' '.join(re.findall(r'\(((?:[^()\\]|\\.)*)\)\s*Tj', raw[1])).replace('\\(', '(').replace('\\)', ')')
ADD = """()=>{[30,12].forEach((h,n)=>{const i=newShip();Object.assign(ST.P[i],{n:'HKG · PRUEBA'+n+' · 20/10',h,col:['#0583c3','#e5484d'][n]})});save();go('embarques')}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1440, 900), (820, 1180), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg, 'admin@propesa.mx', 'admin123'); pg.evaluate(ADD); pg.wait_for_timeout(100)
        # ---------- 1. pestañas de camiones
        chk(pg.locator('.ttab').count() == 0 and pg.locator('.tcard').count() == 1, f'{vw} con un camión no hay pestañas (como antes)')
        n1, t1 = pdf_text(pg, 'embs', '')
        chk('Plan_de_embarques' in n1 and 'PRUEBA0' in t1 and 'PRUEBA1' in t1, f'{vw} con un camión, el PDF de siempre con todos los embarques')
        u = pg.evaluate("ST.P.find(p=>p.n.includes('PRUEBA1')).u")
        pg.select_option(f'select[data-tk="{u}"]', '+'); pg.wait_for_timeout(100)
        chk(pg.locator('.ttab').count() == 2 and pg.locator('.tcard').count() == 1, f'{vw} «Camión nuevo»: dos pestañas y se ve un camión a la vez')
        chk(pg.get_attribute('#ttab_2', 'aria-selected') == 'true' and 'PRUEBA1' in pg.inner_text('#tk_2'), f'{vw} el camión nuevo se abre en su pestaña')
        tp = pg.inner_text('#tpanel'); a = tp.index('Consignaciones abiertas')
        chk('PRUEBA1' in tp[a:] and 'PRUEBA0' not in tp[a:], f'{vw} la pestaña enseña solo las consignaciones de su camión')
        chk('PDF del Camión 2' in tp and pg.locator('#tpanel [data-pdf]').count() == 2, f'{vw} cada pestaña tiene su PDF')
        n2, t2 = pdf_text(pg, 'embs', pg.evaluate("trucks()[1]"))
        chk('Plan_de_carga_Camion_2' in n2 and 'PRUEBA1' in t2 and 'PRUEBA0' not in t2, f'{vw} el PDF del Camión 2 solo trae su embarque ({n2})')
        n0, t0 = pdf_text(pg, 'embs', pg.evaluate("trucks()[0]"))
        chk('Camion_1' in n0 and 'PRUEBA0' in t0 and 'PRUEBA1' not in t0, f'{vw} el PDF del Camión 1 solo trae el suyo')
        pg.reload(); pg.wait_for_timeout(300)
        chk(pg.get_attribute('#ttab_2', 'aria-selected') == 'true', f'{vw} al recargar sigue abierta la misma pestaña')
        pg.click('#ttab_1'); pg.wait_for_timeout(80)
        chk(pg.get_attribute('#ttab_1', 'aria-selected') == 'true' and pg.locator('#tk_1').count() == 1 and pg.locator('#tk_2').count() == 0, f'{vw} tocar la pestaña 1 regresa al Camión 1')
        pg.focus('#ttab_1'); pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(80)
        chk(pg.get_attribute('#ttab_2', 'aria-selected') == 'true' and pg.evaluate("document.activeElement.id") == 'ttab_2', f'{vw} con el teclado (flecha) se cambia de pestaña')
        hs = pg.evaluate("[...document.querySelectorAll('.ttab')].map(e=>e.getBoundingClientRect().height)")
        chk(min(hs) >= 48, f'{vw} las pestañas miden 48 px o más ({min(hs)})')
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{vw} sin scroll de lado con las pestañas')
        pg.select_option(f'select[data-tk="{u}"]', pg.evaluate("trucks()[0]")); pg.wait_for_timeout(80)
        chk(pg.locator('.ttab').count() == 0 and pg.locator('.tcard').count() == 1, f'{vw} al juntar todo en un camión se quitan las pestañas')
        # ---------- 2. notificaciones
        pg.evaluate("go('inicio')"); pg.wait_for_timeout(80)
        chk(pg.locator('.hd [data-ntb]').count() == 1, f'{vw} la campana está en el encabezado')
        bw = pg.evaluate("(()=>{const r=document.querySelector('[data-ntb]').getBoundingClientRect();return [r.width,r.height]})()")
        chk(min(bw) >= 44, f'{vw} la campana mide 44 px o más {bw}')
        cnt = pg.evaluate("ntCount()")
        badge = pg.inner_text('.ntc') if pg.locator('.ntc').count() else ''
        chk(cnt > 0 and badge == (str(cnt) if cnt <= 99 else '99+'), f'{vw} el contador enseña {cnt}: «{badge}»')
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{vw} sin scroll de lado con la campana')
        pg.click('[data-ntb]'); pg.wait_for_timeout(80)
        chk(pg.is_visible('.ntbox') and pg.get_attribute('[data-ntb]', 'aria-expanded') == 'true', f'{vw} tocar la campana abre las notificaciones')
        box = pg.evaluate("(()=>{const r=document.querySelector('.ntbox').getBoundingClientRect();return [r.left,r.right,r.bottom]})()")
        chk(box[0] >= 0 and box[1] <= vw[0] and box[2] <= vw[1], f'{vw} el panel cabe en la pantalla {box}')
        tx = pg.inner_text('.ntbox')
        chk('FALTA CAPTURAR O RESOLVER' in tx.upper() and 'RECIENTES' in tx.upper(), f'{vw} trae lo que falta y lo reciente')
        chk('Embarque HKG · PRUEBA0' in tx, f'{vw} los pendientes del embarque salen como notificación')
        hs = pg.evaluate("[...document.querySelectorAll('.nti')].map(e=>e.getBoundingClientRect().height)")
        chk(hs and min(hs) >= 48, f'{vw} cada notificación mide 48 px o más')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(50)
        chk(not pg.locator('.ntbox').count() and pg.evaluate("document.activeElement.dataset.ntb") == '1', f'{vw} Escape la cierra y regresa a la campana')
        # orden nueva: sale en recientes, sin ver; al tocarla lleva a la orden y queda vista
        oid = pg.evaluate("(()=>{const id=uidN();ST.OR.push({id,etd:dLoc(),lines:[],sh:{},sp:1});save();render();return id})()")
        c0 = pg.evaluate("ntCount()")
        pg.click('[data-ntb]'); pg.wait_for_timeout(50)
        it = pg.locator(f'.nti[data-ntk="O:{oid}"]')
        chk(it.count() == 1 and 'sin ver' in it.inner_text(), f'{vw} la orden nueva sale en recientes, sin ver')
        chk(pg.locator(f'.nti:not([data-ntk])[data-ntgo="orden:{oid}"]').count() == 1, f'{vw} y en «falta»: no tiene líneas')
        it.click(); pg.wait_for_timeout(80)
        chk(pg.evaluate("V.v+':'+V.id") == f'orden:{oid}' and not pg.locator('.ntbox').count(), f'{vw} tocarla lleva a la orden y cierra el panel')
        chk(pg.evaluate("ntCount()") == c0 - 1, f'{vw} ya vista: el contador baja uno')
        # entrada con hora de madrugada: lleva al lote
        lot = pg.evaluate("(()=>{const r=ST.R[0];r.time='02:10';save();render();return r.lot})()")
        pg.click('[data-ntb]'); pg.wait_for_timeout(50)
        li = pg.locator(f'.nti:not([data-ntk])[data-ntgo="lote:{lot}"]')
        li = li.filter(has_text='madrugada')  # v1.43.0: el mismo lote también puede tener «Sacar de tinas»
        chk(li.count() >= 1, f'{vw} la entrada con hora de madrugada sale como pendiente')
        li.first.click(); pg.wait_for_timeout(80)
        chk(pg.evaluate("V.v+':'+V.id") == f'lote:{lot}', f'{vw} y lleva al lote')
        # marcar todo como visto: lo reciente deja de contar; lo que falta sigue
        pg.click('[data-ntb]'); pg.wait_for_timeout(50)
        if pg.locator('[data-ntall]').count(): pg.click('[data-ntall]'); pg.wait_for_timeout(50)
        F = pg.evaluate("ntFalta().length")
        chk(pg.evaluate("ntCount()") == F and pg.locator('.nti.new').count() == 0 and pg.is_visible('.ntbox'), f'{vw} «Marcar todo como visto»: solo cuentan los {F} pendientes')
        pg.click('.ntx'); pg.wait_for_timeout(50)
        chk(not pg.locator('.ntbox').count(), f'{vw} la ✕ cierra el panel')
        # cerrar un embarque: sale como terminado y lleva a él
        pg.evaluate("(()=>{ST.O.unshift({u:uidS(),subject:'x',t:now(),to:[],body:'',pn:ST.P[0].n,att:'a.pdf',pu:ST.P[0].u});ST.P[0].closed=true;save();render()})()")
        pg.click('[data-ntb]'); pg.wait_for_timeout(50)
        ci = pg.locator('.nti.d')
        chk(ci.count() == 1 and 'Embarque cerrado' in ci.inner_text(), f'{vw} el embarque cerrado sale en recientes como terminado')
        ci.click(); pg.wait_for_timeout(80)
        chk(pg.evaluate("V.v") == 'emb' and pg.evaluate("+V.id") == 0, f'{vw} y lleva al embarque')
        # atrás del navegador cierra el panel
        pg.click('[data-ntb]'); pg.wait_for_timeout(50); pg.go_back(); pg.wait_for_timeout(100)
        chk(not pg.locator('.ntbox').count() and pg.evaluate("V.v") == 'emb', f'{vw} «atrás» cierra el panel sin salir de la pantalla')
        # tema oscuro
        pg.evaluate("document.documentElement.setAttribute('data-theme','dark')"); pg.click('[data-ntb]'); pg.wait_for_timeout(50)
        bg = pg.evaluate("getComputedStyle(document.querySelector('.ntbox')).backgroundColor")
        chk(bg != 'rgb(255, 255, 255)', f'{vw} en tema oscuro el panel es oscuro ({bg})')
        pg.close()
    # Modo piso también tiene la campana; el seen es por usuario
    pg = b.new_page(viewport={'width': 1180, 'height': 820}); pg.on('pageerror', lambda e: errs.append(str(e)))
    entrar(pg, 'piso@propesa.mx', 'piso123')
    chk(pg.locator('.phd [data-ntb]').count() == 1, 'Modo piso: la campana está en el encabezado')
    chk(pg.evaluate("ntK()") != 'propesa-nt-' + str(pg.evaluate("ST.U.find(u=>u.role=='admin').id")), 'lo visto se guarda por usuario')
    pg.click('[data-ntb]'); pg.wait_for_timeout(50); chk(pg.is_visible('.ntbox'), 'Modo piso: abre el panel')
    pg.close()
    b.close()
print('\nERRORES JS:', errs) if errs else None
print(f"\n{'TODO BIEN' if not fails and not errs else str(len(fails)) + ' FALLAS'}")
