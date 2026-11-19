import assert from 'node:assert/strict';
import test from 'node:test';
import {randomUUID} from 'node:crypto';
import {connectCraftAccount} from '../assembly/viewer/craft-account-native.mjs';

const url = new URL('http://localhost:8080/photocraft/index.html?host=webos-account');
const generation = 'a'.repeat(32);
const name = 'Pictures/Project.pcraft';

function fixture(testContext, app = 'photocraft', name = 'PhotoCraft', originalStore, options = {}) {
  const editorURL = new URL('/'+app+'/index.html?host=webos-account',url);
  const desktop = Object.assign(new EventTarget(), {location:url, crypto:{randomUUID}});
  const sent = [], saves = [], localFiles = [];
  const frame = Object.assign(new EventTarget(), {
    ownerDocument:{defaultView:desktop},
    contentDocument:{URL:editorURL.href},
    contentWindow:{postMessage(packet, origin, transfer) {
      assert.equal(origin,url.origin);
      sent.push(structuredClone(packet,{transfer}));
    }}
  });
  const controller = new AbortController();
  const native = connectCraftAccount(frame,{app,name,url:editorURL,signal:controller.signal,originalStore,...options,onSave:packet => saves.push(packet),onLocalFile:file=>localFiles.push(file)});
  testContext.after(() => {
    void native.ready.catch(() => {});
    controller.abort();
  });
  function receive(kind, fields = {}, override = {}) {
    desktop.dispatchEvent(Object.assign(new Event('message'), {
      source:frame.contentWindow, origin:url.origin, ...override,
      data:{type:app+':account-' + kind, generation, ...fields}
    }));
  }
  return {frame, controller, receive, native, sent, saves, localFiles};
}

test('Detached originals use only the active LightCraft frame and can be read during project open', async t => {
  const calls = [];
  const stored = Uint8Array.of(1,2,3);
  const digest = 'f'.repeat(64);
  const originalStore = {
    async read(value) {
      calls.push(['read', value]);
      return stored;
    },
    async store(bytes) {
      calls.push(['store', new Uint8Array(bytes)]);
      return digest;
    },
  };
  const {native,receive,sent,controller} = fixture(t,'lightcraft','LightCraft',originalStore);
  receive('ready');
  await native.ready;
  receive('original-read',{requestId:'1',digest});
  assert.deepEqual(calls,[]);
  const opening = native.start('Pictures/Work.lightcraft',stored);
  receive('original-read',{requestId:'1',digest,generation:'b'.repeat(32)});
  receive('original-read',{requestId:'1',digest},{source:{}});
  assert.deepEqual(calls,[]);
  receive('original-read',{requestId:'1',digest});
  receive('original-read',{requestId:'1',digest});
  receive('original-store',{requestId:'2',bytes:stored.slice().buffer});
  await Promise.resolve();
  assert.deepEqual(calls,[['read',digest]]);
  const read = sent.find(packet => packet.requestId === '1');
  assert.deepEqual(read,{type:'lightcraft:account-original-result',generation,operation:'original-read',requestId:'1',ok:true,bytes:stored.buffer});
  assert.equal(sent.find(packet => packet.requestId === '2').ok,false);

  receive('started',{requestId:sent[0].requestId,ok:true,path:'Pictures/Work.lightcraft',documentId:'10',revision:'0'});
  await opening;
  receive('original-store',{requestId:'3',bytes:stored.slice().buffer});
  await Promise.resolve();
  assert.deepEqual(sent.at(-1),{type:'lightcraft:account-original-result',generation,operation:'original-store',requestId:'3',ok:true,digest});
  assert.deepEqual(calls.at(-1),['store',stored]);
  receive('original-read',{requestId:'4',digest});
  controller.abort();
  await Promise.resolve();
  assert.equal(sent.some(packet => packet.requestId === '4'),false);
});

test('The shared native connection accepts only its selected Craft app namespace', async t => {
  const {native,receive,sent}=fixture(t,'vectorcraft','VectorCraft');
  receive('ready',{type:'photocraft:account-ready'});
  assert.throws(()=>native.assertLive(),/VectorCraft has not started/);
  receive('ready');
  await native.ready;
  native.answerDialog('12',{outcome:'cancelled'});
  assert.equal(sent[0].type,'vectorcraft:account-dialog-result');
  assert.equal(sent[0].generation,generation);
});

