#!/usr/bin/env python3
"""Actual managed Transaction/adapter with disposable Caddy and protected files."""
import contextlib,fcntl,importlib.util,json,os,subprocess,sys,tempfile,time,tomllib,types,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'ops'))
from beta_transaction import Transaction,ManagedWebctlAdapter,_decode,_encode
from opfs_floor import FloorJournal
from opfs_managed import HeldAdapter,ManagedBinding
from opfs_gate_rescue import GateRescue
from opfs_recovery_entry import recover_legacy
CADDY=os.environ.get('CODI_CADDY','/tmp/codi-microduck-hosting-evidence/caddy');PORT=19988;ADMIN=19989
class Timer:
 def __init__(self):self.state={'active':True,'enabled':True}
 def snapshot(self):return dict(self.state)
 def stop_if_active(self,old):assert self.state==old;self.state['active']=False
 def assert_quiescent(self):pass
 def assert_recoverable(self,old):assert self.state in (old,{**old,'active':False})
 def restore(self,old):self.state=dict(old)
def caddy_bytes(state):return ('{\n admin 127.0.0.1:'+str(ADMIN)+'\n}\nhttp://127.0.0.1:'+str(PORT)+' {\n respond "'+state+'" 200\n}\n').encode()
with tempfile.TemporaryDirectory(prefix='codi-managed-floor-') as tmp:
 t=Path(tmp);os.chmod(t,0o700);(t/'lock').touch();paths={k:t/k for k in ('common','manifest','caddy')};source=b'generated-by-fixture';snap={s:{'common':source,'manifest':('profile="'+s+'"\n').encode(),'caddy':caddy_bytes(s)} for s in ('baseline','gate','candidate')}
 for k,v in snap['baseline'].items():paths[k].write_bytes(v)
 proc=subprocess.Popen([CADDY,'run','--config',str(paths['caddy']),'--adapter','caddyfile'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE);lockstate={'fd':None,'count':0};timer=Timer()
 def response():
  with urllib.request.urlopen('http://127.0.0.1:'+str(PORT)+'/',timeout=2) as f:return f.read().decode()
 for _ in range(100):
  try:
   if response()=='baseline':break
  except OSError:time.sleep(.05)
 else:raise RuntimeError('Caddy fixture failed')
 @contextlib.contextmanager
 def held():
  assert lockstate['fd'] is None,'host lock reacquired';f=open(t/'lock','r+');fcntl.flock(f,fcntl.LOCK_EX);lockstate['fd']=f;lockstate['count']+=1
  try:yield
  finally:lockstate['fd']=None;f.close()
 def check():
  if lockstate['fd'] is None:raise ValueError('host lock missing')
 applied=[]
 class Ctl:
  caddy=dump=validate=None
  def run(self,*args,**kwargs):pass
  def caddy_apply(self,data,mode):
   assert mode=='production';applied.append(data['profile']);out=caddy_bytes(data['profile']);paths['caddy'].write_bytes(out)
   subprocess.run([CADDY,'validate','--config',str(paths['caddy']),'--adapter','caddyfile'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   subprocess.run([CADDY,'reload','--address','127.0.0.1:'+str(ADMIN),'--config',str(paths['caddy']),'--adapter','caddyfile'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   assert response()==data['profile']
 gen=types.SimpleNamespace(source=source,module=types.SimpleNamespace(validate=lambda data:None,caddy=lambda *args:None,dump=lambda *args:None));adapter=ManagedWebctlAdapter(Ctl(),gen,gen,paths,timer,held,check,lambda:None,lambda:None,lambda:None,lambda *a,**kw:None,lambda:None,lambda old:'fixture-backup');nested=t/'nested-journal';inject={'phase':None};gate_calls=[]
 def make(old,new):
  tx=Transaction(HeldAdapter(adapter,check),nested);apply=tx.apply
  def run(o,n):
   def phase(name):
    if inject['phase']==name:inject['phase']=None;raise RuntimeError('fault inside actual managed transaction')
   return apply(o,n,phase=phase)
  original_gate=tx.apply_gate
  def run_gate(o,n,**kw):gate_calls.append((o,n));return original_gate(o,n,**kw)
  tx.apply=run;tx.apply_gate=run_gate;return tx
 def prepare(floor):
  if not nested.exists():return
  j=json.loads(nested.read_bytes());old,new=_decode(j['old']),_decode(j['new'])
  if floor and (old==snap['baseline'] or new==snap['baseline']):raise ValueError('Unsafe nested rollback past v2 floor')
  if (old,new) not in [(snap[a],snap[b]) for a,b in (('baseline','gate'),('gate','baseline'),('gate','candidate'),('candidate','gate'))]:raise ValueError('Unpinned nested journal')
  tx=Transaction(HeldAdapter(adapter,check),nested)
  if j.get('version')==2:
   if not floor or (old,new)!=(snap['candidate'],snap['gate']):raise ValueError('Unpinned gate-only journal')
   tx.recover_gate(snap['candidate'],snap['gate'])
  elif floor and (old,new)==(snap['gate'],snap['candidate']):tx.recover_old_gate(snap['gate'],snap['candidate'])
  else:tx.recover()
 def health(expected):assert response()==expected
 rescue=GateRescue(adapter,check,t/'emergency-journal',snap['candidate'],snap['gate'],lambda:None,lambda:None)
 binding=ManagedBinding(held,check,snap,make,adapter.read,prepare,lambda:(t/'opfs-floor.json').exists(),lambda rec,mode:None,lambda:health('gate'),lambda rec:health('candidate'),lambda rec:health('baseline'),lambda rec:(t/'issuer').write_text('candidate'),rescue)
 op=FloorJournal(binding,t)
 try:
  # Before any floor, the same protected dispatch still permits a reviewed,
  # pinned ordinary prepared recovery through the existing transaction.
  fixture_journal=json.dumps({'version':1,'phase':'prepared','old':_encode(snap['baseline']),'new':_encode(snap['gate']),'timer':timer.snapshot(),'caddy_started':False,'backup':'fixture'}).encode();nested.write_bytes(fixture_journal)
  def verify_legacy():check();assert nested.read_bytes()==fixture_journal
  recover_legacy(managed=adapter,host_lock=held,check_lock=check,floor_path=t/'opfs-floor.json',check_floor_custody=check,verify_journal=verify_legacy,journal=nested)
  assert response()=='baseline' and not nested.exists()
  lockstate['count']=0
  inject['phase']='common-written'
  # Inject into the second transaction, after gate and persistent floor.
  def phase(s):
   if s=='gated':inject['phase']='common-written'
  inject['phase']=None
  try:op.apply('a'*64,'b'*64,phase=phase);raise AssertionError('expected fault')
  except RuntimeError:pass
  assert response()=='gate' and op.floor.exists() and op.journal.exists();assert not nested.exists();assert lockstate['count']==1
  op.recover('a'*64,'b'*64);assert response()=='candidate' and op.floor.exists() and not op.journal.exists();assert lockstate['count']==2
  # A committed forward journal must recover to the old pinned gate, not
  # replay candidate, when outer post-floor recovery requests maintenance.
  with held():binding.gate()
  with held():
   try:Transaction(HeldAdapter(adapter,check),nested).apply(snap['gate'],snap['candidate'],phase=lambda x:(_ for _ in ()).throw(RuntimeError('committed')) if x=='committed' else None)
   except RuntimeError:pass
  assert response()=='candidate' and nested.exists();applied.clear()
  try:
   with held():Transaction(HeldAdapter(adapter,check),nested).recover_old_gate(snap['baseline'],snap['candidate'])
   raise AssertionError('wrong pinned gate accepted')
  except ValueError as error:assert 'recovery policy' in str(error)
  assert response()=='candidate' and nested.exists() and not applied
  with held():binding.gate()
  assert response()=='gate' and 'candidate' not in applied and not nested.exists()
  with held():Transaction(HeldAdapter(adapter,check),t/'test-reset-journal').apply(snap['gate'],snap['candidate'])
  gate_calls.clear()
  # The ordinary binding's post-floor candidate→gate move must itself use
  # the forward-only v2 journal, including when interrupted.
  with held():
   try:Transaction(HeldAdapter(adapter,check),nested).apply_gate(snap['candidate'],snap['gate'],phase=lambda x:(_ for _ in ()).throw(RuntimeError('interrupted gate')) if x=='common-written' else None)
   except RuntimeError:pass
  assert json.loads(nested.read_bytes())['policy']=='gate-only';applied.clear()
  with held():binding.gate()
  assert response()=='gate' and 'candidate' not in applied and not nested.exists()
  with held():Transaction(HeldAdapter(adapter,check),t/'test-reset-journal').apply(snap['gate'],snap['candidate'])
  with held():binding.gate()
  assert gate_calls==[(snap['candidate'],snap['gate'])] and response()=='gate'
  with held():Transaction(HeldAdapter(adapter,check),t/'test-reset-journal').apply(snap['gate'],snap['candidate'])
  forbidden=json.dumps({'version':1,'phase':'prepared','old':_encode(snap['baseline']),'new':_encode(snap['gate']),'timer':timer.snapshot(),'caddy_started':False,'backup':'fixture'}).encode();nested.write_bytes(forbidden)
  # Candidate protected dispatch is the supported legacy recovery entry.
  # With a floor present it must never call the original transaction.
  before=adapter.read();journal_before=nested.read_bytes()
  try:
   recover_legacy(managed=adapter,host_lock=held,check_lock=check,floor_path=t/'opfs-floor.json',check_floor_custody=lambda:None,verify_journal=lambda:None,journal=nested)
   raise AssertionError('protected recovery accepted legacy floor')
  except ValueError as error:assert 'v2 floor present' in str(error)
  assert adapter.read()==before and nested.read_bytes()==journal_before and response()=='candidate'

  try:
   with held():binding.gate()
   raise AssertionError('unsafe old rollback accepted')
  except ValueError as error:assert 'Unsafe nested rollback' in str(error)
  assert response()=='gate' and nested.read_bytes()==forbidden, 'forbidden journal must be preserved while gating'
  assert timer.snapshot()=={'active':True,'enabled':True}
  try:
   with held():binding.gate()
   raise AssertionError('unsafe ordinary recovery accepted')
  except ValueError as error:assert 'Unsafe nested rollback' in str(error)
  assert response()=='gate' and nested.read_bytes()==forbidden
  # Restore candidate using the same managed authority solely to set up a
  # second independent fault; never remove or rewrite the retained evidence.
  with held():Transaction(HeldAdapter(adapter,check),t/'test-reset-journal').apply(snap['gate'],snap['candidate'])
  nested.write_text('{broken-json');before=nested.read_bytes()
  try:
   with held():binding.gate()
   raise AssertionError('malformed nested journal accepted')
  except json.JSONDecodeError:pass
  assert response()=='gate' and nested.read_bytes()==before, 'malformed journal must be preserved while gating'
  # Exercise the real gate-only journal at every durable/managed boundary.
  # The old code must reject the new version before doing any route work.
  old_source=subprocess.check_output(['git','show','ef08fe95b:research/beta-isolated-hosting/ops/beta_transaction.py'],cwd=root)
  old_module=types.ModuleType('legacy_beta_transaction');exec(compile(old_source,'legacy_beta_transaction.py','exec'),old_module.__dict__)
  for killed in ('journaled','timer-stopped','common-written','manifest-written','caddy-starting','caddy-applied','committed','timer-restored'):
   with held():Transaction(HeldAdapter(adapter,check),t/'test-reset-journal').apply(snap['gate'],snap['candidate'])
   pid=os.fork()
   if pid==0:
    try:
     with held():rescue(phase=lambda x:os._exit(17) if x==killed else None)
    finally:os._exit(18)
   _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==17,killed
   journal=t/'emergency-journal';assert journal.exists(),killed
   stored=json.loads(journal.read_bytes());assert stored['version']==2 and stored['policy']=='gate-only'
   before=nested.read_bytes();applied.clear();before_files=adapter.read()
   try:
    with held():old_module.Transaction(HeldAdapter(adapter,check),journal).recover()
    raise AssertionError('legacy reader accepted v2 gate-only journal')
   except ValueError as error:assert 'Invalid beta journal' in str(error)
   assert adapter.read()==before_files and not applied
   try:
    with held():Transaction(HeldAdapter(adapter,check),journal).recover()
    raise AssertionError('ordinary v1 recovery accepted gate-only journal')
   except ValueError as error:assert 'recovery policy' in str(error)
   try:
    with held():Transaction(HeldAdapter(adapter,check),journal).recover_gate(snap['baseline'],snap['gate'])
    raise AssertionError('untrusted candidate endpoint accepted')
   except ValueError as error:assert 'recovery policy' in str(error)
   assert adapter.read()==before_files and not applied
   with held():rescue()
   assert 'candidate' not in applied,(killed,applied)
   assert response()=='gate' and not journal.exists() and nested.read_bytes()==before,killed
  print('PASS eight actual process kills: v2-only readers reject generic recovery and never reload candidate')
  # A source outside the reviewed exact snapshots cannot be overwritten.
  with held():Transaction(HeldAdapter(adapter,check),t/'test-reset-journal').apply(snap['gate'],snap['candidate'])
  paths['manifest'].write_bytes(b'unknown-source')
  try:
   with held():rescue()
   raise AssertionError('unknown source accepted')
  except ValueError as error:assert 'Unknown or untrusted routes' in str(error)
  assert paths['manifest'].read_bytes()==b'unknown-source' and response()=='candidate'
  # Unknown timer state is refused before a managed journal/write.
  paths['manifest'].write_bytes(snap['candidate']['manifest']);timer.state={'active':'unknown','enabled':True}
  try:
   with held():rescue()
   raise AssertionError('unknown timer accepted')
  except ValueError as error:assert 'Unknown timer state' in str(error)
  assert response()=='candidate' and not (t/'emergency-journal').exists()
  timer.state={'active':True,'enabled':True}
  # Corrupt emergency journal and unverified custody cannot authorize writes.
  emergency=t/'emergency-journal';emergency.write_text('{broken');emergency.chmod(0o600)
  try:
   with held():rescue()
   raise AssertionError('corrupt emergency journal accepted')
  except json.JSONDecodeError:pass
  assert response()=='candidate' and emergency.read_text()=='{broken'
  def bad_custody():raise ValueError('custody refused')
  blocked=GateRescue(adapter,check,t/'other-emergency',snap['candidate'],snap['gate'],bad_custody,lambda:None)
  try:
   with held():blocked()
   raise AssertionError('untrusted custody accepted')
  except ValueError as error:assert 'custody refused' in str(error)
  assert response()=='candidate'
  # Deliberate bypass negative control: generic Transaction.recover knows
  # nothing of the floor and must never be exposed as an ordinary operator.
  emergency.unlink()
  with held():Transaction(HeldAdapter(adapter,check),t/'test-reset-journal').apply(snap['candidate'],snap['gate'])
  nested.write_bytes(forbidden)
  with held():Transaction(HeldAdapter(adapter,check),nested).recover()
  assert response()=='baseline'
  print('NEGATIVE CONTROL: unwrapped generic recovery resurrects old baseline; production launcher must block bypass')
  print('PASS actual managed transaction with Caddy: poisoned nested journal retained and candidate gated; unknown route refused')
 finally:
  proc.terminate();proc.wait(timeout=10)
