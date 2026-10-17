"""Vista previa al compartir el link (v1.8.6): etiquetas og:/twitter: en index.html y la imagen og-image.png.
No necesita navegador ni servidor. Uso: python3 -I pruebas/vista_previa_t.py"""
import os, re, sys, struct
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
h = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
head = h[:h.index('</head>')] if '</head>' in h else h[:h.index('<style>')]
meta = {m.group(1): m.group(2) for m in re.finditer(r'<meta (?:property|name)="((?:og|twitter):[a-z_:]+)" content="([^"]*)"', head)}
for k in ['og:type', 'og:title', 'og:description', 'og:url', 'og:image', 'og:image:width', 'og:image:height', 'og:image:alt', 'twitter:card', 'twitter:image']:
    chk(meta.get(k), f'tiene {k}: {meta.get(k)}')
img = meta.get('og:image', '')
chk(img.startswith('https://') and meta.get('twitter:image') == img, 'la imagen va con dirección completa https (WhatsApp y Facebook no aceptan rutas relativas)')
chk(meta.get('og:url', '').rstrip('/') == img.split('/og-image')[0], 'og:url y la imagen apuntan al mismo sitio')
chk(meta.get('twitter:card') == 'summary_large_image', 'tarjeta grande en X/Twitter')
f = os.path.join(ROOT, 'og-image.png')
chk(os.path.exists(f), 'og-image.png existe en la carpeta del sitio')
b = open(f, 'rb').read()
w, ht = struct.unpack('>II', b[16:24])
chk(b[:8] == b'\x89PNG\r\n\x1a\n' and (w, ht) == (1200, 630) and meta.get('og:image:width') == str(w) and meta.get('og:image:height') == str(ht), f'og-image.png es PNG de 1200×630 y coincide con las etiquetas ({w}×{ht})')
chk(len(b) < 300_000, f'pesa menos de 300 KB, el límite de WhatsApp ({len(b)//1024} KB)')
chk('mortalidad final' not in meta.get('og:description', '').lower(), 'la descripción ya no presenta Mortalidad final como paso del flujo')
# --- Ícono de la app en alta resolución y pantalla de carga (v1.8.6) ---
import json
man = json.load(open(os.path.join(ROOT, 'manifest.webmanifest'), encoding='utf-8'))
def png_size(path):
    d = open(path, 'rb').read(24); return struct.unpack('>II', d[16:24])
ics = man.get('icons', [])
for ic in ics:
    fp = os.path.join(ROOT, ic['src'].split('?')[0].lstrip('/')); sz = ic['sizes'].split('x')
    chk(os.path.exists(fp) and png_size(fp) == (int(sz[0]), int(sz[1])), f"ícono {ic['src']} ({ic['purpose']}) existe y mide {ic['sizes']}")
big = [ic for ic in ics if int(ic['sizes'].split('x')[0]) >= 1024]
chk({ic['purpose'] for ic in big} >= {'any', 'maskable'}, 'hay ícono de 1024 px normal y maskable (Android ya no estira el de 512 en la pantalla de inicio)')
chk(man.get('background_color', '').lower() == '#0b1d59' and man.get('theme_color', '').lower() == '#0b1d59', 'fondo de la pantalla de inicio de Android = azul marino de la pantalla de carga')
vs = set(re.findall(r'\?v=(\d+)', json.dumps(man))) | set(re.findall(r'(?:favicon\.svg|apple-touch-icon\.png|manifest\.webmanifest)\?v=(\d+)', head))
chk(len(vs) == 1, f'todos los íconos y el manifiesto con la misma versión ?v= ({vs})')
bt = re.search(r'<div id="boot"[^>]*>(.*?)</div>', h, re.S)
chk(bt and '<svg' in bt.group(1) and 'aria-hidden="true"' in bt.group(1), 'pantalla de carga con el logo de PROPESA dentro del HTML (se pinta antes que el código)')
chk(bt and h.index('<div id="boot"') < h.index('<div id="app"') and '#boot{' in h[:h.index('</head>')], 'va antes de la app y su estilo está en el encabezado')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 412, 'height': 915}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local'))
    pg.wait_for_function("!document.getElementById('boot')", timeout=5000)
    chk(pg.locator('#le, #s0n').count() >= 1 and not errs, 'la pantalla de carga se quita sola y queda la app (acceso)')
    b.close()
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
