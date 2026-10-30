#!/usr/bin/env python3
"""Remove a reviewed list of obsolete, unreferenced native27 test releases."""
import fcntl,hashlib,json,os,pathlib,re,shutil,stat,time
P=pathlib.Path;BASE=P('/srv/codi-connected/releases');CFG=P('/etc/codi-connected/ksu/managed.json');LOCK=P('/home/dflanag3/webhost-sites/.controller.lock')
ACTIVE='native27-chat-channel-drafts-r1';PIN='1ba4f1715fd5ff91b4051ad7004ea16d5a945b49e67089ca5f177e9b673aad46'
NAMES='''native27-author-batching-r1 native27-author-names-r1 native27-ban-review-r1 native27-batch-history-r1 native27-catchup-busy-r1 native27-catchup-diagnostic-r2 native27-catchup-hash-r1 native27-catchup-hash-r2 native27-catchup-hash-r3 native27-chat-layout-r1 native27-chat-older-r2 native27-chat-progress-r1 native27-chat-race-r1 native27-chat-receipt-r2 native27-chat-sent-r1 native27-checkpoint-cache-r1 native27-chess-chat-state-r2 native27-chess-history-r1 native27-chess-history-r2 native27-chess-lifecycle-r1 native27-chess-loading-r1 native27-chess-replay-r1 native27-chess-retirement-r1 native27-chess-rotation-r1 native27-chess-switch-r1 native27-early-busy-r1 native27-early-chat-r1 native27-fast-poll-r1 native27-fast-priority-r1 native27-fast-server-r1 native27-node-cache-r1 native27-official-chat-wake-r1 native27-online-retry-r2 native27-receipt-smoothing-r1 native27-reconnect-early-r1 native27-server-only-chat-r1 native27-shared-chat-rate-r1 native27-verified-ids-r1'''.split()
def main():
 assert os.geteuid()==0 and BASE.is_dir() and not BASE.is_symlink() and len(set(NAMES))==len(NAMES)
 with LOCK.open('r+') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  before=CFG.read_bytes();config=json.loads(before);assert config['release']==str(BASE/ACTIVE) and config['manifestSHA256']==PIN
  assert not any((CFG.parent/n).exists() for n in ('maintenance.json','native-rollout.json','site-cutover.json'))
  roots=[BASE/n for n in NAMES];needles=[str(p).encode()+b'/' for p in roots];names=[str(p).encode() for p in roots]
  for directory in (P('/etc/systemd/system'),P('/etc/codi-connected'),P('/etc/caddy')):
   if not directory.exists():continue
   for p in directory.rglob('*'):
    if p.is_symlink() or not p.is_file():continue
    assert p.stat().st_size<10*1024*1024, 'Cannot inspect config: '+str(p)
    data=p.read_bytes();assert not any(re.search(re.escape(n)+rb'(?![A-Za-z0-9_-])',data) for n in names), 'Referenced by '+str(p)
  for process in P('/proc').glob('[0-9]*'):
   try:
    cmd=(process/'cmdline').read_bytes();assert not any(n in cmd for n in names),'Running process '+str(process)
    nodes=[process/'cwd',process/'exe',*(process/'fd').iterdir()]
    for node in nodes:
     try:
      target=os.readlink(node).encode();assert not any(target==n or target.startswith(prefix) for n,prefix in zip(names,needles)),'Open process reference '+str(node)
     except (FileNotFoundError,PermissionError,ProcessLookupError):pass
   except (FileNotFoundError,PermissionError,ProcessLookupError):pass
  removed=[]
  for root in roots:
   assert root.parent==BASE and re.fullmatch(r'native27-[a-z0-9-]+',root.name) and root.is_dir() and not root.is_symlink() and root.stat().st_uid==0
   manifest=root/'connected-release.json';assert manifest.is_file() and not manifest.is_symlink();data=json.loads(manifest.read_bytes());assert data['version']=='codi-connected-development/27'
   size=0
   for node in root.rglob('*'):
    info=node.lstat();assert info.st_uid==0 and not stat.S_ISLNK(info.st_mode) and (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode))
    if stat.S_ISREG(info.st_mode):assert info.st_nlink==1;size+=info.st_size
   removed.append({'name':root.name,'bytes':size,'manifestSHA256':hashlib.sha256(manifest.read_bytes()).hexdigest()})
  for root in roots:shutil.rmtree(root)
  assert CFG.read_bytes()==before
  result={'status':'PASS','removed':removed,'bytes':sum(x['bytes'] for x in removed),'active':ACTIVE,'retainedRollback':'native27-chat-unicode-r1','servicesRestarted':False,'time':int(time.time())}
  receipt=P('/srv/codi-connected')/('native27-cleanup-'+str(time.time_ns())+'.json');fd=os.open(receipt,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
  with os.fdopen(fd,'w') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  return result|{'receipt':str(receipt)}
if __name__=='__main__':print(json.dumps(main()))
