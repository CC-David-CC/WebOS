// Actual browser IndexedDB + production mirror. Controlled in-memory remote
// adapter only; no account credentials, live service, UI, or filesystem probes.
import assert from 'node:assert/strict';import fs from 'node:fs/promises';
import crypto from 'node:crypto';import http from 'node:http';import {pathToFileURL} from 'node:url';
const out=process.env.CODI_AUDIT_OUTPUT;assert(out);await assert.rejects(fs.stat(out));
const repo=new URL('../../',import.meta.url), sources={
 '/mirror.mjs':new URL('active-system/storage/browser/mirror.mjs',repo),
 '/verified-content.mjs':new URL('active-system/storage/browser/verified-content.mjs',repo),
 '/opfs/store.mjs':new URL('active-system/storage/browser/opfs/store.mjs',repo)
};
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const sourcePins=Object.fromEntries(await Promise.all(Object.entries(sources).map(async([key,path])=>[key,sha(await fs.readFile(path))])));
const server=http.createServer(async(req,res)=>{try{if(req.url==='/'){res.setHeader('Content-Type','text/html');res.end('<!doctype html><title>Owned storage sequence fixture</title>');return;}const file=sources[req.url];if(!file){res.writeHead(404);res.end();return;}res.setHeader('Content-Type','text/javascript');res.end(await fs.readFile(file));}catch{res.writeHead(500);res.end();}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const {default:puppeteer}=await import(pathToFileURL(process.env.PUPPETEER_CORE_PATH??'/tmp/codi-occt-release-control/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js'));
let browser,context;const receipt={status:'RUNNING',scope:'Actual browser production mirror/IDB; controlled remote adapter; no signed server or UI claim',sourcePins};
try{
 browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP??'http://127.0.0.1:19329'});context=await browser.createBrowserContext();const page=await context.newPage();
 await page.goto(`http://127.0.0.1:${server.address().port}/`);
 receipt.observed=await page.evaluate(async()=>{
  const {MirroredFiles}=await import('/mirror.mjs');const enc=new TextEncoder(),dec=new TextDecoder();
  const remote=new Map([['a.txt','version one'],['b.txt','other file']]);let unavailable=true;
  const calls={version:[],read:[]},hash=async text=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',enc.encode(text))),x=>x.toString(16).padStart(2,'0')).join('');
  const server={supportsVersion:async()=>true,
   list:async path=>{if(path!=='')throw Error('Unexpected path');return{entries:[...remote.keys()].map(name=>({name,directory:false}))};},
   version:async path=>{calls.version.push(path);return{sha256:await hash(remote.get(path))};},
   read:async path=>{calls.read.push(path);if(path==='b.txt'&&unavailable)throw Error('Controlled B read unavailable');return{data:enc.encode(remote.get(path)),sha256:await hash(remote.get(path))};}
  };
  const mirror=new MirroredFiles({scope:'owned-state-audit:'+crypto.randomUUID(),server,retryMs:0});const stages=[];
  const pass=async label=>{let error=null;try{await mirror.sync();}catch(e){error={name:e.name,message:e.message};}let a=null;try{a=dec.decode((await mirror.read('/a.txt')).data);}catch{}stages.push({label,error,a,status:await mirror.status(),calls:{version:[...calls.version],read:[...calls.read]}});};
  try{await pass('initial-partial-download');remote.set('a.txt','version two');await pass('healthy-A-changed-while-B-still-fails');await pass('manual-retry-with-B-still-failing');unavailable=false;await pass('B-recovers-but-A-skipped-on-that-pass');await pass('next-complete-pass-finally-sees-A');return{stages,remoteA:remote.get('a.txt')};}
  finally{mirror.close();}
 });
 const s=receipt.observed.stages;assert.equal(s.length,5);
 assert.equal(s[0].a,'version one');assert.match(s[0].error.message,/Controlled B read unavailable/);
 assert.equal(s[1].a,'version one');assert.equal(s[2].a,'version one');assert.equal(s[3].a,'version one');assert.equal(s[4].a,'version two');
 assert.equal(s[0].calls.version.filter(p=>p==='a.txt').length,1);
 assert.equal(s[2].calls.version.filter(p=>p==='a.txt').length,1);
 assert.equal(s[3].error,null);assert.equal(s[3].status.error,null);
 assert.equal(s[4].calls.version.filter(p=>p==='a.txt').length,2);
 receipt.status='CONFIRMED_WORKFLOW_DEFECT';receipt.finding='Checked progress is keyed only by local row.version; one failing remote file indefinitely suppresses later refresh of already-checked healthy files, including manual retries. Recovery pass clears the cache only after skipping the healthy file once more.';
}catch(e){receipt.status='HARNESS_OR_UNEXPECTED_FAILURE';receipt.error={message:e.message,stack:e.stack};throw e;}
finally{if(context)await context.close();if(browser)await browser.disconnect();await new Promise(resolve=>server.close(resolve));receipt.producerSha256=sha(await fs.readFile(new URL(import.meta.url)));await fs.writeFile(out,JSON.stringify(receipt,null,2)+'\n');}
