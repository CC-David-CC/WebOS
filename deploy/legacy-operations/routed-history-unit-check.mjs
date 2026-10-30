/** Cache/lease accounting only. Synthetic verified inputs are not crypto proof. */
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const sourceFiles=['scripts/routed-history-unit-check.mjs','network/routed-history.mjs','network/resource-budget.mjs'];
const pins=()=>Object.fromEntries(sourceFiles.map(name=>[name,createHash('sha256').update(readFileSync(new URL('../'+name,import.meta.url))).digest('hex')]));
const sourcePins=pins();
import {RoutedHistory} from '../network/routed-history.mjs';
import {sessionBudget,NETWORK_LIMITS} from '../network/resource-budget.mjs';
const checks=[];function check(name,condition){assert.ok(condition,name);checks.push(name);}
let now=100;const owner={},budget=sessionBudget(owner),cache=new RoutedHistory(owner,{clock:()=>now});
const event=sequence=>({event:{room_id:'accounting-room',author_session_id:'accounting-author',stream_incarnation:'accounting-stream',sequence,kind:'chat',expires_at:101}});
for(let sequence=1;sequence<=80;sequence++)assert.equal(cache.remember(event(sequence),'token'),true);
check('one cache holds at most 64 original events',cache.snapshot().events===64);
check('evicted bytes are unavailable and newest bytes are retained',cache.get('accounting-room','accounting-author','accounting-stream',1)===null&&cache.get('accounting-room','accounting-author','accounting-stream',80)==='token');
check('all retained cache bytes charge the shared metadata budget',cache.snapshot().bytes===budget.snapshot().metadataBytes);
cache.close();check('cache close releases retained byte leases',budget.snapshot().metadataBytes===0);
check('closed cache cannot retain more input',cache.remember(event(81),'token')===false);
const large=new RoutedHistory(owner,{clock:()=>now});for(let sequence=1;sequence<=80;sequence++)large.remember(event(sequence),'x'.repeat(16384));
check('large events remain inside the 1 MiB byte cap',large.snapshot().bytes<=1048576&&large.snapshot().events<64);
check('oversized tokens are refused without growth',large.remember(event(81),'x'.repeat(16385))===false);
now=102;check('expiry withdraws unavailable originals',large.get('accounting-room','accounting-author','accounting-stream',80)===null&&large.snapshot().events===0);
check('expiry releases all metadata charges',budget.snapshot().metadataBytes===0);large.close();
now=100;const tight=new RoutedHistory(owner,{clock:()=>now}),hold=budget.metadata(NETWORK_LIMITS.metadataBytes-1);check('global metadata pressure refuses retention',tight.remember(event(1),'token')===false&&tight.snapshot().events===0);hold();tight.close();
const leases=Array.from({length:8},()=>budget.slot('repairJobs'));assert.throws(()=>budget.slot('repairJobs'),/repairJobs/);check('the ninth shared repair job is refused',budget.snapshot().repairJobs===8);
budget.close();check('closing the budget does not erase in-flight repair charges',budget.snapshot().repairJobs===8);leases.forEach(release=>release());check('settled repair jobs return all charges',Object.entries(budget.snapshot()).every(([key,value])=>key==='closed'||value===0));
assert.deepEqual(pins(),sourcePins,'Source changed during accounting tests');
process.stdout.write(JSON.stringify({sha256:sourcePins,status:'PASS',scope:'Cache and global lease accounting with synthetic verified inputs; not signature/network evidence',checks},null,2)+'\n');
