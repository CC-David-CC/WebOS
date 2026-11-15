import {DeviceOperationTree as BaselineTree,DeviceOperationTreeVerifier as BaselineVerifier} from '../network/device-operation-tree.mjs';
import {DeviceOperationTree as CandidateTree,DeviceOperationTreeVerifier as CandidateVerifier} from '../.build/candidates/index-parallel/network/device-operation-tree.mjs';
import {hash} from '../network/crypto.mjs';
const wires=new Map(),write=new BaselineTree({get:async cid=>wires.get(cid),put:async(cid,wire)=>wires.set(cid,wire)});
let root=null;for(let i=0;i<32;i++)root=(await write.insert(root,await hash('parallel-verifier-fixture-'+i))).link;
const expectedRoot=await write.root(root);
async function run(Tree,Verifier,{bad=false,delay=8,abort=false}={}){
 let active=0,maxActive=0,calls=0,failed=false;const signal=new AbortController();
 const tree=new Tree({get:async cid=>{active++;maxActive=Math.max(active,maxActive);calls++;try{if(abort&&calls===4)signal.abort(Error('fixture cancellation'));await new Promise(resolve=>setTimeout(resolve,delay));if(signal.signal.aborted)throw signal.signal.reason;const value=wires.get(cid);return bad&&cid!==root.cid?value+' ':value;}finally{active--; }},put:async()=>{throw Error('read only');}});
 const verifier=new Verifier({tree,root,expectedRoot});const started=performance.now();try{let status;do{status=await verifier.step({limit:16,signal:signal.signal});}while(!status.complete);return {elapsedMs:performance.now()-started,calls,maxActive,status};}catch(e){failed=true;return {elapsedMs:performance.now()-started,calls,maxActive,failed,message:e.message,status:verifier.snapshot()};}finally{verifier.close();}
}
const baseline=await run(BaselineTree,BaselineVerifier),candidate=await run(CandidateTree,CandidateVerifier),corrupt=await run(CandidateTree,CandidateVerifier,{bad:true}),cancelled=await run(CandidateTree,CandidateVerifier,{abort:true});
const checks={sameCompleteIndex:baseline.status.complete&&candidate.status.complete&&baseline.status.checked===candidate.status.checked&&candidate.status.checked===63,boundedConcurrentReads:candidate.maxActive>1&&candidate.maxActive<=4,corruptionRejected:corrupt.failed&&!corrupt.status.complete,cancellationRejected:cancelled.failed&&!cancelled.status.complete,latencyImproved:candidate.elapsedMs<baseline.elapsedMs};
console.log(JSON.stringify({status:Object.values(checks).every(Boolean)?'PASS':'FAIL',scope:'Node synthetic 32-operation index with a locally generated expected root, artificial 8ms read delay; no real RTC or browser storage. Candidate only.',checks,baseline,candidate,corrupt,cancelled},null,2));if(!Object.values(checks).every(Boolean))process.exitCode=1;
