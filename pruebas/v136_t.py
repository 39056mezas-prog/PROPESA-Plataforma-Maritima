import sys
"""v1.36.0 · Textos de los formularios (/impeccable clarify, 5/nov/2026). El usuario aprobó los cuatro grupos:
1. Avisos de error: el error va junto a su campo, se queda hasta corregirlo, se anuncia y no se repite en otros formularios.
2. Un nombre por talla («Chica · 491-610») y por tanque («T1») en las pantallas.
3. Sin opciones peligrosas ya elegidas: tipo de movimiento, rol del usuario nuevo, a. m./p. m. de la hoja de empaque.
4. Detalles: «Ej.» en los ejemplos, ayudas a la vista, confirmaciones que dicen qué se borra, «o hieleras».
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v136_t.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recep import recibir
from playwright.sync_api import sync_playwright
import os
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em='admin@propesa.mx', piso='0'):
    pg.goto(BASE); pg.evaluate('([s,p])=>{localStorage.clear();sessionStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso",p);localStorage.setItem("propesa-inst",String(Date.now()))}', [seed, piso]); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', 'x'); pg.click('[data-a=lg]'); pg.wait_for_timeout(250)
def ir(pg, r): pg.evaluate(f"go('{r}')"); pg.wait_for_timeout(200)
def abrir(pg): pg.evaluate("document.querySelectorAll('details.fold').forEach(d=>{FOLD[d.dataset.fold]=true});render()"); pg.wait_for_timeout(150)
def fer(pg): return pg.evaluate("[...document.querySelectorAll('#app .fer')].map(e=>[e.id,e.innerText.trim()])")
def avisos(pg): return pg.evaluate("[...document.querySelectorAll('main p.er,main p.ok,main .fer')].map(e=>e.innerText.trim()).filter(Boolean)")
def visible(pg, sel): return pg.evaluate(f"(()=>{{const e=document.querySelector('{sel}');if(!e)return false;const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}})()")
def toast(pg): return pg.evaluate("(()=>{const t=document.getElementById('toast');return getComputedStyle(t).display=='none'?'':t.textContent})()")
def desborde(pg): return pg.evaluate("(()=>{const m=document.querySelector('main')||document.documentElement;return Math.max(document.documentElement.scrollWidth-document.documentElement.clientWidth,m.scrollWidth-m.clientWidth)})()")

with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------- 1. Avisos de error junto al campo ----------
    for W, H in [(1180, 820), (820, 1180), (390, 844), (1440, 900)]:
        pg = b.new_context(viewport={'width': W, 'height': H}).new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg); ir(pg, 'recepcion'); pg.click('[data-a=nf]'); pg.wait_for_timeout(150); pg.click('[data-rt=sv]'); pg.wait_for_timeout(200)
        f = fer(pg)
        chk(f == [['fer_rt_fo', 'Elige el proveedor.']], f'{W} Recepción: el error sale junto a Proveedor: {f}')
        chk(visible(pg, '#fer_rt_fo') and visible(pg, '#rt_fo'), f'{W} Recepción: el campo y su error se ven en la pantalla')
        chk(pg.get_attribute('#rt_fo', 'aria-describedby') == 'fer_rt_fo' and pg.get_attribute('#fer_rt_fo', 'role') == 'alert' and pg.get_attribute('#rt_fo', 'aria-invalid') == 'true', f'{W} Recepción: el error está ligado al campo y se anuncia')
        chk(avisos(pg).count('Elige el proveedor.') == 1, f'{W} Recepción: el error sale una sola vez (no también abajo del botón)')
        chk(desborde(pg) <= 0, f'{W} Recepción con error: sin desborde ({desborde(pg)})')
        pg.select_option('#rt_fo', index=1); pg.wait_for_timeout(100)
        chk(not fer(pg) and pg.get_attribute('#rt_fo', 'aria-invalid') is None, f'{W} Recepción: al elegir proveedor el error se quita')
        pg.fill('#rt_fl', 'WLRPRUEBA'); pg.click('[data-rt=sv]'); pg.wait_for_timeout(200)
        chk(fer(pg) == [['fer_tn_k1', 'Pesa al menos una tina: escribe sus kg y toca su talla.']], f'{W} Recepción: el siguiente dato que falta sale junto a su campo (la primera tina): {fer(pg)}')
        pg.close()

    pg = b.new_context(viewport={'width': 1180, 'height': 820}).new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    entrar(pg)
    # Lote: un error o un ✔ solo en su formulario
    ir(pg, 'lote:WLRCO051026A'); abrir(pg)
    pg.select_option('#ty', 'CONGELACION'); pg.click('[data-a=mv]'); pg.wait_for_timeout(150)
    a = avisos(pg)
    chk(a.count('Ingresa una cantidad mayor a 0.') == 1 and fer(pg)[0][0] == 'fer_kg', f'Lote: el error de Movimientos sale una vez, junto a Kg (antes 3 veces, también bajo «Guardar precio»): {a}')
    chk(pg.inner_text('#pr_m') == '' and pg.inner_text('#tq_m') == '', 'Lote: Precio y Pasar a otro tanque no muestran el error de Movimientos')
    pg.fill('#kg', '1'); pg.click('[data-a=mv]'); pg.wait_for_timeout(150)
    chk(pg.inner_text('#pr_m') == '' and pg.inner_text('#tq_m') == '' and any(x.startswith('✔') or 'registrado' in x for x in avisos(pg)), 'Lote: el ✔ del movimiento no sale en rojo bajo Precio ni bajo Pasar a otro tanque')
    ir(pg, 'lote:WLRCO051026A'); abrir(pg); pg.fill('#pr_u', '-3'); pg.click('[data-a=prs]'); pg.wait_for_timeout(150)
    chk(fer(pg) == [['fer_pr_u', 'Revisa el precio: un número de 0 o más.']] and avisos(pg).count('Revisa el precio: un número de 0 o más.') == 1, f'Lote: el error del precio sale junto al precio, una vez: {fer(pg)}')
    # Orden: el error de la línea ya no se va a los 4 s
    ir(pg, 'orden:1'); pg.click('[data-oa=add]'); pg.click('[data-oa=ln]'); pg.wait_for_timeout(200)
    chk(fer(pg) == [['fer_ol_n', 'Escribe las hieleras por talla o el total (mínimo 1).']] and toast(pg) == '', f'Orden: el error de la línea va junto al total, no en el aviso flotante: {fer(pg)}')
    pg.wait_for_timeout(4500); chk(len(fer(pg)) == 1, 'Orden: el error sigue ahí después de 4 s')
    pg.fill('#ol_n', '2'); pg.wait_for_timeout(100); chk(not fer(pg), 'Orden: al escribir el total el error se quita')
    # Un aviso de error de otra pantalla no se queda encima de la nueva
    pg.evaluate("toast('Elige el lote.')"); ir(pg, 'admin:usr'); chk(toast(pg) == '', 'al cambiar de pantalla se quita el aviso rojo de la anterior')
    # Errores técnicos con qué hacer
    chk(pg.evaluate("/No se pudo crear el PDF\\. Inténtalo otra vez/.test(document.documentElement.innerHTML)||/No se pudo crear el PDF\\. Inténtalo otra vez/.test([...document.scripts].map(s=>s.textContent).join(''))"), 'el error del PDF dice qué hacer (sin el detalle técnico)')
    chk(not pg.evaluate("[...document.scripts].some(s=>s.textContent.includes(\"'No se pudo (error '\"))"), 'ya no existe «No se pudo (error 500).»')

    # ---------- 2. Un nombre por talla y por tanque ----------
    ir(pg, 'recepcion'); pg.click('[data-a=nf]'); pg.wait_for_timeout(150)
    lab = pg.evaluate("[...document.querySelectorAll('[data-rt^=\"z:\"],#tnpad [data-tnk^=\"z:\"]')].map(b=>b.innerText.trim())")
    chk(lab == ['Chica', 'Mediana', 'Grande', 'Jumbo'], f'Recepción: las tallas de tina dicen su nombre (la despatada va aparte): {lab}')
    t = pg.inner_text('main')
    chk('0-650' not in t and '851-1250' not in t, 'Recepción: los rangos del papel ya no salen en la pantalla (siguen en el PDF)')
    ir(pg, 'recepcion')
    chk(pg.evaluate("ST.R.length>0") and 'T1' in pg.inner_text('table.ent tbody'), 'Entrada: la tabla dice T1')
    ir(pg, 'lote:WLRCO051026A'); abrir(pg)
    o = pg.evaluate("[...document.querySelectorAll('#sz option')].map(x=>x.text)")
    chk(o[:4] == ['Chica · 491-610', 'Mediana · 611-850', 'Grande · 851-1220', 'Jumbo · 1221-UP'], f'Lote: Movimientos usa «Chica · 491-610»: {o}')
    chk(pg.evaluate("[...document.querySelectorAll('#rz_de option')][0].text").startswith('Chica · 491-610 · '), 'Lote: Cambio de talla usa el mismo nombre')
    ir(pg, 'embarques'); pg.locator('main [data-go^="emb:"]').first.click(); pg.wait_for_timeout(200)
    pt = pg.inner_text('#emb_lotes')
    chk('Mediana 54' in pt and 'Rojo 54' not in pt, f'Embarque: la columna «Por talla» dice tallas, no colores: {pt[-60:]}')
    chk(pg.evaluate("[...document.querySelectorAll('#emb_tallas label')].map(l=>l.innerText.replace(/\\s+/g,' ').trim())")[:1] == ['Chica 491-610'], 'Embarque: Distribución por talla con nombre y rango')
    ir(pg, 'temperatura'); chk(pg.evaluate("[...document.querySelectorAll('#tq_t option')].map(x=>x.text)")[:2] == ['T1', 'T2'], 'Temperatura: el tanque se llama T1')
    ir(pg, 'orden:1'); abrir(pg)
    chk('Chica · 1' in pg.inner_text('#f6card') and '491-610 · 1' not in pg.inner_text('#f6card'), 'Hoja de empaque: hieleras por talla con su nombre')

    # ---------- 3. Sin opciones peligrosas ya elegidas ----------
    ir(pg, 'lote:WLRCO051026A'); abrir(pg)
    chk(pg.input_value('#ty') == '' and 'Salida a embarque (solo para corregir)' in pg.evaluate("[...document.querySelectorAll('#ty option')].map(x=>x.text).join('|')"), 'Movimientos: el tipo no viene elegido y «Salida a embarque» avisa que es para corregir')
    pg.fill('#kg', '1'); pg.click('[data-a=mv]'); pg.wait_for_timeout(150)
    chk(fer(pg) == [['fer_ty', 'Elige el tipo de movimiento.']], 'Movimientos: sin tipo no registra y lo pide junto al campo')
    ir(pg, 'admin:usr'); pg.click('[data-a=nu]'); pg.wait_for_timeout(150)
    chk(pg.input_value('#ur') == '', 'Usuario nuevo: el rol no viene en Administrador')
    n0 = pg.evaluate("ST.U.length")
    pg.fill('#un', 'Prueba'); pg.fill('#ue', 'prueba@propesa.mx'); pg.fill('#up', '12345678'); pg.click('[data-a=su]'); pg.wait_for_timeout(150)
    chk(fer(pg) == [['fer_ur', 'Elige el rol.']] and pg.evaluate("ST.U.length") == n0 and pg.input_value('#un') == 'Prueba', 'Usuario nuevo: sin rol no se crea, lo pide y conserva lo escrito')
    pg.select_option('#ur', 'piso'); pg.click('[data-a=su]'); pg.wait_for_timeout(150)
    chk(pg.evaluate("ST.U.some(u=>u.email=='prueba@propesa.mx'&&u.role=='piso')"), 'Usuario nuevo: con el rol elegido se crea')
    pg.click('[data-a=nu]'); pg.wait_for_timeout(100)
    chk('Contraseña (mínimo 8)' in pg.inner_text('main') and 'Recibe el informe de cierre de embarque' in pg.inner_text('main'), 'Usuario: el mínimo de la contraseña y qué informe recibe, a la vista')
    ir(pg, 'orden:1'); abrir(pg)
    chk(pg.input_value('#f6_hi') == '' and pg.input_value('#f6_hi_ap') == '', 'Hoja de empaque: sin hora inicial, a. m./p. m. no viene elegido')
    pg.fill('#f6_hi', '6:30'); pg.locator('[data-f6^="ev:"]').first.click(); pg.wait_for_timeout(150)
    chk(fer(pg) == [['fer_f6_hi_ap', 'Elige a. m. o p. m. en la hora inicial.']] and not pg.evaluate("(ST.OR.find(o=>o.id==1).f||{}).hi"), f'Hoja de empaque: una hora sin a. m./p. m. no se guarda y lo pide: {fer(pg)}')
    pg.select_option('#f6_hi_ap', 'am'); pg.locator('[data-f6^="ev:"]').first.click(); pg.wait_for_timeout(150)
    chk(pg.evaluate("ST.OR.find(o=>o.id==1).f.hi") == '06:30', 'Hoja de empaque: con a. m. se guarda 06:30')

    # ---------- 4. Detalles de texto ----------
    ir(pg, 'orden:1')
    t = pg.inner_text('main')
    chk('Editar consignatario o hieleras' in t and 'u hieleras' not in t, '«Editar consignatario o hieleras»')
    ir(pg, 'recepcion'); t0 = pg.inner_text('main'); pg.click('[data-a=nf]'); pg.wait_for_timeout(100)
    chk(pg.get_attribute('#rt_tpn', 'placeholder') == 'Ej. 57.7' and pg.get_attribute('#rt_fl', 'placeholder') == 'Ej. WLRCO051026A', 'Recepción: los ejemplos dicen «Ej.» y la temperatura es un solo número (ya no «59-62»)')
    t = pg.inner_text('main')
    chk('Langosta muerta (kg)' in t and 'Temperatura del producto mínima (°F)' in t and 'Temp. °F' not in t, 'Recepción: etiquetas sin abreviar')
    chk('fecha distinta a la del código' in t0, 'Recepción: el aviso dice qué pasa con la fecha')
    ir(pg, 'cierre'); chk('Las gráficas salen' not in pg.inner_text('main'), 'Mortalidad final: sin el texto de «las gráficas salen…»')
    # nota: confirmación que dice qué se borra
    ir(pg, 'temperatura'); abrir(pg); pg.fill('#ntx', 'Prueba de nota'); pg.locator('[data-ev^="save:"]').first.click(); pg.wait_for_timeout(150)
    pg.locator('[data-ev^="del:"]').first.click(); pg.wait_for_timeout(100)
    chk('¿Eliminar esta nota?' in pg.inner_text('main') and pg.locator('[data-ev^="rm:"]').first.inner_text() == 'Eliminar nota', 'Notas: «¿Eliminar esta nota?» con «Eliminar nota» y «Cancelar»')
    pg.locator('[data-ev=no]').first.click(); pg.wait_for_timeout(100)
    ir(pg, 'temperatura'); abrir(pg); pg.locator('[data-ev^="save:"]').first.click(); pg.wait_for_timeout(150)
    chk(fer(pg) == [['fer_ntx', 'Escribe una nota o agrega una foto.']], 'Notas: guardar vacía lo pide junto al campo')
    pg.close()

    # ---------- Modo piso: mismos nombres, sin desbordes ----------
    for W, H in [(390, 844), (820, 1180), (1180, 820)]:
        pg = b.new_context(viewport={'width': W, 'height': H}).new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg, 'piso@propesa.mx', '1'); ir(pg, 'pent')
        chk(pg.evaluate("[...document.querySelectorAll('select')].some(s=>[...s.options].map(o=>o.text).join(',')=='—,T1,T2,T3,T4,T5,T6')"), f'{W} Modo piso: tanques T1…T6')
        if 'desperdicio' not in pg.inner_text('main'): pg.click('[data-pa^="more:"]'); pg.wait_for_timeout(150)  # «Más datos» puede venir abierto
        pg.evaluate("document.querySelectorAll('.pt2').forEach(d=>d.open=true)")  # v1.39.0: «otro tanque» va plegado
        t = pg.inner_text('main')
        chk('Kg Chica' in t and 'Kg de desperdicio (0 si no hubo)' in t, f'{W} Modo piso: «Kg Chica» y «0 si no hubo»')
        chk(desborde(pg) <= 0, f'{W} Modo piso: sin desborde ({desborde(pg)})')
        pg.close()
    b.close()
chk(not errs, 'sin errores de JavaScript: ' + '; '.join(errs[:3]))
print('TODO BIEN' if not fails else f'{len(fails)} FALLAS')
