const assert=require('node:assert/strict'),puppeteer=require('puppeteer-core');
(async()=>{const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:20085'}),context=await browser.createBrowserContext();try{
 const page=await context.newPage();await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:20086/');await page.waitForFunction('window.launch');await page.evaluate(()=>launch());
 await page.waitForFunction(()=>document.querySelector('.jsketcher-app .app-status')?.textContent.startsWith('New model.'),{timeout:90000});
 const frame=await(await page.$('.jsketcher-app iframe')).contentFrame();await frame.evaluate(()=>__CAD_APP.actionService.run('DesktopSources'));
 await page.waitForFunction('window.sourceStarted');await page.evaluate(()=>views[0].view.dispose());
 assert.equal(await page.evaluate(()=>views[0].controller.signal.aborted),false);await page.waitForFunction('window.sourceAborted');
 assert.equal(await page.evaluate(()=>document.querySelectorAll('.codi-cad-sources-dialog').length),0);
 console.log('PASS actual app mount disposal aborts held source read independently of host signal');
 }finally{await context.close();browser.disconnect()}})().catch(e=>{console.error(e.stack);process.exitCode=1});
