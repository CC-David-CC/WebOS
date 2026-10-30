/** Development-only replay of reconstructed blocks using the browser codec.
 * This is not a trusted server service or a publication authorization token.
 */
import {readDeviceChannelPolicy,initialDeviceChannelPosition,acceptDeviceChannelBlock} from '../../network/device-channel-state.mjs';
let input='';for await(const part of process.stdin)input+=part;
const value=JSON.parse(input);
async function replay(blocks){
 const policy=await readDeviceChannelPolicy(value.policy,{channel:value.channel,genesisHash:value.genesis});
 let at=await initialDeviceChannelPosition(policy);
 for(const row of blocks){at=await acceptDeviceChannelBlock(at,row.block);if(at.head!==row.head)throw Error('History locator differs from verified block');}
 if(at.head!==value.expectedHead||at.height!==value.expectedHeight)throw Error('Replay does not reach expected head');
 return {head:at.head,height:at.height,proofScope:at.proofScope};
}
const output={valid:await replay(value.blocks)};
async function rejects(blocks){try{await replay(blocks);return false;}catch{return true;}}
const corrupted=structuredClone(value.blocks);corrupted[0].block.header.count+=1;output.tamperedBlockRejected=await rejects(corrupted);
const unsigned=structuredClone(value.blocks);unsigned[0].block.commit=[];output.missingQuorumRejected=await rejects(unsigned);
const wrongHead=structuredClone(value.blocks);wrongHead[0].head=value.genesis;output.wrongLocatorRejected=await rejects(wrongHead);
if(value.blocks.length>1)output.reorderedRejected=await rejects([...value.blocks].reverse());
process.stdout.write(JSON.stringify(output));
