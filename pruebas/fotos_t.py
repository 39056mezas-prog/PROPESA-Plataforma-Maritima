"""Fotos en el espacio de archivos de Supabase (v1.8.0).
Las notas guardan solo la referencia «sb:notas/<nota>/<n>.jpg»; la foto se sube al espacio «fotos» antes que la nota,
sin internet espera en el equipo, los demás equipos la bajan con su sesión y la guardan para verla sin internet.
Usa un Supabase de mentira propio (pruebas/supabase_falso.py en el puerto 8791) y varios navegadores a la vez.
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/fotos_t.py"""
import os, sys, json, time, struct, zlib, subprocess, urllib.request
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.environ.get('APP', 'http://localhost:8765/index.html')   # sin ?modo=local: usa la base compartida (la de mentira)
MOCK = 'http://127.0.0.1:8791'
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def mock(path, post=False):
    r = urllib.request.urlopen(urllib.request.Request(MOCK + path, data=b'{}' if post else None, method='POST' if post else 'GET'))
    return json.loads(r.read() or b'null')
def png(w, h, rgb):
    raw = b''.join(b'\x00' + bytes(rgb) * w for _ in range(h))
    ch = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw)) + ch(b'IEND', b'')
FOTO = png(64, 48, (200, 40, 40))

srv = subprocess.Popen([sys.executable, '-I', os.path.join(ROOT, 'pruebas', 'supabase_falso.py'), '8791'])
for _ in range(50):
    try: mock('/__reset', True); break
    except Exception: time.sleep(0.1)

INIT = "window.PROPESA_SB={url:'%s',key:'clave-publica-de-prueba'};" % MOCK
def until(pg, js, t=15):
    end = time.time() + t
    while time.time() < end:
        try:
            if pg.evaluate(js): return True
        except Exception: pass
        time.sleep(0.25)
    return False
def device(b, name):
    ctx = b.new_context(viewport={'width': 1180, 'height': 820}); ctx.add_init_script(INIT)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(name + ' JS ' + str(e)))
    pg.on('dialog', lambda d: d.accept('BORRAR') if d.type == 'prompt' else d.accept())
    pg.goto(APP); return ctx, pg
def login(pg, em, pw):
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]')
    return until(pg, "!!me&&!!document.querySelector('.sb,.pshell')")
def nota(pg, texto, fotos=1):
    """Nota con foto en Entrada (vista completa)."""
    pg.evaluate("setPiso(false);go('recepcion')"); pg.wait_for_timeout(100)
    pg.locator('input[type=file][data-k="recepcion"]').nth(1).set_input_files(files=[{'name': f'f{i}.png', 'mimeType': 'image/png', 'buffer': FOTO} for i in range(fotos)])
    until(pg, f"(ND&&ND.imgs.length)=={fotos}")
    pg.fill('#ntx', texto); pg.click('button[data-ev="save:recepcion"]'); pg.wait_for_timeout(100)
    return pg.evaluate(f"(ST.M.recepcion||[]).find(n=>n.text=={json.dumps(texto)})")
def wait(fn, t=15):
    end = time.time() + t
    while time.time() < end:
        try:
            if fn(): return True
        except Exception: pass
        time.sleep(0.25)
    return False
def rec(nid):
    r = mock('/__estado')['recs'].get(f'M/{nid}'); return r and r['v']
REF = r"/^sb:notas\/\d+\/[0-5]\.jpg$/"

