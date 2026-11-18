import assert from 'node:assert/strict';
import test from 'node:test';
import {createCraftSession} from '../assembly/viewer/craft-account-session.mjs';

const generation = 'c'.repeat(32), documentId = '17', resource = 'Pictures/Layered.pcraft';
const initial = {available:true,generation,documentId,revision:'1',
  dirty:true,unfinishedEdit:false,operationPending:false,capturable:true};

function fixture(choose) {
  const nativeCalls = [], closing = [], frame = {inert:false};
  const inspected = {identity:{generation,documentId},binding:{path:resource,sha256:'1'.repeat(64)},pending:null};
  let authorised = true, cleared = 0, writes = 0, resumed = 0, session;
  session = createCraftSession({
    app:'photocraft', appName:'PhotoCraft',
    native:{async session(...args) { nativeCalls.push(args); },
      async captureSessionSave(target) { nativeCalls.push(['save',target]); return target; }},
    storage:{inspect:() => inspected},
    drafts:{async pause() { return () => { resumed++; }; },async clear() { cleared++; }},
    autosave:{closing(value) { closing.push(value); }},
    signal:new AbortController().signal, valid:() => authorised, loaded:() => true, frame,
    documentName:() => 'PhotoCraft project', choose, choosePath:async () => resource,
    async write() { writes++; session.receive({...initial,revision:'2',dirty:false}); return {}; }, onError:assert.fail,
  });
  session.receive(initial);
  return {session,frame,nativeCalls,closing,inspected,revoke:()=>{authorised=false;},
    get cleared(){return cleared;},get writes(){return writes;},get resumed(){return resumed;}};
}

test('Cancel and a change while deciding both preserve the live PhotoCraft window', async () => {
  const cancelled = fixture(async () => 'cancel');
  assert.equal(await cancelled.session.approve(),false);
  assert.deepEqual(cancelled.closing,[true,false]);
  await assert.rejects(cancelled.session.quiesce(),/Review the current/);
  assert.deepEqual(cancelled.nativeCalls,[]);
  assert.equal(cancelled.cleared,0);

  const changed = fixture(async () => {
    changed.session.receive({...initial,revision:'2'});
    return 'discard';
  });
  await assert.rejects(changed.session.approve(),/changed after you reviewed/);
  await assert.rejects(changed.session.quiesce(),/Review the current/);
  assert.equal(changed.cleared,0);
});

test('Discard is committed only under the same native pause after account revocation', async () => {
  const f = fixture(async () => 'discard');
  assert.equal(await f.session.approve(),true);
  const snapshot = f.session.snapshot();
  const lease = await f.session.quiesce();
  assert.equal(f.frame.inert,true);
  assert.equal(f.cleared,0);
  assert.equal(f.session.snapshot(),snapshot);
  const [op, token, reviewed] = f.nativeCalls[0];
  assert.equal(op,'pause');
  assert.deepEqual(reviewed,initial);
  f.revoke();
  await f.session.commitClose();
  lease.release();
  assert.deepEqual(f.nativeCalls[1],['finalize',token]);
  assert.equal(f.nativeCalls.length,2);
  assert.equal(f.cleared,1);
});

test('A refused sign-out releases the native pause and retains the draft', async () => {
  const f = fixture(async () => 'discard');
  assert.equal(await f.session.approve(),true);
  const lease = await f.session.quiesce();
  lease.release();
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(f.nativeCalls[1],['release',f.nativeCalls[0][1]]);
  assert.equal(f.frame.inert,false);
  assert.equal(f.resumed,1);
  assert.equal(f.cleared,0);
});

test('Save at sign-out uses the reviewed native revision and waits for acknowledgement', async () => {
  const f = fixture(async () => 'save');
  f.session.receive({...initial,unfinishedEdit:true});
  assert.equal(await f.session.approve(),true);
  assert.deepEqual(f.nativeCalls[0],['save',{documentId,revision:'1',path:resource}]);
  assert.equal(f.writes,1);
  assert.equal(f.session.snapshot().dirty,false);
  assert.equal(f.cleared,0);
});

test('A window discard decision cannot authorize discarding during sign-out', async () => {
  const f = fixture(async ({scope}) => {
    assert.equal(scope,'window');
    return 'discard';
  });
  assert.equal(await f.session.approve('window'),true);
  await assert.rejects(f.session.quiesce(),/before signing out/);
  await f.session.quiesce('window');
  await f.session.commitClose();
  assert.equal(f.cleared,1);
});
