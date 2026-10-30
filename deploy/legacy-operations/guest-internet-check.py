#!/usr/bin/env python3
"""Actual Chromium/v86 Internet check through the home-host relay."""
import argparse,hashlib,json,time,urllib.request
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8130/');parser.add_argument('--tls-spki-file');parser.add_argument('--require-trust',choices=['local','test-server']);options=parser.parse_args()
BASE='http://127.0.0.1:19515'
def req(path,data=None,method=None):
 r=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(r,timeout=100) as response:return json.load(response)['value']
chrome_args=['--headless=new','--no-sandbox','--disable-dev-shm-usage']
if options.tls_spki_file:chrome_args.append('--ignore-certificate-errors-spki-list='+Path(options.tls_spki_file).read_text().strip())
s=req('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':chrome_args}}}})['sessionId']
def js(code):return req('/session/'+s+'/execute/sync',{'script':code,'args':[]})
def wait(code,seconds=80):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if js(code):return
  time.sleep(.2)
 raise AssertionError(js('return serialScreen.text()'))
result={}
try:
 req('/session/'+s+'/url',{'url':options.url})
 runtime_config=req('/session/'+s+'/execute/async',{'script':'const done=arguments[0];fetch("/config.json").then(r=>r.json()).then(done)','args':[]})
 relay_revision=runtime_config.get('guestNetwork',{}).get('relayRevision')
 assert relay_revision==hashlib.sha256(Path('guest-relay/server.py').read_bytes()).hexdigest(),'Relay runtime revision does not match current source'
 wait('return desktopLab.guestState==="ready"')
 if options.require_trust:assert js('return currentSession.trust.level')==options.require_trust
 welcome=req('/session/'+s+'/execute/async',{'script':'const done=arguments[0];guestFiles.read("/Documents/README.txt").then(bytes=>done(new TextDecoder().decode(bytes)))','args':[]})
 assert 'Guest Internet uses the relay host and its Internet connection' in welcome and 'timeout 15 wget' in welcome and 'Guest Internet networking is not configured' not in welcome,welcome
 js("v86Instance.serial0_send('ifconfig eth0; route -n; ping -c 2 -W 4 1.1.1.1; echo PING_COMPLETE\\r');")
 wait('return serialScreen.text().includes("2 packets transmitted")',30)
 serial=js('return serialScreen.text()')
 assert '2 packets received' in serial,serial
 js("v86Instance.serial0_send("+json.dumps("nslookup example.com; timeout 15 wget -O /tmp/example.html http://example.com; grep -q 'Example Domain' /tmp/example.html && echo HTTP_CONTENT_VERIFIED; wc -c /tmp/example.html; echo WEB_COMPLETE\r")+");")
 wait('return serialScreen.text().split("WEB_COMPLETE").length>=3',35)
 serial=js('return serialScreen.text()');assert '\nHTTP_CONTENT_VERIFIED\n' in serial.replace('\r', ''),serial
 result={'status':'PASS','scope':'Real Chrome/v86, local relay-host QEMU/libslirp; not public deployment','url':options.url,'identityTrust':js('return currentSession.trust.level'),'guestWelcomeVerified':True,'relayRuntimeRevision':relay_revision,'serial':serial}
except Exception as e:
 result={'status':'FAIL','error':str(e),'serial':js('return typeof serialScreen!=="undefined"?serialScreen.text():document.body.textContent')};raise
finally:
 result['sha256']={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in ('app.js','desktop-apps.js','scripts/guest-init.sh','scripts/build-browser-initramfs.py','scripts/guest-internet-check.py','guest-relay/server.py','guest-relay/requirements.txt','.build/v86/initramfs.cpio.gz')}
 Path('.build/checks/guest-internet-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));req('/session/'+s,method='DELETE')
