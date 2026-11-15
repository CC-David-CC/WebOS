import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18486/';
if(!['http://127.0.0.1','https://ksu.codes'].includes(new URL(base).origin))throw Error('Unexpected test origin');
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),contexts=[],errors=[];
try{
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));await p.setViewport(phone?{width:390,height:844,isMobile:true,hasTouch:true}:{width:1440,height:900});
  await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});await p.goto(base);await p.waitForSelector('.login-toggle');await p.click('.login-toggle');const user='date'+Date.now().toString().slice(-9)+(phone?'b':'a');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');console.log('TEST ACCOUNT',user,await p.evaluate(()=>signedInSubject()));
  const clock=await p.$('.panel .clock');assert.ok(await clock.isIntersectingViewport());const date=await clock.evaluate(e=>e.textContent);assert.match(date,/^\d{2}\/\d{2}\/\d{2}$/);assert.ok(!date.includes(':'),'time is not shown in the bar');
  await clock.click();await p.waitForSelector('.status-popup[data-status-type="clock"] .clock-time',{visible:true});assert.ok((await p.$eval('.clock-date',e=>e.textContent)).length>6);const first=await p.$eval('.clock-time',e=>e.textContent);assert.match(first,/^\d{2}:\d{2}:\d{2}$/);await p.waitForFunction(t=>document.querySelector('.clock-time')?.textContent!==t,{timeout:3500},first);assert.equal(await clock.evaluate(e=>e.textContent),date,'bar still shows the date alone');
  await p.keyboard.press('Escape');assert.equal(await p.$('.status-popup[data-status-type="clock"]'),null,'Escape dismisses');await p.click('.panel .clock');await p.waitForSelector('.clock-time');const desktopBox=await(await p.$('.desktop')).boundingBox();await p.mouse.click(desktopBox.x+desktopBox.width*.35,desktopBox.y+desktopBox.height*.75);assert.equal(await p.$('.status-popup[data-status-type="clock"]'),null,'outside click dismisses');
  await p.click('.panel .clock');await p.waitForSelector('.clock-time');await p.click('.panel .clock');assert.equal(await p.$('.status-popup[data-status-type="clock"]'),null,'date toggles popup closed');
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone date-only bar, live seconds, Escape/outside/toggle dismissal');
}finally{for(const c of contexts)await c.close();await browser.disconnect()}