test('An exact FigCraft startup failure rejects readiness immediately', async t => {
  const {frame,native,receive} = fixture(t,'figcraft','FigCraft');
  const message = 'FigCraft renderer unavailable.';
  const expectedURL = frame.contentDocument.URL;
  receive('failed',{message},{source:{}});
  receive('failed',{message},{origin:'http://localhost:8081'});
  receive('failed',{message,type:'vectorcraft:account-failed'});
  receive('failed',{message,generation:'bad'});
  frame.contentDocument = {URL:expectedURL + '#other'};
  receive('failed',{message});
  assert.throws(() => native.assertLive(), /has not started/);

  frame.contentDocument = {URL:expectedURL};
  const unavailable = assert.rejects(native.ready, {message});
  receive('failed',{message});
  await unavailable;
  receive('ready');
  assert.throws(() => native.assertLive(), {message});
});

test('A dropped local file and its unbound import start require the exact native frame', async t => {
  const {native,receive,sent,localFiles} = fixture(t);
  receive('ready');
  await native.ready;
  const file = new File([Uint8Array.of(9,8)],'Local.png');
  receive('local-file',{file},{source:{}});
  assert.deepEqual(localFiles,[]);
  receive('local-file',{file});
  assert.deepEqual(localFiles,[file]);

  const opening = native.importFile(file.name,await file.arrayBuffer());
  const request = sent[0];
  assert.equal(request.importName,'Local.png');
  assert.equal(request.path,null);
  assert.equal(request.recover,false);
  assert.deepEqual(new Uint8Array(request.bytes),Uint8Array.of(9,8));
  receive('started',{requestId:'wrong',ok:false});
  receive('started',{requestId:request.requestId,ok:true,path:null,documentId:'19',revision:'1'});
  assert.equal((await opening).documentId,'19');
});

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

