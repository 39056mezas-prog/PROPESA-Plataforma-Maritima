"""Varios camiones y acomodo a mano (v1.14.0, pedido del usuario 23/oct/2026).
- Cada embarque abierto va en un camión (p.tk); «Pasar a» lo cambia o crea un camión nuevo. Sin tk = Camión 1 (datos de antes igual).
- Acomodo automático = el de siempre (desde la cabina). Tocar dos celdas las intercambia; con una celda elegida se escribe
  cuántas hieleras de cada embarque lleva (dividir una tarima). Avisos si faltan, sobran o una celda se pasa.
- Los embarques cerrados salen aparte en «Embarques cerrados». tk/ly viajan en cleanST, WN.P y decodeST, y salen en el PDF.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/camiones_t.py"""
from playwright.sync_api import sync_playwright
import os, json
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em, pw):
    pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0")}', seed); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
# el acomodo de antes (v1.13.3), para comprobar que el automático no cambió
OLD = """(TP)=>{const cap=[15,20,20,25,25],slot={};let k=0;const rem=TP.map(p=>p.h);
 for(let i=4;i>=0;i--)for(let r=0;r<2;r++){while(k<rem.length&&rem[k]<=0)k++;if(k<rem.length){const v=Math.min(cap[i],rem[k]);rem[k]-=v;slot[i+'.'+r]={v,k}}}
 return Array.from({length:10},(_,s)=>{const q=slot[(s%5)+'.'+Math.floor(s/5)];return q?[q.k,q.v]:null})}"""
