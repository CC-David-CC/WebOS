import {makeKey,hash,signJws,inspectJws} from '../network/crypto.mjs';
import {deviceChannelId} from '../assets/desktop/channel-keys.mjs';
import {createOfficialRecoveryProposal,acceptOfficialRecoveryProposal,verifyOfficialRecoveryProposal} from '../network/official-controller-recovery-proposal.mjs';
const recover=await makeKey(),next=await makeKey(),other=await makeKey(),old=await makeKey();
const trusted={channel:await hash('channel'),genesisHash:await hash('genesis'),head:await hash('head'),generation:0,oldCommitteeHash:await hash('old committee'),newCommitteeHash:await hash('new committee'),controller:await deviceChannelId(old.publicKey),recoveryKey:recover.publicKey};
const wire=await createOfficialRecoveryProposal(trusted,next.publicKey,recover.privateKey),acceptance=await acceptOfficialRecoveryProposal(wire,next.privateKey),cases=[];
async function add(name,w=wire,a=acceptance,t=trusted){let ok=true;try{await verifyOfficialRecoveryProposal(w,a,t);}catch{ok=false;}cases.push({name,wire:w,acceptance:a,trusted:t,expected:ok});}
await add('valid');for(const [name,value] of Object.entries({channel:await hash('bad channel'),genesisHash:await hash('bad genesis'),head:await hash('bad head'),oldCommitteeHash:await hash('wrong old group'),newCommitteeHash:await hash('wrong new group'),generation:1,controller:await deviceChannelId(other.publicKey),recoveryKey:other.publicKey}))await add('wrong '+name,wire,acceptance,{...trusted,[name]:value});
await add('noninteger generation',wire,acceptance,{...trusted,generation:true});await add('extra context field',wire,acceptance,{...trusted,extra:1});
const unsigned=inspectJws(wire,'codi-official-controller-recovery-proposal/1').payload;
for(const [name,payload] of [['extra proposal field',{...unsigned,extra:1}],['wrong version',{...unsigned,version:'wrong'}],['wrong replacement',{...unsigned,replacement:await deviceChannelId(other.publicKey)}],['generation bool',{...unsigned,generation:true}]]){const w=await signJws(payload,recover.privateKey,'codi-official-controller-recovery-proposal/1');await add(name,w,acceptance);}
await add('wrong acceptance key',wire,await acceptOfficialRecoveryProposal(wire,other.privateKey));
const second=await createOfficialRecoveryProposal(trusted,other.publicKey,recover.privateKey),secondAccept=await acceptOfficialRecoveryProposal(second,other.privateKey);await add('competing valid proposal',second,secondAccept);await add('mixed competing acceptance',second,acceptance);
await add('corrupt signature',wire.slice(0,-2)+(wire.endsWith('AA')?'BB':'AA'),acceptance);
console.log(JSON.stringify(cases));
