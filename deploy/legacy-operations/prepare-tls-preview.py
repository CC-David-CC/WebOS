#!/usr/bin/env python3
"""Create private disposable loopback TLS fixtures; changes no trust stores."""
import argparse,base64,datetime,hashlib,ipaddress,json,os,sys
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from origin_service.mount import validate_base_path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',type=Path,default=ROOT/'.build/checks/tls-preview')
parser.add_argument('--base-path',default='',type=validate_base_path)
parser.add_argument('--valid-days',type=int,choices=[1,4],default=1,help='Disposable certificate validity; four days exercises a managed 48-hour renewal floor')
args=parser.parse_args();base=args.base_path
folder=args.output_dir.absolute()
folder.mkdir(parents=True,exist_ok=True,mode=0o700)
if folder.is_symlink():raise ValueError('Explicit private fixture directory required')
folder.chmod(0o700)
for name in ('key.pem','cert.pem','spki.txt','Caddyfile','Caddyfile.identity','Caddyfile.combined','Caddyfile.active'):
 if (folder/name).exists() or (folder/name).is_symlink():raise ValueError('TLS fixture already exists; use the existing fixture or explicitly archive it first')
key=ec.generate_private_key(ec.SECP256R1());now=datetime.datetime.now(datetime.timezone.utc)
name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'CodiServer disposable loopback test')])
cert=(x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key()).serial_number(x509.random_serial_number())
 .not_valid_before(now-datetime.timedelta(minutes=1)).not_valid_after(now+datetime.timedelta(days=args.valid_days))
 .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address('127.0.0.1')),x509.DNSName('localhost')]),critical=False).sign(key,hashes.SHA256()))
with os.fdopen(os.open(folder/'key.pem',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as output:
 output.write(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
(folder/'cert.pem').write_bytes(cert.public_bytes(serialization.Encoding.PEM))
spki=key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
(folder/'spki.txt').write_text(base64.b64encode(hashlib.sha256(spki).digest()).decode())
config='''{
 admin off
 auto_https off
}
https://127.0.0.1:8445 {
 bind 127.0.0.1
 tls CERT KEY
 @steward path /rendezvous
 reverse_proxy @steward 127.0.0.1:8117
 reverse_proxy 127.0.0.1:8116
}
'''.replace('CERT',str(folder/'cert.pem')).replace('KEY',str(folder/'key.pem'))
(folder/'Caddyfile').write_text(config)
def tls_config(steward=False,guest=False):
 body=('   route {\n    @identity_api path /api/* /discovery.json /.well-known/codi-issuer.json\n    reverse_proxy @identity_api 127.0.0.1:8118\n    reverse_proxy 127.0.0.1:8132\n   }\n' if guest else '   reverse_proxy 127.0.0.1:8118\n')
 inner=''
 if steward:inner+='  handle '+base+'/rendezvous {\n   reverse_proxy 127.0.0.1:8119\n  }\n'
 inner+=('  handle_path '+base+'/* {\n' if base else '  handle {\n')+body+'  }\n'
 if base:inner+='  handle {\n   respond "Not found" 404\n  }\n'
 return '{\n admin off\n auto_https off\n}\nhttps://:8446 {\n bind 127.0.0.1\n tls '+str(folder/'cert.pem')+' '+str(folder/'key.pem')+'\n @issuer host 127.0.0.1\n handle @issuer {\n'+inner+' }\n handle {\n  respond "Forbidden" 403\n }\n}\n'
(folder/'Caddyfile.identity').write_text(tls_config())
(folder/'Caddyfile.combined').write_text(tls_config(steward=True))
(folder/'Caddyfile.active').write_text(tls_config(steward=True,guest=True))
print('Prepared '+str(args.valid_days)+'-day loopback certificate and explicit Caddy config; no trust store changed.')
