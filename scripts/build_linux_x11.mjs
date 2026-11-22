import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdtemp, readFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';

export async function buildLinuxX11(root, packages, sourceInputs, chromiumInputs) {
  const appRoot = 'apps/linux-x11';
  async function source(relative) {
    const bytes = await readFile(path.join(root,relative));
    sourceInputs.set(relative,createHash('sha256').update(bytes).digest('hex'));
    return bytes;
  }
  const files = [];
  for (const file of ['app.mjs','session.html','session.js','screen.css']) {
    files.push({name:file==='app.mjs'?'index.mjs':file,bytes:await source(appRoot+'/'+file)});
  }
  for (const file of ['scripts/build-image.py','base.sha256','packages.sha256',
    'guest/init','guest/session.sh','guest/drop-privileges.py','guest/xorg.conf','guest/twmrc']) {
    await source(appRoot+'/'+file);
  }
  if (chromiumInputs) {
    const metadata = JSON.parse(await source(appRoot+'/chromium-runtime.json'));
    if (metadata.schema !== 'webos-x11-chromium-runtime/1') throw Error('Unrecognized Chromium input receipt');
    const lock = await source(appRoot+'/chromium-packages.json');
    if (createHash('sha256').update(lock).digest('hex') !== metadata.packageLockSHA256) {
      throw Error('Chromium package lock does not match its runtime');
    }
    await source(appRoot+'/guest/chromium');
    await source(appRoot+'/scripts/build-chromium-disk.py');
    files.push({name:'debian-common-licenses.txt',bytes:await source(appRoot+'/docs/debian-common-licenses.txt')});
    const engine = execFileSync('git',['rev-parse','HEAD'],{cwd:path.join(root,'engines/v86'),encoding:'utf8'}).trim();
    if (engine !== metadata.engineCommit) throw Error('Chromium runtime does not match the checked-out v86 source');
    const engineScript = 'v86-chromium.js';
    const inputs = ['browser.sqfs','v86-chromium.wasm','chromium-copyright.txt'];
    if (metadata.files[engineScript]) inputs.push(engineScript);
    for (const name of inputs) {
      const bytes = await readFile(path.resolve(chromiumInputs,name));
      const expected = metadata.files[name];
      if (!expected || bytes.length !== expected.bytes || createHash('sha256').update(bytes).digest('hex') !== expected.sha256) {
        throw Error(`Invalid Chromium runtime input: ${name}`);
      }
      files.push({name,bytes});
    }
    const session = files.find(file => file.name === 'session.html');
    let html = session.bytes.toString('utf8');
    if (metadata.files[engineScript]) {
      const sharedScript = 'src="/assets/terminal/v86/libv86.js"';
      if (!html.includes(sharedScript)) throw Error('Unexpected X11 emulator script');
      html = html.replace(sharedScript, 'src="./' + engineScript + '"');
    }
    if (!html.includes('<html lang="en">')) throw Error('Unexpected X11 document');
    const size = metadata.files['browser.sqfs'].bytes;
    if (size % (256 * 1024)) throw Error('Chromium disk must be padded to its HTTP range block size');
    session.bytes = Buffer.from(html.replace('<html lang="en">',`<html lang="en" data-chromium-disk-bytes="${size}">`));
  }
  await source('scripts/build_linux_x11.mjs');
  const linuxRoot = path.join(root,'apps/linux');
  const metadata = JSON.parse(await source('apps/linux/assets/terminal/v2/image.json'));
  if (!/^assets\/terminal\/v2\/[0-9a-f]{64}\.cpio\.gz$/.test(metadata.path)) {
    throw Error('Unexpected base initramfs path');
  }
  const scratch = await mkdtemp(path.join(tmpdir(),'webos-x11-'));
  try {
    const image = path.join(scratch,'graphics.cpio.gz');
    execFileSync('python3',[path.join(root,appRoot,'scripts/build-image.py'),path.resolve(packages),
      path.join(linuxRoot,metadata.path),path.join(linuxRoot,'runtime/vmlinuz'),image,
      ...(chromiumInputs?['--chromium']:[])],{stdio:'inherit'});
    files.push({name:'graphics.cpio.gz',bytes:await readFile(image)});
    return files;
  } finally {
    await rm(scratch,{recursive:true,force:true});
  }
}
