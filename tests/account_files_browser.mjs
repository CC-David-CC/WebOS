/** Real Login UI + signed Accounts HTTP + SQLite, using disposable browser contexts. */
import assert from 'node:assert/strict';
import {spawn, spawnSync} from 'node:child_process';
import {createInterface} from 'node:readline';
import {randomBytes} from 'node:crypto';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {build} from 'esbuild';
import puppeteer from 'puppeteer-core';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.resolve(process.env.WEBOS_TEST_OUTPUT || '');
const python = process.env.WEBOS_TEST_PYTHON;
assert(python && process.env.WEBOS_TEST_OUTPUT, 'Set WEBOS_TEST_PYTHON and a new private WEBOS_TEST_OUTPUT directory.');
assert(output !== root && !output.startsWith(root + path.sep), 'Test evidence/state must be outside source.');
await mkdir(output, {mode: 0o700}); const publicRoot = path.join(output, 'public'); await mkdir(publicRoot, {mode: 0o700});
await build({stdin: {contents: `
 import {mount} from '@webos/login'; import {createAccountsClient} from '@webos/accounts'; import {UserFiles} from '@webos/storage';
 const accounts=createAccountsClient();let view,files;const events=[];
 function open(){view=mount({accounts,onAuthenticated:publicSession=>{events.push(publicSession);files=new UserFiles(accounts.createFileAuthority(),{workerUrl:new URL('./workers/storage-verify.mjs',import.meta.url)});}});document.body.append(view.element);}
 open();window.__loginHarness=Object.freeze({inspect:()=>({account:accounts.inspect(),view:view.inspect(),authenticatedEvents:events.length}),
 write:(path,text,revision=null)=>files.write(path,text,revision),read:async path=>{const value=await files.read(path);return {text:new TextDecoder().decode(value.data),revision:value.sha256}},renew:()=>accounts.renew(),logout:async()=>{await accounts.logout();view.dispose();open();},dispose:()=>view.dispose()});
`, resolveDir: root, sourcefile: 'login-component-host.mjs'}, bundle: true, format: 'esm',
 outfile: path.join(publicRoot, 'client.mjs'), metafile: true, write: true, logLevel: 'silent'});
