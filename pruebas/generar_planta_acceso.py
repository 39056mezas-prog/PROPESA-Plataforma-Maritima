"""PROPESA · genera acceso-planta.png: la planta 3D de la pantalla de acceso, ya dibujada (v1.38.3; v1.43.0 con tinas).
En la pantalla de acceso la planta es solo un dibujo de muestra (aria-hidden, no se toca): una sola imagen, para no cargar el
celular. Se dibuja con el mismo lienzo de la app (t3Inner + t3Draw) y las tinas de ejemplo de mkScene; las etiquetas
«T1 · 9 tinas» siguen siendo texto encima (mkMount). Si cambia el dibujo de la planta (t3Inner, t3Draw, T3P, MKT),
corre esto otra vez y copia la línea MKI que imprime en index.html.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/generar_planta_acceso.py"""
import os, json
from playwright.sync_api import sync_playwright
from PIL import Image
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R0 = (1000, 560); DPR = 2
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1400, 'height': 900}, device_scale_factor=DPR)
    pg.goto(BASE); pg.wait_for_selector('.mkp', state='attached'); pg.wait_for_timeout(300)
    s0 = pg.evaluate("""([W,H])=>{
      document.getElementById('app').style.display='none';
      document.documentElement.style.background=document.body.style.background='transparent';
      const v=document.createElement('div');v.className='t3v';v.id='cap';
      v.style.cssText='position:fixed;left:0;top:0;width:'+W+'px;height:'+H+'px;background:none!important;border:0!important;border-radius:0!important;box-shadow:none!important;z-index:99999';
      const cv=document.createElement('canvas');cv.className='t3cv';cv.style.cssText='width:100%;height:100%;display:block';v.appendChild(cv);document.body.appendChild(v);
      MKS=null;const Q=mkScene();
      const g=t3Fit(0,0,T3P.W,T3P.D,300,.97,{width:W,height:H},35,57);
      const keep={};['D','all','zoom','pick','M','az','ax','s','px','py','ox','oy'].forEach(k=>keep[k]=T3[k]);
      const K=['D','all','zoom','pick','labs','cs','az','M'];
      Object.assign(T3,{all:false,zoom:false,pick:null,cs:{},az:35});
      // la misma escena de ejemplo de mkScene (tinas de colores)
      const out={},occ=new Map();TK.forEach(t=>{const ns=tnOf(t);let k=0;(MKT[t]||[]).forEach(([c,d])=>c.forEach((n,i)=>{let left=n?n*MKG-(n>3?6000:0):0;while(left>0&&k<ns.length){const q=Math.min(34000,left),tn=ns[k++];left-=q;occ.set(tn,{n:tn,g:q,d,u:null,mq:0,lot:'',col:MKC[i]||'#fff'})}}))});
      T3.D={occ,vis:new Set([0])};t3Inner();Object.assign(T3,g);t3Draw();
      return g.s}""", list(R0))
    pg.wait_for_timeout(300)
    tmp = os.path.join(RAIZ, 'pruebas', '_planta_tmp.png')
    pg.locator('#cap canvas').screenshot(path=tmp, omit_background=True)
    b.close()
im = Image.open(tmp).convert('RGBA'); os.remove(tmp)
x0, y0, x1, y1 = im.getbbox()
x0, y0 = max(0, x0 - 2), max(0, y0 - 2); x1, y1 = min(im.width, x1 + 2), min(im.height, y1 + 2)
im = im.crop((x0, y0, x1, y1))
q = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
out = os.path.join(RAIZ, 'acceso-planta.png'); q.save(out, optimize=True)
MKI = {'x': round(x0 / DPR, 2), 'y': round(y0 / DPR, 2), 'w': round(im.width / DPR, 2), 'h': round(im.height / DPR, 2), 'W': R0[0], 'H': R0[1], 's': round(s0, 6)}
print('acceso-planta.png', os.path.getsize(out) // 1024, 'KB', im.size)
print('const MKI=' + json.dumps(MKI, separators=(',', ':')) + ';')
