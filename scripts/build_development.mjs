/** Build explicit public graphs into a new output directory, never a source/production root. */
import {build} from 'esbuild';
import {mkdir, writeFile, lstat} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = process.argv[2] && path.resolve(process.argv[2]);
if (!output || output === root || output.startsWith(root + path.sep) || root.startsWith(output + path.sep)) throw Error('Provide a new external build directory.');
for (let p = output; p !== path.dirname(p); p = path.dirname(p)) { try { if ((await lstat(p)).isSymbolicLink()) throw Error('Direct build paths required.'); } catch (error) { if (error.code !== 'ENOENT') throw error; } }
await mkdir(output, {mode: 0o700});
const result = await build({stdin: {contents: "import {mountAssembly} from './scripts/frontend.mjs';mountAssembly(document.getElementById('webos'));", resolveDir: root},
 bundle: true, format: 'esm', outfile: path.join(output, 'client.mjs'), metafile: true, logLevel: 'silent'});
await build({entryPoints: [path.join(root, 'platform/storage/src/webos_storage/vendor/js-sha256/verify-worker.mjs')], bundle: true, format: 'esm', outfile: path.join(output, 'workers/storage-verify.mjs'), logLevel: 'silent'});
await writeFile(path.join(output, 'index.html'), '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WebOS development</title><link rel="icon" href="data:,"><link rel="stylesheet" href="/client.css"><link rel="stylesheet" href="/page.css"></head><body><div id="webos"></div><script type="module" src="/client.mjs"></script></body></html>');
await writeFile(path.join(output, 'page.css'), 'html,body,#webos{width:100%;height:100%;margin:0;overflow:hidden}button,input{font:inherit}');
await writeFile(path.join(output, 'build-inputs.json'), JSON.stringify({scope: 'development graph; not a release qualification', inputs: Object.keys(result.metafile.inputs)}, null, 2) + '\n');
console.log(JSON.stringify({output, scope: 'Login/Desktop/Files development; WordCraft not connected'}));
