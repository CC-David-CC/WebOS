import assert from 'node:assert/strict';
import test from 'node:test';
import {randomUUID} from 'node:crypto';
import {connectPhotoNative} from '../assembly/viewer/photocraft-native.mjs';

const url = new URL('http://localhost:8080/photocraft/index.html?host=webos-account');
const generation = 'a'.repeat(32);
const name = 'Pictures/Project.pcraft';

function fixture(testContext) {
  const desktop = Object.assign(new EventTarget(), {location:url, crypto:{randomUUID}});
  const sent = [], saves = [];
  const frame = Object.assign(new EventTarget(), {
    ownerDocument:{defaultView:desktop},
    contentDocument:{URL:url.href},
    contentWindow:{postMessage(packet, origin, transfer) {
      assert.equal(origin,url.origin);
      sent.push(structuredClone(packet,{transfer}));
    }}
  });
  const controller = new AbortController();
  const native = connectPhotoNative(frame,{url,signal:controller.signal,onSave:packet => saves.push(packet)});
  testContext.after(() => {
    void native.ready.catch(() => {});
    controller.abort();
  });
  function receive(kind, fields = {}, override = {}) {
    desktop.dispatchEvent(Object.assign(new Event('message'), {
      source:frame.contentWindow, origin:url.origin, ...override,
      data:{type:'photocraft:account-' + kind, generation, ...fields}
    }));
  }
  return {frame, controller, receive, native, sent, saves};
}

test('PhotoCraft accepts readiness from the exact frame, document URL and origin', async t => {
  const {frame, native, receive, sent, saves} = fixture(t);
  receive('ready', {}, {source:{}});
  receive('ready', {}, {origin:'http://localhost:8081'});
  frame.contentDocument = {URL:url.href + '#different'};
  receive('ready');
  receive('save',{ticket:'1'});
  await assert.rejects(native.start(), /has not started/);
  assert.deepEqual(saves,[]);
  frame.contentDocument = {URL:url.href};
  receive('ready');
  await native.ready;

  const file = Uint8Array.of(0,1,2,3);
  const opening = native.start(name,file.subarray(1,3));
  const outgoing = sent[0];
  assert.equal(outgoing.path,name);
  assert.deepEqual(Array.from(new Uint8Array(outgoing.bytes)),[1,2]);
  assert.deepEqual(Array.from(file),[0,1,2,3]);
  receive('started',{requestId:'other',ok:false});
  receive('started',{requestId:outgoing.requestId,generation:'b'.repeat(32),ok:false});
  receive('started',{requestId:outgoing.requestId,ok:true,path:name,documentId:'9',revision:'0'});
  assert.equal((await opening).documentId,'9');
});

test('A save result waits for the exact native settlement and ignores other tickets', async t => {
  const {native, receive, sent, saves} = fixture(t);
  receive('ready');
  await native.ready;
  const write = {path:name,documentId:'9',revision:'3',ticket:'12'};
  receive('save',write);
  assert.equal(saves.length,1);
  const settlement = native.acknowledge(write,{outcome:'written'});
  assert.deepEqual(sent[0],{type:'photocraft:account-save-result',generation,...write,outcome:'written'});
  receive('save-settled',{...write,ticket:'13',adopted:false});
  receive('save-settled',{...write,revision:'4',adopted:false});
  receive('save-settled',{...write,adopted:true});
  assert.equal((await settlement).adopted,true);
});

test('Frame replacement and account abort reject pending native requests', async t => {
  for (const scenario of ['reload','abort']) {
    const {frame, controller, native, receive, sent, saves} = fixture(t);
    receive('ready');
    await native.ready;
    const opening = native.start();
    if (scenario === 'reload') {
      frame.contentDocument = {URL:url.href};
      frame.dispatchEvent(new Event('load'));
    } else {
      controller.abort();
    }
    receive('started',{requestId:sent[0].requestId,ok:true,documentId:'9'});
    receive('save',{ticket:'1'});
    await assert.rejects(opening,scenario === 'reload' ? /reloaded/ : {name:'AbortError'});
    assert.deepEqual(saves,[]);
  }
});

test('PhotoCraft close requires approval for the matching native window and request', async t => {
  const {native, receive, sent, controller} = fixture(t);
  receive('ready');
  await native.ready;
  const cancelled = native.requestClose(true);
  const {requestId, interactive} = sent[0];
  assert.equal(interactive,true);
  receive('close-result',{requestId:'other',approved:true});
  receive('close-result',{requestId,generation:'b'.repeat(32),approved:true});
  receive('close-result',{requestId,approved:false});
  assert.equal(await cancelled,false);

  const session = native.requestClose(false);
  assert.equal(sent[1].interactive,false);
  const fault = assert.rejects(session, /Finish the active operation/);
  receive('close-result',{requestId:sent[1].requestId,message:'Finish the active operation'});
  await fault;

  const closing = native.requestClose(true);
  const rejected = assert.rejects(closing,{name:'AbortError'});
  controller.abort();
  await rejected;
});
