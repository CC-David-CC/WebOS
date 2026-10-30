#!/usr/bin/env python3
"""Run two legal Stockfish WASM moves in a disposable browser worker."""
import functools,http.server,importlib.util,json,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT.parent)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();sid=None
try:
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];d.call('/session/'+sid+'/timeouts',{'script':60000})
 d.call('/session/'+sid+'/url',{'url':f'http://127.0.0.1:{server.server_port}/active-system/scripts/stockfish-browser-fixture.html'})
 d.wait(lambda:d.call('/session/'+sid+'/execute/sync',{'script':'return window.fixtureReady===true;','args':[]}),20)
 r=d.call('/session/'+sid+'/execute/async',{'script':'const done=arguments[0];stockfishFixture.run().then(value=>done({value}),error=>done({error:error.stack}));','args':[]});assert 'error' not in r,r
 print(json.dumps({'status':'PASS','scope':__doc__,'moves':r['value']['moves']}))
finally:
 if sid:d.call('/session/'+sid,method='DELETE')
 server.shutdown();server.server_close();thread.join()
