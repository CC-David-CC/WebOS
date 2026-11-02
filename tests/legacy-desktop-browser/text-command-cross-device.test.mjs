import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'});
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:19675/';
const user=process.env.CODI_TEST_USER||'txdevice'+Date.now().toString().slice(-8);
const a=await browser.createBrowserContext(), b=await browser.createBrowserContext();
const p=await a.newPage(), q=await b.newPage();
async function login(page, register){
  await page.setViewport(process.env.CODI_PHONE?{width:390,height:844,isMobile:true,hasTouch:true}:{width:1366,height:768});
  await page.goto(base);await page.waitForSelector('.login-toggle');
  if(register)await page.click('.login-toggle');
  await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');
  if(register)await page.type('[aria-label="Confirm password"]','test1234');
  await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
try{
  await login(p,true);
  await p.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.write('/two-devices.txt','original',null);await f.sync();openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/two-devices.txt')});
  await p.waitForFunction(()=>document.querySelector('.cm-content')?.textContent==='original'&&window.codiDesktopCommands?.list().some(c=>c.appId==='text'),{timeout:30000});
  await login(q,false);
  await q.waitForFunction(async()=>{try{return new TextDecoder().decode((await(await mirrorFileContext()).files.read('/two-devices.txt')).data)==='original'}catch{return false}},{timeout:30000});
  const id=await p.evaluate(()=>window.codiDesktopCommands.list().find(c=>c.appId==='text').windowId);
  const current=await p.evaluate(id=>window.codiDesktopCommands.execute({windowId:id,command:'inspect',args:{}}),id);
  const draft=await p.evaluate(({id,revision})=>window.codiDesktopCommands.execute({windowId:id,command:'replace-range',args:{revision,from:0,to:8,text:'device A draft'}}),{id,revision:current.revision});
  await p.evaluate(async()=>{const f=(await mirrorFileContext()).files;window.savedFixtureSync=f.sync.bind(f);f.sync=async()=>{throw Error('Fixture offline')}});
  await q.evaluate(async()=>{const f=(await mirrorFileContext()).files,old=await f.read('/two-devices.txt');await f.write('/two-devices.txt','device B saved',old.version);await f.sync()});
  assert.equal(await q.evaluate(async()=>new TextDecoder().decode((await(await serverFileContext()).files.read('two-devices.txt')).data)),'device B saved');
  const saved=await p.evaluate(({id,revision})=>window.codiDesktopCommands.execute({windowId:id,command:'save',args:{revision}}),{id,revision:draft.revision});
  assert.equal(saved.status,'pending');assert.equal(saved.dirty,false);
  await p.evaluate(async()=>{const f=(await mirrorFileContext()).files;f.sync=window.savedFixtureSync;await f.sync()});
  await p.waitForFunction(async()=>{try{return (await(await mirrorFileContext()).files.stat('/two-devices.txt')).status==='conflict'}catch{return false}},{timeout:45000});
  await p.waitForFunction(()=>document.querySelector('.ce-status-message')?.textContent.toLowerCase().includes('conflict'),{timeout:30000});
  const values=await p.evaluate(async()=>({local:new TextDecoder().decode((await(await mirrorFileContext()).files.read('/two-devices.txt')).data),server:new TextDecoder().decode((await(await serverFileContext()).files.read('two-devices.txt')).data),visible:document.querySelector('.cm-content').textContent}));
  assert.deepEqual(values,{local:'device A draft',server:'device B saved',visible:'device A draft'});
  const subject=await p.evaluate(async()=>{const c=await mirrorFileContext(),f=c.files;const conflicted=await f.read('/two-devices.txt');await f.resolve('/two-devices.txt','server',conflicted.version);const clean=await f.stat('/two-devices.txt');await f.remove('/two-devices.txt',clean.version);await f.sync();return c.owner});
  console.log('CLEANUP_SUBJECT '+subject);console.log('PASS independent browser contexts preserve both versions and report conflict');
}finally{await a.close();await b.close();await browser.disconnect()}
