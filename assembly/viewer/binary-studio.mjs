const digest = /^[a-f0-9]{64}$/;
const guestEditorStorage = new WeakMap();

function create(tag, properties) {
  return Object.assign(document.createElement(tag), properties);
}

export function mountBinaryStudio(host, {name, extension, openExtensions, imports, multipleProjects = false, fileExport, sourceArchive, scopedStorage = false, nativeURL = "./native/index.html?webos", saveExtensions = [extension]}) {
  const session = host.session();
  const owner = host.storage.workspaceOwner();
  const controller = new AbortController();
  const {signal} = controller;
  const element = create('section', {className:'window-content binary-studio'});
  const styles = create('link', {rel:'stylesheet', href:new URL('./workspace.css', import.meta.url).href});
  const tools = create('div', {className:'binary-studio-tools'});
  const view = create('iframe', {
    className:'binary-studio-native', title:name,
    src:new URL(nativeURL, import.meta.url).href,
  });
  if (scopedStorage) {
    if (session.public.kind === 'anonymous') {
      if (!guestEditorStorage.has(session)) {
        guestEditorStorage.set(session, {local:new Map(), session:new Map()});
      }
      Object.defineProperty(view, 'webosGuestStorage', {value:guestEditorStorage.get(session)});
    }
    view.name = JSON.stringify({
      owner, guest:session.public.kind === 'anonymous', document:String(host.w.id),
    });
  }
  const status = create('p', {className:'binary-studio-status', textContent:'Starting ' + name + '…'});
  status.setAttribute('role', 'status');
  element.append(styles, tools, view, status);
  const buttons = [];
  let bridge, context, binding, pending, unregister, poll, project;
  let pendingExport;
  const exportSpec = fileExport ?? {
    label:'Save WAV', title:'Save WAV export', extension:'.wav', mime:'audio/wav',
    take:'take_audio_export',
  };
  const projectBindings = multipleProjects ? new Map() : null;
  let initialized = false;
  let paused = false;

  function check() {
    if (signal.aborted || session !== host.session() || owner !== host.storage.workspaceOwner() ||
        (context && !context.valid())) throw new DOMException('This Files session ended.', 'AbortError');
    if (paused) throw Error('Files are being transferred.');
  }

  function controls() {
    const blocked = !initialized || Boolean(pending) || paused;
    for (const button of buttons) button.disabled = blocked;
    view.inert = blocked;
  }

  function notify(message) {
    status.textContent = message;
    bridge?.workspace_status?.(message);
  }

  function invoke(action) {
    if (!initialized || pending || paused || signal.aborted) return;
    pending = Promise.resolve().then(action);
    controls();
    pending.catch(error => {
      if (signal.aborted || error?.name === 'AbortError') return;
      notify(error?.status === 409
        ? 'The project changed in Files. Use Save as to keep your edits.'
        : error?.message || String(error));
    }).finally(() => {
      bridge?.cancel_file_request?.();
      pending = null;
      controls();
    });
  }

  for (const [label, action] of [
    ['Open', open],
    ...(imports ? [['Import', importFile]] : []),
    ['Save', () => save(false, false)],
    ['Save as', () => save(true, false)],
  ]) {
    const button = create('button', {type:'button', textContent:label, disabled:true});
    button.addEventListener('click', () => invoke(action), {signal});
    buttons.push(button);
    tools.append(button);
  }
  const exportButton = create('button', {type:'button', textContent:exportSpec.label, hidden:!exportSpec.direct});
  exportButton.addEventListener('click', () => invoke(saveExport), {signal});
  buttons.push(exportButton);
  tools.append(exportButton);
  if (sourceArchive) tools.append(create('a', {textContent:'Source',download:'',href:new URL(sourceArchive,import.meta.url).href}));
  controls();

  function workspacePath(value, allowed) {
    const path = String(value).replace(/^\//, '');
    if (!allowed.some(suffix => path.toLowerCase().endsWith(suffix)) ||
        path.split('/').some(part => !part || part === '.' || part === '..' || /[\\\x00-\x1f]/.test(part))) {
      throw Error('Choose a supported file in your workspace.');
    }
    return path;
  }

  function bind(path, sha256) {
    if (path !== null && !digest.test(sha256)) throw Error('Files did not confirm the project revision.');
    binding = path === null ? null : {path, sha256};
    if (projectBindings) {
      if (binding) projectBindings.set(project, binding);
      else projectBindings.delete(project);
    }
    host.desktop.updateAccountFileBinding(host.w, {owner, path, sha256});
  }

  function currentProject() {
    const next = bridge.project_identity();
    if (next !== project) {
      project = next;
      const restored = projectBindings?.get(project);
      if (binding || restored) bind(restored?.path ?? null, restored?.sha256);
    }
    return next;
  }

  function acceptDiscard(all = false) {
    const dirty = all && bridge?.workspace_dirty ? bridge.workspace_dirty() : bridge?.project_dirty();
    return !dirty ||
      host.ui.confirm('Discard unsaved changes to this project?', {confirmLabel:'Discard', signal});
  }

  async function read(path) {
    check();
    const file = await context.files.read(path, {signal});
    check();
    if (!digest.test(file.sha256)) throw Error('Files did not confirm the project revision.');
    return file;
  }

  function focusEditor() {
    const canvas = view.contentDocument?.querySelector('body > canvas[tabindex], main > canvas[tabindex]');
    (canvas || view).focus({preventScroll:true});
  }

  async function load(path, expected = null) {
    const file = await read(path);
    if (expected && file.sha256 !== expected) throw Error('The project changed in Files. Open its current revision.');
    const fileName = path.split('/').at(-1);
    const bytes = new Uint8Array(file.data);
    if (bridge.would_replace_dirty?.(fileName, bytes) &&
        !await host.ui.confirm('Replace the edited manuscript with the copy in Files?', {confirmLabel:'Replace', signal})) return;
    if (!(await bridge.open_project(fileName, bytes))) {
      throw Error(name + ' could not open this project.');
    }
    check();
    project = bridge.project_identity();
    bind(path, file.sha256);
    notify('Opened ' + fileName);
    focusEditor();
  }

  async function open() {
    check();
    if (!multipleProjects && !(await acceptDiscard())) return;
    const picked = await host.storage.pickWorkspaceFile({extensions:openExtensions, signal});
    if (picked) await load(workspacePath(picked, openExtensions));
  }

  async function importFile() {
    check();
    const picked = await host.storage.pickWorkspaceFile({extensions:imports, signal});
    if (!picked) return;
    const path = workspacePath(picked, imports);
    const file = await read(path);
    const fileName = path.split('/').at(-1);
    if ((await bridge.import_file(fileName, new Uint8Array(file.data))) === false) {
      throw Error(name + ' could not import this file.');
    }
    check();
    notify('Imported ' + fileName);
  }

  async function saveExport() {
    check();
    const output = pendingExport ?? (exportSpec.direct ? await bridge[exportSpec.take]() : null);
    if (!output) return;
    const folder = await host.storage.pickWorkspaceFile({foldersOnly:true, signal});
    if (!folder) return;
    const chosen = await host.ui.prompt('File name', {
      title:exportSpec.title, value:output.name, confirmLabel:'Save', signal,
    });
    if (chosen == null) return;
    let fileName = chosen.trim();
    if (!fileName || /[/\\\x00-\x1f]/.test(fileName)) throw Error('Enter one export file name.');
    if (!fileName.toLowerCase().endsWith(exportSpec.extension)) fileName += exportSpec.extension;
    const path = workspacePath((folder === '/' ? '' : folder + '/') + fileName, [exportSpec.extension]);
    check();
    try {
      const receipt = await context.files.write(path, new Blob([output.bytes], {type:exportSpec.mime}), null, {signal});
      if (exportSpec.refreshMirror) {
        check();
        const mirror = await host.storage.workspaceMirrorContext();
        try {
          await mirror.files.sync();
          check();
          const visible = await mirror.files.stat('/' + path, {signal});
          if (visible.sha256 !== receipt.sha256 || visible.status === 'conflict') {
            throw Error('The browser mirror has a different revision.');
          }
        } catch (error) {
          check();
          notify('Saved ' + fileName + ' in Files. Digital Logic will see it after the browser mirror syncs.');
          return;
        }
      }
    } catch (error) {
      if (error?.status === 409) throw Error('A file with that name already exists. Choose another name.');
      throw error;
    }
    check();
    pendingExport = undefined;
    exportButton.hidden = !exportSpec.direct;
    notify('Exported ' + fileName);
  }

  async function save(saveAs, copy) {
    check();
    const savedProject = currentProject();
    let path = binding?.path;
    if (saveAs || !path || !saveExtensions.some(suffix => path.toLowerCase().endsWith(suffix))) {
      const folder = await host.storage.pickWorkspaceFile({foldersOnly:true, signal});
      if (!folder) return;
      const suggested = path?.split('/').at(-1);
      const defaultName = suggested
        ? (copy ? suggested.replace(/(\.[^.]+)$/, ' copy$1') : suggested)
        : name + (copy ? ' copy' : '') + extension;
      const chosen = await host.ui.prompt('File name', {
        title:'Save ' + name + ' project', value:defaultName, confirmLabel:'Save', signal,
      });
      if (chosen == null) return;
      let fileName = chosen.trim();
      if (!fileName || /[/\\\x00-\x1f]/.test(fileName)) throw Error('Enter one project name.');
      if (!saveExtensions.some(suffix => fileName.toLowerCase().endsWith(suffix))) fileName += extension;
      path = workspacePath((folder === '/' ? '' : folder + '/') + fileName, saveExtensions);
    }
    check();
    if (savedProject !== currentProject()) throw Error('The open project changed. Save the current project again.');
    if (copy && path === binding?.path) throw Error('Choose a different file name for the copy.');
    const snapshot = await bridge.project_snapshot(path);
    check();
    if (!ArrayBuffer.isView(snapshot.bytes) || typeof snapshot.revision !== 'string' ||
        snapshot.bytes.byteLength === 0) throw Error(name + ' could not prepare a project to save.');
    const data = new Blob([snapshot.bytes], {type:'application/octet-stream'});
    const receipt = await context.files.write(path, data, path === binding?.path ? binding.sha256 : null, {signal});
    check();
    const fileName = path.split('/').at(-1);
    if (copy || savedProject !== currentProject()) {
      notify('Saved ' + fileName);
      return;
    }
    bind(path, receipt.sha256);
    const clean = bridge.project_saved(snapshot.revision, fileName);
    notify('Saved ' + fileName + (clean ? '' : ' · New edits are unsaved'));
  }

  const ready = (async () => {
    context = await host.storage.workspaceFileContext();
    check();
    if (context.owner !== owner) throw Error('This editor belongs to another Files workspace.');
    const deadline = performance.now() + 90000;
    while (performance.now() < deadline) {
      check();
      bridge = view.contentWindow?.wasmBindings;
      if (bridge?.workspace_ready()) break;
      const error = view.contentDocument?.querySelector('[data-start-error]');
      if (error) throw Error(error.textContent);
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    if (!bridge?.workspace_ready()) throw Error(name + ' took too long to start.');
    project = bridge.project_identity();
    unregister = context.registerFileWriter?.(async () => {
      if (pending) await pending;
      if ((bridge.workspace_dirty ?? bridge.project_dirty)()) throw Error('Save your ' + name + ' project before transferring Files.');
      paused = true;
      controls();
      return () => { paused = false; controls(); };
    });
    const file = host.w.launchContext;
    if (file) {
      if (file.storage !== 'account' || file.owner !== owner) throw Error('Open a project from your Files.');
      try {
        await load(workspacePath(file.path, openExtensions), file.restore ? null : file.sha256);
      } catch (error) {
        check();
        bind(null, null);
        notify(error?.message || String(error));
      }
    } else notify(name + ' is ready');
    initialized = true;
    controls();
    poll = setInterval(() => {
      if (signal.aborted || pending || paused) return;
      try {
        check();
        currentProject();
        const request = bridge.take_file_request();
        if (request === 'open') invoke(open);
        if (request === 'import' && imports) invoke(importFile);
        if (request === 'save') invoke(() => save(false, false));
        if (request === 'save-as') invoke(() => save(true, false));
        if (request === 'save-copy') invoke(() => save(true, true));
        if (request === 'export') {
          const output = bridge[exportSpec.take]?.();
          if (!ArrayBuffer.isView(output?.bytes) || !output.bytes.byteLength) {
            throw Error(name + ' did not produce an export.');
          }
          pendingExport = output;
          exportButton.hidden = false;
          invoke(saveExport);
        }
      } catch (error) {
        if (error?.name !== 'AbortError') notify(error?.message || String(error));
      }
    }, 125);
  })();
  ready.catch(error => { if (!signal.aborted) notify(error?.message || String(error)); });

  return {
    element,
    ready,
    focus:focusEditor,
    inspect:() => ({path:binding?.path ?? null, dirty:initialized && bridge.project_dirty()}),
    async requestClose() {
      if (pending) await pending.catch(() => {});
      return acceptDiscard(true);
    },
    dispose() {
      controller.abort();
      clearInterval(poll);
      unregister?.();
    },
  };
}
