"""Base compartida: varios equipos y varias cuentas ven lo mismo (v1.4.0).
Levanta un Supabase de mentira (pruebas/supabase_falso.py) y abre varios navegadores a la vez.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/sincronizacion_t.py"""
import os, sys, json, time, subprocess, urllib.request
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.environ.get('APP', 'http://localhost:8765/index.html')   # sin ?modo=local: usa la base compartida
MOCK = 'http://127.0.0.1:8790'
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def mock(path, post=False):
    r = urllib.request.urlopen(urllib.request.Request(MOCK + path, data=b'{}' if post else None, method='POST' if post else 'GET'))
    return json.loads(r.read() or b'null')

srv = subprocess.Popen([sys.executable, '-I', os.path.join(ROOT, 'pruebas', 'supabase_falso.py'), '8790'])
for _ in range(50):
    try: mock('/__reset', True); break
    except Exception: time.sleep(0.1)

INIT = "window.PROPESA_SB={url:'%s',key:'clave-publica-de-prueba'};try{localStorage.setItem('propesa-kp','0')}catch(e){}" % MOCK  # empaque con botones en cada caja
def until(pg, js, t=12):
    end = time.time() + t
    while time.time() < end:
        try:
            if pg.evaluate(js): return True
        except Exception: pass
        time.sleep(0.25)
    return False
def device(b, name, **kw):
    ctx = b.new_context(viewport={'width': 1180, 'height': 820}, **kw); ctx.add_init_script(INIT)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(name + ' JS ' + str(e)))
    pg.on('dialog', lambda d: d.accept('BORRAR') if d.type == 'prompt' else d.accept())
    pg.goto(APP); return ctx, pg
def login(pg, em, pw):
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]')
    return until(pg, "!!document.querySelector('.sb,.pshell,[data-avatar]')")
def new_lot(pg, code, kgs=(100, 200, 300, 400)):
    pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.fill('#fl', code); pg.fill('#fo', 'SCPP'); pg.fill('#fkb', '18')
    for i, v in enumerate(kgs): pg.fill(f'#fk{i}', str(v))
    pg.click('[data-a=sv]'); pg.wait_for_timeout(150)
def new_order(pg, etd, cli, n, city='PVG'):
    pg.evaluate("go('ordenes')"); pg.fill('#no_etd', etd); pg.click('[data-oa=new]')
    pg.select_option('#ol_city', city); pg.fill('#ol_cli', cli); pg.fill('#ol_n', str(n)); pg.click('[data-oa=ln]'); pg.wait_for_timeout(150)
DATA = "JSON.stringify(['R','L','B','OR','P','O','T','M'].map(k=>ST[k]))"
CORE = "JSON.stringify([ST.R.map(r=>r.lot),ST.L.map(x=>x.id),Object.keys(ST.B).sort().map(l=>ST.B[l].map(b=>[b.seq,b.c,b.k,b.d,b.o])),ST.OR.map(o=>[o.id,o.lines,o.sh]),ST.P.map(p=>[p.u,p.n,p.h]),Object.keys(ST.M).sort().map(k=>[k,ST.M[k].map(n=>n.text)])])"