try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ca, A = device(b, 'A'); chk(login(A, 'admin@propesa.mx', 'clave-admin1'), 'A (Administrador) entra')
        cb, B = device(b, 'B'); chk(login(B, 'piso@propesa.mx', 'clave-piso1'), 'B (Encargado de piso) entra')

        # --- 1. nota con 2 fotos: la nota solo lleva referencias; las fotos van al espacio de archivos
        n1 = nota(A, 'tanque 3 con espuma', 2)
        chk(n1 and len(n1['imgs']) == 2 and A.evaluate(f"(ST.M.recepcion[0].imgs).every(m=>{REF}.test(m))"), f"la nota guarda referencias, no la foto: {n1 and n1['imgs']}")
        chk(until(A, "outN()==0"), 'las fotos y la nota se suben')
        st = mock('/__estado'); paths = [m[3:] for m in n1['imgs']]
        chk(all(st['files'].get(x, 0) > 200 for x in paths), f'las 2 fotos están en el espacio de archivos: {st["files"]}')
        v = rec(n1['id']); chk(v and v['imgs'] == n1['imgs'], 'el registro de la nota en la base trae las mismas referencias')
        chk('data:image' not in json.dumps(st['recs']), 'ningún registro de la base trae fotos dentro (antes cada foto pesaba ~120 mil letras)')
        chk(until(A, "[...document.querySelectorAll('img[data-fp]')].length==2&&[...document.querySelectorAll('img[data-fp]')].every(i=>i.src.startsWith('data:image/jpeg'))"), 'en A se ven las 2 fotos (desde la cola, sin bajarlas)')

        # --- 2. otro equipo baja la foto con su sesión
        g0 = mock('/__estado')['file_gets']; B.evaluate("setPiso(false);go('recepcion')")
        chk(until(B, "[...document.querySelectorAll('img[data-fp]')].length==2&&[...document.querySelectorAll('img[data-fp]')].every(i=>i.src.startsWith('data:image/jpeg'))"), 'en B se ven las 2 fotos (bajadas del espacio de archivos)')
        chk(mock('/__estado')['file_gets'] - g0 == 2, 'B bajó cada foto una sola vez')
        # se guardan en el equipo: con el espacio de archivos caído, se siguen viendo después de recargar
        B.route('**/storage/v1/object/authenticated/**', lambda r: r.abort())
        B.reload(); chk(until(B, "!!me") and B.evaluate("setPiso(false);go('recepcion');1") and until(B, "[...document.querySelectorAll('img[data-fp]')].filter(i=>i.src.startsWith('data:image/jpeg')).length==2"), 'B recarga sin poder bajar fotos y las sigue viendo (copia del equipo)')
        B.unroute('**/storage/v1/object/authenticated/**')
        B.locator('img[data-fp]').first.click(); chk(B.locator('.lbx img').count() == 1, 'tocar la foto la abre en grande'); B.locator('.lbx').click()

        # --- 3. sin internet: la foto espera en el equipo y se sube antes que la nota
        corta = lambda r: r.abort('internetdisconnected')   # sin internet hacia la base (la página sí carga, como en la tablet)
        B.route(MOCK + '/**', corta); n2 = nota(B, 'caja 12 golpeada')
        chk(until(B, "outN()==2"), 'sin internet: quedan 2 pendientes (la nota y su foto)')
        chk(n2['imgs'][0][3:] not in mock('/__estado')['files'] and B.evaluate("document.querySelector('img[data-fp]').src.startsWith('data:image/jpeg')"), 'la foto todavía no está arriba, pero en B se ve')
        chk(B.evaluate("idbGet('fotos-cola').then(o=>Object.keys(o||{}).length)") == 1, 'la foto pendiente se guarda en la memoria del equipo (cola)')
        B.reload(); chk(until(B, "!!me&&FQ.size==1&&outN()==2"), 'recargar sin internet no pierde la foto pendiente')
        B.unroute(MOCK + '/**', corta); B.evaluate("window.dispatchEvent(new Event('online'))")
        chk(until(B, "outN()==0", 20), 'regresa el internet: se sube todo')
        lg = mock('/__estado')['log']; fa, re_ = 'archivo ' + n2['imgs'][0][3:], f"registro M/{n2['id']}"
        chk(fa in lg and re_ in lg and lg.index(fa) < lg.index(re_), 'en la base, la foto quedó guardada antes que la nota que la nombra')
        chk(n2['imgs'][0][3:] in mock('/__estado')['files'] and rec(n2['id'])['imgs'] == n2['imgs'], 'la foto y la nota quedaron arriba')
        A.evaluate("go('recepcion')"); chk(until(A, f"!!document.querySelector('img[data-fp=\"{n2['imgs'][0][3:]}\"]')&&document.querySelector('img[data-fp=\"{n2['imgs'][0][3:]}\"]').src.startsWith('data:image/jpeg')", 20), 'A ve la foto que B tomó sin internet')

        # --- 4. Consulta ve las fotos (no puede agregar notas)
        cc, C = device(b, 'C'); chk(login(C, 'consulta@propesa.mx', 'clave-ver1'), 'Consulta entra')
        C.evaluate("go('recepcion')"); chk(until(C, "[...document.querySelectorAll('img[data-fp]')].length==3&&[...document.querySelectorAll('img[data-fp]')].every(i=>i.src.startsWith('data:image/jpeg'))"), 'Consulta ve las 3 fotos')
        chk(C.locator('button[data-ev^="save:"]').count() == 0, 'Consulta no puede agregar notas'); cc.close()

        # --- 5. foto que todavía viene dentro de una nota (respaldo viejo): se pasa sola al espacio de archivos
        A.evaluate("(()=>{const d=FC.get(ST.M.recepcion.find(n=>n.text=='tanque 3 con espuma').imgs[0].slice(3));ST.M.temp=[{id:uidN(),t:now(),by:'Ana Torres',text:'foto vieja',ref:'',imgs:[d]}];save()})()")
        chk(until(A, "outN()==0&&ST.M.temp[0].imgs.every(m=>/^sb:/.test(m))"), 'la foto vieja se pasa al espacio de archivos y la nota queda con la referencia')
        nv = A.evaluate("ST.M.temp[0]"); chk(nv['imgs'][0][3:] in mock('/__estado')['files'] and rec(nv['id'])['imgs'] == nv['imgs'], 'arriba: el archivo y la nota sin la foto dentro')

        # --- 6. el espacio de archivos falla: la foto espera y la nota sí se sube; al volver, se sube sola
        mock('/__falla_fotos', True); n3 = nota(A, 'falla storage')
        chk(until(A, f"outN()==1&&!!SYNC_ERR") and rec(n3['id']) is not None, 'con el espacio de archivos caído la nota se sube y la foto queda pendiente (aviso)')
        chk(n3['imgs'][0][3:] not in mock('/__estado')['files'], 'la foto todavía no está arriba')
        mock('/__falla_fotos', True); chk(until(A, "outN()==0&&!SYNC_ERR", 20) and n3['imgs'][0][3:] in mock('/__estado')['files'], 'al volver el espacio de archivos, la foto se sube sola')

        # --- 7. la base rechaza una foto: se quita de su nota y se avisa (no se queda pendiente para siempre)
        A.route('**/storage/v1/object/fotos/**', lambda r: r.fulfill(status=400, content_type='application/json', body='{"statusCode":"403","error":"Unauthorized","message":"new row violates row-level security policy"}'))
        n4 = nota(A, 'rechazada')
        chk(until(A, "outN()==0&&ST.M.recepcion.find(n=>n.text=='rechazada').imgs.length==0") and 'No se pudo subir una foto' in A.inner_text('#toast'), 'foto rechazada: se quita de la nota y se avisa')
        chk(wait(lambda: rec(n4['id'])['imgs'] == []), 'la nota arriba queda sin esa foto')
        A.unroute('**/storage/v1/object/fotos/**')

        # --- 8. eliminar una nota borra sus fotos del espacio de archivos
        A.evaluate("go('recepcion')"); n1p = paths[:]
        A.click(f'button[data-ev="del:{n1["id"]}"]'); A.click(f'button[data-ev="rm:{n1["id"]}"]')
        chk(until(A, "outN()==0") and wait(lambda: not any(x in mock('/__estado')['files'] for x in n1p)), 'eliminar la nota borra sus 2 fotos del espacio de archivos')

        # --- 9. modo local (pruebas, sin base): las fotos siguen dentro de la nota
        cl = b.new_context(); L = cl.new_page(); L.goto(APP + '?modo=local'); chk(not L.evaluate("CLOUD"), 'modo local: sin base compartida'); cl.close()

        # --- 10. borrar todos los datos también borra las fotos
        A.evaluate("go('admin')"); A.click('[data-a=rst]')
        chk(until(A, "Object.keys(ST.M).length==0") and wait(lambda: not mock('/__estado')['files']), f"Borrar todos los datos deja vacío el espacio de archivos: {mock('/__estado')['files']}")
        b.close()
finally:
    srv.terminate()

chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
