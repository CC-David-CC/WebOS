import {createRecoveryStore, createRecoveryJournal} from '@webos/runtime/local-recovery';
import {createOfficeRecovery} from './office-recovery.mjs';
import {projectPath} from './photocraft-storage.mjs';

function capture(value) {
  const {path, revision, bytes, nativeRevision} = value;
  if (path !== null) projectPath(path);
  if (!(path === null ? revision === null : typeof revision === 'string' && /^[0-9a-f]{64}$/.test(revision)) ||
      typeof nativeRevision !== 'string' || !/^[0-9]{1,20}$/.test(nativeRevision) ||
      !(bytes instanceof Blob) || bytes.size < 8 || bytes.size > 128 * 1024 * 1024) {
    throw Error('Invalid PhotoCraft recovery snapshot.');
  }
  return {path, revision, bytes, nativeRevision};
}

export const photoRecovery = createOfficeRecovery('photocraft', 'PhotoCraft', {
  createDraftStore: options => createRecoveryStore({...options, database:'webos-photocraft-recovery-v1', capture}),
  createDraftJournal: options => createRecoveryJournal({...options, capture}),
});

/** Capture at most one revision at a time. Retain prior bytes until a new draft commits. */
export function trackPhotoDraft({journal, native, storage, valid, onError}) {
  let state, recordedState, recordedBinding, timer, task, stopped = false, paused = false;

  function schedule() {
    clearTimeout(timer);
    if (stopped || paused || task || !valid() || !state?.capturable) return;
    const inspected = storage.inspect();
    if (!inspected.identity || state.documentId !== inspected.identity.documentId ||
        state.generation !== inspected.identity.generation || (!state.dirty && inspected.pending) ||
        (state === recordedState && inspected.binding === recordedBinding)) return;
    timer = setTimeout(() => reconcile(state, inspected.binding), 250);
  }

  function receive(packet) {
    if (packet.available !== true) state = null;
    else {
      if (typeof packet.documentId !== 'string' || !/^[0-9]{1,20}$/.test(packet.documentId) ||
          typeof packet.revision !== 'string' || !/^[0-9]{1,20}$/.test(packet.revision) ||
          typeof packet.dirty !== 'boolean' || typeof packet.capturable !== 'boolean') return;
      if (state?.generation === packet.generation && state.documentId === packet.documentId && BigInt(packet.revision) < BigInt(state.revision)) return;
      state = packet;
    }
    schedule();
  }

  function reconcile(current, binding) {
    if (stopped || !valid() || state !== current) return;
    // State events and the Storage write acknowledgement arrive independently.
    const canPublish = () => !stopped && valid() && state === current && storage.inspect().binding === binding;
    let retry = true;
    task = (async () => {
      if (current.dirty) {
        const bytes = await native.captureRecovery(current);
        if (!canPublish()) return;
        await journal.write({path:binding?.path ?? null, revision:binding?.sha256 ?? null, bytes, nativeRevision:current.revision});
      } else {
        if (!canPublish() || storage.inspect().pending) return;
        await journal.clear();
      }
      recordedState = current;
      recordedBinding = binding;
    })().catch(error => {
      if (canPublish()) {
        retry = false;
        onError(error);
      }
    }).finally(() => {
      task = null;
      if (retry) schedule();
    });
  }

  return {
    receive,
    schedule,
    async pause() {
      paused = true;
      clearTimeout(timer);
      await task;
      return () => { paused = false; schedule(); };
    },
    async clear() {
      stopped = true;
      clearTimeout(timer);
      await task;
      await journal.clear();
    },
    stop() {
      stopped = true;
      clearTimeout(timer);
    },
  };
}
