"""v1.38.0 · Auditoría Ponytail del 6/nov/2026 (#1, #2, #3), con el Supabase de mentira y varios navegadores.
#1 Una tablet con código viejo ya no borra los campos que no conoce, y una versión nueva publicada pide recargar y deja de subir.
#2 La misma entrada capturada en dos equipos: ids distintos y aviso rojo «se capturó 2 veces».
#3 Si entra Piso en un equipo con un precio pendiente del Administrador, ya no se pierde lo demás.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/v138_t.py"""
import os, sys, json, time, subprocess, urllib.request
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.environ.get('APP', 'http://localhost:8765/index.html')   # sin ?modo=local: usa la base compartida
MOCK = 'http://127.0.0.1:8796'
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def mock(path, post=False):
    r = urllib.request.urlopen(urllib.request.Request(MOCK + path, data=b'{}' if post else None, method='POST' if post else 'GET'))
    return json.loads(r.read() or b'null')
def recs(): return mock('/__estado')['recs']
srv = subprocess.Popen([sys.executable, '-I', os.path.join(ROOT, 'pruebas', 'supabase_falso.py'), '8796'])
for _ in range(50):
    try: mock('/__reset', True); break
    except Exception: time.sleep(0.1)
INIT = "window.PROPESA_SB={url:'%s',key:'clave-publica-de-prueba'};try{localStorage.setItem('propesa-kp','0')}catch(e){}" % MOCK
def until(pg, js, t=12):
    end = time.time() + t
    while time.time() < end:
        try:
            if pg.evaluate(js): return True
        except Exception: pass
        time.sleep(0.25)
    return False
