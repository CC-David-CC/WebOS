import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const b=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:120000});
try{
 for(const phone of [true,false]){
  const c=await b.createBrowserContext(),p=await c.newPage();
  try{
   await p.setViewport(phone?{width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:1}:{width:1366,height:950});
   await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
   await p.goto('http://127.0.0.1:18139/');await p.waitForSelector('.login-toggle');await p.click('.login-toggle');
   const user='layout'+Date.now().toString().slice(-8)+(phone?'a':'b');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');
   await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
   for(const app of ['text','calculator','document-editor','spreadsheet','image-editor','pdf-viewer','data-explorer','notebook','audio-editor','gcode-preview','svg-editor','diagrams-net']){
    const size=await p.evaluate(app=>{const d=surfaces.get('Desktop'),w=d.launch(app),el=d.root.querySelector('[data-window="'+w.id+'"]'),r=el.getBoundingClientRect(),screen=d.root.getBoundingClientRect();const out={width:r.width,height:r.height,screenWidth:screen.width,screenHeight:screen.height,x:r.left-screen.left,bottom:screen.bottom-r.bottom};el.querySelector('[aria-label="Close"]').click();return out;},app);
    if(phone)assert.ok(size.x<=1&&size.width>=size.screenWidth-2&&size.bottom<=2,app+' should fill phone: '+JSON.stringify(size));
    else assert.ok(size.width<size.screenWidth-10,app+' should retain its normal desktop width: '+JSON.stringify(size));
   }
   console.log('PASS',phone?'phone':'desktop','layout for 12 app types');
  }finally{await c.close();}
 }
}finally{await b.disconnect();}
