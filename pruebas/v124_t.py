"""v1.24.0 · Pedidos del usuario del 27/oct/2026:
1. Logotipo de cada maquila: emblema (iniciales, forma y color propios) + «MAQUILA» + nombre, en el menú, Modo piso, el menú de
   maquilas, el Panel general y Administración. PROPESA conserva su logo.
2. «Langostas vivas al llegar al destino» se captura en Revisión → Mortalidad final, no en el embarque.
3. Lo que falta por empacar de cada orden, por talla: arriba en la orden, en Órdenes y en Empaque.
4. Juntar y separar embarques: un solo lugar (el embarque), antes → después, confirmar y deshacer (también al juntar).
5. El color de cada consignación es el del consignatario en Administración (elegido o no, abierta o cerrada).
Uso: python3 -m http.server 8765 (en la carpeta) y luego python3 -I pruebas/v124_t.py"""
import os
from playwright.sync_api import sync_playwright
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
USERS = "[{id:1,name:'Ana Torres',email:'admin@propesa.mx',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',role:'piso',notify:true}]"
FIX = "localStorage.clear();localStorage.setItem('propesa-kp','0');localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:%s}))" % USERS  # usuarios SOLO para pruebas
SETUP = """()=>{const lot=(code,date,kz)=>{const d={lot:code,origin:pvBy(1)?pvBy(1).n:'Proveedor',pv:1,sp:1,tank:'T1',rdate:date,time:'12:00',tempT:'58',tempP:'59',kgbox:'36',desp:'0',k4:0};kz.forEach((v,i)=>d['k'+i]=v);addLot(d)};
 lot('WLRCO201026','2026-10-20',[300,400,500,200]);
 const mk=(etd,city,cons,z)=>{const id=uidN();ST.OR.push({id,etd,lines:[],sh:{},sp:1});const o=ST.OR[ST.OR.length-1];o.lines.push({id:1,city,cons,boxes:z.reduce((a,b)=>a+b,0),z:S.map((_,i)=>z[i]||0),kp:16,tar:0,cc:0});shipFor(o,city,cons);syncShip(o,city,cons);return o};
 const a=mk('2026-10-27','PVG',0,[3,4,2,1]);mk('2026-10-28','PVG',0,[2,2,1,0]);mk('2026-10-28','HKG',3,[4,4,0,0]);
 for(let j=0;j<4;j++)ST.B['WLRCO201026'].push({c:28,k:TKEY[j%3],d:a.sh['PVG|0'],o:a.id+'.1',seq:uidN()});save();render()}"""
