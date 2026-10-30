#!/usr/bin/env python3
"""Public trusted website/TURN checks and read-only installed ingress audit."""
import hashlib
import http.client
import json
from pathlib import Path
import secrets
import shlex
import socket
import ssl
import struct
import subprocess

ROOT = Path(__file__).resolve().parent.parent
AUDIT = r'''
import csv,hashlib,http.client,io,json,os,pathlib,secrets,socket,ssl,stat,subprocess,sys,time,tomllib
Path=pathlib.Path;args=json.load(sys.stdin);receipt=Path('/srv/codi-ingress/ksu-shared-ingress-activation-result.json');r=json.loads(receipt.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):return subprocess.check_output(list(map(str,a)),text=True,timeout=20).strip()
assert not Path('/var/lib/codi-ingress/maintenance.json').exists()
files={'common.ingress.py':Path('/home/dflanag3/webhost-sites/ops/common.py'),'sites.ingress.toml':Path('/home/dflanag3/webhost-sites/sites.toml'),'Caddyfile.production':Path('/etc/caddy/Caddyfile'),'haproxy.cfg':Path('/etc/codi-ingress/haproxy.cfg'),'codi-shared-ingress.service':Path('/etc/systemd/system/codi-shared-ingress.service'),'30-codi-ingress.conf':Path('/etc/systemd/system/caddy.service.d/30-codi-ingress.conf')}
for name,p in files.items():assert digest(p)==r['candidateFilesSHA256'][name]
for name in ['haproxy.cfg','codi-shared-ingress.service','30-codi-ingress.conf']:
 p=files[name];i=p.lstat();assert stat.S_ISREG(i.st_mode) and i.st_uid==i.st_gid==0 and stat.S_IMODE(i.st_mode)==0o644 and i.st_nlink==1
runtime=Path('/srv/codi-ingress/runtimes')/r['runtimeManifestSHA256'];assert digest(runtime/'runtime.json')==runtime.name
meta=json.loads((runtime/'runtime.json').read_text());assert set(p.name for p in runtime.iterdir())=={'runtime.json',*meta['files']}
for p in [runtime,*runtime.iterdir()]:
 i=p.lstat();assert i.st_uid==i.st_gid==0 and not i.st_mode&0o022 and (stat.S_ISDIR(i.st_mode) or stat.S_ISREG(i.st_mode))
 if p.name in meta['files']:assert meta['files'][p.name]=={'bytes':i.st_size,'sha256':digest(p)}
unit='codi-shared-ingress.service';pid=int(run(['systemctl','show',unit,'-p','MainPID','--value']));assert pid==r['ingressPid']
info=dict(line.split(':',1) for line in Path('/proc',str(pid),'status').read_text().splitlines());assert set(map(int,info['Uid'].split()))=={r['ingressUID']} and r['ingressUID']>0 and info['NoNewPrivs'].strip()=='1'
assert all(int(info[n],16)==1024 for n in ['CapEff','CapBnd','CapAmb'])
assert unit in run(['systemctl','show','caddy.service','-p','Wants','--value']).split() and unit in run(['systemctl','show','caddy.service','-p','Before','--value']).split()
listeners=run(['ss','-lntpH']).splitlines();selected=[]
for port in [80,443,8080,8443]:
 lines=[line for line in listeners if line.split()[3].endswith(':'+str(port))];assert lines
 if port in [8080,8443]:assert all(line.split()[3]=='127.0.0.1:'+str(port) and 'pid='+r['existingPidsUnchanged']['caddy.service']+',' in line for line in lines)
 else:assert all('pid='+str(pid)+',' in line for line in lines)
 selected.extend(line.split()[3] for line in lines)
observed=None
if args['clientProbe']:
 token=secrets.token_hex(12);uri='/robots.txt?codi_ingress_probe='+token;raw=socket.socket();raw.settimeout(5);raw.bind(('127.0.0.3',0));raw.connect(('127.0.0.1',443));c=http.client.HTTPSConnection('ksu.codes',timeout=5);c.sock=ssl.create_default_context().wrap_socket(raw,server_hostname='ksu.codes');c.request('GET',uri);response=c.getresponse();response.read();c.close()
 data=tomllib.loads(files['sites.ingress.toml'].read_text());slug=next(s['slug'] for s in data['sites'] if s['domain']=='ksu.codes');log=Path('/var/log/caddy')/(slug+'.json')
 for attempt in range(30):
  with log.open('rb') as stream:stream.seek(max(0,log.stat().st_size-1048576));lines=stream.read(1048576).splitlines()
  for line in lines:
   try:item=json.loads(line)
   except json.JSONDecodeError:continue
   request=item.get('request',{})
   if request.get('uri')==uri:observed=request['remote_ip'];break
  if observed:break
  time.sleep(.1)
 assert observed=='127.0.0.3',observed
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as c:
 c.settimeout(3);c.connect('/run/codi-shared-ingress/stats.sock');c.sendall(b'show stat\n');c.shutdown(socket.SHUT_WR);raw=b''
 while True:
  chunk=c.recv(65536)
  if not chunk:break
  raw+=chunk
rows=csv.DictReader(io.StringIO(raw.decode().lstrip('# ')));counters={v['pxname']:int(v['stot']) for v in rows if v['svname']=='BACKEND'}
print(json.dumps({'status':'PASS','pid':pid,'uid':r['ingressUID'],'capability':'CAP_NET_BIND_SERVICE','noNewPrivileges':True,'listeners':selected,'caddyBackendsLoopbackOnly':True,'clientAddressFromProductionCaddyLog':observed,'counters':counters,'noPendingJournal':True,'activationReceiptSHA256':digest(receipt),'runtimeManifestSHA256':runtime.name}))
'''


