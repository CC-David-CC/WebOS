"""Run the actual delta scan in a disposable Chromium target via local CDP."""
import json
from pathlib import Path
import urllib.request
from websockets.sync.client import connect

source=(Path(__file__).resolve().parents[1]/'active-system/gateway_service/client.mjs').read_text()
implementation=source[source.index('const DELTA_BLOCK='):source.index('export class UserFiles')]
script='''(async()=>{const requireThat=(ok,msg)=>{if(!ok)throw Error(msg)},MAX_FILE=128*1024*1024;\n'''+implementation+'''
 const input=new Uint8Array(128*1024*1024),signature={version:'codi-file-delta/1',block:65536,size:65536,chunks:[[0,'0'.repeat(64)]]};
 let ticks=0;const timer=setInterval(()=>ticks++,0);
 try {const result=await makeFileDelta(input,signature);let count=0,stopped=false;
 try{await makeFileDelta(input,signature,()=>{if(++count===3)throw Error('session ended')})}catch(e){stopped=e.message==='session ended'}
 return {ticks,fallBack:result===null,stopped,count};}finally{clearInterval(timer)}
})()'''
with urllib.request.urlopen('http://127.0.0.1:19255/json/version',timeout=5) as response: ws=json.load(response)['webSocketDebuggerUrl']
with connect(ws,open_timeout=5,close_timeout=5,max_size=2**20) as conn:
 index=0
 def call(method,params=None,session=None):
  global index
  index+=1;message={'id':index,'method':method,'params':params or {}}
  if session:message['sessionId']=session
  conn.send(json.dumps(message))
  while True:
   result=json.loads(conn.recv(timeout=120))
   if result.get('id')==index:
    if 'error' in result:raise RuntimeError(result['error'])
    return result['result']
 target=call('Target.createTarget',{'url':'about:blank'})['targetId']
 try:
  session=call('Target.attachToTarget',{'targetId':target,'flatten':True})['sessionId']
  result=call('Runtime.evaluate',{'expression':script,'awaitPromise':True,'returnByValue':True},session)
  if 'exceptionDetails' in result:raise RuntimeError(result['exceptionDetails'])
  value=result['result']['value']
  assert value['fallBack'] and value['stopped'] and value['count']==3 and value['ticks']>=5,value
  print('PASS Chromium 128 MiB unrelated file, responsive ticks and session cancellation:',value)
 finally:call('Target.closeTarget',{'targetId':target})