test('PhotoCraft document operations settle only for the exact generation, request and document', async t => {
  const {native,receive,sent} = fixture(t);
  receive('ready');
  await native.ready;
  const result=native.operation({documentId:'7',path:name,command:'document.inspect',args:{}});
  const {requestId}=sent[0];
  assert.equal(sent[0].path,name);
  assert.equal(sent[0].args,'{}');
  receive('operation-result',{generation:'b'.repeat(32),requestId,documentId:'7',message:'wrong frame'});
  receive('operation-result',{requestId,documentId:'17',message:'wrong document'});
  receive('operation-result',{requestId:'wrong',documentId:'7',message:'wrong request'});
  receive('operation-result',{requestId,documentId:'7',result:'{"revision":"4"}'});
  assert.deepEqual(await result,{revision:'4'});
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

test('A PhotoCraft recovery snapshot must match the exact doc and native revision', async t => {
  const {native, receive, sent} = fixture(t);
  receive('ready');
  await native.ready;
  const target = {documentId:'9', revision:'3'};
  const result = native.captureRecovery(target);
  const {requestId} = sent[0];
  receive('recovery-captured',{...target,requestId,revision:'4',bytes:Uint8Array.of(9).buffer});
  receive('recovery-captured',{...target,requestId,documentId:'8',bytes:Uint8Array.of(9).buffer});
  receive('recovery-captured',{...target,requestId,bytes:Uint8Array.of(5,6).buffer});
  assert.deepEqual(new Uint8Array(await (await result).arrayBuffer()),Uint8Array.of(5,6));
});

test('A native AutoSave can return bytes only for the requested document, revision and path', async t => {
  const {native, receive, sent} = fixture(t);
  receive('ready');
  await native.ready;
  const target = {documentId:'9',revision:'4',path:'Pictures/Edit.pcraft'};
  const attempt = native.captureAutosave(target);
  const {requestId} = sent[0];
  receive('autosave-result',{...target,requestId,path:'Pictures/Other.pcraft',outcome:'captured',bytes:Uint8Array.of(1).buffer});
  receive('autosave-result',{...target,requestId,outcome:'busy'});
  assert.equal(await attempt,null);

  const capture = native.captureAutosave(target);
  receive('autosave-result',{...target,requestId:sent[1].requestId,outcome:'captured',ticket:'15',bytes:Uint8Array.of(7).buffer});
  assert.deepEqual(new Uint8Array((await capture).bytes),Uint8Array.of(7));
});

test('PhotoCraft session pause requires the same request, operation and lease', async t => {
  const {native, receive, sent} = fixture(t);
  receive('ready');
  await native.ready;
  const lease = randomUUID();
  const reviewed = {documentId:'9',revision:'4',dirty:true,unfinishedEdit:true};
  const holding = native.session('pause',lease,reviewed);
  assert.deepEqual({...reviewed},Object.fromEntries(Object.keys(reviewed).map(key=>[key,sent[0][key]])));
  const {requestId} = sent[0];
  receive('session-result',{requestId,lease:randomUUID(),operation:'pause',ok:true});
  receive('session-result',{requestId,lease,operation:'finalize',ok:true});
  const rejected = assert.rejects(holding,/PhotoCraft changed/);
  receive('session-result',{requestId,lease,operation:'pause',ok:false,message:'PhotoCraft changed'});
  await rejected;
});

test('A saved model may use a longer open budget while blank opens and write acknowledgments retain their deadlines', async t => {
  t.mock.timers.enable({apis:['setTimeout']});
  const policy = {accountOpenTimeoutMs:180_000};
  const source = Uint8Array.of(1,2,3);
  const {native,receive,sent}=fixture(t,'solidcraft','SolidCraft',null,policy);
  receive('ready');
  await native.ready;
  const opening=native.start('Documents/Fillet.sc',source);
  t.mock.timers.tick(60_000);
  native.assertLive();
  const requestId=sent.at(-1).requestId;
  receive('started',{requestId,ok:true,documentId:'1',revision:'0',path:'Documents/Fillet.sc'});
  assert.equal((await opening).path,'Documents/Fillet.sc');

  const save={ticket:'1',documentId:'1',revision:'1',path:'Documents/Fillet.sc'};
  const writeTimeout=assert.rejects(native.acknowledge(save,{outcome:'written'}),/did not confirm/);
  t.mock.timers.tick(30_001);
  await writeTimeout;

  const blank=fixture(t,'solidcraft','SolidCraft',null,policy);
  blank.receive('ready');
  await blank.native.ready;
  const blankTimeout=assert.rejects(blank.native.start(),/did not confirm/);
  t.mock.timers.tick(30_001);
  await blankTimeout;
});

test('An outstanding model reconstruction can be cancelled and reports an authenticated renderer failure immediately',async t=>{
  for (const abort of [true,false]) {
    const {native,receive,controller}=fixture(t,'solidcraft','SolidCraft',null,{accountOpenTimeoutMs:180_000});
    receive('ready');
    await native.ready;
    const rejected=assert.rejects(native.start('Documents/Fillet.sc',Uint8Array.of(1)),abort?/closed/:/renderer failed/);
    receive('failed',{message:'foreign error',generation:'b'.repeat(32)});
    receive('failed',{message:'foreign error'},{source:{}});
    native.assertLive();
    if (abort) controller.abort();
    else receive('failed',{message:'renderer failed'});
    await rejected;
    assert.throws(()=>native.assertLive(),abort?/closed/:/renderer failed/);
  }
});

test('Saved opens expire at their configured deadline and a late startup cannot revive the document', async t => {
  t.mock.timers.enable({apis:['setTimeout']});
  for (const [app, name, options, limit] of [
    ['solidcraft', 'SolidCraft', {accountOpenTimeoutMs:180_000}, 180_000],
    ['photocraft', 'PhotoCraft', {}, 30_000],
  ]) {
    const {native,receive,sent}=fixture(t,app,name,null,options);
    receive('ready');
    await native.ready;
    const path = 'Documents/Project';
    const expired = assert.rejects(native.start(path,Uint8Array.of(1)), /did not confirm/);
    const requestId = sent.at(-1).requestId;
    t.mock.timers.tick(limit-1);
    native.assertLive();
    t.mock.timers.tick(1);
    await expired;
    receive('started',{requestId,ok:true,documentId:'1',revision:'0',path});
    assert.throws(()=>native.assertLive(),/did not confirm/);
  }
});
