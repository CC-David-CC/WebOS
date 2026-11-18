import {MAX_BYTES} from './craft-account-storage.mjs';

const directory = 'Pictures/LightCraft Originals';
const hash = /^[0-9a-f]{64}$/;

function originalPath(digest) {
  if (typeof digest !== 'string' || !hash.test(digest)) throw Error('Invalid LightCraft original digest.');
  return directory + '/' + digest + '.original';
}

export async function lightCraftAccountScope(origin, owner) {
  const key = new TextEncoder().encode(JSON.stringify(['lightcraft-account-cache/1', origin, owner]));
  const bytes = await crypto.subtle.digest('SHA-256', key);
  return Array.from(new Uint8Array(bytes), byte => byte.toString(16).padStart(2, '0')).join('');
}

/** Store immutable originals under the same account authority as the catalog. */
export function createLightCraftOriginalStore({files, valid, signal}) {
  const pending = new Map();
  let directoryReady;

  function check() {
    if (!valid() || signal?.aborted) throw new DOMException('The LightCraft account window closed.', 'AbortError');
    files.check();
  }

  function directoryExists() {
    directoryReady ??= (async () => {
      try {
        await files.mkdir(directory);
      } catch (error) {
        if (error.status !== 409) throw error;
        check();
        await files.list(directory);
      }
      check();
    })().catch(error => {
      directoryReady = undefined;
      throw error;
    });
    return directoryReady;
  }

  async function write(path, digest, snapshot) {
    await directoryExists();
    check();
    let existing;
    try {
      existing = await files.version(path, {signal});
    } catch (error) {
      if (error.status !== 404) throw error;
    }
    check();
    if (existing) {
      if (existing.sha256 !== digest) throw Error('A different file occupies the LightCraft original path.');
      return digest;
    }
    try {
      const committed = await files.write(path, snapshot, null, {signal});
      check();
      if (committed.sha256 !== digest) throw Error('The account did not confirm the original bytes.');
    } catch (error) {
      // Another window can finish the same conditional create first.
      if (error.status !== 409) throw error;
      check();
      const current = await files.version(path, {signal});
      check();
      if (current.sha256 !== digest) throw error;
    }
    return digest;
  }

  async function store(data) {
    check();
    if (!(data instanceof Blob || data instanceof ArrayBuffer || data instanceof Uint8Array)) throw Error('LightCraft original bytes required.');
    const snapshot = data instanceof Blob ? data : new Blob([data]);
    if (!snapshot.size || snapshot.size > MAX_BYTES) throw Error('The original exceeds the account file size limit.');
    const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', await snapshot.arrayBuffer())),
      byte => byte.toString(16).padStart(2, '0')).join('');
    check();
    if (!pending.has(digest)) {
      pending.set(digest, write(originalPath(digest), digest, snapshot).finally(() => pending.delete(digest)));
    }
    const stored = await pending.get(digest);
    check();
    return stored;
  }

  async function read(digest) {
    check();
    const result = await files.read(originalPath(digest));
    check();
    if (result.sha256 !== digest || !(result.data instanceof Uint8Array) || !result.data.length || result.data.length > MAX_BYTES) {
      throw Error('LightCraft could not verify the account original.');
    }
    return result.data;
  }

  return Object.freeze({store, read});
}
