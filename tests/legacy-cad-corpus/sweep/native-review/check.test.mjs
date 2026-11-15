// Mutations of copies of genuine recorded data test this offline reviewer.
// No Worker replies, native execution or browser model is manufactured.
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {review} from './check.mjs';
const raw=JSON.parse(fs.readFileSync(new URL('raw-receipt-r3.json',import.meta.url))),pins=JSON.parse(fs.readFileSync(new URL('runtime-pins.json',import.meta.url)));
test('genuine recorded35row corpus has21sweep successes13refusals17realqueries',()=>{const r=review(raw,pins);assert.equal(r.successes,21);assert.equal(r.typedRefusals,13);assert.equal(r.actualNativeQueries,17);assert(r.maxVolumeError<1e-12);assert(r.maxBoundsError<1e-6);});
test('producer expected values are never used as independent truth',()=>{const changed=structuredClone(raw);for(const row of changed.rows){row.expected={volume:-123,bounds:null,error:'bogus'};for(const p of row.points||[])p.expected=-999;}assert.deepEqual(review(changed,pins),review(raw,pins));});
test('altered native measurements, rawradius/majorbranch/actualpoint and preservation flags refuse',()=>{for(const change of[r=>r.rows[0].result.nativeVolume+=1,r=>r.rows[0].profile[17]=3,r=>r.rows[0].points[0].actual=1,r=>r.rows[0].callerPayloadPreserved=false,r=>r.rows.find(x=>x.label==='major-circle-not-shortest').path[17]=9,r=>r.finalOwnedNames=1]){const changed=structuredClone(raw);change(changed);assert.throws(()=>review(changed,pins));}});
