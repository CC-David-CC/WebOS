/** Bind a public account application to the existing viewer's API2 host.
 * The app still owns its domain implementation, inspection and close decision.
 */
import {textRecovery} from './text-recovery.mjs';
export function mountAccountApp(mount, host, kind) {
  const element = document.createElement('div');
  element.className = 'window-content';
  element.textContent = 'Opening ' + host.w.title + '…';
  let view, disposed = false, offLifecycle;
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
      resource = {path: launch.path, ...(launch.sha256 ? {sha256: launch.sha256} : {})};
      if (!resource.sha256) resource.sha256 = (await context.files.version(resource.path)).sha256;
    }
    if (!valid()) throw new DOMException('Account view closed.', 'AbortError');
    const openFile = async file => {
      if (!valid()) throw new DOMException('Account view closed.', 'AbortError');
      const app = /[.](docx|odt|rtf)$/i.test(file.path) ? 'wordcraft' : 'text';
      host.desktop.openAccountFile(app, {path: file.path, sha256: file.sha256, owner: context.owner});
    };
    view = mount({instanceId, sessionId, resource, files: context.files, authority, authorize,
      ...(kind === 'text' ? {recovery: textRecovery(host, context, valid)} : {}),
      signal: host.signal, openFile, displayName: session.public.name,
      ...(kind === 'wordcraft' ? {url: new URL('wordcraft/index.html', document.baseURI).href} : {})});
    if (!view || typeof view.dispose !== 'function' || !(view.element instanceof HTMLElement)) throw Error('Invalid account app view.');
    if (view.lifecycle) { offLifecycle = view.lifecycle.subscribe(() => { for (const listener of [...listeners]) listener(); }); for (const listener of [...listeners]) listener(); }
    view.element.style.flex = '1'; view.element.style.minHeight = '0';
    element.style.display = 'flex'; element.style.flexDirection = 'column';
    element.replaceChildren(view.element);
    await view.ready;
    if (!valid()) throw new DOMException('Account view closed.', 'AbortError');
  })();
  ready.catch(error => { if (valid()) element.textContent = 'Could not open this app: ' + error.message; });
  return {
    element, ready,
    ...(kind === 'text' ? {lifecycle: Object.freeze({
      snapshot: () => view?.lifecycle.snapshot() ?? {revision: 0, dirty: false, pending: false},
      subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener); },
      async quiesce(options) { await ready; return view.lifecycle.quiesce(options); },
      async commitClose() { return view?.lifecycle.commitClose(); }
    })} : {}),
    inspect: async () => { await ready; return view.inspect?.(); },
    execute: async (request, candidate) => { await ready; return view.execute(request, candidate); },
    async requestClose() { if (!view) return true; return typeof view.requestClose === 'function' ? await view.requestClose() : true; },
    dispose() { if (disposed) return; disposed = true; offLifecycle?.(); listeners.clear(); view?.dispose(); element.remove(); }
  };
}
