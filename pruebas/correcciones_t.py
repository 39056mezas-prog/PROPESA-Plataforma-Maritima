"""Prueba PROPESA (correcciones_t). Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/correcciones_t.py"""
import json,datetime
from playwright.sync_api import sync_playwright
import os,shutil,tempfile
BASE=os.environ.get('BASE','http://localhost:8765/index.html')
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
FIX="localStorage.clear();localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',pw:'admin123',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',pw:'piso123',role:'piso',notify:true},{id:3,name:'Dirección',email:'consulta@propesa.mx',pw:'ver123',role:'consulta',notify:false}]}))"  # usuarios SOLO para pruebas

seed=open(T+'seed.json').read();errs=[]
def chk(c,m):print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(timezone_id='America/Tijuana',accept_downloads=True);pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    pg.clock.set_fixed_time(datetime.datetime(2026,10,12,19,30,tzinfo=datetime.timezone(datetime.timedelta(hours=-7))))
    pg.goto(BASE);pg.evaluate('s=>{localStorage.clear();localStorage.setItem("propesa-v4",s)}',seed);pg.reload()
    # #2 (v1.4.1): la app ya no maneja contraseñas; en la base compartida las revisa Supabase. El modo local (solo pruebas) entra con el correo.
    chk(pg.evaluate("typeof sha256=='undefined'&&typeof pwHash=='undefined'&&typeof PWD0=='undefined'"),'#2 sin código de contraseñas en la app')
    chk('admin123' not in pg.inner_text('body') and pg.locator('[data-q]').count()==0,'#2 login screen has no demo buttons/passwords')
    pg.fill('#le','nadie@propesa.mx');pg.fill('#lp','x');pg.click('[data-a=lg]');chk('incorrectos' in pg.inner_text('#lm'),'#2 unknown email rejected')
    pg.fill('#le','ADMIN@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]');chk(pg.locator('.sb').count()==1,'#2 login works (email case-insensitive)')
    chk('contraseña de prueba' not in pg.inner_text('#app').lower(),'#2 sin aviso de contraseña de prueba')
    # 3 dates at 19:30 local
    pg.evaluate("go('recepcion')");pg.click('[data-a=nf]');chk(pg.input_value('#fd')=='2026-10-12','#3 reception date local: '+pg.input_value('#fd'))
    pg.evaluate("go('ordenes')");chk(pg.input_value('#no_etd')=='2026-10-13','#3 ETD tomorrow: '+pg.input_value('#no_etd'))
    chk(pg.evaluate("pdfName('Entrada')").endswith('2026-10-12.pdf'),'#3 PDF name date local')
    pg.evaluate("setPiso(true);PEN=null;go('pent')");chk(pg.evaluate("PEN.rows[0].d.rdate")=='2026-10-12','#3 piso entrada date local');pg.evaluate("setPiso(false);go('inicio')")
    # 6 lot ids unique after delete
    pg.evaluate("ST.R.push({id:'R-0123',lot:'TMP3',origin:'x',tank:'T1',final:null,closed:false});ST.B.TMP3=[];ST.R=ST.R.filter(r=>r.lot!=='WLRCO061026B');delete ST.B.WLRCO061026B;save();go('recepcion')")
    pg.click('[data-a=nf]');pg.fill('#fl','NUEVO');pg.fill('#fo','X');pg.fill('#fk0','5');pg.click('[data-a=sv]')
    ids=pg.evaluate("ST.R.map(r=>r.id)");chk(len(ids)==len(set(ids)),'#6 unique lot ids '+str(ids))
    # 5 closed shipment
    pg.evaluate("ST.P[0].z=[2,2,2,1];save();closeP(0);go('orden:1')")
    n0=pg.evaluate("ST.OR[0].lines.length");pg.select_option('#ol_city','PVG');pg.fill('#ol_cli','NEW');pg.fill('#ol_n','3');pg.click('[data-oa=ln]')
    chk(pg.evaluate("ST.OR[0].lines.length")==n0 and 'cerrado' in pg.inner_text('#toast'),'#5 line into closed shipment blocked')
    # 4 XSS via restore
    evil=json.loads(seed);evil['R'][0]['tank']='<img src=x onerror="window.__pwn=1">';evil['P'].append({'n':'<img src=x onerror="window.__pwn=1">','col':'red;background:url(x)','z':[0,0,0,0],'c':[],'h':0})
    evil['M']={'emp:1.1':[{'id':1,'t':'x','by':'<b>x</b>','text':'hola','ref':'','imgs':['javascript:alert(1)','data:image/png;base64,AAAA']}]}
    open(T+'evil.json','w').write(json.dumps(evil));pg.evaluate("go('admin')");pg.set_input_files('[data-bk=up]',T+'evil.json');pg.wait_for_timeout(300)
    for r in ['inicio','recepcion','lote:WLRCO051026A','embarques','emb:1','empacar:1.1','cierre']:
        pg.evaluate(f"go('{r}')");pg.wait_for_timeout(80)
    chk(not pg.evaluate('window.__pwn===1'),'#4 malicious backup cannot run code')
    chk(pg.evaluate("ST.R[0].tank")=='T1' and pg.evaluate("(ST.M['emp:1.1']||[{imgs:[]}])[0].imgs.length")==1,'#4 invalid fields sanitized')
    bad=json.loads(seed);bad['U']=[u for u in bad['U'] if u['role']!='admin'];open(T+'bad2.json','w').write(json.dumps(bad));nR=pg.evaluate('ST.R.length')
    pg.evaluate("go('admin')");pg.set_input_files('[data-bk=up]',T+'bad2.json');pg.wait_for_timeout(200);chk('Administrador' in pg.inner_text('#toast'),'#4 backup without admin rejected')
    # old backup with plain passwords still restores; passwords are dropped
    pg.evaluate("go('admin')");pg.set_input_files('[data-bk=up]',T+'backup.json');pg.wait_for_timeout(300);chk(pg.evaluate("ST.U.length>0&&ST.U.every(u=>!('pw' in u)&&!('pwh' in u))"),'#4 old backup restores without passwords')
    # 1 storage full
    pg.evaluate("(()=>{let n=0;for(const sz of [1<<20,1<<16,1<<12,256,16]){const s='x'.repeat(sz);while(true){try{localStorage.setItem('pad'+(n++),s)}catch(e){break}}}})()")
    pg.evaluate("go('recepcion')");pg.click('[data-a=nf]');pg.fill('#fl','PRUEBA');pg.fill('#fo','X');pg.fill('#fk0','10');pg.click('[data-a=sv]');pg.wait_for_timeout(100)
    chk('Guardado' not in pg.inner_text('#toast') and 'memoria' in pg.inner_text('#toast'),'#1 no false "Guardado": '+pg.inner_text('#toast'))
    chk('NO SE PUDO GUARDAR' in pg.inner_text('#app'),'#1 persistent red banner')
    pg.screenshot(path=T+'f_full.png')
    with pg.expect_download() as d: pg.click(".alb.tb [data-bk=dl]")
    dp=T+'rescue.json';d.value.save_as(dp);chk('PRUEBA' in open(dp).read(),'#1 backup download rescues unsaved data')
    pg.evaluate("for(let i=0;i<200;i++)localStorage.removeItem('pad'+i)");pg.click('[data-retry]');pg.wait_for_timeout(100)
    chk('NO SE PUDO GUARDAR' not in pg.inner_text('#app') and pg.evaluate("localStorage.getItem('propesa-v4').includes('PRUEBA')"),'#1 retry saves and clears banner')
    b.close()
print('ERRS',errs)
