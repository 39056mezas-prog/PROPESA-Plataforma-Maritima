"""Botón de atrás (Android / navegador), v1.8.1: regresa a la pantalla anterior de la app en vez de salir;
si hay algo abierto encima (foto en grande, Ajustes, menú del perfil), primero lo cierra.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/atras_t.py"""
from playwright.sync_api import sync_playwright
import os, sys
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')  # modo local: nunca toca la base real
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def back(pg):
    pg.go_back(wait_until='commit'); pg.wait_for_timeout(250)
V = "[V.v,V.id==null?'':String(V.id),PISO]"

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE); pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso","0")}', seed); pg.reload()
        pg.fill('#le', 'admin@propesa.mx'); pg.fill('#lp', 'admin123'); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
        start = pg.evaluate('history.length'); lot = pg.evaluate('ST.R[0].lot')
        chk(pg.evaluate(V) == ['inicio', '', False], f'{vw} entra al Panel')
        # navegar: Panel → Entrada → lote → Órdenes
        pg.evaluate("go('recepcion')"); pg.evaluate(f"go('lote:{lot}')"); pg.evaluate("go('ordenes')")
        chk(pg.evaluate('history.length') == start + 3, f'{vw} cada pantalla nueva queda en el historial')
        back(pg); chk(pg.evaluate(V) == ['lote', lot, False], f'{vw} atrás → regresa al lote')
        back(pg); chk(pg.evaluate(V) == ['recepcion', '', False], f'{vw} atrás → Entrada')
        back(pg); chk(pg.evaluate(V) == ['inicio', '', False] and pg.locator('.sb').count() == 1, f'{vw} atrás → Panel (sigue dentro de la app)')
        pg.go_forward(wait_until='commit'); pg.wait_for_timeout(250); chk(pg.evaluate(V) == ['recepcion', '', False], f'{vw} adelante también funciona')
        # volver a dibujar la misma pantalla no agrega pasos
        n = pg.evaluate('history.length'); pg.evaluate('render();render();softRender()'); chk(pg.evaluate('history.length') == n, f'{vw} redibujar la misma pantalla no agrega pasos al historial')
        # Ajustes abierto: atrás lo cierra y se queda en la pantalla
        pg.evaluate("go('ordenes')"); pg.click('[data-settings]'); pg.wait_for_timeout(150); chk(pg.evaluate('SETOPEN'), f'{vw} Ajustes abierto')
        back(pg); chk(not pg.evaluate('SETOPEN') and pg.evaluate(V)[0] == 'ordenes', f'{vw} atrás cierra Ajustes y se queda en Órdenes')
        back(pg); chk(pg.evaluate(V)[0] == 'recepcion', f'{vw} el siguiente atrás ya regresa de pantalla')
        # menú del perfil abierto: atrás lo cierra
        pg.evaluate("go('cierre')"); pg.click('[data-avatar]'); pg.wait_for_timeout(100); chk(pg.evaluate('PMOPEN'), f'{vw} menú del perfil abierto')
        back(pg); chk(not pg.evaluate('PMOPEN') and pg.evaluate(V)[0] == 'cierre', f'{vw} atrás cierra el menú del perfil')
        # foto en grande: atrás la cierra
        pg.evaluate("(()=>{const o=document.createElement('div');o.className='lbx';document.body.appendChild(o)})()")
        back(pg); chk(pg.locator('.lbx').count() == 0 and pg.evaluate(V)[0] == 'cierre', f'{vw} atrás cierra la foto en grande')
        if vw[0] < 700:   # celular: el menú lateral (☰) abierto se cierra con atrás
            pg.click('.mb'); chk(pg.evaluate("document.getElementById('app').classList.contains('sbo')"), f'{vw} menú lateral abierto')
            back(pg); chk(not pg.evaluate("document.getElementById('app').classList.contains('sbo')") and pg.evaluate(V)[0] == 'cierre', f'{vw} atrás cierra el menú lateral')
        # Modo piso: Inicio de piso → Empacar → atrás → Inicio de piso; y atrás regresa a la vista completa
        pg.evaluate("switchMode(true)"); pg.wait_for_timeout(1000); chk(pg.evaluate(V) == ['piso', '', True], f'{vw} cambia a Modo piso')
        pg.evaluate("go('pent')"); back(pg); chk(pg.evaluate(V) == ['piso', '', True] and pg.locator('.pshell,.phd').count() >= 1, f'{vw} Modo piso: atrás regresa al inicio de piso')
        back(pg); chk(pg.evaluate(V) == ['cierre', '', False] and pg.locator('.sb').count() == 1, f'{vw} atrás desde Modo piso regresa a la vista completa donde estabas')
        # un lote que ya no existe: atrás no truena, va a Entrada
        pg.evaluate(f"go('lote:{lot}')"); pg.evaluate("go('inicio')")
        pg.evaluate(f"ST.R=ST.R.filter(r=>r.lot!=='{lot}');save()"); back(pg)
        chk(pg.evaluate(V)[0] == 'recepcion', f'{vw} atrás a un lote que ya no existe → Entrada')
        # al cerrar sesión y volver a entrar, el historial empieza en el Panel
        pg.evaluate("signOut('',true)"); chk(pg.locator('#le').count() == 1, f'{vw} cerrar sesión'); back(pg)
        chk(pg.locator('#le').count() == 1 and not pg.evaluate('!!me'), f'{vw} sin sesión, atrás no abre pantallas de la app')
        pg.close()
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('RESULTADO:', 'TODO BIEN' if not fails else f'{len(fails)} FALLAS')
sys.exit(1 if fails else 0)
