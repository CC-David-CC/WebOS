import {DeviceMemberIntroductions} from '../network/device-member-introductions.mjs';
import {makeKey,thumbprint,hash,signJws,verifyJws,inspectJws} from '../network/crypto.mjs';
import {deviceChannelId} from '../assets/desktop/channel-keys.mjs';
const ok=(v,m)=>{if(!v)throw Error(m);},pins={channel:await hash('discovery-channel'),genesisHash:await hash('discovery-genesis')},people={},t=Math.floor(Date.now()/1000);
for(const sid of ['a','b','c','d']){
 const actorKey=await makeKey(),transport=await makeKey(),actor=await deviceChannelId(actorKey.publicKey),identity={sid,sub:sid,name:sid,kind:'anonymous',key:transport.publicKey,certificate:null};
 const sign=body=>signJws({version:'codi-device-channel-key/1',channel:actor,key:actorKey.publicKey,purpose:'member.grant',body},actorKey.privateKey,'codi-device-channel-key-proof+jws');
 const contact={identity,proof:await sign({profile:'codi-device-member-contact/1',...pins,sid,key:await thumbprint(identity.key),issued:t,expires:t+120})};
 people[sid]={sid,actor,transport,identity,sign,contact,entries:new Map(),members:[],bytes:0,accepts:[],offers:0};
}
const connect=(side,other)=>{const p=people[side],q=people[other],entry={id:other,peerId:other,link:{deviceMemberReady:true,closed:false,remoteIdentity:q.identity}};p.entries.set(other,entry);p.members.push({peerId:other,actor:q.actor});};
connect('a','b');connect('b','a');connect('b','c');connect('c','b');connect('c','d');connect('d','c');
for(const sid of ['a','b','c','d']){
 const p=people[sid],session={public:p.identity};
 const pool={usesSession:s=>s===session,resourceBudget:{metadata(n){p.bytes+=n;let done=false;return()=>{ok(!done,'Double release');done=true;p.bytes-=n;};},runCrypto(fn){return fn();}},list:()=>[...p.entries.values()].map(e=>({id:e.id,peerId:e.peerId})),get:id=>p.entries.get(id),closeEntry(id){p.entries.delete(id);},async offer(){const id='offer-'+(++p.offers);p.entries.set(id,{id,peerId:'pending-'+id,link:{deviceMemberReady:false,closed:false}});return {entry:{id},token:await signJws({kind:'offer',sender:p.identity},p.transport.privateKey,'codi-signal+jws')};},async answer(wire){const sender=inspectJws(wire,'codi-signal+jws').payload.sender;await verifyJws(wire,sender.key,'codi-signal+jws');return {entry:{id:'answer-entry'},token:await signJws({kind:'answer',sender:p.identity},p.transport.privateKey,'codi-signal+jws')};},async accept(_id,wire){const sender=inspectJws(wire,'codi-signal+jws').payload.sender;await verifyJws(wire,sender.key,'codi-signal+jws');p.accepts.push(sender.sid);}};
 const exchange={members:()=>p.members,async renew(){},async call(target,_pins,method,value,options){const q=people[target.id];ok(q?.helper,'Missing route peer');return q.helper.invoke(method,value,{actor:p.actor,peer:q.entries.get(sid),signal:options.signal});}};
 p.pool=pool;p.helper=new DeviceMemberIntroductions({session,identityPolicy:{mode:'local-development'},pool,exchange,channel:pins,keys:{sign:(_actor,_purpose,body)=>p.sign(body)},actor:p.actor,authorize:async()=>{}});
}
const {a,b,c,d}=people,release=[];
try{
 // Fill C's six admission slots while retaining a route from B through C to D.
 for(const sid of ['b','d'])release.push(c.helper.admit(c.entries.get(sid),people[sid].actor));
 for(let i=0;i<4;i++){const sid='occupied-'+i,identity={...a.identity,sid,sub:sid,name:sid},entry={id:sid,peerId:sid,link:{deviceMemberReady:true,closed:false,remoteIdentity:identity}};c.entries.set(sid,entry);release.push(c.helper.admit(entry,a.actor));}
 // Refresh direct hints: B knows C, and C knows D. All proofs are genuine.
 await b.helper.invoke('peers',{contact:c.contact,refresh:false},{actor:c.actor,peer:b.entries.get('c')});
 await c.helper.invoke('peers',{contact:d.contact,refresh:false},{actor:d.actor,peer:c.entries.get('d')});
 await a.helper.maintain();ok(a.offers===1&&a.accepts.length===0,'Saturated direct neighbor should refuse');
 await a.helper.maintain();ok(a.accepts.length===1&&a.accepts[0]==='d','Automatic second-hop discovery did not connect to D');
}finally{for(const done of release)done();for(const p of Object.values(people))p.helper.close();await Promise.all(Object.values(people).map(p=>p.helper.idle()));}
ok(Object.values(people).every(p=>p.bytes===0),'Resources leaked');
document.body.textContent='PASS: automatic signed two-hop discovery bypasses full neighbor and cleans up';
