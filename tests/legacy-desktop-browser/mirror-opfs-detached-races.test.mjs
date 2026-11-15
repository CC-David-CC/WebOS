// Independent real-OPFS regression: the injected wait happens AFTER the
// actual verified detached copy has completed, before readBlob rechecks IDB.
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {createServer} from 'node:http';
import {readFile, mkdtemp, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve, sep} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(fileURLToPath(new URL('..',import.meta.url))),profile=await mkdtemp(join(tmpdir(),'codi-detached-race-'));
const server=createServer(async(req,res)=>{try{const path=resolve(root,'.'+new URL(req.url,'http://localhost').pathname);if(path!==root&&!path.startsWith(root+sep))throw Error('path');const data=await readFile(path);res.writeHead(200,{'Content-Type':path.endsWith('.mjs')?'text/javascript':'text/html'});res.end(data)}catch{res.writeHead(404);res.end()}});
let browser;
try{
 await new Promise((yes,no)=>{server.once('error',no);server.listen(0,'127.0.0.1',yes)});
 browser=await puppeteer.launch({executablePath:process.env.CHROME,userDataDir:profile,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/tests/files-copy-pass-evidence-20261104.md`);
 const result=await page.evaluate(async()=>{
  const {MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs'),{VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs');
  let active=true,release,started;const scope='independent-copy-race',content=new VerifiedContent(scope),actualRead=content.read.bind(content);
  const m=new MirroredFiles({scope,server:{async list(){throw Error('offline')}},content,valid:()=>active,retryMs:0});
  try{
   const first=await m.write('/x','old');
   function holdAfterCopy(){const entered=new Promise(r=>started=r),gate=new Promise(r=>release=r);content.read=async(...args)=>{const blob=await actualRead(...args);started();await gate;return blob};return entered;}
   let entered=holdAfterCopy(),pending=m.readBlob('/x').then(()=>({accepted:true}),e=>({name:e.name,message:e.message}));await entered;
   await m.write('/x','new',first.version);release();const race=await pending;content.read=actualRead;
   const retained=(await m.readBlob('/x')).data;
   entered=holdAfterCopy();pending=m.readBlob('/x').then(()=>({accepted:true}),e=>({name:e.name,message:e.message}));await entered;
   active=false;release();const invalid=await pending;
   return {race,invalid,retained:await retained.text()};
  }finally{m.close();}
 });
 assert.equal(result.race.name,'MirrorConflict');assert.notEqual(result.invalid.accepted,true);assert.match(result.invalid.message,/account changed/i);assert.equal(result.retained,'new');
 console.log('PASS real detached copy then delayed completion: concurrent edit conflict, account invalidation, retained Blob');
}finally{await browser?.close();await new Promise(r=>server.close(r));await rm(profile,{recursive:true,force:true});}
