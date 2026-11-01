import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),ctx=await browser.createBrowserContext(),p=await ctx.newPage(),user='filedrag'+Date.now().toString().slice(-9);
try {
 await p.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 await p.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18304/');await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});console.log('Test account:',user,await p.evaluate(()=>signedInSubject()));
 await p.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.mkdir('/Dest');await f.write('/one.txt','one');await f.write('/two.txt','two');await f.write('/Dest/two.txt','existing');await f.sync();surfaces.get('Desktop').launch('files')});
 await p.waitForSelector('[data-chonky-file-id="/one.txt"]');await p.waitForSelector('[data-chonky-file-id="/two.txt"]');await p.waitForSelector('[data-chonky-file-id="/Dest"]');
 await p.click('[data-chonky-file-id="/one.txt"]');await p.keyboard.down('Control');await p.click('[data-chonky-file-id="/two.txt"]');await p.keyboard.up('Control');
 const from=await p.$eval('[data-chonky-file-id="/one.txt"]',e=>{const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}}),to=await p.$eval('[data-chonky-file-id="/Dest"]',e=>{const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}});
 await p.mouse.move(from.x,from.y);await p.mouse.down();await p.mouse.move(to.x,to.y,{steps:16});await p.mouse.up();
 await p.waitForFunction(()=>document.querySelector('.files-content')?.innerText.includes('Move stopped.'),{timeout:12000});
 const result=await p.evaluate(async()=>{const f=(await mirrorFileContext()).files;return {text:document.querySelector('.files-content').innerText,one:new TextDecoder().decode((await f.read('/Dest/one.txt')).data),two:new TextDecoder().decode((await f.read('/two.txt')).data),existing:new TextDecoder().decode((await f.read('/Dest/two.txt')).data)}});
 assert.match(result.text,/1 file was moved; check Files before retrying/);assert.deepEqual([result.one,result.two,result.existing],['one','two','existing']);console.log('PASS partial drag reports completed move and preserves collided file');
}finally{await ctx.close();await browser.disconnect()}
