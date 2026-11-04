/* Scoped beta-only acceptance. Creates TWO dedicated accounts and small files.
 * Do not run until the beta v2 transition is confirmed active. */
const assert=require('node:assert/strict');const crypto=require('node:crypto');const puppeteer=require('puppeteer-core');
(async()=>{
 if(process.env.CODI_BETA_CONFIRMED!=='3ad04c48')throw Error('Confirmed beta candidate token required');
 if(!process.env.CODI_TEST_CDP_A||!process.env.CODI_TEST_CDP_B||process.env.CODI_TEST_CDP_A===process.env.CODI_TEST_CDP_B)throw Error('Two separate isolated Chromium CDP endpoints required');
 await require('./files-public-beta-assert.cjs')();
 const beta='https://beta.ksu.codes/';const id=crypto.randomBytes(6).toString('hex');const users=['bta'+id,'btb'+id],password=crypto.randomBytes(18).toString('base64url'),file='smoke-'+id+'.txt',large='delta-'+id+'.bin';let ba,bb,a,b,fresh;
 try{
  [ba,bb]=await Promise.all([process.env.CODI_TEST_CDP_A,process.env.CODI_TEST_CDP_B].map(browserURL=>puppeteer.connect({browserURL})));
  a=await ba.newPage();b=await bb.newPage();
  const observed=await a.evaluateOnNewDocument(()=>{window.__codiObserved=[];const f=window.fetch;window.fetch=async(...args)=>{if(window.__codiTrack){const x=args[1]?.body;let n=0;if(typeof x==='string')n=new TextEncoder().encode(x).length;else if(x instanceof Blob)n=x.size;else if(x?.byteLength)n=x.byteLength;window.__codiObserved.push({url:String(args[0]),bytes:n})}return f(...args)}});
  async function account(page,user,register){
   await page.goto(beta,{waitUntil:'domcontentloaded',timeout:45000});await page.waitForSelector('.login-gate',{timeout:45000});
   if(register){await page.waitForSelector('.login-toggle');await page.click('.login-toggle')}
   await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]',password);
   if(register)await page.type('[aria-label="Confirm password"]',password);
   await page.click('.login-form button[type=submit]');
   await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:45000});
   const identity=await page.evaluate(async()=>{const c=await(await fetch('/config.json',{cache:'no-store'})).json();return {issuer:c.identity?.issuer,storage:c.fileStorage}});
   assert.equal(identity.issuer,'https://beta.ksu.codes');assert.deepEqual(identity.storage,{version:'codi-browser-file-content/1',backend:'opfs',databaseVersion:2});
  }
  await Promise.all([a.setViewport({width:1366,height:900}),b.setViewport({width:1366,height:900})]);await account(a,users[0],true);await account(b,users[1],true);
  await a.evaluate(()=>surfaces.get('Desktop').launch('files'));await a.waitForSelector('.codi-chonky',{timeout:45000});await a.waitForFunction(()=>document.querySelector('.files-content')?.innerText.includes('Files checked with the server.'),{timeout:45000});
  await a.click('.codi-files-touch-menu');await a.evaluate(()=>{const x=[...document.querySelectorAll('.codi-files-menu button')].find(x=>x.textContent==='New file');if(!x)throw Error('New file action unavailable');x.click()});await a.waitForSelector('dialog[open] input');await a.type('dialog[open] input',file);await a.evaluate(()=>{const x=[...document.querySelectorAll('dialog[open] button')].find(x=>x.textContent.trim()==='Create');if(!x)throw Error('Create action unavailable');x.click()});
  const selector=`[data-chonky-file-id="/${file}"]`;await a.waitForSelector(selector,{timeout:45000});await a.click(selector);await a.click(selector,{clickCount:2});await a.waitForSelector('.codi-text-editor .cm-content',{timeout:30000});await a.focus('.codi-text-editor .cm-content');await a.keyboard.type('Beta Files smoke');await a.click('.ce-desktop-save [data-command=save]');
  await a.waitForFunction(async name=>{try{const x=await(await mirrorFileContext()).files.read('/'+name);return x.status==='synced'&&new TextDecoder().decode(x.data)==='Beta Files smoke'}catch{return false}},{timeout:60000},file);
  const denial=await b.evaluate(async name=>{try{await(await serverFileContext()).files.read(name);return {ok:true}}catch(e){return {name:e.name,status:e.status}}},file);assert.deepEqual(denial,{name:'FileRequestError',status:404});
  fresh=await ba.createBrowserContext();const f=await fresh.newPage();await account(f,users[0],false);await f.waitForFunction(async name=>{try{return new TextDecoder().decode((await(await mirrorFileContext()).files.read('/'+name)).data)==='Beta Files smoke'}catch{return false}},{timeout:45000},file);
  const transfer=await a.evaluate(async name=>{const m=(await mirrorFileContext()).files,raw=(await serverFileContext()).files,buf=new Uint8Array(1024*1024);for(let i=0;i<buf.length;i+=65536)crypto.getRandomValues(buf.subarray(i,i+65536));const first=await m.write('/'+name,new Blob([buf]));await m.sync();buf[12345]^=255;window.__codiObserved=[];window.__codiTrack=true;const next=await m.write('/'+name,new Blob([buf]),first.version);await m.sync();window.__codiTrack=false;const v=await raw.version(name);const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',buf)),x=>x.toString(16).padStart(2,'0')).join('');return {bytes:window.__codiObserved.reduce((n,x)=>n+x.bytes,0),sha:v.sha256,expected:hash,size:v.bytes,local:next.sha256}},large);
  assert.equal(transfer.size,1024*1024);assert.equal(transfer.sha,transfer.expected);assert.ok(transfer.bytes<1024*1024,'one-byte edit sent a full file or more');
  console.log(JSON.stringify({status:'PASS',scope:'public beta only; two new disposable accounts, Files/Text, other-account denial, fresh-context reopen, 1 MiB one-byte changed request bodies',users,files:[file,large],changedRequestBodyBytes:transfer.bytes,hash:transfer.sha,limitations:'request body metric excludes response/headers/TLS; conflict, physical touch, power loss and 128 MiB are not covered'}));
 }finally{if(fresh)await fresh.close();if(a)await a.close();if(b)await b.close();if(ba)ba.disconnect();if(bb)bb.disconnect()}
})().catch(e=>{console.error('Beta acceptance failed:',e.message);process.exitCode=1});
