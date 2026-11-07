"""v1.27.0 (pedido del usuario, 29/oct/2026).
1. Máximo 35 langostas por hielera: no se guarda una hielera con más (vista completa, Modo piso, corregir y teclado).
2. Días máximos en tanque por proveedor (Administración → Proveedores): un lote que los pasa sale en rojo en el lote,
   en Notificaciones y primero en Empaque. Sin número = sin límite. Viaja en WN.V / cleanST.
3. Lo más viejo primero: en Empaque los lotes salen del más viejo al más nuevo (los vencidos antes) y el primero con kilos
   queda elegido con «Más viejo · usar primero»; se puede cambiar.
4. Orden variada: «Repartir tallas: lo más viejo primero» llena las hieleras por talla con lo más viejo de los tanques,
   descontando lo que otras órdenes ya pidieron.
Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/v127_t.py"""
from playwright.sync_api import sync_playwright
import os
BASE = os.environ.get('BASE', 'http://localhost:8765/index.html?modo=local')
seed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos', 'seed.json')).read()
fails, errs = [], []
def chk(c, m):
    print(('PASS ' if c else 'FAIL ') + m)
    if not c: fails.append(m)
def entrar(pg, em, pw, piso='0'):
    pg.goto(BASE); pg.evaluate('([s,p])=>{localStorage.clear();localStorage.setItem("propesa-v4",s);localStorage.setItem("propesa-piso",p)}', [seed, piso]); pg.reload()
    pg.fill('#le', em); pg.fill('#lp', pw); pg.click('[data-a=lg]'); pg.wait_for_timeout(200)
