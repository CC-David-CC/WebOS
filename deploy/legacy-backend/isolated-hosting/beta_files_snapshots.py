"""Exact read-only hosting snapshots for the candidate Files transaction.

Protected caller must load the supplied generator modules from pinned bytes.
"""
import copy,hashlib,json,tomllib
OLD_COMMON='d4f05bbb709e056354a5d2eb4d3a78741cbd044e4d100b965b91ec9a428a5ad0'
NEW_COMMON='d11755a183bc5c12803b6fdc84fa54f4803c0f10c415c07bb9eecc82699132a1'
BASE_MANIFEST='9bf8afdaab7d321940cc01b9275af81ba2b1ad558a3b966f24e05c6561a317b5'
CANDIDATE='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
TABLE='773dcdfa559d9ad5b5012bb4363248e8434e97dc33d2677bdd376d099c87fc1a'
def sha(x):return hashlib.sha256(x).hexdigest()
def build(*,old,new,manifest,candidate_manifest,route_table):
 if sha(old.source)!=OLD_COMMON or sha(new.source)!=NEW_COMMON or sha(manifest)!=BASE_MANIFEST or sha(candidate_manifest)!=CANDIDATE or sha(route_table)!=TABLE:raise ValueError('Snapshot input pin mismatch')
 data=tomllib.loads(manifest.decode());old.module.validate(data)
 if old.module.dump(data).encode()!=manifest or 'codi_beta_maintenance' in data or 'codi_beta_opfs' in data:raise ValueError('Unexpected beta baseline manifest')
 candidate=json.loads(candidate_manifest);table=json.loads(route_table)
 if candidate.get('version')!='codi-beta-opfs-candidate/1' or table.get('candidate')!=CANDIDATE:raise ValueError('Unexpected Files manifest')
 routes=table.get('routes')
 if not isinstance(routes,list) or len(routes)!=84:raise ValueError('Incomplete exact route table')
 seen=set()
 for route in routes:
  if set(route)!={'method','path','query','sha256','target'} or route['method']!=['GET','HEAD'] or route['path'] in seen:raise ValueError('Invalid exact route')
  seen.add(route['path']);record=candidate['files'].get(route['target'])
  if not record or record['sha256']!=route['sha256']:raise ValueError('Route differs from candidate manifest')
  if route['path'] in ('/app.js','/desktop-apps.js'):
   if route['query']!='simplified=1 exactly' or route['target']!='shell/'+route['path'][1:]:raise ValueError('Invalid shell route')
  elif route['query']!='any' or route['target']!=route['path'][1:] or not route['target'].startswith(('assets/','storage/')):raise ValueError('Invalid asset route')
 expected_assets={'/'+p:r['sha256'] for p,r in candidate['files'].items() if p.startswith(('assets/','storage/'))}
 if {r['path']:r['sha256'] for r in routes if r['path'] not in ('/app.js','/desktop-apps.js')}!=expected_assets or new.module.OPFS_PUBLIC_FILES!=expected_assets:raise ValueError('Asset route inventory mismatch')
 normal=copy.deepcopy(data);normal['codi_beta_maintenance']=False;gate=copy.deepcopy(normal);gate['codi_beta_maintenance']=True;active=copy.deepcopy(normal);active['codi_beta_opfs']=CANDIDATE
 for mod,value in ((old.module,data),(old.module,normal),(old.module,gate),(new.module,active)):mod.validate(value)
 def snap(bound,value):return {'common':bound.source,'manifest':bound.module.dump(value).encode(),'caddy':bound.module.caddy(value,'production').encode()}
 initial=snap(old,data);normalized=snap(old,normal);gated=snap(old,gate);v2=snap(new,active)
 for mode in ('prepare','production'):
  if old.module.caddy(data,mode)!=old.module.caddy(normal,mode):raise ValueError('Normalization changes generated routes')
 def strip_beta(raw):
  s=raw.decode();tag='beta.ksu.codes {'
  if s.count(tag)!=1:raise ValueError('Expected exactly one beta block')
  a=s.index(tag);b=s.find('\n}\n',a)
  if b<0:raise ValueError('Incomplete beta block')
  return s[:a]+s[b+3:]
 if strip_beta(initial['caddy'])!=strip_beta(v2['caddy']):raise ValueError('Non-beta routes changed')
 return {'initial':initial,'normalized':normalized,'gate':gated,'candidate':v2,'initialData':data,'normalizedData':normal,'gateData':gate,'candidateData':active}
