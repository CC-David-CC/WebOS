import {verifyHostedRoom,verifyHostedSnapshot,verifyHostedChunk,HostedRoomForkError} from './network/hosted-room-authority.mjs';
import {b64,unb64} from './network/crypto.mjs';

window.runSnapshotProofs=async()=>{
  const f=await (await fetch('/fixture.json')).json(),checks=window.snapshotProofChecks=[];
  const check=(name,ok)=>{if(!ok)throw Error(name);checks.push(name);};
  const refuse=async fn=>{try{await fn();}catch(error){return error;}throw Error('Expected snapshot refusal');};
  const options={now:f.now},room=await verifyHostedRoom(f.bootstrap,f.controllerKey,f.policy,options);
  const fresh=await verifyHostedSnapshot(f.fresh,room,options);
  check('fresh browser jumps to accepted100 using only a bounded recent chat window',fresh.stateSnapshotVerified&&fresh.next.index===100&&fresh.records.length<=32&&fresh.omittedHistoryCount>=68&&fresh.records.at(-1).text==='Saved note100');
  check('checkpoint explicitly distinguishes omitted history and chosen authority from a full audit',!fresh.fullHistoryVerified&&fresh.checkpointAuthority==='chosen-room-controller'&&fresh.historical&&fresh.records.every(r=>r.historical));
  const first=await verifyHostedChunk(f.first,room,options);
  const resumed=await verifyHostedSnapshot(f.anchored,room,{...options,after:first.next});
  check('returning browser verifies the controller attestation from its exact retained cursor',resumed.next.hash===fresh.next.hash&&resumed.next.index===100);
  const tail=await verifyHostedChunk(f.tail,room,{...options,after:fresh.next});
  check('snapshot plus only three later records reaches accepted103 without old-prefix replay',tail.complete&&tail.records.length===3&&tail.next.index===103&&tail.records[0].index===101);
  await refuse(()=>verifyHostedSnapshot(f.anchored,room,options));
  await refuse(()=>verifyHostedSnapshot(f.fresh,room,{...options,after:first.next}));
  check('a fresh or anchored checkpoint cannot silently replace the other request context',true);
  for(const [name,bundle] of Object.entries(f.bad)){
    await refuse(()=>verifyHostedSnapshot(bundle,room,{...options,after:first.next}));
    check('signed malformed snapshot rejected: '+name,true);
  }
  const bad=f.fresh.snapshot.split('.'),sig=unb64(bad[2]);sig[0]^=1;bad[2]=b64(sig);
  const invalid=await refuse(()=>verifyHostedSnapshot({...f.fresh,snapshot:bad.join('.')},room,options));
  check('invalid signature cannot create authenticated fork evidence',!(invalid instanceof HostedRoomForkError));
  const latestRoom=await verifyHostedRoom(f.latestBootstrap,f.controllerKey,f.policy,options);
  await refuse(()=>verifyHostedSnapshot(f.fresh,latestRoom,options));
  await refuse(()=>verifyHostedSnapshot(f.fresh,room,{now:f.now+301}));
  check('stale state behind a known head and expired live authority are refused',true);
  const fork=await refuse(()=>verifyHostedSnapshot(f.fork,room,{...options,after:fresh.next}));
  check('authenticated conflicting state at an already retained height has a distinct fork error',fork instanceof HostedRoomForkError);
  const emptyRoom=await verifyHostedRoom(f.emptyBootstrap,f.controllerKey,f.policy,options);
  const empty=await verifyHostedSnapshot(f.empty,emptyRoom,options);
  check('empty room checkpoint verifies its true genesis without inventing records',empty.fullHistoryVerified&&empty.next.index===0&&empty.records.length===0);
  const largeRoom=await verifyHostedRoom(f.largeBootstrap,f.controllerKey,f.policy,options);
  const large=await verifyHostedSnapshot(f.large,largeRoom,options);
  check('maximum-size Unicode notes keep the visible snapshot within a byte cap',large.next.index===16&&large.records.length>0&&large.records.length<16&&large.omittedHistoryCount>0&&new TextEncoder().encode(JSON.stringify(f.large)).length<131072);
  const longRoom=await verifyHostedRoom(f.long.bootstrap,f.controllerKey,f.policy,{now:f.long.now,floor:room.floor});
  const longState=await verifyHostedSnapshot(f.long.snapshot,longRoom,{now:f.long.now,after:first.next});
  check('simulated15day return uses fresh scoped authority to verify old accepted state without replaying its prefix',longState.next.index===103&&longState.omittedHistoryCount>0&&longState.records.every(r=>r.acceptedAt<f.long.now-14*86400));
  return {status:'PASS',checks,acceptedHead:tail.next.index,skippedPrefixRecords:fresh.omittedHistoryCount,
    independentlyVerifiedRecentRecords:fresh.records.length,tailRecords:tail.records.length,
    executedHistoricalLiveHandlers:0,fullPrefixReplayed:false};
};
window.snapshotProofReady=true;
