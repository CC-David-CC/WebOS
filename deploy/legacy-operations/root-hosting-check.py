#!/usr/bin/env python3
"""Real generated Caddy root routing plus actual blog/prototype FastAPI HTTP.

Loopback-only fixture: native ports use tagged protocol stubs. The real native
root services have separate installed VM evidence; this is no public TLS claim.
"""
import asyncio,base64,hashlib,importlib.util,json,socket,subprocess,sys,tempfile,time
from copy import deepcopy
from pathlib import Path
from aiohttp import ClientSession,web

ROOT=Path(__file__).resolve().parent.parent
INPUT=ROOT/'.build/hosting/root-mount-r1-inputs'
CANDIDATE=ROOT/'.build/hosting/root-mount-r1-candidate'
BINARY=ROOT.parent/'.build/tools/caddy'
WEBSITE=ROOT.parent/'.build/deployment/ksu.codes'


def digest(raw):return hashlib.sha256(raw).hexdigest()


async def run():
    checks=[];runners=[];children=[];seen=[];log=None;listener=None
    def check(name,value):assert value,name;checks.append(name)
    with tempfile.TemporaryDirectory(prefix='codi-root-hosting-') as temporary:
        folder=Path(temporary);speech=folder/'speech';speech.mkdir();(speech/'sample.bin').write_bytes(b'OWNED-SPEECH-ASSET')
        async def backend(role):
            async def request(r):
                if r.headers.get('Upgrade','').lower()=='websocket':
                    seen.append((role,r.path,'websocket'));ws=web.WebSocketResponse();await ws.prepare(r)
                    async for message in ws:
                        if message.type.name=='TEXT':await ws.send_str(role+':'+r.path+':'+message.data)
                    return ws
                body=await r.read();seen.append((role,r.path,len(body)))
                return web.json_response({'role':role,'path':r.path,'method':r.method,'bytes':len(body),'host':r.headers.get('Host')})
            app=web.Application(client_max_size=20*1024*1024);app.router.add_route('*','/{path:.*}',request)
            runner=web.AppRunner(app,access_log=None);await runner.setup();runners.append(runner);site=web.TCPSite(runner,'127.0.0.1',0);await site.start();return site._server.sockets[0].getsockname()[1]
        try:
            ports={p:await backend(role) for p,role in [(8118,'issuer'),(8119,'steward'),(8132,'guest'),(8140,'files')]}
            generic=await backend('other-site')
            listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(32);blog_port=listener.getsockname()[1]
            log=(ROOT/'.build/checks/root-hosting-process.log').open('wb')
            blog=await asyncio.create_subprocess_exec(str(ROOT.parent/'.build/blog-preview-venv/bin/python'),'-m','uvicorn','app.main:app','--fd',str(listener.fileno()),'--log-level','warning',cwd=WEBSITE,pass_fds=(listener.fileno(),),stdout=log,stderr=log);children.append(blog)
            async with ClientSession(headers={'Accept-Encoding':'identity'}) as client:
                deadline=time.monotonic()+15
                while True:
                    try:
                        async with client.get('http://127.0.0.1:'+str(blog_port)+'/healthz',headers={'Host':'ksu.codes'}) as r:
                            if r.status==200:break
                    except OSError:pass
                    assert time.monotonic()<deadline,'Owned blog startup timeout';await asyncio.sleep(.05)
                # The unrelated hardware site's production password hashes
                # stay on the server. Supply an independently generated fixture
                # account only for adapting/testing that unchanged route block.
                password_hash=subprocess.check_output([str(BINARY),'hash-password','--plaintext','codi-root-routing-fixture'],text=True).strip()
                users=folder/'hardware-users';users.write_text('fixture '+password_hash+'\n');users.chmod(0o600)
                prepare=folder/'Caddyfile';prepare.write_text((CANDIDATE/'Caddyfile.prepare').read_text().replace('/etc/caddy/private/hardware-users',str(users)))
                adapted=subprocess.run([str(BINARY),'adapt','--adapter','caddyfile','--config',str(prepare)],capture_output=True,text=True)
                if adapted.returncode:raise ValueError(adapted.stderr)
                config=json.loads(adapted.stdout)
                spec=importlib.util.spec_from_file_location('root_route_generator',CANDIDATE/'common.py');sys.path.insert(0,str(CANDIDATE));generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator);manifest=generator.load(CANDIDATE/'sites.toml')
                for site in manifest['sites']:ports[site['port']]=blog_port if site['domain']=='ksu.codes' else generic
                def remap(value):
                    if isinstance(value,list):return [remap(v) for v in value]
                    if isinstance(value,dict):return {k:remap(v) for k,v in value.items()}
                    if isinstance(value,str):
                        if value.startswith('127.0.0.1:') and value[10:].isdigit() and int(value[10:]) in ports:return '127.0.0.1:'+str(ports[int(value[10:])])
                        if value.startswith('/srv/codi-connected/speech/'):return str(speech)
                        if value.startswith('/var/log/caddy/'):return str(folder/Path(value).name)
                    return value
                config=remap(config);config['admin']={'listen':'unix/'+str(folder/'admin.sock')}
                probe=socket.socket();probe.bind(('127.0.0.1',0));port=probe.getsockname()[1];probe.close()
                servers=config['apps']['http']['servers'];assert len(servers)==1
                for server in servers.values():server['listen']=['127.0.0.1:'+str(port)];server['automatic_https']={'disable':True}
                cfg=folder/'Caddy.json';cfg.write_text(json.dumps(config))
                caddy=await asyncio.create_subprocess_exec(str(BINARY),'run','--config',str(cfg),stdout=log,stderr=log);children.append(caddy)
                base='http://127.0.0.1:'+str(port)
                async def request(path,method='GET',host='ksu.codes',data=None):
                    headers={'Host':host}
                    if host=='hardware.ksu.codes':headers['Authorization']='Basic '+base64.b64encode(b'fixture:codi-root-routing-fixture').decode()
                    async with client.request(method,base+path,headers=headers,data=data,allow_redirects=False) as r:return r.status,dict(r.headers),await r.read()
                deadline=time.monotonic()+15
                while True:
                    try:
                        if (await request('/healthz'))[0]==200:break
                    except OSError:pass
                    assert caddy.returncode is None and time.monotonic()<deadline,'Owned Caddy startup timeout';await asyncio.sleep(.05)
                for path,role in [('/','guest'),('/config.json','guest'),('/vm/manifest.json','guest'),('/assets/desktop/offline-worker.js','guest'),('/api/v1/desktop-status','issuer'),('/discovery.json','issuer'),('/.well-known/codi-issuer.json','issuer'),('/rendezvous','steward'),('/gateway/client.mjs','files')]:
                    status,headers,body=await request(path);value=json.loads(body);assert status==200 and value['role']==role and value['path']==path,(path,status,value)
                check('root desktop assets API discovery gateway and rendezvous route without hidden rewrites',True)
                status,headers,_=await request('/');check('root desktop receives its scoped WASM CSP and no-store',status==200 and "'wasm-unsafe-eval'" in headers['Content-Security-Policy'] and headers['Cache-Control']=='no-store')
                for path in ['/hidden','/hidden/','/hidden/config.json']:
                    status,headers,_=await request(path);assert status==308 and headers['Location']=='/'
                check('old preview paths redirect to the root instead of serving hidden backends',True)
                for method in ['GET','HEAD']:
                    status,headers,body=await request('/blog',method);assert status==308 and headers['Location']=='/blog/'
                    status,headers,body=await request('/blog/',method);assert status==200 and body==((WEBSITE/'public/index.html').read_bytes() if method=='GET' else b'')
                check('real blog GET HEAD canonical redirect and unchanged page bytes pass through Caddy',True)
                _,headers,_=await request('/blog/');check('blog retains strict website policy outside the desktop CSP',"'wasm-unsafe-eval'" not in headers['Content-Security-Policy'] and "script-src" not in headers['Content-Security-Policy'])
                for p in (WEBSITE/'public/posts').glob('*.html'):
                    status,_,body=await request('/posts/'+p.stem);assert status==200 and body==p.read_bytes() and b'href="/blog/"' in body
                check('all real guides keep their content and blog backlinks through reserved routing',True)
                records=json.loads((WEBSITE/'public/desktop/release.json').read_text())['files'];assert len(records)==133
                for name,record in records.items():
                    status,_,body=await request('/desktop/'+name);assert status==200 and record=={'bytes':len(body),'sha256':digest(body)},name
                check('all133 real sizing prototype files remain byte-identical over Caddy HTTP',True)
                _,headers,_=await request('/desktop/');check('prototype retains its separate existing WASM policy',"'wasm-unsafe-eval'" in headers['Content-Security-Policy'])
                for path in ['/static/site.css','/robots.txt','/test-time/','/healthz']:
                    # Static files are selected from the real blog, not guessed.
                    if path=='/static/site.css':path='/static/'+str(next(p for p in sorted((WEBSITE/'public/static').rglob('*')) if p.is_file()).relative_to(WEBSITE/'public/static'))
                    status,_,_=await request(path);assert status==200,(path,status)
                check('existing static test-time robots and health routes retain the website backend',True)
                status,_,body=await request('/assets/speech/sample.bin');check('speech assets use only the selected static directory at the root path',status==200 and body==b'OWNED-SPEECH-ASSET')
                for site in manifest['sites']:
                    if site['domain']=='ksu.codes':continue
                    status,_,body=await request('/',host=site['domain']);assert status==200 and json.loads(body)['role']=='other-site',site['domain']
                check('other nine domain roots stay on their original website routes',True)
                async with client.get(base+'/',headers={'Host':'hardware.ksu.codes'}) as r:check('unrelated hardware authentication remains enforced using fixture-only credentials',r.status==401)
                async with client.ws_connect(base+'/rendezvous',headers={'Host':'ksu.codes','Origin':'http://ksu.codes'}) as ws:
                    await ws.send_str('ROUTE_CHECK');reply=await ws.receive();assert reply.data=='steward:/rendezvous:ROUTE_CHECK'
                check('actual WebSocket upgrade reaches the root steward endpoint',True)
                status,_,_=await request('/api/v1/probe','POST',data=b'x'*65537);check('root API request bodies keep the64KiB limit',status==413)
                status,_,body=await request('/gateway/probe','POST',data=b'x'*65537);check('file gateway accepts payloads above API limit on its separate route',status==200 and json.loads(body)['bytes']==65537)
                status,_,_=await request('/gateway/probe','POST',data=b'x'*(12*1024*1024+1));check('file gateway retains the12MiB ceiling',status==413)
                # Prove the optional selector cannot cross domains or silently
                # turn on backends for an unenabled/unvalidated site.
                for field,value in [('domain','example.invalid'),('codi_mount','/other'),('codi_mount',False),('enabled',False),('codi_preview',False)]:
                    bad=deepcopy(manifest);s=next(s for s in bad['sites'] if s['domain']=='ksu.codes');s[field]=value
                    try:generator.validate(bad)
                    except ValueError:continue
                    raise AssertionError('Unsafe root selector accepted: '+field)
                check('root selector rejects wrong domain mount type disabled and missing preview policy',True)
                return {'status':'PASS','scope':__doc__,'checks':checks,'prototypeHTTPFilesVerified':133,'nativeBackendStubsUsed':True,'realBlogBackendUsed':True,'productionChanged':False,'candidateGeneratorSHA256':digest((CANDIDATE/'common.py').read_bytes()),'CaddyVersion':subprocess.check_output([str(BINARY),'version'],text=True).strip()}
        finally:
            for child in reversed(children):
                if child.returncode is None:
                    child.terminate()
                    try:await asyncio.wait_for(child.wait(),8)
                    except asyncio.TimeoutError:child.kill();await child.wait()
            for runner in reversed(runners):await runner.cleanup()
            if listener:listener.close()
            if log:log.close()


if __name__=='__main__':
    result={'status':'FAIL'}
    try:result.update(asyncio.run(run()))
    finally:
        result['scriptSHA256']=digest(Path(__file__).read_bytes());out=ROOT/'.build/checks/root-hosting-result.json'
        if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
