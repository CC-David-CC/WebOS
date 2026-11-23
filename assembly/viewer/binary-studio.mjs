const digest = /^[a-f0-9]{64}$/;

function create(tag, properties) {
  return Object.assign(document.createElement(tag), properties);
}

export function mountBinaryStudio(host, {name, extension, openExtensions, imports}) {
  const session = host.session();
  const owner = host.storage.workspaceOwner();
  const controller = new AbortController();
  const {signal} = controller;
  const element = create('section', {className:'window-content binary-studio'});
  const styles = create('link', {rel:'stylesheet', href:new URL('./workspace.css', import.meta.url).href});
  const tools = create('div', {className:'binary-studio-tools'});
  const view = create('iframe', {
    className:'binary-studio-native', title:name,
    src:new URL('./native/index.html?webos', import.meta.url).href,
  });
  const status = create('p', {className:'binary-studio-status', textContent:'Starting ' + name + '…'});
  status.setAttribute('role', 'status');
  element.append(styles, tools, view, status);
  const buttons = [];
  let bridge, context, binding, pending, unregister, poll, project;
  let pendingAudio;
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
  const saveAudioButton = create('button', {type:'button', textContent:'Save WAV', hidden:true});
  saveAudioButton.addEventListener('click', () => invoke(saveAudio), {signal});
  buttons.push(saveAudioButton);
  tools.append(saveAudioButton);
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
    host.desktop.updateAccountFileBinding(host.w, {owner, path, sha256});
  }

  function currentProject() {
    const next = bridge.project_identity();
    if (next !== project) {
      project = next;
      if (binding) bind(null, null);
    }
    return next;
  }

  function acceptDiscard() {
    return !bridge?.project_dirty() ||
      host.ui.confirm('Discard unsaved changes to this project?', {confirmLabel:'Discard', signal});
  }

  async function read(path) {
    check();
    const file = await context.files.read(path, {signal});
    check();
    if (!digest.test(file.sha256)) throw Error('Files did not confirm the project revision.');
    return file;
  }

  async function load(path, expected = null) {
    const file = await read(path);
    if (expected && file.sha256 !== expected) throw Error('The project changed in Files. Open its current revision.');
    const fileName = path.split('/').at(-1);
    if (!(await bridge.open_project(fileName, new Uint8Array(file.data)))) {
      throw Error(name + ' could not open this project.');
    }
    check();
    project = bridge.project_identity();
    bind(path, file.sha256);
    notify('Opened ' + fileName);
  }

  async function open() {
    check();
    if (!(await acceptDiscard())) return;
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

  async function saveAudio() {
    check();
    const output = pendingAudio;
    if (!output) return;
    const folder = await host.storage.pickWorkspaceFile({foldersOnly:true, signal});
    if (!folder) return;
    const chosen = await host.ui.prompt('File name', {
      title:'Save WAV export', value:output.name, confirmLabel:'Save', signal,
    });
    if (chosen == null) return;
    let fileName = chosen.trim();
    if (!fileName || /[/\\\x00-\x1f]/.test(fileName)) throw Error('Enter one WAV file name.');
    if (!fileName.toLowerCase().endsWith('.wav')) fileName += '.wav';
    const path = workspacePath((folder === '/' ? '' : folder + '/') + fileName, ['.wav']);
    check();
    try {
      await context.files.write(path, new Blob([output.bytes], {type:'audio/wav'}), null, {signal});
    } catch (error) {
      if (error?.status === 409) throw Error('A WAV with that name already exists. Choose another name.');
      throw error;
    }
    check();
    pendingAudio = undefined;
    saveAudioButton.hidden = true;
    notify('Exported ' + fileName);
  }

  async function save(saveAs, copy) {
    check();
    const savedProject = currentProject();
    let path = binding?.path;
    if (saveAs || !path || !path.toLowerCase().endsWith(extension)) {
      const folder = await host.storage.pickWorkspaceFile({foldersOnly:true, signal});
      if (!folder) return;
      const suggested = path?.split('/').at(-1);
      const defaultName = suggested
        ? suggested.slice(0, suggested.lastIndexOf('.')) + (copy ? ' copy' : '') + extension
        : name + (copy ? ' copy' : '') + extension;
      const chosen = await host.ui.prompt('File name', {
        title:'Save ' + name + ' project', value:defaultName, confirmLabel:'Save', signal,
      });
      if (chosen == null) return;
      let fileName = chosen.trim();
      if (!fileName || /[/\\\x00-\x1f]/.test(fileName)) throw Error('Enter one project name.');
      if (!fileName.toLowerCase().endsWith(extension)) fileName += extension;
      path = workspacePath((folder === '/' ? '' : folder + '/') + fileName, [extension]);
    }
    check();
    if (savedProject !== currentProject()) throw Error('The open project changed. Save the current project again.');
    if (copy && path === binding?.path) throw Error('Choose a different file name for the copy.');
    const snapshot = bridge.project_snapshot();
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
      if (bridge.project_dirty()) throw Error('Save your ' + name + ' project before transferring Files.');
      paused = true;
      controls();
      return () => { paused = false; controls(); };
    });
    const file = host.w.launchContext;
    if (file) {
      if (file.storage !== 'account' || file.owner !== owner) throw Error('Open a project from your Files.');
      await load(workspacePath(file.path, openExtensions), file.restore ? null : file.sha256);
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
          const output = bridge.take_audio_export?.();
          if (!ArrayBuffer.isView(output?.bytes) || !output.bytes.byteLength) {
            throw Error(name + ' did not produce a WAV.');
          }
          pendingAudio = output;
          saveAudioButton.hidden = false;
          invoke(saveAudio);
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
    focus:() => view.focus(),
    inspect:() => ({path:binding?.path ?? null, dirty:initialized && bridge.project_dirty()}),
    async requestClose() {
      if (pending) await pending.catch(() => {});
      return acceptDiscard();
    },
    dispose() {
      controller.abort();
      clearInterval(poll);
      unregister?.();
    },
  };
}
