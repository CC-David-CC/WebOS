// Offline verification of this lane's own normally saved native outputs only.
import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
import {savedIntent} from './oracle.mjs';
const dir=process.argv[2];assert(dir);const receipt=JSON.parse(fs.readFileSync(path.join(dir,'receipt.json')));assert.equal(receipt.status,'PASS');
for(const [name,fillet]of [['boolean-chain',3],['boolean-chain-reedited',4]]){const raw=fs.readFileSync(path.join(dir,name+'.jsketcher.json')),sha=crypto.createHash('sha256').update(raw).digest('hex'),row=receipt.rows.find(r=>r.label===name+' normal native Save and server sync');assert(row);assert.equal(sha,row.sha256);assert.equal(raw.length,row.bytes);console.log(JSON.stringify({name,sha256:sha,...savedIntent(JSON.parse(raw),receipt.binding,{fillet,chamfer:1})}));}
