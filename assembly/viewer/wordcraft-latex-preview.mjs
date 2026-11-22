import './wordcraft-latex-preview.css';

const runtime = new URL('latex/', import.meta.url);
const texExtension = /[.](?:tex|latex|ltx)$/i;
const projectExtension = /[.](?:tex|latex|ltx|sty|cls|clo|def|cfg|fd|pgf|tikz|bib|bst|csv|dat|txt|pdf|png|jpe?g)$/i;
const maxMain = 2 * 1024 * 1024;
const maxProject = 24 * 1024 * 1024;
const maxFiles = 160;
const maxPdfBytes = 24 * 1024 * 1024;
const maxPages = 120;
const utf8 = new TextDecoder('utf-8', {fatal:true});

function element(tag, text = '', props = {}) {
  const node = Object.assign(document.createElement(tag), props);
  node.textContent = text;
  return node;
}

function canonical(path) {
  if (typeof path !== 'string' || path.length > 1024 ||
      path.split('/').some(part => !part || part.startsWith('.') || /[\\\x00-\x1f]/.test(part))) {
    throw Error('Choose a project path relative to the selected folder.');
  }
  return path;
}

async function bytes(data) {
  if (data instanceof Uint8Array) return data;
  return new Uint8Array(await data.arrayBuffer());
}

async function workspaceProject(files, folder, main, signal) {
  const relative = folder ? main.slice(folder.length + 1) : main;
  if (folder && !main.startsWith(folder + '/')) throw Error('Choose a folder containing the main LaTeX file.');
  const pending = [folder], additional = [];
  let total = 0, scanned = 0;
  while (pending.length) {
    const dir = pending.pop();
    const {entries} = await files.list(dir, {signal});
    for (const entry of entries) {
      if (++scanned > maxFiles) throw Error('Choose a folder with at most 160 project items.');
      if (entry.name.startsWith('.')) continue;
      const path = canonical(dir ? dir + '/' + entry.name : entry.name);
      if (entry.directory) pending.push(path);
      else if (path !== main && projectExtension.test(path)) {
        const file = await files.read(path, {signal});
        const content = await bytes(file.data);
        total += content.byteLength;
        if (total > maxProject) throw Error('The project assets exceed 24 MiB.');
        additional.push({path:folder ? path.slice(folder.length + 1) : path, content});
      }
    }
    signal.throwIfAborted();
  }
  return {relative, additional};
}

async function deviceProject(files, main, signal) {
  if (files.length > maxFiles) throw Error('Choose a folder with at most 160 project items.');
  const selected = files.map(file => ({
    file, path:canonical(file.webkitRelativePath.split('/').slice(1).join('/')),
  }));
  const mains = selected.filter(({file}) => file.name === main);
  if (mains.length !== 1) throw Error('Choose a folder containing one copy of the main LaTeX file.');
  const relative = mains[0].path, additional = [];
  let total = 0;
  for (const {file,path} of selected) {
    signal.throwIfAborted();
    if (path === relative || !projectExtension.test(path)) continue;
    total += file.size;
    if (total > maxProject) throw Error('The project assets exceed 24 MiB.');
    additional.push({path, content:await bytes(file)});
  }
  return {relative, additional};
}

function diagnostic(log, main, source) {
  const detail = log.split('\n').map(line => line.trim()).find(line => /^l\.\d+\s/.test(line));
  const line = detail?.match(/^l\.(\d+)/)?.[1];
  if (line) return main + ':' + line + ' — ' + detail.replace(/^l\.\d+\s+/, '');
  const lines = source.split(/\r\n|\n|\r/);
  const comment = source.match(/(?<!\\)%/)?.index;
  const documentEnd = source.lastIndexOf('\\end{document}');
  if (lines.length === 1 && comment !== undefined && documentEnd > comment) {
    return main + ':1 — A percent sign comments out the document ending. Restore the original line breaks.';
  }
  if (documentEnd < 0 && source.includes('\\begin{document}')) {
    return main + ':' + lines.length + ' — The file ends before \\end{document}. Check for missing content or closing commands.';
  }
  return main + ' — LaTeX could not compile this document.';
}

