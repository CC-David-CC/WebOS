#!/usr/bin/env python3
"""Small, manifest-driven operator CLI. No web admin interface or daemon."""
import argparse
import datetime
import fcntl
import hashlib
import http.client
import json
import re
import os
from pathlib import Path
import pwd
import shutil
import signal
import socket
import stat
import subprocess
import sys
import time

from common import ROOT, MANIFEST, load, dump, validate, unit, caddy
from scaffold import scaffold

BASE = Path('/srv/webapps')
CONFIG = Path('/etc/webapps')
STATE = Path('/var/lib/webhost-ops')
BACKUPS = Path('/var/backups/webhost-sites')
SOCKET = 'unix//run/caddy/admin.sock'
# Legacy mutations are frozen during/after the beta OPFS forward-only floor.
BETA_FILES_FLOOR = STATE/'opfs-floor.json'
BETA_FILES_JOURNAL = STATE/'opfs-transition.json'
BETA_V2_BLOCK_SHA = 'b29f6d8858669f3fc1f5755392b59e27c6a860ebdd0fa61dd479704a60876387'
ACTIVE_CADDY = Path('/etc/caddy/Caddyfile')
_floor_guard_active = False

def run(args, **kw):
    return subprocess.run([str(a) for a in args], check=True, text=True, **kw)

def stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')

def root_required():
    if os.geteuid()!=0: raise RuntimeError('This operation requires sudo.')
    if socket.gethostname()!='box-webhost': raise RuntimeError('Wrong target host.')

def owner():
    return pwd.getpwuid(ROOT.stat().st_uid)