def toast(pg): return pg.inner_text('#toast') if pg.locator('#toast').count() else ''
# orden nueva con una línea de 3 hieleras (sin empacar) y el lote B más viejo que el A
SETUP = """()=>{const id=uidN();ST.OR.push({id,etd:dLoc(),lines:[{id:1,city:'PVG',cons:0,boxes:3,kp:16}],sh:{},sp:1});
 const d=new Date();d.setDate(d.getDate()-5);ST.R[1].rdate=dLoc(d);ST.R[0].rdate=dLoc();save();return id}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in [(1180, 820), (390, 844)]:
        pg = b.new_page(viewport={'width': vw[0], 'height': vw[1]}); pg.on('pageerror', lambda e: errs.append(str(e)))
        entrar(pg, 'admin@propesa.mx', 'admin123'); oid = pg.evaluate(SETUP)
        A, B = pg.evaluate("ST.R.map(r=>r.lot)")
        # ---------- 3. lo más viejo primero
        o = f"ST.OR.find(o=>o.id=={oid})"
        chk(pg.evaluate(f"ordLots({o})")[0] == B, f'{vw} en Empaque el lote más viejo ({B}) sale primero')
        pg.evaluate(f"go('empacar:{oid}.1')"); pg.wait_for_timeout(100)
        chk(pg.get_attribute(f'[data-pk="lot:{B}"]', 'aria-pressed') == 'true' and 'usar primero' in pg.inner_text(f'[data-pk="lot:{B}"]').lower(), f'{vw} el más viejo ya está elegido y dice «usar primero»')
        chk('usar primero' not in pg.inner_text(f'[data-pk="lot:{A}"]').lower(), f'{vw} el más nuevo no lo dice')
        pg.click(f'[data-pk="lot:{A}"]'); pg.wait_for_timeout(60)
        chk(pg.get_attribute(f'[data-pk="lot:{A}"]', 'aria-pressed') == 'true', f'{vw} se puede cambiar al otro lote')
        pg.click(f'[data-pk="lot:{B}"]')
        # ---------- 1. máximo 35
        pg.evaluate("PKD.rows[0]={c:'36',k:TKEY[1]};render()"); pg.click('[data-pk=addall]'); pg.wait_for_timeout(80)
        chk(pg.evaluate(f"ordAssigned({o},{o}.lines[0]).length") == 0 and 'máximo 35' in toast(pg), f'{vw} con 36 langostas no se guarda: «{toast(pg)}»')
        pg.evaluate("PKD.rows[0]={c:'35',k:TKEY[1]};render()"); pg.click('[data-pk=addall]'); pg.wait_for_timeout(80)
        chk(pg.evaluate(f"ordAssigned({o},{o}.lines[0]).length") == 1 and pg.evaluate(f"ordAssigned({o},{o}.lines[0])[0].l") == B, f'{vw} con 35 sí se guarda, del lote más viejo')
        # piso: peTry y corregir
        r = pg.evaluate(f"""()=>{{setPiso(true);go('pemp:{oid}.1');chk_q=!!document.querySelector('[data-pe^="lot:"] .lotf');PE.lot='{B}';PE.rows[2]={{c:'40',k:'R'}};const a=peTry(2,true);PE.rows[2]={{c:'30',k:'R'}};const b2=peTry(2,true);return [chk_q,a,b2,ordAssigned({o},{o}.lines[0]).length]}}""")
        chk(r == [True, False, True, 2], f'{vw} Modo piso: pregunta el lote con «usar primero» en el más viejo; 40 no se guarda, 30 sí {r}')
        pg.evaluate("setPiso(false);render()")
        # ---------- 2. días máximos por proveedor
        pg.evaluate("go('admin:cat')"); pg.wait_for_timeout(80)
        pg.click('[data-pva="ed:1"]'); pg.fill('#pv_dm', '0'); pg.click('[data-pva=sv]'); pg.wait_for_timeout(60)
        chk('1 a 60' in pg.inner_text('#app .fer') and not pg.evaluate("pvBy(1).dm"), f'{vw} 0 días no se acepta')
        pg.fill('#pv_dm', '3'); pg.click('[data-pva=sv]'); pg.wait_for_timeout(60)
        chk(pg.evaluate("pvBy(1).dm") == 3 and 'Hasta 3' in pg.inner_text('#provs'), f'{vw} el proveedor guarda «hasta 3 días»')
        chk(pg.evaluate("WN.V(pvBy(1)).dm===3&&cleanST(JSON.parse(JSON.stringify(ST)),true).PV.find(p=>p.id===1).dm===3&&WN.V({...pvBy(1),dm:'x'}).dm===undefined"), f'{vw} se comparte y se limpia (WN.V, cleanST)')
        # el lote B (de otro proveedor) aún no; poner B como de SCPP Ensenada (dm 3) con 5 días
        pg.evaluate(f"(()=>{{const r=R_('{B}');r.origin=pvBy(1).n;r.pv=1;save();render()}})()")
        chk('5 días' in pg.evaluate(f"lotOld('{B}')") and pg.evaluate(f"lotOld('{A}')") == '', f'{vw} el lote con 5 días de un proveedor de 3 sale vencido; el de hoy no')
        pg.evaluate(f"go('lote:{B}')"); pg.wait_for_timeout(80)
        chk(pg.locator('.alb', has_text='empácalo primero').count() == 1 and pg.locator('.alb [data-go=empaque]').count() == 1, f'{vw} aviso rojo en el lote con «Ir a Empaque»')
        chk(pg.evaluate(f"ntFalta().some(x=>x.go==='lote:{B}'&&/5 días/.test(x.tx))"), f'{vw} y en Notificaciones')
        pg.evaluate(f"(()=>{{const d=new Date();d.setDate(d.getDate()-10);const a=R_('{A}');a.rdate=dLoc(d);a.pv=2;a.origin=pvBy(2).n;save()}})()")  # A más viejo, de un proveedor sin límite
        chk(pg.evaluate(f"ordLots({o})")[0] == B, f'{vw} el vencido sale antes que uno más viejo sin límite')
        pg.evaluate(f"go('empacar:{oid}.1')"); pg.wait_for_timeout(80)
        chk('5 días' in pg.inner_text(f'[data-pk="lot:{B}"]') and 'aguanta 3' in pg.inner_text(f'[data-pk="lot:{B}"]'), f'{vw} en Empaque dice «5 días · aguanta 3»')
        pg.evaluate(f"(()=>{{const d=new Date();d.setDate(d.getDate()-3);R_('{B}').rdate=dLoc(d);save();render()}})()")
        chk('Último día' in pg.inner_text(f'[data-pk="lot:{B}"]') and pg.evaluate(f"lotOld('{B}')") == '', f'{vw} con 3 días: «Último día», sin aviso rojo')
        chk(pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), f'{vw} sin scroll de lado')
        pg.evaluate("go('admin:cat')"); pg.click('[data-pva="ed:1"]'); pg.fill('#pv_dm', ''); pg.click('[data-pva=sv]'); pg.wait_for_timeout(60)
        chk(pg.evaluate("pvBy(1).dm") is None and 'Sin límite' in pg.inner_text('#provs'), f'{vw} vacío = sin límite')
        # ---------- 4. orden variada
        oid2 = pg.evaluate("(()=>{const id=uidN();ST.OR.push({id,etd:dLoc(),lines:[],sh:{},sp:1});save();go('orden:'+id);return id})()"); pg.wait_for_timeout(80)
        exp = pg.evaluate(f"zAuto(ST.OR.find(o=>o.id=={oid2}),20,16)")
        chk(exp['falta'] == 0 and sum(exp['z']) == 20, f'{vw} 20 hieleras alcanzan {exp}')
        # lo más viejo primero: A (10 días) va primero; su talla 491-610 tiene 120.5 kg = 7 hieleras de 16 kg
        chk(exp['z'][0] >= 7, f'{vw} empieza por las tallas del lote más viejo {exp["z"]}')
        pg.fill('#ol_n', '20'); pg.click('[data-oa="za:ol"]'); pg.wait_for_timeout(80)
        zs = pg.evaluate("[0,1,2,3].map(i=>document.getElementById('ol_z'+i).value)")
        chk([int(v or 0) for v in zs] == exp['z'][:4] and 'repartidas' in toast(pg), f'{vw} el botón llena las tallas {zs}')
        pg.click('[data-oa=ln]'); pg.wait_for_timeout(80)
        chk(pg.evaluate(f"ST.OR.find(o=>o.id=={oid2}).lines[0].z.slice(0,4).join()") == ','.join(str(x) for x in exp['z'][:4]), f'{vw} y se guarda en la orden')
        # otra orden ya no cuenta lo que pidió la primera
        e2 = pg.evaluate(f"(()=>{{const o3={{id:1,lines:[],sp:1}};return zAuto(o3,20,16)}})()")
        chk(e2['z'] != exp['z'], f'{vw} lo ya pedido por otra orden se descuenta {e2["z"]}')
        e3 = pg.evaluate(f"zAuto(ST.OR.find(o=>o.id=={oid2}),9999,16)")
        chk(e3['falta'] > 0, f'{vw} si no alcanza, dice cuántas faltan ({e3["falta"]})')
        pg.close()
    b.close()
print('\nERRORES JS:', errs) if errs else None
print(f"\n{'TODO BIEN' if not fails and not errs else str(len(fails)) + ' FALLAS'}")
