// Holds a REAL positive native reply for observation, never fabricates geometry.
import assert from 'node:assert/strict';
export async function closePendingRegion(h,args,expectedVolume){
 await h.page.bringToFront();
 await h.frame.evaluate(()=>{
  const Native=window.Worker,Message=MessageEvent,control={started:false,closed:false,outcome:null,release:null,restore:()=>{window.Worker=Native;}};
  window.Worker=class extends Native{
   constructor(...args){super(...args);this.addEventListener('message',event=>{if(!this.selectedTask||control.started||event.data?.kind!=='result')return;event.stopImmediatePropagation();control.started=true;control.volume=event.data.evidence?.nativeVolume;control.release=()=>this.dispatchEvent(new Message('message',{data:event.data}));});}
   postMessage(data,...args){if(data?.kind==='selected-profile-extrude')this.selectedTask=true;return super.postMessage(data,...args);}
   terminate(){if(this.selectedTask)control.closed=true;return super.terminate();}
  };parent.regionHeld=control;
 });
 await h.page.evaluate(({windowId,args})=>{regionHeld.pending=codiDesktopCommands.execute({windowId,command:'edit-selected-profile-region',args}).then(value=>{regionHeld.outcome={ok:true,value};},error=>{regionHeld.outcome={ok:false,name:error.name,message:error.message,committed:error.committed===true,possiblyCommitted:error.possiblyCommitted===true};});},{windowId:h.windowId,args});
 await h.page.waitForFunction(()=>regionHeld.started,{timeout:45000,polling:100});const volume=await h.page.evaluate(()=>regionHeld.volume);assert(Number.isFinite(volume)&&Math.abs(volume-expectedVolume)<1e-6,'Genuine candidate region native volume');await h.page.evaluate(()=>regionHeld.restore());
 await h.page.click('[data-window="'+h.windowId+'"] [aria-label="Close"]');
 if(await h.page.$('.codi-confirm-dialog')){const buttons=await h.page.$$('.codi-confirm-dialog button');let clicked=false;for(const button of buttons)if(await button.evaluate(b=>b.textContent)==='Discard changes'){await button.click();clicked=true;break;}assert(clicked,'Actual discard button required');}
 await h.page.waitForFunction(id=>!document.querySelector('[data-window="'+id+'"]')&&regionHeld.outcome!==null,{timeout:30000,polling:100},h.windowId);
 const proof=await h.page.evaluate(()=>({outcome:regionHeld.outcome,workerClosed:regionHeld.closed}));assert.equal(proof.outcome.ok,false);assert.equal(proof.outcome.committed,false);assert.equal(proof.outcome.possiblyCommitted,false);assert.equal(proof.workerClosed,true);
 await h.page.evaluate(()=>regionHeld.release());await new Promise(r=>setTimeout(r,150));assert(!(await h.page.evaluate(()=>codiDesktopCommands.list())).some(c=>c.appId==='jsketcher'));await h.page.evaluate(()=>delete window.regionHeld);return{genuineNativeVolume:volume,...proof,lateReplyInert:true};
}
