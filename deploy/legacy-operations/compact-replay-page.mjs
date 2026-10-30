import {OriginReplayGate} from '/network/replay.mjs';
import {sessionBudget,NETWORK_LIMITS} from '/network/resource-budget.mjs';
import {verifyMeshDescriptor,verifyMeshMember} from '/network/mesh-membership.mjs';
import {unb64,b64} from '/network/crypto.mjs';

const get=async path=>{const response=await fetch(path,{cache:'no-store'});if(!response.ok)throw Error('Fixture HTTP '+response.status);return response.json();};
const reject=async(fn,pattern)=>{try{await fn();}catch(error){if(pattern&&!pattern.test(error.message))throw error;return error.message;}throw Error('Expected refusal');};
window.runCompactReplay=async count=>{
  const checks=[],samples=[],owner={},budget=sessionBudget(owner),config=await get('/fixture/config');
  const gate=new OriginReplayGate(owner,config.identity,{compact:true});
  const room=await verifyMeshDescriptor(config.descriptor,config.controller,config.identity);
  let completed=0,bytes=0,phase='bulk',firstSid;
  const start=performance.now();
  const accept=async record=>{
    const admission=await budget.runCrypto(()=>verifyMeshMember(record.grant,record.identity,room,config.identity));
    gate.admit(admission);
    const received=await gate.receive(record.event,record.identity);
    if(received.event.author_session_id!==record.identity.sid)throw Error('Wrong verified author');
    completed++;
  };
  try{
    for(let offset=0;offset<count;offset+=64){
      const records=await get('/fixture/batch?start='+offset+'&count='+Math.min(64,count-offset));
      for(let i=0;i<records.length;i+=8){const settled=await Promise.allSettled(records.slice(i,i+8).map(accept));const failed=settled.find(v=>v.status==='rejected');if(failed)throw failed.reason;}
      if(!firstSid)firstSid=records[0].identity.sid;
      bytes+=new TextEncoder().encode(JSON.stringify(records)).length;
      if(offset===0||completed%1024===0||completed===count){
        const sample={authors:completed,elapsedMs:performance.now()-start,accounting:budget.snapshot(),replay:gate.snapshot()};samples.push(sample);window.compactProgress=sample;
      }
    }
    checks.push('distinct certified authors with real controller grants and origin signatures verified');
    if(gate.snapshot().streams!==count||gate.snapshot().retainedIdentityProofs!==0)throw Error('Compact record count or retained proofs');
    if(budget.snapshot().metadataBytes>=count*4096)throw Error('Unexpected per-author metadata accounting');
    checks.push('compact records retain author bindings and replay floors without certificate strings');
    phase='attacks';
    const control=await get('/fixture/controls');
    if(control.identity.sid!==firstSid)throw Error('Control signer changed');
    await reject(()=>gate.receive(control.events[0],control.identity),/Duplicate/);
    checks.push('freshly signed reused sequence cannot replay an already accepted author event');
    const admission=await verifyMeshMember(control.grant,control.identity,room,config.identity);
    gate.admit(admission);await reject(()=>gate.receive(control.events[0],control.identity),/Duplicate/);
    checks.push('repeated admission preserves the original sequence floor');
    await reject(()=>gate.receive(control.events[1]),/identity|proof/i);
    checks.push('compact receive requires the current supplied identity proof');
    const changed=structuredClone(control.identity);changed.sub+='different';
    await reject(()=>gate.receive(control.events[1],changed),/binding/i);
    await reject(()=>gate.admit({...admission,identity:changed}),/binding/i);
    checks.push('identity substitution is refused on both receive and repeated admission');
    const certificate=structuredClone(control.identity),parts=certificate.certificate.split('.'),signature=unb64(parts[2]);signature[0]^=1;parts[2]=b64(signature);certificate.certificate=parts.join('.');
    await reject(()=>gate.receive(control.events[1],certificate),/signature/i);
    checks.push('a forged identity certificate cannot use an admitted author binding');
    const token=control.events[3].split('.'),sig=unb64(token[2]);sig[0]^=1;token[2]=b64(sig);
    await reject(()=>gate.receive(token.join('.'),control.identity),/signature/i);
    checks.push('invalid origin signature cannot poison a later sequence');
    const gap=await gate.receive(control.events[2],control.identity);
    if(gap.gap?.from!==2||gap.gap?.to!==2)throw Error('Lost replay gap');
    const filled=await gate.receiveHistorical(control.events[1],()=>true,control.identity);
    if(!filled.historical)throw Error('Missing historical classification');
    await gate.receive(control.events[3],control.identity);
    checks.push('live gaps and once-only bounded historical fill preserve existing replay semantics');
    const queueHold=budget.wire(NETWORK_LIMITS.queuedBytes-NETWORK_LIMITS.controlBytes-control.events[4].length);
    try{
      await reject(()=>gate.receive(control.events[4],control.identity),/appBytes/);
      const controlLease=budget.wire(64,true);controlLease();
    }finally{queueHold();}
    checks.push('pending identity proof shares the bounded application queue and preserves control reserve');
    const hold=budget.metadata(budget.limits().metadataBytes-budget.snapshot().metadataBytes),before=gate.snapshot().streams;
    try{
      const extra=await verifyMeshMember(control.extra.grant,control.extra.identity,room,config.identity);
      await reject(()=>gate.admit(extra),/metadataBytes/);
      if(gate.snapshot().streams!==before||budget.snapshot().replayStreams!==before)throw Error('Refusal allocated or evicted a floor');
      gate.admit(admission);await gate.receive(control.events[4],control.identity);
    }finally{hold();}
    checks.push('metadata refusal releases its tentative slot and keeps existing authors usable');
    const extended=structuredClone(control.extra.identity);extended.key.unusedProof=extended.certificate.repeat(4);
    const extra=await verifyMeshMember(control.extra.grant,extended,room,config.identity),beforeExtended=budget.snapshot().metadataBytes;
    gate.admit(extra);
    if(budget.snapshot().metadataBytes-beforeExtended>=4096)throw Error('Unneeded JWK properties retained');
    checks.push('retained key binding drops untrusted extra JWK properties and their proof strings');
    const attempts=await Promise.allSettled([gate.receive(control.events[5],control.identity),gate.receive(control.events[5],control.identity)]);
    if(attempts.filter(v=>v.status==='fulfilled').length!==1)throw Error('Concurrent duplicate committed twice');
    checks.push('concurrent valid duplicates commit once');
    const closing=gate.receive(control.events[6],control.identity);gate.closeRoom(room.roomId);await reject(()=>closing,/closed|changed|expired/i);
    await reject(()=>gate.admit(admission),/reset|renewed/i);
    if(gate.snapshot().streams!==count+1||budget.snapshot().replayStreams!==count+1)throw Error('Closed room evicted replay tombstones');
    checks.push('room close during real verification rejects delivery and retains every tombstone');
    gate.close();
    const used=budget.snapshot();if(Object.entries(used).some(([k,v])=>k!=='closed'&&v!==0))throw Error('Resource leak '+JSON.stringify(used));
    checks.push('all compact floors, wire and crypto leases release after close');
    return {status:'PASS',checks,participants:count,completedAuthors:completed,elapsedMs:performance.now()-start,applicationFixtureBytes:bytes,samples,cleanupBudget:used,fixture:await get('/fixture/stats')};
  }catch(error){return {status:'FAIL',phase,error:error.stack,checks,participants:count,completedAuthors:completed,samples,accountingAtFailure:budget.snapshot()};}
  finally{gate.close();window.compactCleanup=budget.snapshot();}
};
window.compactReady=true;
