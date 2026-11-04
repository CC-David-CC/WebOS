import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {spawn} from 'node:child_process';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const profile=await mkdtemp(join(tmpdir(),'codi-storage-floor-'));
const http=spawn('python3',['-m','http.server','19925','--bind','127.0.0.1'],{stdio:'ignore'});let browser;
try{
 await new Promise(r=>setTimeout(r,300));browser=await puppeteer.launch({executablePath:process.env.CHROME,userDataDir:profile,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const ctx=await browser.createBrowserContext(),page=await ctx.newPage();await page.goto('http://127.0.0.1:19925/');
 const result=await page.evaluate(async()=>{
 const {MirroredFiles:Old}=await import('/tests/fixtures/guarded-mirror-v1.mjs'),{MirroredFiles:New}=await import('/active-system/storage/browser/mirror.mjs'),{VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs');
 let release,started;const gate=new Promise(r=>release=r),entered=new Promise(r=>started=r);
 const server={async list(){throw Error('offline')},async captureSnapshot(blob){started();await gate;return {blob,sha256:[...new Uint8Array(await crypto.subtle.digest('SHA-256',await blob.arrayBuffer()))].map(x=>x.toString(16).padStart(2,'0')).join('')}}};
 const scope='floor-test',old=new Old({scope,server,retryMs:0});await old.list('/');
 const pending=old.write('/late',new Blob(['old-tab edit'])).then(()=>null,e=>e.name);await entered;
 const content=new VerifiedContent(scope),modern=new New({scope,server,content,retryMs:0});await modern.list('/');release();
 const oldResult=await pending;let legacyBlocked=false;try{await old.list('/')}catch(e){legacyBlocked=e.name==='VersionError'}
 const entries=await modern.list('/');old.close();modern.close();return {oldResult,legacyBlocked,entries:entries.entries.length};
 });
 assert.deepEqual(result,{oldResult:'VersionError',legacyBlocked:true,entries:0});await ctx.close();
 const ctx2=await browser.createBrowserContext(),p2=await ctx2.newPage();await p2.goto('http://127.0.0.1:19925/');
 const blocked=await p2.evaluate(async()=>{
 const {MirroredFiles:New}=await import('/active-system/storage/browser/mirror.mjs'),{VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs');
 const db=await new Promise((resolve,reject)=>{const r=indexedDB.open('codi-mirrored-files-v1',1);r.onupgradeneeded=()=>{const s=r.result.createObjectStore('files',{keyPath:['scope','path']});s.createIndex('scope','scope')};r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error)});
 db.onversionchange=()=>{};const content=new VerifiedContent('blocked'),m=new New({scope:'blocked',server:{async list(){throw Error('offline')}},content,retryMs:0});let rejected=false;try{await m.list('/')}catch(e){rejected=/blocked/i.test(e.message)}db.close();await new Promise(r=>setTimeout(r,200));
 const actual=await new Promise((resolve,reject)=>{const q=indexedDB.open('codi-mirrored-files-v1',1);q.onsuccess=()=>{const v=q.result.version;q.result.close();resolve(v)};q.onerror=()=>reject(q.error)});
 m.close();return {rejected,actual};
 });
 assert.deepEqual(blocked,{rejected:true,actual:1});await ctx2.close();console.log('PASS v2 floor rejects old in-flight save and aborts blocked late upgrade');
}finally{await browser?.close();http.kill('SIGTERM');await rm(profile,{recursive:true,force:true})}
