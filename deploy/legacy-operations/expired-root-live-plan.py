#!/usr/bin/env python3
"""Read-only expired-steward preflight; no signing, restarts, or data writes."""
import hashlib,json,shlex,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
classifier=(ROOT/'origin_service/expired_root_steps.py').read_text()
remote=r'''
import hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
P=Path
assert os.geteuid()==0
config_path=P('/etc/codi-connected/ksu/managed.json');raw=config_path.read_bytes();config=json.loads(raw);release=P(config['release'])
sys.path.insert(0,str(release));spec=importlib.util.spec_from_file_location('managed_preflight',release/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)
from origin_service import maintenance
from steward.root_authority import RootAuthority
from steward.protocol import jose
from steward.provision import verified_seed
exec(__CLASSIFIER__,globals())
with op.locked(config_path):
 c=op.load(config_path);assert c==config and c['origin']=='https://ksu.codes' and c['basePath']==''
 maintenance.require_clean(op,config_path);bindings=maintenance.binding(c['stateRoot']);fence=maintenance.fence(op,c,config_path,bindings)
 state=P(c['stateRoot']);a=RootAuthority(state/'operator/root');root=a.provision();staged=jose.loads((state/'operator/staging/steward-private/provisioned/provision.json').read_bytes());live=jose.loads((state/'steward/provision.json').read_bytes())
 observed=[]
 for item in [root,staged,live]:
  seed=jose.inspect(item['seed'],'codi-seed/1',32768)[1];verified_seed(item['seed'],root['root_key'],root['realm'],seed['iat']);observed.append((seed,hashlib.sha256(item['seed'].encode()).hexdigest()))
 unit=op.unit(c,'steward');status=dict(line.split('=',1) for line in op.systemctl('show',unit,'-p','ActiveState','-p','SubState','-p','Result','-p','MainPID').splitlines());running=status['ActiveState']=='active'
 action=next_step(base_revision=4,target_revision=5,root_revision=observed[0][0]['revision'],fence_revision=fence['rootFloor'],staged_revision=observed[1][0]['revision'],live_revision=observed[2][0]['revision'],base_hash=observed[0][1],root_hash=observed[0][1],staged_hash=observed[1][1],live_hash=observed[2][1],root_expired=time.time()>=observed[0][0]['exp'],steward_running=running,bindings_verified=True,ledger_verified=True)
 checkpoint=make_checkpoint(root);assert inspect_signed_exports(root,staged,live,checkpoint,fence_revision=fence['rootFloor'],now=int(time.time()),steward_running=running,ledger_verified=True)==action
 db=maintenance.ro_db(state/'steward/ledger/publisher.sqlite3')
 try:publisher_row=db.execute('SELECT binding,seed_revision,seed_hash,revision,token,frozen FROM publisher WHERE id=1').fetchone()
 finally:db.close()
 assert verify_publisher(publisher_row,root,live,checkpoint,minimum_revision=bindings['publisherRevision'])['publisherRevision']==bindings['publisherRevision']
 print(json.dumps({'status':'PASS','scope':'Read-only authority binding, publisher ledger and expired steward preflight','nextStep':action,'rootRevision':observed[0][0]['revision'],'fenceRevision':fence['rootFloor'],'publisherRevision':bindings['publisherRevision'],'accountsCount':bindings['accounts'],'rootExpired':time.time()>=observed[0][0]['exp'],'stewardState':status,'basePath':c['basePath'],'nativeManifestSHA256':c['manifestSHA256'],'configSHA256':hashlib.sha256(raw).hexdigest(),'liveChanged':False,'signingPerformed':False}))
'''
if __name__=='__main__':
 bootstrap="import json,os,pathlib,sys;c=json.loads(pathlib.Path('/etc/codi-connected/ksu/managed.json').read_bytes());code=sys.stdin.read();os.execv(c['python'],[c['python'],'-I','-B','-c',code])"
 code=remote.replace('__CLASSIFIER__',repr(classifier));child=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=5','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(bootstrap)],input=code,text=True,capture_output=True,timeout=30)
 if child.returncode:raise RuntimeError('Read-only preflight failed: '+child.stderr[-4000:])
 result=json.loads(child.stdout);result['classifierSHA256']=hashlib.sha256(classifier.encode()).hexdigest();out=ROOT/'.build/checks/expired-root-live-plan-r6-result.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
