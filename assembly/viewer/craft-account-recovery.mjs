import {createRecoveryStore, createRecoveryJournal} from '@webos/runtime/local-recovery';
import {createOfficeRecovery} from './office-recovery.mjs';
import {MAX_BYTES, craftProjectPath} from './craft-account-storage.mjs';

export function createCraftRecovery({app, name, extension, legacyExtensions}) {
  function capture(value) {
    const {path, revision, bytes, nativeRevision} = value;
    if (path !== null) craftProjectPath(path, extension, legacyExtensions);
    if (!(path === null ? revision === null : typeof revision === 'string' && /^[0-9a-f]{64}$/.test(revision)) ||
        typeof nativeRevision !== 'string' || !/^[0-9]{1,20}$/.test(nativeRevision) ||
        !(bytes instanceof Blob) || bytes.size < 8 || bytes.size > MAX_BYTES) {
      throw Error(`Invalid ${name} recovery snapshot.`);
    }
    return {path, revision, bytes, nativeRevision};
  }

  return createOfficeRecovery(app, name, {
    createDraftStore: options => createRecoveryStore({...options, database:`webos-${app}-recovery-v1`, capture}),
    createDraftJournal: options => createRecoveryJournal({...options, capture}),
  });
}

/** Capture at most one revision at a time. Retain prior bytes until a new draft commits. */
export function trackCraftDraft({journal, native, storage, valid, onError}) {
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
      const recoveryRevision = packet.recoveryRevision === undefined ? packet.revision : packet.recoveryRevision;
      if (typeof packet.documentId !== 'string' || !/^[0-9]{1,20}$/.test(packet.documentId) ||
          typeof packet.revision !== 'string' || !/^[0-9]{1,20}$/.test(packet.revision) ||
          typeof recoveryRevision !== 'string' || !/^[0-9]{1,20}$/.test(recoveryRevision) ||
          typeof packet.dirty !== 'boolean' || typeof packet.capturable !== 'boolean') return;
      if (state?.generation === packet.generation && state.documentId === packet.documentId &&
          (BigInt(packet.revision) < BigInt(state.revision) || BigInt(recoveryRevision) < BigInt(state.recoveryRevision))) return;
      state = {...packet,recoveryRevision};
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
        const bytes = await native.captureRecovery({...current,revision:current.recoveryRevision});
        if (!canPublish()) return;
        await journal.write({path:binding?.path ?? null, revision:binding?.sha256 ?? null, bytes, nativeRevision:current.recoveryRevision});
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
