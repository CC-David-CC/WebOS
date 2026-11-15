#!/usr/bin/env python3
"""Real Chrome microphone-file capture and local Whisper inference, fresh tab."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
DRIVER = 'http://127.0.0.1:19515'
spec = importlib.util.spec_from_file_location('speech_static', ROOT / 'serve.py')
static = importlib.util.module_from_spec(spec)
spec.loader.exec_module(static)
CSP = "default-src 'none'; script-src 'self' 'wasm-unsafe-eval'; connect-src 'self' wss://ksu.codes; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; worker-src 'self' blob:; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
requests = []
class Handler(static.PublicHandler):
    def do_GET(self):
        requests.append({'method': 'GET', 'path': self.path})
        super().do_GET()
    def do_POST(self):
        requests.append({'method': 'POST', 'path': self.path})
        self.send_error(405)
    def end_headers(self):
        self.send_header('Content-Security-Policy', CSP)
        super().end_headers()
    def log_message(self, *args):
        pass

def call(path, data=None, method=None):
    req = urllib.request.Request(DRIVER + path, data=None if data is None else json.dumps(data).encode(), headers={'Content-Type': 'application/json'}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.load(response)['value']
    except Exception as error:
        if hasattr(error, 'read'):
            raise RuntimeError(error.read().decode()) from error
        raise

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url')
parser.add_argument('--gpu-available', action='store_true', help='Expose a GPU adapter while verifying speech stays on WASM')
args = parser.parse_args()
server = None
sid = None
result = {'status': 'FAIL'}
try:
    if args.url:
        url = args.url
    else:
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = 'http://127.0.0.1:' + str(server.server_port) + '/'
    sid = call('/session', {'capabilities': {'alwaysMatch': {'browserName': 'chrome', 'goog:chromeOptions': {'binary': '/snap/chromium/current/usr/lib/chromium-browser/chrome', 'args': ['--headless=new', *(['--enable-unsafe-webgpu', '--use-angle=swiftshader'] if args.gpu_available else []), '--no-sandbox', '--disable-dev-shm-usage', '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream', '--use-file-for-fake-audio-capture=' + str(ROOT / '.build/checks/speech-fixture.wav')]}, 'goog:loggingPrefs': {'browser': 'ALL', 'performance': 'ALL'}}}})['sessionId']
    def js(code):
        return call('/session/' + sid + '/execute/sync', {'script': code, 'args': []})
    def wait(code, seconds=90, allow_error=False):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            error = js('return document.querySelector("[aria-label=\\"Voice to text\\"]")?.dataset.error')
            if error and not allow_error:
                raise AssertionError(error)
            value = js(code)
            if value:
                return value
            time.sleep(.2)
        raise AssertionError('Timed out: ' + str(js('return {status:document.querySelector("[aria-label=\\"Voice to text\\"]")?.title,feedback:document.querySelector("#feedback")?.textContent}')))
    call('/session/' + sid + '/goog/cdp/execute', {'cmd': 'Page.addScriptToEvaluateOnNewDocument', 'params': {'source': '''window.__gpuReads=0;const gpu=navigator.gpu;Object.defineProperty(navigator,"gpu",{get:()=>{__gpuReads++;return gpu}});window.__speechMessages=[];const NativeWorker=window.Worker;window.Worker=class extends NativeWorker{constructor(...args){super(...args);this.addEventListener('message',event=>__speechMessages.push({type:event.data.type,device:event.data.device}));}postMessage(message,...rest){if(window.__holdTranscription&&message.type==='transcribe'){window.__heldTranscription=true;return;}super.postMessage(message,...rest);}};'''}})
    call('/session/' + sid + '/url', {'url': url})
    wait('return window.desktopLab?.guestState==="ready"')
    wait('return window.desktopLab?.session?.id')
    call('/session/' + sid + '/log', {'type': 'performance'})
    assert js('return !document.querySelector(".terminal-touchkeys [aria-label=\\"↑\\"]")&&!document.querySelector(".terminal-menu [aria-label=Help]")&&!!document.querySelector(".terminal-touchkeys [aria-label=Enter]")')
    js('window.__streams=[];window.__getAudio=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);navigator.mediaDevices.getUserMedia=async options=>{const stream=await __getAudio(options);__streams.push(stream);return stream};window.__sent=[];window.__original=v86Instance.serial0_send;v86Instance.serial0_send=text=>{__sent.push(text);__original.call(v86Instance,text)};document.querySelector("[aria-label=\\"Voice to text\\"]").click()')
    wait('return document.querySelector("[aria-label=\\"Voice to text\\"]").title.startsWith("Loading")')
    js('document.querySelector("[aria-label=\\"Voice to text\\"]").click()')
    wait('return document.querySelector("[aria-label=\\"Voice to text\\"]").getAttribute("aria-pressed")==="false"')
    assert js(r'return __streams.length===0&&__sent.every(text=>/^\x1b\[[0-9;?]*[A-Za-z]$/.test(text))'), js('return {streams:__streams.length,sent:__sent}')
    js('document.querySelector("[aria-label=\\"Voice to text\\"]").click()')
    wait('return document.querySelector("[aria-label=\\"Voice to text\\"]").title.startsWith("Listening")', 180)
    print('Recording fixture through real getUserMedia/MediaRecorder', flush=True)
    time.sleep(11)
    js('document.querySelector("[aria-label=\\"Voice to text\\"]").click()')
    text = wait('return __sent.find(text=>/fellow|country|Americans/i.test(text))', 120)
    result['speechText'] = text
    assert not any('\r' in value or '\n' in value for value in js('return __sent'))
    assert js('return __streams.every(stream=>stream.getTracks().every(track=>track.readyState==="ended"))')
    sent = js('const before=__sent.length;document.querySelector(".terminal-touchkeys [aria-label=Enter]").click();return __sent.slice(before)')
    assert sent[0] == '\r', sent
    assert js('return __gpuReads===0&&__speechMessages.some(message=>message.type==="ready"&&message.device==="wasm")&&__speechMessages.some(message=>message.type==="result"&&message.device==="wasm")')
    # Exercise the actual result insertion boundary with the exact reported loop.
    js("window.__guard=null;import(new URL('assets/speech/client.mjs',document.baseURI)).then(module=>{const rejected=[];for(const value of ['biasesVIDEO '.repeat(20),'proc bicy at fair twilight '+'biasesVIDEO '.repeat(20),'abc'.repeat(30)]){try{module.cleanTranscript(value);rejected.push(false)}catch{rejected.push(true)}}__guard={rejected,clean:module.cleanTranscript('ping\\n1.1.1.1')}})")
    wait('return window.__guard')
    assert js('return __guard.rejected.every(Boolean)&&__guard.clean==="ping 1.1.1.1"')
    js('window.__holdTranscription=true;window.__heldTranscription=false;document.querySelector("[aria-label=\\"Voice to text\\"]").click()')
    wait('return document.querySelector("[aria-label=\\"Voice to text\\"]").title.startsWith("Listening")')
    time.sleep(2)
    js('document.querySelector("[aria-label=\\"Voice to text\\"]").click()')
    wait('return __heldTranscription')
    before_cancel = js('return __sent.length')
    js('document.querySelector("[aria-label=\\"Voice to text\\"]").click()')
    wait('return document.querySelector("[aria-label=\\"Voice to text\\"]").getAttribute("aria-pressed")==="false"')
    assert js('return __streams.every(stream=>stream.getTracks().every(track=>track.readyState==="ended"))')
    assert js('return __sent.length') == before_cancel
    js('window.__holdTranscription=false')
    js('navigator.mediaDevices.getUserMedia=()=>Promise.reject(new DOMException("permission denied","NotAllowedError"));document.querySelector("[aria-label=\\"Voice to text\\"]").click()')
    wait('return document.querySelector("[aria-label=\\"Voice to text\\"]").dataset.error', allow_error=True)
    assert js('return document.querySelector("#feedback").textContent.includes("permission was not granted")')
    js('navigator.mediaDevices.getUserMedia=async options=>{const stream=await __getAudio(options);__streams.push(stream);return stream};document.querySelector("[aria-label=\\"Voice to text\\"]").click()')
    wait('return document.querySelector("[aria-label=\\"Voice to text\\"]").title.startsWith("Listening")')
    js('document.querySelector(".window.focused [aria-label=Close]").click()')
    wait('return __streams.at(-1).getTracks().every(track=>track.readyState==="ended")')
    logs = call('/session/' + sid + '/log', {'type': 'browser'})
    assert not [entry for entry in logs if entry['level'] == 'SEVERE'], logs
    events = [json.loads(entry['message'])['message'] for entry in call('/session/' + sid + '/log', {'type': 'performance'})]
    net = [entry['params']['request'] for entry in events if entry['method'] == 'Network.requestWillBeSent']
    parsed=urlsplit(url);origin=parsed.scheme+'://'+parsed.netloc
    safe=lambda item:item['method'] in ('GET','HEAD') and (item['url'].startswith(url) or item['url'].startswith('blob:'+origin+'/'))
    assert all(safe(item) for item in net), [(item['method'], item['url']) for item in net if not safe(item)]
    result.update(status='PASS', url=url, actualMicrophoneApiAndRecorder=True, actualLocalWhisperWasmInference=True, gpuExposedByBrowser=args.gpu_available, speechNeverReadsGpuAdapter=True, repeatedTranscriptRejected=True, cancelDuringModelLoadNeverOpensMicrophone=True, cancelDuringPendingTranscriptionNeverInserts=True, speechText=text, transcriptDoesNotExecute=True, enterButtonSendsCarriageReturn=True, allObservedSpeechRequestsSameOriginReadOnly=True, recordingTracksStoppedAfterTranscription=True, permissionDeniedUiHandled=True, closingTerminalStopsRecording=True, pageCspMatchesPublicPreview=True, audioUploaded=False, physicalMicrophoneNotTested=True)
except BaseException as error:
    result['error'] = type(error).__name__ + ': ' + str(error)
    if sid:
        result['browserLog'] = call('/session/' + sid + '/log', {'type': 'browser'})
    raise
finally:
    if sid:
        call('/session/' + sid, method='DELETE')
    if server:
        server.shutdown()
        server.server_close()
    result['sha256'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ['app.js', 'style.css', 'terminal.js', 'assets/speech/client.mjs', 'assets/speech/worker.mjs', 'scripts/speech-check.py']}
    (ROOT / '.build/checks' / ('speech-public-result.json' if args.url else 'speech-result.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
