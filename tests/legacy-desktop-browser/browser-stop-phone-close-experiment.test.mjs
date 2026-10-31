import puppeteer from 'puppeteer-core';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});
const context=await browser.createBrowserContext(),page=await context.newPage();
try {
  await page.setViewport({width:390,height:844,isMobile:true,hasTouch:true});
  await page.goto('http://127.0.0.1:18195/demo/index.html');
  const ready=()=>page.waitForFunction(()=>document.querySelector('.window-content')?.shadowRoot?.querySelector('.status')?.textContent==='Ready',{timeout:180000});
  const go=url=>page.evaluate(url=>{const address=document.querySelector('.window-content').shadowRoot.querySelector('[aria-label="Website address"]');address.value=url;address.form.requestSubmit();},url);
  const count=()=>page.evaluate(async()=>((await (await fetch('/test-calls')).json()).resolved.filter(x=>x==='SLOW_REQUEST').length));
  await ready();let before=await count();await go('http://fixture.example/slow');
  await page.waitForFunction(async n=>((await (await fetch('/test-calls')).json()).resolved.filter(x=>x==='SLOW_REQUEST').length)>n,{timeout:30000},before);
  await page.evaluate(()=>[...document.querySelector('.window-content').shadowRoot.querySelectorAll('button')].find(x=>x.textContent==='Stop').click());
  await page.waitForFunction(()=>document.querySelector('.window-content').shadowRoot.querySelector('.status').textContent==='Stopped.',{timeout:5000});
  console.log('PASS Stop on a phone-sized viewport');
  before=await count();await go('http://fixture.example/slow');
  await page.waitForFunction(async n=>((await (await fetch('/test-calls')).json()).resolved.filter(x=>x==='SLOW_REQUEST').length)>n,{timeout:30000},before);
  await page.click('.window header button');await page.waitForFunction(()=>!document.querySelector('.window-content'));
  await page.click('#open');await ready();await go('http://fixture.example/after');
  await page.waitForFunction(async()=>((await (await fetch('/test-calls')).json()).resolved.includes('AFTER_RESPONSE')),{timeout:30000});
  console.log('PASS closing during a slow load and reopening');
} finally {await context.close();await browser.disconnect();}
