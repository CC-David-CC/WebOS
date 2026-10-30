#!/usr/bin/env python3
"""One actual Web Crypto receiver, preissued distinct signed authors; not 8k RTC clients.

Private fixture authority creates public certificates/controller grants/origins
using existing cryptography/JOSE. This does NOT exercise server session admission,
browser PoW, gossip transport, v86, WAN, durable history or measured per-client RSS.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import shutil
import sys
import tempfile
import threading
import time
import urllib.parse
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'codiserver-server-v0.3.0'))
sys.path.insert(0, str(ROOT))
from codiauth import jose
from codiauth.service import Config, Service
from cryptography.hazmat.primitives.asymmetric import ec
from origin_service.http_server import BoundedServer, QuietHandler

spec = importlib.util.spec_from_file_location('compact_driver', ROOT / 'scripts/touch-preview-check.py')
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--participants', type=int, default=8000)
    parser.add_argument('--network-root', type=Path, default=ROOT / 'network')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert 1 <= args.participants <= 8192 and not args.output.exists()
    result = {'status': 'FAIL', 'scope': __doc__, 'productionChanged': False,
              'actualBrowsers': 1, 'RTCParticipants': 0, 'actualV86Tested': False,
              'full8kNetworkTested': False, 'serverAdmissionTested': False}
    session = server = None
    try:
        with tempfile.TemporaryDirectory(prefix='codi-compact-replay-') as directory:
            folder = Path(directory)
            public = folder / 'public'
            (public / 'network').mkdir(parents=True)
            source_pins = {}
            for p in args.network_root.glob('*.mjs'):
                shutil.copyfile(p, public / 'network' / p.name)
                source_pins['network/' + p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
            shutil.copyfile(ROOT / 'scripts/compact-replay-page.mjs', public / 'fixture.mjs')
            (public / 'index.html').write_text('<!doctype html><title>Replay fixture</title><script type="module" src="/fixture.mjs"></script>')
            server = make_server('127.0.0.1', 0, lambda *_: [], server_class=BoundedServer, handler_class=QuietHandler)
            origin = 'http://127.0.0.1:' + str(server.server_port)
            issuer = Service(Config(folder / 'state', public, origin=origin))
            policy = issuer.config()['identity']
            controller_key = ec.generate_private_key(ec.SECP256R1())

            def identity(key, name):
                sid = secrets.token_urlsafe(24)
                return issuer.issue({'sid': sid, 'sub': sid, 'name': name, 'kind': 'anonymous',
                                     'key': jose.public_jwk(key), 'deadline': int(time.time()) + 900})['identity']

            controller = identity(controller_key, 'Fixture controller')
            node = jose.b64(secrets.token_bytes(32))
            room_id = jose.digest(jose.dumps(['codi-public-mesh-room/3', node, 'chat']))
            now = int(time.time())
            expiry = now + 300
            descriptor = jose.sign({'version': 'codi-public-mesh-room/3', 'node_id': node,
                'room_id': room_id, 'membership_epoch': 1, 'label': 'Compact replay fixture',
                'controller': controller, 'public': True, 'kinds': ['chat'],
                'issued_at': now, 'expires_at': expiry}, controller_key, 'codi-mesh-descriptor+jws')
            parts = descriptor.split('.')
            descriptor_hash = jose.digest(jose.dumps(['codi-mesh-descriptor+jws', parts[0], parts[1]]))
            keys, first = set(), []
            generated = signing_ms = wire_bytes = 0

            def event(record, key, sequence):
                t = int(time.time())
                return jose.sign({'version': 'codi-mesh/1', 'room_id': room_id,
                    'descriptor_hash': descriptor_hash, 'membership_epoch': 1,
                    'author_session_id': record['identity']['sid'], 'stream_incarnation': record['incarnation'],
                    'sequence': sequence, 'issued_at': t, 'expires_at': min(t+60, expiry),
                    'kind': 'chat', 'payload': {'text': 'Signed author '+str(sequence)}}, key, 'codi-mesh-origin+jws')

            def author(index):
                nonlocal generated, signing_ms
                start = time.monotonic()
                key = ec.generate_private_key(ec.SECP256R1())
                who = identity(key, 'Author '+str(index))
                thumb = jose.thumbprint(who['key'])
                assert thumb not in keys
                keys.add(thumb)
                incarnation = jose.b64(secrets.token_bytes(32))
                record = {'identity': who, 'incarnation': incarnation}
                t = int(time.time())
                record['grant'] = jose.sign({'version': 'codi-public-mesh-room/3', 'node_id': node,
                    'room_id': room_id, 'descriptor_hash': descriptor_hash, 'membership_epoch': 1,
                    'author_session_id': who['sid'], 'author_key': thumb, 'incarnation': incarnation,
                    'kinds': ['chat'], 'work_id': jose.digest('preissued-fixture:'+str(index)),
                    'issued_at': t, 'expires_at': expiry}, controller_key, 'codi-mesh-member+jws')
                record['event'] = event(record, key, 1)
                if not first:
                    first.append((record, key))
                generated += 1
                signing_ms += (time.monotonic()-start)*1000
                return record

            def app(env, start):
                nonlocal wire_bytes
                path = env['PATH_INFO']
                if path.startswith('/fixture/'):
                    if path == '/fixture/config':
                        value = {'identity': policy, 'controller': controller, 'descriptor': descriptor}
                    elif path == '/fixture/batch':
                        query = urllib.parse.parse_qs(env['QUERY_STRING'])
                        index, count = int(query['start'][0]), int(query['count'][0])
                        assert 0 <= index < args.participants and 1 <= count <= 64 and index+count <= args.participants
                        value = [author(i) for i in range(index, index+count)]
                    elif path == '/fixture/controls':
                        record, key = first[0]
                        value = {**record, 'events': [event(record, key, i) for i in range(1, 8)], 'extra': author(args.participants)}
                    elif path == '/fixture/stats':
                        value = {'generatedAuthors': generated, 'distinctSigningKeys': len(keys),
                                 'signingMs': signing_ms, 'fixturePublicResponseBytes': wire_bytes,
                                 'fixtureAuthorityOnly': True, 'privateKeysUploaded': False}
                    else:
                        start('404 Not Found', [('Content-Length', '0')]);return [b'']
                    raw = jose.dumps(value).encode()
                    wire_bytes += len(raw)
                    start('200 OK', [('Content-Type', 'application/json'), ('Cache-Control', 'no-store'), ('Content-Length', str(len(raw)))]);return [raw]
                return issuer(env, start)

            server.set_app(app)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            session = driver.call('/session', {'capabilities': {'alwaysMatch': {'browserName': 'chrome',
                'goog:chromeOptions': {'binary': '/snap/chromium/current/usr/lib/chromium-browser/chrome',
                    'args': ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage']}}}})['sessionId']
            driver.call('/session/'+session+'/timeouts', {'script': 600000})
            driver.call('/session/'+session+'/url', {'url': origin+'/'})
            driver.wait(lambda: driver.call('/session/'+session+'/execute/sync', {'script': 'return window.compactReady===true;', 'args': []}), 30)
            result.update(driver.call('/session/'+session+'/execute/async', {'script': 'const done=arguments[arguments.length-1];runCompactReplay(arguments[0]).then(done,e=>done({status:"FAIL",error:e.stack}));', 'args': [args.participants]}))
            result['cleanupBudget'] = driver.call('/session/'+session+'/execute/sync', {'script':'return window.compactCleanup;','args':[]})
            result['sourceSHA256'] = {**source_pins, **{'scripts/'+name: hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in [Path(__file__).name, 'compact-replay-page.mjs']}}
    finally:
        if session:
            driver.call('/session/'+session, method='DELETE')
            result['ownedBrowserContextsClosed'] = 1
        if server:
            server.shutdown();server.server_close()
        args.output.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k not in ['sourceSHA256', 'samples']}, indent=2))
    return result['status'] == 'PASS'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
