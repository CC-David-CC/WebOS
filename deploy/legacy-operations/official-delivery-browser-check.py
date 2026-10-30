#!/usr/bin/env python3
"""Run the ancestry checks in Chromium, without a JavaScript build runtime."""
import functools,http.server,pathlib,subprocess,threading
root=pathlib.Path(__file__).resolve().parents[1]
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
try:
    command=['/snap/chromium/current/usr/lib/chromium-browser/chrome','--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--virtual-time-budget=5000','--dump-dom',f'http://127.0.0.1:{server.server_port}/scripts/official-delivery-check.html']
    run=subprocess.run(command,capture_output=True,text=True,timeout=30)
    if run.returncode or '<p id="result">PASS</p>' not in run.stdout:raise SystemExit('Chromium check failed: '+run.stdout[-2000:]+'\n'+run.stderr[-1000:])
    print('PASS: cross-page ancestry, missing future and wrong checkpoint')
finally:
    server.shutdown();server.server_close();thread.join()
