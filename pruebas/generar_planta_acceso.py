"""PROPESA · genera acceso-planta.png: la planta 3D de la pantalla de acceso, ya dibujada (v1.38.3).
En la pantalla de acceso la planta es solo un dibujo de muestra (aria-hidden, no se toca). Dibujada en vivo con CSS 3D
eran ~300 capas de la tarjeta gráfica: en celulares con poca memoria Chrome no alcanzaba a pintar el resto de la
pantalla (se veía gris hasta mover la pantalla). Ahora es una sola imagen; las etiquetas «T1 · 48 canastas» siguen
siendo texto encima (mkMount). Si cambia el dibujo de la planta (t3Inner, T3P, MKT), corre esto otra vez y copia
la línea MKI que imprime en index.html.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/generar_planta_acceso.py"""
import os, json
from playwright.sync_api import sync_playwright
from PIL import Image
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R0 = (1000, 560); DPR = 2
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROME') or None, args=['--use-gl=swiftshader', '--ignore-gpu-blocklist'])
    pg = b.new_page(viewport={'width': 1400, 'height': 900}, device_scale_factor=DPR)
    pg.goto(BASE); pg.wait_for_selector('.mkp .t3w', state='attached'); pg.wait_for_timeout(500)
    s0 = pg.evaluate("""([W,H])=>{
      const st=document.querySelector('.mkp .t3st'),w=st.querySelector('.t3w');
      const mk=document.createElement('div');mk.className='mk';mk.id='cap';
      mk.style.cssText='position:fixed;left:0;top:0;width:'+W+'px;height:'+H+'px;background:none!important;box-shadow:none!important;border:0!important;font-size:10px;z-index:99999';
      const v=document.createElement('div');v.className='mkp';v.style.cssText='position:absolute;left:0;top:0;width:'+W+'px;height:'+H+'px;background:none!important;border:0!important;border-radius:0!important';
      mk.appendChild(v);v.appendChild(st);document.body.appendChild(mk);
      document.getElementById('app').style.display='none';
      document.documentElement.style.background=document.body.style.background='transparent';
      const r={width:W,height:H},g=t3Fit(0,0,T3P.W,T3P.D,300,.97,r,35,57),PP=Math.round(9000*g.s+3000),A=g.az*Math.PI/180;
      st.style.perspective=PP+'px';
      w.style.transform=`translate(${W/2}px,${H/2}px) scale(${g.s}) translate(${g.ox}px,${g.oy}px) rotateX(${g.ax}deg) rotateZ(${g.az}deg) translate(${-g.px}px,${-g.py}px)`;
      const vx=Math.sin(A),vy=Math.cos(A),off=k=>(k=='s'&&vy>.2)||(k=='n'&&vy<-.2)||(k=='e'&&vx>.2)||(k=='w'&&vx<-.2);
      w.querySelectorAll('.t3g[data-w]').forEach(e=>e.hidden=off(e.dataset.w));
      return g.s}""", list(R0))
    pg.wait_for_timeout(800)
    tmp = os.path.join(RAIZ, 'pruebas', '_planta_tmp.png')
    pg.locator('#cap').screenshot(path=tmp, omit_background=True)
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
