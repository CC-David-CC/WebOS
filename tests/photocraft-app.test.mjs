import assert from 'node:assert/strict';
import test from 'node:test';
import {randomUUID} from 'node:crypto';
import {mount} from '../assembly/viewer/photocraft-app.mjs';
import {createDocumentOperations, createDocumentOperationCoordinator} from '../platform/runtime/active-system/assets/desktop/document-operations.mjs';

const owner = 'test-account';
const path = 'Pictures/Project.pcraft';
const first = 'a'.repeat(64), next = 'b'.repeat(64), generation = 'c'.repeat(32);

test('The classic API2 view publishes account bindings only after the native frame adopts them', async () => {
  const original = globalThis.document;
  const controller = new AbortController();
  try {
    const desktopWindow = Object.assign(new EventTarget(), {
      location:new URL('http://localhost:8080'),
      crypto:{randomUUID}
    });
    const element = () => Object.assign(new EventTarget(), {
      style:{}, children:[], removed:false,
      setAttribute() {},
      append(node) { this.children.push(node); },
      remove() { this.removed = true; }
    });
    const traffic = [], writes = [], bindings = [];
    let frame;
    const fakeDocument = {
      baseURI:'http://localhost:8080/',
      defaultView:desktopWindow,
      createElement(tag) {
        const node = element();
        if (tag === 'iframe') {
          frame = node;
          frame.ownerDocument = fakeDocument;
          frame.contentWindow = {postMessage(packet) { traffic.push(packet); }};
        }
        return node;
      }
    };
    globalThis.document = fakeDocument;
    const w = {launchContext:{owner, path, sha256:first, storage:'account'}};
    let session = {public:{sub:owner}};
    const view = mount({
      w, session:() => session, signal:controller.signal,
      documentOperations:createDocumentOperations({coordinator:createDocumentOperationCoordinator(),signal:controller.signal}),
      desktop:{windows:[w], updateAccountFileBinding(...args) { bindings.push(args); }},
      storage:{signedInSubject:() => owner, async accountFileContext() {
        return {owner, valid:() => true, files:{
          check() {},
          async read(requestedPath) {
            assert.equal(requestedPath,path);
            return {sha256:first, data:Uint8Array.of(3,4)};
          },
          async write(requestedPath, blob, previous) {
            writes.push([requestedPath,previous,new Uint8Array(await blob.arrayBuffer())]);
            return {sha256:next};
          }
        }};
      }}
    });
    const receive = (kind, fields = {}) => desktopWindow.dispatchEvent(Object.assign(new Event('message'),{
      source:frame.contentWindow, origin:desktopWindow.location.origin,
      data:{type:'photocraft:account-' + kind,generation,...fields}
    }));
    const turn = () => new Promise(resolve => setImmediate(resolve));
    await turn();
    assert.match(frame.src,/profile=test-account/);
    frame.contentDocument = {URL:frame.src};
    receive('ready');
    await turn();
    assert.equal(frame.inert,true);
    assert.equal(traffic[0].path,path);
    assert.deepEqual(new Uint8Array(traffic[0].bytes),Uint8Array.of(3,4));
    assert.deepEqual(bindings,[]);

    receive('started',{requestId:traffic[0].requestId,ok:true,path,documentId:'7',revision:'1'});
    await view.ready;
    assert.equal(frame.inert,false);
    assert.deepEqual(bindings,[[w,{owner,path,sha256:first}]]);

    const identity = {path,ticket:'1',documentId:'7',revision:'2'};
    receive('save',{...identity,bytes:Uint8Array.of(8).buffer});
    await turn();
    assert.deepEqual(writes,[[path,first,Uint8Array.of(8)]]);
    assert.equal(traffic[1].outcome,'written');
    assert.equal(bindings.length,1);
    receive('save-settled',{...identity,adopted:true});
    await turn();
    assert.deepEqual(bindings[1],[w,{owner,path,sha256:next}]);

    session = {public:{sub:'different-account'}};
    receive('save',{...identity,ticket:'2',bytes:Uint8Array.of(9).buffer});
    await turn();
    assert.equal(writes.length,1);

    frame.contentDocument = {URL:frame.src};
    frame.dispatchEvent(new Event('load'));
    assert.equal(frame.inert,true);
    assert.match(view.element.children[0].textContent,/reloaded/);
  } finally {
    controller.abort();
    globalThis.document = original;
  }
});
