#!/usr/bin/env python3
"""Owned R730 ChromeDriver/SDK load job, using project-only existing tools.

No system units, model services, public listeners or production accounts change.
The foreground process owns its driver and closes it after the runner finishes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import urllib.request

BASE=Path('/home/dflanag3/codi-load-tests')
CADDY='b7105518e3ed1c0761f232e44fc09345535533c9cb0abf0e12809416c7ac64d9'
RELEASE='952fe21dfa990b63323f0d9dad597cab8d9a5604ea7fe519bf5547aef4e0a063'

def start_ticks(pid):return (Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19]

def main(a):
    artifact=a.artifact.resolve();assert artifact.is_relative_to(BASE/'artifacts') and artifact.is_dir()
    assert a.job.is_relative_to(BASE/'runs') and not a.job.exists();a.job.mkdir(mode=0o700)
    runner=artifact/'runner';raw=(runner/'runner-source.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==a.runner_sha256
    manifest=json.loads(raw);assert {str(p.relative_to(runner)) for p in runner.rglob('*') if p.is_file()}==set(manifest['files'])|{'runner-source.json'}
    for n,r in manifest['files'].items():
        p=runner/n;assert not p.is_symlink() and r=={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    assert hashlib.sha256((artifact/'release/connected-release.json').read_bytes()).hexdigest()==RELEASE
    caddy=artifact/'tools/caddy';assert hashlib.sha256(caddy.read_bytes()).hexdigest()==CADDY
    chrome=BASE/'browsers/156.0.8078.47/chrome-linux64/chrome';binary=BASE/'browsers/156.0.8078.47/chromedriver-linux64/chromedriver'
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    driver=None;child=None;started=time.monotonic();metadata={'pid':os.getpid(),'startTicks':start_ticks(os.getpid()),'bootID':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'participants':a.participants,'artifact':str(artifact),'runnerSHA256':a.runner_sha256,'productionChanged':False,'actualV86Desktops':0}
    def persist():
        p=a.job/'job.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(metadata,indent=2)+'\n');tmp.chmod(0o600);tmp.replace(p)
    try:
        with (a.job/'driver.log').open('wb') as log:driver=subprocess.Popen([str(binary),'--port='+str(port),'--allowed-ips=127.0.0.1'],stdout=log,stderr=subprocess.STDOUT)
        metadata.update(driverPID=driver.pid,driverStartTicks=start_ticks(driver.pid),driverURL='http://127.0.0.1:'+str(port),state='starting');persist()
        until=time.monotonic()+15
        while True:
            assert driver.poll() is None,'Owned driver exited'
            try:
                with urllib.request.urlopen(metadata['driverURL']+'/status',timeout=1) as r:assert json.load(r)['value']['ready']
                break
            except OSError:
                if time.monotonic()>until:raise
                time.sleep(.1)
        command=[str(BASE/'venv/bin/python'),'-B',str(runner/'scripts/hosted-agent-load-check.py'),'--release',str(artifact/'release'),'--participants',str(a.participants),'--per-browser','32','--admission-interval','.6','--atomic-sync','--proposal-recovery','--reader-coordinator','--caddy',str(caddy),'--steady-seconds',str(a.steady_seconds),'--chrome-binary',str(chrome),'--driver-url',metadata['driverURL'],'--output',str(a.job/'result.json')]
        child=subprocess.Popen(command);metadata.update(runnerPID=child.pid,runnerStartTicks=start_ticks(child.pid),state='running');persist();print(json.dumps({'phase':'owned-job-running',**metadata}),flush=True)
        while child.poll() is None:
            # Leave headroom for the OS and unrelated work; this is a load-job
            # guard, not a changed SDK, gateway or production capacity setting.
            values={line.split(':')[0]:int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')}
            if values['MemAvailable']<12*1024*1024 and not metadata.get('cancellationReason'):
                metadata['cancellationReason']='host available memory fell below12GiB';persist();child.send_signal(signal.SIGINT)
            time.sleep(1)
        metadata.update(state='finished',runnerExitCode=child.returncode,elapsedSeconds=round(time.monotonic()-started,3));persist()
    finally:
        if child and child.poll() is None:
            child.send_signal(signal.SIGINT)
            try:child.wait(timeout=90)
            except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=10)
        if driver and driver.poll() is None:
            driver.terminate()
            try:driver.wait(timeout=10)
            except subprocess.TimeoutExpired:driver.kill();driver.wait(timeout=5)
        metadata.update(driverStopped=driver is None or driver.poll() is not None);persist()
    print(json.dumps({'phase':'owned-job-finished',**metadata}),flush=True)
    return child.returncode

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--artifact',type=Path,required=True);p.add_argument('--runner-sha256',required=True);p.add_argument('--job',type=Path,required=True);p.add_argument('--participants',type=int,choices=[16,128,512,2048,8000],required=True);p.add_argument('--steady-seconds',type=int,default=120);a=p.parse_args();assert 10<=a.steady_seconds<=600;raise SystemExit(main(a))
