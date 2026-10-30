import assert from 'node:assert/strict';
import {hash,unb64} from '../network/crypto.mjs';
import {operationSetEmpty,operationSetLeaf,operationSetNode,applyOperationWitness} from '../network/device-operation-set.mjs';
import {DeviceOperationTree} from '../network/device-operation-tree.mjs';

// Independent deliberately unoptimized 256-level reference for each witness.
async function reference(root,id,witness){
 const zeros=await operationSetEmpty(),siblings=new Map(witness.siblings.map(s=>[s.level,s.hash])),bytes=unb64(id);let absent=zeros[0],inserted=await operationSetLeaf(id);
 for(let level=0;level<256;level++){
  const sibling=siblings.get(level)||zeros[level],right=(bytes[31-Math.floor(level/8)]>>(level%8))&1;
  [absent,inserted]=await Promise.all(right?[operationSetNode(sibling,absent),operationSetNode(sibling,inserted)]:[operationSetNode(absent,sibling),operationSetNode(inserted,sibling)]);
 }
 assert.equal(absent,root);return inserted;
}
const nodes=new Map(),tree=new DeviceOperationTree({get:async cid=>nodes.get(cid),put:async(cid,wire)=>nodes.set(cid,wire)});let link=null,root=(await operationSetEmpty())[256],last;
for(let index=0;index<24;index++){
 const id=await hash('cached-tree-fixture-'+index),witness=await tree.witness(link,id),expected=await reference(root,id,witness);
 assert.equal(await applyOperationWitness(root,id,witness),expected);last={root,id,witness,expected};
 const inserted=await tree.insert(link,id);assert.equal(inserted.root,expected);link=inserted.link;root=expected;
 await assert.rejects(()=>applyOperationWitness(root,id,witness));
}
const original=SubtleCrypto.prototype.digest;let hashes=0;SubtleCrypto.prototype.digest=function(...args){hashes++;return original.apply(this,args);};
await tree.root(link);hashes=0;assert.equal(await tree.root(link),root);assert.equal(hashes,0,'repeated immutable promotion should use its computed hash');
hashes=0;assert.equal(await applyOperationWitness(last.root,last.id,last.witness),last.expected);assert.equal(hashes,0,'identical verified witness should reuse its computed result');
await assert.rejects(()=>applyOperationWitness(last.root,last.id,{siblings:[...last.witness.siblings,{level:256,hash:root}]}));
const aborted=new AbortController();aborted.abort();await assert.rejects(()=>tree.root(link,{signal:aborted.signal}));
const altered={...link,hash:await hash('forged-tree-link')};await assert.rejects(()=>tree.inspect(altered));
const invalid=new DeviceOperationTree({get:async cid=>nodes.get(cid)+' ',put:async()=>{}});await assert.rejects(()=>invalid.inspect(link));
const left=await hash('memo-node-left'),right=await hash('memo-node-right');hashes=0;
const same=await Promise.all([operationSetNode(left,right),operationSetNode(left,right)]);assert.equal(same[0],same[1]);assert.equal(hashes,1,'concurrent identical nodes should share one digest');
const uniqueLeft=await hash('failing-memo-node-left');let failOnce=true;
SubtleCrypto.prototype.digest=function(...args){if(failOnce){failOnce=false;return Promise.reject(Error('simulated digest failure'));}return original.apply(this,args);};
await assert.rejects(()=>operationSetNode(uniqueLeft,right));assert.equal(await operationSetNode(uniqueLeft,right),await hash(JSON.stringify(['codi-operation-set/1','node',uniqueLeft,right])),'failed digest must be retried');
SubtleCrypto.prototype.digest=original;
console.log(JSON.stringify({status:'PASS',operations:24,checks:['optimized witnesses equal independent full 256-level calculation','replay and forged links rejected','cached promotion uses no new digest','corrupt node and cancellation rejected','identical concurrent node digests shared','failed digest retried']}));
