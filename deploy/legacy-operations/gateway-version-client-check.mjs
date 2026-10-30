/** Validate the compact version response without accepting malformed metadata. */
import assert from 'node:assert/strict';
import {UserFiles} from '../gateway_service/client.mjs';

const files = Object.create(UserFiles.prototype);
let reply = {bytes: 3, sha256: 'a'.repeat(64)};
files.request = async (operation, fields) => {
  assert.equal(operation, 'version');
  assert.deepEqual(fields, {path: 'note'});
  return reply;
};
assert.deepEqual(await files.version('note'), reply);
for (const bad of [null, {}, {bytes: -1, sha256: 'a'.repeat(64)},
  {bytes: 8388609, sha256: 'a'.repeat(64)}, {bytes: 1.5, sha256: 'a'.repeat(64)},
  {bytes: 3, sha256: 'A'.repeat(64)}, {bytes: 3, sha256: 'a'.repeat(64), data: 'hidden'}]) {
  reply = bad;
  await assert.rejects(() => files.version('note'));
}
console.log('Compact file-version response validation passed');
files.base='/gateway';files.check=()=>{};
const originalFetch=globalThis.fetch;
try {
  for (const [body,status,expected] of [
    ['{"version":"codi-file-capabilities/1","fileVersion":true}',200,true],
    ['{"version":"codi-file-capabilities/1","fileVersion":false}',200,false],
    ['{"version":"other","fileVersion":true}',200,false],
    ['',404,false],
  ]) {
    globalThis.fetch=async (path,options)=>{assert.equal(path,'/gateway/capabilities');assert.equal(options.cache,'no-store');return new Response(body,{status});};
    assert.equal(await files.supportsVersion(),expected);
  }
  globalThis.fetch=async()=>new Response('x'.repeat(1025));
  await assert.rejects(()=>files.supportsVersion(),/too large/);
  globalThis.fetch=async()=>new Response('not json');
  await assert.rejects(()=>files.supportsVersion(),/Invalid/);
  globalThis.fetch=async()=>new Response('',{status:503});
  await assert.rejects(()=>files.supportsVersion(),e=>e.status===503);
} finally {globalThis.fetch=originalFetch;}
console.log('Worker capability negotiation and legacy fallback passed');
