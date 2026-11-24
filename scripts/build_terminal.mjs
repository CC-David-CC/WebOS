import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {cp, mkdir, mkdtemp, readFile, rm, writeFile} from 'node:fs/promises';
import {gzipSync} from 'node:zlib';
import path from 'node:path';

const builder = 'platform/runtime/active-system/tools/app-builder';
const imageManifest = 'assets/terminal/v2/image.json';
const engine = 'engines/v86/webos/runtime';
const linux = 'apps/linux';
const runtime = 'assets/terminal/v86';

function appendHosts(initramfs, content) {
  const padded = buffer => Buffer.concat([buffer, Buffer.alloc((4 - buffer.length % 4) % 4)]);
  function entry(ino, name, mode, bytes) {
    const encodedName = Buffer.from(name + '\0');
    const fields = [ino, mode, 0, 0, 1, 0, bytes.length, 0, 0, 0, 0, encodedName.length, 0];
    const header = Buffer.from('070701' + fields.map(value => value.toString(16).padStart(8, '0')).join(''));
    return Buffer.concat([padded(Buffer.concat([header, encodedName])), padded(bytes)]);
  }
  const overlay = Buffer.concat([
    entry(1, './etc/hosts', 0o100644, content),
    entry(0, 'TRAILER!!!', 0, Buffer.alloc(0)),
  ]);
  return Buffer.concat([initramfs, gzipSync(overlay, {level: 9})]);
}

export async function buildTerminal({root, output, copySource, recordSource, accountHome = false}) {
  for (const relative of ['scripts/build_terminal.mjs', 'apps/terminal/index.mjs', 'apps/terminal/terminal.css',
    ...['build.mjs', 'inventory-limits.mjs', 'package.json', 'package-lock.json', 'dependency-notices.json',
      'notices/xterm-addon-serialize-0.14.0.txt'].map(name => builder + '/' + name)]) {
    await recordSource(relative);
  }
  const metadata = JSON.parse(await readFile(path.join(root, linux, imageManifest)));
  if (metadata.version !== 'codi-terminal-image/2' || !/^[a-f0-9]{64}$/.test(metadata.sha256) ||
      metadata.path !== 'assets/terminal/v2/' + metadata.sha256 + '.cpio.gz') {
    throw Error('Invalid Linux image manifest');
  }
  const image = await readFile(path.join(root, linux, metadata.path));
  if (image.length !== metadata.bytes || createHash('sha256').update(image).digest('hex') !== metadata.sha256) {
    throw Error('Linux image does not match its manifest');
  }
  const scratch = await mkdtemp(path.join(path.dirname(output), '.terminal-build-'));
  try {
    const config = path.join(scratch, 'builder.json');
    const built = path.join(scratch, 'public');
    await writeFile(config, JSON.stringify({source: path.join(root, 'apps'), output: built, apps: ['terminal']}));
    execFileSync(process.execPath, [path.join(root, builder, 'build.mjs'), config], {stdio: ['ignore', 'pipe', 'inherit']});
    const {apps: [app]} = JSON.parse(await readFile(path.join(built, 'apps.json')));
    const prefix = path.dirname(app.path);
    await mkdir(path.join(output, path.dirname(prefix)), {recursive: true});
    await cp(path.join(built, 'apps/terminal', app.bundleSHA256), path.join(output, prefix), {recursive: true});
    for (const name of ['guest-worker-client.mjs', 'guest-worker-runtime.js',
      ...(accountHome ? ['account-home-9p.mjs'] : [])]) {
      const relative = 'assets/desktop/' + name;
      await copySource(linux + '/' + relative, relative);
    }
    if (accountHome) {
      const hosts = linux + '/scripts/guest-hosts';
      await recordSource(hosts);
      await recordSource(linux + '/' + imageManifest);
      await recordSource(linux + '/' + metadata.path);
      const patched = appendHosts(image, await readFile(path.join(root, hosts)));
      const sha256 = createHash('sha256').update(patched).digest('hex');
      const imagePath = 'assets/terminal/v2/' + sha256 + '.cpio.gz';
      await mkdir(path.join(output, 'assets/terminal/v2'), {recursive: true});
      await writeFile(path.join(output, imagePath), patched);
      await writeFile(path.join(output, imageManifest), JSON.stringify({
        version: metadata.version, path: imagePath, sha256, bytes: patched.length
      }) + '\n');
    } else {
      for (const relative of [imageManifest, metadata.path]) {
        await copySource(linux + '/' + relative, relative);
      }
    }
    for (const name of ['libv86.js', 'v86.wasm', 'seabios.bin', 'vgabios.bin',
      'notices/v86-LICENSE.txt', 'notices/bios-COPYING.LESSER.txt']) {
      await copySource(engine + '/' + name, runtime + '/' + name);
    }
    for (const name of ['vmlinuz', 'notices/linux-copyright.txt', 'notices/busybox-copyright.txt']) {
      await copySource(linux + '/runtime/' + name, runtime + '/' + name);
    }
    return app;
  } finally {
    await rm(scratch, {recursive: true, force: true});
  }
}
