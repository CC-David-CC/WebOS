// Hold only a real positive production native result; public host depth edit,
// then actual visible window Close. No fabricated successful Worker envelope.
import assert from 'node:assert/strict';
import {cmd,frame} from '../numeric-expressions/helpers.mjs';
export async function closePendingDepth(p,depth=9){
 const info=await cmd(p,'inspect-selected-profile-history'),feature=info.features[0];assert.equal(info.ready,true,info.reason);await p.bringToFront();
 await(await frame(p)).evaluate(()=>{
  const Native=window.Worker,Message=MessageEvent,control={started:false,closed:false,outcome:null,release:null,restore:()=>{window.Worker=Native;}};
  window.Worker=class extends Native{
   constructor(...args){super(...args);this.addEventListener('message',event=>{if(!this.selectedTask||control.started||event.data?.kind!=='result')return;event.stopImmediatePropagation();control.started=true;control.volume=event.data.evidence?.nativeVolume;control.release=()=>this.dispatchEvent(new Message('message',{data:event.data}));});}
   postMessage(data,...args){if(data?.kind==='selected-profile-extrude')this.selectedTask=true;return super.postMessage(data,...args);}
   terminate(){if(this.selectedTask)control.closed=true;return super.terminate();}
  };parent.selectedDepthHeld=control;
 });
 await p.evaluate(args=>{const c=codiDesktopCommands.list().find(c=>c.appId==='jsketcher'&&c.id==='edit-selected-profile-depth');selectedDepthHeld.pending=codiDesktopCommands.execute({windowId:c.windowId,command:c.id,args}).then(value=>{selectedDepthHeld.outcome={ok:true,value};},error=>{selectedDepthHeld.outcome={ok:false,name:error.name,message:error.message,committed:error.committed===true};});},{revision:info.revision,index:feature.index,featureId:feature.featureId,depth});
 await p.waitForFunction(()=>selectedDepthHeld.started,{timeout:45000,polling:100});const volume=await p.evaluate(()=>selectedDepthHeld.volume);assert.ok(Math.abs(volume-300*Math.PI*depth)<1e-6,'Genuine annulus native volume');await p.evaluate(()=>selectedDepthHeld.restore());
 await p.click('.window:has(.jsketcher-app) [aria-label="Close"]');if(await p.$('.codi-confirm-dialog'))await p.evaluate(()=>[...document.querySelectorAll('.codi-confirm-dialog button')].find(b=>b.textContent==='Discard changes')?.click());
 await p.waitForFunction(()=>!document.querySelector('.jsketcher-app')&&selectedDepthHeld.outcome!==null,{timeout:30000,polling:100});const outcome=await p.evaluate(()=>selectedDepthHeld.outcome);assert.equal(outcome.ok,false);assert.equal(outcome.committed,false);assert.equal(await p.evaluate(()=>selectedDepthHeld.closed),true);
 await p.evaluate(()=>selectedDepthHeld.release());await new Promise(resolve=>setTimeout(resolve,150));assert.ok(!(await p.evaluate(()=>codiDesktopCommands.list())).some(c=>c.appId==='jsketcher'));await p.evaluate(()=>delete window.selectedDepthHeld);
 return{label:'actual visible Close cancels pending host depth edit; genuine late native result inert',genuineNativeVolume:volume,outcome,workerClosed:true,lateReplyInert:true};
}
