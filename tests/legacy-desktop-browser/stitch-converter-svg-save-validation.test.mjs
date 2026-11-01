import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255'});
try {
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();
  const page=await context.newPage();await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
  await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
  await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18303/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');const user='svgvalid'+Date.now().toString().slice(-10);await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');console.log('Test account:',user,await page.evaluate(()=>signedInSubject()));await page.evaluate(()=>[...surfaces.values()][0].launch('stitch-converter'));await page.waitForSelector('.stitch-converter');
  const input='[aria-label="SVG artwork"]';await page.$eval(input,e=>{e.value='<svg><broken>';e.dispatchEvent(new Event('input',{bubbles:true}))});
  async function save(){const button=await page.$('[aria-label="Save artwork"]');await button.scrollIntoView();if(phone){const box=await button.boundingBox();await page.touchscreen.tap(box.x+box.width/2,box.y+box.height/2)}else await button.click()}
  await save();await page.waitForFunction(()=>/Artwork saved|Could not save artwork/.test(document.querySelector('.stitch-converter .app-status').textContent));
  assert.match(await page.$eval('.stitch-converter .app-status',e=>e.textContent),/valid SVG/i,'malformed SVG must not be saved as reopenable artwork');
  assert.equal(await page.evaluate(async()=>{try{await(await mirrorFileContext()).files.stat('/Artwork.stitch.svg');return true}catch(e){if(e.message==='File not found.')return false;throw e}}),false);
  assert.equal(await page.$eval(input,e=>e.value),'<svg><broken>','invalid draft stays in the editor');
  await page.$eval(input,e=>{e.value='<svg xmlns="http://www.w3.org/2000/svg"/>';e.dispatchEvent(new Event('input',{bubbles:true}))});await save();await page.waitForFunction(()=>document.querySelector('.stitch-converter .app-status').textContent.startsWith('Artwork saved'));
  await page.$eval(input,e=>{e.value='<svg><broken>';e.dispatchEvent(new Event('input',{bubbles:true}))});await save();await page.waitForFunction(()=>document.querySelector('.stitch-converter .app-status').textContent.startsWith('Could not save artwork'));assert.equal(await page.evaluate(async()=>new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Artwork.stitch.svg')).data)),'<svg xmlns="http://www.w3.org/2000/svg"/>','malformed edit must not overwrite the saved file');await page.$eval(input,e=>{e.value='<svg xmlns="http://www.w3.org/2000/svg"/>';e.dispatchEvent(new Event('input',{bubbles:true}))});await save();await page.waitForFunction(()=>document.querySelector('.stitch-converter .app-status').textContent.startsWith('Artwork saved'));
  await page.evaluate(async()=>{await(await mirrorFileContext()).files.sync();document.querySelector('.stitch-converter').closest('.window').querySelector('[aria-label=Close]').click()});await page.waitForFunction(()=>!document.querySelector('.stitch-converter'));await page.evaluate(()=>openMirrorDocument([...surfaces.values()][0],signedInSubject(),'/Artwork.stitch.svg'));await page.waitForFunction(()=>[...document.querySelectorAll('.stitch-converter .app-status')].some(e=>e.textContent.includes('Artwork opened. Preview unavailable')),{timeout:30000});
  await context.close();
 }
 console.log('PASS malformed SVG remains editable and cannot be saved; valid empty SVG saves and reopens');
}finally{await browser.disconnect()}
