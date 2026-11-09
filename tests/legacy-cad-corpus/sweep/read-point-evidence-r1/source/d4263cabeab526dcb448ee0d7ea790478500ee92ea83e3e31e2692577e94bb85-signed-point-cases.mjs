import assert from 'node:assert/strict';
import {workflow} from './signed-cases.mjs';
import {query,refusal} from './signed-point-observation.mjs';

// Wrap the frozen genuine public workflow; never replace its authoring/results.
export async function pointWorkflow(h,a,record,receipt,kind){
 let baselineRequest=null;
 const wrapped={...a,
  async persist(b,label,...rest){const file=await a.persist(b,label,...rest),saved=receipt.saved.at(-1);assert.equal(saved.label,label);const proof=await query(h,a,b,saved,record,label);receipt.pointQueries.push(proof);
   if(kind==='straight-disk'&&label==='straight-disk-baseline'){
    baselineRequest=structuredClone(proof.request);
    await refusal(h,b,{...proof.request,bodyId:'unavailable-current-body'},{code:'UNSUPPORTED_TARGET'},record,'Unknown current body refuses without state/resource change');
    await refusal(h,b,{...proof.request,featureId:b.featureId+1000},{code:'UNSUPPORTED_TARGET'},record,'Wrong actual producer pair refuses without state/resource change');
    assert(typeof b.initialProfileBuild==='string'&&b.initialProfileBuild!==b.engineRevision);
    await refusal(h,b,{...proof.request,engineRevision:b.initialProfileBuild},{code:'ENGINE_REVISION_MISMATCH'},record,'Old registered native build refuses without state/resource change');
    // Current public bridge's exact dense-vector refusal, not engine failure.
    await refusal(h,b,{...proof.request,points:[[0,0]]},{name:'Error',code:null,message:'Expected bounded dense point data.'},record,'Malformed public point vector refuses before native replay');
    const retry=await query(h,a,b,saved,record,label+'-healthy-retry');receipt.pointQueries.push(retry);
   }
   return file;
  },
  async profileEdit(b){const result=await a.profileEdit(b);if(kind==='straight-disk'){assert(baselineRequest);await refusal(h,b,baselineRequest,{name:'AbortError'},record,'Old genuine revision refuses after actual accepted source edit');}return result;}
 };
 return workflow(h,wrapped,record,kind);
}
