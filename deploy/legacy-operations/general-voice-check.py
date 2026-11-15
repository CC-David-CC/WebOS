#!/usr/bin/env python3
"""Actual tap voice, movable overlay, keyboard policy and app/workspace tests."""
import argparse
import hashlib
import importlib.util
import json
import ssl
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
parser.add_argument('--fixture-spki-file', type=Path)
parser.add_argument('--fixture-ca-file', type=Path)
parser.add_argument('--release-dir', type=Path, help='Compare served assets with this sealed release and its active graph')
args = parser.parse_args()
if bool(args.fixture_spki_file) != bool(args.fixture_ca_file):
    parser.error('Fixture certificate and SPKI files must be paired')
if args.fixture_spki_file and (not args.url or urlsplit(args.url).scheme != 'https' or urlsplit(args.url).hostname != '127.0.0.1'):
    parser.error('Certificate exceptions are restricted to a disposable loopback fixture')
if args.release_dir and not args.url:
    parser.error('A sealed release comparison requires an explicit URL')
server = sid = None
result = {'status': 'FAIL', 'fixtureCertificatePinUsed': bool(args.fixture_spki_file)}
try:
    if args.url:
        url = args.url
    else:
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/'
    chrome_args = ['--headless=new', '--enable-unsafe-webgpu', '--use-angle=swiftshader', '--no-sandbox', '--disable-dev-shm-usage', '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream', '--use-file-for-fake-audio-capture=' + str(ROOT / '.build/checks/speech-fixture.wav')]
    if args.fixture_spki_file:
        chrome_args.append('--ignore-certificate-errors-spki-list=' + args.fixture_spki_file.read_text().strip())
    sid = call('/session', {'capabilities': {'alwaysMatch': {'browserName': 'chrome', 'goog:chromeOptions': {'binary': '/snap/chromium/current/usr/lib/chromium-browser/chrome', 'args': chrome_args}, 'goog:loggingPrefs': {'browser': 'ALL', 'performance': 'ALL'}}}})['sessionId']
    def js(script):
        return call(f'/session/{sid}/execute/sync', {'script': script, 'args': []})
    def cdp(cmd, params):
        return call(f'/session/{sid}/goog/cdp/execute', {'cmd': cmd, 'params': params})
    def wait(script, seconds=120, allow_error=False):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            state = js('return {error:document.querySelector(".voice-button")?.dataset.error,note:document.querySelector(".voice-note")?.textContent}')
            if state['error'] and not allow_error:
                raise AssertionError(state)
            value = js(script)
            if value:
                return value
            time.sleep(.15)
        raise AssertionError(('Timed out', script, state))
    def press():
        point = js('const r=document.querySelector(".voice-button").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}')
        cdp('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [point]})
        time.sleep(.06)
        cdp('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    def release():
        press()
    preload = '''window.__streams=[];const gum=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);navigator.mediaDevices.getUserMedia=async options=>{const stream=await gum(options);__streams.push(stream);return stream};window.__gpuReads=0;const gpu=navigator.gpu;Object.defineProperty(navigator,'gpu',{get:()=>{__gpuReads++;return gpu}});window.__messages=[];window.__loads=0;const NativeWorker=Worker;window.Worker=class extends NativeWorker{constructor(...args){super(...args);this.addEventListener('message',event=>__messages.push({type:event.data.type,device:event.data.device}));}postMessage(message,...rest){if(message.type==='load')__loads++;if(window.__withhold&&message.type==='transcribe'){window.__held=true;return;}super.postMessage(message,...rest);}};'''
    cdp('Page.addScriptToEvaluateOnNewDocument', {'source': preload})
    cdp('Emulation.setDeviceMetricsOverride', {'width': 390, 'height': 844, 'deviceScaleFactor': 1, 'mobile': True})
    cdp('Emulation.setTouchEmulationEnabled', {'enabled': True, 'maxTouchPoints': 5})
    call(f'/session/{sid}/url', {'url': url})
    wait('return __loads>0')
    assert js('return __streams.length===0')
    assert js('return document.documentElement.dataset.keyboardMode==="voice"&&[...document.querySelectorAll("textarea,input:not([type])")].every(n=>n.inputMode==="none")')
    wait('return __messages.some(m=>m.type==="ready"&&m.device==="wasm")')
    wait('return desktopLab.guestState==="ready"&&desktopLab.session?.id')
    call(f'/session/{sid}/log', {'type': 'performance'})
    js('window.__d=[...desktopLab.surfaces.values()][0];window.__sent=[];window.__send=sendTerminal;sendTerminal=(id,text)=>{__sent.push(text);__send(id,text)};document.querySelector(".terminal-input").focus()')
    js('window.__micIcon=document.querySelector(".voice-button").innerHTML')
    press();wait('return document.querySelector("#voice-control").dataset.state==="listening"')
    assert js('return document.querySelector(".voice-button").ariaLabel==="Stop recording"&&document.querySelector(".voice-button").innerHTML!==__micIcon')
    assert js('return document.activeElement.matches(".terminal-input")')
    time.sleep(11);release()
    text = wait('return __sent.find(text=>/Americans|country|fellow/i.test(text))')
    assert '\r' not in text and '\n' not in text
    assert js('return __streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))')
    js('document.querySelector(".terminal-touchkeys [aria-label=Enter]").click();window.__editorWindow=__d.launch("text")')
    wait('return !!document.querySelector(".window.focused .guest-editor")')
    js('window.__editor=document.querySelector(".window.focused .guest-editor");__editor.value="before SELECT after";__editor.dispatchEvent(new Event("input",{bubbles:true}));__editor.focus();__editor.setSelectionRange(7,13)')
    press();wait('return document.querySelector("#voice-control").dataset.state==="listening"')
    assert js('return document.activeElement===__editor&&__editor.selectionStart===7&&__editor.selectionEnd===13')
    time.sleep(11);release()
    wait('return /Americans|country|fellow/i.test(__editor.value)')
    assert js('return __editor.value.startsWith("before ")&&__editor.value.endsWith(" after")&&!__editor.value.includes("SELECT")&&__editorWindow.editor.dirty')
    assert js('return __editor.inputMode==="none"&&document.querySelector(".voice-button").innerHTML===__micIcon')
    js('document.querySelector(".keyboard-toggle").click()')
    assert js('return document.activeElement===__editor&&__editor.inputMode!=="none"&&document.documentElement.dataset.keyboardMode==="typing"')
    js('document.querySelector(".keyboard-toggle").click();__editor.focus()')
    assert js('return __editor.inputMode==="none"&&!__editor.readOnly&&!__editor.disabled&&document.documentElement.dataset.keyboardMode==="voice"')

    # Workspace and chrome renders retain the exact live field and cursor.
    js('window.__selection=[__editor.selectionStart,__editor.selectionEnd];__d.switchWorkspace(1);window.__calculator=__d.launch("calculator")')
    wait('return !!document.querySelector(".window.focused [aria-label=\\"Arithmetic expression\\"]")')
    js('window.__calcInput=document.querySelector(".window.focused [aria-label=\\"Arithmetic expression\\"]");__calcInput.value="123 draft";__d.switchWorkspace(0)')
    assert js('return __editor.isConnected&&document.querySelector(".window.focused .guest-editor")===__editor&&__selection[0]===__editor.selectionStart&&__selection[1]===__editor.selectionEnd')
    js('__d.switchWorkspace(1)')
    assert js('return __calcInput.isConnected&&__calcInput.value==="123 draft"&&document.querySelector(".window.focused").dataset.window===String(__calculator.id)')
    # Another editable app, actual recording, cancel an outstanding inference.
    js('__calcInput.focus();window.__withhold=true;window.__held=false')
    press();wait('return document.querySelector("#voice-control").dataset.state==="listening"')
    time.sleep(2);release();wait('return __held')
    press()
    wait('return document.querySelector("#voice-control").dataset.state==="ready"')
    assert js('return __calcInput.value==="123 draft"&&__streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))')
    js('window.__withhold=false;__d.switchWorkspace(0);__d.launchEntry({name:"Terminal"});__d.launchEntry({name:"Terminal"})')
    assert js('return __d.windows.filter(w=>w.app==="terminal").length===3&&document.querySelector(".task[data-app=terminal] .count").textContent==="3"')
    assert js('const roll=document.querySelector(".window.focused [aria-label=\\"Roll up\\"]");return roll.getBoundingClientRect().width>=44')
    js('document.querySelector(".window.focused [aria-label=\\"Roll up\\"]").click()')
    assert js('return document.querySelector(".window.focused").classList.contains("rolled")')
    js('document.querySelector(".window.focused [aria-label=Unroll]").click();document.querySelector(".window.focused [aria-label=Minimize]").click()')
    assert js('return __d.windows.some(w=>w.app==="terminal"&&w.minimized)&&document.querySelector(".task[data-app=terminal]").classList.contains("running")&&document.querySelector(".task[data-app=terminal] .count").textContent==="3"')
    assert js('return !document.querySelector(".task[data-app=calculator]")')
    # Each workspace owns its task icons, pins, counts and minimized windows.
    js('document.querySelector(".task[data-app=terminal]").click()')
    assert js('return document.querySelectorAll(".task-popup .task-preview").length===3&&[...document.querySelectorAll(".task-preview")].every(n=>n.textContent.includes("Workspace 1"))')
    js('[...document.querySelectorAll(".task-popup button")].find(n=>n.textContent.includes("minimized")).click()')
    assert js('return __d.current===0&&!__d.windows.some(w=>w.app==="terminal"&&w.workspace===0&&w.minimized)')
    js('__d.switchWorkspace(1)')
    assert js('return !document.querySelector(".task[data-app=terminal],.task[data-app=files],.task[data-app=text]")&&document.querySelector(".task[data-app=calculator] .count").textContent==="1"&&__calcInput.value==="123 draft"')
    js('__d.launchEntry({name:"Terminal"});__d.launchEntry({name:"Terminal"});__d.switchWorkspace(2)')
    assert js('return !document.querySelector(".tasks .task")')
    js('for(let n=0;n<4;n++)__d.launchEntry({name:"Terminal"});window.__thirdTerminal=__d.windows.find(w=>w.app==="terminal"&&w.workspace===2)')
    for workspace, count in [(0, 3), (1, 2), (2, 4), (0, 3), (2, 4)]:
        js(f'__d.switchWorkspace({workspace})')
        assert js(f'return document.querySelector(".task[data-app=terminal] .count").textContent==="{count}"&&__d.windows.filter(w=>w.app==="terminal"&&w.workspace===__d.current).length==={count}')
    js('document.querySelector(".task[data-app=terminal]").click()')
    assert js('return document.querySelectorAll(".task-popup .task-preview").length===4&&[...document.querySelectorAll(".task-preview")].every(n=>n.textContent.includes("Workspace 3"))')
    js('document.querySelector(".task-popup .pin").click();__d.switchWorkspace(0)')
    assert js('return !__d.pins.includes("terminal")&&__editor.isConnected&&__editor.value.startsWith("before ")&&__editor.selectionStart===__selection[0]&&__editor.selectionEnd===__selection[1]')
    js('__d.switchWorkspace(1)')
    assert js('return !__d.pins.includes("terminal")&&__calcInput.isConnected&&__calcInput.value==="123 draft"')
    js('__d.switchWorkspace(2)')
    assert js('return __d.pins.includes("terminal")')
    # Closing one local terminal changes only that workspace count.
    js('document.querySelector(".window.focused [aria-label=Close]").click();__d.switchWorkspace(0)')
    assert js('return document.querySelector(".task[data-app=terminal] .count").textContent==="3"')
    js('__d.switchWorkspace(1)')
    assert js('return document.querySelector(".task[data-app=terminal] .count").textContent==="2"')
    js('__d.switchWorkspace(2)')
    assert js('return document.querySelector(".task[data-app=terminal] .count").textContent==="3"')
    js('document.querySelector("[aria-label=Applications]").click()')
    assert js('return !document.querySelector(".menu-row[aria-label=Workspaces]")&&document.querySelector(".panel [aria-label=Workspaces]")')
    assert js('return new Set([...document.querySelectorAll(".menu-pane .menu-row svg.icon")].map(n=>n.innerHTML)).size===5')
    js('__d.closePopups()')
    old = js('const r=document.querySelector(".voice-button").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2,streams:__streams.length}')
    cdp('Input.dispatchTouchEvent', {'type':'touchStart','touchPoints':[{'x':old['x'],'y':old['y']}]})
    for step in range(1,9):
        time.sleep(.04);cdp('Input.dispatchTouchEvent', {'type':'touchMove','touchPoints':[{'x':old['x']-step*10,'y':old['y']-step*12}]})
    cdp('Input.dispatchTouchEvent', {'type':'touchEnd','touchPoints':[]})
    moved = js('const r=document.querySelector(".voice-button").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2,streams:__streams.length,state:document.querySelector("#voice-control").dataset.state}')
    assert moved['x']<old['x']-50 and moved['y']<old['y']-60 and moved['streams']==old['streams'] and moved['state']=="ready",moved
    cdp('Emulation.setDeviceMetricsOverride', {'width':320,'height':420,'deviceScaleFactor':1,'mobile':True})
    wait('const r=document.querySelector("#voice-control").getBoundingClientRect();return r.left>=0&&r.top>=0&&r.right<=visualViewport.width&&r.bottom<=visualViewport.height',5)
    assert js('return __gpuReads===0&&__messages.filter(m=>m.device).every(m=>m.device==="wasm")')
    # Dictation in another workspace must go only to its own PTY, even if
    # focus changes while inference runs. It must never submit the command.
    js('window.__voiceShell=__d.launch("terminal")')
    wait('return !!document.querySelector(".window.focused .terminal-input")')
    js('document.querySelector(".window.focused .terminal-input").focus();window.__firstText=serialScreen.text();window.__sent.length=0')
    wait('return terminalSessions.get(__voiceShell.id).screen.text().includes("~ $")')
    press();wait('return document.querySelector("#voice-control").dataset.state==="listening"')
    time.sleep(11);release()
    wait('return __sent.some(text=>/Americans|country|fellow/i.test(text))')
    wait('return /Americans|country|fellow/i.test(terminalSessions.get(__voiceShell.id).screen.text())')
    assert js('return serialScreen.text()===__firstText&&__sent.every(text=>!/[\\r\\n]/.test(text))')
    logs = call(f'/session/{sid}/log', {'type': 'browser'})
    assert not [entry for entry in logs if entry['level'] == 'SEVERE'], logs
    traffic = [json.loads(entry['message'])['message'] for entry in call(f'/session/{sid}/log', {'type': 'performance'})]
    writes = [item['params']['request'] for item in traffic if item['method'] == 'Network.requestWillBeSent' and item['params']['request']['method'] not in ('GET', 'HEAD', 'OPTIONS')]
    assert not writes, [(item['method'], item['url']) for item in writes]
    result['httpWritesDuringVoiceAndAppChecks'] = []
    if args.url:
        context = ssl.create_default_context(cafile=str(args.fixture_ca_file)) if args.fixture_ca_file else ssl.create_default_context()
        served = {}
        expected_root=args.release_dir.resolve() if args.release_dir else ROOT
        paths={name:name for name in ['app.js', 'style.css', 'terminal.js', 'assets/terminal-initramfs.cpio.gz', 'assets/speech/client.mjs', 'assets/speech/worker.mjs']}
        if args.release_dir:
            graph=json.loads((expected_root/'assets/desktop/network-release.json').read_bytes())
            paths.update({name:graph['coreDirectory']+'/'+name for name in ['app.js','terminal.js']})
            paths['style.css']=__import__('re').search(r'<link rel="stylesheet" href="([^"]+)"',(expected_root/'index.html').read_text())[1]
            with urllib.request.urlopen(url,context=context,timeout=30) as response:assert response.read()==(expected_root/'index.html').read_bytes()
            result['nativeManifestSHA256']=hashlib.sha256((expected_root/'connected-release.json').read_bytes()).hexdigest()
        for name,path in paths.items():
            with urllib.request.urlopen(url + path, context=context, timeout=30) as response:
                digest = hashlib.sha256(response.read()).hexdigest()
            assert digest == hashlib.sha256((expected_root / path).read_bytes()).hexdigest(), path
            served[path] = digest
        result['servedAssetsSHA256'] = served
    result.update(status='PASS', url=url, speechText=text, preloadBeforeAnyVoiceGesture=True, preloadNeverOpensMicrophone=True, actualLocalWhisperWasmInference=True, touchTapStartsAndStops=True, recordingIconChanges=True, keyboardSuppressedByDefaultAndExplicitToggleWorks=True, draggableOverlayDoesNotStartRecording=True, floatingOverlayFitsResizedViewport=True, priorFocusAndEditorSelectionPreserved=True, terminalAndEditorActualDictation=True, dictationTargetsIndependentShell=True, anotherAppCancellationDiscardsText=True, noAutomaticEnterOrSend=True, workspaceRetainsAppDomDraftAndCursor=True, applicationsTerminalOpensAdditionalWindow=True, phoneRollUpRestored=True, minimizedTaskCountAndRunningIndicator=True, workspaceAppIconsAndCountsIndependent=True, workspacePinsIndependent=True, localTaskPickerAndMinimizeRestore=True, workspacesOnlyInTopBar=True, distinctApplicationIcons=True, gpuNeverAccessed=True, audioUploaded=False, physicalMicrophoneNotTested=True)
except BaseException as error:
    result['error'] = type(error).__name__ + ': ' + str(error)
    if sid:
        result['browserLog'] = call(f'/session/{sid}/log', {'type': 'browser'})
    raise
finally:
    if sid:
        call(f'/session/{sid}', method='DELETE')
    if server:
        server.shutdown();server.server_close()
    result['sha256'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ['app.js', 'style.css', 'terminal.js', 'assets/terminal-initramfs.cpio.gz', 'assets/speech/client.mjs', 'assets/speech/worker.mjs', 'scripts/general-voice-check.py']}
    name = 'general-voice-fixture-result.json' if args.fixture_spki_file else 'general-voice-public-result.json' if args.url else 'general-voice-result.json'
    output = ROOT / '.build/checks' / name
    if output.exists():
        output.rename(output.with_name(output.stem + '-before-' + str(time.time_ns()) + '.json'))
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

