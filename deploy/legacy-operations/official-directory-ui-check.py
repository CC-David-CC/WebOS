#!/usr/bin/env python3
"""Exercise rendered official/user discovery with a fake host; no backend claim."""
import argparse,functools,http.server,importlib.util,json,shutil,tempfile,threading,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];s=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();server=None;thread=None;sid=None;profile=Path(tempfile.mkdtemp(prefix='codi-official-ui-',dir=Path.home()/'snap/chromium/common'));r={'status':'FAIL','scope':__doc__,'checks':[]}
def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
def check(name,ok):assert ok,name;r['checks'].append(name);print(json.dumps({'check':name}),flush=True)
try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}})['sessionId'];d.call('/session/'+sid+'/url',{'url':origin+'/scripts/fixtures/official-directory-ui.html'});d.wait(lambda:js('return !!window.fixture&&document.querySelector("[data-channel-results]")?.textContent.includes("Chess hall");'),15)
 check('official and user channels are labeled separately',js('const s=document.querySelector("[data-channel-results]").textContent;return s.includes("Chess hall")&&s.includes("Official · server-backed")&&s.includes("Garden")&&s.includes("User-created");'))
 js('document.querySelector("[data-official-more]").click();');d.wait(lambda:js('return document.querySelector("[data-channel-results]").textContent.includes("Science hall");'),10);check('more loads the next official page',True)
 js('const n=document.querySelector("input[type=search]");n.value="chess";n.dispatchEvent(new Event("input",{bubbles:true}));');d.wait(lambda:js('return fixture.calls.some(x=>x.method==="list"&&x.query==="chess")&&document.querySelector("[data-channel-results]").textContent.includes("Chess hall");'),10);check('search filters the displayed directory',js('const s=document.querySelector("[data-channel-results]").textContent;return !s.includes("Science hall")&&!s.includes("Garden");'))
 js('document.querySelector("[data-channel-results] button").click();');d.wait(lambda:js('return fixture.calls.some(x=>x.method==="join"&&x.channel==="official1");'),10);check('official Join targets the selected official channel',True)
 js('fixture.fail(true);const n=document.querySelector("input[type=search]");n.value="";n.dispatchEvent(new Event("input",{bubbles:true}));');d.wait(lambda:js('return document.querySelector("[data-official-more]")?.textContent==="Retry official channels";'),10);check('directory failure offers a retry without hiding user channels',js('return document.querySelector("[data-channel-results]").textContent.includes("Garden");'))
 js('fixture.fail(false);document.querySelector("[data-official-more]").click();');d.wait(lambda:js('return document.querySelector("[data-channel-results]").textContent.includes("Chess hall");'),10);check('retry restores official listings',True)
 js('fixture.dispose();');check('disposing closes the channel service',js('return fixture.calls.some(x=>x.method==="close");'));r['status']='PASS'
except Exception as e:r.update(error=str(e),traceback=traceback.format_exc())
finally:
 if sid:d.call('/session/'+sid,method='DELETE')
 if server:server.shutdown();server.server_close()
 if thread:thread.join(timeout=3)
 shutil.rmtree(profile);r['ownedProfileRemoved']=not profile.exists()
a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error')}));raise SystemExit(r['status']!='PASS')
