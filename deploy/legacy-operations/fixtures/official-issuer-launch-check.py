#!/usr/bin/env python3
"""Check optional official authorization on the actual local issuer launcher."""
import argparse,json,socket,subprocess,sys,tempfile,time,urllib.error,urllib.request
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'))
from codiauth import jose
parser=argparse.ArgumentParser();parser.add_argument('--release',type=Path);args=parser.parse_args();execution=args.release.resolve() if args.release else ROOT

with tempfile.TemporaryDirectory(prefix='official-issuer-launch-') as temp:
    for enabled in (False,True):
        with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
        origin='http://127.0.0.1:'+str(port);runtime=Path(temp)/str(port);runtime.mkdir(mode=0o700)
        command=[sys.executable,'-B',str(execution/'scripts/serve-connected.py'),'--port',str(port),'--runtime-dir',str(runtime)]
        if enabled:command.append('--official-channels')
        child=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            deadline=time.monotonic()+30
            while True:
                if child.poll() is not None:raise AssertionError(child.stderr.read().decode())
                try:
                    with urllib.request.urlopen(origin+'/config.json',timeout=1) as response:assert response.status==200
                    break
                except OSError:
                    if time.monotonic()>deadline:raise AssertionError('Issuer startup timed out')
                    time.sleep(.1)
            data=json.dumps({'key':jose.public_jwk(ec.generate_private_key(ec.SECP256R1())),'path':'/api/v1/official-ingest/authorize'}).encode()
            request=urllib.request.Request(origin+'/api/v1/official-ingest/challenge',data=data,headers={'Content-Type':'application/json','Origin':origin})
            try:
                with urllib.request.urlopen(request,timeout=5) as response:status=response.status;value=json.loads(response.read())
            except urllib.error.HTTPError as error:status=error.code;value=json.loads(error.read())
            assert (status==200 and len(value['nonce'])==43) if enabled else status==404,(enabled,status,value)
        finally:
            child.terminate();child.wait(timeout=10);child.stderr.close()
print('PASS: actual issuer launcher exposes official challenge only when enabled')
