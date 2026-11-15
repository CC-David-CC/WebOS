import {DeviceMemberIntroductions} from '../network/device-member-introductions.mjs';
import {makeKey,thumbprint,hash,signJws} from '../network/crypto.mjs';
import {deviceChannelId} from '../assets/desktop/channel-keys.mjs';
const assert=(ok,message)=>{if(!ok)throw Error(message);};
const actorKey=await makeKey(),transportKey=await makeKey(),actor=await deviceChannelId(actorKey.publicKey);
const validatorKey=await makeKey(),validator=await deviceChannelId(validatorKey.publicKey);
const channel=await hash('fixture-channel'),genesisHash=await hash('fixture-genesis');
const identity=sid=>({sid,sub:sid,name:sid,kind:'anonymous',key:transportKey.publicKey,certificate:null});
const publicSession=identity('self'),session={public:publicSession},now=Math.floor(Date.now()/1000);
const sign=(body,pair=actorKey,subject=actor)=>signJws({version:'codi-device-channel-key/1',channel:subject,key:pair.publicKey,purpose:'member.grant',body},pair.privateKey,'codi-device-channel-key-proof+jws');
const contact=async (sid,pair=actorKey,subject=actor)=>({identity:identity(sid),proof:await sign({profile:'codi-device-member-contact/1',channel,genesisHash,sid,key:await thumbprint(transportKey.publicKey),issued:now,expires:now+120},pair,subject)});
let charged=0,members=[];const entries=new Map();
const budget={metadata(n){charged+=n;let released=false;return ()=>{assert(!released,'Double release');released=true;charged-=n;};},runCrypto(fn){return fn();}};
const pool={resourceBudget:budget,usesSession(v){return v===session;},list(){return [...entries.values()].map(e=>({id:e.id,peerId:e.peerId}));},get(id){return entries.get(id);}};
const exchange={members(){return members;},async renew(){},async call(){throw Error('Unexpected contact refresh');}};
const keys={async sign(_actor,_purpose,body){return sign(body);}};
const createHelper=()=>new DeviceMemberIntroductions({session,identityPolicy:{mode:'local-development'},pool,exchange,channel:{channel,genesisHash},keys,actor,authorize:async()=>{},requiredActors:[validator],settings:{contacts:32}});
let helper=createHelper();
const incoming=async (i,refresh=false,asValidator=i===1)=>{
 const sid='peer-'+i,entry={id:sid,peerId:sid,link:{deviceMemberReady:true,closed:false,remoteIdentity:identity(sid)}};entries.set(sid,entry);
 return helper.invoke('peers',{contact:await contact(sid,asValidator?validatorKey:actorKey,asValidator?validator:actor),refresh},{actor:asValidator?validator:actor,peer:entry});
};
try{
 for(let i=0;i<32;i++)await incoming(i);
 assert(helper.stats().contacts===32,'Cache did not fill');const full=charged;
 members=[{peerId:'peer-0',actor}];
 await incoming(32);assert(helper.stats().contacts===32&&charged===full,'Replacement exceeded the bound or changed accounting');
 // A live neighbor and a required validator were both older than the new hint.
 // Sampling via another peer proves they were preserved alongside the new one.
 members=[{peerId:'peer-0',actor},{peerId:'peer-1',actor:validator}];
 const observed=await incoming(33,true);
 assert(observed.contacts.length===2&&new Set(observed.contacts.map(c=>c.identity.sid)).size===2,'Protected contacts were evicted');
 members=[{peerId:'peer-32',actor}];
 const introduced=await incoming(33,true);
 assert(introduced.contacts.length===1&&introduced.contacts[0].identity.sid==='peer-32','Full cache did not admit the new signed hint');
 assert(charged===full,'Sample changed the cache charge');
}finally{helper.close();await helper.idle();}
assert(charged===0,'Cache resources leaked after close');
members=[];entries.clear();helper=createHelper();
try{
 for(let i=100;i<132;i++)await incoming(i,false,true);
 assert(helper.stats().contacts===32,'Validator duplicate cache did not fill');const full=charged;
 await incoming(132);assert(helper.stats().contacts===32&&charged===full,'Duplicate validator hints monopolized the cache');
 members=[{peerId:'peer-132',actor}];const seen=await incoming(133,true);
 assert(seen.contacts.length===1&&seen.contacts[0].identity.sid==='peer-132','Fresh ordinary contact was blocked by duplicate validator hints');
}finally{helper.close();await helper.idle();}
assert(charged===0,'Duplicate test leaked resources');
document.body.textContent='PASS: full signed contact caches, protected validator, duplicate-hint resistance and cleanup';
