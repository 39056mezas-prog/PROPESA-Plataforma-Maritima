// Lighthouse (accesibilidad) en cada pantalla. Requiere: npm i lighthouse puppeteer-core ; servidor en :8765. Uso: node pruebas/accesibilidad.mjs pruebas/datos/backup.json
import puppeteer from 'puppeteer-core';import {snapshot} from 'lighthouse';import fs from 'fs';
const bk=fs.readFileSync(process.argv[2],'utf8');
const br=await puppeteer.launch({executablePath:process.env.CHROME_PATH||'/opt/pw-browsers/chromium',args:['--no-sandbox']});
const pg=await br.newPage();await pg.setViewport({width:1280,height:860});
pg.on('dialog',d=>d.accept());
await pg.goto(process.env.BASE||'http://localhost:8765/index.html?modo=local');/* modo local: nunca toca la base real */await pg.evaluate(()=>localStorage.clear());await pg.reload();
const res={};const top=[];
const run=async(name)=>{const r=await snapshot(pg,{config:{extends:'lighthouse:default',settings:{onlyCategories:['accessibility']}}});const l=r.lhr;res[name]=Math.round(l.categories.accessibility.score*100);const bad=Object.values(l.audits).filter(a=>a.score===0&&a.scoreDisplayMode!=='notApplicable'&&a.scoreDisplayMode!=='manual');if(bad.length)res[name+'_issues']=bad.map(a=>a.id+': '+(a.details?.items||[]).slice(0,3).map(i=>(i.node?.selector||'')+' '+(i.node?.explanation||'').slice(0,160)).join(' | '));};
await run('configuracion');
await pg.evaluate(b=>{localStorage.setItem('propesa-v4',b)},bk);await pg.reload();
await run('login');
await pg.type('#le','admin@propesa.mx');await pg.type('#lp','admin123');await pg.keyboard.press('Enter');await new Promise(r=>setTimeout(r,300));
for(const r of ['inicio','recepcion','ordenes','empaque','empacar:1.1','embarques','emb:0','cierre','temperatura','admin']){await pg.evaluate(x=>{window.scrollTo(0,0);go(x)},r);await new Promise(r=>setTimeout(r,200));await run(r)}
await pg.evaluate(()=>setPiso(true));await new Promise(r=>setTimeout(r,500));await run('piso');
await pg.evaluate(()=>go('pemp'));await new Promise(r=>setTimeout(r,300));await run('piso_empacar');
await pg.evaluate(()=>{PEN=null;go('pent')});await new Promise(r=>setTimeout(r,300));await pg.click('[data-pa=add]');await pg.select('[data-pr="1:origin"]','1');await pg.type('[data-pr="1:lot"]','wlrco131026');await pg.click('[data-pa="more:1"]');await pg.click('[data-pa=save]');await new Promise(r=>setTimeout(r,300));await run('piso_entradas');
console.log(JSON.stringify(res,null,1));await br.close();
