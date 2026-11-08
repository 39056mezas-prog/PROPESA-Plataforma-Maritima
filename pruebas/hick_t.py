"""Prueba PROPESA (hick_t): actualización Ley de Hick (v1.39.0, 7/nov/2026).
Ajustes con 5 tamaños de texto · logo = Centro de operaciones y la maquila en su propio botón · «‹ Atrás» que regresa con lo escrito ·
Centro de operaciones (4 números → planta 3D; sin avisos ni cuadrícula de accesos) · Panel general con los números arriba ·
3D con su propio ícono · Entrada: acciones al principio, lote sin entrada se arregla desde una tarjeta arriba, «otro tanque» plegado ·
corregir el color de varias hieleras (Administrador) · PDF con los datos oficiales · eliminar discreto que confirma ·
orden con «Empacar lo que falta» · Embarque con la lista primero · Modo piso sin «Inicio» repetido.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/hick_t.py"""
import json,os
from playwright.sync_api import sync_playwright
BASE=os.environ.get('BASE','http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
S=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos','backup.json')).read();errs=[];fails=0
def chk(c,m):
    global fails
    print(('PASS ' if c else 'FAIL ')+m)
    if not c:fails+=1
def start(b,vw=(768,1024),user='admin@propesa.mx',pw='admin123',dark=False):
    ctx=b.new_context(viewport={'width':vw[0],'height':vw[1]},color_scheme='dark' if dark else 'light')
    pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',S);pg.reload()
    pg.fill('#le',user);pg.fill('#lp',pw);pg.click('[data-a=lg]');pg.wait_for_timeout(500);return ctx,pg
def go(pg,r):pg.evaluate(f"go({json.dumps(r)})");pg.wait_for_timeout(150)
ev=lambda pg,js:pg.evaluate(js)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=start(b)
    # ---------- Centro de operaciones
    chk(ev(pg,'V.v')=='inicio','al entrar abre el Centro de operaciones')
    chk(pg.inner_text('main h1')=='Centro de operaciones','título «Centro de operaciones»')
    order=ev(pg,"[...document.querySelectorAll('main .ctg4, main .t3bar')].map(x=>x.className.split(' ')[0])")
    chk(order[:2]==['g4','t3bar'],f'orden: 4 números → planta 3D ({order})')
    chk(ev(pg,"document.querySelectorAll('.ctg4 .ctk').length")==4,'4 números que se tocan')
    chk(ev(pg,"!document.querySelector('main .ctstrip,main .ctl,main .pt,main .fmg')"),'centro de mando, no otro menú: sin cuadrícula de accesos a los módulos')
    chk(ev(pg,"!document.querySelector('main .nti')"),'sin lista de avisos en el Centro (van en la campana)')
    pg.click('.ctk[data-go=embarques]');pg.wait_for_timeout(150);chk(ev(pg,'V.v')=='embarques','un número lleva a su sección')
    go(pg,'formatos');chk(ev(pg,'V.v')=='inicio','«formatos» (de antes) llega al Centro')
    chk(ev(pg,"[...document.querySelectorAll('.sb .fs b')].map(x=>x.textContent).filter(t=>t=='Formatos'||t=='Panel').length")==0,'el menú ya no tiene Formatos ni Panel por separado')
    chk(ev(pg,"(()=>{const a=[...document.querySelectorAll('.sb > *')];return a.indexOf(document.querySelector('.sb [data-mode=piso]'))>a.indexOf(document.querySelector('.sb [data-go=hojas]'))})()"),'el interruptor de Modo piso va al final del menú')
    chk(ev(pg,"document.querySelector('.sb').getBoundingClientRect().width")<=190,'menú más angosto en iPad mini')
    # ---------- logo y maquila
    go(pg,'recepcion');pg.click('.sb .lgh');pg.wait_for_timeout(150)
    chk(ev(pg,'V.v')=='inicio','tocar el logo lleva al Centro de operaciones')
    pg.click('.sb button.mqn');pg.wait_for_timeout(150)
    chk(ev(pg,'MQOPEN'),'el botón de la maquila abre el menú de maquilas');pg.keyboard.press('Escape');pg.wait_for_timeout(100)
    chk(ev(pg,"(()=>{const r=document.querySelector('.sb button.mqn').getBoundingClientRect(),e=document.elementFromPoint(r.left+r.width/2,r.top-5);return !!e&&!!e.closest('button.mqn')})()"),'el botón de la maquila se toca más allá de su borde (44 px)')
    # ---------- «‹ Atrás»
    chk(ev(pg,"!document.querySelector('.hd [data-back]')"),'en el Centro no hay «Atrás»')
    go(pg,'ordenes');pg.fill('#no_etd','15/11/2026');go(pg,'orden:1')
    chk(ev(pg,"!!document.querySelector('.hd [data-back]')"),'en otras pantallas sí hay «Atrás»')
    chk(ev(pg,"!document.querySelector('main .back')"),'sin «‹ Volver a…» repetido dentro de la página')
    pg.click('.hd [data-back]');pg.wait_for_timeout(300)
    chk(ev(pg,'V.v')=='ordenes','«Atrás» regresa a la pantalla anterior')
    chk(pg.input_value('#no_etd')=='15/11/2026','al regresar, lo escrito sigue ahí')
    pg.click('.hd [data-back]');pg.wait_for_timeout(300);chk(ev(pg,'V.v')=='inicio','otra vez «Atrás» → Centro')
    go(pg,'hojas');pg.click('[data-hjv]');pg.wait_for_timeout(200)
    chk(ev(pg,'HJX') is not None,'Hojas: la vista previa se agranda');pg.click('.hd [data-back]');pg.wait_for_timeout(200)
    chk(ev(pg,'HJX') is None and ev(pg,'V.v')=='hojas','«Atrás» primero cierra la vista previa grande')
    # ---------- Ajustes: 5 tamaños, sin vista previa
    pg.click('.hd [data-settings]');pg.wait_for_timeout(150)
    chk(pg.get_attribute('#set_fs','max')=='4' and ev(pg,"document.querySelectorAll('.setends span').length")==5,'5 tamaños de texto')
    chk(ev(pg,"!document.querySelector('.setprev')"),'sin «Vista previa» en Ajustes')
    pg.evaluate("(()=>{const r=document.getElementById('set_fs');r.value=0;r.dispatchEvent(new Event('input',{bubbles:true}));r.dispatchEvent(new Event('change',{bubbles:true}))})()")
    chk(ev(pg,"getComputedStyle(document.documentElement).fontSize")=='11px','«Muy chico» = 11 px (75 %)')
    chk(ev(pg,"localStorage.getItem('propesa-fs')")=='11','se guarda en el equipo')
    pg.keyboard.press('Escape');go(pg,'recepcion');pg.click('[data-a=nf]');pg.wait_for_timeout(100)
    chk(ev(pg,"parseFloat(getComputedStyle(document.getElementById('fl')).fontSize)")>=16,'con texto chico, las casillas siguen en 16 px')
    pg.reload();pg.wait_for_timeout(500);chk(ev(pg,"getComputedStyle(document.documentElement).fontSize")=='11px','al recargar se queda en 11 px')
    pg.evaluate("localStorage.setItem('propesa-fs','15')");pg.reload();pg.wait_for_timeout(500)
    # ---------- Panel general y botón 3D
    go(pg,'general')
    chk(ev(pg,"(()=>{const g=document.querySelector('main .g4'),t=document.querySelector('main .t3bar');return !!g&&!!t&&(g.compareDocumentPosition(t)&4)>0})()"),'Panel general: los 4 números van arriba del 3D')
    on=ev(pg,"document.querySelector('.t3tg').getAttribute('aria-pressed')");pg.click('.t3tg');pg.wait_for_timeout(200)
    chk(ev(pg,"document.querySelector('.t3tg').getAttribute('aria-pressed')")!=on,'el ícono 3D apaga/prende la planta y se queda en su lugar')
    chk(ev(pg,"document.querySelectorAll('.t3tg svg').length")==1,'el botón 3D es un ícono')
    pg.click('.t3tg');pg.wait_for_timeout(200)
    # ---------- Entrada: acciones primero y fijas; «otro tanque» plegado
    go(pg,'recepcion')
    chk(ev(pg,"document.querySelector('table.ent tbody tr td').classList.contains('acts')"),'Entrada: Ver/Editar/Eliminar en la primera columna')
    chk(ev(pg,"getComputedStyle(document.querySelector('table.ent td.acts')).position")=='sticky','esa columna se queda fija al deslizar')
    pg.click('[data-a=nf]');pg.wait_for_timeout(100)
    chk(ev(pg,"!document.querySelector('[data-fold=ent-t2]').open"),'«Repartir en otro tanque» empieza plegado')
    go(pg,'pent')
    chk(ev(pg,"!document.querySelector('.pt2').open"),'hoja de entradas: «otro tanque» plegado')
    # ---------- lote sin lote: se arregla desde su tarjeta
    pg.evaluate("""(()=>{ST.R.push({id:newLotId(),lot:'SIN-LOTE-1310',origin:'',tank:'',rdate:'',time:'',date:'',tempT:null,tempP:'',kgbox:null,desp:null,final:null,closed:false,ne:true,sl:true});
     ST.B['SIN-LOTE-1310']=ST.B.WLRCO051026A.filter(x=>x.o=='2.1');ST.B.WLRCO051026A=ST.B.WLRCO051026A.filter(x=>x.o!='2.1');save()})()""")
    go(pg,'recepcion')
    chk('Arreglar' in ev(pg,"[...document.querySelectorAll('table.ent tr')].find(r=>r.textContent.includes('SIN-LOTE-1310')).textContent"),'en la tabla, el lote sin lote dice «Arreglar ›»')
    pg.click('[data-led="el:SIN-LOTE-1310"]');pg.wait_for_timeout(250)
    chk(ev(pg,'V.v')=='lote' and ev(pg,"!!document.getElementById('nejoin')"),'«Arreglar» abre el lote con su tarjeta')
    chk(ev(pg,"!document.querySelector('main [data-a=el]')"),'sin «Editar» que se queda bloqueado')
    chk(ev(pg,"document.querySelector('main .cd.head').nextElementSibling.id")=='nejoin','la tarjeta va justo debajo del encabezado')
    pg.click('[data-a=nfj]');pg.wait_for_timeout(150)
    pg.evaluate("""(()=>{const v={fh:'09:30',ftt:'58',ftp:'59-61',fl:'WLRCO131026A',fkb:'18',fk0:'10',fk1:'20',fk2:'0',fk3:'0',fdes:'0'};for(const k in v){const e=document.getElementById(k);if(e)e.value=v[k]}
     const fo=document.getElementById('fo');fo.value=fo.options[1].value;fo.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('fd').value='13/10/2026';document.getElementById('fl').value='WLRCO131026A'})()""")
    pg.click('[data-a=sv]');pg.wait_for_timeout(300)
    chk(ev(pg,"!R_('SIN-LOTE-1310')"),'«+ Crear su entrada»: el lote provisional desaparece ('+ev(pg,"(document.querySelector('.fer,.er')||{}).textContent||''")+')')
    chk(ev(pg,"(ST.B.WLRCO131026A||[]).length")==2,'y sus 2 hieleras pasan a la entrada nueva')
    # ---------- eliminar: discreto, a la vista, y confirma
    go(pg,'lote:WLRCO051026A')
    chk(ev(pg,"!!document.querySelector('.cd.head .btn.dq[data-a=dl]')"),'«Eliminar» discreto (texto rojo con bote) en el encabezado')
    chk(ev(pg,"getComputedStyle(document.querySelector('.btn.dq')).backgroundColor")=='rgba(0, 0, 0, 0)','sin fondo rojo lleno')
    pg.click('[data-a=dl]');pg.wait_for_timeout(100)
    chk('¿Eliminar el lote WLRCO051026A?' in pg.inner_text('.dqcf'),'confirma diciendo qué se borra')
    pg.click('[data-a=dln]');pg.wait_for_timeout(100);chk(ev(pg,"!!R_('WLRCO051026A')") and ev(pg,"!document.querySelector('.dqcf')"),'«No» no borra')
    # ---------- orden: acción principal y colores
    go(pg,'orden:1');chk(ev(pg,"!!document.querySelector('.ordact .btn.dq[data-oa=dco]')"),'orden: «Eliminar orden» discreto')
    chk(ev(pg,"!!document.querySelector('.ordact [data-go^=colores]')"),'orden: «Corregir color de hieleras» (Administrador)')
    pg.evaluate("ST.OR.find(o=>o.id==1).lines[0].boxes=5;save();render()")
    chk('Empacar lo que falta' in ev(pg,"(document.querySelector('.ordact .btn:not(.q):not(.dq):not(.s)')||{}).textContent||''"),'orden con faltantes: «Empacar lo que falta ›» arriba')
    go(pg,'colores:1')
    n0=ev(pg,"document.querySelectorAll('[data-ccx]').length");chk(n0==5,f'colores: lista las 5 hieleras ({n0})')
    pg.click('[data-cc="k:R"]');pg.wait_for_timeout(100)
    nr=ev(pg,"document.querySelectorAll('[data-ccx]:checked').length");chk(nr==2,f'«Las de Rojo» marca 2 ({nr})')
    pg.click('[data-cc="to:V"]');pg.wait_for_timeout(100)
    chk('Así queda' in pg.inner_text('.ccpv'),'enseña «Ahora → Así queda» antes de cambiar')
    pg.click('[data-cc=go]');pg.wait_for_timeout(150)
    chk(ev(pg,"ordBoxes(ST.OR.find(o=>o.id==1)).filter(x=>x.b.k=='R').length")==0,'cambió las 2 rojas a verde')
    pg.click('[data-cc=undo]');pg.wait_for_timeout(150)
    chk(ev(pg,"ordBoxes(ST.OR.find(o=>o.id==1)).filter(x=>x.b.k=='R').length")==2,'«Deshacer» las regresa')
    pg.evaluate("ST.P[0].closed=true;render()");go(pg,'colores:1')
    nn=ev(pg,"document.querySelectorAll('[data-ccx]:not(:disabled)').length");tx=pg.inner_text('main');chk(nn==0 and 'embarque cerrado' in tx.lower() and ev(pg,"!!document.querySelector('main .alk[data-go^=emb]')"),f'en un embarque cerrado no se pueden cambiar (y dice por qué) ({nn})');pg.evaluate("ST.P[0].closed=false")
    # ---------- PDF con datos oficiales
    svg=ev(pg,"pdfPrev('ent','')")
    chk('PPE130617V37' in svg and 'Maneadero' in svg and '646 596 0833' in svg,'PDF: RFC, dirección y teléfono de PROPESA')
    # ---------- Embarque: la lista primero
    go(pg,'embarques')
    chk(ev(pg,"(()=>{const h=[...document.querySelectorAll('main h2')].find(x=>x.textContent=='Consignaciones abiertas'),t=document.querySelector('main .tcard');return !!h&&(!t||(h.compareDocumentPosition(t)&4)>0)})()"),'Embarque: consignaciones abiertas antes del camión')
    ctx.close()
    # ---------- Modo piso: «Atrás» en lugar de «Inicio», logo al inicio
    ctx,pg=start(b,user='piso@propesa.mx',pw='piso123')
    go(pg,'pent');chk(ev(pg,"!!document.querySelector('.phd [data-back]') && !document.querySelector('.phd .ph1')"),'Modo piso: «Atrás» y sin el botón «Inicio» repetido')
    hh=ev(pg,"Math.round(document.querySelector('.phd').getBoundingClientRect().height)");chk(hh<=112,f'la barra de Modo piso cabe en un renglón en iPad mini ({hh} px)')
    pg.click('.phd .lgh');pg.wait_for_timeout(150);chk(ev(pg,'V.v')=='piso','Modo piso: el logo lleva a «¿Qué vas a hacer?»')
    ctx.close()
    # ---------- celular y tema oscuro: sin desbordes
    for vw,dark in (((390,844),True),((1440,900),False)):
        ctx,pg=start(b,vw,dark=dark)
        for r in ('inicio','recepcion','colores:1','general'):
            go(pg,r);ov=ev(pg,"(()=>{const m=document.querySelector('main');return Math.max(document.documentElement.scrollWidth-document.documentElement.clientWidth,m.scrollWidth-m.clientWidth)})()")
            chk(ov<=0,f'{vw[0]} px{" oscuro" if dark else ""} · {r}: nada se sale ({ov})')
        ctx.close()
    b.close()
chk(not errs,'sin errores de JavaScript '+str(errs[:3]))
print('TODO BIEN' if not fails else f'{fails} FALLAS')
