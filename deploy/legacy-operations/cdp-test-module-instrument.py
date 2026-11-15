"""Expose selected classes only in a test browser's intercepted module response."""
import base64, json, threading, urllib.request
from websockets.sync.client import connect

class ModuleInstrument:
 def __init__(self, address, target_id=None):
  with urllib.request.urlopen('http://'+address+'/json/list',timeout=10) as f: tabs=json.load(f)
  tab=next(t for t in tabs if t.get('type')=='page' and (target_id is None or t.get('id')==target_id))
  ws=tab['webSocketDebuggerUrl'];ws='ws://'+address+'/'+ws.split('/',3)[3]
  self.ws=connect(ws,origin='http://localhost',open_timeout=10,max_size=8*1024*1024)
  self.lock=threading.Lock();self.pending={};self.counter=0;self.error=None;self.changed=0
  self.thread=threading.Thread(target=self._reader,daemon=True);self.thread.start()
  self.command('Network.enable');self.command('Network.setCacheDisabled',{'cacheDisabled':True});self.command('Network.setBypassServiceWorker',{'bypass':True})
  self.command('Fetch.enable',{'patterns':[{'urlPattern':'*services/device-history/*/index.mjs','requestStage':'Response'}]})
 def command(self,method,params=None):
  event=threading.Event();item={'event':event}
  with self.lock:
   self.counter+=1;key=self.counter;self.pending[key]=item
   self.ws.send(json.dumps({'id':key,'method':method,'params':params or {}}))
  if not event.wait(20):
   with self.lock:self.pending.pop(key,None)
   raise TimeoutError('CDP command timed out: '+method)
  if 'error' in item['reply']:raise RuntimeError(str(item['reply']['error']))
  return item['reply'].get('result',{})
 def _reader(self):
  try:
   for raw in self.ws:
    msg=json.loads(raw)
    if 'id' in msg:
     with self.lock:item=self.pending.pop(msg['id'],None)
     if item:item['reply']=msg;item['event'].set()
    elif msg.get('method')=='Fetch.requestPaused':threading.Thread(target=self._intercept,args=(msg['params'],),daemon=True).start()
  except Exception as e:self.error=str(e)
 def _intercept(self,event):
  rid=event['requestId']
  try:
   if event.get('responseStatusCode')!=200:
    self.command('Fetch.continueRequest',{'requestId':rid});return
   result=self.command('Fetch.getResponseBody',{'requestId':rid});body=base64.b64decode(result['body']) if result.get('base64Encoded') else result['body'].encode()
   suffix=b'\nexport {DeviceChannelArchive as __TraceArchive, DeviceMemberChannel as __TraceMember, DeviceMemberIntroductions as __TraceTopology, DeviceChannelTransfer as __TraceTransfer, DeviceReplicaScheduler as __TraceScheduler};\n'
   headers=[h for h in event.get('responseHeaders',[]) if h['name'].lower() not in ('content-length','content-encoding','transfer-encoding')]
   self.command('Fetch.fulfillRequest',{'requestId':rid,'responseCode':200,'responseHeaders':headers,'body':base64.b64encode(body+suffix).decode()});self.changed+=1
  except Exception as e:
   self.error=str(e)
   try:self.command('Fetch.continueRequest',{'requestId':rid})
   except Exception:pass
 def close(self):
  try:self.command('Fetch.disable')
  finally:self.ws.close();self.thread.join(timeout=5)