def write(path, content, mode=0o640, uid=0, gid=0, backup=True):
    path=Path(path)
    if path.is_symlink(): raise ValueError(f'Refusing config symlink: {path}')
    raw=content.encode() if isinstance(content,str) else content
    if path.exists() and path.read_bytes()==raw: return
    if backup and path.exists(): snapshot(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.new-'+stamp())
    tmp.write_bytes(raw)
    os.chown(tmp,uid,gid); os.chmod(tmp,mode)
    os.replace(tmp,path)

def snapshot(path):
    dest=BACKUPS/('change-'+stamp())
    dest.mkdir(parents=True,mode=0o700)
    os.chmod(BACKUPS,0o700)
    shutil.copy2(path,dest/Path(path).name)
    (dest/'source-path.txt').write_text(str(path)+'\n')
    return dest

def _check_floor_record():
    parent=BETA_FILES_FLOOR.parent.lstat()
    if not stat.S_ISDIR(parent.st_mode) or parent.st_uid!=os.geteuid() or stat.S_IMODE(parent.st_mode)!=0o700: raise ValueError('Unsafe beta floor custody')
    fd=os.open(BETA_FILES_FLOOR,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        a=os.fstat(fd)
        if not stat.S_ISREG(a.st_mode) or a.st_uid!=os.geteuid() or stat.S_IMODE(a.st_mode)!=0o600 or a.st_nlink!=1 or a.st_size>4096: raise ValueError('Unsafe beta floor')
        raw=os.read(fd,4097);z=os.fstat(fd)
        if len(raw)!=a.st_size or (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns): raise ValueError('Beta floor changed')
    finally:os.close(fd)
    value=json.loads(raw)
    if not isinstance(value,dict) or set(value)!={'version','baseline','candidate'} or type(value['version']) is not int or value['version']!=1 or value['candidate']!='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc' or not isinstance(value['baseline'],str) or not re.fullmatch('[0-9a-f]{64}',value['baseline']): raise ValueError('Unrecognized beta floor')

def _beta_block(data):
    marker='beta.ksu.codes {'
    if data.count(marker)!=1: raise ValueError('Expected exactly one beta site block')
    start=data.index(marker); end=data.find('\n}\n',start)
    if end<0: raise ValueError('Incomplete beta site block')
    return data[start:end+3]

def _assert_v2_beta(data):
    if not _floor_guard_active: return
    if data.get('codi_beta_opfs')!='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc' or data.get('codi_beta_maintenance') is not False:
        raise ValueError('Legacy hosting must preserve active beta v2')
    proposed=_beta_block(caddy(data,'production'))
    if hashlib.sha256(proposed.encode()).hexdigest()!=BETA_V2_BLOCK_SHA: raise ValueError('Unreviewed beta route output')
    fd=os.open(ACTIVE_CADDY,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.geteuid() or before.st_mode&0o022 or before.st_nlink!=1 or before.st_size>4*1024*1024: raise ValueError('Unsafe active Caddyfile')
        raw=b''
        while len(raw)<=4*1024*1024:
            part=os.read(fd,min(65536,4*1024*1024+1-len(raw)))
            if not part: break
            raw+=part
        after=os.fstat(fd)
        if len(raw)!=before.st_size or (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns): raise ValueError('Active Caddyfile changed')
    finally:os.close(fd)
    active=raw.decode('utf-8')
    if '# webhost-sites mode: production' not in active or _beta_block(active)!=proposed: raise ValueError('Active beta route is not the reviewed v2 route')

def save_manifest(data):
    _assert_v2_beta(data)
    p=owner()
    write(MANIFEST,dump(data),0o644,p.pw_uid,p.pw_gid)

def site(data, domain):
    for s in data['sites']:
        if s['domain']==domain: return s
    raise ValueError('Domain is not in sites.toml')

def render(data):
    _assert_v2_beta(data)
    p=owner()
    for mode in ['prepare','production']:
        write(ROOT/f'deploy/caddy/Caddyfile.{mode}',caddy(data,mode),0o644,p.pw_uid,p.pw_gid,False)
    for s in data['sites']:
        write(ROOT/f"deploy/systemd/{s['service']}",unit(s),0o644,p.pw_uid,p.pw_gid,False)

def account(s):
    try:
        a=pwd.getpwnam(s['user'])
        if a.pw_shell!='/usr/sbin/nologin' or a.pw_dir!='/nonexistent':
            raise RuntimeError('Existing service account does not match expected no-login account')
    except KeyError:
        run(['useradd','--system','--user-group','--no-create-home','--home-dir','/nonexistent','--shell','/usr/sbin/nologin',s['user']])
        a=pwd.getpwnam(s['user'])
    for path in [BASE/s['domain'],BASE/s['domain']/'releases']:
        path.mkdir(parents=True,exist_ok=True)
        os.chown(path,0,a.pw_gid); os.chmod(path,0o711)
    return a

def install_unit(s):
    CONFIG.mkdir(exist_ok=True,mode=0o755)
    env=CONFIG/f"{s['slug']}.env"
    if not env.exists(): write(env,f"WEB_WORKERS={s['workers']}\n",0o600)
    write(Path('/etc/systemd/system')/s['service'],unit(s),0o644)
    run(['systemd-analyze','verify',Path('/etc/systemd/system')/s['service']],stdout=subprocess.DEVNULL)
    run(['systemctl','daemon-reload'])

def request(s,path='/healthz',port=None):
    if s.get('hardware_studio'):
        from hardware_hosting import request as hardware_request
        return hardware_request(s,path,port)
    if s.get('cardboard_studio'):
        from cardboard_hosting import request as cardboard_request
        return cardboard_request(s,path,port)
    c=http.client.HTTPConnection('127.0.0.1',port or s['port'],timeout=8)
    try:
        c.request('GET',path,headers={'Host':s['domain']})
        r=c.getresponse(); body=r.read()
        if path=='/healthz':
            assert r.status==200 and json.loads(body)=={'status':'ok','site':s['domain']}
        else: assert r.status==200 and f"site:{s['domain']}:starter-v1".encode() in body
    finally: c.close()

def healthy(s):
    for _ in range(30):
        try: request(s); return
        except (OSError,AssertionError,json.JSONDecodeError): time.sleep(.3)
    raise RuntimeError(f"Health failed: {s['domain']}")

def point(s, release):
    target=BASE/s['domain']/'releases'/release
    if not target.is_dir() or target.is_symlink(): raise ValueError('Invalid release')
    link=BASE/s['domain']/'current'
    tmp=link.with_name('current.new-'+stamp())
    tmp.symlink_to(Path('releases')/release)
    os.replace(tmp,link)

def release_state(s):
    path=STATE/f"{s['slug']}.json"
    return json.loads(path.read_text()) if path.exists() else {'current':None,'previous':None}

def record_release(s,current,previous):
    STATE.mkdir(exist_ok=True,mode=0o700)
    write(STATE/f"{s['slug']}.json",json.dumps(dict(current=current,previous=previous),indent=2)+'\n',0o600)

def deploy(s):
    if s.get('hardware_studio'):
        from hardware_hosting import deploy as hardware_deploy
        return hardware_deploy(s,sys.modules[__name__])
    if s.get('cardboard_studio'):
        from cardboard_hosting import deploy as cardboard_deploy
        return cardboard_deploy(s,sys.modules[__name__])
    if not (BASE/s['domain']/'current').exists():
        with socket.socket() as probe:
            try: probe.bind(('127.0.0.1',s['port']))
            except OSError as e: raise RuntimeError(f"Application port already occupied: {s['port']}") from e
    a=account(s); p=owner()
    source=ROOT/'sites'/s['domain']
    if not source.is_dir(): raise RuntimeError('Missing site source')
    for path in source.rglob('*'):
        if path.is_symlink(): raise ValueError(f'Source symlinks are not publishable: {path}')
    digest=hashlib.sha256()
    for path in sorted(source.rglob('*')):
        if path.is_file(): digest.update(path.read_bytes())
    rid=stamp()+'-'+digest.hexdigest()[:8]
    dest=BASE/s['domain']/'releases'/rid
    dest.mkdir(mode=0o750)
    os.chown(dest,p.pw_uid,a.pw_gid)
    for folder in ['app','public']:
        shutil.copytree(source/folder,dest/folder)
    for name in ['requirements.in','requirements.lock.txt']:
        if (source/name).exists(): shutil.copy2(source/name,dest/name)
    for path in [dest]+list(dest.rglob('*')): os.chown(path,p.pw_uid,a.pw_gid)
    prefix=['runuser','-u',p.pw_name,'--']
    run(prefix+['python3','-m','venv',str(dest/'.venv')])
    py=str(dest/'.venv/bin/python')
    requirement='requirements.lock.txt' if (dest/'requirements.lock.txt').exists() else 'requirements.in'
    run(prefix+[py,'-m','pip','install','--disable-pip-version-check','--only-binary=:all:','-r',str(dest/requirement)])
    run(prefix+[py,'-m','pip','check'])
    frozen=run(prefix+[py,'-m','pip','freeze'],capture_output=True).stdout
    (dest/'requirements.lock.txt').write_text(frozen)
    if not (source/'requirements.lock.txt').exists():
        write(source/'requirements.lock.txt',frozen,0o644,p.pw_uid,p.pw_gid,False)
    # Lock every release to root and its own runtime group. Apps cannot modify it.
    for path in [dest]+list(dest.rglob('*')):
        if path.is_symlink(): continue
        mode=path.stat().st_mode
        os.chown(path,0,a.pw_gid)
        os.chmod(path,0o750 if path.is_dir() or mode & stat.S_IXUSR else 0o640)
    run(['runuser','-u',s['user'],'--','env','PYTHONDONTWRITEBYTECODE=1',py,'-c','from app.main import app; assert not app.debug'],cwd=dest)
    # Exercise the candidate release privately before changing current.
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0)); candidate_port=probe.getsockname()[1]
    candidate=subprocess.Popen(['runuser','-u',s['user'],'--','env','PYTHONDONTWRITEBYTECODE=1',py,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(candidate_port),'--no-access-log'],cwd=dest,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    try:
        for attempt in range(40):
            try: request(s,port=candidate_port); break
            except (OSError,AssertionError): time.sleep(.2)
        else: raise RuntimeError('Candidate release failed its independent health test')
        request(s,path='/',port=candidate_port)
    finally:
        os.killpg(candidate.pid,signal.SIGTERM)
        candidate.wait(timeout=15)
    prior=release_state(s)
    point(s,rid)
    try:
        install_unit(s)
        run(['systemctl','restart',s['service']]); healthy(s)
        run(['systemctl','enable',s['service']],stdout=subprocess.DEVNULL)
    except Exception:
        if prior['current']:
            point(s,prior['current']); run(['systemctl','restart',s['service']]); healthy(s)
        else:
            run(['systemctl','stop',s['service']])
        raise
    record_release(s,rid,prior['current'])
    print(f"Deployed {s['domain']}: {rid}",flush=True)

def caddy_validate(path):
    run(['runuser','-u','caddy','--','/usr/bin/caddy','validate','--config',str(path),'--adapter','caddyfile'])

def current_mode():
    path=Path('/etc/caddy/Caddyfile')
    if path.exists() and '# webhost-sites mode: production' in path.read_text(): return 'production'
    return 'prepare'

def caddy_apply(data,mode):
    if _floor_guard_active and mode!='production': raise ValueError('Legacy hosting cannot change beta out of production')
    _assert_v2_beta(data)
    render(data)
    a=pwd.getpwnam('caddy')
    logs=Path('/var/log/caddy'); logs.mkdir(exist_ok=True)
    os.chown(logs,a.pw_uid,a.pw_gid); os.chmod(logs,0o750)
    for m in ['prepare','production']:
        path=Path(f'/etc/caddy/Caddyfile.{m}')
        write(path,caddy(data,m),0o640,0,a.pw_gid)
        caddy_validate(path)
    active=Path('/etc/caddy/Caddyfile')
    old=active.read_bytes() if active.exists() else None
    write(active,caddy(data,mode),0o640,0,a.pw_gid)
    try:
        if subprocess.run(['systemctl','is-active','--quiet','caddy']).returncode==0:
            run(['systemctl','reload','caddy'])
        else:
            run(['systemctl','unmask','--runtime','caddy.service','caddy-api.service'])
            run(['systemctl','enable','--now','caddy.service'])
    except Exception:
        if old is not None:
            write(active,old,0o640,0,a.pw_gid)
            run(['systemctl','reload','caddy'])
        raise

def setup_caddy():
    write('/etc/systemd/system/caddy.service.d/webhost.conf','''[Service]
RuntimeDirectory=caddy
RuntimeDirectoryMode=0700
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile --force --address unix//run/caddy/admin.sock
''',0o644)
    run(['systemctl','daemon-reload'])

def gates(data,args):
    for flag in ['owner_confirmed','stable_lan_confirmed','public_ip_confirmed','firewall_verified']:
        if not getattr(args,flag): raise RuntimeError('Public activation requires all explicit readiness confirmations.')
    # The reviewed policy must be live; do not treat UFW status as an ingress test.
    nft=run(['nft','list','table','inet','webhost_guard'],capture_output=True).stdout
    if 'policy drop' not in nft or 'tailscale0' not in nft:
        raise RuntimeError('Reviewed effective host firewall is not installed.')
    for s in data['sites']:
        if not s['enabled']: continue
        for resolver in ['1.1.1.1','8.8.8.8']:
            for kind in ['A','AAAA']:
                raw=run(['dig','@'+resolver,s['domain'],kind,'+tcp','+time=4','+tries=2','+noall','+comments','+answer'],capture_output=True).stdout
                if 'status: NOERROR' not in raw: raise RuntimeError('DNS response unsuccessful')
                vals={line.split()[-1] for line in raw.splitlines() if line and not line.startswith(';') and len(line.split())>=5 and line.split()[3]==kind}
                if (kind=='A' and vals!={'104.180.210.33'}) or (kind=='AAAA' and vals):
                    raise RuntimeError(f'DNS readiness failed: {s["domain"]} {kind} {vals}')
        healthy(s)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    for name in ['prepare','render','status','validate','private']:
        sub.add_parser(name)
    for name in ['deploy','up','down','restart','rollback','workers']:
        sp=sub.add_parser(name); sp.add_argument('domain')
        if name=='workers': sp.add_argument('count',type=int)
    sp=sub.add_parser('add'); sp.add_argument('domain'); sp.add_argument('--slug'); sp.add_argument('--theme',required=True); sp.add_argument('--description',required=True); sp.add_argument('--port',type=int); sp.add_argument('--accent',default='#215e51')
    sp=sub.add_parser('activate')
    for flag in ['owner-confirmed','stable-lan-confirmed','public-ip-confirmed','firewall-verified']: sp.add_argument('--'+flag,action='store_true')
    sp=sub.add_parser('caddy-rollback'); sp.add_argument('backup',type=Path)
    args=p.parse_args()
    if args.command=='status':
        data=load()
        try: mode=current_mode()
        except PermissionError: mode='run status with sudo to read the protected active configuration'
        print('Caddy mode:',mode)
        for s in data['sites']:
            state=subprocess.run(['systemctl','is-active',s['service']],text=True,capture_output=True).stdout.strip()
            print(s['domain'],s['port'],s['workers'],s['enabled'],state)
        return
    root_required()
    ROOT.joinpath('.controller.lock').touch(exist_ok=True)
    with ROOT.joinpath('.controller.lock').open('r') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # Pending work blocks all legacy writes. A durable floor permits
        # only reviewed v2-preserving production changes after locked loading.
        try: BETA_FILES_JOURNAL.lstat()
        except FileNotFoundError: pass
        else: raise RuntimeError('Legacy hosting writes frozen by pending beta Files transition')
        global _floor_guard_active
        try: BETA_FILES_FLOOR.lstat()
        except FileNotFoundError: _floor_guard_active=False
        else: _floor_guard_active=True
        data=load()
        if _floor_guard_active:
            _check_floor_record()
            if args.command in ('prepare','private','caddy-rollback'): raise RuntimeError('Legacy hosting cannot replace active beta v2 routes')
            _assert_v2_beta(data)
        if args.command=='render': render(data)
        elif args.command=='validate':
            render(data)
            for s in data['sites']: run(['systemd-analyze','verify',ROOT/'deploy/systemd'/s['service']])
            for m in ['prepare','production']: caddy_validate(f'/etc/caddy/Caddyfile.{m}')
        elif args.command=='prepare':
            if current_mode()=='production': raise RuntimeError('Use private explicitly to leave production.')
            setup_caddy()
            for s in data['sites']:
                if s['enabled'] and not (BASE/s['domain']/'current').exists(): deploy(s)
            caddy_apply(data,'prepare')
        elif args.command=='private': caddy_apply(data,'prepare')
        elif args.command=='activate': gates(data,args); caddy_apply(data,'production')
        elif args.command=='add':
            slug=args.slug or args.domain.replace('.','-')
            port=args.port or max([s['port'] for s in data['sites']]+[8010])+1
            s=dict(domain=args.domain,slug=slug,port=port,service=f'web-{slug}.service',user=f'site-{slug}',workers=1,enabled=False,theme=args.theme,description=args.description,accent=args.accent)
            data['sites'].append(s); validate(data); snapshot(MANIFEST); scaffold(s)
            account_owner=owner()
            for x in (ROOT/'sites'/s['domain']).rglob('*'): os.chown(x,account_owner.pw_uid,account_owner.pw_gid)
            os.chown(ROOT/'sites'/s['domain'],account_owner.pw_uid,account_owner.pw_gid)
            save_manifest(data); render(data)
            print('Scaffolded only; review content/DNS before webctl up. No DNS changes made.')
        elif args.command=='caddy-rollback':
            path=args.backup.resolve()
            if not path.is_relative_to(BACKUPS) or not path.is_file(): raise ValueError('Use a config file under the backup directory')
            text=path.read_text()
            if '# webhost-sites mode: prepare' not in text:
                raise ValueError('Only private Caddy rollback here; production rollback needs the activation gate')
            a=pwd.getpwnam('caddy')
            candidate=Path('/etc/caddy/Caddyfile.rollback-candidate')
            write(candidate,text,0o640,0,a.pw_gid)
            caddy_validate(candidate)
            write('/etc/caddy/Caddyfile',text,0o640,0,a.pw_gid)
            run(['systemctl','reload','caddy'])
        else:
            s=site(data,args.domain)
            if args.command=='deploy':
                if not s['enabled']: raise ValueError('Site is down; use up to deploy/start it')
                deploy(s)
            elif args.command=='restart': run(['systemctl','restart',s['service']]); healthy(s)
            elif args.command=='workers':
                s['workers']=args.count; validate(data)
                write(CONFIG/f"{s['slug']}.env",f'WEB_WORKERS={args.count}\n',0o600)
                if s['enabled']: run(['systemctl','restart',s['service']]); healthy(s)
                save_manifest(data); render(data)
            elif args.command=='rollback':
                prior=release_state(s)
                if not prior['previous']: raise ValueError('No preceding release retained')
                point(s,prior['previous'])
                try: run(['systemctl','restart',s['service']]); healthy(s)
                except Exception:
                    point(s,prior['current']); run(['systemctl','restart',s['service']]); raise
                record_release(s,prior['previous'],prior['current'])
            elif args.command=='down':
                s['enabled']=False
                caddy_apply(data,current_mode())
                run(['systemctl','disable','--now',s['service']]); save_manifest(data)
            elif args.command=='up':
                if current_mode()=='production' and not s['enabled']:
                    raise RuntimeError('New public hostname requires reviewed DNS/TLS; return to private preparation first.')
                if not (BASE/s['domain']/'current').exists(): deploy(s)
                else: run(['systemctl','enable','--now',s['service']]); healthy(s)
                s['enabled']=True
                caddy_apply(data,current_mode()); save_manifest(data)

if __name__=='__main__':
    try: main()
    except Exception as e:
        print(f'ERROR: {e}',file=sys.stderr)
        sys.exit(1)
