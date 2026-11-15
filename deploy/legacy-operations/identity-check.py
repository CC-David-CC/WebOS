#!/usr/bin/env python3
"""Real Chromium + loopback issuer integration; no production authority claim."""
import argparse,hashlib,json,re,ssl,time,urllib.request
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8098/');parser.add_argument('--tls-spki-file');parser.add_argument('--ca-file');parser.add_argument('--public-tls',action='store_true');parser.add_argument('--probe-account-name');options=parser.parse_args()
if options.public_tls and (not options.url.startswith('https://') or options.tls_spki_file or options.ca_file):parser.error('Public TLS requires HTTPS and default trust without certificate overrides')
if options.probe_account_name and not re.fullmatch('publiccheck_[0-9a-f]{12}',options.probe_account_name):parser.error('Explicit probe account must be a publiccheck_ random name')
origin=options.url.rstrip('/')
BASE='http://127.0.0.1:19515'
def request(path,data=None,method=None):
    req=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
    with urllib.request.urlopen(req,timeout=120) as r:return json.load(r)['value']
chrome_args=['--headless=new','--no-sandbox','--disable-dev-shm-usage']
if options.tls_spki_file:chrome_args.append('--ignore-certificate-errors-spki-list='+Path(options.tls_spki_file).read_text().strip())
s=request('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':chrome_args}}}})['sessionId']
def js(code):return request('/session/'+s+'/execute/sync',{'script':code,'args':[]})
def asyncjs(code):
    result=request('/session/'+s+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({value})).catch(e=>done({error:e.message}));','args':[]})
    assert 'error' not in result,result
    return result['value']
try:
    request('/session/'+s+'/url',{'url':options.url})
    deadline=time.monotonic()+100
    while time.monotonic()<deadline:
        if js('return window.desktopLab?.guestState==="ready"'):break
        time.sleep(.3)
    assert js('return desktopLab.guestState==="ready"'),js('return document.body.textContent')
    assert js('return isSecureContext')
    assert js('return currentSession.trust.level==="test-server"&&currentSession.public.kind==="anonymous"')
    js('window.identityProbeAccount='+json.dumps(options.probe_account_name))
    result=asyncjs('''
      const id=currentSession.public.sid,key=currentSession.fingerprint;
      // Exercise the desktop renewal scheduler's due branch without waiting 12 minutes.
      currentSession.trust.claims.exp=Math.floor(Date.now()/1000)+100;
      await maintainIdentity();
      if(currentSession.trust.claims.exp-Math.floor(Date.now()/1000)<800)throw Error('Desktop renewal did not refresh certificate');
      const before=currentSession.public.certificate;
      await identityModule.renewSession(identityConfig,currentSession);
      if(currentSession.public.sid!==id||currentSession.fingerprint!==key||currentSession.public.certificate===before)throw Error('Renewal binding failed');
      const name=window.identityProbeAccount||'test_'+crypto.randomUUID().replaceAll('-','').slice(0,12);
      const password=crypto.randomUUID()+crypto.randomUUID();
      const one=await identityModule.beginSession(identityConfig,'registered',name,password);
      const two=await identityModule.beginSession(identityConfig,'registered',name,password);
      if(one.public.sub!==two.public.sub||one.public.sid===two.public.sid||one.fingerprint===two.fingerprint)throw Error('Account/session separation failed');
      let rejected=false;try{await identityModule.beginSession(identityConfig,'registered',name,password+'wrong');}catch{rejected=true;}
      if(!rejected)throw Error('Wrong password accepted');
      await identityModule.logoutSession(identityConfig,one);
      let revoked=false;try{await identityModule.renewSession(identityConfig,one);}catch{revoked=true;}
      if(!revoked)throw Error('Logged out session renewed');
      await identityModule.logoutSession(identityConfig,two);
      return {anonymousEntry:true,realGuestBoot:true,desktopRenewal:true,renewalSameKeyAndSession:true,stableAccountFreshSession:true,wrongPasswordRejected:true,logoutRevoked:true,trust:currentSession.trust.label,probeAccount:name};
    ''')
    # Private state/source paths must not be reachable through the public service.
    import urllib.error
    for path in ['/issuer.pem','/accounts.sqlite3','/scripts/serve-connected.py','/.build/connected-state/issuer.pem']:
        try:urllib.request.urlopen(origin+path,context=ssl.create_default_context(cafile=options.ca_file) if options.ca_file else None);raise AssertionError('Private resource served')
        except urllib.error.HTTPError as e:assert e.code==404
    context=ssl.create_default_context(cafile=options.ca_file) if options.ca_file else None
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args):return None
    opener=urllib.request.build_opener(NoRedirect(),urllib.request.HTTPSHandler(context=context))
    foreign_host_rejected=True
    for headers in ({'Origin':'https://foreign.invalid'},{'Origin':origin,'Host':'foreign.invalid'}):
        probe=urllib.request.Request(origin+'/api/v1/challenge',data=b'{}',headers={'Content-Type':'application/json',**headers})
        try:
            with opener.open(probe,timeout=10) as response:
                # An unmatched hostname reaches no Caddy site. Its default empty
                # 200 is not an issuer challenge or acceptance of that Host.
                if options.public_tls and headers.get('Host')=='foreign.invalid':
                    assert response.status==200 and response.read(1)==b'' and response.headers.get_content_type()!='application/json'
                    foreign_host_rejected=False
                else:raise AssertionError('Wrong issuer Origin accepted')
        except urllib.error.HTTPError as error:assert error.code in ((403,404,421) if options.public_tls and headers.get('Host')=='foreign.invalid' else (403,)),error
    result['foreignOriginRejected']=True
    result['foreignHostRejected']=foreign_host_rejected
    result['foreignHostNotRoutedToIssuer']=True
    result['privatePathsNotServed']=True
    result['url']=options.url
    result['https']=origin.startswith('https://')
    result['secureContext']=True
    result['defaultCertificateTrust']=options.public_tls
    result['servedAssetsSHA256']={}
    for name in ('app.js','network/identity.mjs'):
        with urllib.request.urlopen(origin+'/'+name,context=context,timeout=15) as response:
            result['servedAssetsSHA256'][name]=hashlib.sha256(response.read()).hexdigest()
    result['sha256']={'scripts/identity-check.py':hashlib.sha256(Path('scripts/identity-check.py').read_bytes()).hexdigest()}
    Path('.build/checks/identity-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
finally:request('/session/'+s,method='DELETE')
