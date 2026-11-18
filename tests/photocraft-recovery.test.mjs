import assert from 'node:assert/strict';
import test from 'node:test';
import {trackPhotoDraft} from '../assembly/viewer/photocraft-recovery.mjs';

for (const independentRevision of [false,true]) test(
  independentRevision ? 'A newer child-tab checkpoint wins even when the parent revision stays fixed'
    : 'A superseded PhotoCraft capture never replaces the newer browser draft', async t => {
  const generation = 'a'.repeat(32), documentId = '3';
  const binding = {path:'Pictures/Edit.pcraft',sha256:'b'.repeat(64)};
  const inspected = {identity:{generation,documentId},binding,pending:'unknown'};
  const written = [];
  let release, started, saved;
  const start = new Promise(resolve => { started = resolve; });
  const checkpoint = new Promise(resolve => { saved = resolve; });
  const stalled = new Promise(resolve => { release = resolve; });
  const tracker = trackPhotoDraft({
    valid:() => true,
    onError:assert.fail,
    storage:{inspect:() => inspected},
    journal:{async write(value) { written.push(value); saved(); }},
    native:{async captureRecovery({revision}) {
      if (revision === '1') {
        started();
        await stalled;
      }
      return new Blob(['snapshot for '+revision]);
    }},
  });
  t.after(() => tracker.stop());
  const packet = revision => ({available:true,generation,documentId,dirty:true,capturable:true,
    ...(independentRevision ? {revision:'7',recoveryRevision:revision} : {revision})});
  tracker.receive(packet('1'));
  await start;
  tracker.receive(packet('2'));
  tracker.receive(packet('1'));
  release();
  await checkpoint;
  assert.equal(written.length,1);
  assert.equal(written[0].nativeRevision,'2');
  assert.equal(written[0].revision,binding.sha256);
  assert.equal(await written[0].bytes.text(),'snapshot for 2');
  });
