// Owned host-integration fixture; not a public chat implementation.
export function mount(host){
  const f=window.hostFixture;
  if(host.network.disabled){const element=host.ui.make('div','window-content','Chat is temporarily unavailable');element.dataset.chatDisabled='';return {element,dispose(){}};}
  f.mounts++;f.active++;
  const body=host.ui.make('div','window-content'),status=host.ui.make('p','','Opening signed device history…');body.dataset.historyApp='';body.append(status);
  let closed=false,journal,keys;const timer=setInterval(()=>f.timerTicks++,10000);
  const listener=()=>f.inputEvents++;window.addEventListener('fixture-history-event',listener,{signal:host.signal});
  const stop=()=>{if(closed)return;closed=true;clearInterval(timer);f.active--;journal?.close();keys?.close();};host.onDispose(stop);
  f.liveScopes.push(host.storage.deviceHistory.scope);
  host.storage.deviceHistory.open({verify:f.verify}).then(async j=>{
    if(host.signal.aborted){j.close();return;}journal=j;
    const old=await j.load(f.channel);if(host.signal.aborted)return;
    keys=await host.storage.deviceHistory.openKeys();if(host.signal.aborted){keys.close();return;}
    (f.keyFacades??=[]).push(keys);
    status.textContent=old?'Saved note: '+(await f.payload(old.wire)).text:'No saved device note.';
    const button=host.ui.textButton('Save signed device note',async()=>{
      try{
        const previous=await j.load(f.channel),count=(previous?.floor.count||0)+1;
        const wire=await f.packet(host.storage.deviceHistory.scope,count,'Note '+count,previous?.hash||null);
        const result=await j.save(f.channel,wire,{expected:previous?.hash||null});
        if(!host.signal.aborted)status.textContent='Saved note: '+(await f.payload(result.wire)).text;
      }catch(e){if(!host.signal.aborted)status.textContent=e.message;}
    });body.append(button);body.dataset.historyReady='';
    f.facades.push(j);
  }).catch(e=>{if(!host.signal.aborted)status.textContent=e.message;});
  return {element:body,dispose:stop};
}
