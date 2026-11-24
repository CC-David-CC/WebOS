import initialize, {PracticeWindow} from './i_success.js';

const suffix = '.isuccess';
const limit = 128 * 1024;
let initialized;

export function mount(host) {
  const element = document.createElement('section');
  element.className = 'window-content practice-workspace';
  const tools = document.createElement('div');
  tools.className = 'practice-toolbar';
  const status = document.createElement('span');
  status.setAttribute('role', 'status');
  const canvas = document.createElement('canvas');
  canvas.tabIndex = 0;
  canvas.setAttribute('aria-label', 'I-SUCCESS practice');
  const open = document.createElement('button');
  const save = document.createElement('button');
  const saveAs = document.createElement('button');
  for (const [button, label] of [[open,'Open'],[save,'Save'],[saveAs,'Save as']]) {
    button.type = 'button';
    button.textContent = label;
    tools.append(button);
  }
  tools.append(status);
  element.append(tools, canvas);
  const session = host.session();
  const owner = session.public.sub;
  let releasePractice;
  let context, practice, binding, clean, disposed = false, pending = false;

  function check() {
    if (disposed || host.signal.aborted || host.session() !== session || !context.valid() || owner !== context.owner) {
      throw new DOMException('Practice session closed.', 'AbortError');
    }
  }
  function bind(path, sha256, content) {
    host.desktop.updateAccountFileBinding(host.w, {owner, path, sha256});
    binding = {path, sha256};
    clean = content;
  }
  function buttons(disabled) {
    open.disabled = save.disabled = saveAs.disabled = disabled;
  }
  async function load(path, expected) {
    check();
    const file = await context.files.read(path);
    check();
    if (expected && expected !== file.sha256) throw Error('This practice file changed. Open its current revision from Files.');
    const bytes = file.data instanceof Blob ? await file.data.arrayBuffer() : file.data;
    check();
    if (bytes.byteLength > limit) throw Error('Practice files must be smaller than 128 KiB.');
    practice.load(new TextDecoder('utf-8', {fatal:true}).decode(bytes));
    bind(path, file.sha256, practice.document());
    status.textContent = 'Opened ' + path.split('/').pop();
    canvas.focus();
  }
  async function openDocument() {
    const selection = await host.storage.pickWorkspaceFile({extensions:[suffix], signal:host.signal});
    if (!selection) return;
    check();
    if (practice.document() !== clean && !await host.ui.confirm('Discard changes to this practice session?', {confirmLabel:'Discard', signal:host.signal})) return;
    await load(selection.slice(1));
  }
  async function chooseSavePath() {
    const folder = await host.storage.pickWorkspaceFile({foldersOnly:true, signal:host.signal});
    if (!folder) return null;
    const name = await host.ui.prompt('File name', {title:'Save practice session', value:binding?.path.split('/').pop() || 'Practice'+suffix, confirmLabel:'Save', signal:host.signal});
    if (name == null) return null;
    const trimmed = name.trim();
    if (!trimmed || trimmed === '.' || trimmed === '..' || /[\\/\u0000-\u001f]/.test(trimmed)) throw Error('Choose a file name without a folder separator.');
    return [folder.slice(1),trimmed.toLowerCase().endsWith(suffix) ? trimmed : trimmed + suffix].filter(Boolean).join('/');
  }
  async function saveDocument(copy) {
    let path = !copy && binding?.path;
    if (!path) path = await chooseSavePath();
    if (!path) return;
    check();
    let expected = binding?.path === path ? binding.sha256 : null;
    if (!expected) {
      let existing;
      try { existing = await context.files.version(path); } catch (error) { if (error.status !== 404) throw error; }
      check();
      if (existing) {
        if (!await host.ui.confirm('Replace '+path+'?',{confirmLabel:'Replace',signal:host.signal})) return;
        expected = existing.sha256;
      }
    }
    check();
    const content = practice.document();
    const body = new Blob([content],{type:'text/plain;charset=utf-8'});
    if (body.size > limit) throw Error('Practice files must be smaller than 128 KiB.');
    const result = await context.files.write(path, body, expected, {signal:host.signal});
    check();
    bind(path,result.sha256,content);
    status.textContent = 'Saved ' + path.split('/').pop();
  }
  function run(operation) {
    if (pending || !practice || disposed) return;
    pending = true;
    buttons(true);
    operation().catch(error => { if (!disposed) status.textContent = error.message; })
      .finally(() => {pending=false;if (!disposed) buttons(false);});
  }
  open.onclick = () => run(openDocument);
  save.onclick = () => run(() => saveDocument(false));
  saveAs.onclick = () => run(() => saveDocument(true));
  buttons(true);
  status.textContent = 'Opening practice…';
  const ready = (async () => {
    context = await host.storage.workspaceFileContext();
    check();
    initialized ??= initialize().catch(error => { initialized=undefined;throw error; });
    await initialized;
    check();
    const instance = new PracticeWindow();
    let released = false;
    releasePractice = () => {
      if (released) return;
      released = true;
      instance.close();
      instance.free();
      practice = undefined;
    };
    try {
      await instance.start(canvas);
      check();
      practice=instance;
      clean=practice.document();
      const source=host.w.launchContext;
      if (source) {
        if (source.storage !== 'account' || source.owner !== owner || !source.path.toLowerCase().endsWith(suffix) || !/^[0-9a-f]{64}$/.test(source.sha256)) throw Error('Choose a practice document from your Files.');
        await load(source.path,source.sha256);
      } else {status.textContent='';canvas.focus();}
      buttons(false);
    } catch (error) {
      releasePractice();
      throw error;
    }
  })().catch(error => { if (!disposed) status.textContent=error.message; throw error; });
  return {
    element, ready, focus() { canvas.focus(); },
    async requestClose() {
      if (pending) {status.textContent='Please wait for the file operation to finish.';return false;}
      return !practice || practice.document() === clean || await host.ui.confirm('Discard unsaved practice changes?',{confirmLabel:'Discard',signal:host.signal});
    },
    dispose() { disposed = true; if (practice) releasePractice(); }
  };
}
