import {beginSession} from './network/identity.mjs';
import {PersistentDeviceStorage,mountDeviceStorageGate} from './assets/desktop/storage-consent.mjs';
identityConfig=await (await fetch('config.json')).json();currentSession=await beginSession(identityConfig,'anonymous');
window.networkCase={approved:false,prepare(){
  networkCase.policy=new PersistentDeviceStorage();
  networkCase.view=mountDeviceStorageGate({policy:networkCase.policy,make,onReady:()=>{networkCase.approved=true;}});
  document.body.append(networkCase.view.element);
}};
window.networkCaseReady=true;
