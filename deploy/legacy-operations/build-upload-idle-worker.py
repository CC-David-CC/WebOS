#!/usr/bin/env python3
"""Build the private file worker with a longer authenticated-upload idle limit."""
import argparse, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='0685f9925f2d00cb2433d6d3d9066ee86da7f901a2c3302e3c1f1e1842ab2152'
CHANGED='gateway_service/http.py'
def sha(data):return hashlib.sha256(data).hexdigest()
def build(base,destination):
    base=Path(base).absolute();destination=Path(destination).absolute()
    if not base.is_dir() or base.is_symlink() or destination.exists() or destination.is_symlink() or not destination.parent.is_dir():raise ValueError('Existing baseline and new destination required')
    if base in destination.parents or destination in base.parents:raise ValueError('Baseline and destination must be disjoint')
    raw=(base/'files-service.json').read_bytes()
    if sha(raw)!=BASE:raise ValueError('Wrong live worker baseline')
    manifest=json.loads(raw)
    if manifest.get('version')!='codi-private-file-service/1':raise ValueError('Wrong worker format')
    actual={p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
    if actual!=set(manifest['files'])|{'files-service.json'} or any(p.is_symlink() for p in base.rglob('*')):raise ValueError('Unexpected baseline files')
    for name,record in manifest['files'].items():
        content=(base/name).read_bytes()
        if record!={'bytes':len(content),'sha256':sha(content)}:raise ValueError('Changed baseline: '+name)
    if subprocess.check_output(['git','-C',str(ROOT.parent),'status','--porcelain','--','active-system/'+CHANGED],text=True):raise ValueError('Commit worker source first')
    before=(base/CHANGED).read_text();candidate=(ROOT/CHANGED).read_text()
    replacements=[
      ('seconds_per_use=900, idle_seconds=5, max_requests_per_minute=256):','seconds_per_use=900, idle_seconds=5, upload_idle_seconds=60, max_requests_per_minute=256):'),
      ('or not 0<idle_seconds<=10:','or not 0<idle_seconds<=10 or not 0<upload_idle_seconds<=120:'),
      ('self.seconds=seconds_per_use;self.idle=idle_seconds;self.active=0','self.seconds=seconds_per_use;self.idle=idle_seconds;self.upload_idle=upload_idle_seconds;self.active=0'),
      ('async def _read(self, request, *, principal=None, deadline, length=None):','async def _read(self, request, *, principal=None, deadline, length=None, idle=None):'),
      ('asyncio.timeout(min(self.idle,max(.001,deadline-time.monotonic())))','asyncio.timeout(min(self.idle if idle is None else idle,max(.001,deadline-time.monotonic())))'),
      ('prefix=await self._read(request,principal=principal,deadline=deadline,length=4)','prefix=await self._read(request,principal=principal,deadline=deadline,length=4,idle=self.upload_idle)'),
      ('raw=await self._read(request,principal=principal,deadline=deadline,length=length)','raw=await self._read(request,principal=principal,deadline=deadline,length=length,idle=self.upload_idle)'),
      ('while seen<size:\n                async with asyncio.timeout(min(self.idle,max(.001,deadline-time.monotonic()))):','while seen<size:\n                async with asyncio.timeout(min(self.upload_idle,max(.001,deadline-time.monotonic()))):'),
    ]
    for old,new in replacements:
        if old not in before:raise ValueError('Expected worker source anchor missing')
        before=before.replace(old,new,1)
    if candidate!=before:raise ValueError('Candidate includes unrelated worker changes')
    stage=Path(tempfile.mkdtemp(prefix='.upload-idle-worker-',dir=destination.parent))
    try:
        shutil.copytree(base,stage,dirs_exist_ok=True);content=candidate.encode();(stage/CHANGED).write_bytes(content)
        manifest['files'][CHANGED]={'bytes':len(content),'sha256':sha(content)}
        result=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode();(stage/'files-service.json').write_bytes(result)
        for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
        stage.rename(destination)
        return {'directory':str(destination),'manifestSHA256':sha(result),'changed':[CHANGED]}
    finally:
        if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:print(json.dumps(build(a.base,a.output),indent=2))
    except (ValueError,OSError,subprocess.CalledProcessError) as error:p.error(str(error))
