/** Account side of PhotoCraft's native project exchange. */
const MAX_BYTES = 128 * 1024 * 1024;
const sha = value => typeof value === 'string' && /^[0-9a-f]{64}$/.test(value);
const generation = value => typeof value === 'string' && /^[0-9a-f]{32}$/.test(value);
const decimal = value => typeof value === 'string' && /^(0|[1-9][0-9]{0,19})$/.test(value);
const ticketFields = ['generation','documentId','revision','ticket','path'];
const key = path => 'mirror:/' + path;

export function projectPath(path) {
  if (typeof path !== 'string' || !/[.]pcraft$/i.test(path) || new TextEncoder().encode(path).length > 2048 ||
      /[\\\u0000-\u001f\u007f-\u009f]/u.test(path) || path.split('/').some(part => !part || part === '.' || part === '..')) {
    throw Error('Choose an account-relative .pcraft project path.');
  }
  return path;
}

function exact(receipt, request) {
  return receipt && ticketFields.every(field => receipt[field] === request[field]);
}

function nativeIdentity(value, path) {
  if (!generation(value?.generation) || !decimal(value.documentId) || !decimal(value.revision) || value.path !== path) {
    throw Error('PhotoCraft did not adopt the requested project.');
  }
  return Object.freeze({generation:value.generation,documentId:value.documentId});
}

export function createPhotoStorage({files, operations, valid}) {
  let identity = null, binding = null, pending = null, lastTicket = 0n;

  function check() {
    if (!valid()) throw new DOMException('PhotoCraft account view closed.', 'AbortError');
    files.check();
  }

  function inspect() {
    return {identity, binding, pending:pending?.state ?? null};
  }

  function attachBlank(native) {
    check();
    if (identity) throw Error('This PhotoCraft editor already owns a project.');
    identity = nativeIdentity(native, null);
  }

  async function open(resource, adopt) {
    check();
    const path = projectPath(resource?.path), expected = resource?.sha256;
    if (identity || !sha(expected)) throw Error('An exact unopened account project revision is required.');
    const operation = operations.begin('open');
    if (!operation) throw Error('Another file operation is active.');
    try {
      if (!operation.claimDocument(key(path))) throw Error('This project is busy in another window.');
      const file = await files.read(path);
      check();
      if (!operation.current() || file?.sha256 !== expected || !(file.data instanceof Uint8Array) ||
          !file.data.byteLength || file.data.byteLength > MAX_BYTES) throw Error('The account project changed or could not be read.');
      const native = nativeIdentity(await adopt(path, file.data), path);
      check();
      if (!operation.setDocument(key(path))) throw Error('This account editor changed during Open.');
      identity = native;
      binding = Object.freeze({path, sha256:expected});
      return binding;
    } finally {
      operation.finish();
    }
  }

  async function save(message, acknowledge) {
    check();
    if (pending) throw Error('Resolve the pending account save before starting another.');
    if (!identity || message?.generation !== identity.generation || message.documentId !== identity.documentId ||
        !decimal(message.revision) || !decimal(message.ticket) || BigInt(message.ticket) <= lastTicket) {
      throw Error('PhotoCraft save did not identify this live project.');
    }
    const request = Object.freeze(Object.fromEntries(ticketFields.map(field => [field,message[field]])));
    lastTicket = BigInt(request.ticket);
    const transaction = {state:'writing'};
    pending = transaction;
    let operation, durable = false;

    try {
      const path = projectPath(request.path);
      if (!(message.bytes instanceof ArrayBuffer) || !message.bytes.byteLength || message.bytes.byteLength > MAX_BYTES) {
        throw Error('Invalid PhotoCraft project bytes.');
      }
      const bytes = new Blob([message.bytes]);
      const expected = binding?.path === path ? binding.sha256 : null;
      operation = operations.begin('save');
      if (!operation?.claimDocument(key(path))) throw Error('This project is busy in another window.');
      check();
      const result = await files.write(path, bytes, expected, {signal:operation.signal});
      durable = true;
      check();
      if (!operation.current() || !sha(result?.sha256)) throw Error('Could not verify the account write.');

      transaction.state = 'adopting';
      const receipt = await acknowledge(request, {outcome:'written'});
      check();
      if (!exact(receipt, request) || receipt.adopted !== true || !operation.setDocument(key(path))) {
        throw Error('PhotoCraft did not accept the saved account revision.');
      }
      binding = Object.freeze({path, sha256:result.sha256});
      pending = null;
      return binding;
    } catch (error) {
      if (durable || error?.outcome === 'unknown') {
        transaction.state = 'unknown';
        throw Object.assign(Error('The account save result is unconfirmed. Verify it before retrying.'), {outcome:'unknown',cause:error});
      }
      try {
        check();
        const detail = String(error?.message || 'Account write failed.').slice(0, 250);
        const receipt = await acknowledge(request, {outcome:'failed',message:detail});
        check();
        if (!exact(receipt, request) || receipt.adopted !== false) throw Error('PhotoCraft did not acknowledge the failed write.');
        pending = null;
      } catch (settlementError) {
        transaction.state = 'settlement-failed';
        throw settlementError;
      }
      throw error;
    } finally {
      operation?.finish();
    }
  }

  return Object.freeze({attachBlank,open,save,inspect});
}
