import assert from 'node:assert/strict';
import {DeviceChannelBandwidth} from '../network/device-channel-bandwidth.mjs';
import {ResourceBudget} from '../network/resource-budget.mjs';
const channel='A'.repeat(43),genesisHash='B'.repeat(42)+'A',body={op:'call',method:'head',channel,genesisHash},limits=()=>({windowMs:60000,uploadBytes:1048576,downloadBytes:1048576,serveBytes:1048576,controlBytes:65536});
async function scenario(explicit){
 let clock=0,requests=0,owner;const budget=new ResourceBudget(),pool={resourceBudget:budget,attachDeviceTraffic(){},detachDeviceTraffic(){}};
 const peer={id:'fixture',link:{closed:false,deviceCreditReady:true,deviceCreditCost:()=>512,sendDeviceCredit:async request=>{
  requests++;
  if(requests===1&&!explicit)throw Error('transient local send failure');
  const refused=requests===1&&explicit;
  await owner.control(peer,{op:'grant',channel,genesisHash,request_id:request.request_id,credit:refused?null:'1'.repeat(32),bytes:refused?0:4096,validForMs:refused?0:60000,retryAfterMs:refused?5000:1000},512);
 }}};
 owner=new DeviceChannelBandwidth(pool,{clock:()=>clock});owner.register(channel,genesisHash,limits);
 try{
  await assert.rejects(owner.beforeSend(peer,'device-channel-member/1',body,1024));
  clock=999;await assert.rejects(owner.beforeSend(peer,'device-channel-member/1',body,1024));assert.equal(requests,1);
  clock=1001;
  if(explicit){await assert.rejects(owner.beforeSend(peer,'device-channel-member/1',body,1024),e=>e.retryAfterMs>=3999);assert.equal(requests,1);clock=5001;}
  const credit=await owner.beforeSend(peer,'device-channel-member/1',body,1024);assert.equal(credit,'1'.repeat(32));assert.equal(requests,2);
 }finally{owner.close();await owner.idle();}
 assert.equal(budget.snapshot().metadataBytes,0);
}
await scenario(false);await scenario(true);
console.log('Transient failure retries after one second; explicit peer delay remains enforced; cleanup passed');
