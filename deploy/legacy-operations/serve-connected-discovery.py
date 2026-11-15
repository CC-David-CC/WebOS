#!/usr/bin/env python3
"""Isolated development issuer plus independently scoped native steward process behind TLS.

Both backends bind loopback. No official authority, public listener or system service.
"""
import argparse,asyncio,importlib.util,json,os,re,secrets,signal,sys,threading,time
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('connected_preview',ROOT/'scripts/serve-connected.py')
connected=importlib.util.module_from_spec(spec);spec.loader.exec_module(connected)
from steward.publisher import PublisherState
from steward.root_authority import private_read,private_directory
from steward.provision import verified_seed
from cryptography.hazmat.primitives import serialization
from steward.protocol import jose,exact,times
from cryptography.hazmat.primitives.asymmetric import ec
from wsgiref.simple_server import make_server

def provisioned_inputs(private,issuer_policy,args):
 private_directory(private);provision=jose.loads(private_read(private/'provision.json'));exact(provision,'seed root_key realm endpoint identity_policy origins')
 if provision['identity_policy']!=issuer_policy or provision['origins']!=[args.origin] or provision['endpoint']!=args.endpoint:raise ValueError('Provision must match this issuer, origin and endpoint')
 service=serialization.load_pem_private_key(private_read(private/'service.pem'),password=None)
 if not isinstance(service,ec.EllipticCurvePrivateKey) or not isinstance(service.curve,ec.SECP256R1):raise ValueError('Scoped P-256 service key required')
 seed=verified_seed(provision['seed'],provision['root_key'],provision['realm'],int(time.time()))
 grant=next((g for g in seed['stewards'] if g['key_id']==jose.thumbprint(jose.public_jwk(service)) and args.endpoint in g['endpoints']),None)
 if grant is None or len(grant['scopes'])!=1:raise ValueError('Provisioned service needs one delegated public scope')
 PublisherState(private/'ledger')
 return provision,service,seed,grant

