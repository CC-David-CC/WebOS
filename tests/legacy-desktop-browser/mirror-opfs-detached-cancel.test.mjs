// Real OPFS copy: abort after an actual copy-worker progress message. The
// caller's account stays valid and a subsequent verified read must succeed.
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {createServer} from 'node:http';
import {readFile,mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(fileURLToPath(new URL('..',import.meta.url))),profile=await mkdtemp(join(tmpdir(),'codi-copy-cancel-'));
const server=createServer(async(req,res)=>{try{const path=resolve(root,'.'+new URL(req.url,'http://localhost').pathname);if(path!==root&&!path.startsWith(root+sep))throw Error('path');const data=await readFile(path);res.writeHead(200,{'Content-Type':path.endsWith('.mjs')?'text/javascript':'text/html'});res.end(data)}catch{res.writeHead(404);res.end()}});
let browser;
try{
 await new Promise((yes,no)=>{server.once('error',no);server.listen(0,'127.0.0.1',yes)});
 browser=await puppeteer.launch({executablePath:process.env.CHROME,userDataDir:profile,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/tests/files-copy-pass-evidence-20261104.md`);
 const result=await page.evaluate(async()=>{
  const {MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs'),{VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs');
  const scope='detached-copy-cancel',content=new VerifiedContent(scope),m=new MirroredFiles({scope,server:{async list(){throw Error('offline')}},content,valid:()=>true,retryMs:0}),ctrl=new AbortController();
  const source=new Uint8Array(8*1024*1024+7);for(let i=0;i<source.length;i++)source[i]=i%251;await m.write('/x',new Blob([source]));
  const Native=window.Worker;let progress=0,terminated=0;
  window.Worker=class extends Native{
   postMessage(msg,...rest){this.copy=msg?.action==='copy';return super.postMessage(msg,...rest)}
   set onmessage(fn){super.onmessage=e=>{if(this.copy&&e.data?.progress!==undefined){progress++;ctrl.abort();}fn(e)}}
   terminate(){if(this.copy)terminated++;return super.terminate()}
  };
  let outcome;try{outcome=await m.readBlob('/x',{signal:ctrl.signal}).then(()=>({accepted:true}),e=>({name:e.name,message:e.message}));}finally{window.Worker=Native;}
  let contentLocks=1;for(let i=0;i<100&&contentLocks;i++){const q=await navigator.locks.query();contentLocks=q.held.filter(x=>x.name.startsWith('codi-content:')).length;if(contentLocks)await new Promise(r=>setTimeout(r,10));}
  const later=await m.readBlob('/x'),sha=await crypto.subtle.digest('SHA-256',await later.data.arrayBuffer()),expected=await crypto.subtle.digest('SHA-256',source);
  m.close();return {outcome,progress,terminated,contentLocks,match:[...new Uint8Array(sha)].join(',')===[...new Uint8Array(expected)].join(',')};
 });
 console.log('COPY_ABORT_OBSERVED',JSON.stringify(result));assert.ok(result.progress>0,'real copy worker never reported progress');assert.equal(result.outcome.name,'AbortError');assert.equal(result.terminated,1);assert.equal(result.contentLocks,0);assert.equal(result.match,true);
 console.log('PASS actual OPFS copy abort releases its worker/lock and later verified read succeeds',JSON.stringify(result));
}finally{await browser?.close();await new Promise(r=>server.close(r));await rm(profile,{recursive:true,force:true});}
