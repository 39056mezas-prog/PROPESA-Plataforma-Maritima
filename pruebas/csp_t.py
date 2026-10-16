"""Aplica las cabeceras de seguridad de vercel.json (CSP incluida) y recorre la app buscando bloqueos. Uso: python3 -I pruebas/csp_t.py"""
import os,json,base64
from playwright.sync_api import sync_playwright
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local');fails=[];errs=[]  # modo local: nunca toca la base real
def chk(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
H={h['key']:h['value'] for h in json.load(open(os.path.join(ROOT,'vercel.json')))['headers'][0]['headers']}
chk('Content-Security-Policy' in H and "object-src 'none'" in H['Content-Security-Policy'],'vercel.json define una CSP estricta')
for k in ['Strict-Transport-Security','Permissions-Policy','X-Content-Type-Options','Referrer-Policy']:chk(k in H,f'vercel.json define {k}')
H.pop('Strict-Transport-Security');H.pop('Content-Security-Policy');CSP=json.load(open(os.path.join(ROOT,'vercel.json')))['headers'][0]['headers'][0]['value'].replace('; upgrade-insecure-requests','')
PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':1280,'height':860},accept_downloads=True)
    def route(r):
        resp=r.fetch();hd=dict(resp.headers);hd.update(H);hd['content-security-policy']=CSP;r.fulfill(response=resp,headers=hd)
    ctx.route('**/*',route)
    pg=ctx.new_page();viol=[]
    pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    pg.on('console',lambda m:viol.append(m.text) if 'Content Security Policy' in m.text else None)
    pg.add_init_script("document.addEventListener('securitypolicyviolation',e=>{(window.__v=window.__v||[]).push(e.violatedDirective+' '+e.blockedURI)})")
    pg.goto(BASE);pg.evaluate('localStorage.clear()');pg.reload()
    chk(pg.locator('#s0n').count()==1,'con la CSP activa abre la configuración inicial')
    pg.fill('#s0n','Admin Prueba');pg.fill('#s0e','admin@empresa.mx');pg.fill('#s0p','Segura2026');pg.fill('#s0q','Segura2026');pg.click('[data-a=s0]')
    chk(pg.locator('.sb').count()==1,'crea Administrador y entra con la CSP activa')
    for r in ['inicio','recepcion','ordenes','empaque','embarques','cierre','temperatura','admin','buscar']:pg.evaluate(f"go('{r}')")
    pg.evaluate("go('temperatura')");f=pg.locator('input[type=file][accept^="image"]').first
    if f.count():f.set_input_files(files=[{'name':'f.png','mimeType':'image/png','buffer':PNG}]);pg.wait_for_timeout(400)
    chk(pg.locator('#app img[src^="data:image"]').count()>=1,'las fotos de evidencia se ven (img data:)')
    pg.evaluate("go('admin')");pg.locator('input[data-bk=up]').first.set_input_files(os.path.join(ROOT,'pruebas','datos','backup.json'));pg.wait_for_timeout(500)
    if pg.locator('#le').count():pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.press('#lp','Enter')
    chk(pg.evaluate('ST.R.length')>=1 and pg.locator('.sb').count()==1,'restaurar un respaldo funciona con la CSP')
    pg.evaluate("go('recepcion')");btn=pg.locator('[data-pdf^="dl:"]').first
    with pg.expect_download() as d:btn.click()
    chk(d.value.suggested_filename.endswith('.pdf'),'la descarga de PDF funciona con la CSP')
    pg.evaluate("go('admin')");bk=pg.locator('[data-bk=dl],[data-a=bk]').first
    if bk.count():
        with pg.expect_download() as d2:bk.click()
        chk(d2.value.suggested_filename.endswith('.json'),'la descarga del respaldo funciona con la CSP')
    pg.locator('#app [data-avatar]').click();pg.keyboard.press('Escape')
    pg.locator('[data-settings]:visible').first.click();pg.keyboard.press('Escape')
    v=(pg.evaluate('window.__v||[]') or [])+viol
    chk(not v,f'ninguna violación de la CSP {v[:5]}')
    print('ERRS',errs);chk(not errs,'sin errores de JavaScript')
    b.close()
print('RESULTADO:',len(fails),'fallas')
