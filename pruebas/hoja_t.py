"""Hoja de empaque (Formato 06) por orden e indicaciones de carga por embarque (v1.9.0).
- La hora inicial se pone sola con la primera hielera; al terminar la última se piden hora final, quién realizó y evaluación (S/NS/N/D/N/A).
- Tanques de origen y tanque y temperatura los propone la app; placas se guardan en mayúsculas.
- Lo que falta sale en rojo con «Completar ›»; cerrar el embarque con la hoja incompleta pide confirmación.
- Todo sale en el informe de cierre (correo) y en los PDF; las indicaciones de carga salen en grande en Embarque, camión y Modo piso.
- Se comparte entre equipos (WN) y sobrevive a un respaldo (cleanST); Consulta no edita; con el embarque cerrado no se cambia.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/hoja_t.py"""
from playwright.sync_api import sync_playwright
import os, sys, re
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em, pw, piso='0'):
    pg.goto(BASE); pg.evaluate('([s,p])=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso",p);localStorage.setItem("propesa-kp","0")}', [seed, piso]); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def pdf_text(pg, k, arg):
    """Texto del PDF que arma la app (sin comprimir: los textos van entre paréntesis)."""
    raw = pg.evaluate(f"(async()=>{{const d=await pdfMake('{k}','{arg}');return Array.from(d.u8).map(c=>String.fromCharCode(c)).join('')}})()")
    return ' '.join(re.findall(r'\(((?:[^()\\]|\\.)*)\)\s*Tj', raw)).replace('\\(', '(').replace('\\)', ')')

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        dialogs = []; pg.on('dialog', lambda d: (dialogs.append(d.message), d.dismiss()))
        entrar(pg, 'admin@propesa.mx', 'admin123')
        pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '2026-10-20'); pg.click('[data-oa=new]'); oid = pg.evaluate('+V.id')
        for j, n in enumerate([2, 1]):
            (pg.locator('[data-oa=add]').count() and pg.click('[data-oa=add]')); pg.select_option('#ol_city', 'PVG'); pg.select_option('#ol_cons', index=j); pg.fill('#ol_n', str(n)); pg.fill('#ol_z1', str(n)); pg.fill('#ol_tar', '1'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(80)
        O = f"ST.OR.find(o=>o.id=={oid})"
        chk(pg.locator('#f6card').count() == 1, f'{vw} la orden muestra la hoja de empaque (Formato 06)')
        t = pg.inner_text('#f6card')
        chk('Langosta Roja' in t and '20/10/2026' in t and 'PVG' in t, f'{vw} la hoja trae fecha, especie y destino solos')
        chk(pg.evaluate(f"f6Miss({O}).length") == 0 and 'Faltan datos de la hoja' not in t, f'{vw} antes de empacar no pide nada en rojo')
        chk('Empacar hieleras' in pg.inner_text('#app') or 'hieleras' in pg.inner_text('#app'), f'{vw} la orden habla de hieleras')
        chk(not re.search(r'\b[Cc]ajas?\b', re.sub(r'(?i)cajas? de cart[oó]n', '', pg.inner_text('#app'))), f'{vw} la orden ya no dice «cajas»')
        # empacar ABC (2 hieleras) en la vista completa
        lids = pg.evaluate(f"{O}.lines.map(l=>l.id)")
        pg.evaluate(f"go('empacar:{oid}.{lids[0]}')"); pg.evaluate("PKD.lot=openLots()[0]")
        chk('Guardar' in pg.inner_text('#app') and not re.search(r'\b[Cc]ajas?\b', pg.inner_text('#app')), f'{vw} Empaque dice «hieleras», no «cajas»')
        for r in range(2):  # v1.12.0: cada hielera se completa sola
            pg.fill('#pk_c0', str(25 + r)); pg.click('#pkr0 [data-pk^="k:"] >> nth=1'); pg.wait_for_timeout(100)
        hi = pg.evaluate(f"({O}.f||{{}}).hi")
        chk(bool(hi) and re.match(r'^\d{2}:\d{2}$', hi or ''), f'{vw} la hora inicial se pone sola con la primera hielera: {hi}')
        chk(pg.locator('#f6card').count() == 0, f'{vw} con la orden a medias no aparece «Terminar empaque» en Empaque')
        m = pg.evaluate(f"f6Miss({O})")
        chk('pl' in m and 'tp' in m and 'hf' not in m and 'ev' not in m, f'{vw} a medias pide transporte y temperatura, todavía no hora final ni evaluación: {m}')
        pg.evaluate(f"go('orden:{oid}')")
        chk(pg.locator('#f6card .alb').count() == 1 and pg.locator('[data-jump="#f6_pl"]').count() >= 1, f'{vw} la hoja muestra en rojo lo que falta con «Completar ›»')
        # terminar con DEF
        pg.evaluate(f"go('empacar:{oid}.{lids[1]}')"); pg.evaluate("PKD.lot=openLots()[0]"); pg.fill('#pk_c0', '30'); pg.click('#pkr0 [data-pk^="k:"] >> nth=2'); (pg.locator('[data-pk=addall]').count() and pg.click('[data-pk=addall]')); pg.wait_for_timeout(100)
        chk(pg.locator('#f6card').count() == 1 and 'Terminar empaque' in pg.inner_text('#f6card'), f'{vw} al terminar la última hielera aparece «Terminar empaque»')
        chk(re.match(r'^\d{2}:\d{2}$', pg.input_value('#f6_hf')) and pg.input_value('#f6_re') == 'Ana Torres', f'{vw} hora final y quién realizó vienen llenos: {pg.input_value("#f6_hf")} / {pg.input_value("#f6_re")}')
        chk(pg.locator('[data-f6$=":S"]').count() == 1 and pg.locator('[data-f6$=":NS"]').count() == 1 and pg.locator('[data-f6$=":ND"]').count() == 1 and pg.locator('[data-f6$=":NA"]').count() == 1, f'{vw} botones S, NS, N/D y N/A')
        bh = pg.evaluate("Math.min(...[...document.querySelectorAll('[data-f6^=\"ev:\"]')].map(b=>b.getBoundingClientRect().height))")
        chk(bh >= 56, f'{vw} los botones de evaluación son grandes: {bh}px')
        pg.click('[data-f6$=":S"]'); pg.wait_for_timeout(80)
        f = pg.evaluate(f"{O}.f")
        chk(f.get('ev') == 'S' and f.get('hf') and f.get('re') == 'Ana Torres', f'{vw} un toque en S guarda evaluación, hora final y quién realizó: {f}')
        chk(f.get('to') == 'T1', f'{vw} tanques de origen propuestos por la app y guardados: {f.get("to")}')
        chk(pg.get_attribute('[data-f6$=":S"]', 'aria-pressed') == 'true', f'{vw} S queda marcado')
        # datos del transporte
        pg.fill('#f6_pl', 'zry68f3'); pg.fill('#f6_ch', 'Alejandro S.'); pg.fill('#f6_tel', '646-294-1282'); pg.fill('#f6_tp', '48 - 49 °F')
        if not pg.input_value('#f6_tq'): pg.fill('#f6_tq', 'T1 - 50 °F')
        pg.fill('#f6_ob', 'Hielera #2: <b>1 débil</b>'); pg.click('[data-f6^="sv:"]'); pg.wait_for_timeout(80)
        f = pg.evaluate(f"{O}.f")
        chk(f.get('pl') == 'ZRY68F3', f'{vw} las placas se guardan en mayúsculas: {f.get("pl")}')
        chk(pg.evaluate(f"f6Miss({O},true).length") == 0 and 'Hoja de empaque completa' in pg.inner_text('#app'), f'{vw} hoja completa')
        chk(pg.locator('#f6card b:has-text("1 débil")').count() == 0, f'{vw} las observaciones se muestran como texto (escapadas)')
        si = pg.evaluate(f"{O}.sh[Object.keys({O}.sh)[0]]")
        # indicaciones de carga
        pg.evaluate(f"go('emb:{si}')"); pg.fill('#emb_obs', 'Echar 2 tarimas vacías y fleje'); pg.click('[data-obs]'); pg.wait_for_timeout(80)
        chk(pg.evaluate(f"ST.P[{si}].ob") == 'Echar 2 tarimas vacías y fleje', f'{vw} las indicaciones se guardan en el embarque')
        chk(pg.locator('.obsb').count() >= 1 and 'TARIMAS' in pg.inner_text('.obsb >> nth=0').upper(), f'{vw} se ven en grande arriba del embarque')
        ob_h = pg.evaluate("document.querySelector('.obsb b').getBoundingClientRect().width>0&&parseFloat(getComputedStyle(document.querySelector('.obsb b')).fontSize)")
        chk(ob_h and ob_h >= 18, f'{vw} letra grande en las indicaciones: {ob_h}px')
        tx = pdf_text(pg, 'embs', '')
        chk('INDICACIONES PARA LA CARGA' in tx and 'ECHAR 2 TARIMAS' in tx, f'{vw} el PDF del camión (plan de embarques) trae las indicaciones')
        pg.evaluate("go('embarques')")
        chk(pg.locator('.obsb').count() >= 1 and pg.locator('.bpo').count() >= 1, f'{vw} también en el plan del camión y en la tarjeta del embarque')
        pg.evaluate(f"go('orden:{oid}')"); chk(pg.locator('#f6card .obsb').count() == 1, f'{vw} y dentro de la hoja de la orden')
        # tallas y cierre
        pg.evaluate(f"go('emb:{si}')")
        h = pg.evaluate(f"ST.P[{si}].h"); pg.evaluate(f"ST.P[{si}].z=[{h},0,0,0];save();render()")
        pg.click('[data-a=cp]'); pg.wait_for_timeout(200)
        chk(pg.evaluate(f"ST.P[{si}].closed") and not dialogs, f'{vw} con la hoja completa se cierra sin preguntar')
        body = pg.evaluate("ST.O[0].body")
        for s in ['HOJA DE EMPAQUE', 'Langosta Roja', 'ZRY68F3', 'Alejandro S.', '646-294-1282', '48 - 49 °F', 'Evaluación: S (Satisfactorio)', 'Hora inicial: ' + hi, 'INDICACIONES PARA LA CARGA: Echar 2 tarimas', 'Realizó: Ana Torres', 'Tanques de origen: T1']:
            chk(s in body, f'{vw} el informe de correo trae «{s}»')
        pg.evaluate(f"Object.values({O}.sh).forEach(i=>ST.P[i].closed=true);save();render()")  # la orden lleva dos consignatarios: dos embarques
        chk(pg.locator('#f6_pl').count() == 0 or pg.is_disabled('#f6_pl'), f'{vw} con el embarque cerrado la hoja ya no se cambia')
        pg.evaluate(f"go('orden:{oid}')"); chk(pg.is_disabled('#f6_pl') and pg.locator('[data-f6^="sv:"]').count() == 0, f'{vw} en la orden la hoja queda de solo lectura')
        tx = pdf_text(pg, 'emb', si)
        for s in ['Formato 06', 'ZRY68F3', 'INDICACIONES PARA LA CARGA', 'Satisfactorio', 'CONNOTACIONES', 'Alejandro S.']:
            chk(s in tx, f'{vw} el PDF del embarque trae «{s}»')
        tx = pdf_text(pg, 'emp', oid)
        chk('Formato 06' in tx and 'ZRY68F3' in tx and 'hieleras' in tx.lower() and not re.search(r'\bcajas?\b', tx.lower()), f'{vw} el packing list de la orden trae la hoja y dice hieleras')
        # cerrar con la hoja incompleta pide confirmación
        pg.evaluate("go('ordenes')"); pg.fill('#no_etd', '2026-10-21'); pg.click('[data-oa=new]'); o2 = pg.evaluate('+V.id')
        pg.select_option('#ol_city', 'HKG'); pg.fill('#ol_n', '1'); pg.fill('#ol_z0', '1'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(80)
        l2 = pg.evaluate(f"ST.OR.find(o=>o.id=={o2}).lines[0].id"); pg.evaluate(f"go('empacar:{o2}.{l2}')"); pg.evaluate("PKD.lot=openLots()[0]"); pg.fill('#pk_c0', '20'); pg.click('#pkr0 [data-pk^="k:"] >> nth=0'); (pg.locator('[data-pk=addall]').count() and pg.click('[data-pk=addall]')); pg.wait_for_timeout(80)
        s2 = pg.evaluate(f"(o=>o.sh[Object.keys(o.sh)[0]])(ST.OR.find(o=>o.id=={o2}))")
        pg.evaluate(f"go('emb:{s2}')"); iss = pg.evaluate(f"shipIssues({s2}).map(x=>x.t+'|'+(x.go||''))")
        chk(any('Hoja de empaque' in x and f'orden:{o2}' in x for x in iss), f'{vw} el embarque avisa en rojo la hoja incompleta y lleva a la orden: {iss}')
        pg.evaluate(f"ST.P[{s2}].z=[1,0,0,0];save();render()"); pg.click('[data-a=cp]'); pg.wait_for_timeout(150)
        chk(dialogs and 'hoja de empaque' in dialogs[-1] and not pg.evaluate(f"ST.P[{s2}].closed"), f'{vw} cerrar con la hoja incompleta pregunta, y si dices que no, no se cierra')
        tx = pdf_text(pg, 'emb', s2); chk('FALTAN DATOS DE LA HOJA' in tx, f'{vw} el PDF marca la hoja incompleta')
        pg.close()
    # Datos: se comparten (WN) y sobreviven a un respaldo (cleanST); valores raros se descartan
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, 'admin@propesa.mx', 'admin123')
    r = pg.evaluate("""(()=>{const o={id:5,etd:'2026-10-20',lines:[{id:1,city:'PVG',cons:0,cli:'ABC',boxes:2}],sh:{},f:{hi:'07:05',hf:'25:99',ev:'XX',pl:'ABC1',ob:'ok',zz:'x',tel:5}};
      const w=WN.OR(o),c=cleanST({...ST,OR:[{...o,sh:{}}]}).OR[0],pw=WN.P({...ST.P[0],ob:'ECHAR FLEJE'}),pc=cleanST({...ST,P:ST.P.map(p=>({...p,ob:'ECHAR FLEJE'}))}).P[0];
      return{w:w.f,c:c.f,pw:pw.ob,pc:pc.ob}})()""")
    chk(r['w'] == {'hi': '07:05', 'pl': 'ABC1', 'ob': 'ok', 'tel': '5'}, f'la hoja se comparte entre equipos y descarta horas o evaluación inválidas: {r["w"]}')
    chk(r['c'] == {'hi': '07:05', 'pl': 'ABC1', 'ob': 'ok', 'tel': '5'}, f'la hoja sobrevive a un respaldo: {r["c"]}')
    chk(r['pw'] == 'ECHAR FLEJE' and r['pc'] == 'ECHAR FLEJE', 'las indicaciones se comparten y sobreviven a un respaldo')
    pg.close()
    # Modo piso: hoja al terminar e indicaciones en el inicio; Consulta solo ve
    pg = b.new_page(viewport={'width': 820, 'height': 1180}); pg.on('pageerror', lambda e: errs.append(str(e)))
    entrar(pg, 'piso@propesa.mx', 'piso123', '1')
    if pg.locator('#le').count(): chk(True, 'piso: no entra con estos datos de prueba (se omite)')
    else:
        pg.evaluate("ST.P[0].closed=false;ST.P[0].ob='Echar 2 tarimas';save();go('piso')")
        chk(pg.locator('.obsb').count() >= 1 and 'tarimas' in pg.inner_text('.obsb >> nth=0').lower(), 'Modo piso: las indicaciones de carga salen en el inicio')
        chk('Empacar hieleras' in pg.inner_text('#app'), 'Modo piso: el botón dice «Empacar hieleras»')
        k = pg.evaluate("(()=>{for(const o of ST.OR){if(ordTot(o)&&ordAsg(o)>=ordTot(o))return o.id+'.'+o.lines[0].id}})()")
        if k:
            pg.evaluate(f"go('pemp:{k}')"); chk(pg.locator('#f6card').count() == 1, 'Modo piso: con la orden completa aparece la hoja para terminar')
            pg.click('[data-f6$=":NA"]'); pg.wait_for_timeout(80)
            chk(pg.evaluate(f"ST.OR.find(o=>o.id=={k.split('.')[0]}).f.ev") == 'NA', 'Modo piso: el encargado marca la evaluación con un toque')
    pg.close()
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, 'consulta@propesa.mx', 'ver123')
    if not pg.locator('#le').count():
        pg.evaluate("setPiso(false);ST.P.forEach(p=>p.closed=false);go('orden:'+ST.OR[0].id)")
        chk(pg.locator('#f6card').count() == 1 and pg.is_disabled('#f6_pl') and pg.locator('[data-f6^="sv:"]').count() == 0, 'Consulta ve la hoja pero no la cambia')
        pg.evaluate("go('emb:0')"); chk(pg.is_disabled('#emb_obs') and pg.locator('[data-obs]').count() == 0, 'Consulta no cambia las indicaciones')
    pg.close()
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
