import {connectPhotoNative} from './photocraft-native.mjs';
import {trackPhotoAutosave} from './photocraft-autosave.mjs';
import {photoRecovery, trackPhotoDraft} from './photocraft-recovery.mjs';
import {createPhotoSession} from './photocraft-session.mjs';
import {createPhotoStorage, MAX_BYTES, projectPath} from './photocraft-storage.mjs';

const localImports = new WeakMap();

const scopedCommands = Object.freeze({
  'document.inspect': args => args && !Array.isArray(args) && typeof args === 'object' && !Object.keys(args).length,
  'layer.rename': args => args && !Array.isArray(args) && typeof args === 'object' && Object.keys(args).length === 2 &&
    typeof args.layerId === 'string' && /^[1-9][0-9]{0,19}$/.test(args.layerId) &&
    typeof args.name === 'string' && args.name.trim() && new TextEncoder().encode(args.name).length <= 256 &&
    !/[\u0000-\u001f\u007f-\u009f]/u.test(args.name),
});

function fileFromDevice(file) {
  return file instanceof File && file.size > 0 && file.size <= MAX_BYTES && file.name.trim() &&
    file.name !== '.' && file.name !== '..' && !/[/\\\u0000-\u001f\u007f-\u009f]/u.test(file.name) &&
    new TextEncoder().encode(file.name).length <= 255;
}

