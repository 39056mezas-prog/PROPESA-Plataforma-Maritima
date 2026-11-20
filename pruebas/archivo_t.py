# v1.55.1 · Abrir el .html con doble clic (file://) = copia de prueba en modo local: pide crear el Administrador, guarda solo en ese navegador, nunca toca la base real.
# Correr: python3 -I pruebas/archivo_t.py → «TODO BIEN».
import sys
from playwright.sync_api import sync_playwright
import os;url="file://"+os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"index.html")
bad=[]
def ok(c,t):
    print(('  ✔ ' if c else '  ✘ ')+t)
    if not c: bad.append(t)
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(viewport={'width':1280,'height':800});pg=ctx.new_page();errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(url);pg.wait_for_timeout(1200)
    ok(pg.evaluate('LOCAL&&FILEMODE&&!CLOUD'),'Abierto como archivo = modo local')
    pg.wait_for_timeout(300)
    ok(pg.locator('#s0n').count()==1,'Pide la Configuración inicial')
    ok('Copia de prueba' in pg.locator('body').inner_text(),'Dice que es copia de prueba')
    pg.screenshot(path='/tmp/archivo_file_setup.png')
    pg.fill('#s0n','Prueba');pg.fill('#s0e','prueba@propesa.org')
    pw=pg.locator('input[type=password]')
    for i in range(pw.count()): pw.nth(i).fill('Langosta-2026!')
    pg.locator('button.btn').filter(has_text='Crear').first.click();pg.wait_for_timeout(1000)
    ok(pg.evaluate('!!me'),'Crea el Administrador y entra')
    ok(pg.locator('.fmb').count()==1,'Aviso «Copia de prueba» arriba')
    pg.screenshot(path='/tmp/archivo_file_in.png')
    pg.evaluate("go('recepcion')");pg.wait_for_timeout(300)
    pg.reload();pg.wait_for_timeout(1200)
    ok(pg.evaluate('!!me') or pg.locator('#s0n').count()==0,'Al recargar no vuelve a pedir la configuración inicial')
    ok(not errs,'Sin errores JS '+';'.join(errs))
print('TODO BIEN' if not bad else 'FALLAS');sys.exit(1 if bad else 0)
