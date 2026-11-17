/** Bind a public account application to the existing viewer's API2 host.
 * The app still owns its domain implementation, inspection and close decision.
 */
import {textRecovery} from './text-recovery.mjs';
import {wordcraftRecovery} from './wordcraft-recovery.mjs';
export function mountAccountApp(mount, host, kind) {
  const element = document.createElement('div');
  element.className = 'window-content';
  element.textContent = 'Opening ' + host.w.title + '…';
  let view, disposed = false, offLifecycle, offBinding;
  const listeners = new Set();
  const authority = Object.freeze({});
  const instanceId = String(host.w.id), session = host.session(), sessionId = session.public.sid;
  const valid = () => !disposed && !host.signal.aborted && host.session() === session
    && host.storage.signedInSubject() === session.public.sub && host.desktop.windows.includes(host.w);
  const authorize = async (candidate, target) => candidate === authority && valid()
    && target.instanceId === instanceId && target.sessionId === sessionId;
  const ready = (async () => {
    const context = await host.storage.accountFileContext();
    if (!valid() || !context.valid()) throw new DOMException('Account view closed.', 'AbortError');
    let resource = null;
    const launch = host.w.launchContext;
    if (launch) {
      if (launch.storage !== 'account' || launch.owner !== context.owner) throw Error('An account file launch is required.');
      const restore = ['text','wordcraft'].includes(kind) && launch.restore === true;
      resource = {path: launch.path, ...(restore ? {restore: true} : launch.sha256 ? {sha256: launch.sha256} : {})};
      if (!restore && !resource.sha256) resource.sha256 = (await context.files.version(resource.path)).sha256;
    }
    if (!valid()) throw new DOMException('Account view closed.', 'AbortError');
    const activateFile = file => {
      if (!valid()) throw new DOMException('Account view closed.', 'AbortError');
      return !!host.desktop.activateAccountFile({path: file.path, owner: context.owner});
    };
    const openFile = async file => {
      if (!valid()) throw new DOMException('Account view closed.', 'AbortError');
      // A second Files instance may have opened it while this read waited.
      if (activateFile(file)) return {status: 'activated'};
      const app = kind === 'wordcraft' || /[.](docx|odt|rtf)$/i.test(file.path) ? 'wordcraft' : 'text';
      host.desktop.openAccountFile(app, {path: file.path, sha256: file.sha256, owner: context.owner});
      return {status: 'opened'};
    };
    view = mount({instanceId, sessionId, resource, files: context.files, authority, authorize,
      ...(kind === 'text' ? {recovery: textRecovery(host, context, valid)} : {}),
      ...(kind === 'wordcraft' ? {
        recovery: wordcraftRecovery(host,context,valid), profileId: context.owner,
        imported: host.w.wordcraftImport || null, template: host.w.wordcraftTemplate || 'blank', recoveryAsCopy: !!host.w.wordcraftRecoveryAsCopy,
        newDocument(params={}) {if(!valid())throw new DOMException('Account view closed.','AbortError');const w=host.desktop.launch('wordcraft');w.wordcraftTemplate=params.template||'blank';return {status:'opened',instanceId:String(w.id)};},
        importDocument(input) {if(!valid())throw new DOMException('Account view closed.','AbortError');const w=host.desktop.launch('wordcraft',input.name+' — WordCraft');w.wordcraftImport=Object.freeze({...input});return {status:'opened',instanceId:String(w.id)};},
        closeView: () => host.desktop.requestWindowClose(host.w)
      } : {}),
      signal: host.signal, openFile, activateFile, displayName: session.public.name,
      ...(kind === 'wordcraft' ? {url: new URL('wordcraft/index.html', document.baseURI).href} : {})});
    if (!view || typeof view.dispose !== 'function' || !(view.element instanceof HTMLElement)) throw Error('Invalid account app view.');
    // The app owns the transient import until parsing succeeds or Retry needs
    // it. Layout/window metadata must not retain another full base64 payload.
    if(kind==='wordcraft')delete host.w.wordcraftImport;
    if (['text','wordcraft'].includes(kind)) {
      const synchronize = binding => {
        if (!valid() || !binding.loaded) return;
        if(kind==='wordcraft'&&binding.path!==null)delete host.w.wordcraftRecoveryAsCopy;
        host.desktop.updateAccountFileBinding(host.w, {owner: context.owner, path: binding.path, sha256: binding.revision});
      };
      offBinding = view.fileBinding.subscribe(synchronize); synchronize(view.fileBinding.snapshot());
    }
    if (view.lifecycle) { offLifecycle = view.lifecycle.subscribe(() => { for (const listener of [...listeners]) listener(); }); for (const listener of [...listeners]) listener(); }
    view.element.style.flex = '1'; view.element.style.minHeight = '0';
    element.style.display = 'flex'; element.style.flexDirection = 'column';
    element.replaceChildren(view.element);
    await view.ready;
    if (!valid()) throw new DOMException('Account view closed.', 'AbortError');
  })();
  ready.catch(error => { if (valid() && !view?.retry) element.textContent = 'Could not open this app: ' + error.message; });
  return {
    element, ready,
    focus() {
      if (!valid()) return false;
      if (view?.focus?.()) return true;
      // Never steal focus if the user selects a different window while loading.
      void ready.then(() => { if (valid() && host.desktop.active === host.w.id && host.desktop.current === host.w.workspace) view?.focus?.(); }).catch(() => {});
      return false;
    },
    ...(['text','wordcraft'].includes(kind) ? {lifecycle: Object.freeze({
      snapshot: () => view?.lifecycle.snapshot() ?? {revision: 0, dirty: false, pending: true},
      subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener); },
      async quiesce(options) { if (!view) await ready; return view.lifecycle.quiesce(options); },
      async commitClose() { return view?.lifecycle.commitClose(); }
    })} : {}),
    inspect: async () => { if (!view) await ready; return view.inspect?.(); },
    execute: async (request, candidate) => { if (!view) await ready; return view.execute(request, candidate); },
    async requestClose() { if (!view) return true; return typeof view.requestClose === 'function' ? await view.requestClose() : true; },
    dispose() { if (disposed) return; disposed = true; offLifecycle?.(); offBinding?.(); listeners.clear(); view?.dispose(); element.remove(); }
  };
}
