#!/usr/bin/env python3
"""Real isolated TURN quota, profile migration, death recovery and rollback proof."""
import datetime,hashlib,hmac,json,os,secrets,shutil,socket,ssl,struct,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from relay_service import manager as relay
from steward.turn_credentials import mint

def attribute(kind,value):return struct.pack('!HH',kind,len(value))+value+b'\0'*((-len(value))%4)
def exact(stream,size):
 data=b''
 while len(data)<size:
  chunk=stream.recv(size-len(data))
  if not chunk:raise AssertionError('Truncated TURN response')
  data+=chunk
 return data
def exchange(tls,attrs,key=None):
 transaction=secrets.token_bytes(12);body=b''.join(attribute(k,v) for k,v in attrs)
 header=struct.pack('!HHI12s',3,len(body)+(24 if key else 0),0x2112a442,transaction)
 tls.sendall(header+body+(attribute(8,hmac.new(key,header+body,hashlib.sha1).digest()) if key else b''))
 header=exact(tls,20);kind,size,magic,echo=struct.unpack('!HHI12s',header);assert magic==0x2112a442 and echo==transaction and size<=4096
 body=exact(tls,size);values={};offset=0
 while offset<len(body):
  attr,length=struct.unpack('!HH',body[offset:offset+4]);value=body[offset+4:offset+4+length];assert len(value)==length
  if attr==8 and key:
   signed=struct.pack('!HHI12s',kind,offset+24,magic,echo)+body[:offset]
   assert hmac.compare_digest(value,hmac.new(key,signed,hashlib.sha1).digest()),'TURN response integrity'
  values[attr]=value;offset+=4+((length+3)//4)*4
 code=(values[9][2]&7)*100+values[9][3] if 9 in values else None
 return kind,values,code

def main():
 assert os.geteuid()==0
 name='codi-relay-bandwidth-'+secrets.token_hex(5);stage=Path('/srv')/name;manager=None;streams=[];checks=[]
 result={'status':'FAIL','scope':__doc__,'publicIngressOrWANTested':False}
 def passed(label):checks.append(label)
 try:
  stage.mkdir(mode=0o755);binary=stage/'turnserver';shutil.copyfile(ROOT/'.build/tools/coturn-4.18.0-build-r1/runtime/turnserver',binary);binary.chmod(0o755)
  key=ec.generate_private_key(ec.SECP256R1());now=datetime.datetime.now(datetime.timezone.utc);subject=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'turn.fixture.invalid')])
  cert=x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-datetime.timedelta(minutes=1)).not_valid_after(now+datetime.timedelta(days=4)).add_extension(x509.SubjectAlternativeName([x509.DNSName('turn.fixture.invalid')]),critical=False).sign(key,hashes.SHA256())
  cert_pem=cert.public_bytes(serialization.Encoding.PEM);key_pem=key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
  manager=relay.Manager(stage/'config');kwargs={'instance':name,'hostname':'turn.fixture.invalid','binary':binary,'port':17489,'unit_dir':'/run/systemd/system','cert':cert_pem,'key':key_pem}
  with manager.locked():manager.configure(**kwargs);manager.start();legacy=manager.load();secret=manager.secret()
  context=ssl.create_default_context(cadata=cert_pem.decode())
  def allocate(credential=None):
   tls=context.wrap_socket(socket.create_connection(('127.0.0.1',17489),3),server_hostname='turn.fixture.invalid');tls.settimeout(4);streams.append(tls)
   assert hashlib.sha256(tls.getpeercert(binary_form=True)).hexdigest()==hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest()
   transport=[(0x19,struct.pack('!I',17<<24))]
   kind,values,code=exchange(tls,transport);assert kind==0x113 and code==401
   credential=credential or mint(secret)
   authkey=hashlib.md5(credential['username'].encode()+b':'+values[0x14]+b':'+credential['credential'].encode()).digest()
   kind,values,code=exchange(tls,transport+[(6,credential['username'].encode()),(0x14,values[0x14]),(0x15,values[0x15])],authkey)
   if kind==0x103:
    assert 8 in values and code is None and 0x16 in values
    assert values[0x16][1]==1 and socket.inet_ntoa(bytes(a^b for a,b in zip(values[0x16][4:8],struct.pack('!I',0x2112a442))))=='127.0.0.2'
   else:assert kind==0x113 and code is not None
   return code
  def close_streams():
   for stream in streams:stream.close()
   streams.clear()
   # Observe actual allocation teardown, rather than assume the TLS close releases it.
   end=time.monotonic()+8
   while time.monotonic()<end:
    pid=manager.states(manager.load())[name+'.service']['MainPID']
    rows=subprocess.check_output(['nsenter','-t',pid,'-n','ss','-H','-uan'],text=True).splitlines()
    if not rows:return
    time.sleep(.1)
   raise AssertionError('TURN allocations retained after owned streams closed')
  assert [allocate() for _ in range(4)]==[None]*4 and allocate()==486
  passed('legacy actual authenticated fifth allocation refused at bandwidth reservation ceiling')
  close_streams()
  with manager.locked():
   changed=manager.bandwidth_profile('text-32k/1');text=manager.load();assert changed['effectiveBandwidthAllocationSlots']==32 and changed['aggregateReservedBytesPerSecond']==1048576
   assert manager.secret()==secret and {k:v for k,v in text.items() if k not in ('bundle','version','bandwidthProfile')}=={k:v for k,v in legacy.items() if k not in ('bundle','version','bandwidthProfile')}
  assert [allocate() for _ in range(32)]==[None]*32 and allocate()==486
  passed('text profile admits32 real authenticated allocations and refuses33 without raising aggregate ceiling')
  close_streams()
  same=mint(secret);assert [allocate(same) for _ in range(8)]==[None]*8 and allocate(same)==486
  passed('per-username eight-allocation quota still enforced below global capacity')
  close_streams()
  with manager.locked():
   changed=manager.bandwidth_profile('text-256/1');large=manager.load()
   assert changed['effectiveBandwidthAllocationSlots']==256 and changed['aggregateReservedBytesPerSecond']==8388608
  same=mint(secret);assert [allocate(same) for _ in range(32)]==[None]*32 and allocate(same)==486
  passed('larger profile admits32 actual allocations for one username and refuses33')
  close_streams()
  with manager.locked():manager.bandwidth_profile('text-32k/1');assert manager.load()==text
  with manager.locked():
   pids=manager.states(text);assert manager.bandwidth_profile('text-32k/1')['status']=='relay-already-current' and manager.states(text)==pids
   assert manager.configure(**kwargs)['status']=='relay-already-current' and manager.load()==text and manager.states(text)==pids
   try:manager.bandwidth_profile('unlimited');raise AssertionError('Unknown profile accepted')
   except ValueError:pass
   assert manager.load()==text and manager.states(text)==pids
  passed('profile no-op and same-certificate refresh retain PIDs; unknown profile refused')
  with manager.locked():manager.bandwidth_profile('legacy');assert manager.load()==legacy
  assert [allocate() for _ in range(4)]==[None]*4 and allocate()==486
  passed('explicit rollback restores exact legacy metadata and effective quota')
  close_streams()
  for phase,exitcode in [('prepared',87),('committed',88)]:
   child=os.fork()
   if child==0:
    try:
     with manager.locked():
      if phase=='prepared':
       original=manager.apply
       def killed(value):original(value);os._exit(exitcode)
       manager.apply=killed
      else:manager.clear=lambda:os._exit(exitcode)
      manager.bandwidth_profile('text-32k/1')
    finally:os._exit(99)
   _,status=os.waitpid(child,0);assert os.waitstatus_to_exitcode(status)==exitcode and manager.journal.exists()
   with manager.locked():
    restored=manager.recover();assert not manager.journal.exists()
    assert restored['status']==('interrupted-relay-rolled-back' if phase=='prepared' else 'committed-relay-recovered')
    assert manager.load()==(legacy if phase=='prepared' else text) and manager.secret()==secret
    assert manager.ready(manager.load())['unauthenticatedAllocation401']
   passed('actual process death after '+phase+' profile transition recovers correct generation')
  assert [allocate() for _ in range(8)]==[None]*8
  passed('recovered text generation admits more than legacy four allocations')
  close_streams()
  result.update(status='PASS',checks=checks,legacyEffectiveAllocations=4,textEffectiveAllocations=32,aggregateReservedBytesPerSecond=1048576,secretPreserved=True,routerFirewallAndPublicPortsChanged=False)
 finally:
  for stream in streams:stream.close()
  if manager:
   with manager.locked():
    if manager.journal.exists():manager.recover()
    if manager.config.exists():
     value=manager.load();manager.stop()
     for unit in manager.names(value):(Path(value['unitDir'])/unit).unlink(missing_ok=True)
   subprocess.run(['systemctl','daemon-reload'],check=True)
   subprocess.run(['systemctl','reset-failed',*manager.names(value)],capture_output=True)
  if stage.exists():shutil.rmtree(stage)
  result['fixtureRemoved']=not stage.exists();result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['relay_service/manager.py','scripts/manage-relay.py','scripts/relay-bandwidth-profile-check.py']}
  output=ROOT/'.build/checks/relay-bandwidth-profile-result.json'
  if output.exists():output.rename(output.with_name(output.stem+'-before-'+str(time.time_ns())+'.json'))
  output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
