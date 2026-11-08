"""v1.40.0 · Eliminar en Catálogos y sin pestaña Maquilas (pedido del usuario, 7/nov/2026: «en admin settings debería de poder
eliminar proveedores y también las especies y las demás cosas… no agregar ni quitar maquilas»; aprobó «borrar solo si nunca se usó»).
- Proveedores, especies, destinos, tallas y consignatarios llevan «Eliminar» (texto rojo con bote, al final de la fila).
- Confirmación en un renglón debajo: dice qué se borra («¿Eliminar el proveedor X?» → «Sí, eliminar proveedor» / «No»).
- Si ya se usó (en cualquier maquila) no se borra: dice en qué y ofrece «Ocultar». Siempre queda al menos uno visible.
- Tallas y consignatarios se guardan por posición: al borrar uno, lo guardado detrás se recorre (z, cons, sh, colores, otras maquilas).
- Lo borrado deja de salir en los registros que se comparten (encodeAll). Sin pestaña Maquilas.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/catalogos_t.py"""
from playwright.sync_api import sync_playwright
import os, json, tempfile
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
OUT = os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-'); os.makedirs(OUT, exist_ok=True)
seed = json.dumps(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json'))))
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em='admin@propesa.mx', pw='admin123'):
    pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0");localStorage.setItem("propesa-kp","0")}', seed); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def cat(pg): pg.evaluate("go('admin:cat')"); pg.wait_for_timeout(80)
