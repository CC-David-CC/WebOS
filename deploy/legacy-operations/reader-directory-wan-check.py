#!/usr/bin/env python3
"""Zero-seed and complete-cut recovery between Linux desktops across two public IPs.

Three owned full-v86 Chrome contexts: two local, one on Moonpie. Tailscale
only controls WebDriver; the site uses ordinary HTTPS and TURN/TLS443. No
certificate bypass, synthetic SDP, protocol timing/expiry/capacity override or8k
claim. Cold Linux readiness uses a measured, bounded180s startup allowance.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


suite = module('wan_readers_installed', ROOT/'scripts/reader-directory-native-check.py')
public = module('wan_readers_public', ROOT/'scripts/hosted-peer-public-check.py')
wire = module('wan_readers_wire', ROOT/'scripts/hosted-peer-window-wan-check.py')


def run(release):
    fixture = json.loads((ROOT/'.build/checks/moonpie-browser-fixture.json').read_bytes())
    assert fixture['sshTarget'] == 'maint@100.105.243.29' and not fixture['driverStopped'] and not fixture['fixtureFolderRemoved']
    local_ip = subprocess.check_output(['curl', '--noproxy', '*', '-fsS', '--max-time', '15', 'https://api.ipify.org'], text=True, timeout=20).strip()
    outside_ip = subprocess.check_output(['ssh', '-o', 'BatchMode=yes', fixture['sshTarget'], 'curl --noproxy "*" -fsS --max-time 15 https://api.ipify.org'], text=True, timeout=25).strip()
    assert local_ip != outside_ip
    endpoints, closed = {}, set()
    counter = 0

    def routed_call(path, data=None, method=None):
        nonlocal counter
        if path == '/session':
            remote = counter == 2
            assert counter < 3
            counter += 1
            caps = data['capabilities']['alwaysMatch']
            args = caps['goog:chromeOptions']['args']
            marker = '--ignore-certificate-errors-spki-list='+public.MARKER
            assert args.count(marker) == 1
            args.remove(marker)
            assert not any('ignore-certificate' in value for value in args)
            caps['acceptInsecureCerts'] = False
            args.append('--no-proxy-server')
            if remote:
                args.append('--user-data-dir='+fixture['folder']+'/readers-'+str(time.time_ns()))
            endpoint = fixture['localDriverURL'] if remote else 'http://127.0.0.1:19515'
            value = wire.request(endpoint, path, data, method)
            endpoints[value['sessionId']] = endpoint
            return value
        assert path.startswith('/session/')
        browser = path.split('/')[2]
        # Bound the test control channel separately from the application's
        # protocol/guest deadlines. An offline jump box must not mask cleanup.
        timeout=15 if method=='DELETE' else 120 if path.endswith('/execute/async') else 180 if path.endswith('/url') else 30
        value = wire.request(endpoints[browser], path, data, method,timeout=timeout)
        if method == 'DELETE' and path == '/session/'+browser:
            closed.add(browser)
        return value

    suite.driver.call = routed_call
    suite.vm.remote = public.public_remote

    def prepare(browser):
        routed_call('/session/'+browser+'/execute/sync', {'script': 'identityConfig.rtc.preference.preferred="relay";return true;', 'args': []})
        value = routed_call('/session/'+browser+'/execute/async', {'script': 'const done=arguments[0];changeAccount("anonymous").then(()=>done({ok:true}),error=>done({ok:false,error:error.stack}));', 'args': []})
        assert value['ok'], value

    def inspect(links):
        out = []
        for browser, entry in links:
            value = routed_call('/session/'+browser+'/execute/async', {'script': '''const id=arguments[0],done=arguments[1];(async()=>{
const e=desktopNetwork.appContext().pool.get(id),report=await e.link.pc.getStats(),pairs=[];
for(const t of report.values())if(t.type==='transport'&&t.selectedCandidatePairId){const p=report.get(t.selectedCandidatePairId),l=report.get(p.localCandidateId),r=report.get(p.remoteCandidateId);pairs.push({state:e.link.pc.connectionState,localType:l?.candidateType,remoteType:r?.candidateType,relayProtocol:l?.relayProtocol,turnURL:l?.url,bytesSent:p.bytesSent,bytesReceived:p.bytesReceived});}return pairs;
})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));''', 'args': [entry]})
            assert value['ok'], value
            out.append({'endpoint': 'moonpie' if endpoints[browser] == fixture['localDriverURL'] else 'development', 'pairs': value['value']})
        return out

    value = suite.run(release, prepare_browser=prepare, inspect_link=inspect)
    pairs = [p for key in ['introducedLinkEvidence','repairedLinkEvidence'] for endpoint in value.get(key, []) for p in endpoint['pairs']]
    if value['status'] == 'PASS':
        assert len(pairs) == 4 and all(p['state'] == 'connected' and p['localType'] == p['remoteType'] == 'relay' and p['relayProtocol'] == 'tls' and p['turnURL'].startswith('turns:turn.ksu.codes:443') for p in pairs), pairs
        value['checks'].append('both ends of initial and repaired zero-seed WAN links select actual public TURN TLS443')
    if len(closed)!=counter:
        value['status']='FAIL'
        value.setdefault('cleanupErrors',[]).append({'stage':'WAN-contexts','error':'Owned outside context cleanup remains unverified; reconcile the saved fixture before another run'})
    value.update(scope=__doc__, defaultPublicTLS=True, fixtureSPKIOnly=False, publicWANTested=value['status'] == 'PASS', publicIPs={'development': local_ip, 'moonpie': outside_ip}, actualBrowsers=counter, ownedBrowserContextsClosed=len(closed), productionDeploymentChanged=False, fullGoalComplete=False, wrapperSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    try:
        value = run(args.release.resolve())
    except Exception as error:
        import traceback
        value = dict(status='FAIL', error=str(error), traceback=traceback.format_exc(), fullGoalComplete=False)
    args.output.write_text(json.dumps(value, indent=2)+'\n')
    print(json.dumps({k: value.get(k) for k in ['status', 'error', 'checks', 'publicWANTested']}))
    raise SystemExit(0 if value['status'] == 'PASS' else 1)
