"""Supabase de mentira para las pruebas de sincronización (solo lo que usa la app).
Uso: python3 -I pruebas/supabase_falso.py 8790
Imita: /auth/v1/token, /auth/v1/logout, /rest/v1/profiles, /rest/v1/rpc/pull, /rest/v1/rpc/push, /rest/v1/rpc/has_admin,
/functions/v1/usuarios y el espacio de archivos «fotos» (/storage/v1/object…, v1.8.0).
Reglas: consulta no puede escribir (403 / 42501); fotos: ver con perfil, subir y borrar Administrador y Piso
(igual que migrations/20261015_fotos.sql); máximo 2 MB; solo imágenes; no se sobrescribe (409).
Control para las pruebas: GET /__estado (registros y escrituras), POST /__reset."""
import json, sys, time, uuid, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

LOCK = threading.Lock()
def fresh():
    return {'users': {}, 'recs': {}, 'rev': 0, 'writes': 0, 'tokens': {}, 'refresh': {}, 'files': {}, 'file_gets': 0, 'log': []}
DB = fresh()
TOKEN_LIFE = 3600

def add_user(name, email, pw, role, notify=True):
    uid = str(uuid.uuid4())
    DB['users'][uid] = {'id': uid, 'name': name, 'email': email.lower(), 'pw': pw, 'role': role, 'notify': notify}
    return uid

