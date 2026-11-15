// Isolated preview, synthetic cookie, no secrets in logs.
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=new URL(process.env.MICRODUCK_PREVIEW_URL||'http://127.0.0.1:19752/'),runner=new URL(process.env.MICRODUCK_RUNNER_ORIGIN||'http://127.0.0.1:19753/');
if(!['127.0.0.1','localhost','[::1]'].includes(base.hostname)||!['127.0.0.1','localhost','[::1]'].includes(runner.hostname)||base.origin===runner.origin)throw Error('Distinct loopback origins required');
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255',protocolTimeout:120000}),ctx=await browser.createBrowserContext();let otherContext;
try{
 const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.setViewport({width:1366,height:900});
 await page.setCookie({name:'microduckIsolatedProbe',value:'synthetic',url:runner.href});
 await page.goto(base.href);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
 const user='secure'+Date.now().toString().slice(-8);await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test-password-123');await page.type('[aria-label="Confirm password"]','test-password-123');await page.click('.login-form button[type=submit]');
 await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 assert.equal(await page.evaluate(()=>document.cookie.includes('microduckIsolatedProbe=synthetic')),true,'synthetic same-host cookie exists in ordinary context');
 for(let n=1;n<=2;n++){
  await page.evaluate(()=>surfaces.get('Desktop').launch('microduck'));
  await page.waitForFunction(n=>[...document.querySelectorAll('.microduck-app')].length===n&&[...document.querySelectorAll('.microduck-app')].every(x=>x.querySelector('[data-brf=app-status]')?.textContent==='Project open.'),{timeout:120000},n);
 }
 const props=await page.evaluate(()=>[...document.querySelectorAll('.microduck-app [data-brf=app-runner] iframe')].map(f=>({credentialless:f.credentialless,sandbox:f.getAttribute('sandbox'),src:f.src})));
 assert.equal(props.length,2);assert.ok(props.every(x=>x.credentialless&&x.sandbox==='allow-scripts allow-same-origin'&&new URL(x.src).origin===runner.origin));
 const runnerFrames=page.frames().filter(f=>{try{return new URL(f.url()).origin===runner.origin}catch{return false}});assert.equal(runnerFrames.length,2);
 for(const f of runnerFrames){
  assert.equal(await f.evaluate(()=>document.cookie.includes('microduckIsolatedProbe=synthetic')),false,'credentialless frame must not share ordinary cookie jar');
  const blocked=await f.evaluate(async url=>{let violation=false;const listener=e=>{if(e.effectiveDirective==='connect-src')violation=true};addEventListener('securitypolicyviolation',listener);try{await fetch(url)}catch{}await new Promise(r=>setTimeout(r,100));removeEventListener('securitypolicyviolation',listener);return violation},new URL('/config.json',base).href);
  assert.equal(blocked,true,'runner CSP blocks fetching the desktop origin');
 }
 // A separate signed-in account cannot read the first account's server file.
 await page.evaluate(async()=>{const c=await mirrorFileContext();await c.files.write('/microduck-isolation-marker.brf','synthetic',null);await c.files.sync()});
 otherContext=await browser.createBrowserContext();const other=await otherContext.newPage();await other.goto(base.href);await other.waitForSelector('.login-toggle');await other.click('.login-toggle');
 await other.type('[aria-label=Username]',user+'b');await other.type('[aria-label=Password]','test-password-123');await other.type('[aria-label="Confirm password"]','test-password-123');await other.click('.login-form button[type=submit]');await other.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 const denied=await other.evaluate(async()=>{try{await(await serverFileContext()).files.read('microduck-isolation-marker.brf');return 0}catch(e){return e.status}});
 assert.ok(denied===403||denied===404,'other account must be denied');
 await otherContext.close();otherContext=null;
 await page.evaluate(()=>document.querySelector('.microduck-app').closest('.window').querySelector('[aria-label=Close]').click());
 await page.waitForSelector('dialog[open]');await page.evaluate(()=>[...document.querySelector('dialog[open]').querySelectorAll('button')].find(b=>b.textContent==='Discard changes').click());
 await page.waitForFunction(()=>document.querySelectorAll('.microduck-app').length===1&&document.querySelectorAll('.microduck-app [data-brf=app-runner] iframe').length===1,{timeout:30000});
 assert.equal(await page.evaluate(()=>document.querySelector('.microduck-app [data-brf=app-status]')?.textContent),'Project open.','other window stays open');
 await page.evaluate(()=>document.querySelector('.microduck-app').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForSelector('dialog[open]');await page.evaluate(()=>[...document.querySelector('dialog[open]').querySelectorAll('button')].find(b=>b.textContent==='Discard changes').click());await page.waitForFunction(()=>document.querySelectorAll('.microduck-app').length===0,{timeout:30000});
 assert.deepEqual(errors,[]);console.log('PASS synthetic cookie isolated, runner CSP enforced, account files isolated, independent windows and close cleanup');
}finally{if(otherContext)await otherContext.close();await ctx.close();browser.disconnect()}
