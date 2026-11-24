import {connectCraftAccount} from './craft-account-native.mjs';
import {trackCraftAutosave} from './craft-account-autosave.mjs';
import {trackCraftDraft} from './craft-account-recovery.mjs';
import {createCraftSession} from './craft-account-session.mjs';
import {createCraftStorage, MAX_BYTES, craftProjectPath} from './craft-account-storage.mjs';

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

/** Mount a native layer editor in its own classic Desktop account window. */
export function mountCraftAccount(host, {app, name, extension, recovery, deviceImport = false, reviewWindowClose = false, forceWebGL = false,
  setupOriginals, commands = scopedCommands, accountControls = false, artworkExtensions, accountAutosave = true, accountOpenTimeoutMs, legacyExtensions = []}) {
  const extensions = [extension,...legacyExtensions];
  const projectPath = path => craftProjectPath(path, extension, legacyExtensions);
  const element = document.createElement('div');
  element.className = `window-content webos-${app}`;
  element.style.display = 'flex';
  element.style.flexDirection = 'column';
  const status = document.createElement('div');
  status.setAttribute('role', 'status');
  status.textContent = `Opening ${name}…`;
  status.style.flex = '1';
  const appBar = document.createElement('div');
  appBar.style.display = 'flex';
  const autoToggle = document.createElement('button');
  autoToggle.type = 'button';
  autoToggle.textContent = 'AutoSave';
  autoToggle.hidden = true;
  let openLocal;
  const controls = [];
  const frame = document.createElement('iframe');
  frame.title = `${name} editor`;
  frame.style.flex = '1';
  frame.style.minHeight = '0';
  frame.style.border = '0';
  frame.inert = true;

  const abort = new AbortController();
  const session = host.session();
  const guest = session?.public.kind === 'anonymous';
  const currentOwner = guest ? host.storage.workspaceOwner : host.storage.signedInSubject;
  const pickFile = guest ? host.storage.pickWorkspaceFile : host.storage.pickAccountFile;
  const instanceId = !guest && typeof host.registerAgentView === 'function' ? crypto.randomUUID() : null;
  let native, storage, context, dialog, journal, drafts, autosave, accountSession, windowLease;
  let loaded = false, windowCloseApproved = false;
  let autosaveKey, autoEnabled = false;
  let lastDialog = 0n;
  let agentPath, bindingId;
  const valid = () => !abort.signal.aborted && !host.signal.aborted && host.session() === session &&
    host.desktop.windows.includes(host.w) && currentOwner() === session?.public.sub && context?.valid();
  const check = () => {
    if (!valid()) throw new DOMException(`${name} account view closed.`, 'AbortError');
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
      host.ui.feedback(`${name} needs a named file no larger than 128 MiB.`);
      return;
    }
    const window = host.desktop.launch(app, `${file.name} — ${name}`);
    if (!window) return;
    window.ownerSub = context.owner;
    localImports.set(window, {file, session});
  }

  if (deviceImport) {
    openLocal = document.createElement('button');
    openLocal.type = 'button';
    openLocal.textContent = 'Open from device';
    openLocal.hidden = true;
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.hidden = true;
    appBar.append(status, openLocal, autoToggle, fileInput);
    openLocal.addEventListener('click', () => { if (loaded && valid()) fileInput.click(); });
    fileInput.addEventListener('change', () => {
      const file = fileInput.files?.[0];
      fileInput.value = '';
      if (file) launchLocal(file);
    });
  } else appBar.append(status, autoToggle);

  if (accountControls) {
    for (const label of ['Open','Save','Save As']) {
      const control = document.createElement('button');
      control.type = 'button';
      control.textContent = label;
      control.hidden = true;
      control.addEventListener('click', async () => {
        if (!loaded || !valid() || dialog) return;
        const controller = new AbortController();
        dialog = controller;
        for (const button of controls) button.disabled = true;
        try {
          if (label === 'Open') await chooseProject({path:null},controller.signal);
          else await accountSession.saveManually({saveAs:label === 'Save As',signal:controller.signal});
        } catch (error) {
          if (valid()) message(error.message);
        } finally {
          dialog = null;
          for (const button of controls) button.disabled = false;
        }
      });
      controls.push(control);
      appBar.insertBefore(control,autoToggle);
    }
  }

  function setAutosave(value) {
    autoEnabled = value;
    autoToggle.setAttribute('aria-pressed', String(value));
    autoToggle.title = value ? 'Account AutoSave is on' : 'Account AutoSave is off';
    autosave.enabled(value);
  }
  autoToggle.addEventListener('click', () => {
    if (guest || !accountAutosave || !loaded || !valid()) return;
    setAutosave(!autoEnabled);
    try {
      document.defaultView.localStorage?.setItem(autosaveKey, autoEnabled ? 'on' : 'off');
    } catch {
      host.ui.feedback(`This browser could not remember the ${name} AutoSave setting.`);
    }
  });

  async function save(packet, automatic = false) {
    if (!loaded || !valid()) return {error:Error(`The ${name} account editor is closed.`)};
    message(guest ? 'Saving in this tab…' : 'Saving to your account…');
    try {
      check();
      const writing = storage.save(packet, native.acknowledge);
      accountSession.observe();
      const binding = await writing;
      bind(binding);
      message(guest ? `Saved in this tab: ${binding.path}` : '');
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
      accountSession.observe();
    }
  }

  async function chooseProject(packet, signal) {
    const picked = packet.path === null ? await pickFile({extensions, signal}) : null;
    check();
    if (!loaded || signal.aborted) return {outcome:'cancelled'};
    if (packet.path === null && picked === null) return {outcome:'cancelled'};
    if (packet.path === null && (typeof picked !== 'string' || !picked.startsWith('/'))) throw Error('Invalid account project selection.');
    const path = projectPath(packet.path === null ? picked.slice(1) : packet.path);
    const resource = {owner:context.owner, path};
    if (host.desktop.activateAccountFile(resource, app)) return {outcome:'opened'};
    const {sha256} = await context.files.version(path, {signal});
    check();
    if (!loaded || signal.aborted) return {outcome:'cancelled'};
    host.desktop.openAccountFile(app, {...resource, sha256});
    return {outcome:'opened'};
  }

  async function chooseDestination(suggested, signal) {
    const folder = await pickFile({foldersOnly:true, signal});
    check();
    if (!loaded || signal.aborted || folder === null) return {outcome:'cancelled'};
    if (typeof folder !== 'string' || !folder.startsWith('/')) throw Error('Invalid account folder selection.');
    const input = await host.ui.prompt('File name', {
      title:`Save ${name} project`, value:suggested.split('/').pop(), confirmLabel:'Save', signal
    });
    check();
    if (!loaded || signal.aborted || input === null) return {outcome:'cancelled'};
    const filename = input.trim();
    if (!filename || filename.includes('/') || filename === '.' || filename === '..') throw Error('Enter a project file name.');
    const suffix = extensions.some(suffix=>filename.toLowerCase().endsWith(suffix)) ? '' : extension;
    return {outcome:'destination', path:projectPath((folder === '/' ? '' : folder.slice(1) + '/') + filename + suffix)};
  }

  async function chooseArtwork(signal) {
    const picked = await pickFile({extensions:artworkExtensions, signal});
    check();
    if (!loaded || signal.aborted || picked === null) return {outcome:'cancelled'};
    if (typeof picked !== 'string' || !picked.startsWith('/')) throw Error('Invalid account artwork selection.');
    const filePath = picked.slice(1);
    const expected = await context.files.version(filePath,{signal});
    check();
    if (!loaded || signal.aborted) return {outcome:'cancelled'};
    const graphic = await context.files.read(filePath,{signal});
    check();
    if (!loaded || signal.aborted) return {outcome:'cancelled'};
    if (!/^[a-f0-9]{64}$/.test(expected?.sha256) || graphic?.sha256 !== expected.sha256 ||
        !(graphic.data instanceof Uint8Array) || !graphic.data.byteLength || graphic.data.byteLength > MAX_BYTES) {
      throw Error('The account artwork changed or could not be read.');
    }
    return {outcome:'asset',name:filePath.split('/').at(-1),bytes:graphic.data.slice().buffer};
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
        const window = host.desktop.launch(app);
        if (!window) throw Error(`${name} is unavailable.`);
        window[app + 'NewSettings'] = packet.settings;
        answer = {outcome:'opened'};
      } else if (packet.operation === 'open') answer = await chooseProject(packet, controller.signal);
      else if (packet.operation === 'save' && typeof packet.suggested === 'string' && packet.suggested.length <= 2048) {
        answer = await chooseDestination(packet.suggested, controller.signal);
      } else if (packet.operation === 'relink' && artworkExtensions) {
        answer = await chooseArtwork(controller.signal);
      } else throw Error(`Invalid ${name} dialog request.`);
    } catch (error) {
      answer = {outcome:'failed', message:String(error.message || `${name} dialog failed.`).slice(0, 250)};
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
    context = guest ? await host.storage.workspaceFileContext() : await host.storage.accountFileContext();
    check();
    journal = guest ? null : recovery.journal(host, context, valid);
    const draft = await journal?.load();
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

    const url = new URL(`${app}/index.html`, document.baseURI);
    url.searchParams.set('host', 'webos-account');
    let originalStore;
    if (setupOriginals) {
      const {scope, store} = await setupOriginals({context, origin:url.origin, valid, signal:abort.signal});
      check();
      url.searchParams.set('scope', scope);
      originalStore = store;
    } else {
      url.searchParams.set('profile', context.owner);
    }
    if (forceWebGL) url.searchParams.set('webgl', '1');
    storage = createCraftStorage({name, extension, legacyExtensions, files:context.files, operations:host.documentOperations, valid});
    native = connectCraftAccount(frame, {
      app, name, url, signal:abort.signal, originalStore, accountOpenTimeoutMs, onSave:packet => void save(packet), onDialog:handleDialog,
      onLocalFile:deviceImport ? launchLocal : undefined,
      onProjectState(packet) {
        drafts?.receive(packet);
        autosave?.receive(packet);
        accountSession?.receive(packet);
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
        accountSession?.observe();
        message(reason);
      }
    });
    drafts = trackCraftDraft({
      journal, native, storage, valid:() => loaded && valid(),
      onError(error) { message(`${name} could not update the browser draft. ` + error.message); }
    });
    autosave = trackCraftAutosave({
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
    accountSession = createCraftSession({
      app, appName:name, native, storage, drafts, autosave, frame, signal:abort.signal, valid, loaded:() => loaded,
      documentName:() => host.w.title || `The ${name} project`,
      async choosePath(suggested = 'Untitled' + extension, signal = abort.signal) {
        const result = await chooseDestination(suggested,signal);
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
      const duplicate = draft.path !== null && !!host.desktop.accountFileLocation({owner:context.owner, path:draft.path}, app, host.w);
      const recoveryBinding = await storage.restore(draft, (path, bytes) => native.start(path, bytes, null, true),
        {asCopy:duplicate || host.w[app + 'RecoveryAsCopy'] === true, signal:abort.signal});
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
        if (source.session !== session) throw Error(`The account changed before ${name} could import the file.`);
        const bytes = await source.file.arrayBuffer();
        check();
        // Native import questions are part of the opening flow.
        frame.inert = false;
        storage.attachBlank(await native.importFile(source.file.name, bytes));
      } else {
        const settings = host.w[app + 'NewSettings'];
        delete host.w[app + 'NewSettings'];
        storage.attachBlank(await native.start(null, null, settings));
      }
    }
    check();
    loaded = true;
    frame.inert = false;
    accountSession.observe();
    let value = false;
    if (accountAutosave && !guest) {
      autosaveKey = `webos:${app}:account-autosave:` + encodeURIComponent(context.owner);
      try { value = document.defaultView.localStorage?.getItem(autosaveKey) === 'on'; } catch { /* Use this window's default. */ }
    }
    setAutosave(value);
    autoToggle.hidden = guest || !accountAutosave;
    for (const control of controls) control.hidden = false;
    if (openLocal) openLocal.hidden = false;
    message(guest ? (resource ? `Opened in this tab: ${resource.path}` : 'New temporary project.') : recoveryMessage);
    drafts.schedule();
    if (instanceId) host.registerAgentView({
      windowId:host.w.id, name, signal:abort.signal,
      instanceId, sessionId:session.public.sid, accountId:context.owner,
      commands, bindingId:() => agentDocument()?.bindingId,
      snapshot:agentDocument,
      execute(request, authorize) {
        check();
        const target = agentDocument();
        if (!target || ['instanceId','sessionId','documentId','resourceId'].some(key => request[key] !== target[key])) {
          throw Error(`The ${name} document binding changed.`);
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
    accountSession?.dispose();
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
      snapshot:() => accountSession?.snapshot() ?? {revision:0,dirty:false,pending:true},
      subscribe:listener => accountSession?.subscribe(listener) ?? (() => {}),
      async quiesce() { await ready; return accountSession.quiesce(); },
      async commitClose() {
        if (windowCloseApproved) return;
        try {
          await accountSession.commitClose();
        } catch (error) {
          windowLease?.release();
          throw error;
        } finally {
          windowLease = null;
        }
      },
    }),
    async requestClose({scope = 'window'} = {}) {
      if (accountControls && dialog) return false;
      if (!loaded && scope === 'window') {
        windowCloseApproved = true;
        return true;
      }
      check();
      if (scope === 'session') {
        await ready;
        return accountSession.approve();
      }
      const interactive = scope === 'window';
      if (interactive && reviewWindowClose) {
        if (!await accountSession.approve('window')) return false;
        windowLease = await accountSession.quiesce('window');
        return true;
      }
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
            host.ui.feedback(`The browser could not remove this ${name} draft. ` + error.message);
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
