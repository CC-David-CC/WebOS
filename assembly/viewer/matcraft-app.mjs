const extension = '.m';
const maxScriptBytes = 2 * 1024 * 1024;
const digest = /^[a-f0-9]{64}$/;
const utf8 = new TextDecoder('utf-8', {fatal:true, ignoreBOM:true});

function element(tag, properties) {
  return Object.assign(document.createElement(tag), properties);
}

function workspacePath(value) {
  const path = String(value).replace(/^\//, '');
  if (!path.toLowerCase().endsWith(extension) ||
      path.split('/').some(part => !part || part === '.' || part === '..' || /[\\\x00-\x1f]/.test(part))) {
    throw Error('Choose an M script in your Files workspace.');
  }
  return path;
}

function decodeScript(bytes) {
  try {
    return utf8.decode(bytes);
  } catch {
    // Match MatCraft's native reader when a script uses Latin-1.
    return Array.from(new Uint8Array(bytes.buffer, bytes.byteOffset, bytes.byteLength), byte => String.fromCharCode(byte)).join('');
  }
}

export function mount(host) {
  const session = host.session();
  const owner = host.storage.workspaceOwner();
  const abort = new AbortController();
  const {signal} = abort;
  const app = element('section', {className:'window-content matcraft-workspace'});
  const styles = element('link', {rel:'stylesheet', href:new URL('./workspace.css', import.meta.url).href});
  const tools = element('div', {className:'matcraft-tools'});
  const view = element('iframe', {
    className:'matcraft-studio', title:'MatCraft Studio',
    src:new URL('./native/index.html', import.meta.url).href,
  });
  const compactPane = element('section', {className:'matcraft-compact', hidden:true});
  const script = element('textarea', {className:'matcraft-script', spellcheck:false, autocapitalize:'off'});
  script.setAttribute('aria-label', 'M script');
  const output = element('pre', {className:'matcraft-output', textContent:'Run the script to see its output.'});
  output.setAttribute('role', 'log');
  output.setAttribute('aria-label', 'Script output');
  const studioToggle = element('button', {type:'button', textContent:'Studio', hidden:true});
  compactPane.append(script, output);
  const status = element('p', {className:'matcraft-status', textContent:'Starting MatCraft…'});
  status.setAttribute('role', 'status');
  app.append(styles, tools, view, compactPane, status);

  const buttons = [];
  let bridge, context, binding, pending, unregister, poll, lastRun;
  let initialized = false;
  let paused = false;
  let compact = false;
  let preferStudio = false;
  let cleanText = null;
  const touch = matchMedia('(pointer: coarse)');

  function enableTouchTyping() {
    if (touch.matches) host.ui.enableKeyboard?.();
  }

  function showOutput(message) {
    output.textContent = message;
    output.scrollTop = 0;
  }

  function pushCompactScript() {
    const text = script.value;
    const name = binding?.path.split('/').at(-1) || '';
    if (text !== nativeSnapshot().text && !bridge.replace(name, text)) {
      throw Error('The Studio could not load these edits.');
    }
    if (cleanText !== null) bridge.saved(name, cleanText);
  }

  function updateLayout() {
    if (!app.isConnected || pending) return;
    const narrow = app.clientWidth <= 650 || touch.matches && app.clientHeight < 440;
    const next = narrow && !preferStudio;
    if (initialized && next !== compact) {
      if (next) script.value = nativeSnapshot().text;
      else pushCompactScript();
    }
    compact = next;
    app.classList.toggle('matcraft-compact-active', compact);
    compactPane.hidden = !compact;
    studioToggle.hidden = !narrow;
    studioToggle.textContent = compact ? 'Studio' : 'Script view';
    controls();
  }


  function check() {
    if (signal.aborted || session !== host.session() || owner !== host.storage.workspaceOwner() ||
        (context && !context.valid())) {
      throw new DOMException('This Files session ended.', 'AbortError');
    }
    if (paused) throw Error('Files are being transferred.');
  }

  function notify(message) {
    status.textContent = message;
  }

  function controls() {
    const blocked = !initialized || Boolean(pending) || paused;
    for (const button of buttons) button.disabled = blocked;
    view.inert = blocked || compact;
    script.readOnly = blocked;
    studioToggle.disabled = blocked;
  }

  function invoke(action) {
    if (!initialized || pending || paused || signal.aborted) return;
    const operation = Promise.resolve().then(action);
    pending = operation;
    controls();
    operation.catch(error => {
      if (!signal.aborted) {
        notify(error?.status === 409
          ? 'The script changed in Files. Use Save as to keep your edits.'
          : error?.message || String(error));
      }
    }).finally(() => {
      pending = null;
      updateLayout();
    });
  }

  for (const [label, action] of [
    ['New script', () => newScript()],
    ['Open', open],
    ['Save', () => save(false)],
    ['Save as', () => save(true)],
    ['Run script', runScript],
  ]) {
    const button = element('button', {type:'button', textContent:label, disabled:true});
    button.addEventListener('click', () => invoke(action), {signal});
    buttons.push(button);
    tools.append(button);
  }
  tools.append(studioToggle);
  studioToggle.addEventListener('click', () => {
    preferStudio = compact;
    updateLayout();
    if (compact) script.focus();
    else view.focus();
  }, {signal});
  script.addEventListener('pointerdown', enableTouchTyping, {signal});
  const layoutObserver = new ResizeObserver(updateLayout);
  layoutObserver.observe(app);
  controls();

  function nativeSnapshot() {
    return JSON.parse(bridge.snapshot());
  }

  function snapshot() {
    return compact ? {text:script.value, dirty:script.value !== cleanText} : nativeSnapshot();
  }

  function replace(name, text) {
    if (!bridge.replace(name, text)) throw Error('The MatCraft editor could not open this script.');
    const current = nativeSnapshot();
    script.value = current.text;
    cleanText = current.dirty ? null : current.text;
    lastRun = null;
    showOutput('Run the script to see its output.');
  }

  async function acceptDiscard() {
    return !bridge || !snapshot().dirty ||
      host.ui.confirm('Discard unsaved changes to this M script?', {confirmLabel:'Discard', signal});
  }

  function bind(path, sha256) {
    if (path !== null && !digest.test(sha256)) throw Error('Files did not confirm the script revision.');
    binding = path === null ? null : {path, sha256};
    host.desktop.updateAccountFileBinding(host.w, {owner, path, sha256});
  }

  async function newScript(text) {
    check();
    if (!(await acceptDiscard())) return;
    check();
    replace('', text ?? undefined);
    bind(null, null);
    notify('New script');
  }

  async function load(path, expected = null) {
    check();
    const file = await context.files.read(path, {signal});
    check();
    if (!digest.test(file.sha256)) throw Error('Files did not confirm the script revision.');
    if (expected && file.sha256 !== expected) throw Error('The script changed in Files. Open its current revision.');
    if (file.data.byteLength > maxScriptBytes) throw Error('M scripts can be up to 2 MiB.');
    const name = path.split('/').at(-1);
    replace(name, decodeScript(file.data));
    bind(path, file.sha256);
    notify('Opened ' + name);
  }

  async function open() {
    check();
    if (!(await acceptDiscard())) return;
    const picked = await host.storage.pickWorkspaceFile({extensions:[extension], signal});
    if (picked) await load(workspacePath(picked));
  }

  async function save(copy) {
    check();
    const savedText = snapshot().text;
    const data = new Blob([savedText], {type:'text/plain;charset=utf-8'});
    if (data.size > maxScriptBytes) throw Error('M scripts can be up to 2 MiB.');
    let path = binding?.path;
    if (copy || !path) {
      const folder = await host.storage.pickWorkspaceFile({foldersOnly:true, signal});
      if (!folder) return;
      enableTouchTyping();
      const picked = await host.ui.prompt('File name', {
        title:'Save M script', value:path?.split('/').at(-1) || 'Script.m', confirmLabel:'Save', signal,
      });
      if (picked == null) return;
      let name = picked.trim();
      if (!name || /[/\\\x00-\x1f]/.test(name)) throw Error('Enter one script name.');
      if (!name.toLowerCase().endsWith(extension)) name += extension;
      path = workspacePath((folder === '/' ? '' : folder + '/') + name);
    }
    check();
    const receipt = await context.files.write(path, data, path === binding?.path ? binding.sha256 : null, {signal});
    check();
    bind(path, receipt.sha256);
    const name = path.split('/').at(-1);
    cleanText = savedText;
    if (compact) pushCompactScript();
    notify(bridge.saved(name, savedText) ? 'Saved ' + name : 'Saved ' + name + ' · New edits are unsaved');
  }

  function runScript() {
    check();
    if (compact) pushCompactScript();
    lastRun = JSON.parse(bridge.run());
    showOutput(lastRun.ok ? lastRun.output || 'Script finished with no output.' : lastRun.error || 'Script stopped.');
    if (lastRun.ok) notify(compact ? 'Script ran' : 'Script ran · See Command Window');
    else notify(compact ? 'Script stopped' : lastRun.error || 'Script stopped');
  }

  async function waitForStudio() {
    const deadline = performance.now() + 90000;
    while (performance.now() < deadline) {
      check();
      const native = view.contentWindow?.matcraftWorkspace;
      if (native?.ready()) return native;
      const error = view.contentDocument?.querySelector('[data-start-error]');
      if (error) throw Error(error.textContent);
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw Error('MatCraft Studio took too long to start.');
  }

  const ready = (async () => {
    context = await host.storage.workspaceFileContext();
    check();
    if (context.owner !== owner) throw Error('This editor belongs to another Files workspace.');
    bridge = await waitForStudio();
    unregister = context.registerFileWriter?.(async () => {
      if (pending) await pending;
      if (snapshot().dirty) throw Error('Save your M script before transferring Files.');
      paused = true;
      controls();
      return () => { paused = false; controls(); };
    });
    const file = host.w.launchContext;
    if (file) {
      if (file.storage !== 'account' || file.owner !== owner) throw Error('Open an M script from your Files.');
      await load(workspacePath(file.path), file.restore ? null : file.sha256);
    } else {
      const current = nativeSnapshot();
      script.value = current.text;
      cleanText = current.text;
      notify('MatCraft is ready');
    }
    initialized = true;
    updateLayout();
    poll = setInterval(() => {
      if (signal.aborted || pending || paused) return;
      try {
        check();
        const request = bridge.request();
        if (!request) return;
        const action = JSON.parse(request);
        if (action.kind === 'new') invoke(() => newScript(action.text));
        if (action.kind === 'open') invoke(open);
        if (action.kind === 'save') invoke(() => save(false));
      } catch (error) {
        if (!signal.aborted && error?.name !== 'AbortError') notify(error?.message || String(error));
      }
    }, 125);
  })();
  ready.catch(error => { if (!signal.aborted) notify(error?.message || String(error)); });

  return {
    element:app,
    ready,
    focus:() => compact ? script.focus() : view.focus(),
    inspect:() => ({path:binding?.path ?? null, dirty:initialized && snapshot().dirty, lastRun}),
    async requestClose() {
      if (pending) await pending.catch(() => {});
      return acceptDiscard();
    },
    dispose() {
      abort.abort();
      layoutObserver.disconnect();
      clearInterval(poll);
      unregister?.();
    },
  };
}
