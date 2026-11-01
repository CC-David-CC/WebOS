import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18413/',phone=!!process.env.CODI_PHONE;
if(!['http://127.0.0.1','https://ksu.codes'].includes(new URL(base).origin))throw Error('Unexpected test origin');
const b=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19413'}),c=await b.createBrowserContext(),p=await c.newPage(),user='board'+Date.now().toString().slice(-9)+process.pid,errors=[];
p.on('pageerror',e=>errors.push(e.message));
async function click(label){await p.evaluate(label=>{const x=[...document.querySelectorAll('.solitaire-view button')].find(e=>e.getAttribute('aria-label')===label);if(!x)throw Error('missing '+label);x.click()},label)}
async function card(x,y){const el=await p.$('.solitaire-board');await el.scrollIntoView();const box=await el.boundingBox();const cx=box.x+x*box.width/636,cy=box.y+y*box.height/620;if(phone)await p.touchscreen.tap(cx,cy);else await p.mouse.click(cx,cy)}
try{
 await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1920,height:1080});
 await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await p.goto(base);await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');console.log('Test account',user,await p.evaluate(()=>signedInSubject()));
 // Construct a complete, unique deck with a six-hidden, thirteen-face-up legal run.
 await p.evaluate(async()=>{const up=[38,24,10,22,34,20,6,18,4,16,2,14,0],hidden=[1,3,5,8,9,11],tableau=[{cards:[],faceUpCount:0},{cards:[7,19],faceUpCount:2},{cards:[21],faceUpCount:1},{cards:[...hidden,...up],faceUpCount:13},{cards:[33],faceUpCount:1},{cards:[],faceUpCount:0},{cards:[],faceUpCount:0}],used=new Set(tableau.flatMap(x=>x.cards)),stock=Array.from({length:52},(_,i)=>i).filter(x=>!used.has(x));if(used.size!==23||stock.length!==29)throw Error('fixture is not a unique deck');const payload={drawMode:3,stock,waste:[],wasteVisibleFrom:0,tableau,foundations:[[],[],[],[]],score:0,moves:0,redeals:0,elapsedMs:0,undoStack:[],rngState:1,won:false,paused:true};const save={format:'ksu.game.save',schemaVersion:1,appId:'solitaire',kind:'logical-snapshot',gameBuild:'rules-1',contentVersion:'1',payload};const ctx=await mirrorFileContext();await ctx.files.write('/Layout.game.json',JSON.stringify(save),null);await ctx.files.sync();await openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Layout.game.json')});
 await p.waitForFunction(()=>document.querySelector('.solitaire-view .app-status')?.textContent.includes('Game loaded and paused'),{timeout:30000});await click('Start game');
 // The last card of the compressed long pile sits near the bottom of the canvas.
 await card(10+3*88+35,575);await card(330,50);
 // Move an actual two-card run from column two to column three.
 await card(10+1*88+35,150);await card(10+2*88+35,150);
 // Keyboard moves the now-exposed black seven from column three to red eight in column five.
 const board=await p.$('.solitaire-board');await board.focus();await p.keyboard.press('ArrowRight');await p.keyboard.press('ArrowRight');
 assert.equal(await p.evaluate(()=>{const d=document.querySelector('.solitaire-board').getContext('2d').getImageData(183,135,1,1).data;return d[0]===119&&d[1]===217&&d[2]===255}),true,'keyboard column is visibly marked');
 await p.keyboard.press('Enter');await p.keyboard.press('ArrowRight');await p.keyboard.press('ArrowRight');await p.keyboard.press('Enter');
 // Typing a path containing shortcuts must not invoke board commands.
 await p.evaluate(()=>document.querySelector('.solitaire-save').open=true);const path=await p.$('[aria-label="Solitaire save path"]');await path.click({clickCount:3});await p.keyboard.type('/h test.game.json');assert.equal(await p.$eval('[aria-label="Solitaire save path"]',e=>e.value),'/h test.game.json');
 await click('Save to My files');await p.waitForFunction(()=>document.querySelector('.solitaire-view .app-status')?.textContent.includes('syncing with the server'));
 const save=await p.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await mirrorFileContext()).files.read('/h test.game.json')).data)));assert.deepEqual(save.payload.foundations[0],[0]);assert.deepEqual(save.payload.tableau[1].cards,[]);assert.deepEqual(save.payload.tableau[2].cards,[21,7]);assert.deepEqual(save.payload.tableau[4].cards,[33,19]);assert.equal(save.payload.tableau[3].cards.length,18);assert.equal(save.payload.moves,3);
 assert.deepEqual(errors,[]);console.log(`PASS ${phone?'phone-sized touch':'desktop pointer'} long pile, multi-card move, keyboard move, focus marker and filename`);
}finally{await c.close();await b.disconnect()}
