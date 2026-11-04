import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import puppeteer from 'puppeteer-core';
import {spawn} from 'node:child_process';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

const port=Number(process.env.CODI_TEST_PORT||19962);
if(!Number.isInteger(port)||port<1024||port>65535)throw Error('Invalid test port');
const size=2*1024*1024+37,rounds=12,source=Buffer.allocUnsafe(size);
for(let i=0;i<size;i++)source[i]=i%251;
const expected=crypto.createHash('sha256').update(source).digest('hex');
const profile=await mkdtemp(join(tmpdir(),'codi-detached-lifetime-'));
const http=spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1'],{stdio:'ignore'});let browser;
try{
 await new Promise(r=>setTimeout(r,300));
 browser=await puppeteer.launch({executablePath:process.env.CHROME,userDataDir:profile,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage();await page.goto(`http://127.0.0.1:${port}/`);
 const result=await page.evaluate(async({size,rounds,expected})=>{
  const active=new Set(),actions=[],original=window.Worker;
  class TrackedWorker extends original {constructor(...args){super(...args);active.add(this)}postMessage(value,...args){if(value?.action)actions.push(value.action);return super.postMessage(value,...args)}terminate(){active.delete(this);return super.terminate()}}
  window.Worker=TrackedWorker;
  const {MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs');
  const {VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs');
  const scope='detached-lifecycle-'+crypto.randomUUID(),open=()=>{const content=new VerifiedContent(scope);return {content,mirror:new MirroredFiles({scope,server:{async list(){throw Error('offline')}},content,retryMs:0})}};let {mirror:m,content}=open();
  const bytes=new Uint8Array(size);for(let i=0;i<size;i++)bytes[i]=i%251;
  await m.write('/file',new Blob([bytes]));m.close();content.close();
  const hex=b=>Array.from(new Uint8Array(b),v=>v.toString(16).padStart(2,'0')).join('');
  const check=async blob=>hex(await crypto.subtle.digest('SHA-256',await blob.arrayBuffer()));
  const settle=async()=>{for(let n=0;n<100;n++){const locks=await navigator.locks.query();const relevant=locks.held.filter(x=>x.name.startsWith('codi-content:')||x.name==='codi-file-heavy-worker/1'||x.name.startsWith('codi-opfs:'));if(!active.size&&!relevant.length)return;if(n===99)throw Error('worker or storage lock not released');await new Promise(r=>setTimeout(r,20))}};
  let urlsCreated=0,urlsRevoked=0,activeUrls=new Set(),heap=[];
  for(let i=0;i<rounds;i++){
   ({mirror:m,content}=open());const {data}=await m.readBlob('/file');if(data.size!==size||await check(data)!==expected)throw Error('detached bytes mismatch');
   const url=URL.createObjectURL(data);urlsCreated++;activeUrls.add(url);
   try{const response=await fetch(url);if(!response.ok||hex(await crypto.subtle.digest('SHA-256',await response.arrayBuffer()))!==expected)throw Error('object URL mismatch')}finally{URL.revokeObjectURL(url);urlsRevoked++;activeUrls.delete(url)}
   let revoked=false;try{await fetch(url)}catch{revoked=true}if(!revoked)throw Error('revoked URL still fetchable');
   m.close();content.close();await settle();if(performance.memory)heap.push(performance.memory.usedJSHeapSize);
  }
  ({mirror:m,content}=open());const held=(await m.readBlob('/file')).data;m.close();content.close();await settle();if(await check(held)!==expected)throw Error('caller-held Blob invalid after close');
  if(activeUrls.size||active.size)throw Error('test resources remain active');
  return {size,rounds,expected,urlsCreated,urlsRevoked,workersStarted:actions.length,actions,activeWorkers:active.size,activeUrls:activeUrls.size,heap,heldAfterClose:true};
 },{size,rounds,expected});
 assert.equal(result.urlsCreated,rounds);assert.equal(result.urlsRevoked,rounds);assert.equal(result.activeWorkers,0);assert.equal(result.activeUrls,0);assert.equal(result.heldAfterClose,true);assert.ok(result.actions.filter(x=>x==='copy').length>=rounds);
 console.log('PASS detached OPFS repeated read/drop/close',JSON.stringify(result));
}finally{await browser?.close();http.kill('SIGTERM');await rm(profile,{recursive:true,force:true})}
