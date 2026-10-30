#!/usr/bin/env python3
"""Automatic same-room reader introductions over actual Chrome RTC links.

Disposable loopback issuer, SQLite, ES256/WebCrypto, IndexedDB, four browsers;
three consenting readers and one old window-only peer. No v86/public changes.
Tests bounded local repair with a remaining route, not disconnected bootstrap,
independent-WAN, consensus, 8k or resource/bandwidth plateau acceptance.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reader_source_support', ROOT/'scripts/hosted-peer-check.py')
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)
fixture, driver = support.fixture, support.driver


def run(network, participants=4, faults=False):
    assert participants in (4, 10)
    sessions, checks, f = [], [], None
    pins = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__), ROOT/'scripts/hosted-peer-page.mjs', *sorted(network.glob('*.mjs'))]}
    result = dict(status='FAIL', scope=__doc__, checks=checks, productionChanged=False, actualBrowsers=participants, actualV86Desktops=0, explicitSeedLinks=0)

    def js(browser, code, args=[]):
        return driver.call('/session/'+browser+'/execute/sync', {'script': code, 'args': args})

    def task(browser, code, args=[]):
        value = driver.call('/session/'+browser+'/execute/async', {'script': 'const params=arguments,done=params[params.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));', 'args': args})
        assert value['ok'], value
        return value.get('value')

    def wait(fn, seconds=45):
        return driver.wait(fn, seconds)

    def check(name, ok):
        assert ok, name
        checks.append(name)
        print(json.dumps({'check': name}), flush=True)

    def snap(browser, node=None):
        return js(browser, 'return client.snapshot(arguments[0]);', [node])

    def ready(browser):
        wait(lambda: js(browser, 'if(window.fixtureFatal)throw Error(fixtureFatal);return window.fixtureReady===true;'))
        js(browser, 'for(const method of ["offer","answer"]){const original=pool[method].bind(pool);pool[method]=async(...args)=>{const result=await original(...args),link=result.entry.link,send=link.sendHostedApplication.bind(link);link.sendHostedApplication=async(body,kind)=>{if(body.op?.startsWith("reader.")&&readerControls.length<256)readerControls.push({entryId:result.entry.id,body:structuredClone(body)});return send(body,kind);};return result;};}')

    def connect(a, b):
        offer = task(a, 'const r=await pool.offer();return {id:r.entry.id,token:r.token};')
        answer = task(b, 'const r=await pool.answer(params[0]);return {id:r.entry.id,token:r.token};', [offer['token']])
        task(a, 'await pool.accept(params[0],params[1]);return true;', [offer['id'], answer['token']])
        for browser, entry in [(a, offer['id']), (b, answer['id'])]:
            wait(lambda: js(browser, 'return pool.get(arguments[0]).link.hostedWindowReady;', [entry]))
        result['explicitSeedLinks'] += 1
        return offer['id'], answer['id']

    def pump(browser):
        js(browser, 'window.readerPump=setInterval(()=>client.tick(),1000);client.tick();')

    def peer_entry(browser, peer):
        return js(browser, 'return pool.list().find(e=>e.peerId===arguments[0]&&e.state==="ready")?.id||null;', [peer])

    def new_browser(origin, suffix):
        browser = driver.call('/session', {'capabilities': {'alwaysMatch': {'browserName': 'chrome', 'goog:chromeOptions': {'binary': '/snap/chromium/current/usr/lib/chromium-browser/chrome', 'args': ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage']}, 'goog:loggingPrefs': {'browser': 'ALL'}}}})['sessionId']
        sessions.append(browser)
        driver.call('/session/'+browser+'/timeouts', {'script': 120000})
        driver.call('/session/'+browser+'/url', {'url': origin+'/'+suffix})
        ready(browser)
        return browser

    try:
        with tempfile.TemporaryDirectory(prefix='codi-hosted-readers-') as directory:
            folder = Path(directory)
            f = fixture.Fixture(folder)
            f.clock.realtime = True
            public = folder/'public'
            shutil.copytree(network, public/'network', ignore=shutil.ignore_patterns('*.md'))
            shutil.copyfile(ROOT/'scripts/hosted-peer-page.mjs', public/'fixture.mjs')
            (public/'fixture-loader.mjs').write_text('import("/fixture.mjs").catch(e=>window.fixtureFatal=e.stack);')
            (public/'index.html').write_text('<!doctype html><title>Hosted reader organization</title><script type="module" src="/fixture-loader.mjs"></script>')
            config = f.issuer.config()
            config['hostedRooms'] = dict(version='codi-hosted-room/1', basePath='/rooms', controllerKey=f.store.public, certificatePath='/api/v1/room-control/controller', challengePath='/api/v1/room-control/challenge', authorizePath='/api/v1/room-control/authorize')
            (public/'fixture-config.json').write_text(json.dumps(config))
            for suffix in ['?owner=1&readers=1', '?readers=1', '?readers=1', '?window=1']:
                new_browser(f.origin, suffix)
            a, b, c, old = sessions
            identities = [js(s, 'return currentSession.public.sid;') for s in sessions]
            node = task(a, 'return await client.create("Automatically organized readers");')
            result['ownedRoom'] = node
            task(a, 'return await client.send(params[0],"Initial accepted reader state");', [node])
            ab, ba = connect(a, b)
            bc, cb = connect(b, c)
            ao, oa = connect(a, old)
            for browser in [b, c]:
                task(browser, 'await client.open(params[0]);return true;', [node])
            for browser in [a, b, c]:
                pump(browser)
            wait(lambda: peer_entry(a, identities[2]) and peer_entry(c, identities[0]))
            ac, ca = peer_entry(a, identities[2]), peer_entry(c, identities[0])
            check('three signed readers form the missing RTC edge from a two-edge chain without manual signaling', all(snap(s)['delivery']['readers']['connected'] >= 1 for s in [a, c]) and snap(b)['delivery']['readers']['relayed'] >= 2)
            check('automatic introduction and catch-up do not make hosted HTTP requests on either anonymous reader', all(js(s, 'return httpOperations.length===0;') for s in [b, c]))
            check('a connected window-only peer gets no unrequested room IDs and keeps its working link', not snap(old)['rooms'] and js(a, 'return readerControls.filter(v=>v.entryId===arguments[0]).every(v=>v.body.op==="reader.features")&&pool.get(arguments[0]).link.hostedWindowReady;', [ao]))
            stats = [snap(s)['delivery']['readers'] for s in [a, b, c]]
            check('reader organization stays inside the explicit neighbor, pending, cache and job bounds', all(len(v['members']) <= 6 and v['pending'] <= 4 and v['hintsPending'] <= 64 and v['jobs'] <= 16 and v['automaticConnections'] <= 8 for v in stats))
            # The only old peer ignores the in-band feature probe. Its existing
            # authenticated direct chat and old state-window application survive.
            task(old, 'await pool.get(params[0]).link.send("OLD_PEER_STILL_WORKS");return true;', [oa])
            wait(lambda: js(a, 'return directMessages.some(v=>v.text==="OLD_PEER_STILL_WORKS");'))
            check('an older peer remains usable after ignoring reader negotiation', True)
            # Mutate real signed introduction envelopes. Verification must reject
            # recipient, room, SDP and author proof changes, without affecting RTC.
            intro = js(b, 'return readerControls.find(v=>v.body.op==="reader.forward-offer").body;')
            result['introductionNegativeControls'] = task(b, '''
              const {verifyReaderIntroduction}=await import("./network/hosted-reader-peers.mjs");
              const {inspectJws}=await import("./network/crypto.mjs");
              const body=params[0],p=inspectJws(body.presence,"codi-hosted-reader+jws").payload;
              const room={id:body.node,descriptorHash:p.descriptor_hash};const out=[];
              await verifyReaderIntroduction(body,room,config.identity,"offer");
              for(const [name,change] of [["recipient",b=>b.to="wrong-recipient"],["room",b=>b.node="a".repeat(43)],["signal",b=>b.signal=b.signal.slice(0,-1)+(b.signal.endsWith("A")?"B":"A")],["proof",b=>b.proof=b.proof.slice(0,-2)+"aa"]]){
                const b=structuredClone(body);change(b);try{await verifyReaderIntroduction(b,room,config.identity,"offer");out.push({name,rejected:false});}catch{out.push({name,rejected:true});}
              }return out;''', [intro])
            check('recipient, room, SDP hash and signature mutations are all rejected', all(v['rejected'] for v in result['introductionNegativeControls']))
            # Replay a real forwarded offer through its original live route.
            target = a if intro['to'] == identities[0] else c
            target_relay = ab if target == a else cb
            rejected = snap(target)['delivery']['readers']['rejected']
            replay = task(target, 'return await client.receivePeer(pool.get(params[0]),{mode:"hosted-checkpoint/1",type:"sync",body:params[1]});', [target_relay, intro])
            check('a completed introduction cannot be replayed and its established path remains available', replay is False and snap(target)['delivery']['readers']['rejected'] > rejected and peer_entry(a, identities[2]) == ac)
            # Retire the original intermediary completely, not merely a mocked
            # routing table. The newly introduced RTC edge must carry the update.
            task(b, 'clearInterval(readerPump);await client.close();pool.close();return true;')
            before = js(c, 'return httpOperations.length;')
            task(a, 'return await client.send(params[0],"Accepted after the intermediary left");', [node])
            wait(lambda: snap(c, node)['selected']['count'] == 2)
            check('accepted updates survive loss of the seed intermediary over the new direct path', snap(c, node)['selected']['source'] == 'peer' and js(c, 'return httpOperations.length;') == before)
            # Rejoin with a genuinely new issuer session, one explicit seed edge,
            # and the retained IndexedDB floor. The second edge is automatic.
            driver.call('/session/'+b+'/refresh', {})
            ready(b)
            rejoined = js(b, 'return currentSession.public.sid;')
            assert rejoined != identities[1]
            ab2, ba2 = connect(a, b)
            task(b, 'await client.open(params[0]);return true;', [node])
            pump(b)
            wait(lambda: peer_entry(b, identities[2]) and peer_entry(c, rejoined))
            check('a fresh rejoining identity discovers another reader from a single surviving seed', snap(b, node)['selected']['count'] == 2 and js(b, 'return httpOperations.length===0;') and peer_entry(a, identities[2]) == ac)
            task(a, 'return await client.send(params[0],"Accepted after rejoin");', [node])
            wait(lambda: all(snap(s, node)['selected']['count'] == 3 for s in [b, c]))
            check('all current readers converge to the same accepted head after rejoin', all(snap(s, node)['selected']['source'] == 'peer' for s in [b, c]))
            if participants == 10:
                extras, previous = [], c
                for _ in range(6):
                    browser = new_browser(f.origin, '?readers=1')
                    extras.append(browser)
                    connect(previous, browser)
                    task(browser, 'await client.open(params[0]);return true;', [node])
                    pump(browser)
                    previous = browser
                readers = [a, b, c, *extras]
                victim = extras[2]
                reader_ids = {s: js(s, 'return currentSession.public.sid;') for s in readers}

                def has_surviving_route():
                    graph = {reader_ids[s]: {e['peerId'] for e in js(s, 'return pool.list().filter(e=>e.state==="ready");')} for s in readers if s != victim}
                    seen, queue = set(), [reader_ids[a]]
                    while queue:
                        sid = queue.pop()
                        if sid in seen or sid not in graph:
                            continue
                        seen.add(sid)
                        queue.extend(graph[sid]-seen)
                    return len(seen) == len(graph)

                # At least three independently introduced new edges beyond the
                # original triangle, with real signaling/data channels only.
                wait(lambda: sum(snap(s)['delivery']['readers']['connected'] for s in readers) >= 10, 60)
                # This increment repairs over a remaining signaling path; full
                # disconnected-component bootstrap is explicitly not implemented.
                # Observe a redundant path before removing the seed intermediary.
                wait(has_surviving_route, 60)
                before_stats = [snap(s)['delivery']['readers'] for s in readers]
                check('nine consenting readers add redundant RTC edges beyond the explicit seed chain', all(len(v['members']) <= 6 and v['pending'] <= 4 and v['automaticConnections'] <= 8 for v in before_stats))
                result['largerGroupBeforeFailure'] = before_stats
                task(victim, 'clearInterval(readerPump);await client.close();pool.close();return true;')
                survivors = [s for s in readers if s != victim]
                before_http = {s: js(s, 'return httpOperations.length;') for s in survivors}
                began = time.monotonic()
                task(a, 'return await client.send(params[0],"Accepted after a larger-group intermediary left");', [node])
                wait(lambda: all(snap(s, node)['selected']['count'] == 4 for s in survivors), 25)
                result['largerGroupConvergenceSeconds'] = round(time.monotonic()-began, 3)
                check('the larger group propagates an accepted update after an interior seed node leaves', all(snap(s, node)['selected']['source'] == 'peer' for s in survivors if s != a))
                result['largerGroupHTTPDelta'] = [js(s, 'return httpOperations.length;')-before_http[s] for s in survivors if s != a]
                check('surviving larger-group readers catch up through RTC without hosted server reads', all(v == 0 for v in result['largerGroupHTTPDelta']))
                check('the unrelated legacy peer remains available during larger-group churn', js(a, 'return pool.get(arguments[0]).link.hostedWindowReady;', [ao]))
            result['organizationStats'] = [snap(s)['delivery']['readers'] for s in [a, b, c]]
            if faults:
                assert participants == 4
                # Five additional real issuer identities/RTC offerers in the old
                # peer's browser. Their signed introductions are relayed over the
                # existing authenticated A->C channel; answers are deliberately
                # not delivered back. This exercises actual pending PC custody.
                js(c, 'clearInterval(readerPump);')
                baseline = js(c, 'return {ids:pool.list().filter(e=>e.state==="ready").map(e=>e.id),stats:client.snapshot().delivery.readers};')
                descriptor = js(a, 'return readerControls.find(v=>v.body.node===arguments[0]&&v.body.descriptor_hash).body.descriptor_hash;', [node])
                target_id = js(c, 'return currentSession.public.sid;')
                js(old, 'window.faultActors=[];')
                pending_ids = []
                for number in range(5):
                    body = task(old, '''
                      const {makeKey,signJws,hash,b64}=await import("./network/crypto.mjs");
                      const {authenticatedRequest,verifyIdentity}=await import("./network/identity.mjs");
                      const {PeerPool}=await import("./network/peer-pool.mjs");
                      const keys=await makeKey(),session={privateKey:keys.privateKey,public:{sid:crypto.randomUUID(),key:keys.publicKey}};
                      const issued=await authenticatedRequest(config.identity,session,config.identity.apiBase+"/anonymous",{});
                      session.public=issued.identity;session.token=issued.session_token;session.trust=await verifyIdentity(session.public,config.identity);
                      const peers=new PeerPool(session,config,{hostedWindow:true,onHostedApplication:()=>false});faultActors.push({session,peers});
                      const offer=await peers.offer(),t=Math.floor(Date.now()/1000),request=b64(crypto.getRandomValues(new Uint8Array(32)));
                      const presence=await signJws({version:"codi-hosted-readers/1",node_id:params[0],descriptor_hash:params[1],reader:session.public.sid,iat:t,exp:t+90},session.privateKey,"codi-hosted-reader+jws");
                      const proof=await signJws({version:"codi-hosted-readers/1",node_id:params[0],descriptor_hash:params[1],request_id:request,kind:"offer",from:session.public.sid,to:params[2],signal_sha256:await hash(offer.token),iat:t,exp:t+30},session.privateKey,"codi-hosted-introduction+jws");
                      return {op:"reader.forward-offer",node:params[0],descriptor_hash:params[1],request_id:request,to:params[2],signal:offer.token,presence,proof};
                    ''', [node, descriptor, target_id])
                    before_rejected = snap(c)['delivery']['readers']['rejected']
                    before_entries = js(c, 'return pool.list().length;')
                    task(a, 'await pool.get(params[0]).link.sendHostedApplication(params[1]);return true;', [ac, body])
                    if number < 4:
                        wait(lambda: snap(c)['delivery']['readers']['pending'] == number+1)
                        wait(lambda: js(c, 'return pool.list().filter(e=>e.state!=="ready"&&!pool.get(e.id).link.closed).length===arguments[0];', [number+1]))
                        pending_ids = js(c, 'return pool.list().filter(e=>e.state!=="ready"&&!pool.get(e.id).link.closed).map(e=>e.id);')
                    else:
                        wait(lambda: snap(c)['delivery']['readers']['rejected'] > before_rejected)
                        check('a fifth valid introduction is refused before allocating another RTC connection', js(c, 'return client.snapshot().delivery.readers.pending===4&&pool.list().length===arguments[0];', [before_entries]))
                    time.sleep(1.1)
                check('four unfinished introductions retain only their bounded pending jobs', len(pending_ids) == 4 and js(c, 'return pool.list().filter(e=>e.state==="ready").map(e=>e.id).sort().join()===arguments[0].sort().join();', [baseline['ids']]))
                wait(lambda: snap(c)['delivery']['readers']['answered'] >= baseline['stats']['answered']+4)
                task(c, 'await client.close();return true;')
                check('retiring the reader service closes all of its new pending PCs and preserves existing links', js(c, 'return arguments[0].every(id=>pool.get(id).link.closed)&&arguments[1].every(id=>pool.get(id).link.hostedWindowReady)&&client.snapshot().delivery.readers.pending===0&&client.snapshot().delivery.readers.jobs===0;', [pending_ids, baseline['ids']]))
                task(c, 'await pool.get(params[0]).link.send("DIRECT_AFTER_PENDING_READER_RETIREMENT");return true;', [ca])
                wait(lambda: js(a, 'return directMessages.some(v=>v.text==="DIRECT_AFTER_PENDING_READER_RETIREMENT");'))
                check('unrelated authenticated direct chat survives pending capacity refusal and service retirement', True)
                result['pendingIntroductionFaults'] = dict(realAdditionalIssuerIdentities=5, actualAdditionalRTCOfferers=5, acceptedPending=4, refusedBeforePCAllocation=1, preservedReadyConnections=len(baseline['ids']))
            cleanup = []
            for browser in sessions:
                task(browser, 'clearInterval(window.readerPump);await client.close();pool.close();for(const actor of window.faultActors||[])actor.peers.close();return true;')
                wait(lambda: js(browser, 'return pool.list().length===0&&client.snapshot().delivery.peer.pending===0&&client.snapshot().delivery.peer.serving===0;'))
                wait(lambda: js(browser, 'return client.snapshot().delivery.readers?.jobs===0||client.snapshot().delivery.readers===null;'))
                cleanup.append(task(browser, 'const {sessionBudget}=await import("./network/resource-budget.mjs");return sessionBudget(currentSession).snapshot();'))
            if faults:
                extra_cleanup = task(old, 'const {sessionBudget}=await import("./network/resource-budget.mjs");return faultActors.map(actor=>sessionBudget(actor.session).snapshot());')
                check('all additional offerer identities release their real RTC and accounting resources', all(not any(v for k, v in value.items() if k != 'closed') for value in extra_cleanup))
                result['extraActorCleanup'] = extra_cleanup
            check('closing every reader releases all session-accounted resources', all(not any(v for k, v in value.items() if k != 'closed') for value in cleanup))
            result.update(status='PASS', resourceCleanup=cleanup, fullyDisconnectedBootstrapImplemented=False, fullGoalComplete=False)
    except Exception as error:
        result.update(error=str(error), traceback=traceback.format_exc(), diagnostics=[])
        for browser in sessions:
            try:
                result['diagnostics'].append({'state': js(browser, 'return {ready:window.fixtureReady,fatal:window.fixtureFatal,state:window.client?.snapshot(arguments[0]),peers:window.pool?.list(),controls:window.readerControls?.slice(-8),http:window.httpOperations?.slice(-10)};', [result.get('ownedRoom')]), 'logs': driver.call('/session/'+browser+'/log', {'type': 'browser'})})
            except Exception as diagnostic_error:
                result['diagnostics'].append({'error': str(diagnostic_error)})
    finally:
        for browser in sessions:
            try:
                driver.call('/session/'+browser, method='DELETE')
            except Exception as error:
                result.setdefault('cleanupErrors', []).append(str(error))
                result['status'] = 'FAIL'
        result['ownedBrowserContextsClosed'] = len(sessions)
        if f:
            f.close()
    result.update(sourceSHA256=pins, sourceChangedDuringTest=any(hashlib.sha256(Path(name).read_bytes()).hexdigest() != pin for name, pin in pins.items()))
    if result['sourceChangedDuringTest']:
        result['status'] = 'FAIL'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--network-root', type=Path, default=ROOT/'network')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--participants', type=int, choices=[4, 10], default=4)
    parser.add_argument('--faults', action='store_true')
    args = parser.parse_args()
    assert not args.output.exists()
    value = run(args.network_root.resolve(), args.participants, args.faults)
    args.output.write_text(json.dumps(value, indent=2)+'\n')
    print(json.dumps({'status': value['status'], 'checks': len(value['checks']), 'error': value.get('error')}))
    raise SystemExit(0 if value['status'] == 'PASS' else 1)