def seed_users():
    add_user('Ana Torres', 'admin@propesa.mx', 'clave-admin1', 'admin')
    add_user('Beto Ruiz', 'admin2@propesa.mx', 'clave-admin2', 'admin')
    add_user('Luis Meza', 'piso@propesa.mx', 'clave-piso1', 'piso')
    add_user('Dirección', 'consulta@propesa.mx', 'clave-ver1', 'consulta', False)

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'authorization, apikey, content-type, prefer, x-client-info')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    def out(self, code, body=None):
        b = b'' if body is None else json.dumps(body).encode()
        self.send_response(code); self.cors()
        self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(b)))
        self.end_headers(); self.wfile.write(b)
    def do_OPTIONS(self):
        self.send_response(204); self.cors(); self.send_header('Content-Length', '0'); self.end_headers()
    def raw(self):
        n = int(self.headers.get('Content-Length') or 0)
        return self.rfile.read(n) if n else b''
    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(n) if n else b''
        return json.loads(raw) if raw else {}
    def who(self):
        a = self.headers.get('Authorization', '')
        t = a[7:] if a.startswith('Bearer ') else ''
        x = DB['tokens'].get(t)
        if not x or x['exp'] < time.time(): return None
        u = DB['users'].get(x['uid'])
        return u
    def session(self, u):
        at, rt = 'at-' + uuid.uuid4().hex, 'rt-' + uuid.uuid4().hex
        DB['tokens'][at] = {'uid': u['id'], 'exp': time.time() + TOKEN_LIFE}
        DB['refresh'][rt] = u['id']
        return {'access_token': at, 'refresh_token': rt, 'expires_in': TOKEN_LIFE, 'expires_at': int(time.time() + TOKEN_LIFE), 'user': {'id': u['id'], 'email': u['email']}}
    def do_GET(self):
        p = urlparse(self.path)
        with LOCK:
            if p.path == '/__estado':
                return self.out(200, {'recs': DB['recs'], 'rev': DB['rev'], 'writes': DB['writes'], 'users': list(DB['users'].values()),
                                      'files': {k: len(v[0]) for k, v in DB['files'].items()}, 'file_gets': DB['file_gets'], 'log': DB['log']})
            if p.path.startswith('/storage/v1/object/authenticated/fotos/'):
                if not self.who(): return self.out(400, {'statusCode': '403', 'error': 'Unauthorized', 'message': 'invalid jwt'})
                f = DB['files'].get(p.path[len('/storage/v1/object/authenticated/fotos/'):])
                if not f: return self.out(400, {'statusCode': '404', 'error': 'not_found', 'message': 'Object not found'})
                DB['file_gets'] += 1
                self.send_response(200); self.cors(); self.send_header('Content-Type', f[1]); self.send_header('Content-Length', str(len(f[0])))
                self.end_headers(); self.wfile.write(f[0]); return
            if p.path == '/rest/v1/profiles':
                if not self.who(): return self.out(401, {'message': 'JWT expired'})
                us = sorted(DB['users'].values(), key=lambda u: u['name'])
                return self.out(200, [{k: u[k] for k in ('id', 'name', 'email', 'role', 'notify')} for u in us])
        self.out(404, {'message': 'no'})
    def do_DELETE(self):
        p = urlparse(self.path); b = self.body()
        with LOCK:
            u = self.who()
            if p.path != '/storage/v1/object/fotos': return self.out(404, {'message': 'no'})
            if not u: return self.out(400, {'statusCode': '403', 'error': 'Unauthorized', 'message': 'invalid jwt'})
            if u['role'] not in ('admin', 'piso'): return self.out(200, [])   # la regla no deja ver/borrar: Storage responde lista vacía
            gone = [k for k in b.get('prefixes', []) if DB['files'].pop(k, None)]
            return self.out(200, [{'name': k} for k in gone])
    def do_POST(self):
        p = urlparse(self.path); q = parse_qs(p.query)
        if p.path.startswith('/storage/v1/object/fotos/'):
            data = self.raw()
            with LOCK:
                u = self.who(); k = p.path[len('/storage/v1/object/fotos/'):]; ct = self.headers.get('Content-Type', '')
                if DB.get('falla_fotos'): return self.out(500, {'statusCode': '500', 'error': 'internal', 'message': 'storage caído'})
                if not u: return self.out(400, {'statusCode': '403', 'error': 'Unauthorized', 'message': 'invalid jwt'})
                if u['role'] not in ('admin', 'piso') or not k.startswith('notas/'):
                    return self.out(400, {'statusCode': '403', 'error': 'Unauthorized', 'message': 'new row violates row-level security policy'})
                if ct not in ('image/jpeg', 'image/png', 'image/webp', 'image/gif'): return self.out(400, {'statusCode': '415', 'error': 'invalid_mime_type', 'message': 'mime type not supported'})
                if len(data) > 2 * 1024 * 1024: return self.out(413, {'statusCode': '413', 'error': 'Payload too large', 'message': 'The object exceeded the maximum allowed size'})
                if k in DB['files']: return self.out(400, {'statusCode': '409', 'error': 'Duplicate', 'message': 'The resource already exists'})
                DB['files'][k] = (data, ct); DB['log'].append('archivo ' + k); return self.out(200, {'Key': 'fotos/' + k, 'Id': str(uuid.uuid4())})
        b = self.body()
        if p.path == '/rest/v1/rpc/push' and DB.get('lento'): time.sleep(DB['lento'])   # internet lento (fuera del candado)
        with LOCK:
            if p.path == '/__lento':      # cada subida tarda 2 s (se llama otra vez para quitarlo)
                DB['lento'] = 0 if DB.get('lento') else 2; return self.out(200, {'ok': True})
            if p.path == '/__reset':
                DB.clear(); DB.update(fresh()); seed_users(); return self.out(200, {'ok': True})
            if p.path == '/__sin_usuarios':  # base recién creada: sin Administrador
                DB['users'].clear(); return self.out(200, {'ok': True})
            if p.path == '/__sin_admins':    # alguien borró a los Administradores desde el panel; quedan otras cuentas
                for k in [k for k, x in DB['users'].items() if x['role'] == 'admin']: del DB['users'][k]
                return self.out(200, {'ok': True})
            if p.path == '/__falla_fotos':  # el espacio de archivos falla con 500 (se llama otra vez para quitarlo)
                DB['falla_fotos'] = not DB.get('falla_fotos'); return self.out(200, {'ok': True})
            if p.path == '/__falla_push':  # la base rechaza lo que sube piso (se llama otra vez para quitarlo)
                DB['falla_push'] = not DB.get('falla_push'); return self.out(200, {'ok': True})
            if p.path == '/__expira':     # vence todos los tokens (para probar la renovación)
                for t in DB['tokens'].values(): t['exp'] = 0
                return self.out(200, {'ok': True})
            if p.path == '/auth/v1/token':
                g = q.get('grant_type', [''])[0]
                if g == 'password':
                    u = next((u for u in DB['users'].values() if u['email'] == str(b.get('email', '')).lower()), None)
                    if not u or u['pw'] != b.get('password'):
                        return self.out(400, {'error': 'invalid_grant', 'error_code': 'invalid_credentials', 'msg': 'Invalid login credentials'})
                    return self.out(200, self.session(u))
                if g == 'refresh_token':
                    uid = DB['refresh'].pop(b.get('refresh_token'), None)
                    if not uid or uid not in DB['users']:
                        return self.out(400, {'error': 'invalid_grant', 'error_code': 'refresh_token_not_found', 'msg': 'Invalid Refresh Token'})
                    return self.out(200, self.session(DB['users'][uid]))
                return self.out(400, {'msg': 'grant'})
            if p.path == '/auth/v1/logout':
                return self.out(204)
            if p.path == '/rest/v1/rpc/has_admin':
                return self.out(200, any(u['role'] == 'admin' for u in DB['users'].values()))
            u = self.who()
            if p.path == '/functions/v1/usuarios':
                return self.fn(b, u)
            if not u: return self.out(401, {'message': 'JWT expired'})
            if p.path == '/rest/v1/rpc/pull':
                since, lim = int(b.get('since', 0)), int(b.get('lim', 500))
                now = time.time()
                rows = sorted((r for r in DB['recs'].values() if r['rev'] > since), key=lambda r: r['rev'])[:lim]
                return self.out(200, [{'k': r['k'], 'v': r['v'], 'rev': r['rev'], 'age': now - r['t']} for r in rows])
            if p.path == '/rest/v1/rpc/push':   # igual que public.push (migrations/20261014b_sin_pisar.sql)
                if u['role'] not in ('admin', 'piso'):
                    return self.out(403, {'code': '42501', 'message': 'new row violates row-level security policy for table "app_records"'})
                if (DB.get('falla_push') and u['role'] == 'piso') or '\\u0000' in json.dumps(b):   # Postgres no guarda \u0000 en jsonb
                    return self.out(400, {'code': '22P05', 'message': 'unsupported Unicode escape sequence'})
                lost = []
                for r in b.get('rows', []):
                    cur = DB['recs'].get(r['k'])
                    if cur and cur['v'] == r['v']: continue
                    if cur and 'b' in r and cur['v'] != r['b']: lost.append({'k': r['k'], 'v': cur['v']}); continue
                    DB['rev'] += 1; DB['writes'] += 1
                    DB['recs'][r['k']] = {'k': r['k'], 'v': r['v'], 'rev': DB['rev'], 't': time.time()}; DB['log'].append('registro ' + r['k'])
                return self.out(200, lost)
        self.out(404, {'message': 'no'})
    def fn(self, b, u):
        a = b.get('action')
        weak = ['admin123', 'piso123', 'ver123', '123456', '1234567', '12345678', '123456789', 'password', 'contraseña', 'propesa', 'propesa1', 'langosta', 'qwerty', 'abc123', '111111', '000000']
        pw = str(b.get('password') or '')
        bad = 'La contraseña debe tener al menos 8 caracteres.' if len(pw) < 8 else 'Esa contraseña es muy fácil de adivinar. Elige otra.' if pw.lower() in weak else None
        if a == 'setup':   # igual que supabase/functions/usuarios (v1.7.0): solo si no hay ninguna cuenta
            if any(x['role'] == 'admin' for x in DB['users'].values()): return self.out(403, {'error': 'Ya existe un Administrador.'})
            if DB['users']: return self.out(403, {'error': 'Ya hay cuentas en la base. Para dar de alta un Administrador, pide ayuda a quien administra Supabase.'})
            if bad: return self.out(400, {'error': bad})
            uid = add_user(b['name'], b['email'], b['password'], 'admin'); return self.out(200, {'ok': True, 'id': uid})
        if not u: return self.out(401, {'error': 'Tu sesión venció. Vuelve a entrar.'})
        if u['role'] != 'admin': return self.out(403, {'error': 'Solo el Administrador gestiona usuarios.'})
        if a == 'create':
            if bad: return self.out(400, {'error': bad})
            if any(x['email'] == b['email'].lower() for x in DB['users'].values()): return self.out(400, {'error': 'Ese correo ya existe.'})
            uid = add_user(b['name'], b['email'], b['password'], b.get('role', 'consulta'), bool(b.get('notify'))); return self.out(200, {'ok': True, 'id': uid})
        x = DB['users'].get(b.get('id'))
        if not x: return self.out(404, {'error': 'Ese usuario ya no existe.'})
        if a == 'update':
            x.update(name=b['name'], email=b['email'].lower(), role=b['role'], notify=bool(b.get('notify')))
            if b.get('password'):
                if bad: return self.out(400, {'error': bad})
                x['pw'] = b['password']
            return self.out(200, {'ok': True})
        if a == 'delete':
            if x['id'] == u['id']: return self.out(400, {'error': 'No puedes eliminar tu propio usuario.'})
            del DB['users'][x['id']]; return self.out(200, {'ok': True})
        return self.out(400, {'error': 'Acción desconocida.'})

if __name__ == '__main__':
    seed_users()
    ThreadingHTTPServer(('127.0.0.1', int(sys.argv[1]) if len(sys.argv) > 1 else 8790), H).serve_forever()
