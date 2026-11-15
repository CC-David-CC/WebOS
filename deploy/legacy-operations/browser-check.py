#!/usr/bin/env python3
"""Check the real browser via a loopback Chromium DevTools endpoint; stdlib only."""
import argparse,base64,hashlib,json,os,socket,struct,time,urllib.parse,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=9223);p.add_argument('--output',type=Path,default=Path('/tmp/desktop-lab-check.png'));p.add_argument('--close-browser',action='store_true');a=p.parse_args()
root='http://127.0.0.1:'+str(a.port)
target=next(t for t in json.load(urllib.request.urlopen(root+'/json')) if t['type']=='page' and ':8097/' in t['url'])
url=urllib.parse.urlsplit(target['webSocketDebuggerUrl']);s=socket.create_connection(('127.0.0.1',a.port),timeout=15);s.settimeout(20)
key=base64.b64encode(os.urandom(16)).decode();s.sendall(('GET '+url.path+' HTTP/1.1\r\nHost: 127.0.0.1:'+str(a.port)+'\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: '+key+'\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
header=b''
while not header.endswith(b'\r\n\r\n'):header+=s.recv(1)
assert header.startswith(b'HTTP/1.1 101 ') and base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()) in header
counter=0;errors=[]
def read(n):
 data=b''
 while len(data)<n:
  chunk=s.recv(n-len(data))
  if not chunk:raise EOFError('DevTools websocket closed')
  data+=chunk
 return data
def send(value):
 data=json.dumps(value).encode();mask=os.urandom(4);n=len(data)
 header=bytes([0x81,0x80|n]) if n<126 else bytes([0x81,0xfe])+struct.pack('!H',n) if n<65536 else bytes([0x81,0xff])+struct.pack('!Q',n)
 s.sendall(header+mask+bytes(v^mask[i%4] for i,v in enumerate(data)))
def receive():
 payload=b''
 while True:
  first,second=read(2);n=second&127
  if n==126:n=struct.unpack('!H',read(2))[0]
  if n==127:n=struct.unpack('!Q',read(8))[0]
  mask=read(4) if second&128 else None;chunk=read(n)
  if mask:chunk=bytes(v^mask[i%4] for i,v in enumerate(chunk))
  if first&15==8:raise EOFError('Websocket close')
  payload+=chunk
  if first&128:return json.loads(payload)
def call(method,params=None):
 global counter
 counter+=1;send({'id':counter,'method':method,'params':params or {}})
 while True:
  value=receive()
  if value.get('method')=='Runtime.exceptionThrown':errors.append(value['params'])
  if value.get('id')==counter:
   if 'error' in value:raise RuntimeError(value['error'])
   return value['result']
def js(code):
 result=call('Runtime.evaluate',{'expression':code,'returnByValue':True,'awaitPromise':True})
 if 'exceptionDetails' in result:raise AssertionError(result['exceptionDetails'])
 return result.get('result',{}).get('value')
def check(name,code):
 assert js(code),name
 print('PASS',name,flush=True)
call('Runtime.enable');call('Page.enable');call('Page.bringToFront');call('Page.reload',{'ignoreCache':True});time.sleep(1)
check('Loaded interactive desktop',"!!window.desktopLab && document.querySelectorAll('.desktop').length===1")
js("document.querySelector('[data-preset=selected]').click()")
check('User-selected layout is preserved',"window.desktopLab.settings.panelHeight===48 && window.desktopLab.settings.iconSize===31 && window.desktopLab.settings.workspaceWidth===82 && window.desktopLab.settings.titleHeight===44 && window.desktopLab.settings.controlWidth===96")
check('Applications and username are bold',"getComputedStyle(document.querySelector('.app-menu-button')).fontWeight==='700' && getComputedStyle(document.querySelector('.account')).fontWeight==='700'")
check('Legacy preset retains its logo size',"window.desktopLab.validateSettings({titleHeight:44}).titleIconSize===24")
original_height=js("document.querySelector('.window.focused').offsetHeight")
js("document.querySelector('.window.focused [aria-label=\"Roll up\"]').click()")
check('Rolled-up window has no 150px minimum',"document.querySelector('.window.rolled').offsetHeight===56 && getComputedStyle(document.querySelector('.window.rolled .resize-handle')).display==='none'")
js("document.querySelector('.window.rolled [aria-label=Unroll]').click()")
assert js("document.querySelector('.window.focused').offsetHeight")==original_height,'Unroll did not restore height'
print('PASS Unroll restores full window height',flush=True)
js("document.querySelector('[data-preset=shipped]').click();document.querySelector('.app-menu-button').click()")
check('Real menu layout and nesting',"document.querySelectorAll('.menu-pane .menu-row')[1].textContent==='File Manager' && window.desktopLab.reference.menu.some(e=>e.name==='Office'&&e.children.length>0)")
js("[...document.querySelectorAll('.menu-row')].find(b=>b.textContent.includes('Office')).click()")
check('Touch/click opens submenu',"document.querySelectorAll('.menu-pane').length===2")
js("document.querySelectorAll('.menu-pane')[1].querySelector('.menu-row').click()")
check('Menu launches mock app window',"[...window.desktopLab.surfaces.values()][0].windows.length===5")
js("document.querySelector('[data-preset=touch]').click()")
check('Touch preset updates actual hitboxes',"window.desktopLab.settings.panelHeight===56 && getComputedStyle(document.querySelector('.panel')).height==='56px' && getComputedStyle(document.querySelector('.workspace-button')).width==='100px'")
check('Control symbols grow independently of logo/title',"window.desktopLab.settings.titleIconSize===66 && window.desktopLab.settings.titleHeight===86 && getComputedStyle(document.querySelector('.window-controls svg')).width==='36px' && getComputedStyle(document.querySelector('.window-caption>.icon')).width==='66px'")
js("document.querySelector('.workspace-button:nth-child(2)').click()")
check('Workspace switches its windows',"[...window.desktopLab.surfaces.values()][0].current===1 && document.querySelectorAll('.window').length===1")
js("document.querySelector('.workspace-button:nth-child(1)').click();document.querySelector('.task[data-app=terminal]').click()")
check('Grouped terminal picker',"document.querySelectorAll('.task-popup .task-preview').length===2")
js("document.querySelector('.task-popup button').click();document.querySelector('.window.focused [aria-label=Minimize]').click()")
check('Minimize works',"[...window.desktopLab.surfaces.values()][0].windows.filter(w=>w.minimized).length===1")
js("document.querySelector('.task[data-app=terminal]').click();document.querySelector('.task-popup button').click();document.querySelector('.window.focused [aria-label=Maximize]').click()")
check('Maximize works',"[...window.desktopLab.surfaces.values()][0].windows.some(w=>w.w===1920&&w.h===1024)")
js("document.querySelector('.window.focused [aria-label=Maximize]').click();document.querySelector('.app-menu-button').click();const r=document.querySelector('#range-panelHeight');r.value=60;r.dispatchEvent(new Event('input',{bubbles:true}));")
check('Sizing preserves open menu and window state',"!!document.querySelector('.menu-pane') && [...window.desktopLab.surfaces.values()][0].windows.length===5 && window.desktopLab.settings.panelHeight===60")
js("document.querySelector('[data-view=compare]').click()")
check('Comparison retains shipped 34px panel',"document.querySelectorAll('.desktop').length===2 && getComputedStyle(document.querySelectorAll('.panel')[0]).height==='34px' && getComputedStyle(document.querySelectorAll('.panel')[1]).height==='60px'")
check('Preset validation rejects invalid data',"(()=>{try{window.desktopLab.validateSettings({panelHeight:'huge'});return false}catch(e){return true}})()")
call('Page.reload',{'ignoreCache':True});time.sleep(.5)
check('Preset survives reload',"window.desktopLab.settings.panelHeight===60")
js("document.querySelector('[data-preset=touch]').click()")
start=js("(()=>{const d=[...window.desktopLab.surfaces.values()][0],w=d.windows.find(w=>w.id===d.active),r=document.querySelector('.window.focused .window-caption').getBoundingClientRect();return {x:r.left+90,y:r.top+r.height/2,wx:w.x}})()")
call('Input.dispatchMouseEvent',{'type':'mouseMoved','x':start['x'],'y':start['y']})
call('Input.dispatchMouseEvent',{'type':'mousePressed','x':start['x'],'y':start['y'],'button':'left','clickCount':1})
call('Input.dispatchMouseEvent',{'type':'mouseMoved','x':start['x']+35,'y':start['y']+15,'button':'left','buttons':1})
call('Input.dispatchMouseEvent',{'type':'mouseReleased','x':start['x']+35,'y':start['y']+15,'button':'left','clickCount':1})
moved=js("(()=>{const d=[...window.desktopLab.surfaces.values()][0];return {active:d.active,positions:d.windows.map(w=>({id:w.id,x:w.x,y:w.y}))}})()");None
assert next(w['x'] for w in moved['positions'] if w['id']==moved['active'])!=start['wx'],'Dragging did not move the window'
print('PASS Real pointer drag moves window',flush=True)
point=js("(()=>{const r=document.querySelector('.workspace-button:nth-child(2)').getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2}})()")
call('Emulation.setTouchEmulationEnabled',{'enabled':True,'maxTouchPoints':5})
call('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[point]})
call('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});time.sleep(.1)
check('Real touch event switches workspace',"[...window.desktopLab.surfaces.values()][0].current===1")
call('Emulation.setTouchEmulationEnabled',{'enabled':False})
js("document.querySelector('.workspace-button:nth-child(1)').click();document.querySelector('.app-menu-button').click()")
call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False});time.sleep(.3)
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(base64.b64decode(call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True});time.sleep(.3)
check('Phone layout stays within viewport',"document.documentElement.scrollWidth<=innerWidth+1")
call('Emulation.clearDeviceMetricsOverride');js("document.querySelector('[data-preset=shipped]').click()")
assert not errors,errors
print('DESKTOP_LAB_BROWSER_CHECKS_OK; uncaught JavaScript errors:',len(errors))
if a.close_browser:
 try:call('Browser.close')
 except EOFError:pass
s.close()
