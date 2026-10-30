#!/usr/bin/env python3
"""Exercise two registered public-site browsers and the real featured game."""
import importlib.util,json,secrets,shlex,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);origin='https://ksu.codes';sessions=[];names=['livecheck'+secrets.token_hex(5) for _ in range(2)];print('Disposable accounts:',*names,flush=True)
def js(s,code,args=[]):return d.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
def ready(s,selector,timeout=90):
 def check():
  value=js(s,'const n=document.querySelector(arguments[0]);return {exists:!!n,text:n?.textContent||"",loading:!!n?.querySelector("[data-app-loading]")};',[selector])
  if 'Could not load this app' in value['text'] or 'Chat networking is unavailable' in value['text']:raise RuntimeError(value['text'])
  return value['exists'] and not value['loading']
 return d.wait(check,timeout)
try:
 for name in names:
  s=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(s);d.call('/session/'+s+'/goog/cdp/execute',{'cmd':'Emulation.setDeviceMetricsOverride','params':{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True}});d.call('/session/'+s+'/goog/cdp/execute',{'cmd':'Emulation.setTouchEmulationEnabled','params':{'enabled':True}});d.call('/session/'+s+'/url',{'url':origin+'/'});d.call('/session/'+s+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});d.wait(lambda:js(s,'return !!document.querySelector(".login-gate");'),30);js(s,'document.querySelector(".login-toggle").click();');js(s,'''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');set('Confirm password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name]);d.wait(lambda:js(s,'return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),60);js(s,'localStorage.setItem("codi-device-history-consent-v1","accepted-v1");window.liveDesktop=[...surfaces.values()][0];window.chatId=liveDesktop.launch("chat").id;');selector=js(s,'return "[data-window=\\\""+chatId+"\\\"]";');ready(s,selector)
  def chat_ready():
   value=js(s,'const n=document.querySelector(arguments[0]);const button=n?.querySelector("button[type=submit]");return {ready:!!button&&!button.disabled,text:n?.textContent||""};',[selector])
   if 'Could not load this app' in value['text']:raise RuntimeError(value['text'])
   return value['ready']
  d.wait(chat_ready,90)
  assert js(s,'return !document.querySelector(arguments[0]).querySelector(".channel-list").textContent.includes("SYSTEM");',[selector])
 for s in sessions:js(s,'''window.chatTrace=[];const original=window.fetch.bind(window);window.fetch=async(...args)=>{const url=new URL(args[0] instanceof Request?args[0].url:String(args[0]),location.href),start=performance.now();try{const response=await original(...args);if(url.pathname.includes('/official-'))chatTrace.push({path:url.pathname,status:response.status,start:Math.round(start),end:Math.round(performance.now())});return response;}catch(error){if(url.pathname.includes('/official-'))chatTrace.push({path:url.pathname,status:0,start:Math.round(start),end:Math.round(performance.now())});throw error;}};''')
 message='Live test '+secrets.token_hex(3);started=time.monotonic();js(sessions[0],'''window.chatTrace.push({path:'SEND',start:Math.round(performance.now()),end:Math.round(performance.now())});const n=document.querySelector('[data-window="'+chatId+'"]'),t=n.querySelector('textarea');t.value=arguments[0];n.querySelector('form').requestSubmit();''',[message])
 for s in sessions:d.wait(lambda:js(s,'''const n=document.querySelector('[data-window="'+chatId+'"]');return n?.querySelector('.channel-history')?.textContent.includes(arguments[0])&&!n.querySelector('.is-pending');''',[message]),120)
 print('PASS two registered public browsers received a server-accepted message in',round(time.monotonic()-started,1),'seconds',flush=True)
 d.wait(lambda:js(sessions[1],'''const n=document.querySelector('[data-window="'+chatId+'"]');return [...(n?.querySelectorAll('.channel-message')||[])].some(line=>line.textContent.includes(arguments[0]+': '+arguments[1]));''',[names[0],message]),45)
 print('PASS the receiving browser shows the registered sender name',flush=True)
 def accepted_marker():
  return js(sessions[0],'''const n=document.querySelector('[data-window="'+chatId+'"]'),m=[...n.querySelectorAll('.channel-message.is-own')].find(x=>x.textContent.includes(arguments[0])&&x.dataset.delivery==='sent');return !!m&&getComputedStyle(m,'::after').content==='"Sent"'&&m.getAttribute('aria-label')?.includes('Sent to server')&&m.title.includes('other people is not tracked');''',[message])
 d.wait(accepted_marker,120);print('PASS own message displays honest server acceptance',flush=True)

 d.wait(lambda:js(sessions[0],'''const h=document.querySelector('[data-window="'+chatId+'"] .channel-history');return h&&h.clientHeight>30&&h.scrollHeight>h.clientHeight+32;'''),120)
 js(sessions[0],'''const h=document.querySelector('[data-window="'+chatId+'"] .channel-history');h.scrollTop=0;h.dispatchEvent(new Event('scroll'));''')
 reply='Live reply '+secrets.token_hex(3);js(sessions[1],'''const n=document.querySelector('[data-window="'+chatId+'"]'),t=n.querySelector('textarea');t.value=arguments[0];n.querySelector('form').requestSubmit();''',[reply])
 d.wait(lambda:js(sessions[0],'''return document.querySelector('[data-window="'+chatId+'"] .channel-history')?.textContent.includes(arguments[0]);''',[reply]),120)
 result=js(sessions[0],'''const n=document.querySelector('[data-window="'+chatId+'"]'),h=n.querySelector('.channel-history'),latest=[...n.querySelectorAll('button')].find(b=>b.textContent==='Latest messages');return {top:h.scrollTop,hasLatest:!!latest&&!latest.hidden,height:h.clientHeight};''');assert result['top']<5 and result['hasLatest'],result
 js(sessions[0],'''const n=document.querySelector('[data-window="'+chatId+'"]');[...n.querySelectorAll('button')].find(b=>b.textContent==='Latest messages').click();''');assert js(sessions[0],'''const h=document.querySelector('[data-window="'+chatId+'"] .channel-history');return h.scrollHeight-h.clientHeight-h.scrollTop<4;''');print('PASS phone-sized chat keeps reading position and jumps to latest',flush=True)
 js(sessions[0],'''const h=document.querySelector('[data-window="'+chatId+'"] .channel-history');h.scrollTop=0;h.dispatchEvent(new Event('scroll'));''');before=js(sessions[0],'''const n=document.querySelector('[data-window="'+chatId+'"]');return n.querySelectorAll('.channel-history [data-message]').length;''');d.wait(lambda:js(sessions[0],'''const b=document.querySelector('[data-window="'+chatId+'"] .channel-older');return b&&!b.disabled;'''),60);js(sessions[0],'''document.querySelector('[data-window="'+chatId+'"] .channel-older').click();''');d.wait(lambda:js(sessions[0],'''const n=document.querySelector('[data-window="'+chatId+'"]');return n.querySelectorAll('.channel-history [data-message]').length>arguments[0];''',[before]),120);print('PASS phone-sized chat loads earlier verified messages',flush=True)


 s=sessions[0];js(s,'window.chessId=liveDesktop.launch("chess").id;');selector=js(s,'return "[data-window=\\\""+chessId+"\\\"]";');ready(s,selector)
 def chess_ready():
  value=js(s,'const n=document.querySelector(arguments[0]);return {squares:n?.querySelectorAll(".chess-square").length||0,moves:n?.querySelector(".chess-moves")?.textContent||"",text:n?.textContent||""};',[selector])
  if 'Game is unavailable:' in value['text']:raise RuntimeError(value['text'])
  return value['squares']==64 and value['moves'] and value['moves']!='No moves yet.'
 d.wait(chess_ready,120);d.wait(lambda:js(s,'const n=document.querySelector(arguments[0])?.querySelector("button[type=submit]");return !!n&&!n.disabled;',[selector]),60);print('PASS featured Stockfish game loads its current saved board and moves on the public desktop',flush=True)
 d.wait(lambda:js(s,'''const n=document.querySelector(arguments[0]);return n?.querySelector('.chess-chat-history')?.textContent.includes(arguments[1]+': '+arguments[2]);''',[selector,names[1],reply]),45)
 print('PASS Chess shows the registered sender name in its separate chat',flush=True)
 js(s,"""const n=document.querySelector(arguments[0]),b=[...n.querySelectorAll('button')].find(x=>x.textContent==='Previous game');if(!b||b.hidden||b.disabled||b.getBoundingClientRect().height<44)throw Error('Previous game control missing or too small');b.click();""",[selector])
 def previous_ready():
  state=js(s,"""const n=document.querySelector(arguments[0]);return {heading:n?.querySelector('h2')?.textContent||'',moves:n?.querySelector('.chess-moves')?.textContent||'',status:n?.querySelector('.chess-status')?.textContent||'',button:[...n.querySelectorAll('button')].find(x=>x.textContent==='Watch current game')?.hidden};""",[selector]);return 'Previous game' in state['heading'] and state['moves']!='No moves yet.' and state['moves'] and 'Game finished:' in state['status'] and state['button'] is False
 d.wait(previous_ready,180);print('PASS previous saved game loads and is verified in Chess',flush=True)
 js(s,"""const n=document.querySelector(arguments[0]);[...n.querySelectorAll('button')].find(x=>x.textContent==='Watch current game').click();""",[selector]);d.wait(lambda:js(s,"""const n=document.querySelector(arguments[0]);return !n?.querySelector('h2')?.textContent.includes('Previous game')&&n?.querySelectorAll('.chess-square').length===64&&!n?.querySelector('.chess-replay button')?.disabled;""",[selector]),120);print('PASS returning to the current game',flush=True)

 replay=js(s,'''const n=document.querySelector(arguments[0]),before=n.querySelector('.chess-position')?.textContent,previous=[...n.querySelectorAll('.chess-replay button')].find(b=>b.textContent==='Previous');if(!previous||previous.disabled)return null;previous.click();const after=n.querySelector('.chess-position').textContent;[...n.querySelectorAll('.chess-replay button')].find(b=>b.textContent==='Latest').click();return {before,after,latest:n.querySelector('.chess-position').textContent};''',[selector]);assert replay and replay['before']!=replay['after'] and replay['latest']==replay['before'],replay;print('PASS the finished game can be stepped backward and returned to its latest position',flush=True)
 message='Live game test '+secrets.token_hex(3);started=time.monotonic();js(s,'''const n=document.querySelector('[data-window="'+chessId+'"]'),t=n.querySelector('textarea');t.value=arguments[0];n.querySelector('form').requestSubmit();''',[message]);other=sessions[1]
 d.wait(lambda:js(other,'''const n=document.querySelector('[data-window="'+chatId+'"]');return n?.querySelector('.channel-history')?.textContent.includes(arguments[0]);''',[message]),120);print('PASS Chess-window message reaches the other user in',round(time.monotonic()-started,1),'seconds',flush=True)
finally:
 for index,s in enumerate(sessions):
  try:print('Official request timings browser',index+1,json.dumps(js(s,'return window.chatTrace||[];')),flush=True)
  except Exception:pass
 for s in sessions:
  try:js(s,'endSession();')
  except Exception:pass
  try:d.call('/session/'+s,method='DELETE')
  except Exception:pass

 cleanup="""import json,re,sqlite3,sys\nnames=json.load(sys.stdin);assert len(names)<=2 and all(re.fullmatch(r'livecheck[0-9a-f]{10}',n) for n in names)\na=sqlite3.connect('/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3',timeout=30);b=sqlite3.connect('/var/lib/codi-official/state/official.sqlite',timeout=30)\nfor name in names:\n row=a.execute('SELECT subject FROM accounts WHERE username=?',(name,)).fetchone()\n if row:\n  sub=row[0];b.execute('BEGIN IMMEDIATE');b.execute('DELETE FROM official_chat_names WHERE EXISTS (SELECT 1 FROM official_chat_actors x WHERE x.channel=official_chat_names.channel AND x.actor=official_chat_names.actor AND x.subject=?)',(sub,))\n  for table in ('official_upload_bans','official_chat_ban_epochs','official_chat_actor_reviews','official_chat_actors'):b.execute('DELETE FROM '+table+' WHERE subject=?',(sub,))\n  b.commit();a.execute('BEGIN IMMEDIATE');a.execute('DELETE FROM account_policy WHERE subject=?',(sub,));a.execute('DELETE FROM accounts WHERE username=? AND subject=?',(name,sub));a.commit()\nprint('removed',len(names),'disposable accounts and author metadata')"""
 try:print(subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','python3','-B','-c',shlex.quote(cleanup)],input=json.dumps(names),capture_output=True,text=True,check=True,timeout=30).stdout.strip(),flush=True)
 except Exception as error:print('Account cleanup failed:',error,'names:',names,flush=True)
