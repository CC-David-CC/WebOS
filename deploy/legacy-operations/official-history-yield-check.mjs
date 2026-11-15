import assert from 'node:assert/strict';
import {installOfficialHistoryPage} from '../assets/desktop/official-history-page.mjs';
const head='A'.repeat(43),page={status:'experimental-replayed-segment',afterHeight:0,height:3,head,complete:true,blocks:[1,2,3].map(height=>({height,wire:'{}'}))};
let height=0,steps=0,release,started;const gate=new Promise(r=>release=r),paused=new Promise(r=>started=r),archive={load:async()=>({position:{height,head}}),append:async()=>({position:{height:++height,head}})};
const task=installOfficialHistoryPage(archive,page,{beforeBlock:async()=>{if(++steps===2){started();await gate;}}});await paused;assert.equal(height,1);release();assert.equal((await task).height,3);assert.equal(steps,3);
let unblock,entered;const wait=new Promise(r=>unblock=r),waiting=new Promise(r=>entered=r),abort=new AbortController();height=0;const cancelled=installOfficialHistoryPage(archive,page,{signal:abort.signal,beforeBlock:async()=>{entered();await wait;}});await waiting;abort.abort();unblock();await assert.rejects(cancelled);assert.equal(height,0);
console.log('PASS history yields before each block and abort does not append after the yield');

height=0;const reported=[];const corrupt={load:archive.load,append:async()=>{if(height===1)throw Error('bad block');return {position:{height:++height,head}};}};
await assert.rejects(installOfficialHistoryPage(corrupt,page,{onBatch:p=>reported.push(p.height)}),/bad block/);assert.deepEqual(reported,[1],'only successfully committed batches produce progress');
height=0;await assert.rejects(installOfficialHistoryPage(archive,page,{onBatch:'bad'}),/Invalid history progress/);assert.equal(height,0);
console.log('PASS progress reports only committed verified batches');
