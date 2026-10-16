"""Tarea diaria que mantiene despierta la base (api/despierta.js + vercel.json, v1.8.0).
Corre la función con Node contra el Supabase de mentira (puerto 8792). No necesita navegador ni el servidor de la app.
Uso: python3 -I pruebas/despierta_t.py"""
import os, sys, json, time, re, subprocess, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK = 'http://127.0.0.1:8792'
fails = []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

# Llama a la función como lo hace Vercel (req/res de Node) y devuelve {status, body}.
RUN = r"""
const f=require(process.argv[1]);let st=0,body=null,h={};
const res={setHeader:(k,v)=>{h[k.toLowerCase()]=v},status(s){st=s;return this},json(b){body=b;return this}};
f({headers:{authorization:process.argv[2]||undefined}},res).then(()=>console.log(JSON.stringify({status:st,body,h})));
"""
def call(env, auth=''):
    e = dict(os.environ); e.update(env)
    out = subprocess.run(['node', '-e', RUN, os.path.join(ROOT, 'api', 'despierta.js'), auth], env=e, capture_output=True, text=True, timeout=30)
    return json.loads(out.stdout.strip().splitlines()[-1])

srv = subprocess.Popen([sys.executable, '-I', os.path.join(ROOT, 'pruebas', 'supabase_falso.py'), '8792'])
try:
    for _ in range(50):
        try: urllib.request.urlopen(urllib.request.Request(MOCK + '/__reset', data=b'{}', method='POST')); break
        except Exception: time.sleep(0.1)
    base = {'SUPABASE_URL': MOCK, 'SUPABASE_KEY': 'clave-publica-de-prueba', 'CRON_SECRET': ''}
    r = call(base); chk(r['status'] == 200 and r['body']['ok'] and r['body']['base'] == 200, f'la función consulta la base y responde 200: {r}')
    chk(r['h'].get('cache-control') == 'no-store', 'la respuesta no se guarda en caché (Vercel la registra cada día)')
    s = dict(base, CRON_SECRET='secreto-de-prueba-123')
    chk(call(s)['status'] == 401, 'con CRON_SECRET en Vercel, una llamada sin la clave no hace nada (401)')
    chk(call(s, 'Bearer secreto-de-prueba-123')['status'] == 200, 'con la clave correcta (la que manda Vercel) sí consulta')
    srv.terminate(); srv.wait()
    r = call(base); chk(r['status'] == 502 and not r['body']['ok'], f'si la base no responde, devuelve 502 (se ve en Vercel → Logs): {r["body"]}')
finally:
    if srv.poll() is None: srv.terminate()

# La dirección y la llave por omisión son las mismas de la app
src = open(os.path.join(ROOT, 'api', 'despierta.js')).read(); app = open(os.path.join(ROOT, 'index.html')).read()
m = re.search(r"url:'([^']+)',key:'([^']+)'", app)
chk(m and f"'{m.group(1)}'" in src and f"'{m.group(2)}'" in src, 'la función usa la misma base y llave pública que index.html')
# vercel.json: una vez al día (el plan Hobby rechaza más seguido) y a la ruta de la función
v = json.load(open(os.path.join(ROOT, 'vercel.json'))); cr = v.get('crons') or []
chk(len(cr) == 1 and cr[0]['path'] == '/api/despierta', f'vercel.json tiene la tarea diaria: {cr}')
f = cr[0]['schedule'].split() if cr else []
chk(len(f) == 5 and f[0].isdigit() and f[1].isdigit() and f[2:] == ['*', '*', '*'], f'se corre una vez al día (plan gratis de Vercel): {cr and cr[0]["schedule"]}')

print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
