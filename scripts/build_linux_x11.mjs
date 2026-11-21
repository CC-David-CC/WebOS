import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdtemp, readFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';

export async function buildLinuxX11(root, packages, sourceInputs) {
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
      path.join(linuxRoot,metadata.path),path.join(linuxRoot,'runtime/vmlinuz'),image],{stdio:'inherit'});
    files.push({name:'graphics.cpio.gz',bytes:await readFile(image)});
    return files;
  } finally {
    await rm(scratch,{recursive:true,force:true});
  }
}