def login(pg, em):
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")
def txt(pg, sel): return ' '.join(pg.eval_on_selector_all(sel, 'e=>e.map(x=>x.textContent)')).replace('\n', ' ')
def rgb(pg, sel): return pg.evaluate(f"getComputedStyle(document.querySelector({sel!r})).backgroundColor")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append('JS ' + str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append('CONSOLE ' + m.text))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.evaluate(FIX); pg.reload(); login(pg, 'admin@propesa.mx'); pg.evaluate("mqSet(1)"); pg.evaluate(SETUP); pg.wait_for_timeout(150)

    # --- 5. colores: el de Administración, elegido o no
    hexs = lambda: pg.evaluate("ST.P.map((p,i)=>[pCol(p),consColor(shipCC(i).cons)])")
    chk(all(a == c for a, c in hexs()), 'sin color elegido, cada consignación toma el color que enseña Administración')
    chk(pg.evaluate("pCol(ST.P[0])===pCol(ST.P[1])"), 'dos consignaciones del mismo consignatario tienen el mismo color (antes iban por turno)')
    pg.evaluate("go('admin:cat')"); pg.wait_for_timeout(150)
    adm = pg.evaluate("document.querySelector('[data-cc=\"0\"]').value")
    pg.evaluate("go('embarques')"); pg.wait_for_timeout(150)
    sw = pg.evaluate("getComputedStyle(document.querySelector('.bp[data-go=\"emb:0\"]')).getPropertyValue('--c').trim()")
    chk(sw.lower() == adm.lower(), f'la tarjeta del embarque lleva el mismo color que Administración ({sw} = {adm})')
    pg.evaluate("go('admin:cat')"); pg.wait_for_timeout(100)
    pg.evaluate("(()=>{const x=document.querySelector('[data-cc=\"0\"]');x.value='#e8473d';x.dispatchEvent(new Event('change',{bubbles:true}))})()"); pg.wait_for_timeout(150)
    chk(pg.evaluate("pCol(ST.P[0])") == '#e8473d' and pg.evaluate("pCol(ST.P[1])") == '#e8473d', 'al cambiar el color en Administración cambian sus consignaciones')
    pg.evaluate("ST.CC={...ST.CC,0:'#123456'};save();render()")  # como si llegara de otro equipo
    chk(pg.evaluate("pCol(ST.P[0])") == '#123456', 'un color que llega de otro equipo se ve sin volver a guardar el embarque')
    pg.evaluate("ST.P[1].closed=true;ST.CC={...ST.CC,0:'#e8473d'};save();render()")
    chk(pg.evaluate("pCol(ST.P[1])") == '#e8473d', 'un embarque cerrado también enseña el color de su consignatario')
    pg.evaluate("ST.P[1].closed=false;save()")
    pg.evaluate("go('embarques')"); pg.wait_for_timeout(150)
    chk(pg.evaluate("[...document.querySelectorAll('.tleg i')].some(i=>i.style.background.includes('232, 71, 61'))"), 'el plan del camión usa el mismo color')

    # --- 3. lo que falta por empacar
    oid = pg.evaluate("ST.OR[0].id"); pg.evaluate(f"go('orden:{oid}')"); pg.wait_for_timeout(150)
    t = ' '.join(txt(pg, '#ord_falta').split())
    chk('Lo que falta por empacar' in t and '1 Chica' in t and '3 Mediana' in t and '1 Grande' in t and '1 Jumbo' in t and '4 de 10' in t, 'la orden dice arriba lo que falta, por talla: ' + t.replace('\n', ' | '))
    chk(pg.evaluate("document.querySelector('#ord_falta').compareDocumentPosition(document.querySelector('.cd .shp'))&4") > 0, 'la tarjeta va antes del detalle de los consignatarios')
    chk(pg.locator('#ord_falta [data-go^="empacar:"]').count() == 1, '«Seguir empacando ›» lleva a empacar esa línea')
    pg.evaluate("go('ordenes')"); pg.wait_for_timeout(120)
    chk(pg.locator('.ordt .zfs').count() == 3 and '3 Mediana' in ' '.join(txt(pg, '.ordt').split()), 'Órdenes: cada orden dice lo que falta por talla')
    pg.evaluate("go('empaque')"); pg.wait_for_timeout(120)
    chk(pg.locator('main .zfs').count() == 3, 'Empaque: cada consignatario dice lo que falta por talla')
    pg.evaluate(f"(()=>{{const o=ST.OR.find(x=>x.id=={oid});const sz=[[0,1],[1,3],[2,1],[3,1]];sz.forEach(([k,n])=>{{for(let j=0;j<n;j++)ST.B['WLRCO201026'].push({{c:28,k:TKEY[k],d:o.sh['PVG|0'],o:o.id+'.1',seq:uidN()}})}});save();go('orden:{oid}')}})()"); pg.wait_for_timeout(150)
    chk('Todo empacado' in txt(pg, '#ord_falta'), 'completa: «✔ Todo empacado»')

    # --- 4. juntar / separar
    pg.evaluate("go('orden:'+ST.OR[1].id)"); pg.wait_for_timeout(120)
    chk('Va en el embarque' in pg.inner_text('main .shp') and pg.locator('main .shp select').count() == 0, 'la orden dice en qué embarque va, sin selector ni «Unir»')
    pg.click('main .shp [data-go^="emb:"]'); pg.wait_for_timeout(250)
    chk(pg.evaluate("V.v") == 'emb' and pg.locator('#ordship [data-shq^="ask:join"]').count() == 1, 'lleva al embarque, a «Órdenes en este embarque»')
    n0 = pg.evaluate("ST.P.length")
    pg.click('[data-shq^="ask:join"]'); pg.wait_for_timeout(120)
    t = pg.inner_text('#shq'); chk('¿Juntar la orden del 27/10/2026' in t and 'Ahora' in t.title() and '15 hieleras' in t and '27/10 + 28/10' in t, 'antes de juntar enseña cómo queda: ' + t.replace('\n', ' | ')[:160])
    chk(pg.evaluate("ST.P.length") == n0, 'preguntar no cambia nada')
    pg.click('#shq [data-shq=no]'); pg.wait_for_timeout(100); chk(pg.locator('#shq').count() == 0 and pg.evaluate("ST.P.length") == n0, '«Cancelar» no cambia nada')
    pg.click('[data-shq^="ask:join"]'); pg.click('#shq [data-shq=ok]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("ST.P.length") == n0 - 1 and pg.locator('.shok').count() == 1 and '15 hieleras' in pg.inner_text('.shok'), 'juntadas, con el resultado en pantalla')
    pg.click('.shok [data-shq=undo]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("ST.P.length") == n0 and pg.evaluate("ST.P.every(p=>p.h>0)"), 'deshacer al juntar las vuelve a separar')
    chk(pg.evaluate("ST.B['WLRCO201026'].every(b=>b.d==null||!!ST.P[b.d])"), 'las hieleras siguen en un embarque que existe')

    # --- 2. vivas al llegar en Revisión
    pg.evaluate("go('emb:0')"); pg.wait_for_timeout(120)
    chk(pg.locator('main [data-alive],main [data-mc],main [data-tar]').count() == 0 and 'Langostas vivas al llegar al destino' not in pg.inner_text('main'), 'el embarque ya no tiene la captura de la llegada')
    pg.evaluate("go('cierre')"); pg.wait_for_timeout(120)
    chk(pg.locator('#envcli [data-alive]').count() >= 1 and 'Langostas vivas al llegar al destino' in pg.inner_text('#envcli') and '(enviadas − vivas)' in pg.text_content('[data-fold=mort-calc]'), 'Mortalidad final (Revisión) captura las vivas al llegar de cada envío')
    chk(pg.evaluate("document.querySelector('.sb [data-go=cierre]').previousElementSibling.textContent") == 'Revisión', 'Mortalidad final está en el grupo «Revisión» del menú')

    # --- 1. logotipo de cada maquila
    pg.evaluate("go('inicio')"); pg.wait_for_timeout(100)
    chk(pg.locator('.sb .mqlt').count() == 0 and pg.locator('.sb [data-mq] svg').count() == 1, 'PROPESA: el logo de PROPESA')
    marks = {}
    for mid, nm in [(2, 'Abel'), (3, 'David'), (4, 'Luis Arce')]:
        pg.evaluate(f"mqSet({mid});go('inicio')"); pg.wait_for_timeout(150)
        t = txt(pg, '.sb .mqlt .mqw')
        chk(t.upper().startswith('MAQUILA') and nm in t, f'{nm}: logotipo «MAQUILA {nm}» en el menú')
        marks[nm] = pg.evaluate("document.querySelector('.sb .mqlt .mqb').innerHTML")
        chk(pg.evaluate("document.querySelector('.sb').classList.contains('mqa')"), f'{nm}: franja de su color arriba del menú')
    chk(len(set(marks.values())) == 3, 'cada maquila tiene un emblema distinto')
    chk('>A<' in marks['Abel'] and '>D<' in marks['David'] and '>LA<' in marks['Luis Arce'], 'iniciales: A, D, LA')
    pg.click('.sb [data-mq]'); pg.wait_for_timeout(150)
    chk(pg.locator('#mqmenu .mqtg .mqb').count() == 3, 'el menú de maquilas lleva el emblema de cada una')
    pg.keyboard.press('Escape')
    pg.evaluate("PISO=true;go('piso')"); pg.wait_for_timeout(200)
    chk('Luis Arce' in pg.inner_text('.phd .mqlt') and pg.evaluate("document.querySelector('.phd').classList.contains('mqa')"), 'Modo piso: el logotipo en el encabezado')
    pg.evaluate("PISO=false;mqSet(1);go('general')"); pg.wait_for_timeout(150)
    chk(pg.locator('.mqt .mqtg .mqb').count() == 3, 'Panel general: emblema en la tabla por maquila')
    pg.evaluate("go('admin:mq')"); pg.wait_for_timeout(150)
    chk(pg.locator('#mqs .mqtg .mqb').count() == 3, 'Administración → Maquilas: emblema de cada una')
    pg.evaluate("ST.MQL=mqAll().concat([{id:5,n:'Pesquera Norte'}]);save();render()")
    chk(pg.evaluate("mqIni('Pesquera Norte')") == 'PN' and pg.evaluate("mqBadge(5)!==mqBadge(2)"), 'una maquila nueva también tiene su emblema')

    # --- tamaños, tema oscuro, celular
    pg.evaluate("mqSet(2)")
    for w_, h_ in [(390, 844), (820, 1180), (1440, 900)]:
        pg.set_viewport_size({'width': w_, 'height': h_})
        for r_ in ['inicio', 'ordenes', 'empaque', 'cierre']:
            pg.evaluate(f"go('{r_}')"); pg.wait_for_timeout(100); chk(not overflow(pg), f'Abel · {r_} sin scroll de lado en {w_} px')
    pg.evaluate("mqSet(1)")
    for w_, h_ in [(390, 844), (820, 1180)]:
        pg.set_viewport_size({'width': w_, 'height': h_})
        for r_ in ['orden:' + str(oid), 'emb:0', 'cierre']:
            pg.evaluate(f"go('{r_}')"); pg.wait_for_timeout(100); chk(not overflow(pg), f'{r_} sin scroll de lado en {w_} px')
        pg.evaluate("go('emb:0')"); pg.click('[data-shq^="ask:"] >> nth=0'); pg.wait_for_timeout(100); chk(not overflow(pg), f'la pregunta antes → después sin scroll de lado en {w_} px')
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.evaluate("mqSet(2);go('inicio')"); pg.wait_for_timeout(100)
    chk(pg.locator('.hd .hmq').is_visible(), 'celular: el emblema de la maquila en la barra de arriba')
    pg.click('.hd .hmq'); pg.wait_for_timeout(120); chk(pg.locator('#mqmenu .mqbox').count() == 1, 'tocar el emblema abre «Cambiar de maquila»')
    pg.keyboard.press('Escape'); pg.evaluate("document.documentElement.dataset.theme='dark';go('cierre')"); pg.wait_for_timeout(100)
    pg.evaluate("document.documentElement.dataset.theme='light'")
    # Piso no cambia la llegada
    pg.evaluate("me=null;mqSet(1);render()"); login(pg, 'piso@propesa.mx'); pg.evaluate("PISO=false;go('cierre')"); pg.wait_for_timeout(120)
    chk(pg.locator('#envcli [data-shq]').count() == 0, 'sin botones de juntar en Revisión')
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:5]))
print(f'\n{len(fails)} fallas')
