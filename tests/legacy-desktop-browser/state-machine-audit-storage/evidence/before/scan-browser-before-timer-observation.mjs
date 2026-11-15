// Strict-CSP actual Chromium/IDB/OPFS/Worker regression. Remote adapters are
// controlled single-account fixtures, not a signed gateway or browser UI.
import assert from 'node:assert/strict';import fs from 'node:fs/promises';import crypto from 'node:crypto';import http from 'node:http';import {pathToFileURL} from 'node:url';
const out=process.env.CODI_AUDIT_OUTPUT;assert(out);await assert.rejects(fs.stat(out));const repo=new URL('../../',import.meta.url);
const paths=['mirror.mjs','verified-content.mjs','opfs/store.mjs','opfs/worker.mjs','opfs/core.mjs','opfs/shared.mjs'];
const sources=Object.fromEntries(paths.map(p=>['/'+p,new URL('active-system/storage/browser/'+p,repo)])),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const sourcePins=Object.fromEntries(await Promise.all(Object.entries(sources).map(async([k,p])=>[k,sha(await fs.readFile(p))]))),requests=new Set();
const server=http.createServer(async(req,res)=>{res.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self'; worker-src 'self'; connect-src 'self'; object-src 'none'");if(req.url==='/'){res.end('<!doctype html><title>Owned scan regression</title>');return;}if(!sources[req.url]){res.writeHead(404);res.end();return;}requests.add(req.url);res.setHeader('Content-Type','text/javascript');res.end(await fs.readFile(sources[req.url]));});await new Promise(r=>server.listen(0,'127.0.0.1',r));
const {default:puppeteer}=await import(pathToFileURL(process.env.PUPPETEER_CORE_PATH??'/tmp/codi-occt-release-control/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js'));let browser;const contexts=[],receipt={status:'RUNNING',scope:'Actual Chromium module/IDB/OPFS Workers and real retry timers; controlled remote adapters; no signed service/UI/filesystem-race claim',sourcePins,rows:[]};
try{browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP??'http://127.0.0.1:19329'});
 for(const mode of ['legacy-idb','opfs-v2']){
  const context=await browser.createBrowserContext();contexts.push(context);const page=await context.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/`);
  const result=await page.evaluate(async mode=>{
   const NativeWorker=Worker,live=new Set();let created=0,terminated=0;globalThis.Worker=class extends NativeWorker{constructor(...args){super(...args);created++;live.add(this);}terminate(){if(live.delete(this))terminated++;super.terminate();}};
   const {MirroredFiles}=await import('/mirror.mjs'),{VerifiedContent}=await import('/verified-content.mjs');const enc=new TextEncoder(),dec=new TextDecoder();
   const digest=async x=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',enc.encode(x))),b=>b.toString(16).padStart(2,'0')).join(''),gate=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};
   const fixture=()=>{const data=new Map();let lists=0,reads=0;const server={supportsVersion:async()=>true,list:async()=>{lists++;return{entries:[...data.keys()].map(name=>({name,directory:false}))};},version:async p=>({sha256:await digest(data.get(p))}),read:async p=>{reads++;const text=data.get(p);return{data:enc.encode(text),sha256:await digest(text)};}};return{data,server,get lists(){return lists;},get reads(){return reads;}};};
   const open=(f,{scope='browser-scan:'+crypto.randomUUID(),retryMs=0}={})=>new MirroredFiles({scope,server:f.server,retryMs,...(mode==='opfs-v2'?{content:new VerifiedContent(scope)}:{})});
   const text=async(f,p='/a')=>dec.decode((await f.read(p)).data),rows=[];
   {
    const f=fixture();f.data.set('a','one');f.data.set('b','other');let broken=true;const read=f.server.read;f.server.read=p=>p==='b'&&broken?Promise.reject(Error('B unavailable')):read(p);const mirror=open(f),stages=[];
    try{for(const[label,a,b]of[['first','one',true],['A-changes-B-fails','two',true],['B-recovers','three',false]]){f.data.set('a',a);broken=b;let error=null;try{await mirror.sync();}catch(e){error=e.message;}stages.push({label,a:await text(mirror),error,status:await mirror.status()});}rows.push({id:'fresh-partial-recovery',stages});}finally{mirror.close();}
   }
   {
    const f=fixture();for(let i=0;i<12;i++)f.data.set('file'+String(i).padStart(2,'0'),'value '+i);let remaining=0,versions=0;const list=f.server.list,version=f.server.version,times=[];f.server.list=async()=>{times.push(Date.now());remaining=3;return list();};f.server.version=async p=>{if(remaining--<=0)throw Object.assign(Error('rate limited'),{status:429});versions++;return version(p);};
    const mirror=open(f,{retryMs:15});let timeout,off;
    try{const status=await new Promise((resolve,reject)=>{timeout=setTimeout(()=>reject(Error('Automatic continuation did not finish')),20000);off=mirror.subscribe(()=>{mirror.status().then(s=>{if(s.lastSynced!==null&&!s.error&&s.verification?.attempts===4)resolve(s);},reject);});});clearTimeout(timeout);off();const listing=await mirror.list('/');const bodies=[];for(const e of listing.entries)bodies.push(await text(mirror,e.path));rows.push({id:'real-automatic-timer-continuation',explicitSyncCalls:0,lists:f.lists,versions,times,status,bodies});}finally{clearTimeout(timeout);off?.();mirror.close();}
   }
   {
    const f=fixture();f.data.set('a','one');const started=gate(),release=gate(),read=f.server.read;let held=true;f.server.read=async p=>{const response=await read(p);if(held){held=false;started.resolve();await release.promise;}return response;};const mirror=open(f);
    try{const first=mirror.sync({continuation:true});await started.promise;f.data.set('a','two');const second=mirror.sync(),third=mirror.sync();const samePromise=first===second&&second===third;release.resolve();await first;rows.push({id:'coalesced-fresh-followup',samePromise,lists:f.lists,reads:f.reads,a:await text(mirror),status:await mirror.status()});}finally{release.resolve();mirror.close();}
   }
   {
    const f=fixture();f.data.set('a','one');const scope='browser-close:'+crypto.randomUUID();let mirror=open(f,{scope});await mirror.sync();f.data.set('a','two');const started=gate(),release=gate(),read=f.server.read;f.server.read=async p=>{const response=await read(p);started.resolve();await release.promise;return response;};const work=mirror.sync();await started.promise;mirror.close();release.resolve();const error=await work.then(()=>null,e=>e.message);f.server.read=read;mirror=open(f,{scope});try{rows.push({id:'close-held-read-preserves',error,a:await text(mirror)});}finally{mirror.close();}
   }
   return{mode,rows,workers:{created,terminated,live:live.size}};
  },mode);
  const [fresh,timer,coalesced,closed]=result.rows;
  assert.deepEqual(fresh.stages.map(s=>s.a),['one','two','three']);assert.match(fresh.stages[0].error,/B unavailable/);assert.match(fresh.stages[1].error,/B unavailable/);assert.equal(fresh.stages[2].error,null);assert.equal(fresh.stages[2].status.verification.historicalChecks,0);
  assert.equal(timer.explicitSyncCalls,0);assert.equal(timer.lists,4);assert.equal(timer.versions,12);assert.equal(timer.bodies.length,12);assert.deepEqual(timer.bodies,Array.from({length:12},(_,i)=>'value '+i));assert.equal(timer.status.verification.historicalChecks,9);assert.equal(timer.status.lastSynced,timer.status.verification.oldestCheckAt);assert(timer.status.verification.completedAt>timer.status.lastSynced);
  assert.equal(coalesced.samePromise,true);assert.equal(coalesced.lists,2);assert.equal(coalesced.reads,2);assert.equal(coalesced.a,'two');assert.equal(coalesced.status.verification.historicalChecks,0);assert.match(closed.error,/Account changed|closed|Cancelled/);assert.equal(closed.a,'one');assert.equal(result.workers.live,0);assert.equal(result.workers.created,result.workers.terminated);if(mode==='opfs-v2')assert(result.workers.created>0);
  receipt.rows.push(result);await context.close();contexts.splice(contexts.indexOf(context),1);
 }
 assert(paths.every(p=>requests.has('/'+p)));receipt.requests=[...requests];receipt.status='PASS_COMPONENT_REGRESSION';
}catch(e){receipt.status='FAIL';receipt.error={message:e.message,stack:e.stack};throw e;}
finally{for(const context of contexts)await context.close();if(browser)await browser.disconnect();await new Promise(r=>server.close(r));receipt.producerSha256=sha(await fs.readFile(new URL(import.meta.url)));await fs.writeFile(out,JSON.stringify(receipt,null,2)+'\n');}
