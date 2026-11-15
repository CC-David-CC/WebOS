import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {spawn} from 'node:child_process';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const profile=await mkdtemp(join(tmpdir(),'codi-copy-passes-'));
const http=spawn('python3',['-m','http.server','19952','--bind','127.0.0.1'],{stdio:'ignore'});let browser;
try{
 await new Promise(r=>setTimeout(r,300));browser=await puppeteer.launch({executablePath:process.env.CHROME,userDataDir:profile,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});const page=await browser.newPage();await page.goto('http://127.0.0.1:19952/');
 const result=await page.evaluate(async()=>{
  const actions=[];const original=Worker.prototype.postMessage;Worker.prototype.postMessage=function(m,...rest){if(['write','verify','copy','digest'].includes(m?.action))actions.push({action:m.action,size:typeof m.source==='number'?m.source:m.source?.size});return original.call(this,m,...rest)};
  const {MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs'),{VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs');const scope='copy-passes',content=new VerifiedContent(scope),m=new MirroredFiles({scope,server:{async list(){throw Error('offline')}},content,retryMs:0});
  const size=2*1024*1024+7,bytes=new Uint8Array(size);for(let i=0;i<size;i++)bytes[i]=i%251;const expected=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');await m.write('/sample',new Blob([bytes]));const capture=actions.splice(0);const lease=await m.acquireSnapshot('/sample');const snapshot=actions.splice(0);lease.release();const copied=(await m.readBlob('/sample')).data,read=actions.splice(0);const actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await copied.arrayBuffer())),b=>b.toString(16).padStart(2,'0')).join('');const db=await new Promise((resolve,reject)=>{const q=indexedDB.open('codi-mirrored-files-v1',2);q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)}),row=await new Promise((resolve,reject)=>{const q=db.transaction('files').objectStore('files').get([scope,'/sample']);q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)});db.close();const scopeHash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(scope))),b=>b.toString(16).padStart(2,'0')).join(''),root=await navigator.storage.getDirectory(),dir=await root.getDirectoryHandle('codi-opfs-'+scopeHash),handle=await dir.getFileHandle(row.data.generation),w=await handle.createWritable();await w.write(new Uint8Array(size));await w.close();let corruptRejected=false;try{await m.readBlob('/sample')}catch{corruptRejected=true}m.close();return {size,capture,snapshot,read,expected,actual,corruptRejected};
 });
 assert.equal(result.actual,result.expected);assert.equal(result.corruptRejected,true);assert.deepEqual(result.capture,[{action:'write',size:result.size}]);assert.deepEqual(result.snapshot,[{action:'verify',size:result.size}]);assert.deepEqual(result.read,[{action:'copy',size:result.size}]);console.log('PASS worker operation counts and hashes',JSON.stringify(result));
}finally{await browser?.close();http.kill('SIGTERM');await rm(profile,{recursive:true,force:true})}
