#!/usr/bin/env python3
"""Keep paused6ded and bridge952; remove exact obsolete b3/5ac code only."""
import fcntl,hashlib,importlib.util,json,os,shutil,socket,time,tomllib
from pathlib import Path
CURRENT='6ded1364d04182b48d3fc8b65f6d1dd24a5d322d3cf91b1dda853d05794e1bf9'
BASE='952fe21dfa990b63323f0d9dad597cab8d9a5604ea7fe519bf5547aef4e0a063'
OLD=['b3c292a13b6a7c1d69f15d9c23c27a15d58009646ae030e1a7806607abcbb897','5ac541f0e439dc0808ece01115f4aa1307e6e531449bddd7c38bfd8175c5329e']
def main():
 assert os.geteuid()==0 and socket.gethostname()=='box-webhost'
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 helper=Path('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py');assert sha(helper)==helper.parent.name
 spec=importlib.util.spec_from_file_location('pause_retention',helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.protected(helper)
 with (m.HOST/'.controller.lock').open('rb') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  config=m.CONTROL.read_bytes();c=json.loads(config);assert c['manifestSHA256']==CURRENT and 'hostedRooms' not in c
  assert not any((m.CONTROL.parent/n).exists() for n in ['maintenance.json','native-rollout.json','site-cutover.json'])
  assert next(s for s in tomllib.loads((m.HOST/'sites.toml').read_text())['sites'] if s['domain']=='ksu.codes')['codi_chat_disabled'] is True
  for unit in ['codi-rooms-ksu.service','codi-readers-ksu.service','codi-readers-ksu-refresh.timer']:assert m.run(['systemctl','show',unit,'-p','ActiveState','--value'])=='inactive'
  pins=m.hosting_pins();before=m.capture(c);database=Path('/var/lib/codi-rooms/ksu/rooms.sqlite3');dbpin=sha(database)
  def graph(pin):
   root=Path('/srv/codi-connected/releases/native25-'+pin[:16]);m.protected(root);assert sha(root/'connected-release.json')==pin
   records=json.loads((root/'connected-release.json').read_bytes())['files'];assert {str(p.relative_to(root)) for p in root.rglob('*') if not p.is_dir()}==set(records)|{'connected-release.json'}
   for n,r in records.items():
    p=root/n;m.protected(p);assert not p.is_symlink() and p.stat().st_nlink==1 and r=={'bytes':p.stat().st_size,'sha256':sha(p)}
   return root
  for pin in [CURRENT,BASE]:graph(pin)
  targets=[graph(pin) for pin in OLD if Path('/srv/codi-connected/releases/native25-'+pin[:16]).exists()]
  for proc in Path('/proc').glob('[0-9]*'):
   try:
    assert not any(str(p).encode() in (proc/'cmdline').read_bytes() for p in targets),str(proc)
    for node in [proc/'cwd',proc/'exe',*(proc/'fd').iterdir()]:
     try:assert not any(os.readlink(node).startswith(str(p)) for p in targets),str(node)
     except OSError:pass
   except (FileNotFoundError,ProcessLookupError):pass
  for node in Path('/etc/systemd/system').rglob('*'):
   if node.is_symlink() or not node.is_file():continue
   raw=node.read_bytes();assert not any(str(p).encode() in raw for p in targets),str(node)
  removed=[]
  for root in targets:
   size=sum(p.stat().st_size for p in root.rglob('*') if p.is_file());shutil.rmtree(root);removed.append({'path':str(root),'bytes':size})
  assert m.CONTROL.read_bytes()==config and m.hosting_pins()==pins and sha(database)==dbpin
  m.preserved(before,c)
  return {'status':'PASS','removed':removed,'codeBytesRemoved':sum(v['bytes'] for v in removed),'current':CURRENT,'retainedDevelopmentBase':BASE,'privateStateUnchanged':True,'servicesRestarted':False,'liveChatReenabled':False}
if __name__=='__main__':
 result=main();out=Path('/srv/codi-connected')/('paused-code-retention-'+str(time.time_ns())+'-result.json');fd=os.open(out,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w') as f:json.dump(result,f,indent=2)
 print(json.dumps(result|{'rootReceipt':str(out),'rootReceiptSHA256':hashlib.sha256(out.read_bytes()).hexdigest()}))
