#!/usr/bin/env python3
"""Integrate reviewed routed-public profile2 over the sealed live document release.

The strict registered-only gateway and document backend come from the deployed
native15 artifact. New host and network modules have one content-addressed graph.
No development-tree backend, private state, account data or credentials are copied.
"""
import argparse
import hashlib
import importlib.util
import json
import posixpath
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'.build/releases/connected-document-r2'
PIN='6789b29e7ed65ff2087e791448306ba68ab0b8bcc45ed70cdaa60a23fa404f35'
PROFILE='codi-connected-development/16'
MODULES=frozenset({'crypto.mjs','identity.mjs','peer.mjs','strict-json.mjs',
 'mesh-contract.mjs','origin-event.mjs','resource-budget.mjs','namespace.mjs',
 'subscriptions.mjs','replay.mjs','room-invitation.mjs','public-rooms.mjs',
 'chess-record.mjs','pgn-worker.mjs','pgn-importer.mjs','peer-pool.mjs',
 'traffic-scheduler.mjs','bootstrap.mjs','bootstrap-source.mjs','support-client.mjs',
 'discovery.mjs','routed-rooms.mjs','routed-room-grant.mjs','routed-history.mjs'})
sys.dont_write_bytecode=True

def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def record(path):
 raw=path.read_bytes();return {'bytes':len(raw),'sha256':digest(raw)}
