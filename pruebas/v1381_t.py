"""Prueba PROPESA (v1381_t): arreglos de la auditoría del 6/nov/2026 (v1.38.1).
1 · Empaque: una hielera que llega de otro equipo no borra ni «corrige» lo que se está capturando (Modo piso y vista completa).
2 · Packing list: el título de las notas usa el nombre del consignatario (antes «Notas · undefined»).
3 · Alta de cuenta: si falla el paso de las maquilas, «Guardar» otra vez cambia la cuenta en lugar de crearla de nuevo.
4 · Teclado: las categorías van en letra grande (contraste AA de texto grande).
5 · Planta 3D: los botones de la cámara no tapan las etiquetas de los tanques.
6 · Planta 3D sin «pointer events» (Safari 12): el texto dice que se gira con los botones.
7 · Modo piso en celular: el encabezado cabe en una línea.
8 · v1.38.2: los tanques vacíos no llevan etiqueta en la planta 3D (solo su letrero).
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v1381_t.py"""
import json,os
from playwright.sync_api import sync_playwright
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed=json.loads(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos','seed.json')).read())
seed['OR'].append({'id':3,'etd':'2026-10-14','lines':[{'id':1,'city':'HKG','cons':0,'boxes':3}],'sh':{}})  # línea nueva: sin cliente final
S=json.dumps(seed);errs=[];fails=0
def chk(c,m):
    global fails
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails+=1
def start(b,user,pw,route,vw=(768,1024),touch=True,init=None):
    ctx=b.new_context(viewport={'width':vw[0],'height':vw[1]},has_touch=touch,is_mobile=touch and vw[0]<800,accept_downloads=True)
    if init:ctx.add_init_script(init)
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',S);pg.reload()
    pg.fill('#le',user);pg.fill('#lp',pw);pg.click('[data-a=lg]');pg.wait_for_timeout(600)
    pg.evaluate(f"go('{route}')");pg.wait_for_timeout(200);return ctx,pg
BX="Object.values(ST.B).flat().filter(x=>x.o=='3.1').map(x=>[x.ps||0,x.c,x.k]).sort((a,b)=>a[0]-b[0]||a[1]-b[1])"
REMOTE="(c,k,ps)=>{const o=ST.OR.find(o=>o.id==3),b={c,k,d:shipFor(o,'HKG',0),o:'3.1',seq:uidN()};if(ps)b.ps=ps;ST.B.WLRCO061026B.push(b);softRender()}"
def toast(pg):return pg.evaluate("(document.getElementById('toast')||{}).textContent||''")
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---------- 1a · Modo piso: escribí 22 en la hielera 1 y llega una de la oficina (sin lugar) que cae en el lugar 1
    ctx,pg=start(b,'piso@propesa.mx','piso123','pemp:3.1')
    pg.tap('[data-pe="lot:WLRCO061026B"]');pg.wait_for_timeout(150)
    pg.tap('#kpad [data-kp="d:2"]');pg.tap('#kpad [data-kp="d:2"]')
    pg.evaluate(f"({REMOTE})(30,'V',0)");pg.wait_for_timeout(150)
    chk(pg.evaluate('KPT.t')=='slot:2' and pg.inner_text('#kpv')=='22','piso: lo escrito (22) pasó a la hielera 2 y el teclado la sigue')
    chk('pasó a la hielera 2' in toast(pg),'piso: aviso «Otro equipo guardó la hielera 1… pasó a la hielera 2»: '+toast(pg))
    pg.tap('#kpad [data-kp="k:R"]');pg.wait_for_timeout(250)
    chk(pg.evaluate(BX)==[[1,30,'V'],[2,22,'R']],f'piso: la hielera de la oficina sigue 30 Verde y la nueva es 22 Rojo {pg.evaluate(BX)}')
    # ---------- 1b · sin escribir nada: llega una hielera al lugar activo → el teclado pasa a la siguiente vacía, no la corrige
    chk(pg.evaluate('KPT.t')=='slot:3','piso: el teclado pasó a la hielera 3')
    pg.evaluate(f"({REMOTE})(25,'B',3)");pg.wait_for_timeout(150)
    chk(pg.evaluate('KPT.t') is None and 'Toca una hielera' in pg.inner_text('#kpt'),'piso: la hielera 3 la guardó otro equipo y ya no hay vacías: el teclado no queda en una hielera ajena')
    chk(pg.is_disabled('#kpad [data-kp="k:R"]') and pg.evaluate(BX)==[[1,30,'V'],[2,22,'R'],[3,25,'B']],'piso: sin hielera elegida las categorías no se pueden tocar y ninguna hielera cambia')
    # ---------- 1c · corregir a propósito sigue funcionando
    pg.tap('#pps1');pg.wait_for_timeout(100)
    chk(pg.evaluate('KPT.t')=='slot:1' and 'Corrigiendo' in pg.inner_text('#kps'),'piso: tocar una hielera guardada la abre para corregir')
    pg.tap('#kpad [data-kp="d:3"]');pg.tap('#kpad [data-kp="d:1"]');pg.tap('#kpad [data-kp="k:A"]');pg.wait_for_timeout(250)
    chk(pg.evaluate(BX)[0]==[1,31,'A'],f'piso: la corrección a propósito se guarda {pg.evaluate(BX)[0]}')
    ctx.close()
    # ---------- 1d · línea llena mientras escribes: se avisa que no se guardó
    ctx,pg=start(b,'piso@propesa.mx','piso123','pemp:3.1')
    pg.tap('[data-pe="lot:WLRCO061026B"]');pg.wait_for_timeout(150)
    pg.evaluate(f"({REMOTE})(20,'R',2)");pg.evaluate(f"({REMOTE})(21,'R',3)");pg.wait_for_timeout(100)
    pg.tap('#kpad [data-kp="d:1"]');pg.tap('#kpad [data-kp="d:9"]')
    pg.evaluate(f"({REMOTE})(30,'V',1)");pg.wait_for_timeout(150)
    chk('No se guardó lo que escribiste (19 piezas)' in toast(pg),'piso: si ya no hay lugar, avisa que lo escrito no se guardó: '+toast(pg))
    chk(pg.evaluate(BX)==[[1,30,'V'],[2,20,'R'],[3,21,'R']],'piso: las hieleras de los otros equipos no cambian')
    ctx.close()
    # ---------- 1f · computadora con el teclado de la app (el campo tiene el foco y la pantalla no se redibuja mientras escribes)
    ctx,pg=start(b,'piso@propesa.mx','piso123','pemp:3.1',vw=(1180,820),touch=False)
    pg.click('[data-pe="lot:WLRCO061026B"]');pg.wait_for_timeout(150);pg.click('#pps1');pg.wait_for_timeout(100)
    pg.keyboard.type('24');pg.evaluate(f"({REMOTE})(30,'V',1)");pg.wait_for_timeout(150)
    chk(pg.evaluate('busyField()'),'computadora: con el foco en el campo, lo que llega espera (no se pierde lo que escribes)')
    pg.click('#kpad [data-kp="k:R"]');pg.wait_for_timeout(250)
    chk(pg.evaluate(BX)==[[1,30,'V'],[2,24,'R']],f'computadora: al tocar la categoría se guarda en la hielera 2 y la de otro equipo no cambia {pg.evaluate(BX)}')
    chk('Guardada como hielera 2' in toast(pg),'computadora: avisa a qué hielera pasó: '+toast(pg))
    ctx.close()
    # ---------- 1e · vista completa: la fila que ya no cabe se ve en rojo
    ctx,pg=start(b,'admin@propesa.mx','admin123','empacar:3.1',vw=(1180,900),touch=False)
    pg.evaluate("localStorage.setItem('propesa-kp','0');KPON=false;render()");pg.click('[data-pk="lot:WLRCO061026B"]');pg.wait_for_timeout(100)
    pg.fill('#pk_c0','20');pg.fill('#pk_c1','21');pg.fill('#pk_c2','22')
    pg.evaluate(f"document.activeElement.blur();({REMOTE})(30,'V',0)");pg.wait_for_timeout(150)
    ov=pg.locator('.pkover')
    chk(ov.count()==1 and '22 piezas' in ov.inner_text(),'vista completa: la captura que ya no cabe sale en rojo: '+(ov.inner_text() if ov.count() else ''))
    pg.click('[data-pk="k:0:R"]');pg.wait_for_timeout(200)
    chk(pg.locator('.pkover').count()==1,'vista completa: después de guardar una, la que no cabe sigue a la vista')
    pg.click('[data-pk^="drop:"]');pg.wait_for_timeout(150)
    chk(pg.locator('.pkover').count()==0,'vista completa: «Quitar» la quita')
    # ---------- 2 · PDF: título de las notas
    pg.evaluate("(ST.M=ST.M||{})['emp:3.1']=[{id:uidN(),text:'Revisar tapa',imgs:[],by:'Ana',t:now()}];save();render()")
    with pg.expect_download() as d: pg.locator('[data-pdf^="dl:emp"]').first.click()
    raw=open(d.value.path(),'rb').read()
    chk(b'undefined' not in raw and b'(Notas \xb7 YISHUNHAI)' in raw,'packing list: «Notas · YISHUNHAI» (sin «undefined»)')
    # ---------- 3 · alta de cuenta: falla el paso de las maquilas y se vuelve a guardar
    r=pg.evaluate("""async()=>{const calls=[];const F=fnUsers,SF=sbFetch;fnUsers=async(a,b)=>{calls.push(a);return a=='create'?{ok:true,id:'u-nuevo'}:{ok:true}};
      let n=0;sbFetch=async()=>{if(!n++){const e=new Error('Sin conexión');e.status=null;throw e}return {json:async()=>[]}};
      const L=loadProfiles;loadProfiles=async()=>true;uf={};
      try{await saveUCloud('Comprador','c@x.mx','12345678x','cliente',false,true,[1]);const id1=uf&&uf.id;
        await saveUCloud('Comprador','c@x.mx','12345678x','cliente',false,!(uf&&uf.id),[1]);return {calls,id1}}
      finally{fnUsers=F;sbFetch=SF;loadProfiles=L}}""")
    chk(r['id1']=='u-nuevo' and r['calls']==['create','update'],f"alta de cuenta: el segundo intento es un cambio, no un alta {r}")
    ctx.close()
    # ---------- 4 · categorías del teclado en letra grande (≥ 18.66 px y negrita)
    for vw in [(1180,820),(768,1024),(390,844)]:
        ctx,pg=start(b,'piso@propesa.mx','piso123','pemp:3.1',vw=vw)
        pg.tap('[data-pe="lot:WLRCO061026B"]');pg.wait_for_timeout(150)
        fs=pg.evaluate("[...document.querySelectorAll('#kpad .kpc button')].map(e=>{const c=getComputedStyle(e);return [parseFloat(c.fontSize),+c.fontWeight]})")
        chk(all(x[0]>=18.6 and x[1]>=700 for x in fs),f'{vw[0]}: categorías del teclado en texto grande {fs[0]}')
        cut=pg.evaluate("[...document.querySelectorAll('#kpad .kpc button')].filter(e=>e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+1).length")
        chk(cut==0,f'{vw[0]}: los nombres caben en sus botones')
        # ---------- 7 · encabezado de Modo piso en una línea
        h=pg.evaluate("Math.round(document.querySelector('.phd').getBoundingClientRect().height)")
        chk(h<=112,f'{vw[0]}: el encabezado de Modo piso cabe en una línea ({h} px)')
        ctx.close()
    ctx,pg=start(b,'piso@propesa.mx','piso123','piso',vw=(360,800));pg.evaluate("go('pemp')");pg.wait_for_timeout(200)
    h=pg.evaluate("Math.round(document.querySelector('.phd').getBoundingClientRect().height)")
    chk(h<=112,f'360: el encabezado de Modo piso cabe en una línea ({h} px)')
    chk(pg.get_attribute('.phd [data-back]','aria-label')=='Atrás','360: «‹ Atrás» tiene nombre para el lector de pantalla (v1.39.0: reemplaza a «Inicio»; el logo lleva al inicio)')
    ctx.close()
    # ---------- 5 · planta 3D: los botones no tapan etiquetas
    for vw in [(768,1024),(390,844),(1440,900)]:
        ctx,pg=start(b,'admin@propesa.mx','admin123','inicio',vw=vw,touch=False)
        pg.evaluate("FOLD['ent-tq']=true;T3.on=true;go('recepcion')");pg.wait_for_timeout(900)
        ov=pg.evaluate("""(()=>{const c=document.querySelector('.t3ctl').getBoundingClientRect();return [...document.querySelectorAll('.t3l:not([hidden]) .t3tag')].filter(e=>{const r=e.getBoundingClientRect();return r.right>c.left&&r.left<c.right&&r.bottom>c.top&&r.top<c.bottom}).map(e=>e.textContent)})()""")
        chk(ov==[],f'{vw[0]}: ninguna etiqueta de tanque queda detrás de los botones de la cámara {ov}')
        tg=pg.evaluate("[...document.querySelectorAll('.t3v .t3tag')].map(e=>e.textContent)")
        chk(tg and not any('Vacío' in t for t in tg) and len(tg)==pg.evaluate("TK.filter(t=>(T3.cs[t]||[]).n>0).length"),f'{vw[0]}: v1.38.2 · solo los tanques con canastas llevan etiqueta {tg}')
        chk(pg.locator('.t3v .t3sign').count()==6,f'{vw[0]}: los 6 tanques siguen con su letrero «TANQUE n»')
        ctx.close()
    # ---------- 6 · sin pointer events
    ctx,pg=start(b,'admin@propesa.mx','admin123','inicio',touch=False,init="delete window.PointerEvent")
    pg.evaluate("FOLD['ent-tq']=true;T3.on=true;go('recepcion')");pg.wait_for_timeout(600)
    chk('Usa los botones' in pg.inner_text('.t3bar'),'sin pointer events (Safari 12): «Usa los botones ⟲ ⟳ para girar»')
    ctx.close()
    ctx,pg=start(b,'admin@propesa.mx','admin123','inicio',touch=False)
    pg.evaluate("FOLD['ent-tq']=true;T3.on=true;go('recepcion')");pg.wait_for_timeout(600)
    chk('Arrastra para girar' in pg.inner_text('.t3bar'),'con pointer events: «Arrastra para girar»')
    ctx.close()
    chk(not errs,f'sin errores de JavaScript {errs[:3]}')
    b.close()
print('RESULTADO:',fails,'FALLAS' if fails else 'TODO BIEN')
