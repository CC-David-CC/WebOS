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
  let native, storage, context, loaded = false;
  const valid = () => !abort.signal.aborted && !host.signal.aborted && host.session() === session &&
    host.desktop.windows.includes(host.w) && host.storage.signedInSubject() === session?.public.sub && context?.valid();
  const check = () => {
    if (!valid()) throw new DOMException('PhotoCraft account view closed.', 'AbortError');
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
      const binding = await storage.save(packet, native.acknowledge);
      bind(binding);
      message('');
    } catch (error) {
      if (valid()) message(error.message);
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
      const sha256 = launch.sha256 ?? (await context.files.version(path)).sha256;
      check();
      resource = {path, sha256};
    }

    const url = new URL('photocraft/index.html', document.baseURI);
    url.searchParams.set('host', 'webos-account');
    url.searchParams.set('profile', context.owner);
    storage = createPhotoStorage({files:context.files, operations:host.documentOperations, valid});
    native = connectPhotoNative(frame, {
      url, signal:abort.signal, onSave:save,
      onUnavailable(reason) {
        loaded = false;
        frame.inert = true;
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
      if (!loaded || !valid()) return false;
      frame.contentWindow?.focus();
      frame.contentDocument?.querySelector('canvas')?.focus();
      return true;
    },
    dispose
  };
}