async def run(args,runtime=None):
 base=runtime.root if runtime else ROOT/'.build/connected-instances'/(args.instance or 'combined-tls')
 public_path=runtime.public if runtime else base/'public'
 turn_policy=connected.policy_from_arguments(args,public_path)
 public=connected.stage(public_path)
 class Issuer(connected.Service):
  discovery=None
  def config(self):
   config=super().config()
   if self.discovery:
    with self.lock:
     try:
      raw=(public/'discovery.json').read_bytes()
      if len(raw)>49152:raise ValueError('Public bundle size')
      bundle=jose.loads(raw);exact(bundle,'version seed descriptor')
      if bundle['version']!='codi-bootstrap-bundle/1':raise ValueError('Unexpected bundle version')
      if args.provisioned_steward:
       stamp=int(time.time());payload=verified_seed(bundle['seed'],self.discovery['pin']['rootKey'],self.discovery['pin']['realm'],stamp)
       previous=jose.inspect(self.discovery['seed'],'codi-seed/1',32768)[1]
       if payload['revision']<previous['revision'] or payload['revision']==previous['revision'] and bundle['seed']!=self.discovery['seed']:raise ValueError('Root policy rollback or fork')
       descriptor=jose.verify(bundle['descriptor'],jose.public_jwk(service),'codi-steward/1',8192);exact(descriptor,'version realm key_id revision iat exp endpoint scopes limits');times(descriptor,stamp,300)
       delegated=next(g for g in payload['stewards'] if g['key_id']==jose.thumbprint(jose.public_jwk(service)) and args.endpoint in g['endpoints'])
       limits=delegated['limits'];bounded={'lease_seconds':limits['lease_seconds'],'sample_size':min(4,limits['sample_size']),'signal_bytes':min(32768,limits['signal_bytes'])}
       if descriptor['version']!='codi-steward/1' or descriptor['key_id']!=delegated['key_id'] or descriptor['realm']!=realm or descriptor['endpoint']!=args.endpoint or descriptor['scopes']!=delegated['scopes'] or descriptor['limits']!=bounded or descriptor['exp']>delegated['exp'] or type(descriptor['revision']) is not int or descriptor['revision']<max(payload['revision'],jose.inspect(self.discovery['descriptor'],'codi-steward/1',8192)[1]['revision']):raise ValueError('Descriptor binding')
      elif bundle['seed']!=self.discovery['seed']:raise ValueError('Unexpected preview root policy')
      self.discovery={**self.discovery,'seed':bundle['seed'],'descriptor':bundle['descriptor']}
     except (OSError,ValueError,KeyError,TypeError,StopIteration):pass  # Retain signed metadata; never create authority on worker failure.
     config['discovery']={**self.discovery}
   return config
 issuer=Issuer(connected.Config(base/'state',public,origin=args.origin),turn_policy=turn_policy,base_path=args.base_path)
 issuer_policy=issuer.config()['identity'];now=int(time.time())
 if args.provisioned_steward:
  private=base/'steward-private/provisioned';provision,service,payload,grant=provisioned_inputs(private,issuer_policy,args)
  realm=provision['realm'];scope=grant['scopes'][0];seed=provision['seed'];root_key=provision['root_key']
 else:
  root=ec.generate_private_key(ec.SECP256R1());service=ec.generate_private_key(ec.SECP256R1());realm=secrets.token_urlsafe(32);scope=secrets.token_urlsafe(32);key=jose.public_jwk(service);root_key=jose.public_jwk(root)
  grant={'key_id':jose.thumbprint(key),'public_key':key,'endpoints':[args.endpoint],'scopes':[scope],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768},'exp':now+args.delegation_seconds,'failure_domain':'one-loopback-host'}
  seed=jose.sign({'version':'codi-seed/1','realm':realm,'revision':1,'iat':now,'exp':now+args.delegation_seconds,'stewards':[grant]},root,'codi-seed/1')
  private=base/'steward-private'/secrets.token_hex(12);private.mkdir(parents=True,mode=0o700);private.parent.chmod(0o700);PublisherState.initialize(private/'ledger')
  provision={'seed':seed,'root_key':root_key,'realm':realm,'endpoint':args.endpoint,'identity_policy':issuer_policy,'origins':[args.origin]}
 def write_private(path,data):
  with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as output:output.write(data)
 if not args.provisioned_steward:
  write_private(private/'provision.json',jose.dumps(provision).encode())
  write_private(private/'service.pem',service.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
 def delegation_deadline():
  if not args.provisioned_steward:return now+args.delegation_seconds
  try:
   current,_,_,delegated=provisioned_inputs(private,issuer_policy,args)
   if any(current[k]!=provision[k] for k in provision if k!='seed'):return 0
   return delegated['exp']
  except (ValueError,OSError):return 0
 command=[sys.executable,str(ROOT/'scripts/serve-steward.py'),'serve','--state',str(private/'ledger'),'--provision',str(private/'provision.json'),'--key',str(private/'service.pem'),'--bundle-out',str(public/'discovery.json'),'--port',str(args.steward_port)]
 http=make_server('127.0.0.1',args.port,connected.HeadSupport(issuer),server_class=connected.BoundedServer,handler_class=connected.Quiet);serving=False;worker=None;monitor=None
 stop=asyncio.Event();loop=asyncio.get_running_loop()
 for sig in (signal.SIGTERM,signal.SIGINT):loop.add_signal_handler(sig,stop.set)
 restarts=0;runtime=base/'state/steward-process.json'
 def record_worker(status):
  temporary=runtime.with_name('.steward-process-'+secrets.token_hex(6))
  write_private(temporary,json.dumps({'pid':worker.pid,'port':args.steward_port,'privateRun':str(private),'command':command,'restarts':restarts,'status':status}).encode());temporary.replace(runtime)
 async def start_worker():
  nonlocal worker
  with os.fdopen(os.open(private/'worker.log',os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600),'ab') as errors:
   worker=await asyncio.create_subprocess_exec(*command,stdout=asyncio.subprocess.PIPE,stderr=errors)
  announcement=await asyncio.wait_for(worker.stdout.readline(),10)
  if not announcement.startswith(b'Provisioned steward:'):raise RuntimeError('Steward startup failed; inspect private worker log')
  record_worker('running')
 try:
  await start_worker()
  bundle=jose.loads((public/'discovery.json').read_bytes())
  issuer.discovery={'pin':{'realm':realm,'rootKey':root_key,'endpoints':[args.endpoint],'allowLoopback':False},'seed':seed,'descriptor':bundle['descriptor'],'scope':scope,'sourcePath':args.base_path+'/discovery.json'}
  threading.Thread(target=http.serve_forever,daemon=True).start();serving=True
  print('Combined development preview: '+args.origin+' (separate loopback processes; '+('operator-provisioned' if args.provisioned_steward else 'disposable')+' delegation)',flush=True)
  async def authority_available():
   if int(time.time())<delegation_deadline():return True
   record_worker('delegation-expired');print('Steward delegation expired; issuer remains available.',flush=True)
   if not args.provisioned_steward:return False
   # Only a newly valid operator-signed provision can allow another worker.
   # No root private key or signing operation is present in this wait loop.
   while not stop.is_set():
    if int(time.time())<delegation_deadline():return True
    try:await asyncio.wait_for(stop.wait(),2)
    except asyncio.TimeoutError:pass
   return False
  async def watch_worker():
   nonlocal restarts
   while not stop.is_set():
    await worker.wait()
    if stop.is_set():return
    if not await authority_available():return
    if restarts>=3:
     record_worker('exhausted');print('Steward restart limit reached; issuer remains available.',flush=True);return
    restarts+=1;record_worker('backoff');await asyncio.sleep(2**(restarts-1))
    if stop.is_set():return
    if not await authority_available():return
    try:await start_worker()
    except Exception:
     if worker.returncode is None:worker.kill();await worker.wait()
     print('Steward restart failed; authority and publisher state were retained.',flush=True)
  monitor=asyncio.create_task(watch_worker());await stop.wait()
 finally:
  stop.set()
  if monitor:monitor.cancel();await asyncio.gather(monitor,return_exceptions=True)
  if worker is not None and worker.returncode is None:
   worker.terminate()
   try:await asyncio.wait_for(worker.wait(),3)
   except asyncio.TimeoutError:worker.kill();await worker.wait()
  if serving:await asyncio.to_thread(http.shutdown)
  http.server_close()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=8118);p.add_argument('--steward-port',type=int,default=8119)
 location=p.add_mutually_exclusive_group();location.add_argument('--instance');location.add_argument('--runtime-dir',type=Path,help='Private writable absolute directory outside the application release')
 mode=p.add_mutually_exclusive_group();mode.add_argument('--provisioned-steward',action='store_true',help='Use explicitly initialized stable provision/key/ledger in the external runtime');mode.add_argument('--delegation-seconds',type=int,default=600)
 p.add_argument('--origin',default='https://127.0.0.1:8446');p.add_argument('--endpoint',default='wss://127.0.0.1:8446/rendezvous');p.add_argument('--base-path',default='',type=connected.validate_base_path);connected.add_turn_arguments(p);a=p.parse_args()
 if a.provisioned_steward and a.runtime_dir is None:p.error('Provisioned steward requires a private external --runtime-dir')
 if not 30<=a.delegation_seconds<=600:p.error('Disposable delegation must be 30..600 seconds')
 if a.instance is not None and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',a.instance):p.error('Bounded instance label required')
 if not all(1<=port<=65535 for port in (a.port,a.steward_port)) or a.port==a.steward_port:p.error('Distinct valid loopback ports required')
 u=urlsplit(a.origin)
 if u.scheme!='https' or not u.hostname or u.username or u.password or u.path or u.query or u.fragment:p.error('Explicit HTTPS origin required')
 if urlsplit(a.endpoint).scheme!='wss' or urlsplit(a.endpoint).path!=a.base_path+'/rendezvous':p.error('Explicit WSS endpoint must match the configured base path')
 try:
  with connected.PrivateRuntime(a.runtime_dir,ROOT) if a.runtime_dir is not None else connected.nullcontext(None) as runtime:asyncio.run(run(a,runtime))
 except ValueError as error:p.error(str(error))
 except KeyboardInterrupt:pass
if __name__=='__main__':main()
