import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const setup = readFileSync(new URL('../assembly/viewer/scoped-editor-storage.js', import.meta.url), 'utf8');
class Storage {
  getItem(key) { return this[key] ?? null; }
  setItem(key,value) { this[key] = String(value); }
  removeItem(key) { delete this[key]; }
}
function open({owner,id='1',guest=false,local,session,temporary}) {
  const window = {
    name:JSON.stringify({owner,guest,document:id}), parent:{}, frameElement:{webosGuestStorage:temporary},
    localStorage:local, sessionStorage:session, indexedDB:{cmp(){},open:name=>name},
  };
  vm.runInNewContext(setup,{window,document:{documentElement:{dataset:{editor:'sewing-pattern-drafter'}}}});
  return window;
}

test('account vault is shared within the account and autosaves belong to individual windows', () => {
  const backing={local:new Storage(),session:new Storage()};
  const a=open({...backing,owner:'account-a'}), b=open({...backing,owner:'account-b'});
  const second=open({...backing,owner:'account-a',id:'2'});
  a.localStorage.setItem('library','sample'); a.localStorage.setItem('pdraft:autosave','private draft');
  assert.equal(second.localStorage.getItem('library'),'sample');
  assert.equal(second.localStorage.getItem('pdraft:autosave'),null);
  assert.equal(a.localStorage.length,2); assert.equal(b.localStorage.length,0);
  assert.notEqual(a.indexedDB.open('pdraft-autosave'),second.indexedDB.open('pdraft-autosave'));
  assert.equal(a.indexedDB.open('pdraft-library'),second.indexedDB.open('pdraft-library'));
  assert.notEqual(a.indexedDB.open('pdraft-library'),b.indexedDB.open('pdraft-library'));
  b.localStorage.clear(); assert.equal(a.localStorage.getItem('library'),'sample');
});
test('a guest can reopen a vault in the same session and leaves both browser stores empty', () => {
  const backing={local:new Storage(),session:new Storage()}, temporary={local:new Map(),session:new Map()};
  const options={...backing,owner:'guest-a',guest:true,temporary};
  const a=open(options);a.localStorage.setItem('novel','guest manuscript');
  assert.equal(open({...options,id:'2'}).localStorage.getItem('novel'),'guest manuscript');
  assert.equal(a.sessionStorage.getItem('novel'),null);assert.equal(a.indexedDB,undefined);
  assert.deepEqual(Object.keys(backing.local),[]);assert.deepEqual(Object.keys(backing.session),[]);
  assert.equal(open({...options,temporary:{local:new Map(),session:new Map()}}).localStorage.length,0);
  assert.equal(open({...backing,owner:'account-a'}).localStorage.getItem('novel'),null);
});
