#!/usr/bin/env python3
"""Build a disposable, local-only i386 AVR toolchain archive for v86 research.

The three Debian packages and matching guest libraries are pinned below. This
is not a release artifact or a complete corresponding-source distribution.
"""
import argparse, hashlib, shutil, subprocess, tarfile, tempfile
from pathlib import Path

PACKAGES={
 'gcc-avr_5.4.0+Atmel3.6.2-3_i386.deb':'0a8995029e34f2fdcc1869b284cbe89029c77a56ca0634fc60d1162db2543a25',
 'binutils-avr_2.26.20160125+Atmel3.6.2-4_i386.deb':'5b2a81eec101396fd10bec6c581344cdc60699169a185eefa73cf6b1015efabd',
 'avr-libc_2.0.0+Atmel3.6.2-3_all.deb':'a7adb563082d291c49fe5f4a483fca18d27f30627c2c8a520c5e23578d0fa5af',
}
LIBRARIES={
 'libdl.so.2':'3a86c2cca559881fc964f4bac0808c168e89760e17e298737dd2c0a626324937',
 'libgmp.so.10':'727991d7c0d4c3bc8c4965f11462785f1e8d37b8ca824761c160cb724c3d663b',
 'libm.so.6':'d2792ef9413118b53434e9d04d02ab29a684f3993f05b0788ccee298cf01571a',
 'libmpc.so.3':'3fb7e147f6d82483f172d43ce5e2f2611e1b41dd908206078d6f3d126b180770',
 'libmpfr.so.6':'614e37cac5acc29186733b573689f4874e718bacf3527a924d6a1ed8d6405e18',
 'libz.so.1':'cd6d6cfe9cd92eb6894e50db8c41f0295063cdac54b423108d4d26e8b5384c0d',
}
def verify(path,expected):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 if h.hexdigest()!=expected:raise ValueError('Unexpected input: '+str(path))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packages',type=Path,required=True);p.add_argument('--guest-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--core-release',type=Path,required=True);p.add_argument('--core-output',type=Path,required=True);a=p.parse_args()
 if any(x.exists() or x.is_symlink() for x in (a.output,a.core_output)):raise ValueError('Output already exists')
 verify(a.core_release,'639a745994b00eb8d806f80c2302056f76403c9dc737df0676da81418c7ddd17')
 for name,digest in PACKAGES.items():verify(a.packages/name,digest)
 libs=a.guest_root/'usr/lib/i386-linux-gnu'
 for name,digest in LIBRARIES.items():verify(libs/name,digest)
 verify(libs/'libc.so.6','ef7792b351dba25b48ad223224966db839b132efd7755d26f422ba2eb0f1a6a1')
 with tempfile.TemporaryDirectory(prefix='codi-avr-v86-') as tmp:
  root=Path(tmp);(root/'libs').mkdir()
  for name in PACKAGES:subprocess.run(['dpkg-deb','--extract',str(a.packages/name),str(root)],check=True)
  for name in LIBRARIES:
   target=root/'libs'/name;shutil.copyfile(libs/name,target);target.chmod(0o644 if name in ('libdl.so.2','libm.so.6') else 0o664)
  subprocess.run(['tar','-C',str(root),'-czf',str(a.output.absolute()),'usr/bin','usr/lib/gcc/avr','usr/lib/avr','libs'],check=True)
 with tarfile.open(a.core_release,'r:') as src,tarfile.open(a.core_output,'w:gz') as dst:
  count=0
  for m in src:
   name=m.name.removeprefix('./')
   if not name.startswith('arduino-core/'):continue
   relative=Path(name.removeprefix('arduino-core/'))
   if relative.is_absolute() or '..' in relative.parts or not (m.isfile() or m.isdir()):raise ValueError('Unexpected Arduino core member')
   m.name=relative.as_posix()
   if m.isfile():
    with src.extractfile(m) as f:dst.addfile(m,f)
    count+=1
   elif m.name!='.':dst.addfile(m)
  if count!=47:raise ValueError('Unexpected Arduino core file count')
 print('Prepared research-only archives:',a.output,a.output.stat().st_size,'bytes;',a.core_output,a.core_output.stat().st_size,'bytes')
if __name__=='__main__':main()
