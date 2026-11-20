# v1.58.0 · Auditoría UI/UX (L8): una «}» de más en el CSS hacía que la capa CPX del iPad viejo dejara de leer el resto de la hoja
# (tanques, tinas… sin estilo). Los navegadores nuevos la saltan y no se nota en Chrome. Esta prueba revisa que las llaves del
# <style> de index.html cuadren, sin contar comentarios ni textos entre comillas.
#   python3 -I pruebas/css_llaves_t.py   → «TODO BIEN» o «FALLAS»
import os, re, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(RAIZ, 'index.html'), encoding='utf-8').read()
bad = []
def ok(c, t):
    print(('  ✔ ' if c else '  ✘ ') + t)
    if not c: bad.append(t)
for n, css in enumerate(re.findall(r'<style[^>]*>([\s\S]*?)</style>', html), 1):
    c = re.sub(r'/\*[\s\S]*?\*/', lambda m: ' ' * len(m.group(0)), css)
    c = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', lambda m: ' ' * len(m.group(0)), c)
    d, sueltas = 0, []
    for i, ch in enumerate(c):
        if ch == '{': d += 1
        elif ch == '}':
            d -= 1
            if d < 0: sueltas.append(i); d = 0
    for i in sueltas: print('     «}» suelta cerca de: ' + css[max(0, i - 80):i + 20].replace('\n', ' '))
    ok(not sueltas, f'<style> {n}: ninguna «}}» de más')
    ok(d == 0, f'<style> {n}: ninguna «{{» sin cerrar')
print('TODO BIEN' if not bad else 'FALLAS'); sys.exit(1 if bad else 0)
