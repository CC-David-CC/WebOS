"""Checksummed connected-release verification shared by operator tools."""
import hashlib,json
from pathlib import Path
# Profiles 1..14 keep their original contracts when newer launchers/assets grow.
# Do not derive old verification rules from the current static server allowlist.
PUBLIC=frozenset({'index.html','style.css','app.js','reference.js','terminal.js','desktop-apps.js','networking.js','config.json'})
NETWORK=frozenset({'crypto.mjs','identity.mjs','peer.mjs','strict-json.mjs','mesh-contract.mjs','origin-event.mjs','resource-budget.mjs','namespace.mjs','subscriptions.mjs','replay.mjs','room-invitation.mjs','public-rooms.mjs','chess-record.mjs','pgn-worker.mjs','pgn-importer.mjs','peer-pool.mjs','traffic-scheduler.mjs','bootstrap.mjs','bootstrap-source.mjs','support-client.mjs','discovery.mjs'})
RUNTIME=frozenset({'libv86.js','v86.wasm','seabios.bin','vgabios.bin','vmlinuz','initramfs.cpio.gz'})
V1_NATIVE={
 'serve.py','requirements.lock',
 'scripts/serve-connected.py','scripts/serve-connected-discovery.py','scripts/serve-steward.py',
 'guest-relay/server.py',
 *('origin_service/'+n+'.py' for n in ['__init__','http_server','lifecycle','mount','runtime','turn']),
 *('steward/'+n+'.py' for n in ['__init__','leases','protocol','provision','publisher','server','turn_credentials']),
 *('codiserver-server-v0.3.0/codiauth/'+n+'.py' for n in ['__init__','jose','service']),
}
V2_NATIVE=V1_NATIVE|{'scripts/provision-connected.py','steward/root_authority.py'}
V3_NATIVE=V2_NATIVE|{'origin_service/discovery.py'}
V4_NATIVE=V3_NATIVE|{'scripts/install-service-accounts.py'}
V5_NATIVE=V4_NATIVE|{'origin_service/release.py','scripts/manage-services.py'}
V6_NATIVE=V5_NATIVE|{'origin_service/maintenance.py'}
V7_NATIVE=V6_NATIVE|{'origin_service/deployment.py'}
V9_NATIVE=V7_NATIVE|{'origin_service/turn_management.py'}
V10_NATIVE=V9_NATIVE|{'origin_service/guest_cookie.py'}
V11_NATIVE=frozenset(V10_NATIVE|{'origin_service/gateway_authority.py','origin_service/files_management.py',
 *('gateway_service/'+n+'.py' for n in ['__init__','auth','policy','user_store'])})
V12_NATIVE=frozenset(V11_NATIVE|{'origin_service/guest_authority.py','origin_service/network_management.py','guest_service/client.mjs',
 *('guest_service/'+n+'.py' for n in ['__init__','authorization','egress','frames','worker','coordinator','runtime','frontend'])})
V13_NATIVE=frozenset(V12_NATIVE|{'scripts/desktop-maintenance.py'})
V14_NATIVE=frozenset(V13_NATIVE|{'origin_service/ice_preference.py'})
V15_NATIVE=frozenset(V14_NATIVE|{'origin_service/official_authority.py'})
NATIVE=V14_NATIVE
def record(path):return {'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def public_name(name):
 if not isinstance(name,str) or len(name)>512 or '\\' in name or '\x00' in name:return False
 parts=name.split('/')
 if any(p in ('','.','..') for p in parts):return False
 if name in PUBLIC:return True
 if len(parts)==2 and parts[0]=='network':return parts[1] in NETWORK
 if len(parts)==3 and parts[:2]==['.build','v86']:return parts[2] in RUNTIME
 if len(parts)==3 and parts[:2]==['licenses','runtime']:return parts[2] in {'LICENSE-v86','LICENSE-bios','LICENSE-linux','LICENSE-busybox','LICENSE-glibc'}
 return len(parts)>1 and parts[0]=='assets' and not any(p.startswith('.') for p in parts[1:]) and Path(name).suffix.lower() not in {'.pem','.key','.sqlite','.sqlite3','.db','.py','.env'}
def verify(directory):
 directory=Path(directory).absolute()
 if directory.is_symlink() or not directory.is_dir():raise ValueError('Real release directory required')
 manifest_path=directory/'connected-release.json'
 if manifest_path.is_symlink() or not manifest_path.is_file():raise ValueError('Missing release manifest')
 manifest=json.loads(manifest_path.read_text())
 if set(manifest)!={'version','authorityClass','mount','guestEgress','files'} or manifest['version'] not in tuple('codi-connected-development/'+str(n) for n in range(1,16)) or manifest['authorityClass']!='development' or manifest['mount']!='configurable' or manifest['guestEgress']!='relay-host':raise ValueError('Invalid development release manifest')
 public=directory/'release.json'
 if public.is_symlink() or not public.is_file():raise ValueError('Missing public export manifest')
 frontend=json.loads(public.read_text())
 if not isinstance(manifest['files'],dict) or not isinstance(frontend.get('files'),dict):raise ValueError('Invalid file records')
 if not all(public_name(name) for name in frontend['files']):raise ValueError('Nonpublic file in public manifest')
 required=set(PUBLIC)|{'network/'+n for n in NETWORK}|{'.build/v86/'+n for n in RUNTIME}|{'licenses/runtime/LICENSE-'+n for n in ['v86','bios','linux','busybox','glibc']}
 if not required<=set(frontend['files']):raise ValueError('Public runtime or notices missing')
 native={'codi-connected-development/1':V1_NATIVE,'codi-connected-development/2':V2_NATIVE,'codi-connected-development/3':V3_NATIVE,'codi-connected-development/4':V4_NATIVE,'codi-connected-development/5':V5_NATIVE,'codi-connected-development/6':V6_NATIVE,'codi-connected-development/7':V7_NATIVE,'codi-connected-development/8':V7_NATIVE,'codi-connected-development/9':V9_NATIVE,'codi-connected-development/10':V10_NATIVE,'codi-connected-development/11':V11_NATIVE,'codi-connected-development/12':V12_NATIVE,'codi-connected-development/13':V13_NATIVE,'codi-connected-development/14':V14_NATIVE,'codi-connected-development/15':V15_NATIVE}[manifest['version']]
 if set(manifest['files'])!=set(frontend['files'])|native|{'release.json'}:raise ValueError('Release does not match explicit public/native file lists')
 found=set()
 for path in directory.rglob('*'):
  if path.is_symlink():raise ValueError('Symlink in release')
  if path.is_dir():continue
  if not path.is_file() or path.stat().st_nlink!=1:raise ValueError('Nonregular or linked release file')
  name=str(path.relative_to(directory))
  if name=='connected-release.json':continue
  if name not in manifest['files'] or manifest['files'][name]!=record(path):raise ValueError('Unexpected or changed release file: '+name)
  if name in frontend['files'] and frontend['files'][name]!=record(path):raise ValueError('Changed public runtime: '+name)
  found.add(name)
 if found!=set(manifest['files']):raise ValueError('Release files missing')
 config=json.loads((directory/'config.json').read_text())
 if config.get('identity',{}).get('mode')!='local-development' or set(config)-{'protocol','identity','rtc','vm'}:raise ValueError('Static baseline must not embed service credentials or state')
 return {'directory':str(directory),'files':len(found),'bytes':sum(x['bytes'] for x in manifest['files'].values()),'manifestSHA256':hashlib.sha256(manifest_path.read_bytes()).hexdigest()}

