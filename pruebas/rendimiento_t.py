"""Prueba PROPESA (rendimiento_t). Uso: python3 -m http.server 8765 en la carpeta del proyecto y luego python3 -I pruebas/rendimiento_t.py"""
import json,sys
from playwright.sync_api import sync_playwright
import os,shutil,tempfile
BASE=os.environ.get('BASE','http://localhost:8765/index.html')
OUT=os.environ.get('OUT') or tempfile.mkdtemp(prefix='propesa-');os.makedirs(OUT,exist_ok=True)
_D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'datos')
for _f in os.listdir(_D):shutil.copy(os.path.join(_D,_f),OUT)
T=OUT.rstrip('/')+'/'
FIX="localStorage.clear();localStorage.setItem('propesa-v4',JSON.stringify({PK:1,BN:0,L:[],N:0,R:[],B:{},P:[],O:[],M:{},OR:[],ORc:1,E0:1,T:[],RN:120,U:[{id:1,name:'Ana Torres',email:'admin@propesa.mx',pw:'admin123',role:'admin',notify:true},{id:2,name:'Luis Meza',email:'piso@propesa.mx',pw:'piso123',role:'piso',notify:true},{id:3,name:'Dirección',email:'consulta@propesa.mx',pw:'ver123',role:'consulta',notify:false}]}))"  # usuarios SOLO para pruebas

GEN=r"""(days)=>{const S0=S,R=[],L=[],B={},OR=[],P=[];let N=0,seq=0;const sh=(i)=>i;
 for(let d=0;d<days;d++){const dt=new Date(2026,0,1+d),ds=dLoc(dt);
  for(let k=0;k<2;k++){const lot='L'+String(d).padStart(3,'0')+k;R.push({id:'R-'+(1000+d*2+k),lot,origin:'SCPP '+(k?'Sur':'Norte'),tank:'T'+(1+(d+k)%6),rdate:ds,time:'08:00',date:fd(ds),tempT:58,tempP:'59-62',kgbox:18,desp:2,final:null,closed:d<days-10});B[lot]=[];
   S0.forEach((s,i)=>L.push({id:++N,t:'x',type:'RECEPCION',lot,size:s,m:400000,rev:0,rc:''}))}
  const o={id:d+1,etd:ds,lines:[],sh:{}};const pi=P.length;P.push({n:'PVG · YISHUNHAI · '+fs(ds),z0:'',col:'#1c7f9a',exp:0,h:150,z:[40,40,40,30],c:[['Hieleras',1.4,150],['Gel ice',1.5,150],['Producto',16,150],['Caja de cartón',0.7,150]],alive:d<days-5?140*20:null,closed:d<days-3});P[pi].exp=gross(P[pi]);o.sh['PVG|0']=pi;
  for(let j=0;j<5;j++){o.lines.push({id:j+1,city:'PVG',cons:0,cli:['HXH','ZSM','LHD','RSK','HSF'][j],boxes:30});const lot='L'+String(d).padStart(3,'0')+(j%2);
   for(let b=0;b<(d<days-1?30:10);b++)B[lot].push({c:18+b%9,k:'RVB'[b%3],d:pi,o:o.id+'.'+(j+1),seq:++seq})}
  OR.push(o)}
 ST.R=R;ST.L=L;ST.B=B;ST.OR=OR;ST.P=P;ST.N=N;ST.BN=seq;const t0=performance.now();const ok=save();return{ok,saveMs:performance.now()-t0,bytes:JSON.stringify(ST).length,lots:R.length,boxes:seq,orders:OR.length,ships:P.length}}"""
ROUTES=['inicio','recepcion','ordenes','orden:%d','empaque','empacar:%d.1','embarques','emb:%d','cierre','piso','pemp:%d.1']
days=int(sys.argv[1]) if len(sys.argv)>1 else 250
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1180,'height':820})
    pg.goto(BASE);pg.evaluate(FIX);pg.reload()
    pg.fill('#le','admin@propesa.mx');pg.fill('#lp','admin123');pg.click('[data-a=lg]')
    info=pg.evaluate(GEN,days);print('DATA',info)
    cdp=pg.context.new_cdp_session(pg)
    for rate in [1,4]:
        cdp.send('Emulation.setCPUThrottlingRate',{'rate':rate})
        res={}
        for r in ROUTES:
            rr=r%days if '%d' in r else r
            if rr in('piso','pemp:%d.1'%days):pg.evaluate("setPiso(true)")
            ms=pg.evaluate("r=>{const t=[];for(let i=0;i<3;i++){const a=performance.now();go(r);t.push(performance.now()-a)}return Math.min(...t)}",rr)
            pg.evaluate("setPiso(false)");res[rr]=round(ms)
        print(f'CPUx{rate} render ms',res)
        # interaction: tap category in piso to save a box (save + render)
        pg.evaluate(f"setPiso(true);go('pemp:{days}.1')")
        if pg.locator('[data-pe^="lot:"]').count():pg.click('[data-pe^="lot:"] >> nth=0')
        t=pg.evaluate("""()=>{const i=document.querySelector('.ppc');if(!i)return -1;i.value='20';i.dispatchEvent(new Event('input',{bubbles:true}));const no=i.dataset.slot;kpGo('slot:'+no);const btn=document.querySelector('#kpad [data-kp="k:R"]');const a=performance.now();btn.click();return performance.now()-a}""")
        print(f'CPUx{rate} guardar una caja (modo piso) ms',round(t))
        k=pg.evaluate("()=>{const a=performance.now();for(let i=0;i<20;i++)save();return (performance.now()-a)/20}");print(f'CPUx{rate} save() promedio ms',round(k,1))
        pg.evaluate("setPiso(false)")
    b.close()
