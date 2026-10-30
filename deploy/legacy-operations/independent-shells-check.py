#!/usr/bin/env python3
"""Real v86 PTYs, workspace/window lifecycle and isolated shell jobs in Chrome."""
import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRIVER = 'http://127.0.0.1:19515'

def call(path, data=None, method=None):
    request = urllib.request.Request(DRIVER + path, data=None if data is None else json.dumps(data).encode(), headers={'Content-Type': 'application/json'}, method=method)
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.load(response)['value']
    except Exception as error:
        if hasattr(error, 'read'):
            raise RuntimeError(error.read().decode()) from error
        raise

def run(url, mobile):
    sid = call('/session', {'capabilities': {'alwaysMatch': {'browserName': 'chrome', 'goog:chromeOptions': {'binary': '/snap/chromium/current/usr/lib/chromium-browser/chrome', 'args': ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage', '--window-size=1366,900']}, 'goog:loggingPrefs': {'browser': 'ALL'}}}})['sessionId']
    def js(script):
        return call(f'/session/{sid}/execute/sync', {'script': script, 'args': []})
    def cdp(cmd, params):
        return call(f'/session/{sid}/goog/cdp/execute', {'cmd': cmd, 'params': params})
    def wait(script, seconds=120):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            value = js(script)
            if value:
                return value
            time.sleep(.15)
        raise AssertionError((script, js('return [...terminalSessions].map(([id,s])=>[id,s.screen.text()])')))
    def click(selector):
        if mobile:
            point = js('const r=document.querySelector('+json.dumps(selector)+').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}')
            cdp('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [point]})
            cdp('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        else:
            js('document.querySelector('+json.dumps(selector)+').click()')
    def command(id, text):
        js(f'__d.activateWindow(__d.windows.find(w=>w.id==={id}));document.querySelector("[data-window=\\"{id}\\"] .terminal-input").focus()')
        cdp('Input.insertText', {'text': text})
        click(f'[data-window="{id}"] .terminal-touchkeys [aria-label=Enter]')
    def screen(id):
        return f'terminalSessions.get({id}).screen.text()'
    def launch():
        # The Applications entry must create a new shell even when one exists.
        click('.panel [aria-label=Applications]')
        click('.menu-row[aria-label=Terminal]')
        return js('return __d.active')
    try:
        if mobile:
            cdp('Emulation.setDeviceMetricsOverride', {'width': 390, 'height': 844, 'deviceScaleFactor': 1, 'mobile': True})
            cdp('Emulation.setTouchEmulationEnabled', {'enabled': True, 'maxTouchPoints': 5})
        call(f'/session/{sid}/url', {'url': url})
        wait('return window.desktopLab?.guestState==="ready"')
        js('window.__d=[...desktopLab.surfaces.values()][0];window.__vm=v86Instance')
        wait('return serialScreen.text().includes("~ $")')
        command(2, "export SHELL_MARK=first; cd /tmp; printf '\\nFIRST:%s:%s:%s\\n' \"$$\" \"$SHELL_MARK\" \"$PWD\"; tty; id")
        wait('return '+screen(2)+'.includes("uid=1000(guest) gid=1000(guest)")')
        first = js('return '+screen(2))
        assert '/dev/pts/0' in first and ':first:/tmp' in first, first
        # Single running task still offers an explicit New window action.
        click('.task[data-app=terminal]')
        click('.task-popup .new-window')
        second = js('return __d.active')
        assert second != 2
        wait(f'return {screen(second)}.includes("~ $")')
        command(second, "printf '\\nSECOND:%s:%s:%s\\n' \"$$\" \"${SHELL_MARK-unset}\" \"$PWD\"; tty")
        wait(f'return {screen(second)}.includes("/dev/pts/1")')
        second_text = js('return '+screen(second))
        assert ':unset:/home/guest' in second_text and 'FIRST:' not in second_text, second_text
        assert 'SECOND:' not in js('return '+screen(2))
        third = launch()
        wait(f'return {screen(third)}.includes("~ $")')
        assert js('return document.querySelector(".task[data-app=terminal] .count").textContent') == '3'
        assert js('return document.querySelectorAll(".window:not([hidden])").length') == 4
        # A foreground job continues when switching workspaces; Ctrl+C elsewhere
        # must not interrupt it. The shared filesystem remains one guest home.
        command(second, "sleep 4; echo JOB_SURVIVED > /home/guest/job-survived.txt; echo JOB_DONE")
        command(2, 'sleep 30')
        click('[data-window="2"] .terminal-touchkeys [aria-label="Ctrl+C"]')
        command(2, 'echo FIRST_STILL_ALIVE')
        wait('return '+screen(2)+'.includes("\\nFIRST_STILL_ALIVE\\n")')
        click('.workspace-toggle');click('.workspace-choice[aria-label="Workspace 2"]')
        assert js('return !document.querySelector(".tasks .task")')
        fourth, fifth = launch(), launch()
        for id in [fourth, fifth]:
            wait(f'return {screen(id)}.includes("~ $")')
        wait(f'return {screen(second)}.includes("\\nJOB_DONE\\n")')
        command(fifth, "printf '\\nOTHER_WORKSPACE:%s:%s\\n' \"${SHELL_MARK-unset}\" \"$PWD\"; cat /home/guest/job-survived.txt; tty")
        wait(f'return {screen(fifth)}.includes("\\nJOB_SURVIVED\\n")')
        assert ':unset:/home/guest' in js('return '+screen(fifth))
        assert js('return document.querySelector(".task[data-app=terminal] .count").textContent') == '2'
        click('.workspace-toggle');click('.workspace-choice[aria-label="Workspace 1"]')
        assert js('return document.querySelector(".task[data-app=terminal] .count").textContent') == '3'
        wait(f'return {screen(second)}.includes("\\nJOB_DONE\\n")')
        js(f'__d.activateWindow(__d.windows.find(w=>w.id==={second}))')
        click(f'[data-window="{second}"] [aria-label=Minimize]')
        assert js(f'return terminalSessions.has({second})&&document.querySelector("[data-window=\\"{second}\\"]").hidden')
        click('.task[data-app=terminal]')
        click(f'.task-popup button[data-window-id="{second}"]')
        assert js(f'return __d.active==={second}&&!document.querySelector("[data-window=\\"{second}\\"]").hidden')
        command(second, 'echo SECOND_PRESERVED')
        wait(f'return {screen(second)}.includes("\\nSECOND_PRESERVED\\n")')
        command(third, 'exit')
        wait(f'return terminalSessions.get({third}).exited')
        command(2, 'echo OTHERS_SURVIVE_EXIT')
        wait('return '+screen(2)+'.includes("\\nOTHERS_SURVIVE_EXIT\\n")')
        js(f'__d.activateWindow(__d.windows.find(w=>w.id==={third}))')
        click(f'[data-window="{third}"] [aria-label=Close]')
        assert js(f'return !terminalSessions.has({third})&&document.querySelector(".task[data-app=terminal] .count").textContent==="2"&&v86Instance===__vm')
        click('.workspace-toggle');click('.workspace-choice[aria-label="Workspace 2"]')
        assert js('return document.querySelector(".task[data-app=terminal] .count").textContent') == '2'
        if url.startswith('https://'):
            command(fifth, 'ping -c 2 1.1.1.1; nslookup example.com; wget -O /tmp/pty-web.html http://example.com; test -s /tmp/pty-web.html && echo PTY_WEB_OK')
            wait(f'return {screen(fifth)}.includes("2 packets received")&&{screen(fifth)}.includes("\\nPTY_WEB_OK\\n")')
        logs = call(f'/session/{sid}/log', {'type': 'browser'})
        assert not [entry for entry in logs if entry['level'] == 'SEVERE'], logs
        return {'mode': 'phone touch emulation' if mobile else 'desktop', 'distinctPtys': True, 'unprivilegedShells': True, 'independentCwdEnvironmentAndOutput': True, 'foregroundJobsSurviveWorkspaceSwitch': True, 'ctrlCOnlyInterruptsTargetShell': True, 'sharedGuestFiles': True, 'newWindowFromSingleTaskAndApplications': True, 'workspaceCounts': [3, 2], 'otherWindowsRemainVisible': True, 'minimizeRestoreRetainsShell': True, 'exitAndCloseOnlyAffectTargetShell': True, 'vmNotRestarted': True}
    finally:
        call(f'/session/{sid}', method='DELETE')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8118/')
    args = parser.parse_args()
    result = {'status': 'FAIL', 'url': args.url}
    try:
        result['witnesses'] = [run(args.url, mobile) for mobile in [True, False]]
        result['status'] = 'PASS'
    finally:
        result['sha256'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ['app.js', 'terminal.js', 'style.css', 'assets/terminal-initramfs.cpio.gz', 'scripts/guest-terminal-mux.c', 'scripts/independent-shells-check.py']}
        name = 'independent-shells-public-result.json' if args.url.startswith('https://') else 'independent-shells-result.json'
        (ROOT / '.build/checks' / name).write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2), flush=True)
