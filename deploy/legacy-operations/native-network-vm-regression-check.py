#!/usr/bin/env python3
"""Actual voice or RTC/chat/chess regression on the existing private native VM.

Only the disposable VM's public certificate is copied. No service keys, real
account data, public-site TLS bypass or host firewall change is involved.
"""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
CHECKS = ROOT / '.build/checks'
spec = importlib.util.spec_from_file_location('vm_candidate', ROOT / 'scripts/upgrade-native-network-vm.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(kind):
    candidate.vm.status()
    before = candidate.runtime()
    assert before['version'] == 'codi-managed-instance/5'
    assert before['clientSHA256'] == sha(ROOT / 'guest_service/client.mjs')
    assert before['appSHA256'] == sha(ROOT / 'app.js')
    installed = json.loads(candidate.remote('cat /srv/codi-network-fixture/installed-result.json'))
    certificate = candidate.vm.FOLDER / 'public-cert.pem'
    certificate.write_text(candidate.remote('cat /etc/codi-fixture-tls/cert.pem'))
    pub = subprocess.run(['openssl', 'x509', '-in', str(certificate), '-pubkey', '-noout'], check=True, capture_output=True).stdout
    der = subprocess.run(['openssl', 'pkey', '-pubin', '-outform', 'DER'], input=pub, check=True, capture_output=True).stdout
    assert base64.b64encode(hashlib.sha256(der).digest()).decode() == installed['fixtureSPKI']
    spki = candidate.vm.FOLDER / 'public-spki.txt'
    spki.write_text(installed['fixtureSPKI'] + '\n')
    url = installed['publicOrigin'] + '/hidden/'
    if kind == 'voice':
        argv = ['scripts/general-voice-check.py', '--url', url, '--fixture-spki-file', str(spki), '--fixture-ca-file', str(certificate)]
        result_path = CHECKS / 'general-voice-fixture-result.json'
    else:
        argv = ['scripts/tls-discovery-check.py', '--url', url, '--spki-file', str(spki), '--ca-file', str(certificate), '--require-trust', 'test-server', '--read-only-operator', '--expect-direct']
        result_path = CHECKS / 'tls-discovery-result.json'
        if result_path.exists():
            result_path.rename(result_path.with_name('tls-discovery-before-vm-' + str(time.time_ns()) + '.json'))
    started = time.time_ns()
    log = CHECKS / ('native-network-vm-' + kind + '-run.log')
    print(json.dumps({'check': kind, 'status': 'running', 'manifestSHA256': before['manifestSHA256'], 'log': str(log)}), flush=True)
    with log.open('w') as output:
        subprocess.run([sys.executable, '-B', *argv], cwd=ROOT, stdout=output, stderr=subprocess.STDOUT, check=True, timeout=900)
    assert result_path.stat().st_mtime_ns >= started
    proof = json.loads(result_path.read_text())
    assert proof['status'] == 'PASS' and proof['url'] == url
    if kind == 'voice':
        assert proof['fixtureCertificatePinUsed'] and proof['actualLocalWhisperWasmInference']
        assert proof['dictationTargetsIndependentShell'] and not proof['audioUploaded']
        assert proof['httpWritesDuringVoiceAndAppChecks'] == []
        assert proof['servedAssetsSHA256']['app.js'] == before['appSHA256']
    else:
        assert not proof['defaultCertificateTrust'] and proof['bidirectionalRTC']
        assert proof['separateRoomChatAndMoves'] and proof['pgnExportMatchesAcrossPeersAndExcludesChat']
        assert proof['rtcSurvivesWssStop'] and proof['guestAndIdentityPreserved']
        assert proof['directCandidatesRequired'] and all(proof['disposed'])
        assert proof['servedAssetsSHA256']['app.js'] == before['appSHA256']
    after = candidate.runtime()
    assert before == after, 'Regression must retain the exact installed native release and processes'
    return {'status': 'PASS', 'scope': __doc__, 'kind': kind, 'executedRuntime': before,
            'proof': proof, 'fixturePublicCertificateSHA256': sha(certificate),
            'nativeProcessesUnchanged': True, 'liveWebhostChanged': False,
            'hostFirewallChanged': False, 'publicDefaultTLSVerified': False,
            'independentWANVerified': False, 'physicalAndroidVerified': False}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', required=True, choices=['voice', 'rtc'])
    args = parser.parse_args()
    value = {'status': 'FAIL', 'kind': args.check, 'scope': __doc__}
    try:
        value.update(run(args.check))
    finally:
        names = ['scripts/native-network-vm-regression-check.py', 'scripts/upgrade-native-network-vm.py', 'scripts/general-voice-check.py' if args.check == 'voice' else 'scripts/tls-discovery-check.py', 'app.js', 'guest_service/client.mjs']
        value['sha256'] = {name: sha(ROOT / name) for name in names}
        output = CHECKS / ('native-network-vm-' + args.check + '-result.json')
        if output.exists():
            output.rename(output.with_name(output.stem + '-before-' + str(time.time_ns()) + '.json'))
        output.write_text(json.dumps(value, indent=2) + '\n')
        print(json.dumps(value, indent=2))
