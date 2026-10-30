#!/usr/bin/env python3
"""Exercise shared official authorization limits without weakening login limits."""
import io,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'codiserver-server-v0.3.0')]
from codiauth.service import Config,Failure,Service
from origin_service.official_authority import OfficialAuthority

with tempfile.TemporaryDirectory() as directory:
 root=Path(directory);web=root/'public';web.mkdir();(web/'index.html').write_text('fixture')
 issuer=Service(Config(root/'state',web,origin='http://127.0.0.1:8098',rate_per_minute=3),clock=lambda:1000);issuer.base_path=''
 app=OfficialAuthority(issuer);body=json.dumps({'key':issuer.jwk,'path':'/api/v1/official-ingest/authorize'}).encode()
 def request(origin='http://127.0.0.1:8098'):
  status=[];env={'PATH_INFO':'/api/v1/official-ingest/challenge','HTTP_HOST':'127.0.0.1:8098','HTTP_ORIGIN':origin,'REQUEST_METHOD':'POST','CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(body)),'REMOTE_ADDR':'shared','wsgi.input':io.BytesIO(body)}
  result=app(env,lambda s,h:status.append(s));b''.join(result);return int(status[0].split()[0])
 assert request('http://example.com')==403
 assert all(request()==200 for _ in range(60))
 assert request()==429
 for _ in range(3):issuer.throttle('login-ip:shared')
 try:issuer.throttle('login-ip:shared')
 except Failure as error:assert error.status==429
 else:raise AssertionError('Login rate limit was weakened')
 print('PASS shared official budget remains bounded; origin and login limits remain enforced')
