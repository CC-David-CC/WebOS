// Actual production mirror + browser IDB; controlled remote namespace changes.
import assert from 'node:assert/strict';import fs from 'node:fs/promises';import crypto from 'node:crypto';import http from 'node:http';import {pathToFileURL} from 'node:url';
const out=process.env.CODI_AUDIT_OUTPUT;assert(out);await assert.rejects(fs.stat(out));const repo=new URL('../../',import.meta.url),sources=Object.fromEntries(['mirror.mjs','verified-content.mjs','opfs/store.mjs'].map(p=>['/'+p,new URL('active-system/storage/browser/'+p,repo)]));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex'),sourcePins=Object.fromEntries(await Promise.all(Object.entries(sources).map(async([k,p])=>[k,sha(await fs.readFile(p))])));
const server=http.createServer(async(req,res)=>{if(req.url==='/'){res.end('<!doctype html><title>Owned folder sequence</title>');return;}if(!sources[req.url]){res.writeHead(404);res.end();return;}res.setHeader('Content-Type','text/javascript');res.end(await fs.readFile(sources[req.url]));});await new Promise(r=>server.listen(0,'127.0.0.1',r));
const {default:puppeteer}=await import(pathToFileURL(process.env.PUPPETEER_CORE_PATH??'/tmp/codi-occt-release-control/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js'));let browser,context;const receipt={status:'RUNNING',scope:'Production mirror/real browser IDB; controlled same-account remote adapter, no signed service or UI claim',sourcePins};
try{browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP??'http://127.0.0.1:19329'});context=await browser.createBrowserContext();const page=await context.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/`);
 receipt.observed=await page.evaluate(async()=>{
  const {MirroredFiles}=await import('/mirror.mjs');let directory=true;const bytes=new TextEncoder().encode('remote replacement file');const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
  const remote={list:async path=>({entries:path===''?[{name:'projects',directory}]:[]}),supportsVersion:async()=>true,version:async()=>({sha256:hash}),read:async()=>({data:bytes,sha256:hash})};
  const mirror=new MirroredFiles({scope:'owned-folder-audit:'+crypto.randomUUID(),server:remote,retryMs:0});
  const row=async()=>({listing:await mirror.list('/'),status:await mirror.status()});
  try{
   await mirror.sync();const initial=await row();directory=false;await mirror.sync();const replaced=await row(),version=replaced.listing.entries[0].version;
   const attempts=[];for(const [operation,action]of[['use-server',()=>mirror.resolve('/projects','server',version)],['keep-local',()=>mirror.resolve('/projects','local',version)],['delete-empty-local-folder',()=>mirror.remove('/projects',version)],['move-local-folder',()=>mirror.move('/projects','/recovered',version)]]){let error=null;try{await action();}catch(e){error={name:e.name,message:e.message};}attempts.push({operation,error});}
   const afterAttempts=await row();directory=true;await mirror.sync();const restoredRemoteDirectory=await row();
   return{initial,replaced,attempts,afterAttempts,restoredRemoteDirectory};
  }finally{mirror.close();}
 });
 const x=receipt.observed;assert.equal(x.initial.status.conflicts,0);assert.equal(x.initial.listing.entries[0].directory,true);assert.equal(x.replaced.status.conflicts,1);assert(x.attempts.every(a=>a.error));assert.equal(x.afterAttempts.status.conflicts,1);assert.equal(x.restoredRemoteDirectory.status.conflicts,1);assert.equal(x.restoredRemoteDirectory.listing.entries[0].status,'conflict');
 receipt.status='CONFIRMED_WORKFLOW_GAP';receipt.finding='A clean local folder replaced by a remote file enters a conflict with no supported resolve/delete/move transition. Restoring the remote directory and syncing also leaves the conflict permanently flagged.';
}catch(e){receipt.status='HARNESS_OR_UNEXPECTED_FAILURE';receipt.error={message:e.message,stack:e.stack};throw e;}
finally{if(context)await context.close();if(browser)await browser.disconnect();await new Promise(r=>server.close(r));receipt.producerSha256=sha(await fs.readFile(new URL(import.meta.url)));await fs.writeFile(out,JSON.stringify(receipt,null,2)+'\n');}