await build({entryPoints:[path.join(root,'platform/storage/src/webos_storage/vendor/js-sha256/verify-worker.mjs')],bundle:true,format:'esm',outfile:path.join(publicRoot,'workers/storage-verify.mjs'),logLevel:'silent'});
await writeFile(path.join(publicRoot, 'index.html'), '<!doctype html><html><head><meta charset="utf-8"><link rel="icon" href="data:,"><link rel="stylesheet" href="/client.css"></head><body><script type="module" src="/client.mjs"></script></body></html>');
let server = spawn(python, ['-u', path.join(root, 'scripts/run_development.py'), '--public-root', publicRoot, '--private-root', path.join(output, 'state'), '--port', '0'], {stdio: ['ignore', 'pipe', 'pipe']});
let browser; const serverErrors=[];server.stderr.on('data', data=>serverErrors.push(data));
const report={scope:'Real Login + signed account-file backend and workers across clean browsers; not Desktop/WordCraft acceptance',status:'FAIL'};
try {
 let origin=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Account fixture did not start.')),15000);const lines=createInterface({input:server.stdout});lines.once('line',line=>{clearTimeout(timer);try{resolve(JSON.parse(line).origin)}catch{reject(Error('Invalid fixture readiness'))}});server.once('exit',()=>{clearTimeout(timer);reject(Error('Account fixture exited before readiness.'))});});
 browser=await puppeteer.launch({executablePath:process.env.WEBOS_TEST_CHROMIUM || '/snap/chromium/current/usr/lib/chromium-browser/chrome',headless:true,args:['--no-sandbox','--disable-dev-shm-usage'],userDataDir:path.join(output,'browser-profile')});
 const requests=[],errors=[];
 async function context(){const c=await browser.createBrowserContext(),p=await c.newPage();p.on('request',r=>requests.push(new URL(r.url()).pathname));p.on('pageerror',e=>errors.push(e.message));await p.goto(origin,{waitUntil:'networkidle0'});await p.waitForFunction(()=>window.__loginHarness?.inspect().view.phase==='ready');return {c,p};}
 async function submit(p,name,secret,register=false){if(register)await p.click('.login-toggle');await p.$eval('[name=username]',el=>{el.value=''});await p.type('[name=username]',name);await p.type('[name=password]',secret);if(register)await p.type('[name=confirmation]',secret);await p.click('[type=submit]');}
 const name='test'+randomBytes(6).toString('hex'),secret=randomBytes(16).toString('base64url');
 const first=await context();await submit(first.p,name,secret,true);await first.p.waitForFunction(()=>window.__loginHarness.inspect().account.phase==='authenticated');
 const a=await first.p.evaluate(()=>window.__loginHarness.inspect());assert.match(a.account.accountId,/^user:/);assert.equal(a.view.phase,'authenticated');assert.equal(a.authenticatedEvents,1);
 assert(!JSON.stringify(a).includes(secret),'Inspection exposed a credential');assert.deepEqual(Object.keys(a.account).sort(),['accountId','displayName','epoch','expiresAt','phase','sessionId','trust'].sort());
 const second=await context();await submit(second.p,'test'+randomBytes(6).toString('hex'),secret);await second.p.waitForFunction(()=>document.querySelector('.login-error').textContent&&window.__loginHarness.inspect().view.phase==='ready');
 const count=spawnSync(python,['-c',"import sqlite3,sys;print(sqlite3.connect(sys.argv[1]).execute('select count(*) from accounts').fetchone()[0])",path.join(output,'state/identity/accounts.sqlite3')],{encoding:'utf8'});assert.equal(count.status,0);assert.equal(count.stdout.trim(),'1','Unknown-user sign-in created another account');
 await submit(second.p,name,secret);await second.p.waitForFunction(()=>window.__loginHarness.inspect().account.phase==='authenticated');const b=await second.p.evaluate(()=>window.__loginHarness.inspect());assert.equal(b.account.accountId,a.account.accountId);assert.notEqual(b.account.sessionId,a.account.sessionId);
 const saved=await first.p.evaluate(()=>window.__loginHarness.write('Documents/shared.txt','Server document revision one'));
 const opened=await second.p.evaluate(()=>window.__loginHarness.read('Documents/shared.txt'));assert.equal(opened.text,'Server document revision one');assert.equal(opened.revision,saved.sha256);
 const changed=await first.p.evaluate(revision=>window.__loginHarness.write('Documents/shared.txt','Server document revision two',revision),saved.sha256);
 const stale=await second.p.evaluate(async revision=>{try{await window.__loginHarness.write('Documents/shared.txt','Stale overwrite',revision);return {accepted:true}}catch(error){return {accepted:false,status:error.status}}},saved.sha256);assert.equal(stale.accepted,false);assert.equal(stale.status,409);assert.equal((await second.p.evaluate(()=>window.__loginHarness.read('Documents/shared.txt'))).revision,changed.sha256);
 const outsider=await context();await submit(outsider.p,'test'+randomBytes(6).toString('hex'),secret,true);await outsider.p.waitForFunction(()=>window.__loginHarness.inspect().account.phase==='authenticated');const denied=await outsider.p.evaluate(async()=>{try{await window.__loginHarness.read('Documents/shared.txt');return false}catch{return true}});assert.equal(denied,true);await outsider.p.evaluate(()=>window.__loginHarness.logout());await outsider.c.close();
 const unsigned=await second.p.evaluate(async()=>{const response=await fetch('/gateway/use',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({resource:'my-files',operation:'list',path:''})});return response.status});assert.equal(unsigned,401);
 await first.p.evaluate(()=>window.__loginHarness.logout());await first.p.waitForFunction(()=>window.__loginHarness.inspect().view.phase==='ready');assert.equal((await first.p.evaluate(()=>window.__loginHarness.inspect())).account.accountId,null);const fenced=await first.p.evaluate(async()=>{try{await window.__loginHarness.read('Documents/shared.txt');return false}catch{return true}});assert.equal(fenced,true);
 await second.p.evaluate(()=>window.__loginHarness.dispose());assert.equal((await second.p.evaluate(()=>window.__loginHarness.inspect())).account.phase,'authenticated');const renewed=await second.p.evaluate(()=>window.__loginHarness.renew());assert.equal(renewed.accountId,a.account.accountId);assert.equal(renewed.sessionId,b.account.sessionId);assert.equal((await second.p.evaluate(()=>window.__loginHarness.read('Documents/shared.txt'))).text,'Server document revision two');
 const third=await context();await third.p.setRequestInterception(true);third.p.on('request',r=>{if(r.url().endsWith('/api/v1/auth'))setTimeout(()=>r.continue().catch(()=>{}),200);else r.continue().catch(()=>{})});await submit(third.p,name,secret);await third.p.waitForFunction(()=>window.__loginHarness.inspect().account.phase==='authenticating');await third.p.evaluate(()=>window.__loginHarness.dispose());await third.p.waitForFunction(()=>window.__loginHarness.inspect().account.phase==='signed-out');assert.equal((await third.p.evaluate(()=>window.__loginHarness.inspect())).authenticatedEvents,0);
 const sessions=spawnSync(python,['-c',"import sqlite3,sys;print(sqlite3.connect(sys.argv[1]).execute('select count(*) from registered_sessions').fetchone()[0])",path.join(output,'state/identity/accounts.sqlite3')],{encoding:'utf8'});assert.equal(sessions.status,0);assert.equal(sessions.stdout.trim(),'1','Disposed pending sign-in left an unowned retained session');
 assert(!requests.some(p=>/v86|\/vm\/|terminal/.test(p)),'Login required guest assets');assert.deepEqual(errors,[]);
 await first.p.screenshot({path:path.join(output,'login.png')});
 await first.c.close();await second.c.close();await third.c.close();
 server.kill('SIGTERM');await new Promise(resolve=>server.once('exit',resolve));
 server=spawn(python,['-u',path.join(root,'scripts/run_development.py'),'--public-root',publicRoot,'--private-root',path.join(output,'state'),'--port','0'],{stdio:['ignore','pipe','pipe']});server.stderr.on('data',data=>serverErrors.push(data));
 origin=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Restart did not become ready.')),15000);const lines=createInterface({input:server.stdout});lines.once('line',line=>{clearTimeout(timer);resolve(JSON.parse(line).origin)});server.once('exit',()=>{clearTimeout(timer);reject(Error('Restart failed.'))});});
 const resumed=await context();await submit(resumed.p,name,secret);await resumed.p.waitForFunction(()=>window.__loginHarness.inspect().account.phase==='authenticated');assert.equal((await resumed.p.evaluate(()=>window.__loginHarness.inspect())).account.accountId,a.account.accountId);const durable=await resumed.p.evaluate(()=>window.__loginHarness.read('Documents/shared.txt'));assert.equal(durable.text,'Server document revision two');assert.equal(durable.revision,changed.sha256);

 Object.assign(report,{status:'PASS',realBrowserContexts:5,serverRestartPreservesIdentityAndFileRevision:true,realSignedServerFiles:true,verificationWorker:true,secondContextFetchesServerBytes:true,staleSaveRejected:true,anotherAccountDenied:true,unsignedFileRequestDenied:true,logoutFencesOldFileAuthority:true,closingViewPreservesFileService:true,sharedAccountDistinctSessions:true,unknownSigninDoesNotRegister:true,inspectionContainsNoCredentials:true,viewClosePreservesAccountService:true,pendingViewCloseRevokesLateSession:true,logoutAndRenew:true,noGuestRequests:true,pageErrors:0});
} catch(error) {report.error={name:error.name,message:error.message};throw error;}
finally {if(browser)await browser.close();server.kill('SIGTERM');await new Promise(resolve=>{if(server.exitCode!==null||server.signalCode)resolve();else server.once('exit',resolve)});await writeFile(path.join(output,'result.json'),JSON.stringify(report,null,2)+'\n');await writeFile(path.join(output,'server-errors.log'),Buffer.concat(serverErrors));}
console.log(JSON.stringify(report));
