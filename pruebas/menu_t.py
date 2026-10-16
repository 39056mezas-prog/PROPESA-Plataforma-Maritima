"""Menú de perfil. Uso: python3 -I pruebas/menu_t.py (con python3 -m http.server 8765 corriendo)"""
import os,sys
from playwright.sync_api import sync_playwright
FIX="localStorage.clear();localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',pw:'admin123',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',pw:'piso123',role:'piso',notify:true},{id:3,name:'Dirección',email:'consulta@propesa.mx',pw:'ver123',role:'consulta',notify:false}]}))"  # usuarios SOLO para pruebas

BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local');fails=[];errs=[]  # modo local: nunca toca la base real
def chk(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw,sch in [((1440,900),'dark'),((390,844),'light')]:
        pg=b.new_page(viewport={'width':vw[0],'height':vw[1]},color_scheme=sch);pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(BASE);pg.evaluate(FIX);pg.reload()
        pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
        hd=pg.inner_text('.hd')
        chk('Administrador' not in hd and 'Salir' not in hd and pg.locator('#app [data-settings]').is_visible(),f'{vw[0]}px: la barra tiene Ajustes y el círculo; ya no rol ni Salir')
        av=pg.locator('#app [data-avatar]');chk(av.inner_text().strip()=='A','el círculo muestra la inicial del usuario (A de Ana Torres)')
        av.click();chk(pg.locator('#pmenu .pmbox').is_visible() and av.get_attribute('aria-expanded')=='true','tocar el círculo abre el menú')
        chk(pg.evaluate("document.activeElement.dataset.pm")=='users','el foco pasa a la primera opción')
        items=pg.locator('#pmenu [role=menuitem]').all_inner_texts();chk(any('Administración' in x for x in items) and not any('Ajustes' in x for x in items) and any('Cerrar sesión' in x for x in items),'opciones: Administración y Cerrar sesión (Ajustes se queda en la barra)')
        txt=pg.inner_text('#pmenu');chk('Ana Torres' in txt and 'admin@propesa.mx' in txt and 'Administrador' in txt,'el menú muestra nombre, correo y rol')
        pg.keyboard.press('ArrowDown');chk(pg.evaluate("document.activeElement.dataset.pm")=='logout','flecha abajo mueve entre opciones')
        bb=pg.locator('#pmenu .pmbox').bounding_box();chk(bb['x']>=0 and bb['x']+bb['width']<=vw[0]+1,'el menú cabe en la pantalla')
        pg.keyboard.press('Escape');chk(not pg.locator('#pmenu .pmbox').count() and pg.evaluate("!!document.activeElement.closest('[data-avatar]')"),'Esc cierra y regresa el foco al círculo')
        av.click();pg.mouse.click(vw[0]//2,vw[1]-20);chk(not pg.locator('#pmenu .pmbox').count(),'tocar fuera cierra')
        av.click();pg.click('[data-pm=users]');chk(pg.evaluate('V.v')=='admin' and 'Usuarios' in pg.inner_text('#app'),'Administración abre la pantalla de usuarios')
        pg.locator('#app [data-settings]').click();chk(pg.locator('#setp .setpanel').is_visible(),'el botón Ajustes de la barra abre Configuración');pg.keyboard.press('Escape')
        pg.evaluate("go('recepcion')");pg.click('[data-a=nf]');pg.fill('#fo','escrito')
        pg.locator('#app [data-avatar]').click();pg.keyboard.press('Escape');chk(pg.input_value('#fo')=='escrito','abrir el menú no borra lo capturado')
        pg.screenshot(path='/tmp/propesa-menu.png') if False else None
        pg.locator('#app [data-avatar]').click();pg.click('[data-pm=logout]');chk(pg.locator('#le').count()==1,'Cerrar sesión regresa a la pantalla de entrada')
        # piso role: no users option; menu in piso header
        pg.fill('#le','piso@propesa.mx');pg.fill('#lp','piso123');pg.click('[data-a=lg]')
        pa=pg.locator('.phd [data-avatar]');chk(pa.is_visible() and pa.inner_text().strip()=='L','Modo piso: círculo con la inicial (L de Luis Meza)')
        pa.click();items=pg.locator('#pmenu [role=menuitem]').all_inner_texts();chk(not any('Administración' in x for x in items) and any('Cerrar sesión' in x for x in items) and pg.locator('.phd [data-settings]').is_visible(),'el Encargado de piso no ve Administración; tiene Ajustes en la barra y Cerrar sesión en el menú')
        pg.click('[data-pm=logout]');chk(pg.locator('#le').count()==1,'Cerrar sesión desde Modo piso')
        ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth");chk(ov==0,'sin desbordes')
        pg.close()
    b.close()
print('ERRS',errs);print('RESULTADO:','TODO BIEN' if not fails and not errs else f'{len(fails)} fallas');sys.exit(1 if fails or errs else 0)
