"""Prueba PROPESA (tabla_entrada_t): la tabla de Entrada se lee bien.
Encabezados de talla en dos renglones (rango principal arriba, secundario abajo), sin números partidos,
punto de color junto a su talla, encabezados sin cortes de más y desplazamiento horizontal dentro de la tarjeta.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/tabla_entrada_t.py"""
import os
from playwright.sync_api import sync_playwright
BASE=os.environ.get('BASE','http://localhost:8765/index.html')
SEED=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos','seed.json'),encoding='utf-8').read()
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
PRI=['0-650','651-850','851-1250','1251-UP'];SEC=['491-610','611-850','851-1220','1221-UP']
MEDIR="""()=>{const t=document.querySelector('table.ent'),w=t.closest('.tbl'),lh=e=>parseFloat(getComputedStyle(e).lineHeight);
 const lines=e=>{const r=document.createRange();r.selectNodeContents(e);const ys=new Set([...r.getClientRects()].map(x=>Math.round(x.top)));return ys.size};
 const sz=[...t.querySelectorAll('th.szh')].map(th=>{const a=th.querySelector('.szh1'),b=th.querySelector('.szh2'),d=th.querySelector('.szd');
   const ra=a.getBoundingClientRect(),rb=b.getBoundingClientRect(),rd=d.getBoundingClientRect(),rt=th.getBoundingClientRect();
   return {a:a.textContent,b:b.textContent.replace(' / ',''),la:lines(a),lb:lines(b),below:rb.top>=ra.bottom-1,
     dotIn:rd.left>=rt.left&&rd.right<=rt.right,dotMid:Math.abs((rd.top+rd.bottom)/2-(ra.top+rb.bottom)/2)<4,
     ctr:getComputedStyle(th).textAlign}});
 const other=[...t.querySelectorAll('thead th:not(.szh)')].filter(th=>th.textContent.trim()).map(th=>({t:th.textContent,n:Math.round(th.querySelector('br')?th.getBoundingClientRect().height:0),
   lines:(()=>{const r=document.createRange();r.selectNodeContents(th);return new Set([...r.getClientRects()].map(x=>Math.round(x.top))).size})(),br:th.querySelectorAll('br').length}));
 const vals=[...t.querySelectorAll('tbody td.szv')].map(td=>({c:getComputedStyle(td).textAlign,l:lines(td)}));
 const ths=[...t.querySelectorAll('thead th')].map(th=>th.getBoundingClientRect());
 return {sz,other,vals,sameBottom:new Set(ths.map(r=>Math.round(r.bottom))).size==1,
   scroll:w.scrollWidth>w.clientWidth,ovx:getComputedStyle(w).overflowX,docOver:document.documentElement.scrollWidth>innerWidth+1,
   minW:Math.min(...[...t.querySelectorAll('th.szh')].map(th=>th.getBoundingClientRect().width)),fs:parseFloat(getComputedStyle(t.querySelector('td.szv')).fontSize)}}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw,th,fs in [(1440,'light',None),(1440,'dark',None),(820,'light',None),(390,'light',None),(1440,'light','20')]:
        tag=f'{vw}px {th}'+(f' texto {fs}px' if fs else '')
        pg=b.new_page(viewport={'width':vw,'height':900});errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:m.type=='error' and errs.append(m.text))
        pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',SEED)
        pg.evaluate(f"localStorage.setItem('propesa-theme','{th}')")
        if fs:pg.evaluate(f"localStorage.setItem('propesa-fs','{fs}')")
        pg.reload();pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]');pg.evaluate("go('recepcion')")
        m=pg.evaluate(MEDIR)
        chk([s['a'] for s in m['sz']]==PRI and [s['b'] for s in m['sz']]==SEC,f'{tag}: rango principal arriba y secundario abajo')
        chk(all(s['la']==1 and s['lb']==1 and s['below'] for s in m['sz']),f'{tag}: cada rango en un solo renglón, sin números partidos')
        chk(all(s['dotIn'] and s['dotMid'] for s in m['sz']),f'{tag}: punto de color junto a su talla')
        chk(all(s['ctr']=='center' for s in m['sz']) and all(v['c']=='center' and v['l']==1 for v in m['vals']),f'{tag}: tallas centradas y valores en un renglón')
        chk(all(o['lines']<=o['br']+1 for o in m['other']),f'{tag}: otros encabezados sin cortes de más '+str([o['t'] for o in m['other'] if o['lines']>o['br']+1]))
        chk(m['sameBottom'],f'{tag}: encabezados alineados abajo')
        chk(m['ovx']=='auto' and not m['docOver'],f'{tag}: se desliza dentro de la tarjeta, la página no se desborda')
        chk(m['fs']>=15 if not fs else m['fs']>=20,f'{tag}: no se achicó la letra ({m["fs"]}px)')
        chk(not errs,f'{tag}: sin errores en consola {errs}')
        pg.close()
    b.close()
