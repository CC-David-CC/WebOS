import {hash} from '../network/crypto.mjs';
import {operationSetEmpty} from '../network/device-operation-set.mjs';
import {DeviceOperationTree} from '../network/device-operation-tree.mjs';
const raw=SubtleCrypto.prototype.digest;let count=0;SubtleCrypto.prototype.digest=function(...args){count++;return raw.apply(this,args);};
const nodes=new Map(),tree=new DeviceOperationTree({get:async cid=>nodes.get(cid),put:async(cid,wire)=>nodes.set(cid,wire)});let root=null;const start=performance.now();
for(let i=0;i<134;i++){const id=await hash('node-cache-profile-'+i);root=(await tree.insert(root,id)).link;}
console.log(JSON.stringify({operations:134,digests:count,elapsedMs:Math.round(performance.now()-start),root:await tree.root(root),nodes:nodes.size}));
