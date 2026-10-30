import {DeviceMemberIntroductions,verifyDeviceMemberContact} from '../network/device-member-introductions.mjs';
import {makeKey,thumbprint,hash,signJws} from '../network/crypto.mjs';
import {deviceChannelId,verifyDeviceChannelProof} from '../assets/desktop/channel-keys.mjs';
const ok=(v,m)=>{if(!v)throw Error(m);},channel=await hash('route-channel'),genesisHash=await hash('route-genesis'),pins={channel,genesisHash};
const typ='codi-device-channel-key-proof+jws',t=Math.floor(Date.now()/1000),people={};
for(const sid of ['a','b','c','d']){
 const actorKey=await makeKey(),transport=await makeKey(),actor=await deviceChannelId(actorKey.publicKey),identity={sid,sub:sid,name:sid,kind:'anonymous',key:transport.publicKey,certificate:null};
 const sign=body=>signJws({version:'codi-device-channel-key/1',channel:actor,key:actorKey.publicKey,purpose:'member.grant',body},actorKey.privateKey,typ);
 const contact={identity,proof:await sign({profile:'codi-device-member-contact/1',...pins,sid,key:await thumbprint(identity.key),issued:t,expires:t+120})};
 people[sid]={sid,actor,actorKey,transport,identity,sign,contact,entries:new Map(),members:[],bytes:0,denied:new Set()};
}
const connect=(side,other)=>{const a=people[side],b=people[other],entry={id:other,peerId:other,link:{deviceMemberReady:true,closed:false,remoteIdentity:b.identity}};a.entries.set(other,entry);a.members.push({peerId:other,actor:b.actor});};
connect('b','a');connect('b','c');connect('c','b');connect('c','d');connect('d','c');
for(const sid of ['b','c','d']){
 const p=people[sid],session={public:p.identity};
 const pool={usesSession:s=>s===session,resourceBudget:{metadata(n){p.bytes+=n;let done=false;return()=>{ok(!done,'Double release');done=true;p.bytes-=n;};},runCrypto(fn){return fn();}},list:()=>[...p.entries.values()].map(e=>({id:e.id,peerId:e.peerId})),get:id=>p.entries.get(id),closeEntry(){},async answer(){return {entry:{id:'answer-entry'},token:await signJws({kind:'answer',sender:p.identity},p.transport.privateKey,'codi-signal+jws')};}};
 const exchange={members:()=>p.members,async call(target,_pins,method,value,options){const q=people[target.id];ok(q.helper,'Missing relay helper');return q.helper.invoke(method,value,{actor:p.actor,peer:q.entries.get(sid),signal:options.signal});}};
 p.helper=new DeviceMemberIntroductions({session,identityPolicy:{mode:'local-development'},pool,exchange,channel:pins,keys:{sign:(_actor,_purpose,body)=>p.sign(body)},actor:p.actor,authorize:async who=>{if(p.denied.has(who))throw Error('Denied actor');}});
}
const a=people.a,d=people.d,request='1'.repeat(32),signal=await signJws({kind:'offer',sender:a.identity},a.transport.privateKey,'codi-signal+jws');
const proof=await a.sign({profile:'codi-device-member-introduction/1',...pins,request,kind:'offer',from:'a',to:'d',target:d.actor,signal:await hash(signal),issued:t,expires:t+30});
const value={operation:'offer',request,from:a.contact,to:d.contact,signal,proof,via:'c'},options={actor:a.actor,peer:people.b.entries.get('a')};
try{
 const answer=await people.b.helper.invoke('introduce',value,options);ok(answer.operation==='answer'&&answer.request===request,'Missing routed answer');
 const answerFrom=await verifyDeviceMemberContact(answer.from,pins,{mode:'local-development'});ok(answerFrom.actor===d.actor,'Answer identity changed');
 const signed=await verifyDeviceChannelProof(answer.proof,{channel:d.actor,purpose:'member.grant'});ok(signed.body.to==='a'&&signed.body.from==='d'&&signed.body.signal===await hash(answer.signal),'Answer signature changed endpoints');
 let denied=false;try{await people.b.helper.invoke('introduce',value,options);}catch{denied=true;}ok(denied,'Replay accepted');
 const second={...value,request:'2'.repeat(32)};second.proof=await a.sign({...signed.body,profile:'codi-device-member-introduction/1',request:second.request,kind:'offer',from:'a',to:'d',target:d.actor,signal:await hash(signal),issued:t,expires:t+30});
 people.c.denied.add(a.actor);denied=false;try{await people.b.helper.invoke('introduce',second,options);}catch{denied=true;}ok(denied,'Unauthorized origin crossed the second relay');
}finally{for(const sid of ['b','c','d'])people[sid].helper.close();await Promise.all(['b','c','d'].map(s=>people[s].helper.idle()));}
ok(['b','c','d'].every(s=>people[s].bytes===0),'Relay resources leaked');
document.body.textContent='PASS: signed two-hop introduction, replay and permission refusal, cleanup';
