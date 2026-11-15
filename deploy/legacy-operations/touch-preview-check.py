#!/usr/bin/env python3
"""Fresh Chrome touch/desktop checks with real v86; no existing tab is touched."""
import argparse,base64,hashlib,http.client,json,socket,ssl,subprocess,sys,time,urllib.request,urllib.error
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks';DRIVER='http://127.0.0.1:19515'
def call(path,data=None,method=None):
 request=urllib.request.Request(DRIVER+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 try:
  with urllib.request.urlopen(request,timeout=120) as response:return json.load(response)['value']
 except urllib.error.HTTPError as error:raise RuntimeError(error.read().decode()) from error
def wait(fn,seconds=90):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  value=fn()
  if value:return value
  time.sleep(.15)
 raise AssertionError('Readiness timeout')
def run(url,fixture_spki=None):
 witnesses=[]
 for mobile in [True,False]:
  chrome_args=['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1366,900']
  if fixture_spki:chrome_args.append('--ignore-certificate-errors-spki-list='+fixture_spki)
  session=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':chrome_args},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
  def js(code):return call('/session/'+session+'/execute/sync',{'script':code,'args':[]})
  def cdp(cmd,params):return call('/session/'+session+'/goog/cdp/execute',{'cmd':cmd,'params':params})
  def size(width,height):
   cdp('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':mobile});time.sleep(.25)
  def touch(selector):
   rect=js('const r=document.querySelector('+json.dumps(selector)+').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};')
   cdp('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[rect]});time.sleep(.08);cdp('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});time.sleep(.2)
  def type_text(text):cdp('Input.insertText',{'text':text})
  def key(name,code):
   for event in ['keyDown','keyUp']:cdp('Input.dispatchKeyEvent',{'type':event,'key':name,'code':name,'windowsVirtualKeyCode':code})
  def screenshot(name):
   raw=base64.b64decode(call('/session/'+session+'/screenshot'));file=CHECKS/name;file.write_bytes(raw);return str(file)
  try:
   if mobile:
    size(390,844);cdp('Emulation.setTouchEmulationEnabled',{'enabled':True,'maxTouchPoints':5})
   call('/session/'+session+'/url',{'url':url});wait(lambda:js('return window.desktopLab?.guestState==="ready"'))
   assert not js('return [...document.querySelectorAll(".panel button")].some(n=>/batter|Guest session status/i.test(n.ariaLabel||n.textContent))')
   if mobile:
    assert js('return document.querySelector(".desktop").classList.contains("compact-desktop")')
    assert js('return [...document.querySelectorAll(".terminal-touchkeys button")].map(n=>n.ariaLabel).join("|")==="Show terminal keyboard|Ctrl+C|Tab|Esc|Enter"&&!document.querySelector(".terminal-menu [aria-label=Help]")')
    touch('.panel [aria-label="Workspaces"]')
    assert js('return document.querySelectorAll(".workspace-choice").length===3&&[...document.querySelectorAll(".workspace-choice")].every(n=>n.getBoundingClientRect().width>=44&&n.getBoundingClientRect().height>=44)&&!document.querySelector(".status-popup").textContent.includes("Browser:")')
    assert js('return !document.querySelector(".status-popup [aria-label=Close]")')
    touch('.popup-backdrop');assert js('return !document.querySelector(".status-popup")&&[...desktopLab.surfaces.values()][0].current===0')
    touch('.panel [aria-label="Workspaces"]');touch('.panel [aria-label="Workspaces"]');assert js('return !document.querySelector(".status-popup")')
    touch('.panel [aria-label="Workspaces"]')
    screenshot('touch-workspaces.png')
    touch('.workspace-choice[aria-label="Workspace 2"]')
    assert js('return [...desktopLab.surfaces.values()][0].current===1&&!document.querySelector(".status-popup")&&document.querySelector(".workspace-current").textContent==="2"&&!document.querySelector(".window:not([hidden])")&&!document.querySelector(".tasks .task")')
    touch('.panel [aria-label="Workspaces"]')
    assert js('return document.querySelector(".workspace-choice[aria-pressed=true]").ariaLabel==="Workspace 2"')
    touch('.workspace-choice[aria-label="Workspace 1"]')
    assert js('return [...desktopLab.surfaces.values()][0].current===0&&!!document.querySelector(".real-terminal")')
    touch('[aria-label="Show terminal keyboard"]');assert js('return document.activeElement.matches(".terminal-input")')
    type_text('echo PHONE_INPUT_OK');touch('.terminal-touchkeys [aria-label=Enter]')
    wait(lambda:js('return /(?:^|\\n)PHONE_INPUT_OK(?:\\n|$)/.test(serialScreen.text())'))
    assert js('const output=document.querySelector(".real-terminal").getBoundingClientRect(),tools=document.querySelector(".terminal-menu").getBoundingClientRect(),keys=document.querySelector(".terminal-touchkeys").getBoundingClientRect();return tools.top>=output.bottom-1&&keys.top>=tools.bottom-1')
    for width in [320,360,390]:
     size(width,844)
     assert js('const keys=[...document.querySelectorAll(".window.focused .terminal-touchkeys button")];return keys.length===5&&keys.every(n=>{const r=n.getBoundingClientRect();return r.width>=44&&r.height>=44&&r.left>=0&&r.right<=innerWidth})')
    js('window.__native=document.querySelector(".terminal-input")');size(390,420)
    wait(lambda:js('const t=document.querySelector(".real-terminal");return t.scrollHeight-t.scrollTop-t.clientHeight<3'))
    type_text('echo KEYBOARD_VISIBLE_OK');key('Enter',13);wait(lambda:js('return /(?:^|\\n)KEYBOARD_VISIBLE_OK(?:\\n|$)/.test(serialScreen.text())'))
    assert js('const t=document.querySelector(".real-terminal");return document.activeElement===__native&&t.scrollHeight-t.scrollTop-t.clientHeight<3')
    size(390,844);js('appendSerial("\\r\\n"+Array.from({length:60},(_,i)=>"scroll line "+i).join("\\r\\n")+"\\r\\n")');time.sleep(.1)
    js('const t=document.querySelector(".real-terminal");t.dispatchEvent(new WheelEvent("wheel",{deltaY:-100,bubbles:true}));t.scrollTop=0;');time.sleep(.1)
    js('appendSerial("scrollback stays put\\r\\n")');time.sleep(.1);assert js('return document.querySelector(".real-terminal").scrollTop<5')
    touch('[aria-label="Show terminal keyboard"]');assert js('const t=document.querySelector(".real-terminal");return t.scrollHeight-t.scrollTop-t.clientHeight<3')
    # Test both composition event orders and native delete/line-break handling.
    js('window.__raw=[];window.__send=sendTerminal;sendTerminal=(id,t)=>__raw.push(t);')
    for final_after_end in [False,True]:
     code='''const f=document.querySelector('.terminal-input');f.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true}));f.value='\u200bime';f.dispatchEvent(new InputEvent('input',{inputType:'insertCompositionText',data:'ime',isComposing:true,bubbles:true}));f.dispatchEvent(new CompositionEvent('compositionend',{data:'ime',bubbles:true}));'''
     if final_after_end:code+="f.dispatchEvent(new InputEvent('input',{inputType:'insertText',data:'ime',bubbles:true}));"
     js(code);time.sleep(.05)
    js("const f=document.querySelector('.terminal-input');for(const inputType of ['deleteContentBackward','insertLineBreak'])f.dispatchEvent(new InputEvent('beforeinput',{inputType,bubbles:true,cancelable:true}));")
    assert js('return __raw')==['ime','ime','\x7f','\r'];js('sendTerminal=__send;delete __send;delete __raw;')
    touch('[aria-label="Ctrl+C"]')
    # Pointer capture must keep the native field/DOM alive after a real drag.
    before=js('window.__field=document.querySelector(".terminal-input");const d=[...desktopLab.surfaces.values()][0],w=d.windows.find(w=>w.id===d.active),r=document.querySelector(".window.focused .caption-text").getBoundingClientRect();return {y:w.y,x:r.x+10,cy:r.y+r.height/2};')
    cdp('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':before['x'],'y':before['cy']}]})
    # Give the gesture human timing; a single zero-duration 40px move creates
    # compositor fling/tap suppression even in a minimal unrelated HTML page.
    for step in range(1,9):
     time.sleep(.05);cdp('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':before['x'],'y':before['cy']+step*5}]})
    time.sleep(.15);cdp('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':before['x'],'y':before['cy']+40}]})
    cdp('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    time.sleep(.3)
    assert js('const d=[...desktopLab.surfaces.values()][0];return d.windows.find(w=>w.id===d.active).y')>before['y']+20
    assert js('return __field===document.querySelector(".terminal-input")');screenshot('touch-terminal.png')
    js('window.__events=[];for(const t of ["pointerdown","pointerup","click"])document.addEventListener(t,e=>__events.push([t,e.target.className,e.clientX,e.clientY]),true)')
    touch('[aria-label="Applications"]')
    wait(lambda:js('return !!document.querySelector(".menu-pane")'),2)
    assert js('const r=document.querySelector(".menu-pane").getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.bottom<=visualViewport.height+1')
    assert js('return [...document.querySelectorAll(".menu-row")].every(n=>n.getBoundingClientRect().height>=44)')
    screenshot('touch-menu.png')
    assert js('return !document.querySelector(".menu-row[aria-label=Workspaces]")')
    touch('.menu-row[aria-label="Text Editor"]')
    wait(lambda:js('return !!document.querySelector(".guest-editor")'),20)
    js('document.querySelector(".guest-editor").focus()');type_text('Phone draft survives viewport changes.')
    for width,height in [(360,740),(320,640),(428,926),(390,420),(844,390),(390,844)]:
     old=js('window.__editor=document.querySelector(".guest-editor");return __editor.value')
     size(width,height)
     assert js('const r=document.querySelector(".panel [aria-label=Workspaces]").getBoundingClientRect();return r.width>=44&&r.height>=44&&r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=48')
     assert js('return [...document.querySelectorAll(".terminal-touchkeys button")].filter(n=>n.getBoundingClientRect().width).every(n=>{const r=n.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.width>=44&&r.height>=44})')
     assert js('return document.activeElement===__editor&&__editor===document.querySelector(".guest-editor")&&__editor.value')==old
     layout=js('const r=document.querySelector(".window.focused").getBoundingClientRect(),p=document.querySelector(".panel").getBoundingClientRect();return {width:innerWidth,height:visualViewport.height,left:r.left,right:r.right,top:r.top,bottom:r.bottom,panelRight:p.right,visible:[...document.querySelectorAll(".window")].filter(n=>!n.hidden).length};')
     assert layout['left']>=0 and layout['right']<=width+1 and layout['top']>=47 and layout['bottom']<=height+1 and layout['visible']==3,layout
    screenshot('touch-editor.png')
    touch('.panel .account');assert js('const r=document.querySelector(".status-popup").getBoundingClientRect();return r.right<=innerWidth&&r.left>=0&&r.bottom<=visualViewport.height+1')
    assert js('const p=document.querySelector(".status-popup");return p.textContent.includes("Browser:")&&p.querySelector("[aria-label=\\"End session\\"]")&&p.querySelector("[aria-label=Close]")&&!p.querySelector(".workspace-choice")')
    screenshot('touch-session-network.png')
    touch('.status-popup [aria-label=Close]')
    js('feedback("First status")');time.sleep(2);js('feedback("Latest status")');time.sleep(2.2);assert js('return document.querySelector("#feedback").textContent')=='Latest status';wait(lambda:js('return document.querySelector("#feedback").textContent===""'),3)
    witnesses.append({'mode':'touch emulation','topBarWorkspaceIconAndChooserSwitchable':True,'networkInfoInSessionMenu':True,'workspacePopupDismissesOnSelectionOutsideAndIconWithoutCloseButton':True,'globalVoiceAndTerminalEnterReplaceArrowsAndHelp':True,'nativeTerminalFieldFocused':True,'realGuestCommand':True,'compositionAndDeleteForwarding':True,'allTerminalCommandsAtBottom':True,'terminalPromptVisibleInKeyboardSizedViewport':True,'manualScrollbackPreservedAndTypingResumesFollow':True,'dragPreservesInputDom':True,'menuContainedAndTargets44px':True,'singlePaneSubmenus':True,'editorAndFocusSurviveKeyboardSizedViewportAndRotation':True,'statusAutoDismissesAndNewMessageResetsTimer':True,'phoneWidths':[320,360,390,428,844],'actualPhoneOsKeyboardVerified':False})
   else:
    assert js('return !document.querySelector(".desktop").classList.contains("compact-desktop")&&getComputedStyle(document.querySelector(".window-caption")).height==="86px"')
    js('document.querySelector(".panel [aria-label=Workspaces]").click()');assert js('return document.querySelectorAll(".workspace-choice").length===3&&!document.querySelector(".status-popup").textContent.includes("Browser:")')
    js('document.querySelector(".workspace-toggle").click();document.querySelector(".panel .account").click()');assert js('return document.querySelector(".status-popup").textContent.includes("Browser:")')
    js('document.querySelector(".status-popup [aria-label=Close]").click()')
    js('document.querySelector(".real-terminal").focus()');key('Enter',13)
    # Physical keyboard events retain the original serial path.
    for char in 'echo DESKTOP_INPUT_OK':
     cdp('Input.dispatchKeyEvent',{'type':'keyDown','key':char,'text':char});cdp('Input.dispatchKeyEvent',{'type':'keyUp','key':char})
    key('Enter',13);wait(lambda:js('return /(?:^|\\n)DESKTOP_INPUT_OK(?:\\n|$)/.test(serialScreen.text())'))
    drag=js('const d=[...desktopLab.surfaces.values()][0],w=d.windows.find(w=>w.app==="files"),r=document.querySelector(`[data-window="${w.id}"] .caption-text`).getBoundingClientRect();window.__files=document.querySelector(`[data-window="${w.id}"]`);return {id:w.id,x:r.right-8,y:r.y+r.height/2,oldY:w.y};')
    cdp('Input.dispatchMouseEvent',{'type':'mousePressed','x':drag['x'],'y':drag['y'],'button':'left','clickCount':1})
    cdp('Input.dispatchMouseEvent',{'type':'mouseMoved','x':drag['x']+20,'y':drag['y']+30,'button':'left','buttons':1})
    cdp('Input.dispatchMouseEvent',{'type':'mouseReleased','x':drag['x']+20,'y':drag['y']+30,'button':'left','clickCount':1})
    assert js('return __files===document.querySelector(".window.focused")')
    assert js('return [...desktopLab.surfaces.values()][0].windows.find(w=>w.app==="files").y')>drag['oldY']
    js('document.querySelector(".window.focused [aria-label=Maximize]").click()');assert js('const w=[...desktopLab.surfaces.values()][0].windows.find(w=>w.app==="files");return w.x===0&&w.w===document.querySelector(".viewport").clientWidth')
    js('document.querySelector(".window.focused [aria-label=Maximize]").click()')
    screenshot('touch-desktop-regression.png');witnesses.append({'mode':'desktop mouse/keyboard','titleHeightUnchanged':86,'realGuestKeyboardCommand':True,'mouseDragAndFocusPreserveDom':True,'maximizeAndRestore':True,'batteryMenuRemoved':True})
   errors=[entry for entry in call('/session/'+session+'/log',{'type':'browser'}) if entry['level']=='SEVERE'];assert not errors,errors
  finally:call('/session/'+session,method='DELETE')
 return witnesses

def ready(url):
 try:
  with urllib.request.urlopen(url+'config.json',timeout=.5) as response:return response.status==200
 except OSError:return False

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--url');p.add_argument('--fixture-spki-file',type=Path);p.add_argument('--fixture-ca-file',type=Path);a=p.parse_args();server=None
 if bool(a.fixture_spki_file)!=bool(a.fixture_ca_file):p.error('Fixture CA and SPKI must be paired')
 if a.fixture_spki_file and (not a.url or urlsplit(a.url).scheme!='https' or urlsplit(a.url).hostname!='127.0.0.1'):p.error('Certificate exceptions require an owned loopback fixture')
 try:
  url=a.url
  if not url:
   with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
   server=subprocess.Popen([sys.executable,'-B',ROOT/'serve.py','--port',str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   url='http://127.0.0.1:'+str(port)+'/'
   wait(lambda:server.poll() is None and ready(url),5)
  served={}
  context=ssl.create_default_context(cafile=str(a.fixture_ca_file)) if a.fixture_ca_file else ssl.create_default_context()
  for name in ['app.js','style.css','terminal.js','assets/terminal-initramfs.cpio.gz']:
   with urllib.request.urlopen(url+name,timeout=15,context=context) as response:served[name]=hashlib.sha256(response.read()).hexdigest()
   assert served[name]==hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
  with urllib.request.urlopen(url,timeout=15,context=context) as response:bootstrap=hashlib.sha256(response.read()).hexdigest()
  witnesses=run(url,a.fixture_spki_file.read_text().strip() if a.fixture_spki_file else None);report={'status':'PASS','url':url,'scope':'Chrome touch emulation and real v86, plus desktop keyboard regression; actual phone keyboard appearance still needs device feedback','fixtureCertificatePinUsed':bool(a.fixture_spki_file),'witnesses':witnesses,'servedAssetsSHA256':served,'bootstrapHTMLSHA256':bootstrap,'sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['app.js','style.css','terminal.js','assets/terminal-initramfs.cpio.gz','scripts/touch-preview-check.py']}}
  output=CHECKS/('touch-fixture-result.json' if a.fixture_spki_file else 'touch-public-result.json' if a.url else 'touch-preview-result.json')
  if output.exists():output.rename(output.with_name(output.stem+'-before-'+str(time.time_ns())+'.json'))
  output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 finally:
  if server is not None:server.terminate();server.wait(5)

