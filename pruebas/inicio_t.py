"""Primer uso, sin rastros de demo, temperatura y borrado de datos. Uso: python3 -I pruebas/inicio_t.py"""
import os,sys,re
from playwright.sync_api import sync_playwright
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local');fails=[];errs=[]  # modo local: nunca toca la base real
def chk(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
DEMO=re.compile(r'demo|simulad|sistema real|admin123|piso123|Ana Torres|Luis Meza|Q-22|provisional',re.I)
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':860});pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept('BORRAR') if d.type=='prompt' else d.accept())
    pg.goto(BASE);pg.evaluate('localStorage.clear()');pg.reload()
    chk(pg.locator('#s0n').count()==1 and 'Configuración inicial' in pg.inner_text('#app'),'equipo nuevo: pide crear el Administrador (sin usuarios de demostración)')
    chk(not DEMO.search(pg.inner_text('body')),'pantalla inicial sin textos de demostración')
    pg.click('[data-a=s0]');chk('nombre' in pg.inner_text('#lm'),'valida el nombre')
    pg.fill('#s0n','María López');pg.fill('#s0e','maria@propesa.com.mx');pg.fill('#s0p','corto');pg.click('[data-a=s0]');chk('8 caracteres' in pg.inner_text('#lm'),'pide contraseña de 8+ (auditoría #20)')
    pg.fill('#s0p','Langosta2026');pg.fill('#s0q','otra');pg.click('[data-a=s0]');chk('coinciden' in pg.inner_text('#lm'),'valida que coincidan')
    pg.fill('#s0q','Langosta2026');pg.press('#s0q','Enter');chk(pg.locator('.sb').count()==1,'crea el Administrador y entra')
    chk(pg.locator('#app [data-avatar]').inner_text().strip()=='M','el círculo muestra su inicial')
    st=pg.evaluate("JSON.parse(localStorage.getItem('propesa-v4')).U");chk(len(st)==1 and st[0]['role']=='admin' and 'pw' not in st[0] and 'pwh' not in st[0],'un solo usuario, Administrador, sin contraseña guardada en el equipo')
    chk('contraseña de prueba' not in pg.inner_text('#app').lower(),'sin aviso de contraseña de prueba')
    seen=[]
    for r in ['inicio','recepcion','ordenes','empaque','embarques','cierre','temperatura','admin']:
        pg.evaluate(f"go('{r}')");tx=pg.inner_text('#app')
        if DEMO.search(tx):seen.append((r,DEMO.search(tx).group(0)))
    pg.locator('#app [data-avatar]').click();tx=pg.inner_text('#pmenu');pg.keyboard.press('Escape')
    chk(not seen,f'ninguna pantalla muestra rastros de demo {seen}');chk('Versión 1.10.1' in tx,'el menú de perfil muestra la versión 1.10.1')
    # temperatura real
    pg.evaluate("go('temperatura')");chk('Todavía no hay lecturas' in pg.inner_text('#app'),'temperatura empieza vacía (sin datos inventados)')
    pg.select_option('#tq_t','T2');pg.fill('#tq_a','150');pg.click('[data-a=tq]');chk('20 y 110' in pg.inner_text('#app'),'valida el rango de temperatura')
    pg.fill('#tq_a','54.3');pg.fill('#tq_p','58');pg.click('[data-a=tq]')
    t=pg.evaluate("ST.T");chk(len(t)==1 and t[0]['tank']=='T2' and t[0]['a']==54.3 and t[0]['p']==58 and t[0]['s'] is None and t[0]['by']=='María López','lectura guardada con tanque, valores y quién la capturó')
    chk('54.3 °F' in pg.inner_text('#app'),'la lectura aparece en la tabla')
    pg.click('[data-tqdel]');chk(pg.evaluate("ST.T.length")==0,'el Administrador puede eliminar una lectura')
    # informe de cierre: sin "simulado"
    pg.evaluate("go('admin')");chk('Informes de cierre' in pg.inner_text('#app'),'Administración muestra Informes de cierre')
    # v1.10.1: «Borrar todos los datos» regresa, escondido: solo en Administración, dentro de «Configuración avanzada» cerrada
    chk(pg.locator('details#adv:not([open])').count()==1 and not pg.locator('[data-a=rst]').is_visible(),'«Borrar todos los datos» está escondido en «Configuración avanzada» (cerrada)')
    pg.click('#adv summary');chk(pg.locator('[data-a=rst]').is_disabled(),'sin respaldo reciente no se puede borrar')
    pg.evaluate("BK_T=Date.now();render()");pg.fill('#rst_t','borrar');pg.click('[data-a=rst]');n1=pg.evaluate("JSON.stringify([ST.R,ST.OR,ST.T])");chk('BORRAR TODO' in pg.inner_text('#rst_m') and pg.evaluate("!!me"),'sin escribir BORRAR TODO no borra nada')
    n0=pg.evaluate("JSON.stringify([ST.R,ST.OR,ST.T,ST.U.length])")
    with pg.expect_download():pg.click('[data-bk=dl]')
    chk(pg.evaluate("JSON.stringify([ST.R,ST.OR,ST.T,ST.U.length])")==n0 and pg.locator('#s0n').count()==0,'descargar el respaldo sigue funcionando y no borra nada')
    pg.close()
    # equipo con datos anteriores: conserva sus usuarios
    pg=b.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE);pg.evaluate("localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,U:[{id:7,name:'Jefe de planta',email:'jefe@x.mx',pw:'Clave123',role:'admin',notify:true}]}))");pg.reload()
    chk(pg.locator('#le').count()==1,'equipo que ya tenía usuarios: pide iniciar sesión, no configuración inicial')
    pg.fill('#le','jefe@x.mx');pg.fill('#lp','Clave123');pg.click('[data-a=lg]');chk(pg.locator('.sb').count()==1,'sus usuarios siguen funcionando')
    b.close()
print('ERRS',errs);print('RESULTADO:','TODO BIEN' if not fails and not errs else f'{len(fails)} fallas');sys.exit(1 if fails or errs else 0)
