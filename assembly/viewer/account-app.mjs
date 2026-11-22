/** Bind a public account application to the existing viewer's API2 host.
 * The app still owns its domain implementation, inspection and close decision.
 */
import {textRecovery} from './text-recovery.mjs';
import {wordcraftRecovery} from './wordcraft-recovery.mjs';
import {pdfcraftRecovery} from './pdfcraft-recovery.mjs';
import {accountFileApp} from './file-associations.mjs';

function gridCell(args, write) {
  return args && typeof args === 'object' && !Array.isArray(args) &&
    Object.keys(args).length === (write ? 3 : 2) &&
    typeof args.sheet === 'string' && args.sheet.length > 0 && args.sheet.length <= 31 &&
    typeof args.cell === 'string' && /^[A-Z]{1,3}[1-9]\d{0,6}$/.test(args.cell) &&
    (!write || typeof args.input === 'string' && args.input.length <= 32_767);
}

const gridCommands = Object.freeze({
  'document.inspect': args => args && typeof args === 'object' && !Array.isArray(args) && !Object.keys(args).length,
  'cell.get': args => gridCell(args, false),
  'cell.set': args => gridCell(args, true)
});

// Each bundle owns its app's launch and mount. The ID returned by New or an
// import must be the native view ID even while that view is still loading.
const pendingInstances = new WeakMap();

