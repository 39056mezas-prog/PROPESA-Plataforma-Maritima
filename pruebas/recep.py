"""v1.42.0 · Ayuda para las pruebas: registrar una recepción POR TINAS desde la pantalla, como lo haría una persona.
La recepción vieja (kg por talla y «kg por caja en tanque») ya no existe: cada tina se pesa y se toca su talla.

Uso:
    import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from recep import recibir
    recibir(pg, 'WLRCO051026A', pv='1', kz=[40, 30], tank='T1', fecha='05/10/2026')

kz = kg por talla en el orden de las tallas de la maquila (Chica, Mediana, Grande, Jumbo…); cada talla se reparte en tinas de
hasta 35 kg (más si no caben en las tinas libres), en las tinas libres del tanque elegido (y si se llena, sigue en el siguiente). dp = kg de despatada (aparte).
Regresa la lista de tinas usadas [(tina, índice de talla, kg)]."""


def _tinas(kz, por=35.0):
    out = []
    for i, kg in enumerate(kz or []):
        kg = float(kg or 0)
        while kg > 1e-9:
            q = min(por, kg)
            out.append((i, round(q, 3)))
            kg = round(kg - q, 3)
    return out


def recibir(pg, lot, pv='1', kz=(), tank='T1', fecha=None, hora='09:00', hf='', tt='58', tpn='57', tpx='60',
            mu='', db='', rz='', dp='', guardar=True, sp=None, por=None, nuevo=True):
    """nuevo=False: sigue en la recepción que ya está abierta (por ejemplo «Completar» un lote sin recepción)."""
    if nuevo:
        pg.evaluate("RT=null;msg='';go('rtin')")
    pg.wait_for_timeout(80)
    if fecha:
        pg.fill('#rt_fd', fecha); pg.keyboard.press('Escape')
    pg.fill('#rt_hi', hora)
    if hf:
        pg.fill('#rt_hf', hf)
    if pv is not None:
        pg.select_option('#rt_fo', str(pv))
    if sp is not None and pg.locator('#rt_sp').count():
        pg.select_option('#rt_sp', str(sp))
    if lot is not None and not pg.locator('#rt_fl').is_disabled():  # lot=None: se queda el lote que propone la app
        pg.fill('#rt_fl', lot)
    if tank and pg.evaluate(f"rtFreeIn('{tank}',tnOcc()).length"):
        pg.click(f'[data-rt="tk:{tank}"]'); pg.wait_for_timeout(60)
    used = []
    S = pg.evaluate('S')
    kz = list(kz or [])
    if 'desp' in S and S.index('desp') < len(kz):  # la despatada va aparte, sin tina
        i = S.index('desp'); dpk = float(kz[i] or 0); kz[i] = 0
        if dpk and dp == '':
            dp = '%g' % dpk
    if por is None:  # tinas de 35 kg; si no caben en las tinas libres, tinas más llenas (datos grandes de prueba)
        libres = 180 - pg.evaluate('tnOcc().size'); tot = sum(float(v or 0) for v in kz)
        por = min(95.0, max(35.0, tot / max(1, libres * 0.9) + 1))
    for zi, kg in _tinas(kz, por):
        for intento in range(4):  # si otro equipo ocupó la tina mientras se capturaba, la app pasa a la siguiente libre
            n = pg.evaluate("RT.act")
            if n is None:
                raise RuntimeError('no hay tinas libres')
            try:
                pg.fill(f'#tn_k{n}', ('%g' % kg), timeout=4000); break
            except Exception:
                if intento == 3: raise
                pg.wait_for_timeout(200)
        pad = pg.locator('#tnpad').count() > 0
        pg.click(f'#tnpad [data-tnk="z:{zi}"]' if pad else f'[data-rt="z:{zi}"]')
        pg.wait_for_timeout(30)
        used.append((n, zi, kg))
    for k, v in (('rt_mu', mu), ('rt_db', db), ('rt_rz', rz), ('rt_dp', dp)):
        if v != '' and pg.locator('#' + k).count():
            pg.fill('#' + k, str(v))
    tks = sorted({pg.evaluate(f"tnTk({n})") for n, _, _ in used})
    for t in tks:
        pg.fill(f'#rt_tt{t}', str(tt))
    pg.fill('#rt_tpn', str(tpn)); pg.fill('#rt_tpx', str(tpx))
    if guardar:
        pg.click('[data-rt=sv]'); pg.wait_for_timeout(150)
        if pg.evaluate("V.v") != 'lote':
            raise RuntimeError('no se guardó la recepción %s: %s' % (lot, pg.evaluate("msg")))
    return used
