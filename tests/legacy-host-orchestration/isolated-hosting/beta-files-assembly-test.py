#!/usr/bin/env python3
"""Combined transaction/process fixture; no live files, services or keys."""
import contextlib,fcntl,json,os,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'ops'))
from beta_transaction import Transaction,_decode,_encode
from opfs_managed import HeldAdapter,ManagedBinding
from opfs_floor import FloorJournal
from opfs_gate_rescue import GateRescue
from beta_files_assembly import FilesAssembly,IssuerInstall
import beta_issuer_switch as issuer,beta_service_operator as svc
plan={'origin':svc.ORIGIN,'ports':svc.PORTS,'network':'disabled','native_release':'/srv/codi-connected/releases/microduck-issuer-'+issuer.OLD,'native_manifest':issuer.OLD,'worker_release':'/srv/codi-gateway/releases/'+svc.GATEWAY_MANIFEST,'worker_manifest':svc.GATEWAY_MANIFEST,'python':'/srv/codi-connected/venvs/517179c/bin/python','issuer_policy_sha256':'71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca','guest_source_sha256':svc.GUEST_SOURCE};unit_bytes=svc.render_units(plan);old_unit=unit_bytes[issuer.UNIT_NAMES[0]].encode();new_unit=issuer.derive(old_unit)
def snapshots(name):return {k:(name+'-'+k).encode() for k in ('common','manifest','caddy')}
pre,normal,gate,candidate=map(snapshots,('pre','normal','gate','candidate'))
with tempfile.TemporaryDirectory(prefix='opfs-assembled-') as temp:
 for killed in ('normalized','journaled','gated','floor','issuer-unit-written','forward','complete','finalize-failure'):
  t=Path(temp)/killed;t.mkdir(mode=0o700);routes=t/'routes';routes.mkdir();units=t/'units';units.mkdir();lock=t/'lock';lock.touch();unitstate=t/'unitstate';unitstate.write_text(json.dumps({n:'active' for n in issuer.UNIT_NAMES}));log=t/'log';log.write_text('')
  for k,v in pre.items():(routes/k).write_bytes(v)
  for n,v in unit_bytes.items():(units/n).write_text(v);(units/n).chmod(0o644)
  state={'lock':None,'timer':{'active':True,'enabled':True}}
  @contextlib.contextmanager
  def held():
   assert state['lock'] is None;f=lock.open('r');fcntl.flock(f,fcntl.LOCK_EX);state['lock']=f
   try:yield
   finally:state['lock']=None;f.close()
  def check():
   if state['lock'] is None:raise ValueError('host lock absent')
  class Routes:
   def held(self):return held()
   def check_lock(self):check()
   def read(self):return {k:(routes/k).read_bytes() for k in pre}
   def beta_ready(self):pass
   def backup(self,old):return 'fixture-backup'
   def timer_snapshot(self):return dict(state['timer'])
   def timer_stop_if_active(self,old):state['timer']['active']=False
   def assert_renewal_quiescent(self):pass
   def timer_assert_recoverable(self,old):pass
   def timer_restore(self,old):state['timer']=dict(old)
   def replace_source(self,k,v):(routes/k).write_bytes(v)
   def apply_caddy(self,manifest,common,*,recovery=False):
    choices=(pre,normal,gate,candidate);match=next(x for x in choices if x['manifest']==manifest and x['common']==common)
    if match==candidate and not (t/'opfs-floor.json').exists():raise AssertionError('v2 before floor')
    (routes/'caddy').write_bytes(match['caddy']);log.open('a').write('route '+match['caddy'].decode()+'\n')
   def check_main_health(self):pass
   def check_health(self):pass
  r=Routes();nested=t/'hosting-journal'
  def run(args):
   states=json.loads(unitstate.read_text());name=args[1] if len(args)>1 else None
   if args[0]=='show':return f"ActiveState={states[name]}\nFragmentPath={units/name}\nDropInPaths=\nNeedDaemonReload=no\n"
   if args[0]=='restart':assert name==issuer.UNIT_NAMES[0] and (t/'opfs-floor.json').exists() and r.read()==gate;states[name]='active';unitstate.write_text(json.dumps(states));return ''
   if args[0]=='daemon-reload':assert (t/'opfs-floor.json').exists() and r.read()==gate;return ''
   if args[0]=='start':states[name]='active';unitstate.write_text(json.dumps(states));return ''
   raise AssertionError(args)
  def gatecheck():
   check()
   if not (t/'opfs-floor.json').exists() or r.read()!=gate:raise ValueError('issuer needs floor and gate')
  switching=issuer.IssuerSwitch(unit_dir=units,journal=t/'issuer-journal',check_lock=check,check_floor_gate=gatecheck,verify_release=check,health=check,run=run)
  orig_apply=switching.apply
  def observed_apply(*,retain=True,phase=lambda _:None):
   return orig_apply(retain=retain,phase=lambda x:os._exit(17) if killed=='issuer-'+x else phase(x))
  switching.apply=observed_apply
  install=IssuerInstall(switching,old_unit)
  def make(old,new):return Transaction(HeldAdapter(r,check),nested)
  def prepare(floor):
   if not nested.exists():return
   j=json.loads(nested.read_bytes());a,b=_decode(j['old']),_decode(j['new'])
   if floor and (a==normal or b==normal):raise ValueError('old routes after floor')
   Transaction(HeldAdapter(r,check),nested).recover()
  rescue=GateRescue(r,check,t/'emergency-journal',candidate,gate,check,check)
  def gate_health():assert r.read()==gate
  def v2_health():assert (t/'opfs-floor.json').exists() and r.read()==candidate and (units/issuer.UNIT_NAMES[0]).read_bytes()==new_unit
  binding=ManagedBinding(held,check,{'baseline':normal,'gate':gate,'candidate':candidate},make,r.read,prepare,lambda:(t/'opfs-floor.json').exists(),lambda rec,mode:check(),gate_health,lambda rec:v2_health(),lambda rec:None,install,rescue)
  floor=FloorJournal(binding,t);assembly=FilesAssembly(floor=floor,issuer=switching,installer=install,issuer_old=old_unit,normal_adapter=r,normal_journal=t/'normalize-journal',normal_old=pre,normal_new=normal,v2_health=v2_health,pre_normalization=check,pre_normalization_recovery=check)
  if killed=='finalize-failure':
   assembly.v2_health=lambda:(_ for _ in ()).throw(ValueError('final health unavailable'))
   try:assembly.apply('a'*64,'b'*64);raise AssertionError('failed final health accepted')
   except RuntimeError as error:assert 'maintenance gate verified' in str(error)
   assert r.read()==gate and (t/'opfs-floor.json').exists() and not (t/'opfs-transition.json').exists() and switching.journal.exists()
   assembly.v2_health=v2_health
   assert assembly.recover('a'*64,'b'*64)=='v2-verified' and r.read()==candidate and not switching.journal.exists()
   continue
  if killed=='normalized':
   def reject_before_normalization():check();raise ValueError('preflight rejected')
   rejected=FilesAssembly(floor=floor,issuer=switching,installer=install,issuer_old=old_unit,normal_adapter=r,normal_journal=t/'normalize-journal',normal_old=pre,normal_new=normal,v2_health=v2_health,pre_normalization=reject_before_normalization,pre_normalization_recovery=check)
   try:rejected.apply('a'*64,'b'*64);raise AssertionError('failed preflight accepted')
   except ValueError as e:assert str(e)=='preflight rejected'
   assert r.read()==pre and not (t/'normalize-journal').exists() and not (t/'opfs-transition.json').exists()
  pid=os.fork()
  if pid==0:
   try:assembly.apply('a'*64,'b'*64,phase=lambda x:os._exit(17) if x==killed else None)
   except BaseException:
    import traceback;traceback.print_exc();os._exit(18)
   os._exit(19)
  _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==17,(killed,status)
  result=assembly.recover('a'*64,'b'*64)
  if killed=='normalized':
   # Even a correctly shaped journal cannot cause writes before custody checks.
   good=json.dumps({'version':1,'phase':'prepared','old':_encode(pre),'new':_encode(normal),'timer':{'active':True,'enabled':True},'caddy_started':False,'backup':'fixture'}).encode();j=t/'normalize-journal';j.write_bytes(good);j.chmod(0o600);before=r.read()
   def reject_recovery():check();raise ValueError('recovery custody rejected')
   guarded=FilesAssembly(floor=floor,issuer=switching,installer=install,issuer_old=old_unit,normal_adapter=r,normal_journal=j,normal_old=pre,normal_new=normal,v2_health=v2_health,pre_normalization=check,pre_normalization_recovery=reject_recovery)
   try:guarded.recover('a'*64,'b'*64);raise AssertionError('failed recovery custody accepted')
   except ValueError as e:assert str(e)=='recovery custody rejected'
   assert j.read_bytes()==good and r.read()==before;j.unlink()
   # Never hand an unpinned normalization record to generic v1 recovery.
   bad=json.dumps({'version':1,'phase':'prepared','old':_encode(candidate),'new':_encode(normal),'timer':{'active':True,'enabled':True},'caddy_started':False,'backup':'fixture'}).encode();j=t/'normalize-journal';j.write_bytes(bad);j.chmod(0o600);before=r.read()
   try:assembly.recover('a'*64,'b'*64);raise AssertionError('unpinned normalization recovery accepted')
   except ValueError as error:assert 'Unpinned normalization journal' in str(error)
   assert j.read_bytes()==bad and r.read()==before;j.unlink()
  if killed in ('normalized','journaled','gated'):
   assert result=='pre-floor' and not (t/'opfs-floor.json').exists() and not switching.journal.exists() and r.read()==normal,(killed,result,r.read())
  else:
   assert result=='v2-verified' and (t/'opfs-floor.json').exists() and not switching.journal.exists();v2_health()
   if killed=='complete':
    healthy=assembly.v2_health;assembly.v2_health=lambda:(_ for _ in ()).throw(ValueError('candidate unavailable'))
    original_ready=r.beta_ready;r.beta_ready=lambda:(_ for _ in ()).throw(ValueError('gate unavailable'))
    try:assembly.recover('a'*64,'b'*64);raise AssertionError('unverified gate reported as safe')
    except RuntimeError as error:assert 'gate closure unverified' in str(error)
    assert r.read()==candidate
    r.beta_ready=original_ready
    try:assembly.recover('a'*64,'b'*64);raise AssertionError('unhealthy candidate accepted')
    except RuntimeError as error:assert 'maintenance gate verified' in str(error)
    assert r.read()==gate and not (t/'opfs-transition.json').exists()
    assembly.v2_health=healthy
    assert assembly.recover('a'*64,'b'*64)=='v2-verified' and r.read()==candidate
    floorpath=t/'opfs-floor.json';saved=floorpath.read_bytes();floorpath.write_text('{}');before=r.read()
    try:assembly.recover('a'*64,'b'*64);raise AssertionError('malformed floor accepted')
    except ValueError:pass
    assert r.read()==before;floorpath.write_bytes(saved)
print('PASS assembled floor/issuer/route fixture: seven process deaths and no v2/issuer before durable floor')