export function mountWordcraftLatex(mountNative, options, host) {
  const filename = options.resource?.path?.split('/').at(-1) ?? options.imported?.name;
  if (!texExtension.test(filename ?? '')) return mountNative(options);

  const root = element('section', '', {className:'wordcraft-latex'});
  const header = element('div', '', {className:'wordcraft-latex-toolbar'});
  const status = element('div', 'Choose how to open ' + filename + '.', {className:'wordcraft-latex-status'});
  status.setAttribute('role', 'status');
  const logBox = element('details', '', {className:'wordcraft-latex-log', hidden:true});
  const log = element('pre');
  logBox.append(element('summary', 'Compilation log'), log);
  const navigation = element('div', '', {className:'wordcraft-latex-pages', hidden:true});
  navigation.setAttribute('role', 'group');
  navigation.setAttribute('aria-label', 'PDF preview pages');
  const pageStatus = element('span');
  pageStatus.setAttribute('role', 'status');
  const paper = element('div', '', {className:'wordcraft-latex-paper', hidden:true});
  const canvas = element('canvas');
  canvas.setAttribute('role', 'img');
  paper.append(canvas);
  root.append(header, status, logBox, navigation, paper);

  const abort = new AbortController();
  const {signal} = abort;
  const lifecycleListeners = new Set(), bindingListeners = new Set();
  let editor, detachBinding, detachLifecycle, runner, pdf, pageNo = 1, activeRender;
  let revision = 0, compile, disposed = false, selectedFolder, selectedFiles;
  let binding = {loaded:false, documentId:null, path:null, revision:null};
  const button = (parent, title, action) => {
    const node = element('button', title, {type:'button'});
    node.addEventListener('click', action, {signal});
    parent.append(node);
    return node;
  };
  const notify = () => { revision++; for (const listener of lifecycleListeners) listener(); };
  const publishBinding = snapshot => { binding = snapshot; for (const listener of bindingListeners) listener(snapshot); };
  const check = () => { signal.throwIfAborted(); options.files.check(); };
  const noteError = error => {
    if (!disposed && error.name !== 'AbortError') status.textContent = error.message;
  };

  const preview = button(header, 'LaTeX Preview', () => void renderPreview().catch(noteError));
  const importButton = button(header, 'Import as editable', importEditable);
  const folder = options.resource && button(header, 'Choose project folder', () => {
    void chooseFolder().catch(noteError);
  });
  const chooser = element('input', '', {type:'file', hidden:true});
  chooser.setAttribute('webkitdirectory', '');
  const device = !options.resource && button(header, 'Choose project folder', () => chooser.click());
  header.append(chooser);
  chooser.addEventListener('change', () => {
    selectedFiles = Array.from(chooser.files ?? []);
    if (!selectedFiles.length) return;
    status.textContent = 'Selected ' + selectedFiles[0].webkitRelativePath.split('/')[0] + '. Choose LaTeX Preview.';
  }, {signal});
  const cancel = button(header, 'Cancel compilation', stop);
  cancel.hidden = true;
  const previous = button(navigation, 'Previous page', () => void showPage(pageNo - 1).catch(noteError));
  navigation.append(pageStatus);
  const next = button(navigation, 'Next page', () => void showPage(pageNo + 1).catch(noteError));

  async function chooseFolder() {
    check();
    const picked = await host.storage.pickWorkspaceFile({foldersOnly:true, signal});
    check();
    if (picked == null) return;
    const path = picked.replace(/^\//, '');
    if (path) canonical(path);
    if (path && !options.resource.path.startsWith(path + '/')) throw Error('Choose a folder containing ' + filename + '.');
    selectedFolder = path;
    status.textContent = 'Selected ' + (path || 'My files') + '. Choose LaTeX Preview.';
  }

  function controls() {
    const running = Boolean(compile);
    preview.disabled = importButton.disabled = running;
    if (folder) folder.disabled = running;
    if (device) device.disabled = running;
    cancel.hidden = !running;
    notify();
  }

  async function readMain(taskSignal) {
    if (options.resource) {
      const file = await options.files.read(options.resource.path, {signal:taskSignal});
      check();
      taskSignal.throwIfAborted();
      if (!options.resource.restore && file.sha256 !== options.resource.sha256) {
        throw Error('This file changed before opening. Refresh Files and open it again.');
      }
      if (file.data.size > maxMain || file.data.byteLength > maxMain) throw Error('The main LaTeX file exceeds 2 MiB.');
      return {main:await bytes(file.data), sha256:file.sha256};
    }
    if (options.imported.data.length > Math.ceil(maxMain / 3) * 4) throw Error('The main LaTeX file exceeds 2 MiB.');
    return {main:Uint8Array.from(atob(options.imported.data), char => char.charCodeAt(0))};
  }

  async function renderPreview() {
    check();
    if (compile) return;
    const operation = new AbortController();
    compile = operation;
    controls();
    logBox.hidden = true;
    log.textContent = '';
    status.textContent = 'Reading LaTeX source…';
    try {
      const {main, sha256} = await readMain(operation.signal);
      if (main.byteLength > maxMain) throw Error('The main LaTeX file exceeds 2 MiB.');
      const {relative, additional} = selectedFolder !== undefined
        ? await workspaceProject(options.files, selectedFolder, options.resource.path, operation.signal)
        : selectedFiles?.length
          ? await deviceProject(selectedFiles, filename, operation.signal)
          : {relative:filename, additional:[]};
      const source = utf8.decode(main);
      operation.signal.throwIfAborted();
      check();
      if (options.resource) publishBinding({
        loaded:true, documentId:null, path:options.resource.path, revision:sha256,
      });
      status.textContent = 'Loading the LaTeX compiler…';
      const {BusyTexRunner, PdfLatex} = await import(new URL('runner/index.js', runtime).href);
      operation.signal.throwIfAborted();
      runner = new BusyTexRunner({
        busytexBasePath:new URL('busytex', runtime).href,
        preloadDataPackages:[new URL('busytex/texlive-preview.js', runtime).href],
        initRetries:0,
      });
      await runner.initialize(true);
      operation.signal.throwIfAborted();
      status.textContent = 'Compiling ' + filename + '…';
      const result = await new PdfLatex(runner).compile({
        input:source, mainTexPath:canonical(relative), additionalFiles:additional,
        rerun:true, shellEscape:false,
      });
      // Release the TeX filesystem before constructing the PDF renderer.
      runner.terminate();
      runner = null;
      operation.signal.throwIfAborted();
      check();
      if (!result.success || !result.pdf?.length) {
        const output = String(result.log ?? '');
        log.textContent = output.slice(-24000);
        logBox.hidden = !output;
        logBox.open = true;
        throw Error(diagnostic(output, relative, source));
      }
      if (result.pdf.byteLength > maxPdfBytes) throw Error('The compiled PDF exceeds the 24 MiB preview limit.');
      const pdfjs = await import(new URL('pdf/pdf.mjs', runtime).href);
      operation.signal.throwIfAborted();
      pdfjs.GlobalWorkerOptions.workerSrc = new URL('pdf/pdf.worker.mjs', runtime).href;
      const task = pdfjs.getDocument({
        data:result.pdf, isEvalSupported:false, useSystemFonts:false,
        cMapUrl:new URL('pdf/cmaps/', runtime).href, cMapPacked:true,
        standardFontDataUrl:new URL('pdf/standard_fonts/', runtime).href,
      });
      const cancelPdf = () => { void task.destroy().catch(() => {}); };
      operation.signal.addEventListener('abort', cancelPdf, {once:true});
      let rendered;
      try { rendered = await task.promise; }
      finally { operation.signal.removeEventListener('abort', cancelPdf); }
      if (rendered.numPages > maxPages) {
        await rendered.destroy();
        throw Error('The compiled PDF exceeds the 120-page preview limit.');
      }
      activeRender?.cancel();
      const prior = pdf;
      pdf = rendered;
      if (prior) await prior.destroy();
      check();
      status.textContent = 'Compiled ' + filename + '.';
      navigation.hidden = paper.hidden = false;
      await showPage(1);
    } finally {
      if (compile === operation) {
        runner?.terminate();
        runner = compile = null;
        controls();
      }
    }
  }

  async function showPage(number) {
    if (!pdf || number < 1 || number > pdf.numPages) return;
    const document = pdf;
    pageNo = number;
    activeRender?.cancel();
    const page = await document.getPage(number);
    if (disposed || pdf !== document || pageNo !== number) return;
    const points = page.getViewport({scale:1});
    const width = Math.min(960, Math.max(1, paper.clientWidth - 24));
    const viewport = page.getViewport({scale:width / points.width * Math.min(devicePixelRatio, 2)});
    const heightLimit = 4096;
    const fitted = viewport.height <= heightLimit ? viewport
      : page.getViewport({scale:viewport.scale * heightLimit / viewport.height});
    canvas.width = Math.ceil(fitted.width);
    canvas.height = Math.ceil(fitted.height);
    canvas.style.width = width + 'px';
    canvas.setAttribute('aria-label', 'Compiled PDF page ' + number);
    previous.disabled = number === 1;
    next.disabled = number === document.numPages;
    pageStatus.textContent = 'Page ' + number + ' of ' + document.numPages;
    const painting = page.render({canvasContext:canvas.getContext('2d'),viewport:fitted});
    activeRender = painting;
    try { await painting.promise; }
    catch (error) { if (error.name !== 'RenderingCancelledException') throw error; }
    finally { if (activeRender === painting) activeRender = null; }
  }

  function stop() {
    if (!compile) return;
    runner?.terminate();
    runner = null;
    compile.abort();
    compile = null;
    controls();
    if (!disposed) status.textContent = 'Compilation canceled.';
  }

  function importEditable() {
    try {
      check();
      if (compile || editor) return;
      activeRender?.cancel();
      if (pdf) void pdf.destroy().catch(() => {});
      pdf = null;
      editor = mountNative(options);
      detachBinding = editor.fileBinding.subscribe(publishBinding);
      publishBinding(editor.fileBinding.snapshot());
      detachLifecycle = editor.lifecycle.subscribe(notify);
      root.replaceChildren(editor.element);
      root.classList.add('wordcraft-latex-editing');
      notify();
      void editor.ready.then(() => editor.focus?.()).catch(noteError);
    } catch (error) { noteError(error); }
  }

  function dispose() {
    if (disposed) return;
    disposed = true;
    stop();
    abort.abort();
    activeRender?.cancel();
    if (pdf) void pdf.destroy().catch(() => {});
    detachBinding?.();
    detachLifecycle?.();
    editor?.dispose();
    options.signal?.removeEventListener('abort', dispose);
    lifecycleListeners.clear();
    bindingListeners.clear();
  }

  options.signal?.addEventListener('abort', dispose, {once:true});
  return {
    element:root, ready:Promise.resolve(), retry:true,
    focus() { if (editor) return editor.focus?.(); preview.focus(); return true; },
    requestClose() { return editor?.requestClose?.() ?? true; },
    inspect() { return editor?.inspect?.() ?? {phase:'latex', path:binding.path, compiling:Boolean(compile), page:pageNo, pages:pdf?.numPages ?? 0}; },
    execute(...args) {
      if (editor) return editor.execute(...args);
      throw Error('Open an editable WordCraft document to use this command.');
    },
    fileBinding:{
      snapshot:() => binding,
      subscribe(listener) { bindingListeners.add(listener); return () => bindingListeners.delete(listener); },
    },
    lifecycle:{
      snapshot:() => editor?.lifecycle.snapshot() ?? {revision, dirty:false, pending:Boolean(compile)},
      subscribe(listener) { lifecycleListeners.add(listener); return () => lifecycleListeners.delete(listener); },
      quiesce(options) { if (editor) return editor.lifecycle.quiesce(options); stop(); return {release() {}}; },
      commitClose() { return editor?.lifecycle.commitClose(); },
    },
    dispose,
  };
}
