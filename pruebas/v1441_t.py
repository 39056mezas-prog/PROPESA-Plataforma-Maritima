"""v1.44.1 · Fase 1 del Centro de operaciones: menú en tres grupos (General · Operación · Control).
Control = Temperatura, Mortalidad final, Hojas para imprimir y, solo para el Administrador, Administración.
Uso: servidor en la carpeta (python3 -m http.server 8765) y luego python3 -I pruebas/v1441_t.py"""
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
def entrar(pg, mail):
    pg.goto(BASE); pg.evaluate(FIX); pg.reload()
    pg.fill('#le', mail); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(300)
GROUPS = "[...document.querySelectorAll('.sb h4')].map(h=>h.textContent.trim())"
ITEMS = "(g)=>{const h=[...document.querySelectorAll('.sb h4')].find(x=>x.textContent.trim()==g);const out=[];let e=h&&h.nextElementSibling;while(e&&e.tagName!=='H4'){if(e.matches('button.fs'))out.push(e.querySelector('b').textContent.trim());e=e.nextElementSibling}return out}"
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (390, 1280):
        for mail, rol in (('admin@propesa.mx', 'admin'), ('piso@propesa.mx', 'piso')):
            c = b.new_context(viewport={'width': w, 'height': 900}); pg = c.new_page()
            pg.on('pageerror', lambda e: errs.append(str(e)))
            entrar(pg, mail)
            if pg.evaluate("PISO"):
                pg.evaluate("PISO=false;render()"); pg.wait_for_timeout(300)  # vista completa, para ver el menú del rol
            pg.evaluate("go('inicio')"); pg.wait_for_timeout(150)
            tag = f'{w}px {rol}'
            g = pg.evaluate(GROUPS)
            chk(g[:3] == ['General', 'Operación', 'Control'], f'{tag}: grupos en orden General · Operación · Control ({g})')
            op = pg.evaluate(f"({ITEMS})('Operación')")
            chk(op == ['Recepción', 'Órdenes', 'Empaque', 'Embarque'], f'{tag}: Operación = Recepción, Órdenes, Empaque, Embarque ({op})')
            ctl = pg.evaluate(f"({ITEMS})('Control')")
            esperado = ['Temperatura', 'Inventario', 'Mortalidad final', 'Hojas para imprimir'] + (['Administración'] if rol == 'admin' else [])  # v1.44.2: Inventario en Control
            chk(ctl == esperado, f'{tag}: Control = {esperado} ({ctl})')
            chk(pg.evaluate("document.querySelector('.sb button.fs[data-go=inicio]').textContent.includes('Centro de operaciones')"), f'{tag}: Centro de operaciones arriba')
            if rol == 'admin':
                pg.evaluate("document.querySelector('.sb [data-go=admin]').click()"); pg.wait_for_timeout(200)
                chk(pg.evaluate("V.v") == 'admin', f'{tag}: Administración abre su pantalla')
            c.close()
    b.close()
print('ERRORES JS:', errs or 'ninguno')
if errs: fails.append('error js')
print('TODO BIEN' if not fails else f'FALLAS: {len(fails)}')
sys.exit(1 if fails else 0)
