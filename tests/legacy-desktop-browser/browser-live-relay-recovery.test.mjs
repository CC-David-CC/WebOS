import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
const name=process.env.CODI_TEST_USER;
if(!/^browserprobe[0-9a-f]{10}$/.test(name||''))throw Error('Set a disposable browserprobe username');
const ssh=(...args)=>execFileSync('ssh',['-o','BatchMode=yes','box-webhost',...args],{encoding:'utf8',timeout:60000});
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});const context=await browser.createBrowserContext(),page=await context.newPage();let stopped=false;
try{
 await page.setViewport({width:1366,height:950});
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto('https://ksu.codes/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',name);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 ssh('systemctl','is-active','--quiet','codi-browser-relay.service');stopped=true;ssh('sudo','-n','systemctl','stop','codi-browser-relay.service');
 await page.evaluate(()=>[...surfaces.values()][0].launch('browser'));
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent.includes('temporarily unavailable'),{timeout:30000});
 const text=await page.evaluate(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('.status').textContent);assert.match(text,/Select Reset engine/);
 ssh('sudo','-n','systemctl','start','codi-browser-relay.service');stopped=false;
 await page.waitForFunction(()=>true,{timeout:1000});
 for(let i=0;i<50;i++){try{ssh('sudo','-n','/usr/bin/python3','-c',"'import socket;s=socket.socket(socket.AF_UNIX);s.connect(\"/run/codi-browser/relay.sock\");s.close()'");break;}catch(e){if(i===49)throw e;await new Promise(r=>setTimeout(r,200));}}
 await page.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;[...r.querySelectorAll('button')].find(b=>b.textContent==='Reset engine').click()});
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent==='Ready',{timeout:180000});
 console.log('PASS live relay stopped: clear recovery message; restart and Reset engine reconnect');
}finally{
 if(stopped)ssh('sudo','-n','systemctl','start','codi-browser-relay.service');
 await context.close();await browser.disconnect();
}
