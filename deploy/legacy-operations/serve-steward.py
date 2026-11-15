#!/usr/bin/env python3
"""Run a provisioned loopback steward with an explicitly initialized private ledger.

No keys are generated, accounts created, public listeners opened or trust pins reset.
"""
import argparse,asyncio,json,os,stat,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from steward.publisher import PublisherState
from steward.server import StewardServer
from steward.official_channel_checker import OfficialChannelChecker
from steward.protocol import jose,exact

def private_file(path):
    path=Path(path).absolute();parent=path.parent.lstat();info=path.lstat()
    if not stat.S_ISDIR(parent.st_mode) or parent.st_uid!=os.geteuid() or stat.S_IMODE(parent.st_mode)!=0o700:raise ValueError('Private input directory must be owned and 0700')
    if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.geteuid() or stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1 or info.st_size>65536:raise ValueError('Private input must be owned, regular and 0600')
    return path.read_bytes()

def write_bundle(path,bundle):
    parent=path.parent
    if parent.is_symlink() or not parent.is_dir():raise ValueError('Explicit public output directory required')
    if path.is_symlink() or path.exists() and not path.is_file():raise ValueError('Invalid public output file')
    raw=jose.dumps(bundle).encode();fd,name=tempfile.mkstemp(prefix='.bootstrap-',dir=parent)
    try:
        with os.fdopen(fd,'wb') as out:os.fchmod(out.fileno(),0o644);out.write(raw);out.flush();os.fsync(out.fileno())
        os.replace(name,path)
        directory=os.open(parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if os.path.exists(name):os.unlink(name)

def anonymous_policy(path,owner=0):
    # Root-owned operator input, never a browser-writable path. A malformed or
    # missing configured policy fails closed for anonymous introductions.
    parent=Path(path).absolute().parent.lstat()
    if not stat.S_ISDIR(parent.st_mode) or parent.st_uid!=owner or stat.S_IMODE(parent.st_mode)&0o022:raise ValueError('Invalid anonymous policy directory')
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid!=owner or info.st_nlink!=1 or stat.S_IMODE(info.st_mode)&0o022 or info.st_size>16:raise ValueError('Invalid anonymous introduction policy file')
        data=os.read(fd,17)
        if data==b'enabled\n':return True
        if data==b'disabled\n':return False
        raise ValueError('Invalid anonymous introduction policy value')
    finally:os.close(fd)

async def watch_anonymous_policy(server,path,owner=0):
    previous=None
    while True:
        try:allowed=anonymous_policy(path,owner=owner)
        except (OSError,ValueError):allowed=False
        if allowed!=previous:
            await server.set_anonymous_allowed(allowed);previous=allowed
        await asyncio.sleep(1)

async def run(args):
    until=asyncio.get_running_loop().time()+getattr(args,'wait_for_provision',0)
    while not all(Path(path).exists() for path in [args.state,args.provision,args.key]):
        if asyncio.get_running_loop().time()>=until:raise ValueError('Explicit provision/key/ledger are not available')
        await asyncio.sleep(.1)
    state=PublisherState(args.state);provision=jose.loads(private_file(args.provision));exact(provision,'seed root_key realm endpoint identity_policy origins')
    key=serialization.load_pem_private_key(private_file(args.key),password=None)
    if not isinstance(key,ec.EllipticCurvePrivateKey) or not isinstance(key.curve,ec.SECP256R1):raise ValueError('P-256 service private key required')
    output=Path(args.bundle_out).absolute()
    for private in [Path(args.state).absolute(),Path(args.key).absolute(),Path(args.provision).absolute()]:
        if private.resolve().is_relative_to(output.parent.resolve()):raise ValueError('Public bundle directory must be separate from private state and inputs')
    checker=OfficialChannelChecker(args.official_reader_port,provision['identity_policy']['issuer']) if args.official_reader_port else None
    server=StewardServer(**provision,service_key=key,publisher_state=state,official_channel_allowed=checker,offered_channels_only=bool(checker));watcher=None
    policy_file=getattr(args,'anonymous_policy_file',None)
    default_policy=Path(args.state).absolute().parent.parent/'network-policy'/'anonymous-introductions'
    if not policy_file and default_policy.parent.exists():policy_file=default_policy
    if policy_file:
        try:allowed=anonymous_policy(policy_file)
        except (OSError,ValueError):allowed=False
        await server.set_anonymous_allowed(allowed)
    try:
        port=await server.start(args.port)
        if policy_file:watcher=asyncio.create_task(watch_anonymous_policy(server,policy_file))
        last_rejection=None
        while True:
            try:
                updated=jose.loads(private_file(args.provision));exact(updated,'seed root_key realm endpoint identity_policy origins')
                if any(updated[k]!=provision[k] for k in provision if k!='seed'):raise ValueError('Non-seed provision changes require restart')
                await server.reload_seed(updated['seed'],publish=lambda bundle:write_bundle(output,bundle))
                last_rejection=None
            except Exception as error:
                # Keep a rejected untrusted update from replacing valid policy.
                # Frozen/revoked authority cannot use its old policy to serve.
                rejection=type(error).__name__
                if rejection!=last_rejection:print('Provision update rejected; current valid authority is not extended.',file=sys.stderr,flush=True);last_rejection=rejection
            write_bundle(output,server.bundle(renew_if_expiring=True))
            if not getattr(args,'announced',False):
                print(f'Provisioned steward: 127.0.0.1:{port} (loopback only)',flush=True);args.announced=True
            # No new public endpoint; an origin may serve this public JSON file.
            await asyncio.sleep(30)
    finally:
        if watcher:
            watcher.cancel();await asyncio.gather(watcher,return_exceptions=True)
        await server.close()

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    init=sub.add_parser('init-state');init.add_argument('--state',required=True)
    serve=sub.add_parser('serve');serve.add_argument('--state',required=True);serve.add_argument('--provision',required=True);serve.add_argument('--key',required=True);serve.add_argument('--bundle-out',required=True);serve.add_argument('--port',type=int,default=8101);serve.add_argument('--wait-for-provision',type=int,default=0,help='Bounded startup wait for operator-installed inputs, without initialization');serve.add_argument('--anonymous-policy-file',help='Root-owned enabled/disabled policy for anonymous introductions');serve.add_argument('--official-reader-port',type=int,help='Loopback operator-offered channel reader; required for channel frame relay')
    args=parser.parse_args()
    if args.command=='init-state':PublisherState.initialize(args.state);print('Private publisher ledger initialized.');return
    if not 1<=args.port<=65535:raise ValueError('Invalid loopback port')
    if not 0<=args.wait_for_provision<=30:raise ValueError('Startup wait must be 0..30 seconds')
    try:asyncio.run(run(args))
    except KeyboardInterrupt:pass
if __name__=='__main__':main()
