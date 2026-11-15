#!/usr/bin/env python3
"""Real xterm/v86: independent shells, PTY sizing, nano, flow control and view disposal."""
import asyncio,hashlib,importlib.util,json,re,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('xterm_browser_fixture',ROOT/'scripts/guest-client-browser-check.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.PAGE=(ROOT/'index.html').read_bytes();call,wait=f.call,f.wait

def browser(fixture):
 sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','unhandledPromptBehavior':'accept','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1366,1000']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];checks=[];probes=[]
 def js(code,args=[]):return call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  d=call('/session/'+sid+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+code+'})().then(v=>done({ok:true,value:v}),e=>done({ok:false,error:e.stack}));','args':args});assert d['ok'],d;return d.get('value')
 def check(label,value):assert value,label;checks.append(label)
 def mounted(id):wait(lambda:js('return !!document.querySelector("[data-window=\\\""+arguments[0]+"\\\"] .xterm-terminal")?.terminal',[id]),20)
 def screen(id):return js('return terminalSessions.get(arguments[0]).screen.text()',[id])
 def command(id,shell,expected=None):
  wait(lambda:js('return guestState==="ready"&&!desktopLifecycle?.state.blocked'),30)
  token='XT_'+str(time.time_ns());send='printf "\\n'+token+'_BEGIN\\n"; '+shell+'; printf "\\n'+token+'_END\\n"\r'
  js('sendTerminal(arguments[0],arguments[1])',[id,send]);wait(lambda:'\n'+token+'_END' in screen(id),30)
  text=screen(id);start=text.rfind('\n'+token+'_BEGIN\n');end=text.rfind('\n'+token+'_END');value=text[start+len(token)+8:end]
  if expected is not None:assert expected in value,(shell,expected,value[-1200:])
  return value
 try:
  call('/session/'+sid+'/timeouts',{'script':120000});call('/session/'+sid+'/url',{'url':fixture.origin+fixture.base+'/'})
  def ready():
   if js('return window.desktopLab?.guestState==="error"'):raise AssertionError(js('return guestMessage'))
   return js('return window.desktopLab?.guestState==="ready"&&guestFiles.ready&&!desktopLab.lifecycle?.blocked')
  wait(ready,150);mounted(2);js('window.d=[...surfaces.values()][0];window.keepVM=v86Instance;window.keepFS=v86Instance.fs9p;')
  check('actual terminal is xterm with native input and generic bundled CSS',js('return !!document.querySelector(".xterm-screen")&&!!document.querySelector(".xterm-helper-textarea.terminal-input")&&typeof SerialScreen==="undefined"'))
  command(2,'export XT_SCOPE=first; printf "TERM=%s SCOPE=%s\\n" "$TERM" "$XT_SCOPE"','TERM=xterm-256color SCOPE=first')
  second=js('return d.launch("terminal").id');mounted(second);command(second,'export XT_SCOPE=second; printf "SCOPE=%s\\n" "$XT_SCOPE"','SCOPE=second');command(2,'printf "SCOPE=%s\\n" "$XT_SCOPE"','SCOPE=first');check('two real PTYs preserve independent shell environments',True)
  for id in [2,second]:
   size=js('const t=document.querySelector("[data-window=\\\""+arguments[0]+"\\\"] .xterm-terminal").terminal;return [t.rows,t.cols];',[id]);value=command(id,'stty size');check('Linux PTY geometry equals xterm for window '+str(id),str(size[0])+' '+str(size[1]) in value);probes.append({'window':id,'initialSize':size})
  # An interactive ash line editor handles WINCH itself; probe an actual
  # foreground noninteractive program rather than relying on that editor's trap.
  js('sendTerminal(2,arguments[0])',["sh -c 'trap \"echo SIGNAL_DELIVERED\" WINCH; echo RESIZE_READY; read line'\r"])
  wait(lambda:re.search(r'(?:^|\n)RESIZE_READY(?:\n|$)',screen(2)),15)
  old=js('return [terminalSessions.get(2).rows,terminalSessions.get(2).cols]');js('const w=d.windows.find(w=>w.id===2);w.w=650;w.h=430;d.render();')
  wait(lambda:js('return JSON.stringify([terminalSessions.get(2).rows,terminalSessions.get(2).cols])!==arguments[0]',[json.dumps(old,separators=(',',':'))]),15)
  wait(lambda:re.search(r'(?:^|\n)SIGNAL_DELIVERED(?:\n|$)',screen(2)),15);check('kernel delivers SIGWINCH to foreground program',True)
  js('sendTerminal(2,"\\x03")')
  size=js('return [terminalSessions.get(2).rows,terminalSessions.get(2).cols]');check('resize changes actual PTY rows and columns',str(size[0])+' '+str(size[1]) in command(2,'stty size'))
  command(2,'printf "caf\\303\\251 \\317\\200\\n"','café π');check('UTF-8 output is decoded by xterm',True)
  # Native nano, not a browser editor or a simulated terminal screen.
  js('sendTerminal(2,"nano /home/guest/Documents/xterm-nano.txt\\r")');wait(lambda:'GNU nano' in screen(2),20)
  js('sendTerminal(2,"Actual nano in browser Linux.")');command(second,'printf "OTHER=%s\\n" "$XT_SCOPE"','OTHER=second');check('second interactive shell works while first runs nano',True)
  js('d.activateWindow(d.windows.find(w=>w.id===2))');
  import base64
  (ROOT/'.build/checks/xterm-nano.png').write_bytes(base64.b64decode(call('/session/'+sid+'/screenshot')))
  def terminal_button(label):
   buttons=call('/session/'+sid+'/elements',{'using':'css selector','value':'[data-window="2"] .terminal-touchkeys button'})
   for item in buttons:
    id=item['element-6066-11e4-a52e-4f735466cecf']
    if call('/session/'+sid+'/element/'+id+'/text')==label:call('/session/'+sid+'/element/'+id+'/click',{});return
   raise AssertionError('Missing terminal command: '+label)
  terminal_button('Ctrl+O');wait(lambda:'File Name to Write' in screen(2),15);terminal_button('Enter');wait(lambda:'Wrote' in screen(2),15);terminal_button('Ctrl+X');wait(lambda:screen(2).rstrip().endswith('~ $'),15);command(2,'cat Documents/xterm-nano.txt','Actual nano in browser Linux.')
  check('real nano edits saves and exits through the guest PTY and shared 9p',task('return new TextDecoder().decode(await guestFiles.read("/Documents/xterm-nano.txt")).includes("Actual nano in browser Linux.");'))
  # Alternate screen state and attributes belong to xterm itself.
  js('sendTerminal(2,"printf \'\\\\033[?1049h\\\\033[31mALT_BUFFER_RED\\\\033[0m\'\\r")');wait(lambda:js('return document.querySelector("[data-window=\\\"2\\\"] .xterm-terminal").terminal.buffer.active.type==="alternate"'),10)
  check('alternate screen and SGR are handled by xterm', 'ALT_BUFFER_RED' in screen(2));js('sendTerminal(2,"printf \'\\\\033[?1049l\'\\r")');wait(lambda:js('return document.querySelector("[data-window=\\\"2\\\"] .xterm-terminal").terminal.buffer.active.type==="normal"'),10)
  # Start a producer, detach the view, and let the credit window fill.
  js('sendTerminal(2,"seq 1 30000; printf \\\"\\\\nFLOW_FINISHED\\\\n\\\"\\r");const node=document.querySelector("[data-window=\\\"2\\\"]");disposePublicAppView(node);node.remove();')
  wait(lambda:js('return terminalSessions.get(2).pendingBytes===65536'),20);pending=js('return terminalSessions.get(2).pendingBytes');time.sleep(.5);check('full credit window remains stable while detached',js('return terminalSessions.get(2).pendingBytes===65536'));check('unmounted terminal output is bounded by the 64KiB guest credit window',pending<=65536)
  command(second,'printf "NOT_STARVED\\n"','NOT_STARVED');check('paused output in one PTY does not block another shell',True)
  js('d.render()');mounted(2);wait(lambda:'\nFLOW_FINISHED' in screen(2),60);check('reattached xterm restores state and drains producer without deadlock',True)
  check('same VM and shared filesystem survive view replacement',js('return v86Instance===keepVM&&v86Instance.fs9p===keepFS'))
  # Real keyboard path: xterm translates input; the shell receives it once.
  js('d.activateWindow(d.windows.find(w=>w.id===2));document.querySelector("[data-window=\\\"2\\\"] .xterm-terminal").terminal.focus();')
  element=call('/session/'+sid+'/element',{'using':'css selector','value':'[data-window="2"] .xterm-helper-textarea'})['element-6066-11e4-a52e-4f735466cecf'];call('/session/'+sid+'/element/'+element+'/value',{'text':'echo HARDWARE_XTERM\ue007'})
  wait(lambda:'\nHARDWARE_XTERM\n' in screen(2),15);check('real Chrome keyboard input reaches xterm and the shell',True)
  # Both viewport and keyboard hints use the existing desktop/voice policy.
  check('voice mode keeps native terminal textarea focusable without keyboard hint',js('const n=document.querySelector("[data-window=\\\"2\\\"] .xterm-helper-textarea");return n.inputMode==="none"&&!n.disabled&&!n.readOnly;'))
  js('setScreenKeyboardEnabled(true);');check('keyboard toggle restores native xterm input',js('return document.querySelector("[data-window=\\\"2\\\"] .xterm-helper-textarea").inputMode!=="none"'))
  js('setScreenKeyboardEnabled(false);insertTerminalText(2,"echo DICTATION_TEXT");sendTerminal(2,"\\r")');wait(lambda:'\nDICTATION_TEXT\n' in screen(2),15);check('dictation destination routes text through xterm paste semantics',True)
  js('window.disposedSurface=document.querySelector("[data-window=\\\""+arguments[0]+"\\\"] .xterm-terminal");window.closedView=disposedSurface.closest(".window").appView;disposedSurface.closest(".window").querySelector("[aria-label=Close]").click();',[second])
  check('Close disposes xterm view and only its logical PTY',js('return closedView.signal.aborted&&!disposedSurface.isConnected&&!terminalSessions.has(arguments[0])&&terminalSessions.has(2)',[second]))
  # Emulated phone viewport and trusted browser text/IME paths.
  call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Emulation.setDeviceMetricsOverride','params':{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True}})
  call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Emulation.setTouchEmulationEnabled','params':{'enabled':True,'maxTouchPoints':5}})
  js('d.activateWindow(d.windows.find(w=>w.id===2));')
  wait(lambda:js('return document.querySelector(".desktop-root")?.classList.contains("compact-desktop")||[...surfaces.values()][0].mobile'),15)
  wait(lambda:js('return terminalSessions.get(2).cols<60'),15)
  js('[...document.querySelectorAll(".window.focused .window-controls button")].find(b=>b.ariaLabel==="Maximize").click()');wait(lambda:js('return terminalSessions.get(2).rows>30'),15)
  check('phone terminal fits within its viewport',js('const r=document.querySelector(".window.focused .xterm-terminal").getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1;'))
  command(2,'seq 1 250; printf "SCROLL_%s\\n" READY','SCROLL_READY')
  wait(lambda:js('return document.querySelector(".window.focused .xterm-terminal").terminal.buffer.active.baseY>100'),15)
  def swipe(direction,cancel=False):
   rect=js('const r=document.querySelector(".window.focused .xterm-screen").getBoundingClientRect();return {x:r.left+r.width*.45,y:r.top+r.height*.5};')
   def touch(kind,y):call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Input.dispatchTouchEvent','params':{'type':kind,'touchPoints':[] if kind in ['touchEnd','touchCancel'] else [{'x':rect['x'],'y':y,'id':7}]}})
   touch('touchStart',rect['y'])
   for step in range(1,9):touch('touchMove',rect['y']+direction*step*14);time.sleep(.025)
   touch('touchCancel' if cancel else 'touchEnd',rect['y']+direction*112)
  at_bottom=js('return document.querySelector(".window.focused .xterm-terminal").terminal.buffer.active.viewportY')
  position=js('const w=d.windows.find(w=>w.id===2);return [w.x,w.y,w.w,w.h,document.scrollingElement.scrollTop];')
  swipe(1)
  wait(lambda:js('return document.querySelector(".window.focused .xterm-terminal").terminal.buffer.active.viewportY<arguments[0]',[at_bottom]),10)
  check('trusted phone swipe on terminal text reveals older xterm scrollback',True)
  older=js('return document.querySelector(".window.focused .xterm-terminal").terminal.buffer.active.viewportY')
  check('touch scrolling does not move the desktop window or page',position==js('const w=d.windows.find(w=>w.id===2);return [w.x,w.y,w.w,w.h,document.scrollingElement.scrollTop];'))
  check('touch scrollback pauses output following',js('return d.windows.find(w=>w.id===2).terminalFollow===false&&document.querySelector(".window.focused .xterm-terminal").dataset.followOutput==="false";'))
  visible_line=js('const b=document.querySelector(".window.focused .xterm-terminal").terminal.buffer.active;return b.getLine(b.viewportY).translateToString(true);')
  # Check the renderer's response to newly arriving output without a keyboard action.
  task('await new Promise(done=>document.querySelector(".window.focused .xterm-terminal").terminal.write("\\r\\nTOUCH_BACKGROUND_OUTPUT\\r\\n",done));return true;')
  # At the 2,000-line cap, trimmed rows change the numeric index; visible text
  # must stay anchored even when that index decreases.
  check('incoming xterm output preserves manually scrolled text',visible_line==js('const b=document.querySelector(".window.focused .xterm-terminal").terminal.buffer.active;return b.getLine(b.viewportY).translateToString(true);'))
  older=js('return document.querySelector(".window.focused .xterm-terminal").terminal.buffer.active.viewportY')
  swipe(-1)
  wait(lambda:js('return document.querySelector(".window.focused .xterm-terminal").terminal.buffer.active.viewportY>arguments[0]',[older]),10)
  check('trusted reverse swipe moves toward newer terminal output',True)
  check('swiping preserves voice-mode keyboard suppression',js('return document.querySelector(".window.focused .xterm-helper-textarea").inputMode==="none";'))
  swipe(1,cancel=True)
  cancelled_at=js('return document.querySelector(".window.focused .xterm-terminal").terminal.buffer.active.viewportY')
  swipe(-1)
  wait(lambda:js('return document.querySelector(".window.focused .xterm-terminal").terminal.buffer.active.viewportY>arguments[0]',[cancelled_at]),10)
  check('trusted touch cancellation releases the gesture for the next swipe',True)
  js('document.querySelector(".window.focused .xterm-terminal").followOutput()')
  wait(lambda:js('const b=document.querySelector(".window.focused .xterm-terminal").terminal.buffer.active;return b.viewportY===b.baseY;'),10)
  check('terminal resumes following after returning to the latest output',js('return d.windows.find(w=>w.id===2).terminalFollow===true'))
  check('terminal bar removes Keyboard and retains nano and shell commands',js('const labels=[...document.querySelectorAll("[data-window=\\\"2\\\"] .terminal-touchkeys button")].map(n=>n.textContent);return !document.querySelector("[data-window=\\\"2\\\"] [aria-label=\\\"Show terminal keyboard\\\"]")&&JSON.stringify(labels)===JSON.stringify(["Ctrl+C","Ctrl+O","Ctrl+X","Tab","Esc","Enter","Copy","Paste","Clear"]);'))
  check('phone terminal commands retain44pixel touch targets',js('return [...document.querySelectorAll("[data-window=\\\"2\\\"] .terminal-touchkeys button")].every(n=>{const r=n.getBoundingClientRect();return r.width>=44&&r.height>=44&&r.left>=0&&r.right<=innerWidth+1;});'))
  js('document.querySelector("[data-window=\\\"2\\\"] .xterm-terminal").terminal.focus();')
  keyboard=call('/session/'+sid+'/element',{'using':'css selector','value':'#voice-control [aria-label="Show on-screen keyboard"]'})['element-6066-11e4-a52e-4f735466cecf'];call('/session/'+sid+'/element/'+keyboard+'/click',{})
  check('floating Keyboard control focuses xterm native textarea',js('return document.activeElement.matches(".xterm-helper-textarea")&&document.activeElement.inputMode!=="none"'))
  call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Input.insertText','params':{'text':'echo PHONE_NATIVE_INPUT'}})
  for event in ['keyDown','keyUp']:call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Input.dispatchKeyEvent','params':{'type':event,'key':'Enter','code':'Enter','windowsVirtualKeyCode':13}})
  wait(lambda:'\nPHONE_NATIVE_INPUT\n' in screen(2),15);check('trusted browser text input reaches phone terminal once',True)
  call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Input.insertText','params':{'text':'echo '}})
  call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Input.imeSetComposition','params':{'text':'nihao','selectionStart':5,'selectionEnd':5}})
  call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Input.insertText','params':{'text':'你好'}})
  time.sleep(.1)
  for event in ['keyDown','keyUp']:call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Input.dispatchKeyEvent','params':{'type':event,'key':'Enter','code':'Enter','windowsVirtualKeyCode':13}})
  wait(lambda:'\n你好\n' in screen(2),15);check('trusted browser IME commits Unicode without submitting preedit text',True)
  before=js('return terminalSessions.get(2).rows')
  call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Emulation.setDeviceMetricsOverride','params':{'width':390,'height':470,'deviceScaleFactor':1,'mobile':True}})
  wait(lambda:js('return terminalSessions.get(2).rows<arguments[0]',[before]),15)
  size=js('return [terminalSessions.get(2).rows,terminalSessions.get(2).cols]');check('keyboard-sized viewport resizes the actual Linux PTY',str(size[0])+' '+str(size[1]) in command(2,'stty size'))
  check('typing area stays above keyboard-sized viewport edge',js('const r=document.querySelector(".window.focused .xterm-terminal").getBoundingClientRect();return r.bottom<=visualViewport.height+1;'))
  js('setScreenKeyboardEnabled(false)');check('voice mode suppresses keyboard hint after phone resize',js('return document.querySelector(".window.focused .xterm-helper-textarea").inputMode==="none"'))
  errors=[e for e in call('/session/'+sid+'/log',{'type':'browser'}) if e['level']=='SEVERE'];check('no unexpected browser errors',not errors)
  return {'status':'PASS','checks':checks,'geometryProbes':probes,'detachedPendingBytes':pending,'actualXterm':True,'actualNano':True,'liveChanged':False,'physicalAndroidTested':False}
 except Exception:
  try:(ROOT/'.build/checks/xterm-browser-diagnostics.json').write_text(json.dumps(js('return {state:window.desktopLab?.guestState,lifecycle:typeof desktopLifecycle!=="undefined"?desktopLifecycle.state:null,message:typeof guestMessage!=="undefined"?guestMessage:null,text:typeof serialScreen!=="undefined"?serialScreen.text().slice(-2500):null,body:document.body.innerText.slice(-1800)}'),indent=2)+'\n')
  except Exception:pass
  raise
 finally:
  try:task('desktopLifecycle?.stop();desktopNetwork.close();guestNetworkAdapter?.destroy();await v86Instance?.destroy();return true;')
  except Exception:pass
  call('/session/'+sid,method='DELETE')
async def main():
 fixture=f.Fixture('/hidden')
 try:await fixture.start();return await asyncio.to_thread(browser,fixture)
 finally:await fixture.close()
if __name__=='__main__':
 result={'status':'FAIL'}
 try:result.update(asyncio.run(main()))
 finally:
  names=['scripts/xterm-browser-check.py','scripts/guest-terminal-mux.c','scripts/build-browser-initramfs.py','terminal.js','app.js','desktop-apps.js','assets/desktop/apps.json','assets/terminal/v2/image.json']
  result['sha256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names};out=ROOT/'.build/checks/xterm-browser-result.json'
  if out.exists():out.rename(out.with_name('xterm-browser-before-'+str(time.time_ns())+'.json'))
  out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
