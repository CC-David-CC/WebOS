const legacy=new URL(location.href).searchParams.has('legacy'),core=await import(legacy?'../../old-core/index.mjs':'../../current-core/index.mjs');
const scope=JSON.stringify(['codi-device-history/1',location.origin,'anonymous-device']),lab=window.trafficCase={legacy,core,scope,policy:new core.PersistentDeviceStorage()};
const gate=document.querySelector('button');gate.addEventListener('click',()=>lab.policy.accept({consent:true}).then(permit=>{lab.permit=permit;window.storageReady=true;},e=>lab.error=e.stack));
const status=await lab.policy.status();if(status.state==='ready'){lab.permit=await lab.policy.acquire();window.storageReady=true;}else gate.disabled=!status.supported;
lab.localLimits={windowMs:3600000,uploadBytes:10000,downloadBytes:10000,serveBytes:10000,controlBytes:16384};
lab.globalLimits={windowMs:3600000,uploadBytes:5000,downloadBytes:4096,serveBytes:3000,controlBytes:16384};
lab.raw=()=>new Promise((resolve,reject)=>{const q=indexedDB.open('codi-device-channel-directory-v1');q.onerror=()=>reject(q.error);q.onsuccess=()=>{const db=q.result,tx=db.transaction('channels','readonly'),r=tx.objectStore('channels').getAll();tx.oncomplete=()=>{const result={version:db.version,tables:[...db.objectStoreNames],rows:r.result};db.close();resolve(result);};tx.onabort=()=>{db.close();reject(tx.error);};};});
lab.prepare=async configs=>{
 lab.vault=await new core.DeviceChannelKeys().open(lab.permit);lab.keys={get:(c,o)=>lab.vault.get(scope,c,o),sign:(c,p,b,o)=>lab.vault.sign(scope,c,p,b,o)};
 lab.directory=await new core.DeviceChannelDirectory({scope,keys:lab.keys}).open(lab.permit);
 if(!configs){configs=[];for(let i=0;i<2;i++){const actor=(await lab.vault.create(scope,{label:'Migration actor '+i})).channel,wire=await core.createDeviceChannelPolicy(lab.keys,actor,{stream:'chat',publicWrite:true,publicRead:true,validators:[actor]}),policy=await core.readDeviceChannelPolicy(wire,{channel:actor}),c={channel:actor,genesisHash:policy.genesisHash,policyWire:wire};let row=await lab.directory.remember(c,actor,{label:'Preserve this bookmark '+i});await lab.directory.setTrafficLimits(actor,lab.localLimits,{expected:row.version});configs.push(c);}}
 lab.configs=configs;if(!legacy)lab.ledger=await new core.DeviceTrafficLedger({scope,limits:lab.globalLimits}).open(lab.permit);return {configs,raw:await lab.raw(),keys:await Promise.all(configs.map(c=>lab.vault.get(scope,c.channel)))};
};
lab.reserve=(i,charges,options={})=>lab.ledger.reserve(lab.configs[i].channel,lab.configs[i].genesisHash,charges,options);
lab.snapshot=i=>lab.ledger.snapshot(lab.configs[i].channel,lab.configs[i].genesisHash);
lab.setGlobal=async limits=>{const old=await lab.snapshot(0);return lab.ledger.setGlobalLimits({...old.global.limits,...limits},{expected:old.global.version});};
lab.close=async()=>{lab.ledger?.close();await lab.ledger?.idle();lab.directory?.close();lab.vault?.close();lab.policy.close();return lab.ledger?.stats()||null;};
window.fixtureReady=true;
