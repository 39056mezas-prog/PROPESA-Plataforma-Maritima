"""v1.44.2 · Fase 4: Inventario en el menú (todos los roles). Disponible por talla y por tanque, T1…T6.
Uso: servidor en la carpeta (python3 -m http.server 8765) y luego python3 -I pruebas/v1444_t.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Pedro Piso',email:'piso@propesa.mx',role:'piso',notify:false}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (390, 1280):
        for mail, rol in (('admin@propesa.mx', 'admin'), ('piso@propesa.mx', 'piso')):
            c = b.new_context(viewport={'width': w, 'height': 900}); pg = c.new_page()
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(BASE); pg.evaluate(FIX); pg.reload()
            pg.fill('#le', mail); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(300)
            tag = f'{w}px {rol}'
            if pg.evaluate("PISO"):
                pg.evaluate("PISO=false;render()"); pg.wait_for_timeout(200)
            chk(pg.locator('.sb button.fs[data-go=inventario]').count() == 1, f'{tag}: «Inventario» está en el menú, en Control')
            pg.evaluate("go('inventario')"); pg.wait_for_timeout(200)
            t = pg.inner_text('main')
            chk('Inventario' in t and 'Total disponible' in t, f'{tag}: la pantalla Inventario abre con su total')
            heads = pg.evaluate("[...document.querySelectorAll('main table thead th')].map(th=>th.textContent.trim())")
            chk(heads[2:] == ['T1','T2','T3','T4','T5','T6'], f'{tag}: una columna por tanque, T1…T6 ({heads[2:]})')
            chk(pg.evaluate("document.querySelectorAll('main table tbody tr').length") == len(['x']*0) + pg.evaluate("S.length"), f'{tag}: una fila por talla')
            if rol == 'piso':
                chk(pg.locator('.sb button.fs[data-go=inventario]').count() == 1, f'{tag}: piso también lo ve')
            c.close()
    b.close()
print('ERRORES JS:', errs or 'ninguno')
if errs: fails.append('error js')
print('TODO BIEN' if not fails else f'FALLAS: {len(fails)}')
sys.exit(1 if fails else 0)
