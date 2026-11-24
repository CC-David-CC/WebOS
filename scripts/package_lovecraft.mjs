import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { lstat, readFile } from 'node:fs/promises';
import path from 'node:path';

const entry = `export function mount(host) {
  const doc = host.document ?? document;
  const element = doc.createElement('div');
  element.className = 'window-content lovecraft';
  const frame = doc.createElement('iframe');
  frame.title = 'LoveCraft manuscript editor';
  frame.src = new URL('./native/index.html', import.meta.url);
  frame.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-downloads');
  Object.assign(frame.style, { border: '0', display: 'block', width: '100%', height: '100%' });
  element.append(frame);
  return { element, focus: () => frame.focus(), dispose: () => frame.remove() };
}
`;

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const digest = /^[a-f0-9]{64}$/;
const legal = ['ATTRIBUTION.md', 'LICENSE-APACHE', 'LICENSE-MIT', 'NOTICE', 'licenses/marked.txt', 'licenses/turndown.txt'];

export function packLoveCraft(site, checkout, sourceCommit) {
  return packTrunkApp(site, checkout, sourceCommit, {
    component: 'lovecraft', name: 'LoveCraft', scriptCount: 1, entry, legal,
  });
}

export function packFreeDAWm(site, checkout, sourceCommit) {
  // The software WebGPU renderer can start without painting the embedded canvas.
  const mount = entry.replace('window-content lovecraft', 'window-content freedawm')
    .replace('LoveCraft manuscript editor', 'FreeDAWm audio workstation')
    .replace('./native/index.html', './native/index.html?webgl');
  return packTrunkApp(site, checkout, sourceCommit, {
    component: 'freedawm', name: 'FreeDAWm', scriptCount: 3,
    entry: mount, legal: ['ATTRIBUTION.md', 'LICENSE-APACHE', 'LICENSE-MIT', 'NOTICE'],
  });
}

async function packTrunkApp(site, checkout, sourceCommit, app) {
  const git = (...args) => execFileSync('git', ['--no-optional-locks', '-C', checkout, ...args]);
  const receipt = JSON.parse(await readFile(path.join(site, 'component-build.json'), 'utf8'));
  if (receipt.schema !== 'webos-component-build/1' || receipt.component !== app.component ||
      receipt.sourceCommit !== sourceCommit || git('rev-parse', 'HEAD').toString().trim() !== sourceCommit ||
      receipt.sourceTree !== git('rev-parse', 'HEAD^{tree}').toString().trim() ||
      receipt.cargoLockSHA256 !== hash(git('show', sourceCommit + ':Cargo.lock')) ||
      !Array.isArray(receipt.files) || !receipt.files.length) {
    throw new Error(app.name + ' requires a verified Trunk site from the selected source pin.');
  }

  const files = new Map();
  for (const record of receipt.files) {
    const name = record.path;
    if (typeof name !== 'string' || !/^(?:[\w-]+\/)*[\w-][\w.-]*\.[\w-]+$/.test(name) ||
        files.has(name) || !digest.test(record.sha256)) {
      throw new Error('Invalid ' + app.name + ' bundle file.');
    }
    const source = path.join(site, name);
    const info = await lstat(source);
    if (!info.isFile() || info.size !== record.bytes) throw new Error('Invalid ' + app.name + ' site file: ' + name);
    const bytes = await readFile(source);
    if (hash(bytes) !== record.sha256) throw new Error(app.name + ' site checksum changed: ' + name);
    files.set(name, bytes);
  }

  const document = files.get('index.html')?.toString('utf8') ?? '';
  const inlineScript = /<script( type="module")?>([\s\S]*?)<\/script>/g;
  const scripts = [...document.matchAll(inlineScript)];
  if (scripts.length !== app.scriptCount || scripts.filter(script => script[1]).length !== 1 ||
      ![...files.keys()].some(name => name.endsWith('.wasm'))) {
    throw new Error(app.name + ' requires the Trunk entry and WASM payload.');
  }
  let classicScript = 0;
  files.set('index.html', Buffer.from(document.replace(inlineScript, (inline, module, code) => {
    const name = module ? 'startup.mjs' : 'runtime-' + ++classicScript + '.js';
    if (files.has(name)) throw new Error('Duplicate script in ' + app.name + ': ' + name);
    files.set(name, Buffer.from(code));
    return '<script' + (module ?? '') + ' src="./' + name + '"></script>';
  })));
  for (const name of app.legal) files.set('legal/' + name, git('show', sourceCommit + ':' + name));

  return [{ name: 'index.mjs', bytes: Buffer.from(app.entry) },
    ...[...files].map(([name, bytes]) => ({ name: 'native/' + name, bytes }))];
}
