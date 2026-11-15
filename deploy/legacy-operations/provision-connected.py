#!/usr/bin/env python3
"""Explicit development steward provisioning; root key stays outside runtime.

init attaches a stable steward to an existing/new issuer runtime. renew signs a
new bounded root seed. export republishes committed bytes after an interrupted
export. No command starts a listener, rotates a key or resets publisher state.
"""
import argparse,importlib.util,json,os,secrets,sys,time
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('connected_preview',ROOT/'scripts/serve-connected.py');connected=importlib.util.module_from_spec(spec);spec.loader.exec_module(connected)
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from steward.root_authority import RootAuthority,atomic_private,private_read,private_directory,safe_path,duration
from steward.publisher import PublisherState
from steward.protocol import jose
from steward.provision import verified_seed

def locations(args):
 runtime=safe_path(args.runtime_dir);authority=safe_path(args.root_dir)
 for first,second in [(runtime,authority),(ROOT.resolve(),authority),(ROOT.resolve(),runtime)]:
  if first.is_relative_to(second) or second.is_relative_to(first):raise ValueError('Root authority, runtime and application must be disjoint directory trees')
 return runtime,authority,runtime/'steward-private/provisioned'

def init(args):
 runtime,authority,private=locations(args)
 if authority.exists() or private.exists() or authority.is_symlink() or private.is_symlink():raise ValueError('Existing provision or root directory must be preserved; initialization is explicit and not repeatable')
 origin=urlsplit(args.origin);endpoint=urlsplit(args.endpoint)
 if origin.scheme!='https' or not origin.hostname or origin.username or origin.password or origin.path or origin.query or origin.fragment:raise ValueError('Explicit HTTPS origin required')
 if endpoint.scheme!='wss' or not endpoint.hostname or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment or endpoint.path!=args.base_path+'/rendezvous':raise ValueError('WSS endpoint must match the configured application path')
 with connected.PrivateRuntime(runtime,ROOT) as paths:
  if args.issuer_config:
   supplied=jose.loads(private_read(args.issuer_config));identity=supplied['identity']
   if identity.get('mode')!='server' or identity.get('authorityClass')!='development' or identity.get('issuer')!=args.origin or identity.get('apiBase')!=args.base_path+'/api/v1' or not identity.get('authorityKeys'):raise ValueError('Explicit development issuer public policy required')
  else:
   public=connected.stage(paths.public);issuer=connected.Service(connected.Config(paths.state,public,origin=args.origin),base_path=args.base_path);identity=issuer.config()['identity']
  private.mkdir(mode=0o700,exist_ok=False);service=ec.generate_private_key(ec.SECP256R1());key=jose.public_jwk(service)
  atomic_private(private/'service.pem',service.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
  PublisherState.initialize(private/'ledger')
  template={'root_key':None,'realm':secrets.token_urlsafe(32),'endpoint':args.endpoint,'identity_policy':identity,'origins':[args.origin]}
  grant={'key_id':jose.thumbprint(key),'public_key':key,'endpoints':[args.endpoint],'scopes':[secrets.token_urlsafe(32)],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768},'failure_domain':'one-development-host'}
  root=RootAuthority.initialize(authority,template,grant,args.seconds)
  with root.operator():atomic_private(private/'provision.json',jose.dumps(root.provision()).encode())
  provision=root.provision();policy={'version':'codi-discovery-source/1','pin':{'realm':provision['realm'],'rootKey':provision['root_key'],'endpoints':[args.endpoint],'allowLoopback':False},'scope':grant['scopes'][0],'sourcePath':args.base_path+'/discovery.json','identity':identity}
  atomic_private(private/'origin-discovery.json',jose.dumps(policy).encode())
 return root.provision()

def update(args):
 runtime,authority,private=locations(args);private_directory(runtime);private_directory(private)
 root=RootAuthority(authority)
 with root.operator():
  committed=root.provision();target=private/'provision.json'
  current=committed if args.command=='export' and not target.exists() and not target.is_symlink() else jose.loads(private_read(target))
  if {k:v for k,v in current.items() if k!='seed'}!={k:v for k,v in committed.items() if k!='seed'}:raise ValueError('Provision binding changed; deliberate migration required')
  old=jose.inspect(current['seed'],'codi-seed/1',32768)[1];old=verified_seed(current['seed'],committed['root_key'],committed['realm'],old['iat'])
  saved=jose.inspect(committed['seed'],'codi-seed/1',32768)[1]
  if old['revision']>saved['revision'] or (old['revision']==saved['revision'] and current['seed']!=committed['seed']):raise ValueError('Root state rollback or seed fork; restore consistent authority state')
  service=serialization.load_pem_private_key(private_read(private/'service.pem'),password=None)
  if jose.thumbprint(jose.public_jwk(service))!=saved['stewards'][0]['key_id']:raise ValueError('Scoped service key changed')
  PublisherState(private/'ledger')  # Missing/corrupt publisher state is never recreated.
  if args.command=='renew':
   if current['seed']!=committed['seed']:raise ValueError('Export the already committed policy before another renewal')
   committed=root.renew(args.seconds)
  atomic_private(private/'provision.json',jose.dumps(committed).encode())
 return committed

def main():
 parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
 for command in ['init','renew','export']:
  action=sub.add_parser(command);action.add_argument('--runtime-dir',type=Path,required=True);action.add_argument('--root-dir',type=Path,required=True)
  if command!='export':action.add_argument('--seconds',type=int,default=3600)
  if command=='init':action.add_argument('--origin',required=True);action.add_argument('--endpoint',required=True);action.add_argument('--base-path',default='',type=connected.validate_base_path);action.add_argument('--issuer-config',type=Path,help='Explicit public config from a separately owned issuer; no issuer key access')
 args=parser.parse_args()
 try:
  if args.command!='export':duration(args.seconds)
  provision=init(args) if args.command=='init' else update(args)
  seed=jose.inspect(provision['seed'],'codi-seed/1',32768)[1]
  print(json.dumps({'status':args.command,'authorityClass':'development','revision':seed['revision'],'expiresAt':seed['exp'],'rootKeyOutsideRuntime':True}))
 except (ValueError,OSError) as error:parser.error(str(error))
if __name__=='__main__':main()