def contract(path):
 spec=importlib.util.spec_from_file_location('routed_contract_'+digest(str(path).encode())[:8],path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

GRAPH_VERIFIER='''
def verify_routed_graph(directory,frontend):
 import re
 metadata=json.loads((directory/'assets/desktop/network-release.json').read_text())
 if set(metadata)!={'version','profile','modules','directory','core','coreDirectory'} or metadata['version']!='codi-network-release/1' or metadata['profile']!='codi-routed-room/2':raise ValueError('Invalid routed graph metadata')
 modules=metadata['modules'];core=metadata['core']
 expected=NETWORK|{'routed-rooms.mjs','routed-room-grant.mjs','routed-history.mjs'}
 if not isinstance(modules,dict) or set(modules)!=expected or not isinstance(core,dict) or set(core)!={'reference.js','terminal.js','desktop-apps.js','networking.js','app.js'}:raise ValueError('Incomplete routed module/host graph')
 def key(records):return hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 folder='assets/desktop/network-v2/'+key(modules);host='assets/desktop/core-v2/'+key(core)
 if metadata['directory']!=folder or metadata['coreDirectory']!=host:raise ValueError('Invalid routed graph directory')
 for prefix,records in [(folder,modules),(host,core)]:
  for name,value in records.items():
   if frontend['files'].get(prefix+'/'+name)!=value or record(directory/prefix/name)!=value:raise ValueError('Unbound routed asset')
 index=(directory/'index.html').read_text()
 if any('src="'+host+'/'+name+'"' not in index for name in core):raise ValueError('Unmatched routed host entrypoint')
 for name in ['app.js','networking.js']:
  text=(directory/host/name).read_text()
  if re.search(r"['\\\"](?:\\./)?network/",text):raise ValueError('Unversioned network import in routed host')
  if folder+'/' not in text:raise ValueError('Routed host has no matching network graph')
 return metadata

'''

def patch_native(stage):
 def change(name,fn):
  path=stage/name;old=path.read_text();new=fn(old);assert new!=old,name;path.write_text(new)
 def extend_tuples(text):
  return text.replace("'codi-connected-development/15')", "'codi-connected-development/15','codi-connected-development/16')")
 def verifier(text):
  text=text.replace('range(1,16)','range(1,17)')
  text=text.replace("'codi-connected-development/15':V15_NATIVE}","'codi-connected-development/15':V15_NATIVE,'codi-connected-development/16':V15_NATIVE}")
  anchor=" config=json.loads((directory/'config.json').read_text())"
  assert text.count(anchor)==1
  text=text.replace(anchor," if manifest['version']=='codi-connected-development/16':verify_routed_graph(directory,frontend)\n"+anchor)
  return text+GRAPH_VERIFIER
 change('origin_service/release.py',verifier)
 def operator(text):
  text=extend_tuples(text).replace('profile-5..15','profile-5..16')
  text=text.replace("== 'codi-connected-development/15'","in ('codi-connected-development/15','codi-connected-development/16')")
  text=text.replace("=='codi-connected-development/15'","in ('codi-connected-development/15','codi-connected-development/16')")
  anchor="  if role=='issuer' and config.get('userFiles'):"
  assert text.count(anchor)==1
  return text.replace(anchor,"  if role=='issuer' and json.loads((source/'connected-release.json').read_text())['version']=='codi-connected-development/16':command+=['--routed-public-groups']\n"+anchor)
 change('scripts/manage-services.py',operator)
 change('origin_service/turn_management.py',extend_tuples)
 change('origin_service/deployment.py',lambda t:extend_tuples(t).replace("target!='codi-connected-development/15'","target not in ('codi-connected-development/15','codi-connected-development/16')"))
 def issuer(text):
  anchor="    add_turn_arguments(p)"
  assert text.count(anchor)==1
  text=text.replace(anchor,"    p.add_argument('--routed-public-groups',action='store_true',help='Enable bounded public groups and signed missing-message recovery')\n"+anchor)
  anchor="                    if a.user_files:"
  assert text.count(anchor)==1
  return text.replace(anchor,"                    if a.routed_public_groups:config['routedGroups']={'version':'codi-routed-room/2'}\n"+anchor)
 change('scripts/serve-connected.py',issuer)

def build(destination):
 old=contract(BASE/'origin_service/release.py');assert old.verify(BASE)['manifestSHA256']==PIN
 destination=Path(destination).absolute();assert not destination.exists() and destination.is_relative_to(ROOT/'.build/releases')
 assert not any(p.is_symlink() for p in destination.parents)
 stage=Path(tempfile.mkdtemp(prefix='.routed-native-',dir=destination.parent))
 try:
  for path in BASE.rglob('*'):
   if path.is_file():target=stage/path.relative_to(BASE);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
  public=json.loads((BASE/'release.json').read_text());new=set()
  def put(name,raw):
   assert old.public_name(name),name
   path=stage/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw if isinstance(raw,bytes) else raw.encode());new.add(name)
  assert {p.name for p in (ROOT/'network').glob('*.mjs')}==MODULES
  sources={name:(ROOT/'network'/name).read_text() for name in sorted(MODULES)}
  # All peer modules are siblings. The sole external library stays at the
  # existing immutable vendor URL, four levels above this new network folder.
  assert sources['chess-record.mjs'].count('../assets/vendor/chess/chess.mjs')==1
  sources['chess-record.mjs']=sources['chess-record.mjs'].replace('../assets/vendor/chess/chess.mjs','../../../vendor/chess/chess.mjs')
  for name,text in sources.items():
   for target in re.findall(r"(?:\bfrom\s+|\bimport\s*\(|new URL\s*\()(['\"])(.*?)\1",text):
    target=target[1]
    assert target.startswith('./') and target[2:] in MODULES or name=='chess-record.mjs' and target=='../../../vendor/chess/chess.mjs',(name,target)
  records={name:{'bytes':len(text.encode()),'sha256':digest(text.encode())} for name,text in sources.items()}
  folder='assets/desktop/network-v2/'+digest(canonical(records))
  for name,text in sources.items():put(folder+'/'+name,text)
  index=(BASE/'index.html').read_text();core={}
  for name in ['reference.js','terminal.js','desktop-apps.js','networking.js','app.js']:
   source=re.search('src="([^"]*/'+re.escape(name)+')"',index)[1]
   core[name]=(BASE/source).read_text()
  # Keep the live document/API2 host and add the already-tested routed facade.
  core['networking.js']=(ROOT/'networking.js').read_text()
  # Desktop liveness comes from the issuer status/maintenance endpoint. A full
  # or failed optional Linux relay must not disable unrelated files/chat apps.
  anchor='getGuestLink:()=>!guestNetworkAdapter||guestNetworkAdapter.socket?.readyState===WebSocket.OPEN,'
  assert core['app.js'].count(anchor)==1
  core['app.js']=core['app.js'].replace(anchor,'')
  anchor='if(controlled)guestNetworkAdapter=new GuestNetworkAdapter(emulator,identityConfig,{getSession:()=>currentSession});'
  assert core['app.js'].count(anchor)==1
  core['app.js']=core['app.js'].replace(anchor,"if(controlled)guestNetworkAdapter=new GuestNetworkAdapter(emulator,identityConfig,{getSession:()=>currentSession,onStatus:value=>{if(value.mode==='disconnected')feedback('Linux Internet is unavailable; retrying. Files and browser chat remain available.');}});")
  anchor="    popup.append(make('h4','','Network'),"
  assert core['app.js'].count(anchor)==1
  core['app.js']=core['app.js'].replace(anchor,"    if(network&&signedInSubject()&&guestNetworkAdapter?.mode!=='registered')description='Linux Internet is connecting or unavailable. Files and browser peer apps remain available. The preview has a bounded relay capacity.';\n"+anchor)
  anchor="    if(guestNetworkAdapter?.controlled!==false&&network?.durableAccountLimits)"
  assert core['app.js'].count(anchor)==1
  core['app.js']=core['app.js'].replace(anchor,"    if(network&&guestNetworkAdapter?.message)popup.append(make('p','',guestNetworkAdapter.message));\n"+anchor)
  anchor="    if(guestNetworkAdapter?.controlled!==false&&network?.durableAccountLimits)"
  assert core['app.js'].count(anchor)==1
  settings="""    const advanced=make('details'),summary=make('summary','','Networking allowance');
    const memory=desktopNetwork.memoryPolicy(),allowance=make('select');allowance.setAttribute('aria-label','Shared networking allowance');allowance.dataset.networkMemory='';
    summary.style.cssText='min-height:44px;padding:10px 0;cursor:pointer;';allowance.style.cssText='min-height:44px;width:100%;';
    for(const value of [...new Set([32,64,128,256,512,1024,memory.metadataMiB])].sort((a,b)=>a-b)){const option=make('option','',value+' MiB');option.value=value;option.selected=value===memory.metadataMiB;allowance.append(option);}
    allowance.addEventListener('change',()=>{try{desktopNetwork.configureMemoryBudgetMiB(Number(allowance.value));feedback('Networking allowance updated.');}catch(error){allowance.value=desktopNetwork.memoryPolicy().metadataMiB;feedback(error.message);}});
    advanced.append(summary,make('p','','Shared by all network channels in this tab. This cap does not reserve physical RAM. Saved files and Linux use separate memory.'),allowance);popup.append(advanced);
"""
  core['app.js']=core['app.js'].replace(anchor,settings+anchor)
  core['networking.js']=re.sub(r"import\((['\"])\./([^'\"]+)\1\)",lambda m:'import(new URL('+repr(m[2])+',document.baseURI))',core['networking.js'])
  for name in ['app.js','networking.js']:
   core[name]=re.sub(r"(['\"])network/([^'\"?]+)(?:\?[^'\"]*)?\1",lambda m:repr(folder+'/'+m[2]),core[name])
  core_records={name:{'bytes':len(text.encode()),'sha256':digest(text.encode())} for name,text in core.items()}
  core_folder='assets/desktop/core-v2/'+digest(canonical(core_records))
  for name,text in core.items():
   put(core_folder+'/'+name,text);index=re.sub('src="[^"]*/'+re.escape(name)+'"','src="'+core_folder+'/'+name+'"',index)
  put('index.html',index)
  graph={'version':'codi-network-release/1','profile':'codi-routed-room/2','modules':records,'directory':folder,'core':core_records,'coreDirectory':core_folder}
  put('assets/desktop/network-release.json',json.dumps(graph,indent=2)+'\n')
  patch_native(stage)
  (stage/'guest_service/client.mjs').write_bytes((ROOT/'guest_service/client.mjs').read_bytes())
  cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_text());names=set(cache['files'])|new
  names-={'config.json','assets/desktop/offline-worker.js','assets/desktop/cache-manifest.json'}
  cache['files']={n:record(stage/n) for n in sorted(names)};cache['id']=digest(canonical(cache['files']))
  template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();assert template.count('__PUBLIC_CACHE_MANIFEST__')==1
  put('assets/desktop/cache-manifest.json',json.dumps(cache,indent=2)+'\n')
  put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))))
  public['files']={n:record(stage/n) for n in sorted(set(public['files'])|new)};(stage/'release.json').write_text(json.dumps(public,indent=2)+'\n')
  full=json.loads((BASE/'connected-release.json').read_text());full['version']=PROFILE
  full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'}
  (stage/'connected-release.json').write_text(json.dumps(full,indent=2)+'\n')
  for path in [stage,*stage.rglob('*')]:path.chmod(0o755 if path.is_dir() else 0o644)
  verifier=contract(stage/'origin_service/release.py');verified=verifier.verify(stage)
  assert verifier.verify(BASE)['manifestSHA256']==PIN
  changed_native=[n for n in old.V15_NATIVE if record(stage/n)!=record(BASE/n)]
  assert set(changed_native)=={'origin_service/release.py','origin_service/deployment.py','origin_service/turn_management.py','scripts/manage-services.py','scripts/serve-connected.py','guest_service/client.mjs'}
  stage.rename(destination)
  return verified|{'directory':str(destination),'baseManifestSHA256':PIN,'networkDirectory':folder,'coreDirectory':core_folder,'nativeChanges':sorted(changed_native),'guestAndFileSecurityBackendPreserved':True,'liveDeploymentChanged':False}
 finally:
  if stage.exists():shutil.rmtree(stage)

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
 result=build(parser.parse_args().output);print(json.dumps(result,indent=2))
