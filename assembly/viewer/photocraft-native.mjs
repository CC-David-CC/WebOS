const prefix = 'photocraft:account-';
const generationPattern = /^[0-9a-f]{32}$/;
const saveFields = ['ticket', 'documentId', 'revision', 'path'];

/** One native PhotoCraft instance inside a same-origin classic Desktop window. */
export function connectPhotoNative(frame, {url, signal, onSave, onDialog, onLocalFile, onCloseIntent, onProjectState, onUnavailable}) {
  const desktop = frame.ownerDocument.defaultView;
  if (url.origin !== desktop.location.origin) throw Error('PhotoCraft requires the desktop origin.');

  let nativeDocument, generation, closed;
  const waiting = new Map();
  const abort = () => dispose(new DOMException('PhotoCraft view closed.', 'AbortError'));

  function dispose(error = new Error('PhotoCraft native view closed.')) {
    if (closed) return;
    closed = error;
    desktop.removeEventListener('message', receive);
    frame.removeEventListener('load', verifyDocument);
    signal?.removeEventListener('abort', abort);
    for (const entry of waiting.values()) entry.reject(error);
  }

  function verifyDocument() {
    if (nativeDocument && frame.contentDocument !== nativeDocument) {
      unavailable('PhotoCraft reloaded. Reopen the account project to continue.');
    }
  }

  function unavailable(message) {
    if (closed) return;
    dispose(Error(message));
    onUnavailable?.(message);
  }

  function check() {
    verifyDocument();
    if (closed) throw closed;
    if (!generation) throw Error('PhotoCraft has not started.');
  }

  function expect(kind, matches, milliseconds, fatal) {
    if (waiting.has(kind)) throw Error('PhotoCraft is already processing this request.');
    return new Promise((resolve, reject) => {
      function finish(callback, value) {
        clearTimeout(timer);
        waiting.delete(kind);
        callback(value);
      }
      const timer = milliseconds === null ? null : setTimeout(() => {
        const reason = 'PhotoCraft did not confirm the native request.';
        if (fatal) unavailable(reason);
        else finish(reject, Error(reason));
      }, milliseconds);
      waiting.set(kind, {
        matches,
        resolve: value => finish(resolve, value),
        reject: error => finish(reject, error)
      });
    });
  }

  function receive(event) {
    if (closed || event.source !== frame.contentWindow || event.origin !== url.origin) return;
    const data = event.data;
    if (!data || typeof data.type !== 'string' || !data.type.startsWith(prefix)) return;
    verifyDocument();
    if (closed) return;
    const kind = data.type.slice(prefix.length);
    if (kind === 'ready' && !nativeDocument) {
      const doc = frame.contentDocument;
      if (!doc || doc.URL !== url.href || typeof data.generation !== 'string' || !generationPattern.test(data.generation)) return;
      nativeDocument = doc;
      generation = data.generation;
    }
    if (!generation || generation !== data.generation) return;
    const entry = waiting.get(kind);
    if (entry?.matches(data)) {
      if (kind === 'save-settled' && data.projectState) {
        onProjectState?.({...data.projectState, generation});
      }
      entry.resolve(data);
    }
    if (kind === 'save') onSave(data);
    if (kind === 'dialog') onDialog?.(data);
    if (kind === 'local-file') onLocalFile?.(data.file);
    if (kind === 'close-intent') onCloseIntent?.();
    if (kind === 'project-state') onProjectState?.(data);
  }

  function post(kind, body, transfer = []) {
    check();
    frame.contentWindow.postMessage({type:prefix + kind, generation, ...body}, url.origin, transfer);
  }

  function exchange(kind, body, transfer, reply, matches, milliseconds = 30_000, fatal = true) {
    check();
    const result = expect(reply, matches, milliseconds, fatal);
    try {
      post(kind, body, transfer);
    } catch (error) {
      waiting.get(reply)?.reject(error);
    }
    return result;
  }

  async function captureSave(kind, {documentId, revision, path}) {
    const requestId = desktop.crypto.randomUUID();
    const result = await exchange(kind, {requestId, documentId, revision, path}, [], kind+'-result',
      data => data.requestId === requestId && data.documentId === documentId && data.path === path &&
        (kind === 'session-save' ? data.reviewedRevision === revision : data.revision === revision));
    if (result.outcome === 'busy') return null;
    if (result.outcome !== 'captured' || !(result.bytes instanceof ArrayBuffer)) {
      throw Error(result.message || 'PhotoCraft could not capture the requested save.');
    }
    return result;
  }

  async function startProject(path, bytes, newSettings, recover, importName = null) {
    const requestId = desktop.crypto.randomUUID();
    const packet = await exchange('start', {requestId, path, bytes, newSettings, recover, importName}, bytes ? [bytes] : [],
      'started', data => data.requestId === requestId, importName === null ? 30_000 : null);
    if (packet.ok !== true) throw Error(packet.message || 'PhotoCraft could not open the project.');
    return packet;
  }

  desktop.addEventListener('message', receive);
  frame.addEventListener('load', verifyDocument);
  const ready = expect('ready', () => true, 120_000, true);
  signal?.addEventListener('abort', abort, {once:true});
  if (signal?.aborted) abort();
  else frame.src = url.href;

  return Object.freeze({
    ready,
    assertLive: check,
    start(path = null, bytes = null, newSettings = null, recover = false) {
      return startProject(path, bytes === null ? null : bytes.slice().buffer, newSettings, recover);
    },
    importFile(name, bytes) {
      return startProject(null, bytes, null, false, name);
    },
    async captureRecovery({documentId, revision}) {
      const requestId = desktop.crypto.randomUUID();
      const packet = await exchange('recovery-capture', {requestId, documentId, revision}, [], 'recovery-captured',
        data => data.requestId === requestId && data.documentId === documentId && data.revision === revision,
        30_000, false);
      if (!(packet.bytes instanceof ArrayBuffer) || !packet.bytes.byteLength) throw Error(packet.message || 'PhotoCraft could not capture the draft.');
      return new Blob([packet.bytes]);
    },
    captureAutosave(target) { return captureSave('autosave', target); },
    captureSessionSave(target) { return captureSave('session-save', target); },
    async session(operation, lease, reviewed = {}) {
      const requestId = desktop.crypto.randomUUID();
      const {documentId, revision, dirty, unfinishedEdit} = reviewed;
      const result = await exchange('session',{requestId, operation, lease, documentId, revision, dirty, unfinishedEdit},
        [],'session-result', packet => packet.requestId === requestId && packet.operation === operation && packet.lease === lease,
        30_000, false);
      if (result.ok !== true) throw Error(result.message || 'PhotoCraft could not confirm the session operation.');
    },
    acknowledge(request, result) {
      const identity = Object.fromEntries(saveFields.map(field => [field, request[field]]));
      return exchange('save-result', {...identity, ...result}, [], 'save-settled',
        data => saveFields.every(field => data[field] === identity[field]));
    },
    reportUncertainSave(request) {
      const identity = Object.fromEntries(saveFields.map(field => [field, request[field]]));
      post('save-result', {...identity, outcome:'unknown'});
    },
    async requestClose(interactive) {
      const requestId = desktop.crypto.randomUUID();
      const result = await exchange('close', {requestId, interactive}, [], 'close-result',
        packet => packet.requestId === requestId, interactive ? null : 30_000);
      if (typeof result.approved !== 'boolean') throw Error(result.message || 'PhotoCraft could not confirm close.');
      return result.approved;
    },
    answerDialog(requestId, result) {
      post('dialog-result', {requestId, ...result});
    },
    dispose
  });
}
