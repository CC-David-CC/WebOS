import assert from 'node:assert/strict';
import {makeKey,hash} from '../network/crypto.mjs';
import {deviceChannelId} from '../assets/desktop/channel-keys.mjs';
import {createOfficialRecoveryProposal,acceptOfficialRecoveryProposal} from '../network/official-controller-recovery-proposal.mjs';
import {signOfficialRecoveryCommitteeVote,verifyOfficialRecoveryCertificate,officialRecoveryCommitteeHash} from '../network/official-controller-recovery-certificate.mjs';
const recovery=await makeKey(),prior=await makeKey(),candidate=await makeKey(),other=await makeKey();
async function members(){const rows=[];for(let i=0;i<4;i++){const key=await makeKey();rows.push({actor:await deviceChannelId(key.publicKey),key:key.publicKey,privateKey:key.privateKey});}return rows.sort((a,b)=>a.actor.localeCompare(b.actor,'en',{sensitivity:'variant'}));}
// JavaScript's lexical order, not locale collation, defines the wire order.
const old=(await members()).sort((a,b)=>a.actor<b.actor?-1:1),next=(await members()).sort((a,b)=>a.actor<b.actor?-1:1),publicRows=rows=>rows.map(({actor,key})=>({actor,key}));
const trusted={channel:await hash('channel'),genesisHash:await hash('genesis'),head:await hash('head'),generation:0,controller:await deviceChannelId(prior.publicKey),recoveryKey:recovery.publicKey,oldCommitteeHash:await officialRecoveryCommitteeHash(publicRows(old)),newCommitteeHash:await officialRecoveryCommitteeHash(publicRows(next))};
async function proposal(key){const wire=await createOfficialRecoveryProposal(trusted,key.publicKey,recovery.privateKey),acceptance=await acceptOfficialRecoveryProposal(wire,key.privateKey);return {wire,acceptance};}
async function votes(p){return Promise.all([...old.slice(0,3).map(x=>signOfficialRecoveryCommitteeVote(p.wire,p.acceptance,'old',x.actor,x.privateKey)),...next.slice(0,3).map(x=>signOfficialRecoveryCommitteeVote(p.wire,p.acceptance,'new',x.actor,x.privateKey))]);}
const p=await proposal(candidate),v=await votes(p),verify=(p,vs,oldRows=publicRows(old),newRows=publicRows(next))=>verifyOfficialRecoveryCertificate(p.wire,p.acceptance,trusted,oldRows,newRows,vs,{allowUnfencedTestVotes:true});
await assert.rejects(()=>verifyOfficialRecoveryCertificate(p.wire,p.acceptance,trusted,publicRows(old),publicRows(next),v));assert.equal((await verify(p,v)).oldVotes,3);await assert.rejects(()=>verify(p,v.slice(1)));await assert.rejects(()=>verify(p,[...v,v[0]]));
const otherVote=await signOfficialRecoveryCommitteeVote(p.wire,p.acceptance,'old',old[0].actor,other.privateKey);await assert.rejects(()=>verify(p,[otherVote,...v.slice(1)]));
const q=await proposal(other);await assert.rejects(()=>verify(q,v));await assert.rejects(()=>verify(p,v,[...publicRows(old)].reverse()));await assert.rejects(()=>verify(p,v,publicRows(old),publicRows(old)));await assert.rejects(()=>verify(p,v,publicRows(next),publicRows(next))); 
// Deliberately equivocate: certificates alone cannot prevent signers from voting twice.
const qvotes=await votes(q);assert.equal((await verify(q,qvotes)).newVotes,3);
console.log('PASS: joint quorum, signatures, scope, duplicate votes and explicit equivocation limitation');
