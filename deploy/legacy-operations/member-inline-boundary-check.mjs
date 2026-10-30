import assert from 'node:assert/strict';
import {PeerLink} from '../network/peer.mjs';
import {provisionalInlineFits} from '../network/device-replica-exchange.mjs';
import {encodeDeviceReplicaInline,decodeDeviceReplicaInline,encodeDeviceReplicaValue,decodeDeviceReplicaValue} from '../network/device-replica-values.mjs';
import {hash} from '../network/crypto.mjs';
const pins={channel:await hash('inline-channel'),genesisHash:await hash('inline-genesis'),purpose:'response:node'};
const req={...pins,request_id:'0'.repeat(32)};
const peer={connectionId:'0'.repeat(43),session:{public:{sid:'0'.repeat(43)}},remoteIdentity:{sid:'0'.repeat(43)},packetCost:PeerLink.prototype.packetCost};
const frame=ref=>JSON.stringify({version:'codi-mesh/1',mode:'device-channel-member/1',type:'rpc',body:{op:'result',channel:req.channel,genesisHash:req.genesisHash,request_id:req.request_id,value:ref},credit:'0'.repeat(32)});
const cost=ref=>peer.packetCost('application',frame(ref));
const results=[];
for(const [name,text] of [['ascii','A'],['escaped','"\\\n'],['unicode','♞🌍']]){
 let previous=true, transitions=0, tested=0, largestFit=null, smallestOver=null;
 for(let size=1;size<=2600;size+=7){const value={wire:text.repeat(size)};const ref=await encodeDeviceReplicaInline(value,pins);if(!ref)break;const fits=provisionalInlineFits(peer,'device-channel-member/1',req,ref),estimate=cost(ref);assert.equal(fits,estimate<=4096);if(!fits&&previous)transitions++;assert(!(fits&&!previous),'a larger value returned to the inline range');previous=fits;tested++;if(fits)largestFit={size,estimate};else if(!smallestOver)smallestOver={size,estimate};}
 assert.equal(transitions,1);assert(largestFit&&smallestOver);const value={wire:text.repeat(largestFit.size)},ref=await encodeDeviceReplicaInline(value,pins);assert.equal((await decodeDeviceReplicaInline(ref,pins)).wire,value.wire);const chunked=await encodeDeviceReplicaValue(value,{...pins,chunkBytes:1024});assert.equal((await decodeDeviceReplicaValue({root:chunked.root,bytes:chunked.bytes},cid=>chunked.nodes.get(cid),pins)).wire,value.wire);results.push({name,tested,largestFit,smallestOver,chunkNodes:chunked.nodes.size,inlineFrames:1});
}
console.log(JSON.stringify({status:'PASS',scope:'Actual PeerLink signed frame estimate and value codecs in Node; no transport, quota ledger, or legacy peer.',results},null,2));
