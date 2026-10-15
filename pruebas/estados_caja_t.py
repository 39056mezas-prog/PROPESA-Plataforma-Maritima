"""Prueba PROPESA (estados_caja_t): Empaque → cada caja muestra su estado (Pendiente / En captura / ✔ Completada / Editando),
las completadas se reabren y corrigen sin duplicarse, y la barra de abajo crece con el avance real.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/estados_caja_t.py"""
import json,os,shutil,tempfile
from playwright.sync_api import sync_playwright
BASE=os.environ.get('BASE','http://localhost:8765/index.html')
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
seed=json.loads(open(T+'seed.json').read())
seed['OR'].append({'id':3,'etd':'2026-10-13','lines':[{'id':1,'city':'HKG','cons':0,'cli':'ABC','boxes':4}],'sh':{}})
S=json.dumps(seed);errs=[]
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
def boxes(pg):
    st=json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"));return sorted([(x['seq'],x['c'],x['k'],l) for l,v in st['B'].items() for x in v if x['o']=='3.1'])
def fill(pg):  # ancho de la barra delgada de avance ÷ ancho del riel (espera a que termine la transición)
    pg.wait_for_timeout(650);return pg.evaluate("(()=>{const t=document.querySelector('.pkbar'),i=t.querySelector('i');return i.getBoundingClientRect().width/t.getBoundingClientRect().width})()")
