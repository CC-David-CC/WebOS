/** Build explicit public graphs into a new output directory, never a source/production root. */
import {build} from 'esbuild';
import {mkdir, writeFile, lstat, readFile, copyFile, readdir} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = process.argv[2] && path.resolve(process.argv[2]);
const sites = {};
for (let index = 3; index < process.argv.length; index += 2) {
 const flag = process.argv[index], value = process.argv[index + 1];
 if (!['--wordcraft', '--deckcraft'].includes(flag) || !value || value.startsWith('--') || sites[flag]) throw Error('Usage: node scripts/build_development.mjs NEW_OUTPUT [--wordcraft BUILT_SITE] [--deckcraft BUILT_SITE]');
 sites[flag] = path.resolve(value);
}
const wordcraftSite = sites['--wordcraft'] || null, deckcraftSite = sites['--deckcraft'] || null;
if (!output || output === root || output.startsWith(root + path.sep) || root.startsWith(output + path.sep)) throw Error('Provide a new external build directory.');
for (let p = output; p !== path.dirname(p); p = path.dirname(p)) { try { if ((await lstat(p)).isSymbolicLink()) throw Error('Direct build paths required.'); } catch (error) { if (error.code !== 'ENOENT') throw error; } }
await mkdir(output, {mode: 0o700});
async function copyComponentSite(component, site) {
 const receipt = JSON.parse(await readFile(path.join(site, 'component-build.json'), 'utf8'));
 const selected = execFileSync('git', ['-C', path.join(root, 'apps', component), 'rev-parse', 'HEAD'], {encoding: 'utf8'}).trim();
 if (receipt.schema !== 'webos-component-build/1' || receipt.component !== component || receipt.sourceCommit !== selected || !Array.isArray(receipt.files)) throw Error(component + ' artifact does not match the selected component source.');
 if (component === 'deckcraft') {
   // This app consumes the parent-selected core and embeds its selected fonts.
   // An unchanged app commit does not make an artifact from older dependencies compatible.
   const core = execFileSync('git', ['-C', path.join(root, 'libraries/craft-libs'), 'rev-parse', 'HEAD'], {encoding: 'utf8'}).trim();
   const fonts = execFileSync('git', ['-C', path.join(root, 'assets/craft-fonts'), 'rev-parse', 'HEAD'], {encoding: 'utf8'}).trim();
   if (receipt.nativeBuild?.sourceCommit !== selected || receipt.nativeBuild?.sharedCoreCommit !== core || receipt.nativeBuild?.fontsCommit !== fonts) throw Error('DeckCraft artifact dependency pins do not match the assembly.');
 }
 const expected = new Set(['component-build.json', ...receipt.files.map(file => file.path)]);
 async function walk(folder, prefix = '') { const found = []; for (const item of await readdir(folder, {withFileTypes: true})) { const name = prefix + item.name; if (item.isSymbolicLink()) throw Error('Direct artifact paths required.'); if (item.isDirectory()) found.push(...await walk(path.join(folder, item.name), name + '/')); else if (item.isFile()) found.push(name); else throw Error('Regular artifacts required.'); } return found; }
 const actual = await walk(site); if (actual.length !== expected.size || actual.some(name => !expected.has(name))) throw Error('Unregistered component artifact in input site.');
 async function digest(file) { const hash = createHash('sha256'); for await (const bytes of createReadStream(file)) hash.update(bytes); return hash.digest('hex'); }
 const destination = path.join(output, component); await mkdir(destination);
 for (const record of receipt.files) {
   if (typeof record.path !== 'string' || !/^(?:[A-Za-z0-9_-][A-Za-z0-9_.-]*\/)*[A-Za-z0-9_-][A-Za-z0-9_.-]*$/.test(record.path)) throw Error('Canonical public artifact path required.');
   const input = path.join(site, record.path), target = path.join(destination, record.path), info = await lstat(input);
   if (!info.isFile() || info.size !== record.bytes || await digest(input) !== record.sha256) throw Error('Component input artifact digest mismatch.');
   await mkdir(path.dirname(target), {recursive: true}); await copyFile(input, target);
   if (await digest(target) !== record.sha256) throw Error('Component copied artifact digest mismatch.');
 }
 await copyFile(path.join(site, 'component-build.json'), path.join(destination, 'component-build.json')); return receipt;
}
const wordcraftReceipt = wordcraftSite ? await copyComponentSite('wordcraft', wordcraftSite) : null;
const deckcraftReceipt = deckcraftSite ? await copyComponentSite('deckcraft', deckcraftSite) : null;
const result = await build({stdin: {contents: "import {mountAssembly} from './scripts/frontend.mjs';mountAssembly(document.getElementById('webos')," + JSON.stringify({wordcraftUrl: wordcraftSite ? './wordcraft/index.html' : null, deckcraftUrl: deckcraftSite ? './deckcraft/index.html' : null}) + ");", resolveDir: root},
 bundle: true, format: 'esm', outfile: path.join(output, 'client.mjs'), metafile: true, logLevel: 'silent'});
await build({entryPoints: [path.join(root, 'platform/storage/src/webos_storage/vendor/js-sha256/verify-worker.mjs')], bundle: true, format: 'esm', outfile: path.join(output, 'workers/storage-verify.mjs'), logLevel: 'silent'});
await writeFile(path.join(output, 'index.html'), '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WebOS development</title><link rel="icon" href="data:,"><link rel="stylesheet" href="/client.css"><link rel="stylesheet" href="/page.css"></head><body><div id="webos"></div><script type="module" src="/client.mjs"></script></body></html>');
await writeFile(path.join(output, 'page.css'), 'html,body,#webos{width:100%;height:100%;margin:0;overflow:hidden}button,input{font:inherit}');
await writeFile(path.join(output, 'build-inputs.json'), JSON.stringify({scope: 'development graph; not a release qualification', inputs: Object.keys(result.metafile.inputs), wordcraft: wordcraftReceipt && {sourceCommit: wordcraftReceipt.sourceCommit, totalBytes: wordcraftReceipt.totalBytes}, deckcraft: deckcraftReceipt && {sourceCommit: deckcraftReceipt.sourceCommit, totalBytes: deckcraftReceipt.totalBytes, nativeBuild: deckcraftReceipt.nativeBuild}}, null, 2) + '\n');
console.log(JSON.stringify({output, scope: 'Login/Desktop/Files development; enabled editor artifacts are explicitly verified; acceptance remains separate', editors: [wordcraftReceipt?.component, deckcraftReceipt?.component].filter(Boolean)}));
