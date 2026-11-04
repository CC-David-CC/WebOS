"""Exact post-floor beta snapshot families; research-only, no host entrypoint."""
import copy,hashlib,tomllib
from beta_transaction import _decode
OLD='0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020'
NEW='e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480'
BETA='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
def families(snapshots,oldgen,newgen):
 result={}
 for selector in (OLD,NEW):
  family={}
  for name in ('initial','normalized','gate','candidate'):
   data=copy.deepcopy(snapshots[name+'Data']);sites=[s for s in data['sites'] if s.get('domain')=='ksu.codes']
   if len(sites)!=1 or sites[0].get('codi_simplified')!=OLD:raise ValueError('Unexpected pinned main baseline')
   sites[0]['codi_simplified']=selector;gen=newgen if name=='candidate' else oldgen;gen.module.validate(data)
   family[name]={'common':gen.source,'manifest':gen.module.dump(data).encode(),'caddy':gen.module.caddy(data,'production').encode()};family[name+'Data']=data
   if selector==OLD and family[name]!=snapshots[name]:raise ValueError('Original snapshot changed')
  result[selector]=family
 return result

def select(family_map,current,*,floor,main_journal_present,nested_journal=None):
 if main_journal_present:raise ValueError('Main restriction transaction pending')
 if set(family_map)!={OLD,NEW} or set(current)!={'common','manifest','caddy'}:raise ValueError('Invalid family inputs')
 expected_baseline=hashlib.sha256(family_map[OLD]['normalized']['manifest']).hexdigest()
 if not isinstance(floor,dict) or type(floor.get('version')) is not int or floor!={'version':1,'baseline':expected_baseline,'candidate':BETA}:raise ValueError('Beta floor identity changed')
 matches=[]
 for selector,group in family_map.items():
  gate,candidate=group['gate'],group['candidate']
  if nested_journal is None:
   if current in (gate,candidate):matches.append(selector)
   continue
  j=nested_journal
  if not isinstance(j,dict) or type(j.get('version')) is not int:continue
  try:a,b=_decode(j['old']),_decode(j['new'])
  except Exception:continue
  fields={'version','phase','old','new','timer','caddy_started','backup'}
  candidate_gate=(j.get('version')==2 and j.get('policy')=='gate-only' and set(j)==fields|{'policy'} and (a,b)==(candidate,gate))
  gate_candidate=(j.get('version')==1 and 'policy' not in j and set(j)==fields and (a,b)==(gate,candidate))
  if not (candidate_gate or gate_candidate) or j.get('phase') not in ('prepared','committed') or type(j.get('caddy_started')) is not bool:continue
  timer=j.get('timer')
  if not isinstance(timer,dict) or set(timer)!={'active','enabled'} or any(type(v) is not bool for v in timer.values()) or not isinstance(j.get('backup'),str) or not j['backup']:continue
  if all(current[k] in (a[k],b[k]) for k in current):matches.append(selector)
 if len(matches)!=1:raise ValueError('Unknown, mixed or unpinned post-floor beta routes')
 return matches[0],family_map[matches[0]]
