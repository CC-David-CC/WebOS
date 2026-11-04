"""Main selector-only inventory guard; requires caller-pinned generators/lock."""
import copy,re
from pathlib import Path
from render_inventory import read_regular

def block(text,domain):
 matches=list(re.finditer(r'(?m)^(?:https?://)?'+re.escape(domain)+r'(?::[0-9]+)? \{',text))
 if len(matches)!=1:raise ValueError('Expected exactly one site block')
 start=matches[0].start();end=text.find('\n}\n',start)
 if end<0:raise ValueError('Incomplete site block')
 return text[start:end+3]
def without(text,domain):return text.replace(block(text,domain),'',1)
class MainRenderInventory:
 def __init__(self,root,caddy_dir,gen,old,new,old_selector,new_selector,*,owner_uid,owner_gid,caddy_uid=0,caddy_gid):
  expected=copy.deepcopy(old);sites=[s for s in expected['sites'] if s.get('domain')=='ksu.codes']
  if len(sites)!=1 or sites[0].get('codi_simplified')!=old_selector:raise ValueError('Unexpected baseline main selector')
  sites[0]['codi_simplified']=new_selector
  if expected!=new:raise ValueError('Only exact main selector may change')
  gen.validate(old);gen.validate(new);self.old=old;self.new=new;self.targets={};root=Path(root);caddy_dir=Path(caddy_dir)
  def add(path,a,b,meta):
   if path in self.targets:raise ValueError('Duplicate target')
   self.targets[path]=(a.encode(),b.encode(),meta)
  for mode in ('prepare','production'):
   before=gen.caddy(old,mode);after=gen.caddy(new,mode)
   if without(before,'ksu.codes')!=without(after,'ksu.codes') or block(before,'beta.ksu.codes')!=block(after,'beta.ksu.codes'):raise ValueError('Unrelated generated site changed')
   add(root/'deploy/caddy'/('Caddyfile.'+mode),before,after,(owner_uid,owner_gid,0o644));add(caddy_dir/('Caddyfile.'+mode),before,after,(caddy_uid,caddy_gid,0o640))
  for a,b in zip(old['sites'],new['sites'],strict=True):
   first=gen.unit(a);second=gen.unit(b)
   if first!=second:raise ValueError('Service unit changed')
   add(root/'deploy/systemd'/a['service'],first,second,(owner_uid,owner_gid,0o644))
 def check(self,data,*,recovery=False,after=False):
  if data not in (self.old,self.new):raise ValueError('Unreviewed render data')
  for path,(old,new,metadata) in self.targets.items():
   value,observed=read_regular(path);allowed=((new,) if data==self.new else (old,)) if after else ((old,new) if recovery else (old,))
   if observed!=metadata or value not in allowed:raise ValueError('Unexpected generated render target: '+str(path))
