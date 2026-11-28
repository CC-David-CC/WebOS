// Loaded before the embedded editor. Each account owns its vault and each guest
// uses memory owned by its current Desktop session. Only the current editor window can recover its autosave.
(() => {
  const {owner, guest, document:windowId} = JSON.parse(window.name);
  if (window === window.parent || typeof owner !== 'string' || !owner || !windowId) {
    throw new Error('Launch this editor from the WebOS Desktop.');
  }
  const namespace = 'webos/' + [document.documentElement.dataset.editor, owner]
    .map(encodeURIComponent).join('/') + '/';
  function prefix(key) {
    const perWindow = /autosave|^pdraft:file$/i.test(key);
    return namespace + (perWindow ? 'windows/' + encodeURIComponent(windowId) + '/' : 'vault/') + key;
  }
  function memory(map) {
    return {
      keys:() => Array.from(map.keys()),
      getItem:key => map.get(key) ?? null,
      setItem:(key,value) => map.set(key,String(value)),
      removeItem:key => map.delete(key),
    };
  }
  function scoped(storage, inMemory = false) {
    function keys() {
      return (inMemory ? storage.keys() : Object.keys(storage)).flatMap(key => {
        if (!key.startsWith(namespace)) return [];
        const name = key.slice(key.indexOf('/', namespace.length) + 1);
        const candidate = name.startsWith(encodeURIComponent(windowId) + '/')
          ? name.slice(name.indexOf('/') + 1) : name;
        return key === prefix(candidate) ? [candidate] : [];
      });
    }
    return {
      get length() { return keys().length; },
      key: index => keys()[index] ?? null,
      getItem: key => storage.getItem(prefix(key)),
      setItem: (key, value) => storage.setItem(prefix(key), value),
      removeItem: key => storage.removeItem(prefix(key)),
      clear() { keys().forEach(key => storage.removeItem(prefix(key))); },
    };
  }
  const temporary = guest ? window.frameElement.webosGuestStorage : null;
  const local = guest ? memory(temporary.local) : window.localStorage;
  const session = guest ? memory(temporary.session) : window.sessionStorage;
  const databases = window.indexedDB;
  Object.defineProperties(window, {
    localStorage:{value:scoped(local,guest)},
    sessionStorage:{value:scoped(session,guest)},
    indexedDB:{value:guest ? undefined : {
      open:(name, ...args) => databases.open(prefix(name), ...args),
      deleteDatabase:name => databases.deleteDatabase(prefix(name)),
      cmp:databases.cmp.bind(databases),
    }},
  });
})();
