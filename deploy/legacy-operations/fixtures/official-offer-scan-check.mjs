import assert from 'node:assert/strict';
const {hash}=await import('../../network/crypto.mjs');
const {createOfficialOfferScan}=await import('../../assets/desktop/official-history-offer.mjs');
const channel=await hash('channel'),genesisHash=await hash('genesis'),floor=await hash('floor'),nodes=new Map(),rows=new Map();
async function node(value){const wire=JSON.stringify(value),cid=await hash(wire);nodes.set(cid,wire);return cid;}
const chunk=await node({profile:'codi-channel-content/1',kind:'chunk',data:'YQ'}),blob=await node({profile:'codi-channel-content/1',kind:'blob',bytes:1,tree:{cid:chunk,bytes:1,height:0}});
let previous=floor,parent=null,tip;
for(let height=1;height<=1100;height++){
  const head=await hash('head-'+height),cid=await node({profile:'codi-channel-content/1',kind:'head',channel,genesisHash,height,head,parent,block:blob});
  rows.set(cid,{cid,height,head,block:{header:{parent:previous}},next:parent});previous=head;parent=cid;tip={channel,genesisHash,height,head,history:cid};
}
const archive={transferHead:async()=>tip,readNode:async cid=>nodes.get(cid),history:async({before,limit})=>{let cid=before||tip.history,entries=[];while(cid&&entries.length<limit){const row=rows.get(cid);entries.push(row);cid=row.next;}return {entries,next:cid};}};
const scan=await createOfficialOfferScan(archive,{afterHeight:0,afterHead:floor});let progress,steps=0;do{progress=await scan.step();steps++;}while(progress.status==='scanning');
assert.equal(steps,5);assert.equal(progress.scanned,1100);assert.equal(progress.offer.height,64);assert.equal(progress.offer.expectedHead,floor);assert.equal(progress.offer.nodes.length,66);
const anchors=new Map(scan.anchors().map(a=>[a.height,a]));let accepted=progress.offer,scannedAfterFirst=0;
while(accepted.height<tip.height){const next=Math.min(accepted.height+64,tip.height),start=anchors.get(next);assert.ok(start);const follow=await createOfficialOfferScan(archive,{afterHeight:accepted.height,afterHead:accepted.head,start});const result=await follow.step();assert.equal(result.status,'ready');assert.equal(result.offer.height,next);scannedAfterFirst+=result.scanned;accepted=result.offer;}
assert.equal(accepted.head,tip.head);assert.equal(scannedAfterFirst,1100-64);
await assert.rejects(createOfficialOfferScan(archive,{afterHeight:0,afterHead:floor,start:{...anchors.get(64),head:await hash('wrong')}}),/anchor changed/);
const wrong=await createOfficialOfferScan(archive,{afterHeight:0,afterHead:await hash('wrong')});await assert.rejects(async()=>{while(true){const p=await wrong.step();if(p.status==='ready')break;}},/floor conflicts/);
const cancelled=await createOfficialOfferScan(archive,{afterHeight:0,afterHead:floor});const abort=new AbortController();abort.abort();await assert.rejects(cancelled.step({signal:abort.signal}));
const pinnedTip=tip,concurrent=await createOfficialOfferScan(archive,{afterHeight:0,afterHead:floor});assert.equal((await concurrent.step()).status,'scanning');const newHead=await hash('head-1101'),newCid=await node({profile:'codi-channel-content/1',kind:'head',channel,genesisHash,height:1101,head:newHead,parent:pinnedTip.history,block:blob});rows.set(newCid,{cid:newCid,height:1101,head:newHead,block:{header:{parent:pinnedTip.head}},next:pinnedTip.history});tip={...pinnedTip,height:1101,head:newHead,history:newCid};let resumed;do{resumed=await concurrent.step();}while(resumed.status==='scanning');assert.equal(resumed.offer.height,64);assert.equal(resumed.scanned,1100);
console.log('PASS: 1,100-block resumable scan, indexed following batches, conflict and cancellation');
