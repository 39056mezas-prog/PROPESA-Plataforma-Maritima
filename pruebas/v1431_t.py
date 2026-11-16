"""v1.43.1 · Recepción: (1) «Lo que no entra a tinas» debajo de Temperaturas y plegado;
(2) letra del color en el teclado de la recepción (R, V, A, B) como en Empaque;
(3) al escribir los kg, el campo de la tina NO se vuelve a dibujar (antes se perdía lo escrito).
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/v1431_t.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS
def entrar(pg):
    pg.goto(BASE); pg.evaluate(FIX); pg.reload()
    pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(250)
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (390, 1280):
        c = b.new_context(viewport={'width': w, 'height': 900}); pg = c.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg)
        pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.wait_for_timeout(200)
        # (1) orden de secciones y pestaña plegada
        orden = pg.evaluate("[...document.querySelectorAll('#app .rtw h2.h3, #app .rtw summary')].map(h=>h.textContent.trim())")
        i_t = orden.index('Temperaturas') if 'Temperaturas' in orden else -1
        i_l = orden.index('Lo que no entra a tinas') if 'Lo que no entra a tinas' in orden else -1
        chk(i_t >= 0 and i_l > i_t, f'{w}px: «Lo que no entra a tinas» va después de Temperaturas')
        chk(pg.evaluate("document.querySelector('details.rtlno')?.open") is False, f'{w}px: la pestaña sale plegada si no hay kg')
        # (2) letras de color: escribir kg y pulsar la letra (B, R, V, A)
        pg.click('#tn_k1'); pg.keyboard.type('350'); pg.keyboard.press('r')
        chk(pg.evaluate("RT.tn[1].z") == pg.evaluate("S[1]"), f'{w}px: «r» asigna talla Roja a la tina 1')
        chk(pg.evaluate("RT.act") == 2, f'{w}px: tras la letra, pasa a la siguiente tina')
        pg.keyboard.type('12'); pg.keyboard.press('v')
        chk(pg.evaluate("RT.tn[2].z") == pg.evaluate("S[2]"), f'{w}px: «v» asigna talla Verde')
        # (3) escribir no redibuja el campo: el foco y el valor se conservan
        pg.click('#tn_k3'); pg.keyboard.type('3')
        pg.keyboard.type('4.5')
        val = pg.evaluate("document.getElementById('tn_k3').value")
        foco = pg.evaluate("document.activeElement && document.activeElement.id")
        chk(val == '34.5', f'{w}px: los kg escritos se conservan ({val!r})')
        chk(foco == 'tn_k3', f'{w}px: el campo conserva el foco mientras se escribe ({foco!r})')
        # la pestaña se abre sola si ya hay kg de muerta
        pg.evaluate("document.querySelector('details.rtlno').open=true")
        pg.fill('#rt_mu', '21.45')
        chk(pg.evaluate("RT.h.rt_mu") == '21.45', f'{w}px: kg de muerta se guardan en el borrador')
        pg.evaluate("RT.h.rt_mu='21.45';go('recepcion');"); pg.click('[data-a=nf]'); pg.wait_for_timeout(200)
        chk(pg.evaluate("document.querySelector('details.rtlno')?.open") is False, f'{w}px: al volver a abrir sin kg extra, la pestaña queda plegada')

        # (4) calendario: si la página se mueve con el calendario abierto, se cierra (no flota encima)
        pg.evaluate("go('recepcion')"); pg.click('[data-a=nf]'); pg.wait_for_timeout(200)
        pg.click('#rt_fd'); pg.wait_for_timeout(150)
        pg.evaluate("document.querySelector('main').scrollTop+=40"); pg.wait_for_timeout(150)
        chk(pg.evaluate("!document.querySelector('.flatpickr-calendar.open')"), f'{w}px: con scroll corto, el calendario se cierra y no queda flotando')
        pg.evaluate("document.querySelector('main').scrollTop+=900"); pg.wait_for_timeout(150)
        pg.evaluate("document.querySelector('main').scrollTop=0"); pg.wait_for_timeout(150)
        pg.click('#rt_fd'); pg.wait_for_timeout(150)
        chk(pg.evaluate("!!document.querySelector('.flatpickr-calendar.open')"), f'{w}px: tocar la fecha de nuevo lo vuelve a abrir')
        pg.evaluate("document.querySelector('main').scrollTop=0")
        c.close()
    b.close()
print('ERRORES JS:', errs or 'ninguno')
if errs: fails.append('error js')
print('TODO BIEN' if not fails else f'FALLAS: {len(fails)}')
sys.exit(1 if fails else 0)
