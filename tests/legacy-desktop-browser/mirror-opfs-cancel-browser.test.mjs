import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {spawn} from 'node:child_process';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';import {join} from 'node:path';
const profile=await mkdtemp(join(tmpdir(),'codi-storage-abort-')),http=spawn('python3',['-m','http.server','19926','--bind','127.0.0.1'],{stdio:'ignore'});let browser;
try{await new Promise(r=>setTimeout(r,300));browser=await puppeteer.launch({executablePath:process.env.CHROME,userDataDir:profile,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});const page=await browser.newPage();await page.goto('http://127.0.0.1:19926/');
 const result=await page.evaluate(async()=>{
  const {VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs'),{MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs'),scope='abort-'+crypto.randomUUID(),server={async list(){throw Error('offline')}};
  const real=new VerifiedContent(scope),m=new MirroredFiles({scope,server,content:real,retryMs:0});await m.write('/x','data');m.close();
  let terminated=0,posted=0,started;const entered=new Promise(r=>started=r),workerFactory=()=>{const url=URL.createObjectURL(new Blob(['self.onmessage=()=>{}'],{type:'text/javascript'})),worker=new Worker(url),post=worker.postMessage.bind(worker),stop=worker.terminate.bind(worker);worker.postMessage=(...args)=>{posted++;post(...args);started()};worker.terminate=()=>{terminated++;URL.revokeObjectURL(url);stop()};return worker};
  const content=new VerifiedContent(scope,{workerFactory}),mirror=new MirroredFiles({scope,server,content,retryMs:0}),ctrl=new AbortController(),pending=mirror.readBounded('/x',100,{signal:ctrl.signal}).then(()=>null,e=>e.name);
  await entered;ctrl.abort();const name=await pending;await new Promise(r=>setTimeout(r,10));mirror.close();
  let closedCount=0,closedStarted;const closeEntered=new Promise(r=>closedStarted=r),closeFactory=()=>{const url=URL.createObjectURL(new Blob(['self.onmessage=()=>{}'],{type:'text/javascript'})),worker=new Worker(url),post=worker.postMessage.bind(worker),stop=worker.terminate.bind(worker);worker.postMessage=(...args)=>{post(...args);closedStarted()};worker.terminate=()=>{closedCount++;URL.revokeObjectURL(url);stop()};return worker};
  const c2=new VerifiedContent(scope,{workerFactory:closeFactory}),m2=new MirroredFiles({scope,server,content:c2,retryMs:0}),wait=m2.readBounded('/x',100).then(()=>null,e=>e.name);await closeEntered;m2.close();const closedResult=await wait;await new Promise(r=>setTimeout(r,10));
  const earlyCtrl=new AbortController();let earlyPosts=0,earlyStops=0;
  const earlyFactory=()=>{earlyCtrl.abort();return {postMessage(){earlyPosts++},terminate(){earlyStops++}}};
  const c3=new VerifiedContent(scope,{workerFactory:earlyFactory}),m3=new MirroredFiles({scope,server,content:c3,retryMs:0});
  const earlyResult=await m3.readBounded('/x',100,{signal:earlyCtrl.signal}).then(()=>null,e=>e.name);m3.close();
  return {name,posted,terminated,closedResult,closedCount,earlyResult,earlyPosts,earlyStops};
 });assert.deepEqual(result,{name:'AbortError',posted:1,terminated:1,closedResult:'AbortError',closedCount:1,earlyResult:'AbortError',earlyPosts:0,earlyStops:1});console.log('PASS aborted bounded read and mirror close terminate verification workers');
}finally{await browser?.close();http.kill('SIGTERM');await rm(profile,{recursive:true,force:true})}
