import {createHash} from 'node:crypto';
import {readFile, realpath, stat} from 'node:fs/promises';
import path from 'node:path';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const validAsset = /^(?:[a-zA-Z0-9_@+-][a-zA-Z0-9_@+.-]*\/)*[a-zA-Z0-9_@+-][a-zA-Z0-9_@+.-]*$/;
const viewerRoot = 'viewer';
const engineRoot = viewerRoot+'/lib-assets/source-occt/modules/engine/runtime';
const sources = viewerRoot+'/sources';

// Consume the Runtime app-builder output without renaming its content-addressed files.
export async function assembleAcad({site, sourceCommit, sourceEngine, put}) {
  const directory = path.resolve(site);
  async function read(relative) {
    const target = path.join(directory,relative);
    if (await realpath(target) !== target || !(await stat(target)).isFile()) throw Error('ACAD site must contain regular, direct paths');
    return readFile(target);
  }
  const catalog = JSON.parse(await read('assets/desktop/apps.json'));
  if (catalog.version !== 'codi-public-apps/2' || catalog.hostAPI !== 2 || catalog.apps?.length !== 1)
    throw Error('Expected a standalone Runtime app-builder site for ACAD');
  const [app] = catalog.apps;
  const prefix = 'assets/desktop/apps/jsketcher/'+app.bundleSHA256;
  if (app.id !== 'jsketcher' || app.kind !== 'browser' || !/^[0-9a-f]{64}$/.test(app.bundleSHA256) ||
      app.path !== prefix+'/index.mjs' || JSON.stringify(app.styles) !== '["index.css"]' ||
      hash(JSON.stringify(app.files)) !== app.bundleSHA256 || app.files['index.mjs']?.sha256 !== app.sha256 ||
      app.files['index.mjs']?.bytes !== app.bytes || !app.files['index.css'])
    throw Error('Invalid ACAD content-addressed registry');
  const receiptName = sources+'/build-receipt.txt';
  const receipt = JSON.parse(await read(prefix+'/'+receiptName));
  if (receipt.editor !== sourceCommit || Object.entries(sourceEngine).some(([name,pin])=>receipt.engine?.[name] !== pin))
    throw Error('ACAD site has different editor or engine sources than the assembly pin');
  for (const [name,pin] of Object.entries(receipt.sources)) {
    if (!validAsset.test(name) || name.includes('/') || app.files[sources+'/'+name]?.sha256 !== pin)
      throw Error('ACAD source download differs from its receipt');
  }
  for (const [asset,digest] of [[sourceEngine.glue+'.mjs',sourceEngine.glue],[sourceEngine.wasm+'.wasm',sourceEngine.wasm]]) {
    if (app.files[engineRoot+'/'+asset]?.sha256 !== digest) throw Error('ACAD engine differs from its source pin');
  }
  for (const name of [receiptName,sources+'/SOURCE-INDEX.html',sources+'/acad-source.zip',sources+'/occt-source.zip',sources+'/frontend-source-and-notices.zip']) {
    if (!app.files[name]) throw Error('Missing required ACAD source asset: '+name);
  }
  for (const [name,expected] of Object.entries(app.files)) {
    if (!validAsset.test(name) || name.split('/').includes('node_modules')) throw Error('Invalid ACAD asset path');
    const bytes = await read(prefix+'/'+name);
    if (bytes.length !== expected.bytes || hash(bytes) !== expected.sha256) throw Error('ACAD asset differs from inventory: '+name);
    await put(prefix+'/'+name,bytes);
  }
  return app;
}
