# v1.50.0 · Correos con varios PDF, archivo en Gmail y «Correos enviados» (modo local, sin internet ni base real).
# Correr:  python3 -I pruebas/correo_t.py  → debe terminar en «TODO BIEN».
# El envío de verdad (servidor + Resend) se prueba aparte en pruebas/correo_servidor_t.js; aquí se finge mlSendNow.
import os, sys, subprocess, time, socket, json
from playwright.sync_api import sync_playwright

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('PORT_CORREO', '8791'))
OUT = os.environ.get('SALIDA', '/tmp/correo_t')
os.makedirs(OUT, exist_ok=True)

def libre(p):
    with socket.socket() as s:
        return s.connect_ex(('127.0.0.1', p)) != 0

srv = None
if libre(PORT):
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT)], cwd=RAIZ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)

MAL = []
def ok(c, t):
    print(('  ✔ ' if c else '  ✘ ') + t)
    if not c: MAL.append(t)

SEED = r"""
ST.U=[{id:1,name:'Admin',email:'admin@propesa.org',role:'admin',notify:true}];me=ST.U[0];
const l='LTEST1';ST.R.push({id:'R-'+uidS(),lot:l,origin:'Proveedor X',tank:'T1',rdate:dLoc(),time:'08:00',date:fd(dLoc()),tn:[[1,S[1],30000],[2,S[1],28000]],final:null,closed:false});
ST.B[l]=[];post('RECEPCION',l,S[1],58);
const o={id:uidN(),etd:dLoc(),lines:[{id:1,city:'PVG',cons:0,boxes:2,kp:16}],sh:{}};ST.OR.push(o);
const i=shipFor(o,'PVG',0);ST.B[l].push({c:10,k:'R',d:i,o:o.id+'.1',seq:uidN()},{c:11,k:'R',d:i,o:o.id+'.1',seq:uidN()});
syncShipIdx(i);save();window.__o=o.id;window.__i=i;window.__u=ST.P[i].u;
window.__sent=[];window.__fail=null;
window.mlSendNow=async(D,to,cc,s,b)=>{if(window.__fail)throw new Error(window.__fail);window.__sent.push({n:D.att.map(a=>a.n),k:D.att.map(a=>a.k),to,cc,s,refs:mlRefs(D),ar:mlArchTo(),size:mlSize(D)});return{ok:true}};
go('lote:'+l);"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 900})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{PORT}/index.html?modo=local')
    pg.wait_for_timeout(600)
    pg.evaluate(SEED)
    pg.wait_for_timeout(300)

    print('1 · Lo de siempre')
    d = pg.evaluate("({p:mlCfg('emb').p,r:mlCfg('rec').p,a:mlArch(),m:mlCfg('rec').m})")
    ok(d['p'] == ['emb', 'emp'], 'Embarque cerrado: informe + packing list marcados')
    ok(d['r'] == ['rec'], 'Recepción terminada: Formato 02 marcado')
    ok(d['a']['e'] == 'conectandoensenada@gmail.com' and d['a']['on'], 'Archivo: conectandoensenada@gmail.com prendido')

    print('2 · Lote sin correos')
    ok(pg.locator('#mlsent').count() == 1, 'El lote trae «Correos enviados»')
    ok('Ninguno todavía' in pg.locator('#mlsent').inner_text(), 'Dice «Ninguno todavía»')

    print('3 · Borrador con varios PDF (lote)')
    pg.evaluate("document.querySelector('[data-pdf^=\"mail:rec\"]').click()")
    pg.wait_for_selector('#ml_atts')
    ok(pg.locator('#ml_atts .mlatt').count() == 1, 'Abre con el Formato 02')
    ok('conectandoensenada@gmail.com' in pg.locator('#ml_sum').inner_text(), 'Dice la copia oculta al archivo')
    pg.click('[data-mladd=open]')
    pg.click('#ml_atts .mladd button[data-mladd="0"]')
    pg.wait_for_function("document.querySelectorAll('#ml_atts .mlatt').length==2")
    ok(True, '«+ Agregar PDF» suma el monitoreo de temperatura')
    pg.screenshot(path=f'{OUT}/borrador_1280.png')
    pg.click('#ml_send')
    pg.wait_for_function("!document.querySelector('#mlroot .mlbox')")
    s = pg.evaluate('window.__sent[0]')
    ok(len(s['n']) == 2 and s['k'] == ['rec', 'temp'], 'Sale un solo correo con los 2 PDF')
    ok(s['ar'] == 'conectandoensenada@gmail.com', 'Con copia al archivo')
    ok('l:LTEST1' in s['refs'], 'Lleva la referencia del lote para Gmail')
    e = pg.evaluate("ST.O.find(o=>o.ev=='rec')")
    ok(e and e['ok'] == 1 and e['fs'] == s['n'] and 'body' in e and e['body'] == '', 'Queda el renglón sin el mensaje')
    pg.evaluate("FOLD['ml-sent:l:LTEST1']=true;render()")
    t = pg.locator('#mlsent').inner_text()
    ok('1 correo' in t and 'Formato 02 · lote LTEST1' in t and 'quedó en el archivo' in t, 'El lote enseña el correo con sus PDF')
    href = pg.locator('#mlsent a.btn').get_attribute('href')
    ok(href.startswith('https://mail.google.com/mail/?authuser=conectandoensenada%40gmail.com#search/') and 'PROPESA%20lote%20LTEST1' in href, '«Ver en Gmail» busca el lote en el archivo')
    pg.screenshot(path=f'{OUT}/lote_enviados_1280.png', full_page=True)

    print('4 · Si no sale: rojo, campana y Reintentar')
    pg.evaluate("window.__fail='No hay conexión con el servidor de correo.'")
    pg.evaluate("document.querySelector('[data-pdf^=\"mail:rec\"]').click()")
    pg.wait_for_selector('#ml_send')
    pg.click('#ml_send')
    pg.wait_for_selector('.mlerr')
    ok('Quedó marcado en rojo' in pg.locator('.mlerr').inner_text(), 'El borrador dice que quedó en rojo')
    pg.click('.mlft [data-mlclose]')
    n = pg.evaluate("ST.O.filter(o=>o.ev=='rec'&&!o.ok).length")
    ok(n == 1, 'Queda un renglón «No se envió»')
    ok(pg.evaluate("ntFalta().some(x=>/No se envió el correo/.test(x.ti))"), 'La campana avisa')
    pg.evaluate("render()")
    ok(pg.locator('#mlsent li.bad').count() == 1, 'El renglón sale en rojo, con el plegable abierto')
    pg.evaluate("window.__fail=null")
    pg.click('#mlsent [data-mlre]')
    pg.wait_for_selector('#ml_send')
    ok(pg.locator('#ml_atts .mlatt').count() == pg.evaluate("ST.O.find(o=>o.ev=='rec'&&!o.ok).pk.length") == 1, 'Reintentar trae los mismos PDF del intento')
    pg.click('#ml_send')
    pg.wait_for_function("!document.querySelector('#mlroot .mlbox')")
    ok(pg.evaluate("ST.O.filter(o=>o.ev=='rec'&&!o.ok).length") == 0, 'Al salir, deja de estar en rojo')
    ok(not pg.evaluate("ntFalta().some(x=>/No se envió el correo/.test(x.ti))"), 'La campana ya no avisa')
    ok(pg.evaluate("ST.O.filter(o=>o.ev=='rec').length") == 2, 'Un renglón por correo (el reintento no duplica)')

    print('5 · Embarque cerrado: informe + packing list juntos; se ve en la Orden')
    pg.evaluate("mlOpen('emb',String(window.__i),null)")
    pg.wait_for_selector('#ml_send')
    names = pg.locator('#ml_atts .mlatt b').all_inner_texts()
    ok(len(names) == 2 and names[0].startswith('Informe de embarque') and names[1].startswith('Packing list'), 'Abre con el informe y el packing list')
    rest = pg.evaluate("mlRest(MLD).map(c=>c.n)")
    ok(any(x.startswith('Orden de empaque') for x in rest) and 'PDF del camión' in rest, '«+ Agregar PDF» ofrece la orden y el camión')
    pg.click('#ml_send')
    pg.wait_for_function("!document.querySelector('#mlroot .mlbox')")
    s = pg.evaluate('window.__sent[window.__sent.length-1]')
    oid = pg.evaluate('String(window.__o)')
    ok(('o:' + oid) in s['refs'] and ('e:' + pg.evaluate('window.__u')) in s['refs'], 'Lleva la referencia del embarque y de su orden')
    pg.evaluate("go('orden:'+window.__o)")
    pg.evaluate("FOLD['ml-sent:o:'+window.__o]=true;render()")
    t = pg.locator('#mlsent').inner_text()
    ok('Embarque cerrado' in t and 'Informe de embarque' in t and 'Packing list' in t, 'La orden enseña el correo del embarque con sus 2 PDF')
    pg.screenshot(path=f'{OUT}/orden_enviados_1280.png', full_page=True)

    print('6 · Muy pesado: no deja enviar')
    pg.evaluate("mlOpen('emp',String(window.__o),null)")
    pg.wait_for_selector('#ml_send')
    pg.evaluate("MLD.att[0].d={...MLD.att[0].d,u8:new Uint8Array(3.2*1024*1024)};mlAttRedraw()")
    ok('Muy pesado' in pg.locator('#ml_tot').inner_text(), 'Dice «Muy pesado: quita un PDF»')
    before = pg.evaluate('window.__sent.length')
    pg.click('#ml_send')
    pg.wait_for_timeout(200)
    ok(pg.evaluate('window.__sent.length') == before, 'No manda nada')
    pg.click('.mlft [data-mlclose]')

    print('7 · Administración → Correos')
    pg.evaluate("ADT='mail';go('admin')")
    pg.wait_for_selector('#mlar')
    ok(pg.locator('#mla_e').input_value() == 'conectandoensenada@gmail.com', 'Archivo en Gmail con el correo de siempre')
    pg.fill('#mla_e', 'otro.archivo@gmail.com')
    pg.click('[data-mle=ar]')
    pg.wait_for_timeout(150)
    ok(pg.evaluate("mlArch().e") == 'otro.archivo@gmail.com', 'El archivo se cambia desde la app')
    pg.click('[data-mle=sw]'); pg.click('[data-mle=ar]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("mlArchTo()") == '', 'La copia se puede apagar')
    pg.click('[data-mle=sw]'); pg.fill('#mla_e', 'conectandoensenada@gmail.com'); pg.click('[data-mle=ar]'); pg.wait_for_timeout(150)
    pg.click('[data-mle="ed:rec"]')
    pg.wait_for_selector('#mle_p')
    ok(pg.locator('#mle_f [data-mle="m:off"]').count() == 1, 'Cada paso tiene «Apagado»')
    pg.check('input[name=mle_p][value=temp]')
    pg.click('[data-mle=sv]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("mlCfg('rec').p") == ['rec', 'temp'], 'Las casillas cambian los PDF del paso')
    ok('Formato 02 (recepción) + Monitoreo de temperatura' in pg.locator('#mlev table').inner_text(), 'La tabla dice los PDF de cada paso')
    pg.screenshot(path=f'{OUT}/admin_correos_1280.png', full_page=True)
    pg.click('[data-mle="ed:rec"]'); pg.wait_for_selector('#mle_p')
    pg.uncheck('input[name=mle_p][value=temp]'); pg.uncheck('input[name=mle_p][value=rec]')
    pg.click('[data-mle=sv]'); pg.wait_for_timeout(150)
    ok('al menos un PDF' in pg.locator('#mle_m').inner_text(), 'Sin PDF marcados no guarda y lo dice junto al botón')
    pg.click('[data-mle="m:off"]'); pg.click('[data-mle=sv]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("mlCfg('rec').m") == 'off', '«Apagado» se guarda')
    pg.evaluate("go('lote:LTEST1')")
    ok(pg.locator('[data-pdf^="mail:rec"]').count() == 0 and pg.locator('[data-pdf^="dl:rec"]').count() >= 1, 'Apagado: sin botón de correo (el PDF se sigue descargando)')
    pg.evaluate("mlAfter('rec','rec','LTEST1')"); pg.wait_for_timeout(700)
    ok(pg.locator('#mlroot .mlbox').count() == 0, 'Apagado: al terminar el paso no se abre nada')

    print('8 · Enviar solo que falla')
    pg.evaluate("ST.NE={...ST.NE,emp:{m:'auto',to:['u:1'],cc:[],s:'',b:''}};window.__fail='Sin internet.';mlAfter('emp','emp',String(window.__o))")
    pg.wait_for_selector('.mlerr', timeout=4000)
    ok(pg.evaluate("ST.O.some(o=>o.ev=='emp'&&!o.ok)"), 'Queda en rojo y se abre el borrador con el aviso')
    pg.click('.mlft [data-mlclose]')
    pg.evaluate("window.__fail=null")

    print('9 · Se guarda y se comparte igual')
    r = pg.evaluate("""(()=>{const o=ST.O.find(x=>x.ev=='emb'),w=WN.O(o),c=cleanST({...mqDump(),O:[o]}).O[0],a=neClean({...ST.NE.arch,ev:'arch'}),bad=WN.O({...o,rf:['l:<x>'],pk:['rec|"a'],cc:['no es correo']});
      return{w:w.rf.length&&w.fs.length&&w.ok===1&&w.ev=='emb',c:c&&c.rf.join()==o.rf.join()&&c.ok===1,a:a.e=='conectandoensenada@gmail.com'&&a.on===true,bad:!bad.rf.length&&!bad.pk.length&&!bad.cc.length,
        old:JSON.stringify(WN.O({u:'abc123def',subject:'x',t:'t',to:[],body:'b',pn:'n',att:'a.pdf',pu:'u1'}))}})()""")
    ok(r['w'], 'El registro viaja a la base con sus PDF y referencias')
    ok(r['c'], 'El respaldo lo conserva')
    ok(r['a'], 'El archivo de Gmail viaja como ajuste compartido')
    ok(r['bad'], 'Lo que llega mal de otro equipo se descarta')
    ok('"ev"' not in r['old'], 'Los informes de cierre viejos no cambian')

    print('10 · Celular y tablet')
    for w, h in ((390, 844), (768, 1024)):
        pg.set_viewport_size({'width': w, 'height': h})
        pg.evaluate("ST.NE={...ST.NE,rec:{...ST.NE.rec,m:'rev'}};go('lote:LTEST1');FOLD['ml-sent:l:LTEST1']=true;render()")
        pg.wait_for_timeout(200)
        ov = pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
        ok(ov <= 1, f'{w} px: el lote no se sale de la pantalla')
        pg.locator('#mlsent').scroll_into_view_if_needed()
        pg.screenshot(path=f'{OUT}/lote_enviados_{w}.png')
        pg.evaluate("document.querySelector('[data-pdf^=\"mail:rec\"]').click()")
        pg.wait_for_selector('#ml_atts')
        ov = pg.evaluate("(()=>{const b=document.querySelector('#mlroot .mlbox');return b.scrollWidth-b.clientWidth})()")
        ok(ov <= 1, f'{w} px: el borrador no se sale de la pantalla')
        pg.screenshot(path=f'{OUT}/borrador_{w}.png')
        pg.click('.mlft [data-mlclose]')

    ok(not errs, 'Sin errores de JavaScript' + (': ' + ' | '.join(errs[:3]) if errs else ''))
    b.close()

if srv: srv.terminate()
print('TODO BIEN' if not MAL else f'FALLARON {len(MAL)}: ' + '; '.join(MAL))
sys.exit(1 if MAL else 0)
