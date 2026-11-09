"""Auditoría rápida de index.html (v1.42.0). Busca patrones que gastan batería o memoria y lo que no debe subirse a GitHub.
Son pistas, no veredictos: cada línea es un lugar para revisar.

Uso: python3 -I pruebas/auditoria_rapida.py            # lista lo que encuentra; sale con 0
     python3 -I pruebas/auditoria_rapida.py --estricto  # sale con 1 si encuentra algo (para correr antes de entregar)

Revisa:
- requestAnimationFrame que se vuelve a pedir sin condición (un ciclo que nunca se detiene: la pantalla quieta debe no dibujar nada).
- setInterval de 33 ms o menos.
- Map global que solo crece (tiene .set y nunca .delete ni .clear): todo guardado temporal necesita un tope.
- Medir la pantalla (getBoundingClientRect, offsetHeight…) dentro de un evento de scroll.
- Rastros que no deben ir al repositorio público: rutas de una computadora (/home/, /Users/, /mnt/), llaves y tokens.
- ?? y ?. (el iPad viejo, iOS 12, no los entiende).
"""
import os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scripts_propios(html):
    """El JavaScript de la app, sin la librería del calendario (flatpickr), con el número de línea donde empieza cada bloque."""
    for m in re.finditer(r'<script>([\s\S]*?)</script>', html):
        if 'flatpickr' in m.group(1)[:300]:
            continue
        yield html.count('\n', 0, m.start(1)) + 1, m.group(1)


def linea(base, bloque, pos):
    return base + bloque.count('\n', 0, pos)


def auditar(html):
    out = []
    for base, b in scripts_propios(html):
        # 1. ciclos de requestAnimationFrame sin condición: «function f(){… requestAnimationFrame(f)}» sin if/return antes
        for m in re.finditer(r'requestAnimationFrame\((\w+)\)', b):
            fn = m.group(1)
            d = b.rfind('function ' + fn + '(', 0, m.start())
            if d < 0:
                d = b.rfind(fn + '=', 0, m.start())
            if d < 0 or m.start() - d > 4000:
                continue
            cuerpo = b[d:m.start()]
            antes = b[max(d, m.start() - 160):m.start()]
            if not re.search(r'\bif\s*\(|\?\s*$|&&\s*$', antes) and 'return' not in cuerpo:
                out.append(('ciclo de cuadros sin fin', linea(base, b, m.start()), b[m.start() - 60:m.end()]))
        # 2. setInterval rápido
        for m in re.finditer(r'setInterval\([^;]*?,\s*(\d+)\s*\)', b):
            if int(m.group(1)) <= 33:
                out.append(('setInterval de %s ms' % m.group(1), linea(base, b, m.start()), m.group(0)[:90]))
        # 3. Map global que solo crece
        for m in re.finditer(r'(?:const|let)\s+([A-Z][A-Z0-9_]+)\s*=\s*new Map\(\)', b):  # globales (en esta app, en MAYÚSCULAS)
            n = m.group(1)
            if re.search(r'\b' + re.escape(n) + r'\.set\(', b) and not re.search(r'\b' + re.escape(n) + r'\.(delete|clear)\(', b) \
                    and not re.search(r'\b' + re.escape(n) + r'\s*=(?!=)', b[m.end():]):  # si se reemplaza entero, no crece
                out.append(('Map que solo crece (sin tope)', linea(base, b, m.start()), m.group(0)))
        # 4. medir la pantalla dentro de un evento de scroll
        for m in re.finditer(r"addEventListener\('scroll'", b):
            trozo = b[m.start():m.start() + 600]
            if re.search(r'getBoundingClientRect|offsetHeight|offsetWidth|scrollHeight', trozo):
                out.append(('mide la pantalla en cada scroll', linea(base, b, m.start()), trozo[:90]))
        # 6. iOS 12
        for m in re.finditer(r'[^?]\?\?[^?]|\?\.[A-Za-z_$]', b):
            out.append(('?? o ?. (iOS 12 no los entiende)', linea(base, b, m.start()), b[m.start() - 40:m.end() + 20]))
    return out


PRIVADO = re.compile(r'/home/[a-z]|/Users/|/mnt/user-data|/private/var/|\.ts\.net|ses_[A-Za-z0-9]{20}|session_[A-Za-z0-9]{20}'
                     r'|sk-[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{20}|sb_secret_|"role"\s*:\s*"service_role"')


def rastros():
    out = []
    for dp, dn, fn in os.walk(RAIZ):
        dn[:] = [d for d in dn if d not in ('.git', '__pycache__', 'node_modules')]
        for f in fn:
            if not f.endswith(('.html', '.js', '.mjs', '.py', '.md', '.sh', '.json', '.sql', '.css', '.txt')):
                continue
            ruta = os.path.join(dp, f)
            if ruta == os.path.abspath(__file__):
                continue
            try:
                for i, l in enumerate(open(ruta, encoding='utf-8', errors='ignore'), 1):
                    if PRIVADO.search(l):
                        out.append(('rastro privado (no subir)', os.path.relpath(ruta, RAIZ) + ':%d' % i, l.strip()[:90]))
            except OSError:
                pass
    return out


if __name__ == '__main__':
    html = open(os.path.join(RAIZ, 'index.html'), encoding='utf-8').read()
    res = [(k, 'index.html:%d' % n, t.replace('\n', ' ')) for k, n, t in auditar(html)] + rastros()
    for k, d, t in res:
        print(f'{k}\t{d}\t{t}')
    print(f'{len(res)} hallazgo(s)' if res else 'Sin hallazgos')
    sys.exit(1 if res and '--estricto' in sys.argv else 0)
