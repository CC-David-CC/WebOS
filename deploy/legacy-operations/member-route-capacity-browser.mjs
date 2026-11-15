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
 const exchange={members:()=>p.members,async call(target,_pins,method,value,options){if(sid==='c'&&method==='introduce'){p.holds=(p.holds||0)+1;await new Promise((resolve,reject)=>{const abort=()=>reject(options.signal.reason||Error('aborted'));if(options.signal.aborted)abort();else options.signal.addEventListener('abort',abort,{once:true});});}const q=people[target.id];ok(q.helper,'Missing relay helper');return q.helper.invoke(method,value,{actor:p.actor,peer:q.entries.get(sid),signal:options.signal});}};
 p.helper=new DeviceMemberIntroductions({session,identityPolicy:{mode:'local-development'},pool,exchange,channel:pins,keys:{sign:(_actor,_purpose,body)=>p.sign(body)},actor:p.actor,authorize:async who=>{if(p.denied.has(who))throw Error('Denied actor');}});
}

const a=people.a,d=people.d,signal=await signJws({kind:'offer',sender:a.identity},a.transport.privateKey,'codi-signal+jws'),controllers=[],tasks=[];
const before={b:people.b.bytes,c:people.c.bytes};
try{
 for(let i=0;i<8;i++){
  const request=(i+1).toString(16).padStart(32,'0'),proof=await a.sign({profile:'codi-device-member-introduction/1',...pins,request,kind:'offer',from:'a',to:'d',target:d.actor,signal:await hash(signal),issued:t,expires:t+30}),controller=new AbortController();controllers.push(controller);
  tasks.push(people.b.helper.invoke('introduce',{operation:'offer',request,from:a.contact,to:d.contact,signal,proof,via:'c'},{actor:a.actor,peer:people.b.entries.get('a'),signal:controller.signal}).then(()=>false,()=>true));
 }
 const end=performance.now()+10000;while((people.c.holds||0)<8&&performance.now()<end)await new Promise(r=>setTimeout(r,10));
 ok(people.c.holds===8&&people.b.helper.stats().relaying===8&&people.c.helper.stats().relaying===8,'Eight relay jobs were not bounded and held');
 const request='9'.padStart(32,'0'),proof=await a.sign({profile:'codi-device-member-introduction/1',...pins,request,kind:'offer',from:'a',to:'d',target:d.actor,signal:await hash(signal),issued:t,expires:t+30});
 let refused=false;try{await people.b.helper.invoke('introduce',{operation:'offer',request,from:a.contact,to:d.contact,signal,proof,via:'c'},{actor:a.actor,peer:people.b.entries.get('a')});}catch{refused=true;}ok(refused,'Ninth relay was not refused');
 for(const controller of controllers)controller.abort(Error('test cancellation'));
 ok((await Promise.all(tasks)).every(Boolean),'Cancelled relay unexpectedly succeeded');await Promise.all([people.b.helper.idle(),people.c.helper.idle()]);
 ok(people.b.helper.stats().relaying===0&&people.c.helper.stats().relaying===0,'Relay jobs did not settle');ok(people.b.bytes===before.b&&people.c.bytes===before.c,'Relay metadata not released');
}finally{for(const controller of controllers)controller.abort();for(const sid of ['b','c','d'])people[sid].helper.close();await Promise.all(['b','c','d'].map(x=>people[x].helper.idle()));}
ok(['b','c','d'].every(x=>people[x].bytes===0),'Final resources leaked');
document.body.textContent='PASS: eight bounded relay jobs, ninth refused, cancellation releases accounting';
