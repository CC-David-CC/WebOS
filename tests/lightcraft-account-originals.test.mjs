import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import test from 'node:test';
import {createLightCraftOriginalStore,lightCraftAccountScope} from '../assembly/viewer/lightcraft-account-originals.mjs';

const missing = () => Object.assign(Error('Missing account file'),{status:404});
const conflict = () => Object.assign(Error('Account path conflict'),{status:409});
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');

test('the same account has a stable cache scope and a different account or origin has a separate scope', async () => {
  const scope = await lightCraftAccountScope('https://webos.test','user-a');
  assert.match(scope,/^[0-9a-f]{64}$/);
  assert.equal(await lightCraftAccountScope('https://webos.test','user-a'),scope);
  assert.notEqual(await lightCraftAccountScope('https://webos.test','user-b'),scope);
  assert.notEqual(await lightCraftAccountScope('https://another.test','user-a'),scope);
});

function fixture() {
  const rows = new Map();
  let writes = 0, directory = false;
  const lookup = path => {
    if (!rows.has(path)) throw missing();
    return rows.get(path);
  };
  const files = {
    check() {},
    async mkdir(path) {
      assert.equal(path,'Pictures/LightCraft Originals');
      if (directory) throw conflict();
      directory = true;
    },
    async list(path) {
      assert.equal(path,'Pictures/LightCraft Originals');
      if (!directory) throw missing();
    },
    async version(path) {
      const data = lookup(path);
      return {sha256:sha256(data)};
    },
    async write(path, source, expected) {
      assert.equal(expected,null);
      if (rows.has(path)) throw conflict();
      writes++;
      const data = new Uint8Array(await source.arrayBuffer());
      rows.set(path,data);
      return {sha256:sha256(data)};
    },
    async read(path) {
      const data = lookup(path);
      return {data,sha256:sha256(data)};
    },
  };
  return {files, rows, writes:()=>writes};
}

test('equal originals share a single conditional create and can be reopened by digest', async () => {
  const {files, writes} = fixture();
  const input = Uint8Array.of(1,4,8,2);
  const digest = sha256(input);
  const store = createLightCraftOriginalStore({files,valid:()=>true});
  assert.deepEqual(await Promise.all([store.store(input),store.store(input)]),[digest,digest]);
  assert.equal(writes(),1);
  const reopened = createLightCraftOriginalStore({files,valid:()=>true});
  assert.deepEqual(await reopened.read(digest),input);
  assert.equal(await reopened.store(input),digest);
  assert.equal(writes(),1);
});

test('an occupied digest path must contain the same bytes, and a closed view loses access', async () => {
  const {files, rows, writes} = fixture();
  const input = Uint8Array.of(2,4,6);
  const digest = sha256(input);
  rows.set('Pictures/LightCraft Originals/'+digest+'.original',Uint8Array.of(9));
  let valid = true;
  const store = createLightCraftOriginalStore({files,valid:()=>valid});
  await assert.rejects(store.store(input),/different file/i);
  await assert.rejects(store.read(digest),/could not verify/i);
  await assert.rejects(store.read('../Documents/private.jpg'),/invalid.*digest/i);
  valid = false;
  await assert.rejects(store.store(input),{name:'AbortError'});
  assert.equal(writes(),0);
});
