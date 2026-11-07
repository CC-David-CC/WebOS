// Real Chromium and production lifecycle module. Controlled HTTP/recovery only.
// No accounts, files, guest VM, relay or existing browser profile.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const puppeteer=createRequire(import.meta.url)(process.env.PUPPETEER_CORE_PATH||'/tmp/codi-occt-release-control/node_modules/puppeteer-core');
const out=path.resolve(process.env.CODI_EVIDENCE);assert(!fs.existsSync(out));fs.mkdirSync(out,{recursive:true});
const modulePath=process.env.CODI_LIFECYCLE_SOURCE||'active-system/assets/desktop/lifecycle.mjs';
const epochA='00000000-0000-0000-0000-000000000001',epochB='00000000-0000-0000-0000-000000000002';
let epoch=epochA,maintenance=null,requests=0;
const html=`<!doctype html><main id="workspace"><input id="draft" value="keep my draft"></main><script type="module">
import {startLifecycle} from '/assets/desktop/lifecycle.mjs';
window.recoveries=0;window.releases=[];window.failRecovery=false;
window.life=startLifecycle({config:{identity:{apiBase:'/api/v1'},desktopLifecycle:{version:'codi-desktop-lifecycle/1',statusPath:'/api/v1/desktop-status'}},roots:()=>[document.querySelector('#workspace')],pollMs:60000,recoverSession:()=>{window.recoveries++;if(window.failRecovery)return Promise.reject(Error('Controlled recovery refusal'));return new Promise(resolve=>window.releases.push(resolve));}});
window.releaseAll=()=>{for(const resolve of window.releases.splice(0))resolve();};
</script>`;
const files={'/assets/desktop/lifecycle.mjs':modulePath,'/network/strict-json.mjs':'active-system/network/strict-json.mjs'};
const server=http.createServer((req,res)=>{
 if(req.url==='/api/v1/desktop-status'){requests++;res.writeHead(200,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify({version:'codi-desktop-status/1',epoch,serverTime:Math.floor(Date.now()/1000),maintenance}));}
 else if(files[req.url]){res.writeHead(200,{'Content-Type':'text/javascript'});res.end(fs.readFileSync(files[req.url]));}
 else if(req.url==='/'){res.writeHead(200,{'Content-Type':'text/html'});res.end(html);}
 else{res.writeHead(404);res.end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin='http://127.0.0.1:'+server.address().port;
const report={status:'RUNNING',scope:'Production lifecycle DOM/input behavior with controlled recovery promises; no account/Files tests',sourceSHA256:crypto.createHash('sha256').update(fs.readFileSync(modulePath)).digest('hex'),cases:[]};
const flush=()=>fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(report,null,2)+'\n');
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let browser;
async function exercise(name,page,row){
 if(name==='failed-recovery-is-retryable')await page.evaluate(()=>window.failRecovery=true);
 epoch=epochB;
 if(name==='stop-during-recovery'){const now=Math.floor(Date.now()/1000);maintenance={version:'codi-maintenance-notice/1',id:'1'.repeat(32),phase:'active',deadline:now,expiresAt:now+300,message:'Controlled maintenance'};}
 await page.evaluate(()=>window.dispatchEvent(new Event('online')));
 await page.waitForFunction(()=>window.recoveries===1);
 if(name==='stop-during-recovery'){
  await page.evaluate(()=>window.life.stop());assert.equal(await page.$eval('#workspace',e=>e.inert),false);
  await page.evaluate(()=>window.releaseAll());await pause(100);
  row.after=await page.evaluate(()=>({inert:document.querySelector('#workspace').inert,overlays:document.querySelectorAll('#desktop-recovery').length,state:window.life.state,draft:document.querySelector('#draft').value}));
  assert.equal(row.after.inert,false,'Stopped monitor must not re-block roots after late recovery');assert.equal(row.after.overlays,0);assert.equal(row.after.draft,'keep my draft');
 }else if(name==='online-during-slow-recovery'){
  // Exercise the real four-second fetch deadline during pending recovery.
  await pause(4300);const before=requests;
  await page.evaluate(()=>window.dispatchEvent(new Event('online')));await pause(150);
  row.whilePending={requestsBefore:before,requestsAfter:requests,recoveries:await page.evaluate(()=>window.recoveries)};
  assert.equal(row.whilePending.recoveries,1,'Aborted controller must not admit overlapping recovery');assert.equal(requests,before);
  await page.evaluate(()=>window.releaseAll());await page.waitForFunction(e=>window.life.state.epoch===e&&!document.querySelector('#workspace').inert,{},epochB);
 }else{
  await pause(150);
  row.afterFailure=await page.evaluate(()=>{const b=[...document.querySelectorAll('#desktop-recovery button')].find(x=>x.textContent==='Try again now');return{blocked:window.life.state.blocked,disabled:b.disabled,visible:!b.hidden,title:document.querySelector('#desktop-recovery-title').textContent};});
  assert.equal(row.afterFailure.blocked,true);assert.equal(row.afterFailure.visible,true);assert.equal(row.afterFailure.disabled,false,'Failed recovery must leave a usable retry');
  await page.evaluate(()=>window.failRecovery=false);
  await page.locator('#desktop-recovery button:last-child').click();
  await page.waitForFunction(()=>window.recoveries===2);await page.evaluate(()=>window.releaseAll());
  await page.waitForFunction(e=>window.life.state.epoch===e&&!document.querySelector('#workspace').inert,{},epochB);
 }
}
try{
 browser=await puppeteer.launch({executablePath:process.env.CHROME_BINARY||'/snap/chromium/current/usr/lib/chromium-browser/chrome',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});report.browser=await browser.version();
 for(const name of ['stop-during-recovery','online-during-slow-recovery','failed-recovery-is-retryable']){
  epoch=epochA;maintenance=null;const context=await browser.createBrowserContext(),page=await context.newPage(),row={name,status:'RUNNING'};page.setDefaultTimeout(15000);
  try{await page.goto(origin);await page.waitForFunction(e=>window.life?.state.epoch===e&&!document.querySelector('#workspace').inert,{},epochA);await exercise(name,page,row);row.status='PASS';}
  catch(e){row.status='FAIL';row.error={name:e.name,message:e.message,stack:e.stack};}
  finally{await page.evaluate(()=>{window.life?.stop();window.releaseAll?.();}).catch(()=>{});await context.close();report.cases.push(row);flush();console.log(name,row.status);}
 }
 report.status=report.cases.every(r=>r.status==='PASS')?'PASS':'FAIL';
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));report.fixtureClosed=true;report.sharedBrowserUntouched=true;flush();}
process.exitCode=report.status==='PASS'?0:1;
