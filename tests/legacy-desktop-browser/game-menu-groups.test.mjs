import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18479/';
const testURL=new URL(base);
if(!(testURL.protocol==='http:'&&['127.0.0.1','localhost','[::1]'].includes(testURL.hostname))&&testURL.origin!=='https://ksu.codes')throw Error('Unexpected test origin');
const groups={
 'Arcade games':{'Falling Blocks':'falling-blocks','Chess Study':'chess-study','Solitaire':'solitaire','Sky Courier':'sky-courier','Snake Garden':'snake-garden','Lantern Leap':'lantern-leap','Garden Defense':'garden-defense','Pocket Rally':'pocket-rally'},
 'Physics games (XR planned)':{'Physics Playground':'physics-playground','Marble Works':'marble-works','Stack & Balance':'stack-balance','Sling Targets':'sling-targets','Gravity Pinball':'gravity-pinball','Kinetic Relay':'kinetic-relay','Tabletop Bot Arena':'tabletop-bot-arena'},
 'World games (XR planned)':{'Clockwork Room':'clockwork-room','Crystal Defense':'crystal-defense','Drone Circuit':'drone-circuit','Pocket Golf':'pocket-golf','Target Garden':'target-garden','Orbital Courier':'orbital-courier','Clockwork Quest':'clockwork-quest'},
 'Interactive games':{'Owl Companion':'owl-companion','Reactive Control Desk':'reactive-control-desk','Story Cards':'story-cards','Expression Puppet':'expression-puppet','Rhythm Garden':'rhythm-garden','Memory Garden':'memory-garden'}
};
const catalog=JSON.parse(await readFile(new URL('../apps/games/catalog.json',import.meta.url),'utf8'));
for(const [label,folder] of [['Arcade games','01-phaser-arcade'],['Physics games (XR planned)','02-three-physics-xr'],['World games (XR planned)','03-babylon-xr-games'],['Interactive games','04-rive-interactives']])for(const id of Object.values(groups[label]))assert.equal(catalog[id],folder,`${id}: menu and on-disk group differ`);
assert.equal(Object.keys(catalog).length,28);
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),contexts=[];
try{
 for(const phone of [false,true]){
  const ctx=await browser.createBrowserContext();contexts.push(ctx);const p=await ctx.newPage();await p.setViewport(phone?{width:390,height:844,isMobile:true,hasTouch:true}:{width:1440,height:900});
  await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
  const user='groups'+Date.now().toString().slice(-9)+(phone?'b':'a');await p.goto(base);await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');console.log('TEST ACCOUNT',user,await p.evaluate(()=>signedInSubject()));
  const launcher=async()=>{for(let i=0;i<4;i++){try{await p.click('[aria-label=Applications]');return}catch(e){if(i===3||!String(e.message).includes('detached'))throw e}}};
  const open=async label=>p.evaluate(label=>{const buttons=[...document.querySelectorAll('.menu-pane button')],b=buttons.find(e=>e.getAttribute('aria-label')===label);if(!b)throw Error('Missing '+label);b.click()},label);
  for(const [group,apps] of Object.entries(groups)){
   await launcher();await open('Games');await open(group);
   const labels=await p.$$eval('.menu-pane[data-depth="2"] button',buttons=>buttons.map(b=>b.getAttribute('aria-label')).filter(Boolean));
   for(const label of Object.keys(apps))assert.ok(labels.includes(label+' (preview)'),`${group} missing ${label}`);
   assert.equal(labels.filter(x=>x.endsWith(' (preview)')).length,Object.keys(apps).length);
   if(phone){await open('‹ Back');assert.ok(await p.$(`.menu-pane[data-depth="1"] [aria-label="${group}"]`));}
   await launcher();
   for(const [name,id] of Object.entries(apps)){
    await p.evaluate(()=>{const d=surfaces.get('Desktop');window.realLaunch=d.launch;window.lastGameId=null;d.launch=function(app){window.lastGameId=app;return null}});
    await launcher();await open('Games');await open(group);await open(name+' (preview)');
    assert.equal(await p.evaluate(()=>window.lastGameId),id,`${name} must retain ID`);await p.evaluate(()=>{const d=surfaces.get('Desktop');d.launch=window.realLaunch});
   }
  }
 }
 console.log('PASS all 28 game groups and unchanged launch IDs on desktop and emulated phone');
}finally{for(const c of contexts)await c.close();await browser.disconnect()}
