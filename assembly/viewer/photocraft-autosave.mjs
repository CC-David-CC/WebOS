import {accountAutosaveRetry, createAccountAutosave} from '@webos/runtime/account-autosave';

/** Bind the shared timing policy to one exact PhotoCraft document and its save adapter. */
export function trackPhotoAutosave({native, storage, valid, write, onState}, timing) {
  let state, enabled = false, closing = false;
  function target() {
    const {identity, binding, pending} = storage.inspect();
    if (!identity || !binding || identity.generation !== state?.generation || identity.documentId !== state?.documentId) return null;
    return {
      identity:[state.generation, state.documentId, binding.path].join('\0'),
      version:state.revision,
      path:binding.path,
      dirty:state.dirty === true,
      eligible:valid() && enabled && !closing && !pending && state.autosaveEligible === true,
    };
  }

  const account = createAccountAutosave({
    ...timing,
    async save({identity, version, signal}) {
      const current = target();
      if (!current?.eligible || current.identity !== identity || current.version !== version || signal.aborted) return {status:'busy'};
      const packet = await native.captureAutosave({documentId:state.documentId, revision:version, path:current.path});
      if (!packet) return {status:'busy'};
      const result = await write(packet);
      if (!result.error) return {status:'saved'};
      return accountAutosaveRetry(result.error) ?? {status:'paused',reason:result.error.message};
    },
    onState,
  });

  function update() {
    const current = target();
    account.observe(current ?? {identity:null,version:'',dirty:false,eligible:false});
  }
  return {
    receive(packet) {
      if (packet.available === true && typeof packet.documentId === 'string' &&
          typeof packet.revision === 'string' && /^[0-9]{1,20}$/.test(packet.revision)) {
        if (state?.generation === packet.generation && state.documentId === packet.documentId &&
            BigInt(packet.revision) < BigInt(state.revision)) return;
        state = packet;
      } else state = null;
      update();
    },
    update,
    enabled(value) { enabled = value; update(); },
    closing(value) { closing = value; update(); },
    confirmed() {
      update();
      const current = target();
      if (current) account.confirmed({identity:current.identity});
    },
    failed(error) {
      update();
      if (target()) account.pause(error.message);
    },
    dispose:account.dispose,
  };
}