export function mountAccountApp(mount, host, kind, officeRecovery = null, appAgentCommands = null) {
  const element = document.createElement('div');
  element.className = 'window-content';
  element.textContent = 'Opening ' + host.w.title + '…';
  let view, disposed = false, offLifecycle, offBinding, offAgentView;
  const listeners = new Set();
  const authority = Object.freeze({});
  const commands = kind === 'gridcraft' ? gridCommands : appAgentCommands;
  const workspace = host.storage.workspaceFileContext;
  const guest = !!workspace && host.session()?.public.kind === 'anonymous';
  const delegated = !guest && commands && typeof host.registerAgentView === 'function';
  const invocations = delegated ? new WeakMap() : null;
  const instanceId = delegated ? pendingInstances.get(host.w) ?? crypto.randomUUID() : String(host.w.id);
  if (delegated) pendingInstances.delete(host.w);
  const launched = w => {
    if (!delegated) return {status:'opened',instanceId:String(w.id)};
    const id = crypto.randomUUID();
    pendingInstances.set(w,id);
    return {status:'opened',instanceId:id};
  };
  const session = host.session(), sessionId = session.public.sid;
  const mounted = () => !disposed && !host.signal.aborted && host.session() === session
    && host.desktop.windows.includes(host.w);
  const valid = () => mounted() && (workspace ? host.storage.workspaceOwner() : host.storage.signedInSubject()) === session.public.sub;
  const authorize = async (candidate, target) => {
    if (!valid() || target.instanceId !== instanceId || target.sessionId !== sessionId) return false;
    if (candidate === authority) return true;
    const grant = invocations?.get(candidate);
    if (!grant) return false;
    invocations.delete(candidate);
    const request = grant.request;
    if (request.documentId !== target.documentId || request.resourceId !== target.resourceId ||
        request.command !== target.operation) return false;
    grant.check();
    return true;
  };
  let bindingKey, bindingId;
  const ready = (async () => {
    const context = await (workspace || host.storage.accountFileContext)();
    if (!valid() || !context.valid()) throw new DOMException('Account view closed.', 'AbortError');
    let resource = null;
    const launch = host.w.launchContext;
    if (launch) {
      if (launch.storage !== 'account' || launch.owner !== context.owner) throw Error('An account file launch is required.');
      const restore = ['text','wordcraft','pdfcraft','gridcraft','deckcraft'].includes(kind) && launch.restore === true;
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
      const target = accountFileApp(file.path,kind);
      if (target === 'audio-editor') {
        if (!window.CODI_VIEWER_PROFILE?.apps.includes(target)) throw Error('Audio Editor is unavailable in this desktop. Use Download to keep a copy.');
        host.desktop.open(target, {version: 1, storage: 'mirror', path: '/' + file.path, owner: context.owner});
        return {status: 'opened'};
      }
      if (['calculator','jsketcher','notebook','replicad','embroidery-studio'].includes(target) && window.CODI_VIEWER_PROFILE?.apps.includes(target)) {
        host.desktop.open(target, {version: 1, storage: guest ? 'temporary' : 'mirror', path: '/' + file.path, sha256: file.sha256, owner: context.owner});
        return {status: 'opened'};
      }
      const app = ['calculator','jsketcher','notebook','replicad','embroidery-studio'].includes(target) ? 'text' : target;
      host.desktop.openAccountFile(app, {path: file.path, sha256: file.sha256, owner: context.owner});
      return {status: 'opened'};
    };
    view = mount({instanceId, sessionId, resource, files: context.files, authority, authorize,
      ...(kind === 'files' && host.refreshPanelPins ? {onRefresh() {
        if (valid() && context.valid()) return host.refreshPanelPins();
      }} : {}),
      ...(kind === 'text' ? {recovery: guest ? null : textRecovery(host, context, valid)} : {}),
      ...(kind === 'wordcraft' ? {
        recovery: guest ? null : wordcraftRecovery(host,context,valid), profileId: context.owner,
        imported: host.w.wordcraftImport || null, template: host.w.wordcraftTemplate || 'blank', recoveryAsCopy: !!host.w.wordcraftRecoveryAsCopy,
        newDocument(params={}) {if(!valid())throw new DOMException('Account view closed.','AbortError');const w=host.desktop.launch('wordcraft');w.wordcraftTemplate=params.template||'blank';return {status:'opened',instanceId:String(w.id)};},
        importDocument(input) {if(!valid())throw new DOMException('Account view closed.','AbortError');const w=host.desktop.launch('wordcraft',input.name+' — WordCraft');w.wordcraftImport=Object.freeze({...input});return {status:'opened',instanceId:String(w.id)};},
        closeView: () => host.desktop.requestWindowClose(host.w)
      } : {}),
      ...(kind === 'pdfcraft' ? {
        recovery: guest ? null : pdfcraftRecovery(host,context,valid), profileId: context.owner,
        imported: host.w.pdfcraftImport || null, recoveryAsCopy: !!host.w.pdfcraftRecoveryAsCopy,
        newDocument() {if(!valid())throw new DOMException('Account view closed.','AbortError');const w=host.desktop.launch('pdfcraft');return {status:'opened',instanceId:String(w.id)};},
        importDocument(input) {if(!valid())throw new DOMException('Account view closed.','AbortError');const w=host.desktop.launch('pdfcraft',input.name+' — PdfCraft');w.pdfcraftImport=Object.freeze({...input});return {status:'opened',instanceId:String(w.id)};},
        closeView: () => host.desktop.requestWindowClose(host.w)
      } : {}),
      ...(officeRecovery ? {
        recovery: guest ? null : officeRecovery.journal(host,context,valid), profileId:context.owner,
        imported:host.w[kind+'Import']||null, recoveryAsCopy:!!host.w[kind+'RecoveryAsCopy'],
        template:host.w[kind+'Template']||(kind==='deckcraft'?{}:'blank'),
        newDocument(params={}) {
          if(!valid())throw new DOMException('Account view closed.','AbortError');
          const w=host.desktop.launch(kind);if(!w)throw Error('This application is unavailable.');
          // DeckCraft's native New parameters include theme/template settings;
          // pass the whole bounded native request, not a string-only template.
          w[kind+'Template']=structuredClone(kind==='deckcraft'?params:params.template||'blank');
          return launched(w);
        },
        importDocument(input) {
          if(!valid())throw new DOMException('Account view closed.','AbortError');
          const w=host.desktop.launch(kind,input.name+' — '+officeRecovery.name);if(!w)throw Error('This application is unavailable.');
          w[kind+'Import']=Object.freeze({...input});return launched(w);
        },
        closeView:()=>host.desktop.requestWindowClose(host.w)
      }:{}),
      signal: host.signal, openFile, activateFile, displayName: session.public.name,
      ...(['wordcraft','pdfcraft','gridcraft','deckcraft'].includes(kind) ? {url: new URL(kind+'/index.html', document.baseURI).href} : {})});
    if (!view || typeof view.dispose !== 'function' || !(view.element instanceof HTMLElement)) throw Error('Invalid account app view.');
    // The app owns the transient import until parsing succeeds or Retry needs
    // it. Layout/window metadata must not retain another full base64 payload.
    if(kind==='wordcraft')delete host.w.wordcraftImport;
    if(kind==='pdfcraft')delete host.w.pdfcraftImport;
    if(officeRecovery)delete host.w[kind+'Import'];
    if (['text','wordcraft','pdfcraft','gridcraft','deckcraft'].includes(kind)) {
      const synchronize = binding => {
        if (delegated) {
          const key = JSON.stringify([binding.loaded, binding.documentId, binding.path]);
          if (key !== bindingKey) { bindingKey = key; bindingId = crypto.randomUUID(); }
        }
        if (!valid() || !binding.loaded) return;
        if(kind==='wordcraft'&&binding.path!==null)delete host.w.wordcraftRecoveryAsCopy;
        if(kind==='pdfcraft'&&binding.path!==null)delete host.w.pdfcraftRecoveryAsCopy;
        if(officeRecovery&&binding.path!==null)delete host.w[kind+'RecoveryAsCopy'];
        host.desktop.updateAccountFileBinding(host.w, {owner: context.owner, path: binding.path, sha256: binding.revision});
      };
      offBinding = view.fileBinding.subscribe(synchronize); synchronize(view.fileBinding.snapshot());
    }
    if (view.lifecycle) { offLifecycle = view.lifecycle.subscribe(() => { for (const listener of [...listeners]) listener(); }); for (const listener of [...listeners]) listener(); }
    view.element.style.flex = '1'; view.element.style.minHeight = '0';
    element.style.display = 'flex'; element.style.flexDirection = 'column';
    element.replaceChildren(view.element);
    if (delegated) offAgentView = host.registerAgentView({
      windowId:host.w.id, name:officeRecovery.name, signal:host.signal, instanceId, sessionId, accountId:context.owner,
      commands, bindingId:() => bindingId,
      async snapshot() {
        if (!valid()) return null;
        const state = await view.inspect();
        return valid() && state.phase === 'ready' ? {...state, bindingId} : null;
      },
      async execute(request, check) {
        if (kind === 'gridcraft' && request.command === 'cell.set') {
          const state = await view.inspect();
          if (!state.documents.find(doc => doc.id === request.documentId)?.autosaveEligible) {
            throw Error('Finish the active GridCraft edit or operation first.');
          }
        }
        check();
        const candidate = Object.freeze({});
        invocations.set(candidate, {request, check});
        try { return await view.execute(request, candidate); }
        finally { invocations.delete(candidate); }
      }
    });
    await view.ready;
    if (!valid()) throw new DOMException('Account view closed.', 'AbortError');
  })();
  ready.catch(error => { if (mounted() && !view?.retry) element.textContent = 'Could not open this app: ' + error.message; });
  return {
    element, ready,
    focus() {
      if (!valid()) return false;
      if (view?.focus?.()) return true;
      // Never steal focus if the user selects a different window while loading.
      void ready.then(() => { if (valid() && host.desktop.active === host.w.id && host.desktop.current === host.w.workspace) view?.focus?.(); }).catch(() => {});
      return false;
    },
    ...(['text','wordcraft','pdfcraft','gridcraft','deckcraft'].includes(kind) ? {lifecycle: Object.freeze({
      snapshot: () => view?.lifecycle.snapshot() ?? {revision: 0, dirty: false, pending: true},
      subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener); },
      async quiesce(options) { if (!view) await ready; return view.lifecycle.quiesce(options); },
      async commitClose() { return view?.lifecycle.commitClose(); }
    })} : {}),
    inspect: async () => { if (!view) await ready; return view.inspect?.(); },
    execute: async (request, candidate) => { if (!view) await ready; return view.execute(request, candidate); },
    async requestClose() { if (!view) return true; return typeof view.requestClose === 'function' ? await view.requestClose() : true; },
    dispose() { if (disposed) return; disposed = true; offAgentView?.(); offLifecycle?.(); offBinding?.(); listeners.clear(); view?.dispose(); element.remove(); }
  };
}
