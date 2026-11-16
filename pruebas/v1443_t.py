"""v1.44.2 · Fase 3: ficha de tanque con «Necesita atención» (lote vencido o en su último día, temperatura fuera de rango).
Uso: servidor en la carpeta (python3 -m http.server 8765) y luego python3 -I pruebas/v1443_t.py"""
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
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (390, 1280):
        c = b.new_context(viewport={'width': w, 'height': 900}); pg = c.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE); pg.evaluate(FIX); pg.reload()
        pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(300)
        pg.evaluate("PISO=false;go('inicio');render()"); pg.wait_for_timeout(200)
        tag = f'{w}px'
        # temperatura fuera de rango → aviso en la ficha
        chk(pg.evaluate("tqAlerts('T1',[],{p:99,a:57,s:57}).some(x=>x.t.includes('producto 99 °F'))"), f'{tag}: temperatura del producto de 99 °F sale como aviso')
        chk(pg.evaluate("tqAlerts('T1',[],{p:99}).every(x=>x.go==='temperatura:T1')"), f'{tag}: el aviso de temperatura lleva a Temperatura del tanque')
        chk(pg.evaluate("tqAlerts('T1',[],{p:60,a:58,s:58}).length==0"), f'{tag}: temperaturas normales no generan avisos')
        chk(pg.evaluate("tqAlHtml('T1',[],{p:99}).includes('Necesita atención')"), f'{tag}: el bloque se titula «Necesita atención»')
        chk(pg.evaluate("tqAlHtml('T1',[],{p:60}) === ''"), f'{tag}: sin avisos no se dibuja el bloque')
        # campana: temperatura fuera de rango por tanque
        pg.evaluate("ST.T=[{id:'tq1',t:dLoc()+'T10:00',tank:'T2',a:99,s:null,p:null,by:''}]")
        chk(pg.evaluate("ntFalta().some(x=>x.go==='temperatura:T2' && /Temperatura fuera de rango/.test(x.ti))"), f'{tag}: la campana avisa de temperatura fuera de rango en el tanque 2')
        pg.evaluate("ST.T=[{id:'tq2',t:dLoc()+'T10:00',tank:'T2',a:58,s:null,p:null,by:''}]")
        chk(pg.evaluate("!ntFalta().some(x=>x.go==='temperatura:T2')"), f'{tag}: con temperatura normal, la campana no avisa')
        c.close()
    b.close()
print('ERRORES JS:', errs or 'ninguno')
if errs: fails.append('error js')
print('TODO BIEN' if not fails else f'FALLAS: {len(fails)}')
sys.exit(1 if fails else 0)
