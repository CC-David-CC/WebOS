import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex'),receipt=JSON.parse(fs.readFileSync(new URL('./preparation/receipt.json',import.meta.url)));
assert.equal(receipt.status,'PREPARED_NOT_RUN');assert.equal(receipt.browserExecuted,false);assert.equal(receipt.nativeDepthEditQualified,false);assert.equal(receipt.componentOnly,true);for(const [file,hash]of Object.entries(receipt.sources))assert.equal(sha(fs.readFileSync(new URL(file,import.meta.url))),hash,file);const log=fs.readFileSync(new URL('./preparation/tests.log',import.meta.url),'utf8');for(const expected of ['ℹ tests 34','ℹ pass 34','ℹ fail 0'])assert(log.includes(expected));console.log(JSON.stringify({status:'PASS',scope:'source/preparation and metadata/recorded-source controls only; signed browser NOT RUN',nodeGroups:34,sourceFiles:Object.keys(receipt.sources).length},null,2));
