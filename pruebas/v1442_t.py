"""v1.44.2 · Fase 2 del Centro de operaciones: la planta 3D es lo primero al entrar (Centro y Modo piso).
Uso: servidor en la carpeta (python3 -m http.server 8765) y luego python3 -I pruebas/v1442_t.py"""
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
ORDEN = "(a,b)=>!!(document.querySelector(a)&&document.querySelector(b)&&(document.querySelector(a).compareDocumentPosition(document.querySelector(b))&Node.DOCUMENT_POSITION_FOLLOWING))"
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (390, 1280):
        for mail, rol in (('admin@propesa.mx', 'admin'), ('piso@propesa.mx', 'piso')):
            c = b.new_context(viewport={'width': w, 'height': 900}); pg = c.new_page()
            pg.on('pageerror', lambda e: errs.append(str(e)))
            entrar(pg, mail); pg.wait_for_timeout(200)
            tag = f'{w}px {rol}'
            if rol == 'admin':
                pg.evaluate("PISO=false;go('inicio');render()"); pg.wait_for_timeout(200)
                chk(pg.evaluate(ORDEN.replace('(a,b)','("#app .ct3top .t3v","#app .ctg4")') if False else "(()=>{const a=document.querySelector('.ct3top .t3v'),b=document.querySelector('.ctg4');return !!a&&!!b&&!!(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING)})()"), f'{tag}: en el Centro, la planta 3D va antes que los números')
                chk(pg.evaluate("(()=>{const a=document.querySelector('.ct3top .t3v');if(!a)return false;const r=a.getBoundingClientRect();return r.height>=200})()"), f'{tag}: la planta 3D mide al menos 200 px de alto')
            else:
                pg.evaluate("PISO=true;go('piso');render()"); pg.wait_for_timeout(200)
                chk(pg.evaluate("(()=>{const a=document.querySelector('.ct3top .t3v'),b=document.querySelector('.ph');return !!a&&!!b&&!!(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING)})()"), f'{tag}: en Modo piso, la planta 3D va antes de «¿Qué vas a hacer?»')
            chk(pg.evaluate("!!document.querySelector('.ct3top .t3v') && (document.querySelector('.ct3top .t3v').getBoundingClientRect().width>0)"), f'{tag}: la planta 3D se ve en pantalla')
            c.close()
    b.close()
print('ERRORES JS:', errs or 'ninguno')
if errs: fails.append('error js')
print('TODO BIEN' if not fails else f'FALLAS: {len(fails)}')
sys.exit(1 if fails else 0)