/** The classic Desktop's API2 view for the PhotoCraft editor. */
export function mount(host) {
  const element = document.createElement('div');
  element.className = 'window-content webos-photocraft';
  element.style.display = 'flex';
  element.style.flexDirection = 'column';
  const status = document.createElement('div');
  status.setAttribute('role', 'status');
  status.textContent = 'Opening PhotoCraft…';
  status.style.flex = '1';
  const appBar = document.createElement('div');
  appBar.style.display = 'flex';
  const autoToggle = document.createElement('button');
  autoToggle.type = 'button';
  autoToggle.textContent = 'AutoSave';
  autoToggle.hidden = true;
  const openLocal = document.createElement('button');
  openLocal.type = 'button';
  openLocal.textContent = 'Open from device';
  openLocal.hidden = true;
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.hidden = true;
  appBar.append(status, openLocal, autoToggle, fileInput);
  const frame = document.createElement('iframe');
  frame.title = 'PhotoCraft editor';
  frame.style.flex = '1';
  frame.style.minHeight = '0';
  frame.style.border = '0';
  frame.inert = true;

  const abort = new AbortController();
  const session = host.session();
  const instanceId = typeof host.registerAgentView === 'function' ? crypto.randomUUID() : null;
  let native, storage, context, dialog, journal, drafts, autosave, photoSession, loaded = false, windowCloseApproved = false;
  let autosaveKey, autoEnabled = false;
  let lastDialog = 0n;
  let agentPath, bindingId;
  const valid = () => !abort.signal.aborted && !host.signal.aborted && host.session() === session &&
    host.desktop.windows.includes(host.w) && host.storage.signedInSubject() === session?.public.sub && context?.valid();
  const check = () => {
    if (!valid()) throw new DOMException('PhotoCraft account view closed.', 'AbortError');
    if (loaded) native.assertLive();
  };
  const bind = resource => {
    check();
    host.desktop.updateAccountFileBinding(host.w, {owner:context.owner, ...resource});
    if (instanceId && resource.path !== agentPath) {
      agentPath = resource.path;
      bindingId = crypto.randomUUID();
    }
  };

  function agentDocument() {
    if (!instanceId || !loaded || !valid()) return null;
    const {identity, binding} = storage.inspect();
    const path = binding?.path ?? null;
    if (path !== agentPath) {
      agentPath = path;
      bindingId = crypto.randomUUID();
    }
    return {instanceId, sessionId:session.public.sid, documentId:identity.documentId,
      resourceId:path ?? 'draft:'+identity.documentId, bindingId};
  }

  function message(text) {
    status.textContent = text;
    status.hidden = !text;
  }

  function launchLocal(file) {
    if (!loaded || !valid()) return;
    if (!fileFromDevice(file)) {
      host.ui.feedback('PhotoCraft needs a named file no larger than 128 MiB.');
      return;
    }
    const window = host.desktop.launch('photocraft', file.name + ' — PhotoCraft');
    if (!window) return;
    window.ownerSub = context.owner;
    localImports.set(window, {file, session});
  }

  openLocal.addEventListener('click', () => { if (loaded && valid()) fileInput.click(); });
  fileInput.addEventListener('change', () => {
    const file = fileInput.files?.[0];
    fileInput.value = '';
    if (file) launchLocal(file);
  });

  function setAutosave(value) {
    autoEnabled = value;
    autoToggle.setAttribute('aria-pressed', String(value));
    autoToggle.title = value ? 'Account AutoSave is on' : 'Account AutoSave is off';
    autosave.enabled(value);
  }
  autoToggle.addEventListener('click', () => {
    if (!loaded || !valid()) return;
    setAutosave(!autoEnabled);
    try {
      document.defaultView.localStorage?.setItem(autosaveKey, autoEnabled ? 'on' : 'off');
    } catch {
      host.ui.feedback('This browser could not remember the PhotoCraft AutoSave setting.');
    }
  });

  async function save(packet, automatic = false) {
    if (!loaded || !valid()) return {error:Error('The PhotoCraft account editor is closed.')};
    message('Saving to your account…');
    try {
      check();
      const writing = storage.save(packet, native.acknowledge);
      photoSession.observe();
      const binding = await writing;
      bind(binding);
      message('');
      drafts.schedule();
      if (!automatic) autosave.confirmed();
      return {binding};
    } catch (error) {
      if (!valid()) return {error};
      if (loaded && error.outcome === 'unknown') {
        try { native.reportUncertainSave(packet); } catch { /* The document frame is unavailable. */ }
      }
      message(error.message);
      if (!automatic) autosave.failed(error);
      return {error};
    } finally {
      photoSession.observe();
    }
  }

  async function chooseProject(packet, signal) {
    const picked = packet.path === null ? await host.storage.pickAccountFile({extensions:['.pcraft'], signal}) : null;
    check();
    if (!loaded || signal.aborted) return {outcome:'cancelled'};
    if (packet.path === null && picked === null) return {outcome:'cancelled'};
    if (packet.path === null && (typeof picked !== 'string' || !picked.startsWith('/'))) throw Error('Invalid account project selection.');
    const path = projectPath(packet.path === null ? picked.slice(1) : packet.path);
    const resource = {owner:context.owner, path};
    if (host.desktop.activateAccountFile(resource, 'photocraft')) return {outcome:'opened'};
    const {sha256} = await context.files.version(path, {signal});
    check();
    if (!loaded || signal.aborted) return {outcome:'cancelled'};
    host.desktop.openAccountFile('photocraft', {...resource, sha256});
    return {outcome:'opened'};
  }

  async function chooseDestination(suggested, signal) {
    const folder = await host.storage.pickAccountFile({foldersOnly:true, signal});
    check();
    if (!loaded || signal.aborted || folder === null) return {outcome:'cancelled'};
    if (typeof folder !== 'string' || !folder.startsWith('/')) throw Error('Invalid account folder selection.');
    const name = await host.ui.prompt('File name', {
      title:'Save PhotoCraft project', value:suggested.split('/').pop(), confirmLabel:'Save', signal
    });
    check();
    if (!loaded || signal.aborted || name === null) return {outcome:'cancelled'};
    const filename = name.trim();
    if (!filename || filename.includes('/') || filename === '.' || filename === '..') throw Error('Enter a project file name.');
    const extension = /[.]pcraft$/i.test(filename) ? '' : '.pcraft';
    return {outcome:'destination', path:projectPath((folder === '/' ? '' : folder.slice(1) + '/') + filename + extension)};
  }

  async function handleDialog(packet) {
    const requestId = packet.requestId;
    if (!loaded || !valid() || dialog || typeof requestId !== 'string' || !/^[1-9][0-9]{0,19}$/.test(requestId) ||
        BigInt(requestId) <= lastDialog) return;
    lastDialog = BigInt(requestId);
    const controller = new AbortController();
    dialog = controller;
    let answer;
    try {
      if (packet.operation === 'new' && typeof packet.settings === 'string' && packet.settings.length <= 4096) {
        const settings = JSON.parse(packet.settings);
        if (!settings || typeof settings !== 'object' || Array.isArray(settings)) throw Error('Invalid new project settings.');
        check();
        const window = host.desktop.launch('photocraft');
        if (!window) throw Error('PhotoCraft is unavailable.');
        window.photocraftNewSettings = packet.settings;
        answer = {outcome:'opened'};
      } else if (packet.operation === 'open') answer = await chooseProject(packet, controller.signal);
      else if (packet.operation === 'save' && typeof packet.suggested === 'string' && packet.suggested.length <= 2048) {
        answer = await chooseDestination(packet.suggested, controller.signal);
      } else throw Error('Invalid PhotoCraft dialog request.');
    } catch (error) {
      answer = {outcome:'failed', message:String(error.message || 'PhotoCraft dialog failed.').slice(0, 250)};
    } finally {
      dialog = null;
    }
    if (!loaded || !valid() || controller.signal.aborted) return;
    try {
      native.answerDialog(requestId, answer);
    } catch (error) {
      message(error.message);
    }
  }

  const ready = (async () => {
    context = await host.storage.accountFileContext();
    check();
    journal = photoRecovery.journal(host, context, valid);
    const draft = await journal.load();
    check();
    const launch = host.w.launchContext;
    let resource;
    if (launch && !draft) {
      if (launch.storage !== 'account' || launch.owner !== context.owner) throw Error('An account project launch is required.');
      const path = projectPath(launch.path);
      const sha256 = launch.restore !== true && launch.sha256
        ? launch.sha256
        : (await context.files.version(path, {signal:abort.signal})).sha256;
      check();
      resource = {path, sha256};
    }

    const url = new URL('photocraft/index.html', document.baseURI);
    url.searchParams.set('host', 'webos-account');
    url.searchParams.set('profile', context.owner);
    storage = createPhotoStorage({files:context.files, operations:host.documentOperations, valid});
    native = connectPhotoNative(frame, {
      url, signal:abort.signal, onSave:packet => void save(packet), onDialog:handleDialog, onLocalFile:launchLocal,
      onProjectState(packet) {
        drafts?.receive(packet);
        autosave?.receive(packet);
        photoSession?.receive(packet);
      },
      onCloseIntent() {
        if (loaded && valid()) void host.desktop.requestWindowClose(host.w);
      },
      onUnavailable(reason) {
        loaded = false;
        frame.inert = true;
        dialog?.abort();
        drafts?.stop();
        autosave?.dispose();
        photoSession?.observe();
        message(reason);
      }
    });
    drafts = trackPhotoDraft({
      journal, native, storage, valid:() => loaded && valid(),
      onError(error) { message('PhotoCraft could not update the browser draft. ' + error.message); }
    });
    autosave = trackPhotoAutosave({
      native, storage, valid:() => loaded && valid(), write:packet => save(packet, true),
      onState(state) {
        if (autoEnabled) {
          const details = {idle:'Account AutoSave is on', scheduled:'Account AutoSave is waiting for edits to settle',
            waiting:'Account AutoSave is waiting for an eligible named project',
            saving:'Saving changes to your account', retrying:'Account AutoSave will retry',
            paused:state.reason};
          autoToggle.title = details[state.state] ?? 'Account AutoSave is on';
        }
      },
    });
    photoSession = createPhotoSession({
      native, storage, drafts, autosave, frame, signal:abort.signal, valid, loaded:() => loaded,
      documentName:() => host.w.title || 'The PhotoCraft project',
      async choosePath() {
        const result = await chooseDestination('Untitled.pcraft',abort.signal);
        return result.outcome === 'destination' ? result.path : null;
      },
      write:save,
      onError(error) { host.ui.feedback(error.message); },
    });
    element.append(frame);
    await native.ready;
    check();
    let recoveryMessage = '';
    if (draft) {
      const duplicate = draft.path !== null && !!host.desktop.accountFileLocation({owner:context.owner, path:draft.path}, 'photocraft', host.w);
      const recoveryBinding = await storage.restore(draft, (path, bytes) => native.start(path, bytes, null, true),
        {asCopy:duplicate || host.w.photocraftRecoveryAsCopy === true, signal:abort.signal});
      bind(recoveryBinding ?? {path:null, sha256:null});
      recoveryMessage = !recoveryBinding && draft.path !== null
        ? 'Recovered an unsaved copy. Save As to keep it in your account.'
        : 'Recovered unsaved changes from this browser.';
    } else if (resource) {
      bind(await storage.open(resource, native.start));
    } else {
      const source = localImports.get(host.w);
      localImports.delete(host.w);
      if (source) {
        if (source.session !== session) throw Error('The account changed before PhotoCraft could import the file.');
        const bytes = await source.file.arrayBuffer();
        check();
        // Native import questions are part of the opening flow.
        frame.inert = false;
        storage.attachBlank(await native.importFile(source.file.name, bytes));
      } else {
        const settings = host.w.photocraftNewSettings;
        delete host.w.photocraftNewSettings;
        storage.attachBlank(await native.start(null, null, settings));
      }
    }
    check();
    loaded = true;
    frame.inert = false;
    photoSession.observe();
    autosaveKey = 'webos:photocraft:account-autosave:' + encodeURIComponent(context.owner);
    let value = false;
    try { value = document.defaultView.localStorage?.getItem(autosaveKey) === 'on'; } catch { /* Use this window's default. */ }
    setAutosave(value);
    autoToggle.hidden = false;
    openLocal.hidden = false;
    message(recoveryMessage);
    drafts.schedule();
    if (instanceId) host.registerAgentView({
      windowId:host.w.id, name:'PhotoCraft', signal:abort.signal,
      instanceId, sessionId:session.public.sid, accountId:context.owner,
      commands:scopedCommands, bindingId:() => agentDocument()?.bindingId,
      snapshot:agentDocument,
      execute(request, authorize) {
        check();
        const target = agentDocument();
        if (!target || ['instanceId','sessionId','documentId','resourceId'].some(key => request[key] !== target[key])) {
          throw Error('The PhotoCraft document binding changed.');
        }
        authorize();
        return native.operation({documentId:target.documentId,path:agentPath,command:request.command,args:request.args});
      },
    });
  })();
  ready.catch(error => {
    frame.remove();
    native?.dispose();
    if (!abort.signal.aborted && !host.signal.aborted) message(error.message);
  });

  function dispose() {
    if (abort.signal.aborted) return;
    abort.abort();
    dialog?.abort();
    drafts?.stop();
    autosave?.dispose();
    photoSession?.dispose();
    journal?.close();
    host.signal.removeEventListener('abort', dispose);
    element.remove();
  }

  element.append(appBar);
  host.signal.addEventListener('abort', dispose, {once:true});
  if (host.signal.aborted) dispose();
  return {
    element,
    ready,
    ...(instanceId ? {inspect() {
      const target = agentDocument();
      if (!target) return null;
      const {bindingId, ...document} = target;
      return document;
    }} : {}),
    lifecycle:Object.freeze({
      snapshot:() => photoSession?.snapshot() ?? {revision:0,dirty:false,pending:true},
      subscribe:listener => photoSession?.subscribe(listener) ?? (() => {}),
      async quiesce() { await ready; return photoSession.quiesce(); },
      async commitClose() { if (!windowCloseApproved) await photoSession.commitClose(); },
    }),
    async requestClose({scope = 'window'} = {}) {
      if (!loaded && scope === 'window') {
        windowCloseApproved = true;
        return true;
      }
      check();
      if (scope === 'session') {
        await ready;
        return photoSession.approve();
      }
      const interactive = scope === 'window';
      autosave.closing(true);
      let closeWindow = false;
      let resumeDrafts;
      try {
        if (interactive) {
          // Drain draft work while the native editor can still answer recovery requests.
          resumeDrafts = await drafts.pause();
          check();
          frame.contentWindow?.focus();
          frame.contentDocument?.querySelector('canvas')?.focus();
        }
        const approved = await native.requestClose(interactive);
        check();
        closeWindow = approved && interactive;
        if (closeWindow) {
          windowCloseApproved = true;
          frame.inert = true;
          try {
            await drafts.clear();
          } catch (error) {
            host.ui.feedback('The browser could not remove this PhotoCraft draft. ' + error.message);
          }
        }
        return approved;
      } finally {
        if (!closeWindow) {
          resumeDrafts?.();
          autosave.closing(false);
        }
      }
    },
    focus() {
      if (!loaded || !valid() || dialog) return false;
      frame.contentWindow?.focus();
      frame.contentDocument?.querySelector('canvas')?.focus();
      return true;
    },
    dispose
  };
}
