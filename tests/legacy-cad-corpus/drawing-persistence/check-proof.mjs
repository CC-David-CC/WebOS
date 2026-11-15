import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const read=path=>readFileSync(new URL(path,import.meta.url),'utf8'),r=JSON.parse(read('evidence-r1/receipt.json'));
assert.equal(r.status,0);assert.equal(r.signal,null);assert(r.sourceUnchanged);assert.deepEqual(r.before,r.after);for(const [path,hash]of Object.entries(r.before))assert.equal(createHash('sha256').update(readFileSync(path)).digest('hex'),hash,path);
const log=read('evidence-r1/tests.log');assert.match(log,/tests 77/);assert.match(log,/pass 77/);assert.match(log,/fail 0/);
assert.match(read('before-key-order/test.log'),/pass 6/);assert.match(read('before-key-order/test.log'),/fail 1/);
console.log('PASS: 77 actual host/retained settlement groups, first fixture failure preserved, source pins unchanged.');
