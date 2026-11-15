import {memberContactVictim} from '../network/device-member-introductions.mjs';
const equal=(a,b)=>{if(a!==b)throw new Error(`Expected ${b}, got ${a}`);};

const contacts=new Map([
 ['bound',{actor:'ordinary',expires:1,backoff:100}],
 ['pending',{actor:'ordinary',expires:2,backoff:100}],
 ['validator',{actor:'required',expires:3,backoff:100}],
 ['fresh',{actor:'ordinary',expires:60,backoff:0}],
 ['failed',{actor:'ordinary',expires:100,backoff:30}],
]);
const policy={bound:new Set(['bound']),pending:new Set(['pending']),required:new Set(['required']),now:10};
equal(memberContactVictim(contacts,policy),'failed');
contacts.delete('failed');
equal(memberContactVictim(contacts,policy),'fresh');
contacts.delete('fresh');
equal(memberContactVictim(contacts,policy),null);
equal(contacts.size,3);
const duplicates=new Map([['a',{actor:'required',expires:1,backoff:0}],['b',{actor:'required',expires:2,backoff:0}]]);
equal(memberContactVictim(duplicates,{bound:new Set(),pending:new Set(),required:new Set(['required']),now:10}),'a');
duplicates.delete('a');equal(memberContactVictim(duplicates,{bound:new Set(),pending:new Set(),required:new Set(['required']),now:10}),null);
document.body.textContent='PASS: failed idle hints are replaced first; live, pending and required contacts remain protected';
