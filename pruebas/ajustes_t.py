"""Pruebas del panel de Ajustes (SPEC.md). Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/ajustes_t.py
Variables: BASE (por defecto http://localhost:8765/index.html), OUT (carpeta para capturas)."""
import os,sys,json
from playwright.sync_api import sync_playwright
FIX="localStorage.clear();localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',pw:'admin123',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',pw:'piso123',role:'piso',notify:true},{id:3,name:'Dirección',email:'consulta@propesa.mx',pw:'ver123',role:'consulta',notify:false}]}))"  # usuarios SOLO para pruebas

BASE=os.environ.get('BASE','http://localhost:8765/index.html');OUT=os.environ.get('OUT','/tmp/propesa-pruebas');os.makedirs(OUT,exist_ok=True)
fails=[];errs=[]
def chk(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails.append(m)
DATA="""()=>{ST.R=[];ST.L=[];ST.B={};ST.OR=[];ST.P=[];for(let d=0;d<4;d++){const lot='LOTE'+d;ST.R.push({id:'R-'+(200+d),lot,origin:'SCPP Ensenada',tank:'T'+(d+1),rdate:dLoc(),time:'08:00',date:fd(dLoc()),tempT:58,tempP:'59-62',kgbox:18,desp:2,final:null,closed:false});ST.B[lot]=[];S.forEach(s=>post('RECEPCION',lot,s,100,0,''))}
 const o={id:1,etd:dLoc(),lines:[{id:1,city:'PVG',cons:0,cli:'HXH',boxes:6},{id:2,city:'PVG',cons:0,cli:'ZSM',boxes:4}],sh:{}};ST.OR.push(o);syncShip(o,'PVG',0);
 for(let b=0;b<3;b++){ST.BN=(ST.BN||0)+1;ST.B.LOTE0.push({c:20+b,k:'RVB'[b],d:0,o:'1.1',seq:ST.BN})}save()}"""
def lum(c):
    import re
    v=[int(x) for x in re.findall(r'[\d.]+',c)[:3]];v=[x/255 for x in v];v=[x/12.92 if x<=.03928 else ((x+.055)/1.055)**2.4 for x in v];return .2126*v[0]+.7152*v[1]+.0722*v[2]
def cr(a,b):
    x,y=sorted([lum(a),lum(b)],reverse=True);return (x+.05)/(y+.05)
def open_set(pg):
    pg.locator('[data-settings]:visible').first.click()
def login(pg,u='admin@propesa.mx',pw='admin123'):
    pg.fill('#le',u);pg.fill('#lp',pw);pg.click('[data-a=lg]')
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---- primera vez: sigue al sistema y 15 px ----
    for scheme in ['dark','light']:
        pg=b.new_page(color_scheme=scheme);pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(BASE);pg.evaluate(FIX);pg.reload();login(pg)
        chk(pg.evaluate("document.documentElement.getAttribute('data-theme')") is None,f'primera vez ({scheme}): sin tema forzado, sigue al equipo')
        chk(pg.evaluate("getComputedStyle(document.body).fontSize")=='15px','primera vez: texto base 15 px (igual que antes)')
        pg.close()
    for vw in [(390,844),(820,1180),(1440,900)]:
        pg=b.new_page(viewport={'width':vw[0],'height':vw[1]},color_scheme='dark');pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(BASE);pg.evaluate(FIX);pg.reload();login(pg);pg.evaluate(DATA);pg.evaluate("go('inicio')")
        btn=pg.locator('#app [data-settings]');bb=btn.bounding_box();ab=pg.locator('#app [data-avatar]').bounding_box()
        chk(btn.is_visible() and bb['y']<120 and bb['x']>vw[0]*0.5 and ab['x']>bb['x'],f'{vw[0]}px: botón Ajustes arriba a la derecha, junto al círculo de perfil')
        chk(pg.locator('.zs button').count()==0,f'{vw[0]}px: ya no están los botones A A A')
        # abrir/cerrar
        open_set(pg);chk(pg.locator('#setp .setpanel').is_visible() and btn.get_attribute('aria-expanded')=='true','Ajustes abre con su botón')
        chk(pg.evaluate("document.activeElement.id")=='set_t','el foco pasa al título Configuración')
        pg.keyboard.press('Escape');chk(not pg.locator('#setp .setpanel').count(),'Esc cierra');chk(pg.evaluate("!!document.activeElement.closest('[data-settings]')"),'el foco regresa a Ajustes')
        open_set(pg);pg.click('.setx');chk(not pg.locator('#setp .setpanel').count(),'la ✕ cierra')
        open_set(pg);pg.mouse.click(30,130);chk(not pg.locator('#setp .setpanel').count(),'tocar fuera cierra')
        # trampa de foco
        open_set(pg)
        for _ in range(8):pg.keyboard.press('Tab')
        chk(pg.evaluate("!!document.activeElement.closest('#setp')"),'Tab no se sale del panel');pg.keyboard.press('Escape')
        # no borra lo capturado
        pg.evaluate("go('recepcion')");pg.click('[data-a=nf]');pg.fill('#fo','Proveedor escrito');pg.fill('#fk1','12.5')
        open_set(pg);pg.click('[data-set-theme=light]');pg.keyboard.press('Escape')
        chk(pg.input_value('#fo')=='Proveedor escrito' and pg.input_value('#fk1')=='12.5','abrir Ajustes y cambiar tema no borra lo capturado')
        # tema: toda la app
        def look():
            return pg.evaluate("""()=>{const g=s=>{const e=document.querySelector(s);return e?getComputedStyle(e):null};const cd=g('.cd');return{bg:getComputedStyle(document.body).backgroundColor,cd:cd.backgroundColor,ink:cd.color,hd:g('.hd').backgroundColor,hdc:g('#sq').color,hdi:g('#sq').backgroundColor,mut:g('.mut')?g('.mut').color:null,th:g('th')?g('th').color:null,td:g('td')?g('td').color:null}}""")
        pg.evaluate("go('inicio')");L=look()
        open_set(pg);pg.click('[data-set-theme=dark]');D=look();pg.keyboard.press('Escape')
        chk(lum(L['bg'])>0.5 and lum(D['bg'])<0.05,f'tema cambia el fondo (claro {L["bg"]} / oscuro {D["bg"]})')
        chk(lum(L['cd'])>0.8 and lum(D['cd'])<0.05 and lum(L['hd'])>0.8 and lum(D['hd'])<0.05,'tema cambia tarjetas y encabezado')
        for name,t in [('claro',L),('oscuro',D)]:
            chk(cr(t['ink'],t['cd'])>=4.5,f'{name}: texto principal {cr(t["ink"],t["cd"]):.1f}:1')
            chk(cr(t['mut'],t['cd'])>=4.5,f'{name}: texto secundario {cr(t["mut"],t["cd"]):.1f}:1')
            chk(cr(t['td'],t['cd'])>=4.5 and cr(t['th'],t['cd'])>=4.5,f'{name}: tablas legibles')
            chk(cr(t['hdc'],t['hdi'])>=4.5,f'{name}: buscador del encabezado legible')
        # tamaño del texto con teclado
        open_set(pg);pg.wait_for_timeout(150);pg.focus('#set_fs')
        for _ in range(4):pg.keyboard.press('ArrowLeft')
        chk(pg.input_value('#set_fs')=='0' and pg.inner_text('#set_fsv')=='Normal' and pg.get_attribute('#set_fs','aria-valuetext')=='Normal, 15 píxeles','deslizador en Normal con flechas, valor visible y anunciado')
        sizes=[];labs=[]
        for k in range(3):
            sizes.append(pg.evaluate("getComputedStyle(document.body).fontSize"));labs.append(pg.inner_text('#set_fsv'))
            if k<2:pg.keyboard.press('ArrowRight')
        chk(sizes==['15px','17px','20px'] and labs==['Normal','Grande','Muy grande'],'solo 3 tamaños, deslizando: '+','.join(sizes)+' '+','.join(labs))
        chk(pg.locator('.setends span.on').inner_text()=='Muy grande','la etiqueta del tamaño elegido se resalta')
        # se ve lo que hay debajo
        sc=pg.evaluate("getComputedStyle(document.querySelector('.setscrim')).backgroundColor")
        chk(sc in ('rgba(0, 0, 0, 0)','transparent'),'al abrir Ajustes la pantalla de atrás no se oscurece')
        ph=pg.locator('.setpanel').bounding_box()
        if vw[0]<=600: chk(ph['height']<=vw[1]*0.7 and ph['y']>vw[1]*0.3,f'celular: Ajustes es una hoja desde abajo (deja ver {round(ph["y"])} px de pantalla)')
        else: chk(ph['width']<=vw[0]*0.5,f'el panel deja ver la pantalla a un lado ({round(vw[0]-ph["width"])} px)')
        m=pg.evaluate("""()=>{const q=s=>parseFloat(getComputedStyle(document.querySelector(s)).fontSize);const w=s=>document.querySelector(s).getBoundingClientRect().width;return{nav:q('.fs b'),td:q('td'),h2:q('h2'),inp:q('#sq'),ic:w('.fs i svg'),logo:w('.sb .lgb svg')}}""")
        pg.keyboard.press('Escape')
        pg.evaluate("PREF.fs=15;applyPrefs()");m15=pg.evaluate("""()=>{const q=s=>parseFloat(getComputedStyle(document.querySelector(s)).fontSize);const w=s=>document.querySelector(s).getBoundingClientRect().width;return{nav:q('.fs b'),td:q('td'),h2:q('h2'),inp:q('#sq'),ic:w('.fs i svg'),logo:w('.sb .lgb svg')}}""")
        chk(abs(m['nav']/m15['nav']-20/15)<0.02 and abs(m['td']/m15['td']-20/15)<0.02 and abs(m['h2']/m15['h2']-20/15)<0.02,f'menú, tablas y títulos crecen en proporción ({m15["td"]}→{m["td"]})')
        chk(m['ic']==m15['ic'] and m['logo']==m15['logo'],'íconos y logo no cambian de tamaño')
        pg.evaluate("PREF.fs=15;applyPrefs()");chk(pg.evaluate("parseFloat(getComputedStyle(document.querySelector('#sq')).fontSize)")>=16,'campos de captura nunca bajan de 16 px')
        # sin desbordes a 20 px
        pg.evaluate("PREF.fs=20;applyPrefs()");bad=[]
        for r in ['inicio','recepcion','ordenes','orden:1','empaque','empacar:1.1','embarques','emb:0','cierre','admin']:
            pg.evaluate(f"go('{r}')");ov=pg.evaluate("Math.max(document.documentElement.scrollWidth-document.documentElement.clientWidth,(m=>m.scrollWidth-m.clientWidth)(document.querySelector('main')))")
            if ov>2:bad.append((r,ov))
        pg.evaluate("setPiso(true);go('piso')")
        for r in ['piso','pemp:1.1','pent']:
            pg.evaluate(f"go('{r}')");ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
            if ov>2:bad.append((r,ov))
        chk(not bad,f'{vw[0]}px a 20 px: sin desbordes {bad}')
        chk(pg.locator('.phd [data-settings]').is_visible() and pg.locator('.phd [data-avatar]').is_visible(),'Modo piso también tiene Ajustes y el círculo de perfil')
        pg.screenshot(path=f'{OUT}/ajustes_{vw[0]}_piso20.png')
        pg.evaluate("setPiso(false);PREF.fs=15;applyPrefs();go('inicio')");open_set(pg);pg.screenshot(path=f'{OUT}/ajustes_{vw[0]}_panel.png');pg.keyboard.press('Escape')
        pg.close()
    # ---- se conserva al recargar, sin parpadeo ----
    pg=b.new_page(color_scheme='dark');pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(BASE);pg.evaluate(FIX);pg.reload();login(pg)
    open_set(pg);pg.click('[data-set-theme=light]');pg.fill('#set_fs','1');pg.dispatch_event('#set_fs','change')
    pg.reload()
    chk(pg.evaluate("document.documentElement.getAttribute('data-theme')")=='light' and pg.evaluate("getComputedStyle(document.body).fontSize")=='17px','tema y tamaño se conservan al recargar')
    first=pg.evaluate("""()=>new Promise(ok=>{const m=new MutationObserver(()=>{});ok(performance.getEntriesByType('paint').length)})""")
    pg.add_init_script("document.addEventListener('readystatechange',()=>{if(document.readyState=='interactive'&&!window.__th)window.__th=document.documentElement.getAttribute('data-theme')||'none'})")
    pg.reload();chk(pg.evaluate("window.__th")=='light','el tema guardado se aplica antes de dibujar (sin parpadeo)')
    # migración de "A A A"
    pg.evaluate("localStorage.removeItem('propesa-fs');localStorage.setItem('propesa-z','1.3')");pg.reload()
    chk(pg.evaluate("getComputedStyle(document.body).fontSize")=='20px','el tamaño "muy grande" anterior se respeta (20 px)')
    for old,exp in [('13','15px'),('18','17px'),('19','20px')]:
        pg.evaluate(f"localStorage.setItem('propesa-fs','{old}')");pg.reload();chk(pg.evaluate("getComputedStyle(document.body).fontSize")==exp,f'un tamaño guardado de {old} px se ajusta a {exp}')
    pg.close()
    # ---- sin localStorage ----
    ctx=b.new_context();ctx.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('bloqueado')}})")
    pg=ctx.new_page();e2=[];pg.on('pageerror',lambda e:e2.append(str(e)));pg.goto(BASE)
    chk(pg.locator('#le').count()+pg.locator('#s0n').count()==1,'sin almacenamiento la app abre')
    b.close()
print('ERRS',errs);print('RESULTADO:', 'TODO BIEN' if not fails and not errs else f'{len(fails)} fallas');sys.exit(1 if fails or errs else 0)
