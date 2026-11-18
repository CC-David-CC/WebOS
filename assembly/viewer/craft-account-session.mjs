function sessionChoice({app, appName, name, scope, signal, canSave}) {
  if (signal.aborted) return Promise.resolve('cancel');
  const dialog = document.createElement('dialog');
  const action = scope === 'window' ? 'closing' : 'signing out';
  dialog.className = `codi-confirm-dialog webos-${app}-session`;
  dialog.setAttribute('aria-label', `Save ${appName} changes before ${action}?`);
  const heading = document.createElement('h2');
  heading.textContent = `Save changes before ${action}?`;
  const text = document.createElement('p');
  text.textContent = canSave
    ? name + ' has unsaved changes.'
    : name + ' has an active edit. Cancel to finish it, or discard the changes.';
  const buttons = document.createElement('div');
  buttons.className = 'codi-confirm-actions';
  dialog.append(heading,text,buttons);
  return new Promise(resolve => {
    function finish(result) {
      signal.removeEventListener('abort',cancel);
      dialog.close();
      dialog.remove();
      resolve(result);
    }
    const cancel = () => finish('cancel');
    for (const [label, value] of [['Cancel','cancel'],['Discard','discard'],['Save','save']]) {
      const button = document.createElement('button');
      button.textContent = label;
      button.type = 'button';
      button.disabled = value === 'save' && !canSave;
      button.autofocus = value === 'cancel';
      button.addEventListener('click',()=>finish(value),{once:true});
      buttons.append(button);
    }
    dialog.addEventListener('cancel',event=>{event.preventDefault();cancel();},{once:true});
    signal.addEventListener('abort',cancel,{once:true});
    document.body.append(dialog);
    try { dialog.showModal(); } catch { cancel(); }
  });
}

/** Coordinate the native frame with the Desktop's Accounts finalization lease. */
export function createCraftSession({app, appName, native, storage, drafts, autosave, signal, valid, loaded, frame,
  documentName, choosePath, write, onError, choose = sessionChoice}) {
  const listeners = new Set();
  let state, fingerprint, revision = 0, approved, held, disposed = false;
  let snapshot = Object.freeze({revision,dirty:false,pending:true});

  function observe() {
    const {identity, binding, pending} = storage.inspect();
    const exact = loaded() && state?.available === true && identity &&
      state.generation === identity.generation && state.documentId === identity.documentId;
    const dirty = exact ? state.dirty || state.unfinishedEdit : false;
    const busy = !exact || !!pending || state.operationPending;
    const next = JSON.stringify([exact ? state : null, binding, pending, busy]);
    if (fingerprint !== next) {
      fingerprint = next;
      snapshot = Object.freeze({revision:++revision,dirty,pending:busy});
      for (const listener of [...listeners]) listener(snapshot);
    }
    return snapshot;
  }

  function check(scope, reviewed) {
    if (disposed || signal.aborted || !valid()) throw Error(`The ${appName} account window closed.`);
    const current = observe();
    if (current.pending) throw Error(`Finish the pending ${appName} operation before ${scope === 'window' ? 'closing' : 'signing out'}.`);
    if (reviewed && current.revision !== reviewed.revision) throw Error(`${appName} changed after you reviewed it.`);
    return current;
  }

  return {
    receive(packet) {
      if (packet.available === true) {
        if (typeof packet.documentId !== 'string' || typeof packet.revision !== 'string' ||
            !/^[0-9]{1,20}$/.test(packet.revision) ||
            ['dirty','unfinishedEdit','operationPending','capturable'].some(key=>typeof packet[key]!=='boolean')) return;
        if (state?.generation === packet.generation && state.documentId === packet.documentId &&
            BigInt(packet.revision) < BigInt(state.revision)) return;
        const {available,generation,documentId,revision,dirty,unfinishedEdit,operationPending,capturable} = packet;
        state = {available,generation,documentId,revision,dirty,unfinishedEdit,operationPending,capturable};
      } else state = null;
      observe();
    },
    observe,
    async approve(scope = 'session') {
      approved = null;
      autosave.closing(true);
      try {
        const reviewed = check(scope);
        if (!reviewed.dirty) return true;
        const canSave = state.dirty && (!state.unfinishedEdit || state.capturable);
        const choice = await choose({app,appName,name:documentName(),scope,signal,canSave});
        if (choice === 'cancel') return false;
        check(scope,reviewed);
        if (choice === 'discard') {
          approved = {revision:reviewed.revision,scope};
          return true;
        }
        if (choice !== 'save' || !canSave) return false;
        const path = storage.inspect().binding?.path ?? await choosePath();
        if (path === null) return false;
        check(scope,reviewed);
        const payload = await native.captureSessionSave({documentId:state.documentId,revision:state.revision,path});
        if (!payload) throw Error(`${appName} changed after you reviewed it.`);
        const result = await write(payload);
        if (result.error) throw result.error;
        if (check(scope).dirty) throw Error(`${appName} has changes made after the save capture.`);
        return true;
      } finally {
        autosave.closing(false);
      }
    },
    snapshot:observe,
    subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener); },
    async quiesce(scope = 'session') {
      const reviewed = check(scope);
      if (held || reviewed.dirty && (approved?.revision !== reviewed.revision || approved.scope !== scope)) {
        throw Error(`Review the current ${appName} changes before ${scope === 'window' ? 'closing' : 'signing out'}.`);
      }
      const lease = crypto.randomUUID();
      autosave.closing(true);
      frame.inert = true;
      const resumeDrafts = await drafts.pause();
      try {
        check(scope,reviewed);
        await native.session('pause',lease,state);
        check(scope,reviewed);
      } catch (error) {
        void native.session('release',lease).catch(()=>{});
        resumeDrafts();
        frame.inert = false;
        autosave.closing(false);
        throw error;
      }
      held = {lease,reviewed};
      return Object.freeze({release() {
        if (held?.lease !== lease) return;
        held = null;
        if (disposed) return;
        void native.session('release',lease).then(()=>{
          if (disposed) return;
          frame.inert = false;
          resumeDrafts();
          autosave.closing(false);
        },onError);
      }});
    },
    async commitClose() {
      if (!held || observe().revision !== held.reviewed.revision) throw Error(`The reviewed ${appName} pause is no longer available.`);
      await native.session('finalize',held.lease);
      held = null;
      try { await drafts.clear(); } catch (error) { onError(error); }
    },
    dispose() { disposed = true; listeners.clear(); },
  };
}
