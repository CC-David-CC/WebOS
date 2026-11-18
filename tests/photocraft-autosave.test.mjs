import assert from 'node:assert/strict';
import test from 'node:test';
import {trackPhotoAutosave} from '../assembly/viewer/photocraft-autosave.mjs';

test('PhotoCraft automatic writes require opt-in, a named binding and the latest eligible native revision', async t => {
  const path = 'Pictures/Layered.pcraft', generation = 'a'.repeat(32), documentId = '9';
  const captures = [], states = [];
  const inspected = {identity:{generation,documentId},binding:null,pending:null};
  let time = 0, timer, outcome = {};
  const adapter = trackPhotoAutosave({
    valid:() => true,
    storage:{inspect:() => inspected},
    native:{async captureAutosave(target) { captures.push(target); return target; }},
    write:async () => outcome,
    onState:state => states.push(state),
  },{
    now:() => time, random:() => 0,
    setTimer:(fn,ms) => (timer = {fn,due:time+ms}),
    clearTimer:key => { if (timer === key) timer = null; },
  });
  t.after(() => adapter.dispose());
  const state = (revision, autosaveEligible = true) => adapter.receive({
    available:true,generation,documentId,revision,dirty:true,autosaveEligible
  });
  async function reach(target) {
    while (timer && timer.due <= target) {
      const {due,fn} = timer;
      time = due;
      timer = null;
      fn();
      for (let turn=0; turn<12; turn++) await Promise.resolve();
    }
    time = target;
  }

  state('1');
  adapter.enabled(true);
  assert.equal(timer,undefined,'an untitled draft cannot write automatically');
  adapter.enabled(false);
  inspected.binding = {path,sha256:'b'.repeat(64)};
  adapter.update();
  assert.equal(timer,undefined,'named files require opt-in');
  adapter.enabled(true);
  state('2',false);
  assert.equal(timer,null,'an unfinished native edit stays local');

  state('3');
  await reach(9_000);
  state('4');
  state('3');
  await reach(18_999);
  assert.equal(captures.length,0);
  await reach(19_000);
  assert.deepEqual(captures,[{path,documentId,revision:'4'}]);

  outcome = {error:Object.assign(Error('Transfer allowance reached; try later'),{status:429,retryAfterMs:75_000})};
  state('5');
  await reach(78_999);
  assert.equal(captures.length,1);
  await reach(79_000);
  assert.equal(captures.length,2);
  assert.equal(states.at(-1).state,'retrying');
  assert.equal(timer.due,154_000);

  outcome = {error:Object.assign(Error('Write result is unknown'),{outcome:'unknown'})};
  await reach(154_000);
  state('6');
  await reach(1_000_000);
  assert.equal(captures.length,3);
  assert.equal(states.at(-1).state,'paused');
});
