# v1.55.2 · Auditoría de seguridad: la CSP ya no deja correr cualquier <script> en línea ('unsafe-inline'), solo los 4 bloques de
# index.html, por su huella (sha256). Si alguien cambia un <script> de index.html, la huella cambia y en Vercel la app se quedaría
# en blanco: por eso esta prueba.
#   python3 -I pruebas/csp_hashes.py            → revisa que vercel.json tenga las huellas de index.html («TODO BIEN» o «FALLAS»)
#   python3 -I pruebas/csp_hashes.py --escribir → pone en vercel.json las huellas actuales (correr SIEMPRE después de cambiar index.html)
import base64, hashlib, json, os, re, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(RAIZ, 'index.html'), encoding='utf-8').read()
bloques = re.findall(r'<script>([\s\S]*?)</script>', html)
huellas = ["'sha256-" + base64.b64encode(hashlib.sha256(b.encode('utf-8')).digest()).decode() + "'" for b in bloques]
ruta = os.path.join(RAIZ, 'vercel.json')
cfg = json.load(open(ruta, encoding='utf-8'))
csp = next(h for r in cfg['headers'] for h in r['headers'] if h['key'] == 'Content-Security-Policy')
partes = [p.strip() for p in csp['value'].split(';')]
i = next(n for n, p in enumerate(partes) if p.startswith('script-src '))
nueva = "script-src 'self' " + ' '.join(huellas)
if '--escribir' in sys.argv:
    partes[i] = nueva; csp['value'] = '; '.join(partes)
    open(ruta, 'w', encoding='utf-8').write(json.dumps(cfg, indent=2, ensure_ascii=False) + '\n')
    print(f'vercel.json: {len(huellas)} huellas escritas'); sys.exit(0)
bad = []
def ok(c, t):
    print(('  ✔ ' if c else '  ✘ ') + t)
    if not c: bad.append(t)
ok(len(bloques) == html.count('<script') and len(bloques) >= 1, f'{len(bloques)} bloques <script> sin atributos en index.html')
ok("'unsafe-inline'" not in partes[i] and "'unsafe-eval'" not in partes[i], "script-src sin 'unsafe-inline' ni 'unsafe-eval'")
ok(partes[i] == nueva, 'vercel.json tiene las huellas de index.html (si no: python3 -I pruebas/csp_hashes.py --escribir)')
ok(not re.search(r'\son[a-z]+\s*=\s*["\']', html), 'index.html sin onclick= / onload= en las etiquetas (la CSP los bloquearía)')
print('TODO BIEN' if not bad else 'FALLAS'); sys.exit(1 if bad else 0)