def btnw(pg):return pg.evaluate("(()=>{const b=document.querySelector('.pkgo');return b?b.getBoundingClientRect().width:null})()")
def overlap(pg,a,b):return pg.evaluate("([a,b])=>{const x=document.querySelector(a),y=document.querySelector(b);if(!x||!y)return false;const p=x.getBoundingClientRect(),q=y.getBoundingClientRect();return !(p.right<=q.left||q.right<=p.left||p.bottom<=q.top||q.bottom<=p.top)}",[a,b])
def login(pg,u,pw):
    pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-kp","0")}',S);pg.reload()  # filas con sus botones de categoría (teclado cerrado)
    pg.fill('#le',u);pg.fill('#lp',pw);pg.click('[data-a=lg]');pg.evaluate("syncShip(ST.OR[2],'HKG',0);save()")
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw,sch in [((1440,900),'dark'),((820,1180),'light'),((390,844),'dark')]:
        tag=f'{vw[0]}'
        pg=b.new_page(viewport={'width':vw[0],'height':vw[1]},color_scheme=sch);pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        login(pg,'admin@propesa.mx','admin123');pg.evaluate("go('empacar:3.1')")
        pg.click('[data-pk^="lot:"] >> nth=0')
        # 0 %: todas pendientes, botón al mínimo
        chk(pg.locator('.pkrow').count()==4 and pg.locator('.pkdn').count()==0,tag+' 4 filas pendientes')
        chk('0% completado' in pg.inner_text('#pksum') and '4 pendientes' in pg.inner_text('#pksum'),tag+' resumen 0 % / 4 pendientes')
        f0=fill(pg);b0=btnw(pg)
        chk(f0<0.01,tag+f' barra de avance vacía al 0 % ({f0:.2f})')
        sw=pg.evaluate("[...document.querySelectorAll('#pkr0 .seg .chip')].map(e=>Math.round(e.getBoundingClientRect().width))");chk(len(set(sw))==1 and min(sw)>=60,tag+' Rojo/Verde/Blanco del mismo tamaño '+str(sw))
        sh=pg.evaluate("Math.min(...[...document.querySelectorAll('#pkr0 .seg .chip')].map(e=>e.getBoundingClientRect().height))");chk(sh>=44,tag+f' categoría con objetivo táctil ≥44 px ({sh:.0f})')
        chk(pg.locator('.pklb[aria-pressed=true]').count()==1,tag+' un lote marcado arriba')
        if pg.locator('.pklb').count()>1:  # v1.5: con cajas escritas, cambiar de pestaña de lote avisa y no las lleva al otro lote
            lot0=pg.evaluate("PKD.lot");pg.fill('#pk_c0','7')
            pg.click('.pklb[aria-pressed=false] >> nth=0');pg.wait_for_timeout(100)
            chk(pg.evaluate("PKD.lot")==lot0 and 'Primero guarda' in pg.inner_text('#toast'),tag+' cajas sin guardar: no cambia de lote y avisa')
            pg.fill('#pk_c0','')
        chk(pg.locator('.pkx .chip.ok').count()==0,tag+' sin pastillas verdes de estado')
        # elegir categoría sola: «En captura», NO completada
        pg.click('[data-pk="k:0:R"]')
        chk(pg.locator('#pkr0.is-prog').count()==1 and 'En captura' in pg.inner_text('#pkr0'),tag+' solo color → En captura')
        chk('Completada' not in pg.inner_text('#pkr0') and len(boxes(pg))==0,tag+' solo color no completa ni guarda')
        chk(pg.inner_text('.pkn')=='Guardar cajas',tag+' botón sin cajas listas: «Guardar cajas»')
        pg.fill('#pk_c0','20');chk(pg.inner_text('.pkn')=='Guardar 1 caja',tag+' botón cuenta cajas listas: '+pg.inner_text('.pkn'))
        # doble toque: no duplica
        pg.dblclick('[data-pk=addall]');pg.wait_for_timeout(700)
        bx=boxes(pg);chk(len(bx)==1 and bx[0][1:3]==(20,'R'),tag+' doble toque guarda 1 sola caja '+str(bx))
        chk(pg.locator('.pkdn.is-done').count()==1 and 'Completada' in pg.inner_text('.pkdn.is-done'),tag+' caja guardada → ✔ Completada')
        chk(pg.locator('.pkrow').count()==3,tag+' quedan 3 filas pendientes')
        lab=pg.evaluate("[...document.querySelectorAll('.pkt tbody tr:not(.pkear)')].map(r=>[r.querySelector('.pkno').innerText.split('\\n')[0].trim(),r.querySelector('.pkpz').innerText.replace(/\\s+/g,' ').trim()])")
        chk(all(x[0].startswith('Caja ') for x in lab) and all('piezas' in x[1] for x in lab),tag+' cada fila dice «Caja N» y las piezas llevan «piezas» '+str(lab[:2]))
        tb=pg.evaluate("(()=>{const t=document.querySelector('#toast').getBoundingClientRect(),b=document.querySelector('#pkb').getBoundingClientRect();return t.bottom<=b.top||getComputedStyle(document.querySelector('#toast')).display=='none'})()");chk(tb,tag+' el aviso sale arriba, no sobre la barra')
        chk('1 completada' in pg.inner_text('#pksum') and '3 pendientes' in pg.inner_text('#pksum') and '25% completado' in pg.inner_text('#pksum'),tag+' resumen 25 %: '+pg.inner_text('#pksum').replace('\n',' '))
        f1=fill(pg);chk(abs(f1-0.25)<0.02,tag+f' la barra delgada marca 25 % ({f1:.2f})');chk(abs(btnw(pg)-b0)<1,tag+' el botón Guardar no cambia de tamaño con el avance')
        chk(not overlap(pg,'#toast','#pkb'),tag+' el aviso no tapa la barra de abajo')
        exp=pg.evaluate("(()=>{const b=document.querySelector('.pkb'),p=+b.dataset.p;return p})()");chk(abs(exp-0.25)<1e-6,tag+' avance sale de los datos guardados (0.25)')
        # completadas distinguibles a simple vista: fondo distinto al de una pendiente
        bg=pg.evaluate("(()=>{const c=s=>{const e=document.querySelector(s),td=getComputedStyle(e.querySelector('td')).backgroundColor;return td!='rgba(0, 0, 0, 0)'?td:getComputedStyle(e).backgroundColor};return [c('.pkdn.is-done'),c('#pkr1')]})()")
        chk(bg[0]!=bg[1],tag+' fondo de completada ≠ pendiente '+str(bg))
        if vw[0]==1440:pg.screenshot(path=T+f'estados_{tag}_25.png')
        # reabrir tocando la fila completada; valores conservados
        seq=bx[0][0];pg.click(f'#pkd{seq} .pkv')
        chk(pg.locator('.pkdn.is-edit').count()>=1 and pg.input_value('#pk_e')=='20',tag+' tocar la caja la reabre con sus valores')
        chk(pg.get_attribute('#pkd%d [data-pk="ek:R"]'%seq,'aria-pressed')=='true','%s categoría guardada marcada'%tag)
        chk('Editando' in pg.inner_text('#pkd%d'%seq),tag+' muestra «Editando»')
        # vaciar piezas → pierde «Completada» mientras está incompleta, no se puede actualizar
        pg.fill('#pk_e','');chk('Incompleta' in pg.inner_text('#pkd%d'%seq),tag+' edición incompleta → ⚠ Incompleta')
        pg.click('[data-pk=upd]');chk(boxes(pg)[0][1]==20 and pg.locator('.pkdn.is-edit').count()>=1,tag+' no actualiza con piezas vacías y sigue editando')
        # corregir piezas y categoría → actualiza la MISMA caja
        pg.fill('#pk_e','24');pg.click('[data-pk="ek:V"]');pg.click('[data-pk=upd]')
        bx2=boxes(pg);chk(len(bx2)==1 and bx2[0][:3]==(seq,24,'V'),tag+' actualiza la misma caja sin duplicar '+str(bx2))
        chk(pg.locator('.pkdn.is-edit').count()==0 and 'Completada' in pg.inner_text(f'#pkd{seq}'),tag+' vuelve a ✔ Completada')
        # Cancelar no cambia nada
        pg.click(f'#pkd{seq} [data-pk^="ed:"].pked');pg.fill('#pk_e','99');pg.click('[data-pk=cancel]');chk(boxes(pg)[0][1]==24,tag+' Cancelar conserva lo guardado')
        # Enter guarda la corrección
        pg.click(f'#pkd{seq} .pked');pg.fill('#pk_e','26');pg.press('#pk_e','Enter');chk(boxes(pg)[0][1]==26 and pg.locator('.pkdn.is-edit').count()==0,tag+' Enter actualiza')
        # Esc cancela
        pg.click(f'#pkd{seq} .pked');pg.fill('#pk_e','5');pg.press('#pk_e','Escape');chk(boxes(pg)[0][1]==26,tag+' Esc cancela')
        # editar mientras hay filas a medias: lo escrito en pendientes no se borra
        pg.fill('#pk_c0','17');pg.click(f'#pkd{seq} .pked');pg.click('[data-pk=cancel]');chk(pg.input_value('#pk_c0')=='17',tag+' editar no borra filas a medias')
        # completar el resto → 100 %
        for r in range(3):
            pg.fill(f'#pk_c{r}',str(30+r));pg.click(f'[data-pk="k:{r}:B"]')
        pg.click('[data-pk=addall]');pg.wait_for_timeout(700)
        chk(len(boxes(pg))==4 and pg.locator('.pkdn.is-done').count()==4,tag+' 4 completadas')
        chk('100% completado' in pg.inner_text('#pksum') and '0 pendientes' in pg.inner_text('#pksum'),tag+' resumen 100 %')
        f4=fill(pg);chk(f4>0.98,tag+f' al 100 % la barra está llena ({f4:.2f})')
        chk(pg.locator('[data-pk=addall]').count()==0 and '4 de 4 cajas completadas' in pg.inner_text('.pkall'),tag+' al 100 % dice 4 de 4')
        # se puede corregir aun completa (sin botón Guardar abajo)
        s2=boxes(pg)[-1][0];pg.click(f'#pkd{s2} .pked');pg.fill('#pk_e','40');pg.click('[data-pk=upd]');chk([x for x in boxes(pg) if x[0]==s2][0][1]==40 and len(boxes(pg))==4,tag+' corrige con la línea completa')
        # Quitar desde la corrección (con confirmación) → vuelve a pendiente y la barra baja
        pg.click(f'#pkd{s2} .pked');pg.click('[data-pk^="del:"]');pg.click('[data-pk^="rm:"]')
        chk(len(boxes(pg))==3 and '75% completado' in pg.inner_text('#pksum') and pg.locator('.pkrow').count()==1,tag+' quitar caja → 75 % y 1 pendiente')
        # sin cruces ni desbordes
        ov=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth");chk(ov==0,tag+' sin desborde de página')
        ovr=not overlap(pg,'.pkgo','#pksum') and not overlap(pg,'.pkgo','.pkbar');chk(ovr,tag+' el botón no tapa el resumen')
        # recargar: los estados vienen de los datos guardados
        pg.wait_for_timeout(250);pg.reload()  # desde 1.2.5 recargar NO cierra la sesión: vuelve a la misma pantalla
        chk(pg.locator('#le').count()==0 and pg.evaluate("V.v+':'+V.id")=='empacar:3.1',tag+' tras recargar sigue dentro y en la misma pantalla')
        chk(pg.locator('.pkdn.is-done').count()==3 and '75% completado' in pg.inner_text('#pksum'),tag+' tras recargar: 3 completadas, 75 %')
        if vw[0]==1440:pg.screenshot(path=T+f'estados_{tag}_75.png')
        # Modo piso: mismas cajas, completadas en verde con «Completada»; en captura en cian; resumen
        pg.evaluate("PISO=true;go('pemp:3.1')")
        if pg.locator('[data-pe^="lot:"]').count():pg.click('[data-pe^="lot:"] >> nth=0')
        chk(pg.locator('.pbx.sv').count()==3 and 'Completada' in pg.inner_text('.pbx.sv >> nth=0'),tag+' piso: 3 tarjetas ✔ Completada')
        chk('1 pendiente' in pg.inner_text('.pkn2') and '75% completado' in pg.inner_text('.pkn2'),tag+' piso: resumen '+pg.inner_text('.pkn2').replace('\n',' '))
        free=pg.locator('.pbx:not(.sv)').first;fid=free.get_attribute('id')
        pg.click(f'#{fid} .pbn');pg.click('#kpad [data-kp="k:R"]');chk(pg.locator(f'#{fid}.ip').count()==1,tag+' piso: color sin piezas → en captura')
        pg.fill(f'#{fid} .ppc','12');pg.press(f'#{fid} .ppc','Enter');chk(len(boxes(pg))==4 and pg.locator('.pbx.sv').count()==4,tag+' piso: se guarda sola y queda completada')
        pg.focus('.psc >> nth=0');chk(pg.evaluate("getComputedStyle(document.querySelector('.pbx.sv:focus-within .pde')).display")!='none',tag+' piso: al corregir dice «Editando»')
        if vw[0]==1440:pg.screenshot(path=T+f'estados_{tag}_piso.png')
        pg.close()
    # consulta: solo ve la tabla, sin editar
    pg=b.new_page(viewport={'width':1280,'height':900});login(pg,'consulta@propesa.mx','ver123');pg.evaluate("go('empacar:1.1')")
    chk(pg.locator('.pkdn').count()==0 and pg.locator('[data-pk^="ed:"]').count()==0,'consulta: sin editar')
    pg.close();b.close()
chk(not errs,'sin errores de consola '+str(errs))
print('ERRS',errs)