def device(b, name):
    ctx = b.new_context(viewport={'width': 1180, 'height': 820}); ctx.add_init_script(INIT)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(name + ' JS ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(APP); return pg
def login(pg, em, pw):
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); return until(pg, "!!me&&!!document.querySelector('.sb,.pshell')")
LOT = "addLot({lot:'%s',origin:'SCPP Ensenada',tank:'T1',rdate:'2026-11-06',time:'08:00',tempT:58,tempP:'59',kgbox:18,desp:0,k0:%d,k1:%d,k2:0,k3:0});save()"
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        A = device(b, 'A'); T = device(b, 'T')
        chk(login(A, 'admin@propesa.mx', 'clave-admin1') and login(T, 'piso@propesa.mx', 'clave-piso1'), 'entran el Administrador (A) y Piso (T)')

        # ---------- #1 tablet con código viejo: no borra lo que no conoce ----------
        T.evaluate("(f=>{WN.P=p=>{const o=f(p);delete o.ob;return o}})(WN.P)")   # su lista de campos no tiene «ob» (como una versión de antes)
        A.evaluate("ST.P.push({u:uidS(),n:'PVG · PRUEBA',h:2,z:[0,0,0,0],c:[],alive:null,closed:false});save()")
        chk(until(T, "ST.P.length==1"), 'la tablet recibe el embarque')
        A.evaluate("ST.P[0].ob='Hieleras con hielo extra';save()")
        k = 'P/' + A.evaluate("ST.P[0].u")
        chk(until(A, "outN()==0") and recs()[k]['v'].get('ob') == 'Hieleras con hielo extra', 'la versión nueva guarda la observación')
        time.sleep(5); T.evaluate("ST.P[0].alive=1234;save()")
        chk(until(T, "outN()==0", 15), 'la tablet vieja sube las vivas')
        v = recs()[k]['v']
        chk(v.get('alive') == 1234 and v.get('ob') == 'Hieleras con hielo extra', f'en la base quedan las vivas Y la observación (antes se borraba): {v}')
        chk(until(A, "ST.P[0].alive==1234&&ST.P[0].ob=='Hieleras con hielo extra'"), 'la versión nueva ve los dos')

        # ---------- #1 versión nueva publicada: aviso, no sube, recargar sube lo pendiente ----------
        chk(T.evaluate("VER_TAG") is not None, 'la tablet anotó la versión de index.html al entrar')
        T.evaluate("VER_TAG='otra';VER_T=0;syncNow()")
        chk(until(T, "document.body.innerText.toLowerCase().includes('hay una versión nueva de la plataforma')"), 'cambió index.html: barra roja «Hay una versión nueva de la plataforma»')
        chk(T.locator('[data-reload]').count() == 1 and 'Recargar ahora' in T.inner_text('[data-reload]'), 'con botón «Recargar ahora»')
        w0 = mock('/__estado')['writes']; T.evaluate("ST.P[0].alive=1300;save();render()"); time.sleep(5)
        chk(mock('/__estado')['writes'] == w0 and T.evaluate("outN()") >= 1, 'el código viejo ya no sube: el cambio se queda pendiente en el equipo')
        chk('1 cambio pendiente' in T.inner_text('main').lower() or '1 cambio pendiente' in T.inner_text('body').lower(), 'la barra dice cuántos cambios esperan')
        T.click('[data-reload]'); T.wait_for_load_state(); time.sleep(3)
        chk(until(T, "!!me&&outN()==0", 20) and recs()[k]['v'].get('alive') == 1300 and recs()[k]['v'].get('ob') == 'Hieleras con hielo extra', 'al recargar se sube lo pendiente y la observación sigue')
        chk('No se guardó tu cambio' not in T.inner_text('body'), 'sin aviso falso de «otro equipo lo cambió»')
        chk(T.evaluate("!VER_NEW"), 'después de recargar ya no sale el aviso')

        # ---------- #2 la misma hoja capturada en dos equipos ----------
        chk(A.evaluate("newLotId()") != A.evaluate("newLotId()") and A.evaluate("/^R-[0-9a-z]{15}$/.test(newLotId())"), 'id de lote único (uidS), ya no contador')
        T.context.set_offline(True); T.evaluate(LOT % ('WLRSC061126', 100, 200)); time.sleep(0.5)
        A.evaluate(LOT % ('WLRSC061126', 100, 200)); chk(until(A, "outN()==0"), 'la oficina sube su captura')
        T.context.set_offline(False); T.evaluate("dispatchEvent(new Event('online'))")
        chk(until(A, "bal('WLRSC061126')==600000", 15), 'las dos capturas llegan (300 + 300 kg)')
        A.evaluate("go('lote:WLRSC061126')"); t = A.inner_text('#lotav') if A.locator('#lotav').count() else ''
        chk('se capturó 2 veces' in t and '300.0 kg + 300.0 kg' in t, f'aviso rojo en el lote: «se capturó 2 veces… 300.0 kg + 300.0 kg» ({t[:160]})')
        chk(A.locator('#lotav [data-a=el]').count() == 0 and A.locator('#lotav [data-av]').count() == 1, 'sin «Corregir ›» (se arregla revirtiendo); con «Está bien así»')
        A.evaluate("go('recepcion')"); chk('capturada dos veces' in A.inner_text('main'), 'Entrada lo avisa: «WLRSC061126 · capturada dos veces»')
        chk(until(T, "lotWarn(R_('WLRSC061126')).some(x=>x.d)"), 'la tablet también lo ve')
        # revertir la segunda captura quita el aviso
        rc = A.evaluate("R_('WLRSC061126').id")
        A.evaluate(f"ST.L.filter(x=>x.lot=='WLRSC061126'&&x.type=='RECEPCION'&&x.rc!=='{rc}').forEach(x=>post('REVERSA',x.lot,x.size,-x.m/1000,x.id));save()")
        A.evaluate("go('lote:WLRSC061126')")
        chk(A.evaluate("bal('WLRSC061126')") == 300000 and A.locator('#lotav').count() == 0, 'al revertir la captura que sobra: 300 kg y sin aviso')
        # entrada normal: sin aviso (una sola captura, aunque tenga dos tallas)
        A.evaluate(LOT % ('WLRSC061127', 50, 60)); chk(A.evaluate("lotWarn(R_('WLRSC061127')).every(x=>!x.d)"), 'una entrada normal no avisa')

        # ---------- #3 cambio de cuenta con un precio pendiente ----------
        A.context.set_offline(True)
        A.evaluate(LOT % ('WLRSC061128', 0, 250) + ";R_('WLRSC061127').pr={u:31.5,f:'F'};save()")
        chk(A.evaluate("outN()") >= 3, 'el Administrador sin internet: entrada nueva y precio pendientes')
        A.evaluate("signOut()"); A.context.set_offline(False)
        chk(login(A, 'piso@propesa.mx', 'clave-piso1'), 'entra Piso en el mismo equipo')
        chk(until(A, "outN()==1", 15) and 'R/WLRSC061128' in recs(), 'se sube la entrada; solo el precio sigue esperando a un Administrador')
        chk('$/WLRSC061127' not in recs() and 'No tienes permiso' not in A.inner_text('body'), 'el precio no se manda con la cuenta de Piso (la base rechazaba toda la tanda)')
        A.evaluate("signOut()"); chk(login(A, 'admin@propesa.mx', 'clave-admin1'), 'vuelve a entrar el Administrador')
        chk(until(A, "outN()==0", 15) and recs().get('$/WLRSC061127', {}).get('v', {}).get('u') == 31.5, 'y se sube el precio')
        # si la base no deja guardar (403), lo pendiente ya no se borra
        A.route('**/rest/v1/rpc/push', lambda r: r.fulfill(status=403, content_type='application/json', body='{"code":"42501","message":"new row violates row-level security policy"}'))
        A.evaluate("ST.T.push({id:uidN(),t:'2026-11-06T09:00',tank:'T1',a:58,s:null,p:null,by:me.name});save()"); time.sleep(3)
        chk(A.evaluate("outN()") == 1, 'con un 403 el cambio sigue pendiente (antes se borraba todo)')
        chk(until(A, "document.body.innerText.toLowerCase().includes('no se pudo subir')&&!!document.querySelector('[data-sync]')", 10), 'aviso rojo «No se pudo subir…» con «Reintentar ahora»')
        A.unroute('**/rest/v1/rpc/push'); A.click('[data-sync]')
        chk(until(A, "outN()==0", 15), 'al reintentar con permiso, se sube')
        b.close()
finally:
    srv.terminate()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('TODO BIEN' if not fails else f'{len(fails)} FALLAS')
