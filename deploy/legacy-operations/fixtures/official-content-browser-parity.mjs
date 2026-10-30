import {readDeviceContentNode} from '../../network/device-content-node.mjs';
import {hash} from '../../network/crypto.mjs';
let data='';for await(const part of process.stdin)data+=part;
const rows=JSON.parse(data),results=[];
for(const row of rows){try{await readDeviceContentNode(await hash(row.wire),row.wire,{channel:row.channel,genesisHash:row.genesis});results.push(true);}catch{results.push(false);}}
process.stdout.write(JSON.stringify(results));