def pedir(pg, t, i): pg.click(f'[data-cdel="ask:{t}:{i}"]'); pg.wait_for_timeout(80)
def cf(pg): return pg.inner_text('#cdel') if pg.locator('#cdel').count() else ''
def sin_desborde(pg): return not pg.evaluate("document.documentElement.scrollWidth>innerWidth+1")
J = lambda pg, js: pg.evaluate(js)

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg)
        # ---------- 0. Sin pestaña Maquilas ----------
        pg.evaluate("go('admin')"); pg.wait_for_timeout(80)
        tabs = [t.inner_text() for t in pg.locator('[role=tab]').all()]
        chk(tabs == ['Usuarios', 'Catálogos', 'Informes y respaldo'], f'{vw} Administración: Usuarios · Catálogos · Informes y respaldo ({tabs})')
        chk(pg.locator('[data-mqa]').count() == 0 and '+ Nueva maquila' not in pg.inner_text('#app'), f'{vw} ya no se agregan ni se ocultan maquilas')
        chk(pg.locator('[data-mq]').count() >= 1, f'{vw} se sigue cambiando de maquila con su botón')
        pg.evaluate("go('admin:mq')"); pg.wait_for_timeout(80)
        chk(pg.locator('#mqs').count() == 0 and pg.locator('[role=tab][aria-selected=true]').count() == 1, f'{vw} go(admin:mq) ya no abre la pestaña')

        # ---------- 1. Proveedores ----------
        J(pg, "ST.PV=pvAll().map(q=>({...q})).concat([{id:901,n:'NEWPROV',k:'XR',rfc:'SPE869101AB1',per:'420420420'},{id:902,n:'provenew2',k:'PV',rfc:'',per:''}]);save()")
        cat(pg)
        chk(pg.locator('#provs [data-cdel^="ask:pv:"]').count() == 5, f'{vw} cada proveedor tiene «Eliminar»')
        e = pg.locator('[data-cdel="ask:pv:901"]')
        chk('dq' in e.get_attribute('class') and pg.evaluate("e=>e.parentElement.lastElementChild===e", e.element_handle()), f'{vw} «Eliminar» es discreto (rojo) y va al final de la fila')
        chk(e.get_attribute('aria-label') == 'Eliminar el proveedor NEWPROV', f'{vw} el botón dice a quién borra')
        pedir(pg, 'pv', 901)
        chk('¿Eliminar el proveedor NEWPROV?' in cf(pg) and pg.locator('[data-cdel="del:pv:901"]').inner_text() == 'Sí, eliminar proveedor', f'{vw} confirmación: dice qué se borra')
        chk(pg.evaluate("document.activeElement&&document.activeElement.closest('#cdel')!=null"), f'{vw} el foco pasa a la confirmación')
        chk(sin_desborde(pg) and pg.evaluate("(()=>{const r=document.getElementById('cdel').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1})()"), f'{vw} con la confirmación abierta no hay scroll de lado y se ve completa'); pg.screenshot(path=os.path.join(OUT, f'cat_pv_{vw[0]}.png'))
        pg.click('[data-cdel=no]'); pg.wait_for_timeout(60)
        chk(pg.locator('#cdel').count() == 0 and J(pg, "pvAll().length") == 5, f'{vw} «No» no borra nada')
        pedir(pg, 'pv', 901); pg.click('[data-cdel="del:pv:901"]'); pg.wait_for_timeout(80)
        chk(J(pg, "!pvBy(901)&&pvAll().length==4") and 'NEWPROV' not in pg.inner_text('#provs'), f'{vw} NEWPROV eliminado')
        chk(J(pg, "!encodeAll().has('V/901')&&encodeAll().has('V/902')"), f'{vw} ya no se comparte (sale de los registros)')
        chk(J(pg, "JSON.parse(localStorage.getItem('propesa-v4')).PV.every(p=>p.id!==901)"), f'{vw} se guardó')
        # usado: SCPP Ensenada tiene un lote (por su nombre)
        pedir(pg, 'pv', 1)
        t = cf(pg)
        chk('No se puede eliminar el proveedor SCPP Ensenada SCL: tiene 1 lote' in t and pg.locator('[data-cdel="del:pv:1"]').count() == 0, f'{vw} con lotes no se borra y dice cuántos ({t[:90]})')
        pg.click('[data-cdel="off:pv:1"]'); pg.wait_for_timeout(80)
        chk(J(pg, "pvBy(1).off===true&&R_('WLRCO051026A').origin==='SCPP Ensenada SCL'"), f'{vw} «Ocultar» desde ahí; el lote no cambia')
        # en otra maquila también cuenta
        J(pg, "STX[2]={...mqSeed(),R:[{lot:'WLRXX010126',pv:902,origin:'provenew2',sp:1,closed:false}]}")
        cat(pg); pedir(pg, 'pv', 902)
        chk('tiene 1 lote' in cf(pg), f'{vw} un lote en otra maquila también cuenta')
        J(pg, "delete STX[2]"); pg.click('[data-cdel=no]')

        # ---------- 2. Especies ----------
        J(pg, "ST.ES=esAll().map(q=>({...q})).concat([{id:903,n:'Langosta Azul',en:'Blue lobster'}]);save()"); cat(pg)
        pedir(pg, 'es', 1)
        chk('No se puede eliminar la especie Langosta Roja: tiene 2 lotes y está en 2 órdenes' in cf(pg), f'{vw} Langosta Roja (lotes y órdenes) no se borra ({cf(pg)[:100]})')
        pedir(pg, 'es', 903); pg.click('[data-cdel="del:es:903"]'); pg.wait_for_timeout(80)
        chk(J(pg, "!esBy(903)&&esAll().length==1&&!encodeAll().has('E/903')"), f'{vw} especie sin uso eliminada')
        J(pg, "ST.R=[];ST.L=[];ST.B={};ST.OR=[];ST.P=[];save()"); cat(pg); pedir(pg, 'es', 1)
        chk('debe quedar al menos una especie en la lista' in cf(pg) and pg.locator('[data-cdel="off:es:1"]').count() == 0, f'{vw} la última especie no se borra ni se oculta')
        pg.click('[data-cdel=no]')

        # ---------- 3. Destinos ----------
        J(pg, "dsOwn().push({c:'TPE',n:'Taipéi'});cnOwn()[0].p.push('TPE');save();cnSync()"); cat(pg)
        pedir(pg, 'ds', 'XMN')
        chk('es el único destino de XIAMEN COASTAL' in cf(pg), f'{vw} XMN es el único destino de XIAMEN COASTAL: no se borra')
        J(pg, "ST.OR=[{id:1,etd:'2026-11-07',lines:[{id:1,city:'TPE',cons:0,boxes:2}],sh:{}}];save()"); cat(pg); pedir(pg, 'ds', 'TPE')
        chk('está en 1 línea de orden' in cf(pg), f'{vw} destino en una orden no se borra')
        J(pg, "ST.OR=[];save()"); cat(pg); pedir(pg, 'ds', 'TPE'); pg.click('[data-cdel="del:ds:TPE"]'); pg.wait_for_timeout(80)
        chk(J(pg, "!ST.DS.some(x=>x.c=='TPE')&&!CONS[0].p.includes('TPE')&&CONS[0].p.length==4&&!hasOwn(PORTS,'TPE')&&!encodeAll().has('X/TPE')"), f'{vw} TPE eliminado y quitado de YISHUNHAI')

        # ---------- 4. Tallas (por posición) ----------
        J(pg, "ST.SZ=szAll().map(q=>({...q})).concat([{id:'z950',k:'z950',n:'Extra',r:'1500-UP',c:'#123456',cn:'Azul',en:'Extra'}]);save();szSync()")
        J(pg, "ST.R=[{lot:'WLRCO010126',pv:2,origin:'SCPP Emancipación SC de RL',sp:1,closed:false,date:'2026-11-01',rdate:'2026-11-01'}];ST.L=[{id:1,t:'01/11/26, 08:00',type:'RECEPCION',lot:'WLRCO010126',size:'491-610',m:50}];"
               "ST.OR=[{id:1,etd:'2026-11-07',lines:[{id:1,city:'PVG',cons:0,boxes:3,z:[1,0,0,0,0,2]},{id:2,city:'PVG',cons:1,boxes:1,z:[1,0,0,0]}],sh:{}}];ST.P=[{u:'pq1',n:'PVG',h:3,z:[1,0,0,0,0,2],c:[]}];save();render()")
        cat(pg)
        chk(pg.locator('#szs [data-cdel^="ask:sz:"]').count() == 6, f'{vw} cada talla tiene «Eliminar»')
        pedir(pg, 'sz', '491-610')
        chk('No se puede eliminar la talla Chica: tiene 1 movimiento de lotes y está en 2 líneas de orden y está en 1 embarque' in cf(pg), f'{vw} Chica (usada) no se borra ({cf(pg)[:120]})')
        pedir(pg, 'sz', 'z950'); chk('No se puede eliminar la talla Extra: está en 1 línea de orden y está en 1 embarque' in cf(pg), f'{vw} Extra en una orden no se borra')
        pedir(pg, 'sz', 'desp'); pg.click('[data-cdel="del:sz:desp"]'); pg.wait_for_timeout(80)
        chk(J(pg, "JSON.stringify(S)") == '["491-610","611-850","851-1220","1221-up","z950"]', f'{vw} Despatada (sin uso) eliminada')
        chk(J(pg, "JSON.stringify([ST.OR[0].lines[0].z,ST.OR[0].lines[1].z,ST.P[0].z])") == '[[1,0,0,0,2],[1,0,0,0],[1,0,0,0,2]]', f'{vw} lo de Extra se recorre a su nueva posición (órdenes y embarques)')
        chk(J(pg, "encodeAll().get('Z/tallas')[1].l.length==5&&!JSON.stringify(encodeAll().get('Z/tallas')).includes('desp')"), f'{vw} se comparte sin Despatada')
        chk(J(pg, "OD.z.length==S.length"), f'{vw} el borrador de la orden se acomoda a las tallas')
        # otra maquila con hieleras de lotes de esta maquila: no se recorren posiciones de en medio
        J(pg, "STX[2]={...mqSeed(),B:{'WLRCO010126@1':[{c:1,k:'R',seq:7}]}};ST.SZ.splice(4,0,{id:'z951',k:'z951',n:'Muestra',r:'',c:'#654321',cn:'Café',en:'Sample'});ST.OR[0].lines[0].z.splice(4,0,0);ST.P[0].z.splice(4,0,0);save();szSync()"); cat(pg)
        pedir(pg, 'sz', 'z951'); chk('otra maquila tiene hieleras de lotes de esta maquila' in cf(pg), f'{vw} si otra maquila tiene hieleras de aquí, no se recorre')
        J(pg, "delete STX[2]"); cat(pg); pedir(pg, 'sz', 'z951'); pg.click('[data-cdel="del:sz:z951"]'); pg.wait_for_timeout(80)
        chk(J(pg, "S.length==5&&S[4]=='z950'&&JSON.stringify(ST.OR[0].lines[0].z)=='[1,0,0,0,2]'"), f'{vw} sin eso, sí se elimina y Extra regresa a su lugar')

        # ---------- 5. Consignatarios (por posición, en todas las maquilas) ----------
        J(pg, "const L=cnOwn();L.push({k:'PRUEBA',n:'Prueba Uno',p:['PVG']},{k:'PRUEBA2',n:'Prueba Dos',p:['PVG']});ST.CC={0:'#111111',7:'#222222',8:'#333333'};"
              "ST.OR=[{id:1,etd:'2026-11-07',lines:[{id:1,city:'PVG',cons:8,boxes:1},{id:2,city:'PVG',cons:0,boxes:1}],sh:{'PVG|8':0,'PVG|0':0}}];ST.P=[{u:'pq1',n:'PVG',h:1,z:[0,0,0,0],c:[]}];"
              "STX[2]={...mqSeed(),OR:[{id:5,etd:'2026-11-08',lines:[{id:1,city:'PVG',cons:8,boxes:1}],sh:{},_sh:{'PVG|8':'abc'}}]};OD.cons=8;save();cnSync();render()")
        cat(pg)
        pedir(pg, 'cn', 0); chk('No se puede eliminar el consignatario YISHUNHAI: está en 1 línea de orden' in cf(pg), f'{vw} YISHUNHAI (en una orden) no se borra')
        pedir(pg, 'cn', 8); chk('está en 2 líneas de orden' in cf(pg), f'{vw} PRUEBA2 cuenta también las órdenes de otra maquila')
        pedir(pg, 'cn', 7)
        chk('¿Eliminar el consignatario PRUEBA?' in cf(pg), f'{vw} PRUEBA sin uso se puede eliminar')
        pg.click('[data-cdel="del:cn:7"]'); pg.wait_for_timeout(80)
        chk(J(pg, "CONS.length==8&&CONS[7].k=='PRUEBA2'"), f'{vw} PRUEBA eliminado; PRUEBA2 pasa a su lugar')
        chk(J(pg, "JSON.stringify([ST.OR[0].lines.map(l=>l.cons),Object.keys(ST.OR[0].sh).sort(),ST.CC])") == '[[7,0],["PVG|0","PVG|7"],{"0":"#111111","7":"#333333"}]', f'{vw} órdenes, embarques y colores se recorren')
        chk(J(pg, "JSON.stringify([STX[2].OR[0].lines[0].cons,STX[2].OR[0]._sh])") == '[7,{"PVG|7":"abc"}]', f'{vw} también en la otra maquila')
        chk(J(pg, "OD.cons") == 7, f'{vw} el borrador de la orden sigue en PRUEBA2')
        enc = J(pg, "(()=>{const m=encodeAll();return [m.has('K/7'),m.has('K/8'),m.get('K/7')[1].k,m.get('q2:OR/5')[1].lines[0].cons]})()")
        chk(enc == [True, False, 'PRUEBA2', 7], f'{vw} se comparte ya recorrido ({enc})')
        chk('#333333' in pg.inner_html('#conss') and 'PRUEBA2' in pg.inner_text('#conss'), f'{vw} PRUEBA2 conserva su color en la lista')

        # ---------- 6. Solo el Administrador ----------
        pg.evaluate("me=null;render()"); pg.fill('#le', 'piso@propesa.mx'); pg.fill('#lp', 'piso123'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
        pg.evaluate("go('admin:cat')"); pg.wait_for_timeout(80)
        chk(pg.locator('[data-cdel]').count() == 0, f'{vw} sin Administrador no hay «Eliminar»')
        pg.close()

    # ---------- 7. Tamaños y tema oscuro ----------
    for w, h, th, fs in [(1440, 900, 'light', 17), (820, 1180, 'dark', 20), (744, 1133, 'light', 20)]:
        pg = b.new_page(viewport={'width': w, 'height': h}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg); pg.evaluate(f"localStorage.setItem('propesa-theme','{th}');localStorage.setItem('propesa-fs','{fs}');applyPrefs&&applyPrefs()")
        cat(pg); pedir(pg, 'pv', 1)
        chk(sin_desborde(pg), f'{w} px ({th}, {fs} px): Catálogos con confirmación sin scroll de lado')
        hs = pg.evaluate("[...document.querySelectorAll('#provs tbody tr')].map(r=>[r.querySelector('[data-pva^=ed]').getBoundingClientRect().height,r.querySelector('[data-cdel]').getBoundingClientRect().height])")
        chk(all(abs(a - c) < 1 for a, c in hs), f'{w} px: «Eliminar» mide lo mismo que «Editar» ({hs[0]})')
        bs = pg.evaluate("[...document.querySelectorAll('#cdel button')].map(e=>e.getBoundingClientRect().height)")
        chk(bs and min(bs) >= 44, f'{w} px: los botones de la confirmación miden 44 px o más ({bs})')
        chk(pg.evaluate("(()=>{const r=document.getElementById('cdel').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth})()"), f'{w} px: la confirmación se ve completa (no queda fuera de la tabla)')
        pg.screenshot(path=os.path.join(OUT, f'cat_{w}.png'), full_page=True); pg.close()
    b.close()
chk(not errs, f'sin errores de JavaScript {errs[:3]}')
print(f"\n{'TODO BIEN' if not fails else str(len(fails)) + ' FALLAS'}")
