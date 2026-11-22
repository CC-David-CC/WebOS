"""Verify recording and playback through SoundCraft and WebOS Files using a generated 440 Hz microphone.

Install Python Playwright and run with --help. Run each workspace role against a development viewer or an explicitly selected HTTPS release.
The signed role creates one disposable test account and signs back into it from a separate browser context.
"""
import argparse
import base64
import hashlib
import io
import json
import math
import os
import secrets
import statistics
import struct
import time
import wave
import zipfile
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen
from playwright.sync_api import expect, sync_playwright

def findwin(p, app):
    return p.locator('.window').filter(has=p.locator('.caption-text', has_text=app)).last

def wait(probe, seconds=60):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        v = probe()
        if v:
            return v
        time.sleep(0.1)
    raise TimeoutError(str(probe))

def canvasready(win):
    win.wait_for()
    expect(win.locator('iframe')).to_be_attached(timeout=105000)
    result = win.evaluate("async n => { await n.appView.ready; return true; }")
    assert result is True, result
    expect(win.locator('iframe')).to_be_visible()

def menu(p, group, name):
    p.locator('.app-menu-button').click()
    p.get_by_role('menuitem', name=group, exact=True).click()
    p.get_by_role('menuitem', name=name, exact=True).click()

def close(w):
    w.locator('button[title="Close"],button[aria-label="Close"]').last.click()

def shortcut(p, w, id, k):
    w.locator('.caption-text').click()
    native = next((f for f in p.frames if '/' + id + '/index.html' in f.url))
    native.locator('canvas').first.evaluate('c=>{c.tabIndex=0;c.focus()}')
    p.keyboard.press(k)

def appfiles(p):
    menu(p, 'System Tools', 'Files')
    files = findwin(p, 'Home — Files')
    files.get_by_text('Documents', exact=True).first.dblclick()
    return files

def authenticate(p, action, user, password):
    p.get_by_role('button', name='Session: Anon', exact=True).click()
    p.locator('[data-account-action="' + action + '"]').click()
    form = p.locator('.account-form')
    form.get_by_label('Username', exact=True).fill(user)
    form.get_by_label('Password', exact=True).fill(password)
    if action == 'register':
        form.get_by_label('Confirm password', exact=True).fill(password)
    form.get_by_role('button', name='Register' if action == 'register' else 'Sign in', exact=True).click()
    p.get_by_role('button', name='Session: ' + user, exact=True).wait_for()

def read(p, path):
    encoded = p.evaluate("""async path => {
   const bytes = new Uint8Array((await (await workspaceFileContext()).files.read(path)).data);
   let binary = '';
   for (let i = 0; i < bytes.byteLength; i += 0x8000) {
     binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
   }
   return btoa(binary);
 }""", path)
    return base64.b64decode(encoded)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--origin', required=True, help='WebOS https origin or loopback development origin')
parser.add_argument('--role', choices=('anon', 'signed'), required=True)
parser.add_argument('--source-commit', required=True, help='Expected full SoundCraft commit')
parser.add_argument('--output', required=True, type=Path, help='New directory for private test artifacts')
parser.add_argument('--chromium', help='Installed Chromium executable, optional for Playwright-managed Chromium')
args = parser.parse_args()
origin = args.origin.rstrip('/')
address = urlsplit(origin)
assert address.netloc and (not address.path) and (not address.username) and (not address.password) and (not address.query) and (not address.fragment)
assert address.scheme == 'https' or (address.scheme == 'http' and address.hostname in ('127.0.0.1', 'localhost', '::1'))
with urlopen(origin + '/soundcraft/component-build.json', timeout=30) as reply:
    receipt = json.load(reply)
assert receipt['component'] == 'soundcraft' and receipt['sourceCommit'] == args.source_commit
expected = next((f['sha256'] for f in receipt['files'] if f['path'] == 'soundcraft_web_bg.wasm'))
role = args.role
os.umask(0o077)
out = args.output.absolute()
out.mkdir(parents=True, exist_ok=False)
tone = out / 'fixture.wav'
with wave.open(str(tone), 'wb') as w:
    w.setparams((1, 2, 48000, 0, 'NONE', ''))
    w.writeframes(b''.join((struct.pack('<h', round(12000 * math.sin(2 * math.pi * 440 * x / 48000))) for x in range(48000))))

def log(*a):
    print(*a, flush=True)

