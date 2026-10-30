#!/usr/bin/env python3
"""Actual public GET/HEAD canonical redirect and fresh default-trusted Chrome."""
import base64,hashlib,http.client,json,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks';BASE='http://127.0.0.1:19515'
def driver(path,data=None,method=None):
 request=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(request,timeout=120) as response:return json.load(response)['value']
entries={}
for method in ['GET','HEAD']:
 connection=http.client.HTTPSConnection('ksu.codes',timeout=15)
 try:
  connection.request(method,'/hidden');response=connection.getresponse();response.read();assert response.status==308 and response.getheader('Location')=='/hidden/'
  entries[method]={'status':response.status,'location':response.getheader('Location')}
 finally:connection.close()
witnesses=[]
for suffix in ['hidden','hidden/']:
 session=driver('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1366,900']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
 try:
  driver('/session/'+session+'/url',{'url':'https://ksu.codes/'+suffix})
  deadline=time.monotonic()+100
  while True:
   state=driver('/session/'+session+'/execute/sync',{'script':'return {url:location.href,title:document.title,secure:isSecureContext,desktops:document.querySelectorAll(".desktop").length,state:window.desktopLab?.guestState,text:document.body.innerText.slice(0,1000)}','args':[]})
   if state.get('state')=='ready':break
   if time.monotonic()>deadline:raise AssertionError(state)
   time.sleep(.25)
  assert state['url']=='https://ksu.codes/hidden/' and state['secure'] and state['desktops']==1 and state['title']=='CodiServer'
  logs=driver('/session/'+session+'/log',{'type':'browser'});errors=[entry for entry in logs if entry['level']=='SEVERE'];assert not errors,errors
  image=base64.b64decode(driver('/session/'+session+'/screenshot'));target=CHECKS/('hidden-entry-'+('redirect' if suffix=='hidden' else 'slash')+'.png');target.write_bytes(image)
  witnesses.append({'entered':'https://ksu.codes/'+suffix,**{k:v for k,v in state.items() if k!='text'},'browserErrors':errors,'screenshot':str(target),'screenshotSHA256':hashlib.sha256(image).hexdigest()})
 finally:driver('/session/'+session,method='DELETE')
report={'status':'PASS','scope':'Fresh public Chrome entry through both URL forms, default trust and real Linux readiness; development network, not independent WAN proof','entries':entries,'witnesses':witnesses,'checkerSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(CHECKS/'public-hidden-entry-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
