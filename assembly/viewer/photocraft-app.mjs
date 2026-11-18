import {connectPhotoNative} from './photocraft-native.mjs';
import {createPhotoStorage, projectPath} from './photocraft-storage.mjs';

/** The classic Desktop's API2 view for the PhotoCraft editor. */
export function mount(host) {
  const element = document.createElement('div');
  element.className = 'window-content';
  element.style.display = 'flex';
  element.style.flexDirection = 'column';
  const status = document.createElement('div');
  status.setAttribute('role', 'status');
  status.textContent = 'Opening PhotoCraft…';
  const frame = document.createElement('iframe');
  frame.title = 'PhotoCraft editor';
  frame.style.flex = '1';
  frame.style.minHeight = '0';
  frame.style.border = '0';
  frame.inert = true;

  const abort = new AbortController();
  const session = host.session();
  let native, storage, context, dialog, loaded = false;
  let lastDialog = 0n;
  const valid = () => !abort.signal.aborted && !host.signal.aborted && host.session() === session &&
    host.desktop.windows.includes(host.w) && host.storage.signedInSubject() === session?.public.sub && context?.valid();
  const check = () => {
    if (!valid()) throw new DOMException('PhotoCraft account view closed.', 'AbortError');
    if (loaded) native.assertLive();
  };
  const bind = resource => {
    check();
    host.desktop.updateAccountFileBinding(host.w, {owner:context.owner, ...resource});
  };

  function message(text) {
    status.textContent = text;
    status.hidden = !text;
  }

  async function save(packet) {
    if (!loaded || !valid()) return;
    message('Saving to your account…');
    try {
      check();
      const binding = await storage.save(packet, native.acknowledge);
      bind(binding);
      message('');
    } catch (error) {
      if (valid()) message(error.message);
    }
  }

  async function chooseProject(packet, signal) {
    const picked = packet.path === null ? await host.storage.pickFile({extensions:['.pcraft'], signal}) : null;
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
    const folder = await host.storage.pickFolder({signal});
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
      if (packet.operation === 'open') answer = await chooseProject(packet, controller.signal);
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
    const launch = host.w.launchContext;
    let resource;
    if (launch) {
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
      url, signal:abort.signal, onSave:save, onDialog:handleDialog,
      onUnavailable(reason) {
        loaded = false;
        frame.inert = true;
        dialog?.abort();
        message(reason);
      }
    });
    element.append(frame);
    await native.ready;
    check();
    if (resource) {
      bind(await storage.open(resource, native.start));
    } else {
      storage.attachBlank(await native.start());
    }
    check();
    loaded = true;
    frame.inert = false;
    message('');
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
    host.signal.removeEventListener('abort', dispose);
    element.remove();
  }

  element.append(status);
  host.signal.addEventListener('abort', dispose, {once:true});
  if (host.signal.aborted) dispose();
  return {
    element,
    ready,
    focus() {
      if (!loaded || !valid() || dialog) return false;
      frame.contentWindow?.focus();
      frame.contentDocument?.querySelector('canvas')?.focus();
      return true;
    },
    dispose
  };
}
