"""v1.37.0 · iPad viejo (/impeccable adapt, 5/nov/2026). El usuario: «se va a usar sobre todo en un iPad mini viejo».
Como no sabía el modelo, se pidió que funcione desde el más viejo posible: iPad mini 2/3 con iOS 12 (Safari 12).
Chromium no es Safari 12, así que esta prueba lo simula:
  · window.CPX_SIM: la capa de compatibilidad actúa como si el navegador no conociera @container, :has, :is,
    :focus-visible, clamp() ni gap en flex.
  · gap en flex apagado de verdad (como en Safari < 14.1) y las declaraciones con color-mix() quitadas (Safari < 16.2).
  · sin Pointer Events (Safari < 13): los toques llegan solo como touchstart/touchend.
Compara cada pantalla contra la versión moderna en 768×1024 y 1024×768 (iPad mini vertical y horizontal).
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/ipad_viejo_t.py"""
from playwright.sync_api import sync_playwright
import os, re, json, io
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
AQUI = os.path.dirname(os.path.abspath(__file__))
seed = open(os.path.join(AQUI, 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

# ---------- 1. Código que Safari 12 sí entiende ----------
html = open(os.path.join(AQUI, '..', 'index.html'), encoding='utf8').read()
js = '\n'.join(re.findall(r'<script>([\s\S]*?)</script>', html))
sin_coment = re.sub(r'/\*[\s\S]*?\*/', '', js)
for nom, pat in [('??', r'\?\?'), ('?.', r'\?\.(?=[A-Za-z_$\[(])'), ('??= ||= &&=', r'(\?\?=|\|\|=|&&=)'), ('.at(', r'\.at\('), ('replaceAll', r'\.replaceAll\('),
                 ('structuredClone', r'structuredClone\('), ('Object.hasOwn', r'Object\.hasOwn\('), ('findLast', r'\.findLast(Index)?\('), ('toSorted', r'\.to(Sorted|Reversed|Spliced)\('),
                 ('Promise.allSettled', r'allSettled'), ('dateStyle', r'dateStyle'), ('a.download sin saveBlob', r'\.download=')]:
    n = len(re.findall(pat, sin_coment))
    if nom == 'a.download sin saveBlob': n -= 1  # el único está dentro de saveBlob()
    chk(n == 0, f'JS: sin «{nom}» (Safari de iOS 12 no lo entiende y deja la app en blanco o falla): {n}')
css = re.search(r'<style>([\s\S]*?)</style>', html).group(1)
pre = re.findall(r'(?<=[{;])\s*(?!--)([-\w]+):([^;{}]*color-mix\([^;{}]*)', css)
fb_ok = all(re.search(re.escape(p) + r':[^;{}]*var\(--cm-[^;{}]*;' + re.escape(p) + ':' + re.escape(v), css) for p, v in pre)
chk(fb_ok and len(pre) >= 35, f'CSS: cada color-mix() lleva antes un color fijo (--cm-…) para Safari < 16.2 ({len(pre)} declaraciones)')
cp = re.findall(r'(--[\w-]+):color-mix\(', css)
chk(all(re.search(r'@supports not \(color:color-mix\(in srgb,red,red\)\)\{[^}]*' + re.escape(c) + r':var\(--cm-', css) for c in cp), f'CSS: variables con color-mix() tienen su respaldo en @supports not ({len(cp)})')
usados = set(re.findall(r'var\((--cm-[\w-]+)\)', css)) - {'--cm-zc-13-cd', '--cm-zc-22-cd'}
chk(all(re.search(re.escape(u) + r':(#|rgba)', css) for u in usados), f'CSS: todas las variables --cm-… tienen valor ({len(usados)})')
chk(not re.search(r'(?<![-\w])inset:', css), 'CSS: sin «inset:» (Safari < 14.1); se usa top/right/bottom/left')
chk(css.count('position:sticky') == css.count('position:-webkit-sticky'), 'CSS: position:sticky con prefijo -webkit- (Safari 12)')

# ---------- 2. Simulación de Safari 12 ----------
SIM = r'''window.CPX_SIM=1;
(function(){var g=window.getComputedStyle.bind(window);
 function z(el,cs){if(el.__sg||(cs.display!=='flex'&&cs.display!=='inline-flex'))return;var c=cs.columnGap,r=cs.rowGap;if((c==='normal'||c==='0px')&&(r==='normal'||r==='0px'))return;el.__sg={c:c,r:r};el.style.setProperty('column-gap','0px','important');el.style.setProperty('row-gap','0px','important')}
 function sim(){document.querySelectorAll('*').forEach(function(el){z(el,g(el))})}
 window.getComputedStyle=function(el,p){var cs=g(el,p);if(el&&!p&&el.nodeType==1)z(el,cs);if(!el||!el.__sg||p)return cs;return new Proxy(cs,{get:function(t,k){if(k==='columnGap')return el.__sg.c;if(k==='rowGap')return el.__sg.r;var v=t[k];return typeof v==='function'?v.bind(t):v}})};
 new MutationObserver(sim).observe(document,{childList:true,subtree:true,attributes:true,attributeFilter:['class','data-cq','data-h']});
 document.addEventListener('DOMContentLoaded',function(){sim();document.documentElement.classList.remove('lite')});
})();'''
NOPTR = r'''delete window.PointerEvent;['pointerdown','pointermove','pointerup','pointercancel'].forEach(function(t){window.addEventListener(t,function(e){if(e.isTrusted)e.stopImmediatePropagation()},true)});'''
def strip_cm(h):
    def f(m):
        c = re.sub(r'(?<=[{;])\s*(?!--)[-\w]+\s*:[^;{}]*color-mix\([^;{}]*;?', '', m.group(1))
        return '<style>' + c.replace('@supports not (color:color-mix(in srgb,red,red))', '@supports (display:block)') + '</style>'
    return re.sub(r'<style>([\s\S]*?)</style>', f, h)
def ctx(b, W, H, viejo, extra='', ua=None):
    c = b.new_context(viewport={'width': W, 'height': H}, has_touch=True, device_scale_factor=1, **({'user_agent': ua} if ua else {}))
    if viejo:
        c.add_init_script(SIM + extra)
        def r(rt):
            resp = rt.fetch(); rt.fulfill(response=resp, body=strip_cm(resp.text()), headers={**resp.headers, 'content-type': 'text/html; charset=utf-8'})
        c.route(re.compile(r'.*/index\.html.*'), r)
    pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(('viejo ' if viejo else '') + str(e)))
    return pg
def entrar(pg, piso='0', s=seed, em='admin@propesa.mx', pw='x'):
    pg.goto(BASE)
    pg.evaluate('([s,p])=>{localStorage.clear();sessionStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso",p);localStorage.setItem("propesa-inst",String(Date.now()));localStorage.setItem("propesa-3d","1")}', [s, piso])
    pg.reload(); pg.wait_for_timeout(300)
    if pg.query_selector('#le'): pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(400)
def foto(pg):
    pg.wait_for_timeout(250); return pg.screenshot()
def dif(a, b):
    """% de pixeles distintos (umbral 24/255) entre dos capturas del mismo tamaño."""
    from PIL import Image, ImageChops
    A, B = Image.open(io.BytesIO(a)).convert('RGB'), Image.open(io.BytesIO(b)).convert('RGB')
    if A.size != B.size: return 100.0
    d = ImageChops.difference(A, B).convert('L').point(lambda v: 255 if v > 24 else 0)
    return 100 * d.histogram()[255] / (A.width * A.height)
PANT = ['formatos', 'recepcion', 'lote:WLRCO051026A', 'ordenes', 'orden:1', 'empaque', 'embarques', 'emb:0', 'temperatura', 'general', 'hojas', 'admin', 'admin:usr', 'cierre']
PISO = ['piso', 'rtin', 'pcer', 'pcon']

with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------- 3. Cada pantalla se ve igual que en un navegador nuevo ----------
    for W, H in [(768, 1024), (1024, 768)]:
        nuevo, viejo = ctx(b, W, H, False), ctx(b, W, H, True)
        for pg in (nuevo, viejo): entrar(pg)
        chk(viejo.evaluate('CPX.need&&CPX.nogap&&CPX.CQ.length>=6&&CPX.HAS.length>=4'), f'{W} simulación activa: @container ({viejo.evaluate("CPX.CQ.length")}), :has ({viejo.evaluate("CPX.HAS.length")}) y gap reescritos')
        chk(nuevo.evaluate('!CPX.need&&CPX.nogap===false&&!document.querySelector("[data-cq],[data-h],.nogap,.lite")'), f'{W} navegador nuevo: la capa de compatibilidad no toca nada')
        for grupo, piso in [(PANT, '0'), (PISO, '1')]:
            if piso == '1':
                for pg in (nuevo, viejo): entrar(pg, '1')
            for r in grupo:
                d = []
                for pos in (0, 1):
                    fs = []
                    for pg in (nuevo, viejo):
                        pg.evaluate(f"go('{r}')"); pg.wait_for_timeout(250)
                        pg.evaluate("document.querySelectorAll('details.fold').forEach(d=>{FOLD[d.dataset.fold]=true});render()"); pg.wait_for_timeout(250)
                        pg.evaluate("f=>{[document.scrollingElement,...document.querySelectorAll('main,.pshell,#app,.pw')].filter(e=>e&&e.scrollHeight>e.clientHeight+4).forEach(e=>e.scrollTop=(e.scrollHeight-e.clientHeight)*f)}", pos)
                        fs.append(foto(pg))
                    d.append(dif(*fs))
                chk(max(d) < 1, f'{W}×{H} {r}: igual que en un navegador nuevo (diferencia arriba {d[0]:.1f}%, abajo {d[1]:.1f}%)')
        nuevo.context.close(); viejo.context.close()

    # ---------- 4. Teclado de piso con toques, sin Pointer Events ----------
    s2 = json.loads(seed); s2['OR'].append({'id': 3, 'etd': '2026-10-14', 'lines': [{'id': 1, 'city': 'HKG', 'cons': 0, 'cli': 'LHD', 'boxes': 6}], 'sh': {}}); s2 = json.dumps(s2)
    def tap(pg, sel):
        r = pg.evaluate("s=>{const e=document.querySelector(s);e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}", sel); pg.touchscreen.tap(r[0], r[1]); pg.wait_for_timeout(120)
    for W, H in [(768, 1024), (1024, 768)]:
        fs = []
        for viejo in (False, True):
            pg = ctx(b, W, H, viejo, NOPTR)
            entrar(pg, '0', s2, 'piso@propesa.mx', 'piso123'); pg.evaluate("go('pemp:3.1')"); pg.wait_for_timeout(300)
            tap(pg, '[data-pe="lot:WLRCO061026B"]'); pg.wait_for_timeout(300)
            for c in '12': tap(pg, f'#kpad [data-kp="d:{c}"]')
            tap(pg, '#kpad [data-kp="k:R"]'); tap(pg, '#kpad [data-kp="d:9"]')
            st = json.loads(pg.evaluate("localStorage.getItem('propesa-v4')"))
            bx = [(x.get('ps'), x['c'], x['k']) for v in st['B'].values() for x in v if x['o'] == '3.1']
            if viejo:
                chk(not pg.evaluate('!!window.PointerEvent'), f'{W} sin Pointer Events (como iOS 12)')
                chk(bx == [(1, 12, 'R')] and pg.inner_text('#kpv') == '9', f'{W} teclado de piso con toques: hielera 1 guardada (12 Rojo) y la 2 en captura: {bx}, {pg.inner_text("#kpv")}')
            pg.evaluate("document.querySelectorAll('main,.pshell').forEach(e=>e.scrollTop=0)"); fs.append(foto(pg)); pg.context.close()
        chk(dif(*fs) < 1, f'{W} teclado de piso: se ve igual que en un navegador nuevo ({dif(*fs):.1f}%)')

    # ---------- 5. Descargas en iOS 12 (no conoce «download»): el PDF se abre en otra pestaña ----------
    UA12 = 'Mozilla/5.0 (iPad; CPU OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1'
    pg = ctx(b, 768, 1024, True, '', UA12); entrar(pg)
    chk(pg.evaluate('CPX.oldIOS'), 'iOS 12 reconocido por el navegador')
    pg.evaluate("go('hojas')"); pg.wait_for_timeout(300)
    pg.evaluate("window.__wo=[];window.open=function(u,t){window.__wo.push([String(u),t]);return {}};0")
    pg.click('[data-pdf^="dl:"] >> nth=0'); pg.wait_for_timeout(800)
    wo = pg.evaluate('window.__wo')
    chk(len(wo) == 1 and wo[0][0].startswith('blob:') and wo[0][1] == '_blank', f'iOS 12: el PDF se abre en otra pestaña en vez de reemplazar la app ({wo})')
    chk(pg.url.startswith('http') and pg.locator('#dlnow').count() == 0, 'iOS 12: la app sigue abierta en su pestaña')
    # si Safari bloquea la pestaña, sale un botón «Abrir …» que sí la abre con el toque del usuario
    pg.evaluate("window.open=()=>null;0"); pg.evaluate("go('hojas')"); pg.wait_for_timeout(200)
    pg.click('[data-pdf^="dl:"] >> nth=0')
    pg.wait_for_timeout(600)
    chk(pg.locator('#dlnow').count() == 1 and pg.get_attribute('#dlnow', 'target') == '_blank' and 'Abrir' in pg.inner_text('#dlnow'), 'iOS 12 con la pestaña bloqueada: botón «Abrir …» para abrir el archivo')
    r = pg.evaluate("(()=>{const r=document.getElementById('dlnow').getBoundingClientRect();return [r.height,r.left>=0&&r.right<=innerWidth]})()")
    chk(r[0] >= 44 and r[1], f'el botón «Abrir …» es fácil de tocar y cabe en la pantalla ({r})')
    pg.context.close()

    # ---------- 6. Equipo viejo: sin vidrio esmerilado (caro en un procesador viejo) ----------
    pg = ctx(b, 768, 1024, True, 'document.addEventListener("DOMContentLoaded",function(){setTimeout(function(){document.documentElement.classList.add("lite")},0)});'); entrar(pg); entrar(pg, '1')
    pg.evaluate("go('piso')"); pg.wait_for_timeout(300)
    bf = pg.evaluate("getComputedStyle(document.querySelector('.phd')).backdropFilter")
    chk(bf in ('none', ''), f'equipo viejo: el encabezado de Modo piso sin desenfoque ({bf})')
    pg.context.close()
    LITE = 'document.addEventListener("DOMContentLoaded",function(){setTimeout(function(){document.documentElement.classList.add("lite")},0)});'
    pg = ctx(b, 768, 1024, True, LITE, UA12); entrar(pg); pg.evaluate("localStorage.removeItem('propesa-3d')"); pg.reload(); pg.wait_for_timeout(400)
    pg.evaluate("go('general')"); pg.wait_for_timeout(300)
    chk(pg.evaluate("document.documentElement.classList.contains('lite')") and pg.locator('[data-t3a=on]').count() >= 1 and pg.locator('.t3v').count() == 0, 'iPad viejo: la planta 3D empieza apagada, con el botón «Ver tanques en 3D»')
    pg.click('[data-t3a=on] >> nth=0'); pg.wait_for_timeout(400)
    chk(pg.locator('.t3v').count() >= 1 and pg.evaluate("localStorage.getItem('propesa-3d')") == '1', 'iPad viejo: «Ver tanques en 3D» la prende y se recuerda')
    pg.context.close()

    # ---------- 7. Lo que tarda la capa de compatibilidad (CPU 4× más lento) ----------
    pg = ctx(b, 768, 1024, True); entrar(pg)
    cdp = pg.context.new_cdp_session(pg); cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    t = pg.evaluate("""()=>{const o={};for(const r of ['recepcion','orden:1','general']){go(r);const a=[];for(let i=0;i<3;i++){const s=performance.now();CPX.pass();a.push(performance.now()-s)}o[r]=Math.round(Math.min(...a))}return o}""")
    chk(max(t.values()) <= 120, f'la capa de compatibilidad tarda poco en cada pantalla (CPU 4×): {t} ms (límite 120)')
    pg.context.close()
    b.close()

chk(not errs, f'sin errores en la página: {errs[:3]}')
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} fallas')
import sys; sys.exit(1 if fails else 0)
