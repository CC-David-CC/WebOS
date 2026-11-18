const prefix = 'photocraft:account-';
const generationPattern = /^[0-9a-f]{32}$/;
const saveFields = ['ticket', 'documentId', 'revision', 'path'];

/** One native PhotoCraft instance inside a same-origin classic Desktop window. */
export function connectPhotoNative(frame, {url, signal, onSave, onUnavailable}) {
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

  function expect(kind, matches, milliseconds) {
    if (waiting.has(kind)) throw Error('PhotoCraft is already processing this request.');
    return new Promise((resolve, reject) => {
      function finish(callback, value) {
        clearTimeout(timer);
        waiting.delete(kind);
        callback(value);
      }
      const timer = setTimeout(
        () => unavailable('PhotoCraft did not confirm the native request.'),
        milliseconds
      );
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
    if (entry?.matches(data)) entry.resolve(data);
    if (kind === 'save') onSave(data);
  }

  function exchange(kind, body, transfer, reply, matches) {
    check();
    const result = expect(reply, matches, 30_000);
    try {
      frame.contentWindow.postMessage({type:prefix + kind, generation, ...body}, url.origin, transfer);
    } catch (error) {
      waiting.get(reply)?.reject(error);
    }
    return result;
  }

  desktop.addEventListener('message', receive);
  frame.addEventListener('load', verifyDocument);
  const ready = expect('ready', () => true, 120_000);
  signal?.addEventListener('abort', abort, {once:true});
  if (signal?.aborted) abort();
  else frame.src = url.href;

  return Object.freeze({
    ready,
    async start(path = null, bytes = null) {
      const requestId = desktop.crypto.randomUUID();
      const buffer = bytes === null ? null : bytes.slice().buffer;
      const packet = await exchange('start', {requestId, path, bytes:buffer}, buffer ? [buffer] : [],
        'started', data => data.requestId === requestId);
      if (packet.ok !== true) throw Error(packet.message || 'PhotoCraft could not open the project.');
      return packet;
    },
    acknowledge(request, result) {
      const identity = Object.fromEntries(saveFields.map(field => [field, request[field]]));
      return exchange('save-result', {...identity, ...result}, [], 'save-settled',
        data => saveFields.every(field => data[field] === identity[field]));
    },
    dispose
  });
}