def audit(probe=False):
    p = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', 'box-webhost', 'sudo', '-n', 'python3', '-B', '-c', shlex.quote(AUDIT)], input=json.dumps({'clientProbe': probe}), text=True, capture_output=True, timeout=45)
    if p.returncode:
        raise RuntimeError(p.stderr or p.stdout)
    return json.loads(p.stdout)


def get(host, path='/', tls=True):
    if tls:
        c = http.client.HTTPSConnection(host, timeout=15, context=ssl.create_default_context())
    else:
        c = http.client.HTTPConnection(host, timeout=15)
    try:
        c.request('GET', path)
        r = c.getresponse()
        raw = r.read(2097153)
        assert len(raw) <= 2097152
        return r.status, dict(r.headers), raw
    finally:
        c.close()


def turn():
    with ssl.create_default_context().wrap_socket(socket.create_connection(('turn.ksu.codes', 443), 10), server_hostname='turn.ksu.codes') as tls:
        address = tls.getpeername()[0]
        leaf = hashlib.sha256(tls.getpeercert(binary_form=True)).hexdigest()
        transaction = secrets.token_bytes(12)
        tls.sendall(struct.pack('!HHI12s', 3, 8, 0x2112A442, transaction) + struct.pack('!HHI', 0x19, 4, 17 << 24))
        def exact(size):
            raw = b''
            while len(raw) < size:
                chunk = tls.recv(size - len(raw))
                assert chunk
                raw += chunk
            return raw
        kind, length, magic, echo = struct.unpack('!HHI12s', exact(20))
        assert kind == 0x113 and length <= 4096 and magic == 0x2112A442 and echo == transaction
        body = exact(length)
        offset, code, realm = 0, None, None
        while offset + 4 <= len(body):
            attr, size = struct.unpack('!HH', body[offset:offset + 4])
            value = body[offset + 4:offset + 4 + size]
            assert len(value) == size
            if attr == 9 and size >= 4:
                code = (value[2] & 7) * 100 + value[3]
            if attr == 0x14:
                realm = value.decode()
            offset += 4 + ((size + 3) // 4) * 4
        assert code == 401 and realm == 'turn.ksu.codes'
        return {'publicAddress': address, 'defaultTrustedTLS': True, 'leafSHA256': leaf, 'unauthenticatedAllocation401': True, 'realm': realm}


result = {'status': 'FAIL'}
try:
    activation = json.loads((ROOT / '.build/checks/shared-ingress-apply-result.json').read_text())
    websites = {}
    for host in activation['siteDomains']:
        status, headers, body = get(host)
        assert status == 200 and body, (host, status)
        status, headers, _ = get(host, '/sample?x=1', tls=False)
        assert status == 308 and headers['Location'] == 'https://' + host + '/sample?x=1'
        websites[host] = {'https': 200, 'httpRedirect': headers['Location']}
    for path, expected in [('/desktop/' + n, pin) for n, pin in activation['desktopSHA256'].items()] + [('/hidden/' + n, pin) for n, pin in activation['frontendSHA256'].items()]:
        status, headers, body = get('ksu.codes', path)
        assert status == 200 and hashlib.sha256(body).hexdigest() == expected
    status, headers, body = get('ksu.codes', '/hidden')
    assert status == 308 and headers['Location'] == '/hidden/'
    challenge = turn()
    private = json.loads((ROOT / '.build/checks/webhost-private-relay-health-result.json').read_text())
    assert challenge['leafSHA256'] == private['certificate']['leafSHA256']
    context = ssl.create_default_context()
    context.set_alpn_protocols(['h2'])
    with context.wrap_socket(socket.create_connection(('ksu.codes', 443), 10), server_hostname='ksu.codes') as tls:
        assert tls.selected_alpn_protocol() == 'h2'
    before = audit(probe=True)
    context = ssl.create_default_context()
    context.set_alpn_protocols(['acme-tls/1'])
    try:
        with context.wrap_socket(socket.create_connection(('turn.ksu.codes', 443), 10), server_hostname='turn.ksu.codes') as tls:
            acme = {'handshakeSucceeded': True, 'selectedALPN': tls.selected_alpn_protocol()}
    except ssl.SSLError as error:
        acme = {'handshakeSucceeded': False, 'reason': error.reason}
    after = audit()
    assert after['counters']['web_tls'] >= before['counters']['web_tls'] + 1 and after['counters']['turn_tls'] == before['counters']['turn_tls']
    assert before['pid'] == after['pid'] == activation['ingressPid']
    result.update(status='PASS', scope='Public default-trusted nine-site HTTP/TLS, TURN401 and ACME routing, plus installed sandbox/listener/client-IP audit; no authenticated allocation, actual CA issuance or independent WAN claim', websites=websites, turn=challenge, publicH2Negotiated=True, acmeALPNRoutedToCaddy=True, acmeHandshake=acme, before=before, after=after, prototypeAndHiddenAssetsPreserved=True, issuerTurnPolicyConfigured=False, independentWanVerified=False, actualCaChallengeIssuanceVerified=False)
except BaseException as error:
    result['error'] = str(error)
    raise
finally:
    result['checkerSHA256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (ROOT / '.build/checks/public-ingress-result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
