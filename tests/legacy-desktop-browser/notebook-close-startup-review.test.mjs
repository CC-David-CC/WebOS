import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255',protocolTimeout:180000});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(m.type()==='error'&&/Disposed|No module named ['"]decorator/i.test(m.text()))errors.push(m.text());});
page.on('dialog',d=>{errors.push('Unexpected native dialog');void d.dismiss();});
try{
 if(process.env.CODI_PHONE==='1')await page.setViewport({width:412,height:915,isMobile:true,hasTouch:true});
 await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18971/');
 await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
 await page.type('[aria-label=Username]','nbclose'+Date.now().toString().slice(-8));
 await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');
 await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');
 const kernelStates=[];
 for(let i=0;i<3;i++){
  await page.evaluate(()=>surfaces.get('Desktop').launch('notebook'));
  await page.waitForFunction(()=>document.querySelector('.notebook-app .app-status')?.textContent.includes('Browser Python notebook ready'),{timeout:120000});
  kernelStates.push(await page.evaluate(()=>document.querySelector('.notebook-app iframe').contentWindow.jupyterapp.shell.currentWidget?.sessionContext?.session?.kernel?.status??'not connected'));
  await page.evaluate(()=>document.querySelector('.notebook-app').closest('.window').querySelector('[aria-label=Close]').click());
  await page.waitForFunction(()=>!document.querySelector('.notebook-app'));
  await new Promise(resolve=>setTimeout(resolve,2000));
 }
 assert.deepEqual(errors,[]);console.log('PASS three immediate closes after notebook-ready; observed kernel states:',kernelStates.join(', '));
}finally{await context.close();await browser.disconnect();}
