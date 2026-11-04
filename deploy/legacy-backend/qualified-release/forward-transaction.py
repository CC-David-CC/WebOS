"""Main-only forward restriction atop the existing managed hosting transaction.

Research binding only: caller must supply pinned protected webctl, same held host
lock, custody/inventory/health checks and an exclusive main-specific journal.
No CLI, installation or live mutation is provided.
"""
import contextlib,copy,hashlib,tomllib
from pathlib import Path

OLD_SELECTOR="0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020"
NEW_SELECTOR="e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480"
PINS={"common":"d11755a183bc5c12803b6fdc84fa54f4803c0f10c415c07bb9eecc82699132a1","old_manifest":"2c3987d449d0d11f69973bf23652cf1fc125127fbb871147c0d71e563eb8434f","new_manifest":"1f53b9caf4fd63631e7d4df2bfdab518dca98744ecc4a7247bd4818b328b374f","old_caddy":"95cecea4a8217afaa6e60e7aee28a5ad01fa9158997f0051cb96626f9916fc48","new_caddy":"f63f92d0994b9ad82899d1c808ee6fdf59e013769a9ee0364cbd21554ae7e53b"}

def digest(value):return hashlib.sha256(value).hexdigest()
def validate_endpoints(ctl,old,new,old_selector,new_selector):
 if (old_selector,new_selector)!=(OLD_SELECTOR,NEW_SELECTOR):raise ValueError('Unexpected selector pins')
 if set(old)!={'common','manifest','caddy'} or set(new)!=set(old) or old['common']!=new['common']:raise ValueError('Exact hosting endpoints required')
 if digest(old['common'])!=PINS['common'] or any(digest(endpoint[key])!=PINS[label+'_'+key] for label,endpoint in [('old',old),('new',new)] for key in ('manifest','caddy')):raise ValueError('Hosting endpoint pin mismatch')
 a=tomllib.loads(old['manifest'].decode());b=tomllib.loads(new['manifest'].decode());expected=copy.deepcopy(a)
 matches=[s for s in expected['sites'] if s.get('domain')=='ksu.codes']
 if len(matches)!=1 or matches[0].get('codi_simplified')!=old_selector:raise ValueError('Unexpected old main selector')
 matches[0]['codi_simplified']=new_selector
 if expected!=b:raise ValueError('Only main selector may change')
 for data,record in ((a,old),(b,new)):
  ctl.validate(data)
  if ctl.dump(data).encode()!=record['manifest'] or ctl.caddy(data,'production').encode()!=record['caddy']:raise ValueError('Generated hosting endpoint mismatch')
 if ctl._beta_block(old['caddy'].decode())!=ctl._beta_block(new['caddy'].decode()):raise ValueError('Beta route changed')
 return a,b

class ForwardAdapter:
 """Wraps ManagedWebctlAdapter under its existing held lock and checks.

 Restore writes to the old active Caddyfile are refused after the durable
 forward journal. A failed reload can leave the running server on its prior
 configuration; the pending journal means blocked/unverified, not success.
 """
 def __init__(self,inner,check_candidate,check_floor):
  if not callable(check_candidate) or not callable(check_floor):raise ValueError('Mandatory custody and floor checks')
  self.inner=inner;self.check_candidate=check_candidate;self.check_floor=check_floor
 @contextlib.contextmanager
 def held(self):
  self.inner.check_lock();yield
 def __getattr__(self,name):return getattr(self.inner,name)
 def apply_caddy(self,manifest,common,recovery=False):
  self.inner.check_lock();self.check_floor();self.check_candidate()
  ctl=self.inner.ctl;data=tomllib.loads(manifest.decode());expected=ctl.caddy(data,'production').encode();active=Path(self.inner.paths['caddy']);prior=ctl.write
  def forward_write(path,content,*args,**kwargs):
   raw=content.encode() if isinstance(content,str) else content
   if Path(path)==active and raw!=expected:raise RuntimeError('Refused Caddy rollback after main forward journal; recover forward')
   return prior(path,content,*args,**kwargs)
  try:
   ctl.write=forward_write
   self.inner.apply_caddy(manifest,common,recovery=recovery)
  finally:ctl.write=prior
  self.check_floor();self.check_candidate()

def apply(tx,adapter,old,new,old_selector,new_selector):
 if tx.io is not adapter:raise ValueError('Wrong transaction adapter')
 adapter.check_lock();adapter.check_floor();adapter.check_candidate();validate_endpoints(adapter.inner.ctl,old,new,old_selector,new_selector)
 # Existing version-2 gate-only journal provides exact-endpoint, always-forward
 # recovery. This must have a distinct main-only path and trusted binding; it
 # must never be presented to the beta gate recovery entrypoint.
 tx.apply_gate(old,new)

def recover(tx,adapter,old,new,old_selector,new_selector):
 if tx.io is not adapter:raise ValueError('Wrong transaction adapter')
 adapter.check_lock();adapter.check_floor();adapter.check_candidate();validate_endpoints(adapter.inner.ctl,old,new,old_selector,new_selector)
 tx.recover_gate(old,new)
