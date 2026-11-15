import {beginSession} from '../.build/shared-services/device-member-data-r8/assets/desktop/services/device-history/ec72b1b09c2366d42ff4930a67e15f9a857cf94d8c1e688b2a9e7058a838ac05/index.mjs';
import {makeKey,signJws} from '../network/crypto.mjs';
import {deviceChannelId} from '../.build/shared-services/device-member-data-r8/assets/desktop/services/device-history/ec72b1b09c2366d42ff4930a67e15f9a857cf94d8c1e688b2a9e7058a838ac05/index.mjs';
import {createDeviceChannelPolicy,readDeviceChannelPolicy} from '../.build/shared-services/device-member-data-r8/assets/desktop/services/device-history/ec72b1b09c2366d42ff4930a67e15f9a857cf94d8c1e688b2a9e7058a838ac05/index.mjs';
import {PeerPool} from '../.build/shared-services/device-member-data-r8/assets/desktop/services/device-history/ec72b1b09c2366d42ff4930a67e15f9a857cf94d8c1e688b2a9e7058a838ac05/index.mjs';
import {DeviceReplicaExchange} from '../.build/shared-services/device-member-data-r8/assets/desktop/services/device-history/ec72b1b09c2366d42ff4930a67e15f9a857cf94d8c1e688b2a9e7058a838ac05/index.mjs';
import {DeviceMemberIntroductions} from '../.build/shared-services/device-member-data-r8/assets/desktop/services/device-history/ec72b1b09c2366d42ff4930a67e15f9a857cf94d8c1e688b2a9e7058a838ac05/index.mjs';
const side=new URL(location.href).searchParams.get('side'),config={identity:{mode:'local-development'},rtc:{iceServers:[]}},session=await beginSession(config,'anonymous',side),key=await makeKey(),actor=await deviceChannelId(key.publicKey);
const keys={sign:(subject,purpose,body)=>{if(subject!==actor)throw Error('Wrong fixture key');return signJws({version:'codi-device-channel-key/1',channel:actor,key:key.publicKey,purpose,body},key.privateKey,'codi-device-channel-key-proof+jws');}};
let exchange,topology;const logs=[],denied=new Set();let denials=0;
const pool=new PeerPool(session,config,{onState:e=>{exchange?.state(e);topology?.onPoolState(e);},onDeviceMember:(e,a)=>exchange.receive(e,a)});
let pins;
async function init(wire,controller){const policy=await readDeviceChannelPolicy(wire,{channel:controller});pins={channel:policy.channel,genesisHash:policy.genesisHash};const authorize=async who=>{if(denied.has(who)){denials++;throw Error('Fixture actor permission denied');}},adapter={actor,keys,policy,authorize,admitPeer:(e,who)=>topology.admit(e,who),invoke:(method,value,options)=>topology.invoke(method,value,options)};
 exchange=new DeviceReplicaExchange(session,pool,{profile:'member',resolveChannel:(c,g)=>c===pins.channel&&g===pins.genesisHash?adapter:null,timeoutMs:15000});
 const call=exchange.call.bind(exchange);exchange.call=(entry,p,method,value,options)=>{if(method==='introduce'&&value.operation==='offer')logs.push({via:value.via||null,to:value.to.identity.sid});return call(entry,p,method,value,options);};
 topology=new DeviceMemberIntroductions({session,identityPolicy:config.identity,pool,exchange,channel:pins,keys,actor,authorize,settings:{target:2,maxNeighbors:side==='c'?2:6,sampleMs:1000,backoffMs:1000}});
}
window.routeFixture={actor,sid:session.public.sid,logs,deny:who=>denied.add(who),allow:who=>denied.delete(who),createPolicy:()=>createDeviceChannelPolicy(keys,actor,{publicRead:true}),init,offer:()=>pool.offer(),answer:token=>pool.answer(token),accept:(id,token)=>pool.accept(id,token),entries:()=>pool.list(),bind:(id,expectedActor)=>exchange.bind(pool.get(id),{...pins,expectedActor}),sample:id=>topology.sample(id),maintain:()=>topology.maintain(),stats:()=>({denials,topology:topology?.stats(),exchange:exchange?.stats(),budget:pool.resourceBudget.snapshot(),entries:pool.list()}),async close(){topology?.close();exchange?.close();pool.close();await Promise.all([topology?.idle(),exchange?.idle()]);return pool.resourceBudget.snapshot();}};
window.fixtureReady=true;
