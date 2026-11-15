/** Check source and packaged desktop policy; no physical-RAM claim. */
import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
const root='.build/releases/network-512-profile26-r1',graph=JSON.parse(fs.readFileSync(root+'/assets/desktop/network-release.json','utf8'));
for(const path of ['networking.js',root+'/'+graph.coreDirectory+'/networking.js']){
 const source=fs.readFileSync(path,'utf8'),context=vm.createContext({});vm.runInContext(source+'\nglobalThis.fixtureNetwork=desktopNetwork;',context);const n=context.fixtureNetwork;
 assert.equal(n.memoryPolicy().metadataMiB,512);assert.equal(n.memoryPolicy().accountedBytes,0);assert.equal(n.configureMemoryBudgetMiB(256).metadataMiB,256);assert.throws(()=>n.configureMemoryBudgetMiB(1025));
}
console.log(JSON.stringify({status:'PASS',checks:8,scope:'source and packaged desktop accounting defaults; no RAM preallocation'}));