ADD = """()=>{[30,12].forEach((h,n)=>{const i=newShip();Object.assign(ST.P[i],{n:'HKG · PRUEBA'+n+' · 20/10',h,col:['#0583c3','#e5484d'][n]})});save();go('embarques')}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    # el automático da lo mismo que antes, con muchas combinaciones
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, 'admin@propesa.mx', 'admin123')
    bad = pg.evaluate("""()=>{const old=%s;let bad=0;for(let t=0;t<300;t++){const n=1+t%%5,hs=Array.from({length:n},()=>Math.floor(Math.random()*90));
      ST.P=hs.map((h,k)=>({u:'zz'+t+'x'+k+'aaaa',n:'X'+k,z0:'',col:'#123',exp:0,h,z:[0,0,0,0],c:[],alive:null,closed:false}));
      const a=old(ST.P),pl=truckPlan('');
      const same=a.every((x,s)=>{const q=pl.cells[s];return x?q.length===1&&q[0].v===x[1]&&pl.ly[x[0]][s]===x[1]:!q.length});if(!same)bad++;
      const ov=hs.reduce((x,y)=>x+y,0)-a.reduce((x,q)=>x+(q?q[1]:0),0);if(pl.over!==ov)bad++}return bad}""" % OLD)
    chk(bad == 0, f'el acomodo automático es igual al de antes (300 combinaciones, {bad} distintas)')
    pg.close()
    for vw in [(1180, 820), (820, 1180), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg, 'admin@propesa.mx', 'admin123'); pg.evaluate(ADD); pg.wait_for_timeout(100)
        chk(pg.locator('.tcard').count() == 1 and 'Camión 1' in pg.inner_text('.tcard h3') and pg.evaluate("ST.P.every(p=>!p.tk)"), f'{vw} datos de antes: un solo camión (Camión 1)')
        # pasar el embarque de 12 a un camión nuevo
        u = pg.evaluate("ST.P.find(p=>p.n.includes('PRUEBA1')).u")
        pg.select_option(f'select[data-tk="{u}"]', '+'); pg.wait_for_timeout(100)
        chk(pg.locator('.tcard').count() == 2 and 'Camión 2' in pg.inner_text('#tk_2 h3') and 'PRUEBA1' in pg.inner_text('#tk_2') and 'PRUEBA1' not in pg.inner_text('#tk_1 .tleg'), f'{vw} «Camión nuevo» crea el Camión 2 con ese embarque')
        chk('12 hieleras' in pg.inner_text('#tk_2 h3') and pg.locator('#tk_2 svg text', has_text='12').count() >= 1, f'{vw} el Camión 2 lleva sus 12 hieleras')
        pg.select_option(f'select[data-tk="{u}"]', pg.evaluate("trucks()[0]")); chk(pg.locator('.tcard').count() == 1, f'{vw} regresarlo al Camión 1 quita el camión vacío')
        pg.select_option(f'select[data-tk="{u}"]', '+')
        # mover hieleras en el Camión 1: tocar dos celdas
        pg.click('#tk_1 [data-ta^="ed:"]'); chk(pg.locator('#tk_1 .tcel').count() == 10, f'{vw} «Mover hieleras» muestra las 10 celdas')
        chk(pg.evaluate("Math.min(...[...document.querySelectorAll('#tk_1 .tcel')].map(e=>e.getBoundingClientRect().height))") >= 44, f'{vw} las celdas miden 44 px o más')
        t0 = pg.evaluate("truckPlan(trucks()[0]).cells.map(q=>q.reduce((a,z)=>a+z.v,0))")
        pg.click('#tk_1 [data-tc$=":4"]'); chk(pg.get_attribute('#tk_1 [data-tc$=":4"]', 'aria-pressed') == 'true' and pg.locator('#tk_1 .tsel input').count() == 2, f'{vw} tocar una celda la elige y deja escribir cuántas hieleras de cada embarque')
        pg.click('#tk_1 [data-tc$=":0"]')
        t1 = pg.evaluate("truckPlan(trucks()[0]).cells.map(q=>q.reduce((a,z)=>a+z.v,0))")
        chk(t1[0] == t0[4] and t1[4] == t0[0] and pg.evaluate("truckPlan(trucks()[0]).man") and not pg.locator('#tk_1 .er').count(), f'{vw} tocar otra celda las intercambia y queda a mano, sin avisos ({t0[4]}↔{t0[0]})')
        # dividir una tarima a mano: 5 hieleras del embarque de 7 en la celda 0
        u0 = pg.evaluate("ST.P[0].u"); pg.click('#tk_1 [data-tc$=":0"]'); pg.click('#tk_1 [data-tc$=":0"]')
        pg.fill(f'#tk_1 [data-tly="{u0}:0"]', '12'); pg.press(f'#tk_1 [data-tly="{u0}:0"]', 'Tab'); pg.wait_for_timeout(100)
        chk(pg.evaluate("ST.P[0].ly[0]") == 12 and 'Sobran 5 hieleras' in pg.inner_text('#tk_1'), f'{vw} escribir 12 (el embarque tiene 7) en una celda y avisa que sobran')
        pg.fill(f'#tk_1 [data-tly="{u0}:0"]', '0'); pg.press(f'#tk_1 [data-tly="{u0}:0"]', 'Tab'); pg.wait_for_timeout(100)
        chk('Faltan 7 hieleras' in pg.inner_text('#tk_1') and pg.locator('#tk_1 [data-ta^="fill:"]').count() == 1, f'{vw} si faltan, avisa en rojo con «Acomodar lo que falta»')
        pg.click('#tk_1 [data-ta^="fill:"]'); chk(not pg.locator('#tk_1 .er').count() and pg.evaluate("lySum(ST.P[0].ly)") == 7, f'{vw} «Acomodar lo que falta» las pone en el espacio libre')
        pg.fill(f'#tk_1 [data-tly="{u0}:0"]', '30'); pg.press(f'#tk_1 [data-tly="{u0}:0"]', 'Tab'); pg.wait_for_timeout(100)
        chk('caben 15' in pg.inner_text('#tk_1') and pg.locator('#tk_1 .tcel.ov').count() == 1, f'{vw} una celda que se pasa de su capacidad sale en rojo')
        pg.click('#tk_1 [data-ta^="auto:"]'); chk(pg.evaluate("ST.P.every(p=>!p.ly)") and not pg.locator('#tk_1 .er').count(), f'{vw} «Volver al acomodo automático»')
        # sin desbordes
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{vw} sin scroll de lado')
        # cerrar uno: pasa a «Embarques cerrados»
        pg.evaluate(f"ST.P[pIx('{u}')].closed=true;save();render()")
        if pg.locator('[data-hist=emb]').count(): pg.click('[data-hist=emb]')  # sin órdenes recientes: está en el historial
        tx = pg.inner_text('#app'); a, c = tx.index('Consignaciones abiertas'), tx.index('Embarques cerrados')
        chk('PRUEBA1' in tx[c:] and 'PRUEBA1' not in tx[a:c] and pg.locator('.tcard').count() == 1, f'{vw} al cerrar, el embarque sale en «Embarques cerrados» y deja el camión')
        pg.close()
    # el consulta no ve los controles
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, 'consulta@propesa.mx', 'consulta123'); pg.evaluate("go('embarques')")
    chk(pg.locator('[data-ta],[data-tk]').count() == 0, 'Consulta no puede mover hieleras ni cambiar camiones')
    # tk/ly se comparten y se limpian
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); entrar(pg, 'admin@propesa.mx', 'admin123'); pg.evaluate(ADD)
    r = pg.evaluate("""()=>{const p=ST.P[1];p.tk=uidS();p.ly=[1,2,3,4,5,6,7,8,9,'x'];const w=WN.P(p),c=cleanST({...ST,P:[...ST.P,{...p,u:'bad1aaaaa',tk:'<b>',ly:[1,2]}]},true),
      d=decodeST(new Map([...encodeST()].map(([k,v])=>[k,v[1]])));return {w:[w.tk===p.tk,JSON.stringify(w.ly)],c:[c.P[1].tk===p.tk,JSON.stringify(c.P[1].ly),'tk' in c.P[3],'ly' in c.P[3]],d:[d.P.find(x=>x.u===p.u).tk===p.tk,d.P.find(x=>x.u===p.u).ly!==p.ly],old:JSON.stringify(WN.P(ST.P[0]))}}""")
    chk(r['w'] == [True, '[1,2,3,4,5,6,7,8,9,0]'], f'WN.P comparte el camión y el acomodo {r["w"]}')
    chk(r['c'] == [True, '[1,2,3,4,5,6,7,8,9,0]', False, False], f'cleanST guarda lo válido y descarta camión o acomodo mal formados {r["c"]}')
    chk(r['d'] == [True, True], 'decodeST trae el camión y una copia del acomodo')
    chk('"tk"' not in r['old'] and '"ly"' not in r['old'], 'un embarque de antes se sube igual que antes (sin campos nuevos)')
    # PDF con dos camiones
    raw = pg.evaluate("(async()=>{ST.P[2].tk=uidS();const r=await pdfEmbarques();return Array.from(r.u8)})()"); raw = bytes(raw)
    chk(b'Cami\xf3n 1 \xb7 Plan de carga' in raw and b'Cami\xf3n 2 \xb7 Plan de carga' in raw, 'el PDF trae un plan de carga por camión')
    b.close()
chk(not errs, f'sin errores de JavaScript {errs[:3]}')
print('FALLAS:', len(fails))