try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        # --- base nueva sin Administrador: Configuración inicial crea la cuenta en la base compartida
        mock('/__sin_usuarios', True); c0, Z = device(b, 'Z')
        chk(until(Z, "!!document.getElementById('s0n')"), 'base sin Administrador: pide la Configuración inicial')
        chk(Z.locator('input[data-bk=up]').count() == 0, 'la Configuración inicial ya no ofrece restaurar en el equipo')
        Z.fill('#s0n', 'Primera Admin'); Z.fill('#s0e', 'primera@propesa.mx'); Z.fill('#s0p', 'Corta-1'); Z.fill('#s0q', 'Corta-1'); Z.click('[data-a=s0]')
        chk('al menos 8 caracteres' in Z.inner_text('#lm') and not mock('/__estado')['users'], 'v1.7.0 (auditoría #20): una contraseña de 7 caracteres no se acepta')
        Z.fill('#s0n', 'Primera Admin'); Z.fill('#s0e', 'primera@propesa.mx'); Z.fill('#s0p', 'Primera-2026'); Z.fill('#s0q', 'Primera-2026'); Z.click('[data-a=s0]')
        chk(until(Z, "!!me&&me.role=='admin'&&!!document.querySelector('.sb')"), 'crea el Administrador en la base compartida y entra')
        chk(any(u['email'] == 'primera@propesa.mx' and u['role'] == 'admin' for u in mock('/__estado')['users']), 'la cuenta del Administrador existe en el servidor')
        c0.close(); mock('/__reset', True)
        # --- v1.7.0 (auditoría #15): si borran a los Administradores desde el panel, la página ya no deja crear uno nuevo
        mock('/__sin_admins', True); c1, Y = device(b, 'Y')
        chk(until(Y, "!!document.getElementById('s0n')"), 'sin Administradores (pero con otras cuentas) se ve la Configuración inicial')
        Y.fill('#s0n', 'Intruso'); Y.fill('#s0e', 'intruso@x.mx'); Y.fill('#s0p', 'Intruso-2026'); Y.fill('#s0q', 'Intruso-2026'); Y.click('[data-a=s0]')
        chk(until(Y, "document.getElementById('lm').textContent.includes('Ya hay cuentas en la base')"), 'pero no deja crear un Administrador: «Ya hay cuentas en la base…»')
        chk(not any(u['email'] == 'intruso@x.mx' for u in mock('/__estado')['users']) and Y.evaluate("!me"), 'no se crea ninguna cuenta y no entra')
        c1.close(); mock('/__reset', True)
        ca, A = device(b, 'A'); cb, B = device(b, 'B')
        # --- acceso con cuentas de la base compartida
        A.fill('#le', 'admin@propesa.mx'); A.fill('#lp', 'mala-clave'); A.click('[data-a=lg]')
        chk(until(A, "document.getElementById('lm').textContent.includes('incorrectos')"), 'contraseña equivocada: «Correo o contraseña incorrectos»')
        chk(login(A, 'admin@propesa.mx', 'clave-admin1'), 'equipo A entra con su cuenta')
        chk(login(B, 'admin2@propesa.mx', 'clave-admin2'), 'equipo B entra con otra cuenta')
        chk(A.evaluate("ST.U.length") == 4 and A.evaluate("me.name") == 'Ana Torres', 'los usuarios vienen de la base compartida')
        chk(A.evaluate("localStorage.getItem('propesa-v4')") is None, 'no usa la memoria vieja de la tablet (propesa-v4)')

        # --- una entrada capturada en A aparece en B
        new_lot(A, 'WLRCO141026A')
        chk(until(B, "ST.R.some(r=>r.lot=='WLRCO141026A')"), 'entrada de A aparece en B')
        chk(B.evaluate("bal('WLRCO141026A')") == 1000000, 'B ve la misma existencia (1000 kg)')
        B.evaluate("go('recepcion')"); chk('WLRCO141026A' in B.inner_text('#app'), 'B la ve en la pantalla de Entrada')
        chk('En vivo' in B.inner_text('.tqleg') and 'WLRCO141026A' in B.inner_text('.tqd'), 'tablero de tanques en B: «● En vivo» y el lote de A en su tanque')
        new_lot(A, 'WLRCO141026E'); B.evaluate("document.activeElement&&document.activeElement.blur()")
        chk(until(B, "V.v=='recepcion'&&document.querySelector('.tqd').textContent.includes('WLRCO141026E')"), 'el tablero de B muestra solo la entrada nueva de A, sin recargar (en vivo)')
        A.evaluate("go('lote:WLRCO141026E')"); A.click('[data-a=dl]'); A.click('[data-a=dl2]')
        chk(until(B, "!document.querySelector('.tqd').textContent.includes('WLRCO141026E')"), 'si A borra ese lote, desaparece del tablero de B')

        # --- dos entradas al mismo tiempo en A y en B: no se pisan
        new_lot(A, 'WLRLE141026C'); new_lot(B, 'WLREM141026B')
        chk(until(A, "ST.R.length==3") and until(B, "ST.R.length==3"), 'dos entradas al mismo tiempo: los dos equipos tienen las 3')
        chk(until(A, "ST.L.length==12") and until(B, "ST.L.length==12"), 'los 12 movimientos de inventario llegan a los dos (ids que no chocan)')

        # --- orden en A, empaque en B
        new_order(A, '2026-10-15', 'HXH', 3)
        chk(until(B, "ST.OR.length==1&&ST.P.length==1&&ST.P[0].h==3"), 'orden de A aparece en B con su embarque (3 hieleras)')
        B.evaluate("go('empaque')"); B.locator('[data-go^="empacar:"]').first.click(); B.click('[data-pk="lot:WLRCO141026A"]')
        B.fill('#pk_c0', '30'); B.click('#pkr0 [data-pk^="k:"] >> nth=0'); B.fill('#pk_c1', '25'); B.click('#pkr1 [data-pk^="k:"] >> nth=1')
        B.click('[data-pk=addall]'); B.wait_for_timeout(200)
        chk(B.evaluate("Object.values(ST.B).flat().length") == 2, 'B guardó 2 cajas: %s' % B.evaluate("JSON.stringify(ST.B)+' '+document.getElementById('toast').textContent"))
        chk(until(A, "Object.values(ST.B).flat().length==2"), 'cajas empacadas en B aparecen en A')
        chk(A.evaluate("Object.values(ST.B).flat().every(b=>b.d===0)"), 'en A las cajas apuntan al mismo embarque')
        chk(A.evaluate("sent(0)") == 55, 'A ve 55 langostas en el embarque')
        # nota del embarque en A → B
        A.evaluate("go('emb:0')"); A.fill('#ntx', 'Tarima revisada'); A.click('[data-ev^=save]')
        chk(until(B, "(ST.M['emb:0']||[]).some(n=>n.text=='Tarima revisada')"), 'nota del embarque de A aparece en el mismo embarque en B')

        # --- dos órdenes al mismo tiempo: mismos embarques y en el mismo orden en los dos equipos
        new_order(A, '2026-10-16', 'ZSM', 2, 'XMN'); new_order(B, '2026-10-16', 'LHD', 4, 'HKG')
        chk(until(A, "ST.OR.length==3&&ST.P.length==3") and until(B, "ST.OR.length==3&&ST.P.length==3"), 'dos órdenes al mismo tiempo: 3 órdenes y 3 embarques en los dos')
        chk(until(A, "1") and A.evaluate("ST.P.map(p=>p.u).join()") == B.evaluate("ST.P.map(p=>p.u).join()"), 'los embarques quedan en el mismo orden en los dos equipos')
        time.sleep(1.5)
        chk(until(B, "1", 1) and A.evaluate(CORE) == B.evaluate(CORE), 'A y B tienen exactamente los mismos datos')

        # --- sin internet en B: se guarda y se sube después
        cb.set_offline(True); new_lot(B, 'WLRCO141026D')
        chk(until(B, "document.body.innerText.includes('Sin conexión')", 15), 'B sin internet: aviso «Sin conexión» con lo pendiente')
        chk(B.evaluate("outN()") > 0, 'B guarda el cambio pendiente en el equipo')
        time.sleep(5); chk(not A.evaluate("ST.R.some(r=>r.lot=='WLRCO141026D')"), 'A todavía no lo ve (B sin internet)')
        cb.set_offline(False); B.evaluate("window.dispatchEvent(new Event('online'))")
        chk(until(A, "ST.R.some(r=>r.lot=='WLRCO141026D')", 15), 'al volver el internet, A recibe la entrada de B')
        chk(until(B, "outN()==0&&!document.body.innerText.includes('Sin conexión')", 15), 'B ya no tiene pendientes y quita el aviso')

        # --- borrar en A desaparece en B
        A.evaluate("go('lote:WLRCO141026D')"); A.click('[data-a=dl]'); A.click('[data-a=dl2]')
        chk(until(B, "!ST.R.some(r=>r.lot=='WLRCO141026D')&&!ST.L.some(x=>x.lot=='WLRCO141026D')"), 'lote borrado en A desaparece en B (con sus movimientos)')

        # --- sesión vencida: se renueva sola y el cambio se sube
        mock('/__expira', True); A.evaluate("ST.R[0].final=null;R_('WLRCO141026A').desp=7;save()")
        chk(until(B, "R_('WLRCO141026A').desp==7"), 'con el token vencido la app se renueva sola y el cambio llega')

        # --- sin escrituras de ida y vuelta cuando nadie captura
        time.sleep(3); w0 = mock('/__estado')['writes']; time.sleep(9); w1 = mock('/__estado')['writes']
        chk(w1 == w0, f'sin cambios de nadie, no se reescribe nada ({w1 - w0} escrituras de más)')

        # --- consulta y piso ven lo mismo
        cc, C = device(b, 'C'); chk(login(C, 'consulta@propesa.mx', 'clave-ver1'), 'consulta entra')
        chk(until(C, "ST.R.length==3&&ST.OR.length==3"), 'consulta ve los mismos lotes y órdenes')
        for r in ['inicio', 'recepcion', 'ordenes', 'empaque', 'embarques', 'cierre', 'temperatura']: C.evaluate(f"go('{r}')")
        time.sleep(2); chk(mock('/__estado')['writes'] == w1, 'consulta no escribe nada en la base')
        C.evaluate("R_('WLRCO141026A').desp=99;save()"); time.sleep(6)
        chk(mock('/__estado')['writes'] == w1 and until(C, "R_('WLRCO141026A').desp==7"), 'si consulta cambia algo por error, no se sube y vuelve a lo de la base')
        cp, D = device(b, 'D'); chk(login(D, 'piso@propesa.mx', 'clave-piso1'), 'encargado de piso entra (Modo piso)')
        chk(until(D, "ST.R.length==3&&Object.values(ST.B).flat().length==2"), 'piso ve los mismos datos')

        # --- usuarios desde la app (Administración)
        A.evaluate("go('admin')"); A.click('[data-a=nu]'); A.fill('#un', 'Rosa Pérez'); A.fill('#ue', 'rosa@propesa.mx'); A.fill('#up', 'Rosa-2026'); A.select_option('#ur', 'piso'); A.click('[data-a=su]')
        chk(until(A, "ST.U.some(u=>u.email=='rosa@propesa.mx'&&u.role=='piso')"), 'el Administrador da de alta un usuario en la base compartida')
        chk(any(u['email'] == 'rosa@propesa.mx' for u in mock('/__estado')['users']), 'la cuenta existe en el servidor')
        ce, R2 = device(b, 'E'); chk(login(R2, 'rosa@propesa.mx', 'Rosa-2026'), 'el usuario nuevo entra desde otro equipo')
        A.evaluate("go('admin')"); A.click('[data-a=nu]'); A.fill('#un', 'Corto'); A.fill('#ue', 'corto@propesa.mx'); A.fill('#up', 'Siete77'); A.click('[data-a=su]')
        chk('al menos 8 caracteres' in A.inner_text('#app') and not any(u['email'] == 'corto@propesa.mx' for u in mock('/__estado')['users']), 'Administración: contraseña de 7 caracteres no se acepta')
        A.evaluate("go('inicio')")

        # --- recargar conserva sesión y datos
        B.reload(); chk(until(B, "!!me&&ST.R.length==3&&ST.OR.length==3"), 'recargar: B sigue dentro con los mismos datos')
        # --- v1.6.0 (auditoría #7): la copia del equipo vive en IndexedDB (cabe mucho más que en localStorage)
        rec = B.evaluate("idbGet('propesa-c1').then(r=>r&&{n:JSON.parse(r.st).R.length,since:r.since})")
        chk(rec and rec['n'] == 3 and rec['since'] > 0 and B.evaluate("localStorage.getItem('propesa-c1')") is None, f'la copia de B está en IndexedDB con hasta dónde bajó, y no en localStorage: {rec}')
        big = "'data:image/jpeg;base64,'+'A'.repeat(120000)"
        A.evaluate(f"(()=>{{const im={big};ST.M.recepcion=ST.M.recepcion||[];for(let i=0;i<45;i++)ST.M.recepcion.unshift({{id:uidN(),t:now(),by:'Ana Torres',text:'foto '+i,ref:'',imgs:[im]}});save()}})()")
        A.evaluate("cacheST()"); r45 = A.evaluate("CACHE_W.then(()=>idbGet('propesa-c1')).then(r=>({len:r.st.length,err:CACHE_ERR}))")
        chk(r45['len'] > 5_400_000 and not r45['err'], f'con 45 fotos (más de 5 millones de letras) la copia se guarda completa y sin aviso: {r45}')
        chk(until(A, "outN()==0", 30), 'las 45 fotos se suben a la base')
        A.evaluate("ST.M.recepcion=ST.M.recepcion.filter(n=>!/^foto \\d+$/.test(n.text));save()"); chk(until(A, "outN()==0", 30), 'se quitan las fotos de prueba')
        # un equipo con la copia vieja en localStorage (v1.5) la pasa a IndexedDB al abrir
        cg, G = device(b, 'G'); old = json.dumps({'PK': 1, 'R': [{'id': 'R-9', 'lot': 'ZZVIEJO', 'origin': 'x', 'tank': 'T1', 'rdate': '2026-10-01', 'time': '', 'date': '', 'tempT': None, 'tempP': '', 'kgbox': None, 'desp': None, 'final': None, 'closed': False}], 'L': [], 'B': {'ZZVIEJO': []}, 'OR': [], 'P': [], 'O': [], 'T': [], 'M': {}, 'U': []})
        G.evaluate("s=>{localStorage.setItem('propesa-c1',s);localStorage.setItem('propesa-c1-since','5')}", old); G.reload()
        chk(until(G, "ST.R.some(r=>r.lot=='ZZVIEJO')&&SINCE===5"), 'la copia vieja de localStorage se usa al abrir')
        chk(until(G, "localStorage.getItem('propesa-c1')===null") and G.evaluate("idbGet('propesa-c1').then(r=>JSON.parse(r.st).R[0].lot)") == 'ZZVIEJO', 'y se pasa a IndexedDB (se libera localStorage)')
        cg.close()
        # si el navegador no deja guardar la copia: aviso, y lo capturado sí se sube
        ch2, H = device(b, 'H'); H.evaluate("1"); ch2.add_init_script("IDBObjectStore.prototype.put=function(){throw new DOMException('lleno','QuotaExceededError')}")
        H.reload(); chk(login(H, 'admin2@propesa.mx', 'clave-admin2') and until(H, "ST.R.length==3"), 'equipo con la memoria llena entra y baja los datos')
        H.evaluate("go('inicio');ST.R[0].desp=11;save();cacheST()")
        chk(until(H, "document.body.innerText.includes('No se pudo guardar la copia de este equipo')"), 'aviso «No se pudo guardar la copia de este equipo»')
        chk(until(A, "ST.R[0].desp===11"), 'aun así el cambio llega a los demás equipos')
        ch2.close()
        # --- equipo nuevo descarga todo
        cf, F = device(b, 'F'); chk(login(F, 'admin2@propesa.mx', 'clave-admin2'), 'equipo nuevo entra')
        chk(until(F, "ST.R.length==3&&ST.OR.length==3&&ST.P.length==3") and until(F, "1") and F.evaluate(CORE) == A.evaluate(CORE), 'equipo nuevo descarga exactamente lo mismo')
        # --- borrar todos los datos (Administración) llega a todos
        A.evaluate("go('admin')"); A.click('[data-a=rst]')
        chk(until(F, "ST.R.length==0&&ST.OR.length==0&&ST.P.length==0") and until(C, "ST.R.length==0"), 'Borrar todos los datos llega a todos los equipos')
        chk(A.evaluate("!!me") and A.evaluate("ST.U.length") >= 5, 'después de borrar, los usuarios siguen y A sigue dentro')
        # --- respaldo restaurado llega a todos
        A.evaluate("go('admin')"); A.locator('input[data-bk=up]').first.set_input_files(os.path.join(ROOT, 'pruebas', 'datos', 'backup.json'))
        chk(until(A, "ST.R.length>=1") and until(F, f"ST.R.length=={A.evaluate('ST.R.length')}&&ST.OR.length=={A.evaluate('ST.OR.length')}", 20), 'restaurar un respaldo lo pone en todos los equipos')
        time.sleep(1.5); chk(until(F, "1") and F.evaluate(CORE) == A.evaluate(CORE), 'tras restaurar, A y el equipo nuevo son idénticos')
        sweep = []
        for r in ['inicio', 'recepcion', 'ordenes', 'empaque', 'embarques', 'cierre', 'temperatura', 'admin']:
            F.evaluate(f"go('{r}')"); tx = F.inner_text('#app')
            if 'NaN' in tx or 'undefined' in tx: sweep.append(r)
        chk(not sweep, f'sin NaN/undefined con los datos sincronizados {sweep}')

        # --- v1.4.1: un equipo que estuvo sin internet no pisa lo que otro guardó
        i = A.evaluate("ST.P.findIndex(p=>!p.closed)"); chk(i >= 0, 'hay un embarque abierto para la prueba')
        chk(until(D, f"ST.P.map(p=>p.u).join()=={json.dumps(A.evaluate('ST.P.map(p=>p.u).join()'))}"), 'piso tiene los mismos embarques que A')
        cp.set_offline(True); D.evaluate(f"ST.P[{i}].alive=1;save()")
        A.evaluate(f"ST.P[{i}].closed=true;save()"); chk(until(A, "outN()==0"), 'A cierra el embarque mientras piso está sin internet')
        cp.set_offline(False); D.evaluate("window.dispatchEvent(new Event('online'))")
        chk(until(D, f"outN()==0&&ST.P[{i}].closed===true", 15), 'al volver el internet, piso NO reabre el embarque: recibe el cerrado')
        chk('No se guardó tu cambio' in D.text_content('#toast'), 'piso ve el aviso de que su cambio no se guardó')
        time.sleep(5); chk(A.evaluate(f"ST.P[{i}].closed===true"), 'en A el embarque sigue cerrado')
        # cambios normales siguen subiendo (sin choque)
        D.evaluate(f"ST.P[{i}].alive=2;save()"); chk(until(A, f"ST.P[{i}].alive===2"), 'después del choque, el siguiente cambio de piso sí llega')

        # --- v1.4.1: Consulta en la misma tablet no borra lo pendiente de piso
        cp.set_offline(True); tid = D.evaluate("(()=>{const id=uidN();ST.T.push({id,t:'2026-10-14T10:00',tank:'T1',a:55,s:null,p:null,by:'Luis Meza'});save();return id})()")
        chk(D.evaluate("outN()") == 1, 'piso sin internet: 1 cambio pendiente')
        D.evaluate("signOut()"); until(D, "!!document.getElementById('le')", 15); cp.set_offline(False)
        chk(login(D, 'consulta@propesa.mx', 'clave-ver1'), 'consulta entra en la tablet de piso'); time.sleep(5)
        chk(D.evaluate("outN()") == 1 and f'T/{tid}' not in mock('/__estado')['recs'], 'consulta no sube ni borra lo pendiente de piso')
        D.evaluate("signOut()"); until(D, "!!document.getElementById('le')", 15)
        chk(login(D, 'piso@propesa.mx', 'clave-piso1') and until(D, "outN()==0", 15), 'piso vuelve a entrar y se sube lo pendiente')
        chk((mock('/__estado')['recs'].get(f'T/{tid}') or {}).get('v', {}).get('a') == 55, 'la lectura de temperatura de piso llegó a la base')

        # --- v1.4.1: si la base rechaza lo que sube un equipo, ese equipo sigue recibiendo lo de los demás
        mock('/__falla_push', True); D.evaluate("ST.T.push({id:uidN(),t:'2026-10-14T11:00',tank:'T2',a:54,s:null,p:null,by:'Luis Meza'});save()")
        chk(until(D, "!!SYNC_ERR&&SYNC_ERR.status===400&&outN()==1", 15), 'base rechaza lo de piso: queda pendiente con el error')
        A.evaluate("ST.R[0].desp=8;save()"); chk(until(D, "ST.R[0].desp===8", 15), 'aun así piso recibe los cambios de A')
        mock('/__falla_push', True); D.evaluate("syncNow(true)"); chk(until(D, "outN()==0&&!SYNC_ERR", 15), 'cuando la base vuelve a aceptar, se sube lo pendiente')
        # --- texto con carácter nulo: se limpia y se sube (antes trababa la cola)
        lot0 = A.evaluate("ST.R[0].lot"); A.evaluate("ST.R[0].origin='SC'+String.fromCharCode(0)+'PP';save()")
        chk(until(A, "outN()==0&&!SYNC_ERR") and mock('/__estado')['recs']['R/' + lot0]['v']['origin'] == 'SCPP', 'texto con carácter nulo se sube sin trabarse')

        # --- v1.4.1: dos Administradores sacan del mismo lote al mismo tiempo: aviso de existencia negativa
        lotn = A.evaluate("ST.R.find(r=>bal(r.lot,S[0])>0).lot"); q = A.evaluate(f"bal({json.dumps(lotn)},S[0])/1000")
        chk(until(B, f"bal({json.dumps(lotn)},S[0])/1000=={q}"), 'B tiene la misma existencia que A')
        cb.set_offline(True)
        A.evaluate(f"post('SALIDA_EMBARQUE',{json.dumps(lotn)},S[0],-{q}*0.6);save()"); B.evaluate(f"post('SALIDA_EMBARQUE',{json.dumps(lotn)},S[0],-{q}*0.6);save()")
        chk(not A.evaluate("document.getElementById('app').textContent.includes('Existencia negativa')"), 'con una sola salida no hay aviso')
        A.evaluate("document.activeElement&&document.activeElement.blur()")  # con el cursor en un campo la app espera para no borrar lo escrito
        cb.set_offline(False); B.evaluate("window.dispatchEvent(new Event('online'))")
        chk(until(A, "document.getElementById('app').textContent.includes('Existencia negativa')", 15), 'al llegar la salida de B, A ve el aviso «Existencia negativa»')
        A.click('[data-go^="lote:"] >> text=Ver lote'); chk(A.evaluate(f"V.v=='lote'&&V.id=={json.dumps(lotn)}"), 'el aviso lleva al lote')
        A.evaluate(f"rev(ST.L.filter(x=>x.lot=={json.dumps(lotn)}&&x.type=='SALIDA_EMBARQUE').pop().id)")
        chk(until(A, "!document.getElementById('app').textContent.includes('Existencia negativa')"), 'al revertir la salida que sobra, el aviso se quita')
        chk(not D.evaluate("document.getElementById('app').textContent.includes('Existencia negativa')"), 'piso no ve el aviso (no puede corregir movimientos)')

        # --- v1.4.1: lo que llega de la base no puede meter código en la pantalla (cuenta de piso escribiendo directo a la base)
        bad = '<img src=x onerror="window.__x=1">'
        D.evaluate("""async(bad)=>{const t=JSON.parse(localStorage.getItem('propesa-sb')).at;const rows=[
          {k:'P/zzzzzzzzzzzzzzz',v:{u:'zzzzzzzzzzzzzzz',n:'PVG · '+bad+' · 1',z0:bad,col:'red" onmouseover="window.__x=1',exp:0,h:1,z:[0,0,0,0],c:[[bad,1,1]],alive:null,closed:false}},
          {k:'R/ZZBAD',v:{id:'1',lot:'ZZ'+bad,origin:bad,tank:bad,rdate:'2026-10-14',time:'10:00',date:bad,tempT:bad,tempP:bad,kgbox:bad,desp:bad,final:bad,closed:false}},
          {k:'T/55555',v:{id:55555,t:'2026-10-14T10:00',tank:'T1',a:bad,s:bad,p:bad,by:bad}},
          {k:'M/987654',v:{key:'recepcion',id:987654,t:bad,by:bad,text:bad,ref:bad,imgs:['data:image/png;base64,AAAA" onerror="window.__x=1']}},
          {k:'OR/987654',v:{id:987654,etd:'2026-10-20',lines:[{id:1,city:'PVG',cons:0,cli:bad,boxes:1}],sh:{'PVG|0':'zzzzzzzzzzzzzzz'}}}];
          await fetch(PROPESA_SB.url+'/rest/v1/rpc/push',{method:'POST',headers:{apikey:'k',Authorization:'Bearer '+t,'Content-Type':'application/json'},body:JSON.stringify({rows})})}""", bad)
        chk(until(A, "ST.P.some(p=>p.u=='zzzzzzzzzzzzzzz')&&ST.OR.some(o=>o.id==987654)"), 'A recibe los registros con código escondido')
        hit = []
        for r in ['inicio', 'recepcion', "'lote:'+ST.R.find(r=>r.lot.startsWith('ZZ')).lot", 'ordenes', 'orden:987654', 'empaque', 'embarques',
                  "'emb:'+ST.P.findIndex(p=>p.u=='zzzzzzzzzzzzzzz')", 'cierre', 'temperatura', 'admin']:
            A.evaluate(f"go({r if r.startswith(chr(39)) else repr(r)})"); A.wait_for_timeout(300)
            A.mouse.move(300, 300); A.mouse.move(700, 400)
            if A.evaluate("!!window.__x||!!document.querySelector('#app img[src=\"x\"],#app [onerror],#app [onmouseover]')"): hit.append(r)
        chk(not hit, f'ninguna pantalla ejecuta código que llegó de la base {hit}')
        chk(A.evaluate("ST.P.find(p=>p.u=='zzzzzzzzzzzzzzz').col") == A.evaluate("XC[0]"), 'un color que no es color se cambia por el de siempre')
        chk(A.evaluate("(ST.M.recepcion||[]).find(n=>n.id==987654).imgs.length") == 0, 'una «foto» que no es imagen se descarta')
        chk(A.evaluate("(ST.T||[]).find(x=>x.id==55555).a") is None and A.evaluate("ST.R.find(r=>r.lot.startsWith('ZZ')).tempT") is None, 'un número con código (temperatura, kg) llega como vacío, no como texto')

        # --- v1.5.1 (auditoría #1): un registro con valores sin sentido no descompone pantallas en ningún equipo
        def raw_push(pg, rows):   # una cuenta de piso escribiendo directo a la base
            pg.evaluate("""async(rows)=>{const t=JSON.parse(localStorage.getItem('propesa-sb')).at;
              await fetch(PROPESA_SB.url+'/rest/v1/rpc/push',{method:'POST',headers:{apikey:'k',Authorization:'Bearer '+t,'Content-Type':'application/json'},body:JSON.stringify({rows})})}""", rows)
        lotv = A.evaluate("ST.R.find(r=>!r.lot.startsWith('ZZ')).lot"); n0 = len(errs)
        raw_push(D, [{'k': 'OR/987655', 'v': {'id': 987655, 'etd': 20261016, 'sh': {}, 'lines': [
                        {'id': 1, 'city': 'PVG', 'cons': 99, 'cli': 'HXH', 'boxes': 2},     # consignatario que no existe
                        {'id': 2, 'city': 'XXX', 'cons': 0, 'cli': 'ZSM', 'boxes': 2},      # ciudad que no existe
                        {'id': 3, 'city': 'PVG', 'cons': 0, 'cli': 'RSK', 'boxes': 0}]}},   # cero cajas
                     {'k': 'B/987656', 'v': {'lot': lotv, 'c': 5, 'k': 'Z', 'd': None, 'o': '987655.3', 'seq': 987656}},   # categoría que no existe
                     {'k': 'B/987657', 'v': {'lot': lotv, 'c': 0, 'k': 'R', 'd': None, 'o': '987655.3', 'seq': 987657}},   # caja sin piezas
                     {'k': 'T/987658', 'v': {'id': 987658, 't': None, 'tank': 'T1', 'a': 50}}])                           # lectura sin fecha
        chk(until(A, "ST.OR.some(o=>o.id==987655)") and until(D, "ST.OR.some(o=>o.id==987655)"), 'A y piso reciben la orden con valores sin sentido')
        chk(A.evaluate("JSON.stringify(ST.OR.find(o=>o.id==987655).lines.map(l=>[l.id,l.boxes]))+ST.OR.find(o=>o.id==987655).etd") == '[[3,1]]',
            'se quedan solo las líneas válidas (consignatario y ciudad que existen, mínimo 1 caja) y la fecha que no es fecha queda vacía')
        chk(not A.evaluate("Object.values(ST.B).flat().some(b=>b.seq>=987656&&b.seq<=987657)") and not A.evaluate("ST.T.some(x=>x.id==987658)"),
            'cajas sin piezas o con categoría que no existe y lecturas sin fecha se ignoran')
        for r in ['inicio', 'ordenes', 'orden:987655', 'empaque', 'empacar:987655.3', 'embarques', 'cierre', 'temperatura']:
            A.evaluate(f"go('{r}')"); A.wait_for_timeout(80)
        D.evaluate("setPiso(true)")
        for r in ['piso', 'pemp', 'pemp:987655.3', 'pent']:
            D.evaluate(f"go('{r}')"); D.wait_for_timeout(80)
        chk(len(errs) == n0, f'ninguna pantalla falla en A ni en Modo piso {errs[n0:]}')
        A.evaluate("go('inicio');document.getElementById('toast').textContent=''")
        A.evaluate("(()=>{const o=ST.OR.find(o=>o.id==987655);o.etd='2026-10-16';o.lines[0].boxes=2;save()})()")
        chk(until(A, "outN()==0&&!SYNC_BUSY", 15), 'el Administrador corrige esa orden y se sube')
        sv = mock('/__estado')['recs']['OR/987655']['v']
        chk(sv['etd'] == '2026-10-16' and [(l['id'], l['boxes']) for l in sv['lines']] == [(3, 2)], f'la orden queda arreglada también en la base: {sv}')
        chk('No se guardó' not in A.text_content('#toast'), 'sin aviso falso de «otro equipo lo cambió» al arreglarla')
        chk(until(D, "ST.OR.find(o=>o.id==987655).lines[0].boxes===2"), 'piso recibe la orden corregida')

        # --- v1.5.1 (auditoría #2): con internet lento, cambiar lo mismo dos veces seguidas guarda el segundo cambio
        i = A.evaluate("ST.P.findIndex(p=>!p.closed)"); pu = A.evaluate(f"ST.P[{i}].u")
        mock('/__lento', True); A.evaluate("document.getElementById('toast').textContent=''")
        A.evaluate(f"ST.P[{i}].z[0]=1;save()")
        chk(until(A, "SYNC_BUSY", 5), 'internet lento: el primer cambio (tallas 1) está subiendo')
        A.evaluate(f"ST.P[{i}].z[0]=2;save()")
        chk(until(A, "outN()==0&&!SYNC_BUSY", 20), 'el segundo cambio (tallas 2) también se sube')
        mock('/__lento', True)
        chk(mock('/__estado')['recs']['P/' + pu]['v']['z'][0] == 2 and A.evaluate(f"ST.P[{i}].z[0]") == 2, 'en la base y en A quedan las tallas 2')
        chk('No se guardó' not in A.text_content('#toast'), 'sin aviso falso de «otro equipo lo cambió»')
        chk(until(B, f"ST.P.find(p=>p.u=={json.dumps(pu)}).z[0]===2"), 'el otro equipo recibe las tallas 2')

        # --- v1.6.0 (auditoría #3): si otro equipo quita un embarque mientras escribes, las vivas y las tallas van al embarque correcto
        us0 = set(A.evaluate("ST.P.map(p=>p.u)")); new_order(A, '2026-10-17', 'HSF', 2, 'XMN')
        ut = [u for u in A.evaluate("ST.P.map(p=>p.u)") if u not in us0][0]; uj = json.dumps(ut)
        A.evaluate(f"(()=>{{const i=ST.P.findIndex(p=>p.u=={uj}),l=ST.R.find(r=>!r.lot.startsWith('ZZ')).lot;ST.B[l].push({{c:30,k:'R',d:i,o:null,seq:uidN()}});ST.P.forEach(p=>{{if(p.alive===9)p.alive=null}});save()}})()")
        dummy = lambda u: {'k': 'P/' + u, 'v': {'u': u, 'n': 'HKG · PRUEBA · 01/01', 'z0': '', 'col': '#1c7f9a', 'exp': 0, 'h': 0, 'z': [0, 0, 0, 0], 'c': [], 'alive': None, 'closed': False}}
        for fld, val, du in (('[data-alive]', '9', '000000'), ('[data-zs$=":1"]', '4', '0000000')):
            raw_push(D, [dummy(du)]); ix = lambda u: f"ST.P.findIndex(p=>p.u=={json.dumps(u)})"
            chk(until(A, f"{ix(du)}>=0&&{ix(du)}<{ix(ut)}"), f'llega un embarque nuevo que queda antes en la lista ({fld})')
            t = A.evaluate(ix(ut)); A.evaluate(f"go('emb:{t}')"); A.fill(fld, val)   # el cursor sigue en el campo
            raw_push(D, [{'k': 'P/' + du, 'v': None}])                                                         # otro equipo lo quita
            chk(until(A, f"ST.P.findIndex(p=>p.u=={uj})=={t - 1}"), f'la lista de embarques se recorre mientras escribe ({fld})')
            A.press(fld, 'Tab'); A.wait_for_timeout(200)
        chk(until(A, f"ST.P.find(p=>p.u=={uj}).alive===9") and A.evaluate("ST.P.filter(p=>p.alive===9).length") == 1, 'las 9 vivas quedan en el embarque que estaba en pantalla, no en otro')
        chk(until(A, f"ST.P.find(p=>p.u=={uj}).z[1]===4") and A.evaluate("ST.P.filter(p=>p.z[1]===4).length") == 1, 'las tallas también van al embarque correcto')
        chk(until(A, "outN()==0") and mock('/__estado')['recs']['P/' + ut]['v']['alive'] == 9, 'la base tiene las vivas en ese embarque')

        # --- v1.6.0 (auditoría #8): si la base no encuentra push (404), ya no se sube pisando: queda pendiente con aviso
        lot = A.evaluate("ST.R[0].lot"); d0 = mock('/__estado')['recs']['R/' + lot]['v']['desp']
        A.route('**/rest/v1/rpc/push', lambda r: r.fulfill(status=404, content_type='application/json', body='{"code":"PGRST202","message":"Could not find the function public.push"}'))
        A.evaluate("ST.R[0].desp=5;save()")
        chk(until(A, "!!SYNC_ERR&&SYNC_ERR.status===404&&outN()==1"), 'sin push en la base: el cambio queda pendiente con el error')
        time.sleep(2); chk(mock('/__estado')['recs']['R/' + lot]['v']['desp'] == d0, 'y no se sube por otro camino sin revisar choques')
        A.unroute('**/rest/v1/rpc/push'); A.evaluate("syncNow(true)")
        chk(until(A, "outN()==0") and mock('/__estado')['recs']['R/' + lot]['v']['desp'] == 5, 'cuando push vuelve, se sube')
        # --- cerrar sesión
        A.locator('#app [data-avatar]').first.click(); A.click('[data-pm=logout]')
        chk(until(A, "!!document.getElementById('le')") and A.evaluate("localStorage.getItem('propesa-sb')") is None, 'cerrar sesión regresa al acceso y olvida la sesión')
        b.close()
finally:
    srv.terminate()
print('ERRS', errs); print('RESULTADO:', 'TODO BIEN' if not fails and not errs else f'{len(fails)} fallas'); sys.exit(1 if fails or errs else 0)
