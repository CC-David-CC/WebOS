// Genuine production native result delayed, adapted from the source public
// selected-profile lifecycle and existing signed Axis Open/Close controls.
import assert from 'node:assert/strict';
import {frame,capture,cmd,discover,intent} from './helpers.mjs';
async function start(p,args,mode='native'){
 await p.bringToFront();await(await frame(p)).evaluate(mode=>{
  const Native=window.Worker,Message=MessageEvent,control={started:false,closed:false,outcome:null,release:null,restore:()=>{window.Worker=Native;}};
  window.Worker=class extends Native{
   constructor(...args){super(...args);this.addEventListener('message',event=>{if(!this.selectedTask||control.started||!(mode==='native'?event.data?.kind==='result':event.data?.ok===true))return;event.stopImmediatePropagation();control.started=true;control.volume=event.data.evidence?.nativeVolume;control.release=()=>this.dispatchEvent(new Message('message',{data:event.data}));});}
   postMessage(data,...args){if(data?.kind===(mode==='native'?'selected-profile-extrude':'inspect-selected'))this.selectedTask=true;return super.postMessage(data,...args);}
   terminate(){if(this.selectedTask)control.closed=true;return super.terminate();}
  };parent.selectedHeld=control;
 },mode);
 await p.evaluate(({args,mode})=>{const c=codiDesktopCommands.list().find(c=>c.appId==='jsketcher'&&c.id===(mode==='native'?'create-selected-extrusion':'inspect-selected-regions'));selectedHeld.pending=codiDesktopCommands.execute({windowId:c.windowId,command:c.id,args}).then(value=>{selectedHeld.outcome={ok:true,value};},e=>{selectedHeld.outcome={ok:false,name:e.name,message:e.message,committed:!!e.committed};});},{args,mode});
 await p.waitForFunction(()=>selectedHeld.started,{timeout:45000,polling:100});
 if(mode==='native')assert.ok(Math.abs(await p.evaluate(()=>selectedHeld.volume)-500*Math.PI)<1e-6,'Held genuine positive native result');await p.evaluate(()=>selectedHeld.restore());
}
export async function openKeepEditing(p,faceId){
 const before=await capture(p,faceId),d=await discover(p,faceId);await start(p,{revision:d.info.revision,faceId,depth:5},'inspect');
 const f=await frame(p);await f.click('[data-action-id="menu.file"]');await f.click('[data-action-id="NativeFormatImport"]');
 try{await p.waitForSelector('.codi-confirm-dialog',{timeout:8000});}catch(error){error.details=await p.evaluate(()=>({status:document.querySelector('.jsketcher-app .app-status')?.textContent,dialogs:[...document.querySelectorAll('dialog')].map(d=>({open:d.open,text:d.textContent})),held:{started:selectedHeld.started,closed:selectedHeld.closed,outcome:selectedHeld.outcome,volume:selectedHeld.volume}}));throw error;}
 await p.waitForFunction(()=>selectedHeld.outcome!==null,{timeout:10000,polling:100});const outcome=await p.evaluate(()=>selectedHeld.outcome);assert.equal(outcome.ok,false);assert.equal(outcome.name,'AbortError');assert.equal(outcome.committed,false);
 await p.evaluate(()=>[...document.querySelectorAll('.codi-confirm-dialog button')].find(b=>b.textContent==='Keep editing').click());
 assert.equal(await p.evaluate(()=>selectedHeld.closed),true);assert.deepEqual(await capture(p,faceId),before);
 await p.evaluate(()=>selectedHeld.release());await new Promise(r=>setTimeout(r,150));assert.deepEqual(await capture(p,faceId),before);await p.evaluate(()=>delete window.selectedHeld);
 return{scenario:'actual File/Open then Keep editing during genuine successful region-discovery delivery delay',genuineSemanticSuccess:true,outcome,priorStateExact:true,lateReplyInert:true};
}
export async function closePending(p,faceId){
 const d=await discover(p,faceId);await start(p,intent(d,faceId));await p.click('.window:has(.jsketcher-app) [aria-label="Close"]');
 if(await p.$('.codi-confirm-dialog'))await p.evaluate(()=>[...document.querySelectorAll('.codi-confirm-dialog button')].find(b=>b.textContent==='Discard changes')?.click());
 await p.waitForFunction(()=>!document.querySelector('.jsketcher-app')&&selectedHeld.outcome!==null,{timeout:30000,polling:100});
 const outcome=await p.evaluate(()=>selectedHeld.outcome);assert.equal(outcome.ok,false);assert.equal(outcome.committed,false);assert.equal(await p.evaluate(()=>selectedHeld.closed),true);
 await p.evaluate(()=>selectedHeld.release());await new Promise(r=>setTimeout(r,150));assert.ok(!(await p.evaluate(()=>codiDesktopCommands.list())).some(c=>c.appId==='jsketcher'));await p.evaluate(()=>delete window.selectedHeld);
 return{scenario:'actual Close during native success delivery delay',outcome,genuineNativeVolume:500*Math.PI,lateReplyInert:true};
}
