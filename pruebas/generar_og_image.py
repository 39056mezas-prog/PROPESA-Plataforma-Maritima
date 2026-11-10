"""PROPESA · genera og-image.png (1200×630): la vista previa al compartir el link de la app (WhatsApp, Facebook, Slack…).
Logo PROPESA en blanco (el mismo LG de la app, versión LOGOD) y «Procesos y Operaciones» sobre azul marino #0B1D59.
Si cambia, sube ?v= en las etiquetas og:image / twitter:image de index.html (las apps guardan la vista vieja varios días).
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/generar_og_image.py"""
import os
from playwright.sync_api import sync_playwright
from PIL import Image
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1200, 'height': 630})
    pg.goto(BASE); pg.wait_for_timeout(400)
    logo = pg.evaluate("LOGOD")
    pg.set_content(f"""<!doctype html><html><head><meta charset="utf-8"><style>
      html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
      body{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;
        background:radial-gradient(ellipse at 50% 30%,#14307a 0%,#0B1D59 55%,#08164a 100%);
        font-family:system-ui,-apple-system,"Segoe UI",Roboto,Inter,sans-serif}}
      svg{{width:620px;height:auto;color:#fff}} .lg path{{fill:#fff!important}} .lg .wm{{stroke:#fff!important}}
      p{{margin:0;color:#cfe0ff;font-size:34px;font-weight:600;letter-spacing:.2px}}
    </style></head><body>{logo}<p>Procesos y Operaciones</p></body></html>""")
    pg.wait_for_timeout(200)
    tmp = os.path.join(RAIZ, 'pruebas', '_og_tmp.png'); pg.screenshot(path=tmp); b.close()
im = Image.open(tmp).convert('RGB'); os.remove(tmp)
out = os.path.join(RAIZ, 'og-image.png'); im.quantize(colors=256, method=Image.Quantize.MEDIANCUT).save(out, optimize=True)
print('og-image.png', os.path.getsize(out) // 1024, 'KB', im.size)