def trace(page):
    return page.evaluate('window.takeTrace||[]')
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=args.chromium, args=['--disable-dev-shm-usage', '--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--disk-cache-size=16777216', '--use-fake-device-for-media-stream', '--use-file-for-fake-audio-capture=' + str(tone)])
    ctx = browser.new_context(service_workers='block', viewport={'width': 1540, 'height': 1000}, permissions=['microphone'])
    requests = []
    errors = []
    script = """window.takeTrace=[];
 if(window.AudioNode) {
  window.takeAnalyzers=new Map();
  const original=AudioNode.prototype.connect;
  AudioNode.prototype.connect=function(...args) {
   const result=original.apply(this,args);
   if(args[0] instanceof AudioDestinationNode && !(this instanceof AudioWorkletNode)) {
    let a=window.takeAnalyzers.get(this.context);
    if(!a){a=this.context.createAnalyser();a.fftSize=4096;window.takeAnalyzers.set(this.context,a);}
    original.call(this,a);
   }
   return result;
  }
 }
 window.addEventListener('pointerdown',e=>{const b=e.target.closest?.('button');if(b)window.takeTrace.push([performance.now(),b.title||b.getAttribute('aria-label')||b.textContent]);},true);
 window.addEventListener('message',e=>{if(e.origin===location.origin && String(e.data?.type).endsWith('session-result')) window.takeTrace.push([performance.now(),e.data.operation,e.data.ok]);});"""
    ctx.add_init_script(script)
    page = ctx.new_page()
    page.set_default_timeout(35000)
    page.on('pageerror', lambda err: errors.append(str(err)))
    page.on('request', lambda r: requests.append(r.url) if '/api/v1/files/' in r.url or '/gateway/' in r.url else None)
    try:
        page.goto(origin, wait_until='domcontentloaded')
        page.get_by_role('button', name='Session: Anon', exact=True).wait_for()
        maps = findwin(page, 'Weather Maps')
        if maps.count():
            close(maps)
        if role == 'signed':
            user = 'testtake' + secrets.token_hex(5)
            pwtext = secrets.token_urlsafe(18)
            authenticate(page, 'register', user, pwtext)
        menu(page, 'Audio Tools', 'SoundCraft')
        win = findwin(page, 'SoundCraft')
        canvasready(win)
        log('native ready')
        win.get_by_role('button', name='Maximize', exact=True).click()
        native = next((f for f in page.frames if '/soundcraft/index.html' in f.url))
        digest = native.evaluate("""async () => {
    const wasm = await (await fetch('./soundcraft_web_bg.wasm')).arrayBuffer();
    return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', wasm)), b => b.toString(16).padStart(2, '0')).join('');
  }""")
        assert digest == expected, ('wrong engine bytes', digest)
        fr = win.locator('iframe')
        box = fr.bounding_box()
        log('box', box)
        title = win.locator('.caption-text')
        # egui renders the transport on a canvas. Use the fixed test viewport and
        # its measured iframe origin to exercise the same controls a user clicks.
        controls = {'New track': (145, 153), 'Arm track': (203, 222),
                    'Record': (1248, 48), 'Stop': (1166, 48),
                    'Rewind': (1125, 77), 'Play': (1208, 48)}
        def click(control):
            x, y = controls[control]
            page.mouse.click(box['x'] + x, box['y'] + y)
        click('New track')
        page.wait_for_timeout(400)
        page.keyboard.press('Enter')
        wait(lambda: win.evaluate('e=>e.appView.lifecycle.snapshot().dirty'), 35)
        click('Arm track')
        page.wait_for_timeout(400)
        click('Record')
        log('record pressed')
        page.wait_for_timeout(2500)
        page.screenshot(path=out / 'record.png')
        click('Stop')
        page.wait_for_timeout(1500)
        log('stop')
        t = time.perf_counter()
        close(win)
        preclose = page.locator('dialog.webos-soundcraft-session[open]')
        expect(preclose).to_be_visible()
        closePrompt = time.perf_counter() - t
        log('dirty close prompt', closePrompt, 's')
        preclose.get_by_role('button', name='Cancel', exact=True).click()
        shortcut(page, win, 'soundcraft', 'Control+Shift+s')
        picker = page.locator('dialog.codi-file-picker[open]')
        picker.get_by_role('button', name='Open folder Documents', exact=True).click()
        picker.get_by_role('button', name='Use this folder', exact=True).click()
        prompt = page.locator('dialog.codi-confirm-dialog[open]')
        prompt.get_by_label('File name').fill('Mic test')
        prompt.get_by_role('button', name='Save', exact=True).click()
        wait(lambda: 'Mic test' in title.inner_text())
        data = read(page, 'Documents/Mic test.scraftz')
        log('bundle', len(data))
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            aud = [n for n in z.namelist() if n.lower().endswith('.wav')]
            assert len(aud) == 1, z.namelist()
            wav = z.read(aud[0])
            fmt = wav.index(b'fmt ') + 8
            off = wav.index(b'data') + 8
            samplerate = struct.unpack_from('<I', wav, fmt + 4)[0]
            bits = struct.unpack_from('<H', wav, fmt + 14)[0]
            channels = struct.unpack_from('<H', wav, fmt + 2)[0]
            assert bits == 32
            sig = struct.unpack_from('<' + 'f' * ((len(wav) - off) // 4), wav, off)[::channels]
            crossings = sum((1 for a, b in zip(sig, sig[1:]) if a < 0 <= b))
            hz = crossings * samplerate / len(sig)
            rms = math.sqrt(statistics.mean((x * x for x in sig)))

            # Goertzel frequency scores over independent 100 ms windows.
            def strength(window, f):
                v1 = v2 = 0.0
                coeff = 2.0 * math.cos(2 * math.pi * f / samplerate)
                for sample in window:
                    v = v1 * coeff - v2 + sample
                    v2, v1 = (v1, v)
                return v1 * v1 + v2 * v2 - coeff * v1 * v2
            n = samplerate // 10
            peaks = [max(range(370, 531, 5), key=lambda f: strength(sig[i:i + n], f)) for i in range(n, len(sig) - n, max(n, len(sig) // 12))]
            (out / 'signal.json').write_text(json.dumps({'peaks': peaks, 'rawZeroCrossingHz': hz, 'rms': rms, 'rate': samplerate, 'duration': len(sig) / samplerate}, indent=2))
            log('signal', peaks, 'zeroes', hz, 'rms', rms)
            assert len(peaks) >= 4 and sum((430 <= x <= 450 for x in peaks)) >= 0.8 * len(peaks) and (0.08 < rms < 0.6), (peaks, hz, rms)
            hz = statistics.median(peaks)
        close(win)
        expect(win).to_have_count(0)
        if role == 'signed':
            ctx.close()
            ctx = browser.new_context(service_workers='block', viewport={'width': 1540, 'height': 1000}, permissions=['microphone'])
            ctx.add_init_script(script)
            page = ctx.new_page()
            page.set_default_timeout(35000)
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(origin, wait_until='domcontentloaded')
            page.get_by_role('button', name='Session: Anon', exact=True).wait_for()
            maps = findwin(page, 'Weather Maps')
            if maps.count():
                close(maps)
            authenticate(page, 'signin', user, pwtext)
            win = findwin(page, 'SoundCraft')
        fv = appfiles(page)
        fv.get_by_text('Mic test.scraftz', exact=True).first.dblclick()
        canvasready(win)
        win.screenshot(path=out / 'reopened.png')
        assert read(page, 'Documents/Mic test.scraftz') == data
        if win.get_by_role('button', name='Maximize', exact=True).count():
            win.get_by_role('button', name='Maximize', exact=True).click()
        box = win.locator('iframe').bounding_box()
        native = next((f for f in page.frames if '/soundcraft/index.html' in f.url))
        click('Rewind')
        click('Play')
        audible = native.evaluate("""async () => {
          let amp = 0, frequency = 0;
          for (let j = 0; j < 100; j++) {
            for (const [context, analyser] of window.takeAnalyzers) {
              const data = new Float32Array(analyser.fftSize);
              analyser.getFloatTimeDomainData(data);
              const rms = Math.sqrt(data.reduce((sum, x) => sum + x*x, 0) / data.length);
              if (rms > amp) {
                amp = rms;
                const rises = data.reduce((sum, x, i) => sum + (i && x >= 0 && data[i-1] < 0 ? 1 : 0), 0);
                frequency = rises * context.sampleRate / data.length;
              }
            }
            if (amp > .05 && frequency > 400 && frequency < 480) break;
            await new Promise(resolve => setTimeout(resolve, 20));
          }
          return {amp, frequency};
        }""")
        assert 400 < audible['frequency'] < 480 and audible['amp'] > 0.05, audible
        click('Stop')
        t = time.perf_counter()
        close(win)
        expect(win).to_have_count(0, timeout=20000)
        cleanClose = time.perf_counter() - t
        log('saved close', cleanClose, 's')
        fv.get_by_text('Mic test.scraftz', exact=True).first.dblclick()
        canvasready(win)
        if win.get_by_role('button', name='Maximize', exact=True).count():
            win.get_by_role('button', name='Maximize', exact=True).click()
        box = win.locator('iframe').bounding_box()
        click('New track')
        page.wait_for_timeout(400)
        page.keyboard.press('Enter')
        wait(lambda: win.evaluate('e=>e.appView.lifecycle.snapshot().dirty'), 35)
        t = time.perf_counter()
        close(win)
        dialog = page.locator('dialog.webos-soundcraft-session[open]')
        dialog.get_by_role('button', name='Discard', exact=True).click()
        expect(win).to_have_count(0, timeout=20000)
        discard_close = time.perf_counter() - t
        assert read(page, 'Documents/Mic test.scraftz') == data
        assert not errors, errors
        if role == 'anon':
            assert not requests
        else:
            assert requests, 'Expected signed storage transfers'
        log('pass', hz, rms, audible)
        (out / 'result.json').write_text(json.dumps({'sourceCommit': args.source_commit, 'wasmSHA256': digest, 'role': role, 'accountFileRequestCount': len(requests), 'dirtyClosePromptSeconds': closePrompt, 'savedCloseSeconds': cleanClose, 'editedDiscardCloseSeconds': discard_close, 'hz': hz, 'rms': rms, 'sha256': hashlib.sha256(data).hexdigest(), 'samples': len(sig), 'playback': audible, 'errors': errors}, indent=2))
    except BaseException:
        log('trace', trace(page)[-12:], 'errors', errors)
        page.screenshot(path=out / 'failure.png')
        raise
    finally:
        ctx.close()
        browser.close()
