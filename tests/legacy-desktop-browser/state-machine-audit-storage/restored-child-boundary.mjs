// Actual frozen production mirror. Controlled remote chronology; no private row
// writes, signed-service/UI claim, or filesystem race/security experiment.
import assert from 'node:assert/strict';import fs from 'node:fs/promises';import crypto from 'node:crypto';import http from 'node:http';import {pathToFileURL} from 'node:url';
const out=process.env.CODI_AUDIT_OUTPUT;assert(out);await assert.rejects(fs.stat(out));const root=new URL('../../',import.meta.url),names=['mirror.mjs','verified-content.mjs','opfs/store.mjs','opfs/worker.mjs','opfs/core.mjs','opfs/shared.mjs'];
const sources=Object.fromEntries(names.map(p=>['/'+p,new URL('active-system/storage/browser/'+p,root)])),sha=b=>crypto.createHash('sha256').update(b).digest('hex'),pins=Object.fromEntries(await Promise.all(Object.entries(sources).map(async([p,u])=>[p,sha(await fs.readFile(u))])));
assert.equal(pins['/mirror.mjs'],'5cc73d2af2a1cc79fe969934e2b85cf9fefe96aee4271a9d900ade4863081d9c','frozen b911 source required');
const server=http.createServer(async(req,res)=>{res.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self'; worker-src 'self'; connect-src 'self'; object-src 'none'");if(req.url==='/'){res.end('<!doctype html><title>Owned restoration boundary</title>');return;}if(!sources[req.url]){res.writeHead(404);res.end();return;}res.setHeader('Content-Type','text/javascript');res.end(await fs.readFile(sources[req.url]));});await new Promise(r=>server.listen(0,'127.0.0.1',r));
const {default:puppeteer}=await import(pathToFileURL(process.env.PUPPETEER_CORE_PATH??'/tmp/codi-occt-release-control/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js'));let browser;const contexts=[],receipt={status:'RUNNING',sourceCommit:'b911068263a467c366cfec784f7d6bbe0e1a228c',scope:'Frozen production mirror +actual Chromium IDB/OPFS, controlled remote chronology; no public deployment or physical-byte erasure claim',pins,rows:[]};
try{browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP??'http://127.0.0.1:19329'});
 for(const mode of ['legacy-idb','opfs-v2']){const ctx=await browser.createBrowserContext();contexts.push(ctx);const page=await ctx.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/`);
  const result=await page.evaluate(async mode=>{
   const NativeWorker=Worker,live=new Set();let created=0,terminated=0;globalThis.Worker=class extends NativeWorker{constructor(...a){super(...a);created++;live.add(this);}terminate(){if(live.delete(this))terminated++;super.terminate();}};
   const {MirroredFiles}=await import('/mirror.mjs'),{VerifiedContent}=await import('/verified-content.mjs'),enc=new TextEncoder(),dec=new TextDecoder(),hash=async text=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',enc.encode(text))),b=>b.toString(16).padStart(2,'0')).join('');
   const rows=[];
   for(const priorConflict of [false,true]){
    const remote=new Map([['projects',{directory:true}],['projects/child',{directory:false,text:'accepted protected child'}]]),operations=[];
    const server={supportsVersion:async()=>true,list:async path=>{const prefix=path?path+'/':'';return{entries:[...remote].filter(([p])=>p.startsWith(prefix)&&!p.slice(prefix.length).includes('/')).map(([p,n])=>({name:p.slice(prefix.length),directory:n.directory}))};},version:async p=>({sha256:await hash(remote.get(p).text)}),read:async p=>({data:enc.encode(remote.get(p).text),sha256:await hash(remote.get(p).text)}),write:async()=>{operations.push('write');throw Error('Unexpected write');},mkdir:async()=>{operations.push('mkdir');throw Error('Unexpected mkdir');},remove:async()=>{operations.push('remove');throw Error('Unexpected removal');}};
    const scope='child-boundary:'+crypto.randomUUID(),open=()=>new MirroredFiles({scope,server,retryMs:0,...(mode==='opfs-v2'?{content:new VerifiedContent(scope)}:{})});let f=open();
    const snapshot=async label=>{const parent=(await f.list('/')).entries.find(e=>e.path==='/projects');let child;try{const r=await f.read('/projects/child');child={text:dec.decode(r.data),sha256:r.sha256,version:r.version,status:r.status};}catch(e){child={error:e.message};}return{label,parent,child,status:await f.status()};};
    try{
     await f.sync();const stages=[await snapshot('accepted-initial')];
     if(priorConflict){remote.set('projects',{directory:false,text:'conflicting remote file'});remote.delete('projects/child');await f.sync();stages.push(await snapshot('wrong-kind-protects-child'));remote.set('projects',{directory:true});}else remote.delete('projects/child');
     await f.sync();stages.push(await snapshot(priorConflict?'directory-only-restored':'ordinary-child-deletion'));
     await f.sync();stages.push(await snapshot('repeated-sync'));
     f.close();f=open();stages.push(await snapshot('fresh-mirror-reopen-without-sync'));
     rows.push({id:priorConflict?'protected-side-directory-only-restoration':'ordinary-deletion-no-prior-conflict',priorConflict,stages,remoteOperations:operations});
    }finally{f.close();}
   }
   return{mode,rows,workers:{created,terminated,live:live.size}};
  },mode);receipt.rows.push(result);
  const[ordinary,protectedSide]=result.rows;assert.equal(ordinary.stages[0].child.text,'accepted protected child');assert.equal(ordinary.stages[1].child.error,'File not found.');assert.equal(ordinary.stages[1].status.conflicts,0);
  assert.equal(protectedSide.stages[1].parent.status,'conflict');assert.deepEqual(protectedSide.stages[1].child,protectedSide.stages[0].child);assert.equal(protectedSide.stages[2].parent.status,'synced');assert.equal(protectedSide.stages[2].child.error,'File not found.');assert.equal(protectedSide.stages[2].status.conflicts,0);assert.equal(protectedSide.stages[3].child.error,'File not found.');assert.equal(protectedSide.stages[4].child.error,'File not found.');assert.deepEqual(protectedSide.remoteOperations,[]);assert.equal(result.workers.live,0);assert.equal(result.workers.created,result.workers.terminated);await ctx.close();contexts.splice(contexts.indexOf(ctx),1);
 }
 receipt.status='CONFIRMED_PROTECTED_SIDE_LOGICAL_LOSS_ON_RESTORATION';
}catch(e){receipt.status='HARNESS_OR_UNEXPECTED_FAILURE';receipt.error={message:e.message,stack:e.stack};throw e;}
finally{for(const c of contexts)await c.close();if(browser)await browser.disconnect();await new Promise(r=>server.close(r));receipt.producerSha256=sha(await fs.readFile(new URL(import.meta.url)));await fs.writeFile(out,JSON.stringify(receipt,null,2)+'\n');}
