#!/usr/bin/env python3
"""Pack trusted local avr-v1.0.0 research inputs; generated files stay out of Git."""
import gzip,json,struct,sys
from pathlib import Path
root=Path(sys.argv[1]);output=Path(sys.argv[2]);paths=[root/'manifest.json']
for directory in ('specs','sysroot','arduino-core','libraries'):
 paths.extend(p for p in (root/directory).rglob('*') if p.is_file())
entries=[];blocks=[];offset=0
for path in sorted(paths):
 if path.is_symlink():raise SystemExit('Linked input refused')
 name=path.relative_to(root).as_posix();data=path.read_bytes();entries.append({'name':name,'offset':offset,'size':len(data)});blocks.append(data);offset+=len(data)
header=json.dumps(entries,separators=(',',':'),ensure_ascii=True).encode('ascii')
if len(entries)>1024 or len(header)>262144 or offset>64*1024*1024:raise SystemExit('Input bundle exceeds bounds')
with output.open('wb') as file:
 with gzip.GzipFile(filename='',mode='wb',fileobj=file,mtime=0,compresslevel=6) as gz:
  gz.write(b'CAVRIN01');gz.write(struct.pack('<I',len(header)));gz.write(header)
  for block in blocks:gz.write(block)
print(f'Packed {len(entries)} files, {offset} bytes into {output.stat().st_size} bytes')
