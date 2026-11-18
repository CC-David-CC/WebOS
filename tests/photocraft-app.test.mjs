import assert from 'node:assert/strict';
import test from 'node:test';
import {randomUUID} from 'node:crypto';
import {mount} from '../assembly/viewer/photocraft-app.mjs';
import {mountCraftAccount} from '../assembly/viewer/craft-account-app.mjs';
import {createDocumentOperations, createDocumentOperationCoordinator} from '../platform/runtime/active-system/assets/desktop/document-operations.mjs';

const owner = 'test-account';
const first = 'a'.repeat(64), next = 'b'.repeat(64), generation = 'c'.repeat(32);

for (const [app,name,extension,reviewWindowClose] of [
  ['photocraft','PhotoCraft','.pcraft',false],
  ['figcraft','FigCraft','.figcraft',true],
]) test(`${name} publishes bindings after native adoption and closes through its editor's contract`, async () => {
  const path = 'Pictures/Project' + extension;
  const original = globalThis.document, originalLocation = globalThis.location;
  const controller = new AbortController();
  try {
    const desktopWindow = Object.assign(new EventTarget(), {
      location:new URL('http://localhost:8080'),
      crypto:{randomUUID}
    });
    const element = () => Object.assign(new EventTarget(), {
      style:{}, children:[], removed:false,
      setAttribute() {},
      append(...nodes) { this.children.push(...nodes); },
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
          frame.contentWindow = {focus() {}, postMessage(packet) { traffic.push(packet); }};
        }
        return node;
      }
    };
    globalThis.document = fakeDocument;
    globalThis.location = desktopWindow.location;
    const w = {launchContext:{owner, path, sha256:first, storage:'account'}};
    let session = {public:{sub:owner}};
    const other = 'Pictures/Other' + extension;
    const activated = [], opened = [], closeIntents = [];
    const newWindow = {};
    let folder = '/Pictures';
    const host = {
      w, session:() => session, signal:controller.signal,
      documentOperations:createDocumentOperations({coordinator:createDocumentOperationCoordinator(),signal:controller.signal}),
      ui:{async prompt(label, options) {
        assert.equal(options.value,'Project' + extension);
        return 'Copy';
      }},
      desktop:{
        windows:[w],
        updateAccountFileBinding(...args) { bindings.push(args); },
        activateAccountFile(resource, app) { activated.push([resource,app]); return resource.path === path; },
        openAccountFile(app, resource) { opened.push([app,resource]); },
        async requestWindowClose(window) { closeIntents.push(window); },
        launch(id) { assert.equal(id,app); return newWindow; }
      },
      storage:{
        signedInSubject:() => owner,
        async pickAccountFile(options) {
          if (options.foldersOnly) return folder;
          assert.deepEqual(options.extensions,[extension]);
          return '/'+path;
        },
        async accountFileContext() {
          return {owner, valid:() => true, files:{
            check() {},
            async version(requestedPath) {
              assert.equal(requestedPath,other);
              return {sha256:first};
            },
            async read(requestedPath) {
              assert.equal(requestedPath,path);
              return {sha256:first, data:Uint8Array.of(3,4)};
            },
            async write(requestedPath, blob, previous) {
              writes.push([requestedPath,previous,new Uint8Array(await blob.arrayBuffer())]);
              return {sha256:next};
            }
          }};
        }
      }
    };
    let draftClears = 0;
    const recovery = {journal:() => ({async load() { return null; }, async clear() { draftClears++; }, close() {}})};
    const view = app === 'photocraft' ? mount(host) : mountCraftAccount(host, {
      app,name,extension,recovery,reviewWindowClose,
    });
    const receive = (kind, fields = {}) => desktopWindow.dispatchEvent(Object.assign(new Event('message'),{
      source:frame.contentWindow, origin:desktopWindow.location.origin,
      data:{type:app + ':account-' + kind,generation,...fields}
    }));
    const turn = () => new Promise(resolve => setImmediate(resolve));
    await turn();
    assert.match(frame.src,/profile=test-account/);
    assert.equal(new URL(frame.src).pathname,`/${app}/index.html`);
    assert.equal(view.element.children[0].children.some(node=>node.textContent==='Open from device'),!reviewWindowClose);
    frame.contentDocument = {URL:frame.src, querySelector:() => null};
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

    receive('dialog',{requestId:'1',operation:'open',path:null});
    await turn();
    assert.deepEqual(activated,[[{owner,path},app]]);
    assert.deepEqual(opened,[]);
    assert.equal(traffic.at(-1).requestId,'1');
    assert.equal(traffic.at(-1).outcome,'opened');

    receive('dialog',{requestId:'2',operation:'open',path:other});
    await turn();
    assert.deepEqual(opened,[[app,{owner,path:other,sha256:first}]]);
    assert.equal(traffic.at(-1).requestId,'2');

    receive('dialog',{requestId:'3',operation:'save',suggested:path});
    await turn();
    assert.equal(traffic.at(-1).outcome,'destination');
    assert.equal(traffic.at(-1).path,'Pictures/Copy' + extension);
    assert.equal(writes.length,1);

    folder = null;
    receive('dialog',{requestId:'4',operation:'save',suggested:path});
    await turn();
    assert.equal(traffic.at(-1).outcome,'cancelled');
    receive('dialog',{requestId:'3',operation:'open',path:other});
    await turn();
    assert.equal(opened.length,1);

    const settings = '{"width":35,"height":24}';
    receive('dialog',{requestId:'5',operation:'new',settings});
    await turn();
    assert.deepEqual(newWindow,{[app + 'NewSettings']:settings});
    assert.equal(traffic.at(-1).outcome,'opened');
    assert.deepEqual(bindings.at(-1),[w,{owner,path,sha256:next}]);

    receive('close-intent');
    assert.deepEqual(closeIntents,[w]);
    receive('project-state',{available:true,documentId:'7',revision:'2',dirty:false,capturable:true,
      unfinishedEdit:false,operationPending:false});
    assert.equal(await view.requestClose({scope:'session'}),true);
    assert.equal(view.lifecycle.snapshot().pending,false);
    assert.equal(frame.inert,false,'session inspection leaves the mounted editor available');
    const closing = view.requestClose({scope:'window'});
    await turn();
    if (reviewWindowClose) {
      const paused = traffic.at(-1);
      assert.equal(paused.operation,'pause');
      assert.equal(paused.revision,'2');
      receive('session-result',{...paused,type:app+':account-session-result',ok:true});
      assert.equal(await closing,true);
      assert.equal(frame.inert,true);
      const finalizing = view.lifecycle.commitClose();
      await turn();
      const finalized = traffic.at(-1);
      assert.equal(finalized.operation,'finalize');
      assert.equal(finalized.lease,paused.lease);
      receive('session-result',{...finalized,type:app+':account-session-result',ok:true});
      await finalizing;
      assert.equal(draftClears,1);
    } else {
      assert.equal(traffic.at(-1).interactive,true);
      receive('close-result',{requestId:traffic.at(-1).requestId,approved:false});
      assert.equal(await closing,false);
      assert.equal(frame.inert,false);
    }

    session = {public:{sub:'different-account'}};
    receive('save',{...identity,ticket:'2',bytes:Uint8Array.of(9).buffer});
    await turn();
    assert.equal(writes.length,1);

    frame.contentDocument = {URL:frame.src};
    frame.dispatchEvent(new Event('load'));
    assert.equal(frame.inert,true);
    assert.match(view.element.children[0].children[0].textContent,/reloaded/);
  } finally {
    controller.abort();
    globalThis.document = original;
    globalThis.location = originalLocation;
  }
});
