// Public WebOS agent commands only. No private modeling/authoring helper or UI.
import assert from 'node:assert/strict';import puppeteer from 'puppeteer-core';
const base=new URL(process.env.CODI_TEST_URL),cdp=new URL(process.env.CODI_TEST_CDP);if(![base,cdp].every(u=>['127.0.0.1','localhost','[::1]'].includes(u.hostname)))throw Error('Loopback only');const browser=await puppeteer.connect({browserURL:cdp.href,protocolTimeout:120000}),contexts=[],user='dxfagent'+Date.now(),password='test1234',path='/public-sketch.dxf';
async function login(register,name=user){const c=await browser.createBrowserContext();contexts.push(c);const p=await c.newPage();await p.goto(base);await p.waitForSelector('.login-toggle');if(register)await p.click('.login-toggle');await p.type('[aria-label=Username]',name);await p.type('[aria-label=Password]',password);if(register)await p.type('[aria-label="Confirm password"]',password);await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>desktopLab?.session?.kind==='registered',{timeout:30000});return p;}
async function cmd(p,id,args={}){return p.evaluate(({id,args})=>{const c=codiDesktopCommands.list().find(x=>x.appId==='jsketcher'&&x.id===id);if(!c)throw Error('Command unavailable: '+id);return codiDesktopCommands.execute({windowId:c.windowId,command:id,args})},{id,args});}
async function sync(p,filePath=path){const end=Date.now()+60000;while(Date.now()<end){try{const r=await p.evaluate(async path=>{const l=await(await mirrorFileContext()).files.read(path),s=await(await serverFileContext()).files.read(path.slice(1));return {local:l.sha256,server:s.sha256,text:new TextDecoder().decode(s.data)}},filePath);if(r.local===r.server)return r}catch{}await new Promise(r=>setTimeout(r,500))}throw Error('Signed file did not sync');}
async function inspect(p,faceId){const list=await cmd(p,'inspect-closed-sketches');assert.equal(list.ready,true);assert.ok(list.candidates.some(c=>c.faceId===faceId));return cmd(p,'inspect-closed-sketch',{revision:list.revision,faceId})}
function parseDxf(text){const lines=text.replace(/\r/g,'').split('\n');while(lines.at(-1)==='')lines.pop();assert.equal(lines.length%2,0,'DXF code/value pairs');const pairs=[];for(let i=0;i<lines.length;i+=2)pairs.push([lines[i].trim(),lines[i+1].trim()]);let section='',active=false,entities=[],current=null;for(let i=0;i<pairs.length;i++){const [code,value]=pairs[i];if(code==='0'&&value==='SECTION'){section=pairs[i+1]?.[1];active=section==='ENTITIES';current=null;continue}if(code==='0'&&value==='ENDSEC'){active=false;current=null;continue}if(active&&code==='0'){current={type:value,groups:[]};entities.push(current)}else if(active&&current)current.groups.push([code,value])}return {pairs,entities}}
const number=(entity,code)=>Number(entity.groups.find(x=>x[0]===String(code))?.[1]);
try{
 console.log('TEST_ACCOUNTS',user,user+'b','FILE',path);let p=await login(true);await p.evaluate(()=>surfaces.get('Desktop').launch('jsketcher'));await p.waitForFunction(()=>document.querySelector('.jsketcher-app .app-status')?.textContent.startsWith('New model.'),{timeout:90000});const creation=await cmd(p,'inspect-sketch-creation'),plane=await cmd(p,'create-empty-sketch-plane',{revision:creation.revision,unit:'millimeter',plane:'XY',depth:0});
 const specs=[{kind:'Point',role:null,data:{x:2,y:3}},{kind:'Segment',role:null,data:{a:{x:0,y:0},b:{x:10,y:0}}},{kind:'Circle',role:null,data:{c:{x:30,y:10},r:5}},{kind:'Arc',role:null,data:{a:{x:51,y:0},b:{x:50,y:1},c:{x:50,y:0}}}];for(const spec of specs){const info=await inspect(p,plane.faceId);await cmd(p,'append-sketch-primitive',{revision:info.revision,faceId:plane.faceId,stage:0,...spec})}
 const beforeExport=await inspect(p,plane.faceId),exports=await cmd(p,'inspect-sketch-dxf-exports');assert.ok(exports.candidates.some(x=>x.faceId===plane.faceId));await assert.rejects(cmd(p,'export-sketch-dxf',{revision:exports.revision,faceId:'missing',path:'/bad-face.dxf'}));await assert.rejects(cmd(p,'export-sketch-dxf',{revision:'stale',faceId:plane.faceId,path:'/bad-stale.dxf'}));const receipt=await cmd(p,'export-sketch-dxf',{revision:exports.revision,faceId:plane.faceId,path});assert.equal(receipt.unit,'millimeter');assert.equal(receipt.coordinates,'sketch-local');assert.equal(receipt.faceId,plane.faceId);assert.equal(receipt.serverStatus,'not-verified');const written=await sync(p),parsed=parseDxf(written.text);assert.ok(parsed.pairs.some((x,i)=>x[0]==='9'&&x[1]==='$INSUNITS'&&parsed.pairs[i+1]?.[0]==='70'&&parsed.pairs[i+1]?.[1]==='4'));const entities=parsed.entities;assert.deepEqual(entities.map(x=>x.type).sort(),['ARC','CIRCLE','LINE','POINT']);const find=t=>entities.find(x=>x.type===t),point=find('POINT'),line=find('LINE'),circle=find('CIRCLE'),arc=find('ARC');assert.deepEqual([number(point,10),number(point,20)],[2,3]);assert.deepEqual([number(line,10),number(line,20),number(line,11),number(line,21)],[0,0,10,0]);assert.deepEqual([number(circle,10),number(circle,20),number(circle,40)],[30,10,5]);assert.deepEqual([number(arc,10),number(arc,20),number(arc,40)],[50,0,1]);assert.ok(Math.abs(number(arc,50))<1e-9&&Math.abs(number(arc,51)-90)<1e-9);await assert.rejects(cmd(p,'export-sketch-dxf',{revision:exports.revision,faceId:plane.faceId,path}));assert.equal((await sync(p)).server,written.server);assert.deepEqual(await inspect(p,plane.faceId),beforeExport);
 const info=await inspect(p,plane.faceId);await cmd(p,'append-sketch-primitive',{revision:info.revision,faceId:plane.faceId,stage:0,kind:'Point',role:null,data:{x:8,y:9}});await assert.rejects(cmd(p,'export-sketch-dxf',{revision:exports.revision,faceId:plane.faceId,path:'/stale-after-edit.dxf'}));const nextCreation=await cmd(p,'inspect-sketch-creation'),xz=await cmd(p,'create-empty-sketch-plane',{revision:nextCreation.revision,unit:'millimeter',plane:'XZ',depth:17});
 const xzInfo=await inspect(p,xz.faceId);await cmd(p,'append-sketch-primitive',{revision:xzInfo.revision,faceId:xz.faceId,stage:0,kind:'Point',role:null,data:{x:3,y:4}});
 const xzExports=await cmd(p,'inspect-sketch-dxf-exports'),xzPath='/local-xz-sketch.dxf',xzReceipt=await cmd(p,'export-sketch-dxf',{revision:xzExports.revision,faceId:xz.faceId,path:xzPath});
 assert.notDeepEqual(xzReceipt.frame,receipt.frame);const xzSaved=await sync(p,xzPath),xzEntities=parseDxf(xzSaved.text).entities;
 assert.deepEqual(xzEntities.map(e=>e.type),['POINT']);assert.deepEqual([number(xzEntities[0],10),number(xzEntities[0],20),number(xzEntities[0],30)],[3,4,0]);
 const other=await login(true,user+'b'),denial=await other.evaluate(async path=>{try{await(await serverFileContext()).files.read(path.slice(1));return 'read succeeded'}catch(e){return e.status}},path);assert.ok([403,404].includes(denial));// The delivery fault holds the actual backend result after its real Worker
 // has finished. It does not replace geometry, DXF bytes, or the native Worker.
 // Closing the app must retire its operation token before that result is freed.
 const currentExports=await cmd(p,'inspect-sketch-dxf-exports'),heldPath='/closed-before-dxf-delivery.dxf';
 await p.evaluate(()=>{
  const craft=document.querySelector('.jsketcher-app iframe').contentWindow.__CAD_APP.craftService;
  const original=craft.exportSketchDXFBlob.bind(craft);
  window.dxfDelivery={ready:false,release:null,outcome:null};
  craft.exportSketchDXFBlob=async(...args)=>{
   const result=await original(...args);
   return new Promise(resolve=>{dxfDelivery.release=()=>resolve(result);dxfDelivery.ready=true;});
  };
 });
 await p.evaluate(args=>{
  const c=codiDesktopCommands.list().find(c=>c.appId==='jsketcher'&&c.id==='export-sketch-dxf');
  dxfDelivery.pending=codiDesktopCommands.execute({windowId:c.windowId,command:c.id,args}).then(
   ()=>{dxfDelivery.outcome='unexpected success'},error=>{dxfDelivery.outcome=error.message});
 },{revision:currentExports.revision,faceId:plane.faceId,path:heldPath});
 await p.waitForFunction(()=>dxfDelivery.ready,{timeout:30000});
 await p.click('.window:has(.jsketcher-app) [aria-label="Close"]');
 if(await p.$('.codi-confirm-dialog'))await p.evaluate(()=>[...document.querySelectorAll('.codi-confirm-dialog button')].find(b=>b.textContent==='Discard changes').click());
 await p.waitForFunction(()=>!document.querySelector('.jsketcher-app')&&dxfDelivery.outcome!==null);
 assert.notEqual(await p.evaluate(()=>dxfDelivery.outcome),'unexpected success');
 await p.evaluate(()=>dxfDelivery.release());
 await new Promise(resolve=>setTimeout(resolve,500));
 const noLateFile=await p.evaluate(async path=>{
  const absent=async fn=>{try{await fn();return false}catch(e){return e.message==='File not found.'||[403,404].includes(e.status)}};
  return {browser:await absent(async()=> (await mirrorFileContext()).files.stat(path)),server:await absent(async()=> (await serverFileContext()).files.read(path.slice(1)))};
 },heldPath);
 assert.deepEqual(noLateFile,{browser:true,server:true});
 assert.ok(!(await p.evaluate(()=>codiDesktopCommands.list())).some(c=>c.appId==='jsketcher'));
 const old=p.browserContext();await old.close();contexts.splice(contexts.indexOf(old),1);
 p=await login(false);const reopened=await sync(p);assert.equal(reopened.server,written.server);assert.equal(reopened.text,written.text);assert.equal((await sync(p,xzPath)).server,xzSaved.server);
 console.log('SERVER_HASH',written.server);console.log('PASS real public sketch DXF export, independent entities/units, stale/no-overwrite, close before real-result delivery, account isolation and fresh-login durable read');
}finally{for(const c of contexts)await c.close().catch(()=>{});browser.disconnect()}
