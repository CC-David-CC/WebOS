import assert from 'node:assert/strict';
import test from 'node:test';
import {createCraftStorage} from '../assembly/viewer/craft-account-storage.mjs';
import {createDocumentOperations, createDocumentOperationCoordinator} from '../platform/runtime/active-system/assets/desktop/document-operations.mjs';

const ID = 'a'.repeat(32), BASE = 'b'.repeat(64), WRITTEN = 'c'.repeat(64);
const FILENAME = 'Pictures/Original.pcraft', NEW_NAME = 'Pictures/Alternate.pcraft';
const blank = {generation:ID,documentId:'1',revision:'1',path:null};
const project = path => ({...blank,path});
const save = (path=FILENAME, ticket='1') => ({...project(path),ticket,bytes:Uint8Array.of(1,2,3).buffer});
const acknowledged = (request, response) => ({...request,adopted:response.outcome==='written'});

function fixture(overrides = {}, editor = {name:'PhotoCraft', extension:'.pcraft'}) {
  const controller = new AbortController(), writes = [];
  const valid = () => !controller.signal.aborted;
  const coordinator = createDocumentOperationCoordinator();
  const operations = createDocumentOperations({coordinator,signal:controller.signal,valid});
  const files = {
    check() {},
    async read() { return {sha256:BASE,data:Uint8Array.of(4,5,6)}; },
    async write(path, blob, expected) {
      writes.push([path,Array.from(new Uint8Array(await blob.arrayBuffer())),expected]);
      return {sha256:WRITTEN};
    },
    ...overrides
  };
  return {store:createCraftStorage({...editor,files,operations,valid}),writes,controller,coordinator};
}

test('The shared account storage enforces the native format of the selected editor', async () => {
  let reads=0;
  const {store}=fixture({async read(){reads++;return {sha256:BASE,data:Uint8Array.of(4,5,6)};}},
    {name:'FigCraft',extension:'.figcraft'});
  await assert.rejects(store.open({path:FILENAME,sha256:BASE},()=>assert.fail()), /\.figcraft project path/);
  assert.equal(reads,0);
  const figResource={path:'Pictures/Design.figcraft',sha256:BASE};
  assert.deepEqual(await store.open(figResource,project),figResource);
  assert.equal(reads,1);
});

test('Open requires the observed Storage revision and an exact native adoption', async () => {
  const {store} = fixture();
  const resource = {path:FILENAME,sha256:BASE};
  await assert.rejects(store.open(resource, () => project(NEW_NAME)), /did not adopt/);
  assert.equal(store.inspect().binding, null);
  await assert.rejects(store.open({...resource,sha256:WRITTEN}, () => assert.fail()), /changed/);
  const opened = await store.open(resource,(path, bytes) => {
    assert.deepEqual(Array.from(bytes),[4,5,6]);
    return project(path);
  });
  assert.deepEqual(opened,resource);
  await assert.rejects(store.open(resource,()=>assert.fail()), /unopened/);
});

test('A recovered project can overwrite only its unchanged account base', async () => {
  for (const mode of ['unchanged','advanced','unavailable','already-open']) {
    let reads = 0;
    const {store,writes} = fixture({async version() {
      reads++;
      if (mode === 'unavailable') throw Error('Storage unreachable');
      return {sha256:mode === 'unchanged' ? BASE : WRITTEN};
    }});
    const draft = {path:FILENAME,revision:BASE,bytes:new Blob(['native snapshot'])};
    const same = mode === 'unchanged';
    const adopted = await store.restore(draft,(path,bytes) => {
      assert.equal(path,same ? FILENAME : null);
      assert.equal(new TextDecoder().decode(bytes),'native snapshot');
      return project(path);
    },{asCopy:mode === 'already-open'});
    assert.equal(reads,mode !== 'already-open' ? 1 : 0);
    assert.deepEqual(adopted,same ? {path:FILENAME,sha256:BASE} : null);
    await store.save(save(same ? FILENAME : NEW_NAME),acknowledged);
    assert.equal(writes[0][2],same ? BASE : null);
  }
});

test('Save replaces the bound revision, while Save As creates and awaits native settlement', async () => {
  const {store,writes} = fixture();
  await store.open({path:FILENAME,sha256:BASE},project);
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  let reached;
  const waiting = new Promise(resolve => { reached = resolve; });
  const mutation = save();
  const saving = store.save(mutation,async (request,response) => {
    assert.equal(response.outcome,'written');
    reached();
    await gate;
    return acknowledged(request,response);
  });
  new Uint8Array(mutation.bytes).fill(0);
  await waiting;
  assert.equal(store.inspect().pending,'adopting');
  assert.deepEqual(store.inspect().binding,{path:FILENAME,sha256:BASE});
  release();
  assert.deepEqual(await saving,{path:FILENAME,sha256:WRITTEN});
  await store.save(save(NEW_NAME,'2'),acknowledged);
  assert.deepEqual(writes,[[FILENAME,[1,2,3],BASE],[NEW_NAME,[1,2,3],null]]);
  await assert.rejects(store.save(save(NEW_NAME,'2'),acknowledged), /did not identify/);
});

test('Account revocation or a lost receipt cannot publish a new binding', async () => {
  for (const mode of ['wrong-generation','wrong-identity','account-ended','server-uncertain']) {
    const write = mode==='server-uncertain' ? {async write() { throw Object.assign(Error('lost response'),{outcome:'unknown'}); }} : {};
    const {store,controller} = fixture(write);
    store.attachBlank(blank);
    const outcome = await store.save(save(),(request,response) => {
      if (mode==='server-uncertain') assert.fail('Native must keep waiting after an uncertain write.');
      if (mode==='account-ended') controller.abort();
      const receipt = acknowledged(request,response);
      if (mode==='wrong-generation') receipt.generation = 'f'.repeat(32);
      if (mode==='wrong-identity') receipt.documentId = '18';
      return receipt;
    }).catch(error => error);
    assert.equal(outcome.outcome,'unknown',mode);
    assert.equal(store.inspect().binding,null,mode);
    assert.equal(store.inspect().pending,'unknown',mode);
  }
});

test('Known write conflicts leave the last binding and release the native ticket', async () => {
  let fail = true;
  const {store} = fixture({async write() {
    if (fail) throw Object.assign(Error('conflict'),{status:409});
    return {sha256:WRITTEN};
  }});
  await store.open({path:FILENAME,sha256:BASE},project);
  await assert.rejects(store.save(save(NEW_NAME),(request,response) => {
    assert.equal(response.outcome,'failed');
    return acknowledged(request,response);
  }), /conflict/);
  assert.deepEqual(store.inspect().binding,{path:FILENAME,sha256:BASE});
  assert.equal(store.inspect().pending,null);
  fail = false;
  await store.save(save(NEW_NAME,'2'),acknowledged);
  assert.equal(store.inspect().binding.path,NEW_NAME);
});

test('Writes contend with existing Files operations and reject path aliases without dispatch', async () => {
  const {store,writes,coordinator} = fixture();
  const other = createDocumentOperations({coordinator});
  store.attachBlank(blank);
  const peer = other.begin('move');
  assert.equal(peer.claimDocumentTree('mirror:/Pictures'),true);
  await assert.rejects(store.save(save(),acknowledged), /busy/);
  peer.finish();
  await assert.rejects(store.save(save('Pictures/../Escape.pcraft','2'),acknowledged), /relative/);
  assert.deepEqual(writes,[]);
  assert.equal(store.inspect().pending,null);
});
