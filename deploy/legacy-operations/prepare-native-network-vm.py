#!/usr/bin/env python3
"""Prepare/status/stop a private KVM systemd fixture without host firewall edits.

State and ephemeral SSH credentials stay in .build/native-network-vm (0700).
The Ubuntu image is downloaded over trusted HTTPS and checked against its
published SHA256SUMS. No host directories or existing SSH keys are shared.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import time
import urllib.request

ROOT=Path(__file__).resolve().parent.parent
FOLDER=ROOT/'.build/native-network-vm'
BASE='https://cloud-images.ubuntu.com/minimal/releases/noble/release/'
IMAGE='ubuntu-24.04-minimal-cloudimg-amd64.img'
def run(args,**kwargs):return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True,timeout=180,**kwargs).stdout
def write(file,value):file.write_text(json.dumps(value,indent=2)+'\n');file.chmod(0o600)
def port():
    with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def qmp(command):
    with socket.socket(socket.AF_UNIX) as sock:
        sock.settimeout(5);sock.connect(str(FOLDER/'qmp.sock'));stream=sock.makefile('rwb',buffering=0);greeting=json.loads(stream.readline());assert 'QMP' in greeting
        for request in ['qmp_capabilities',command]:
            stream.write((json.dumps({'execute':request})+'\r\n').encode())
            while True:
                value=json.loads(stream.readline())
                if 'return' in value:break
                if 'error' in value:raise ValueError(value['error'])
        return value['return']
def status():
    value=json.loads((FOLDER/'fixture.json').read_text());pid=int((FOLDER/'qemu.pid').read_text());cmdline=Path('/proc/'+str(pid)+'/cmdline').read_bytes()
    if str(FOLDER/'disk.qcow2').encode() not in cmdline or b'qemu-system-x86_64' not in cmdline:raise ValueError('Fixture PID does not identify the expected live QEMU')
    live=qmp('query-status');assert live['running'] and live['status']=='running'
    return {'status':'RUNNING','pid':pid,'qmp':live,'sshPort':value['sshPort'],'httpsPort':value['httpsPort'],'imageSHA256':value['imageSHA256'],'privateState':str(FOLDER),'hostFirewallChanged':False}
def ssh_args():
    value=status()
    return ['ssh','-F','/dev/null','-i',str(FOLDER/'ssh-key'),'-p',str(value['sshPort']),'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=accept-new','-o','UserKnownHostsFile='+str(FOLDER/'known_hosts'),'-o','ConnectTimeout=5','root@127.0.0.1']
def prepare():
    if FOLDER.exists():raise ValueError('Preserve existing fixture; use status/ssh/stop rather than overwrite or restart')
    if not os.access('/dev/kvm',os.R_OK|os.W_OK):raise ValueError('KVM is required for the nested systemd test')
    FOLDER.mkdir(mode=0o700)
    with urllib.request.urlopen(BASE+'SHA256SUMS',timeout=30) as response:checksums=response.read(65537)
    if len(checksums)>65536:raise ValueError('Bounded upstream checksums required')
    entries=[line.split() for line in checksums.decode().splitlines()];matches=[entry[0] for entry in entries if len(entry)==2 and entry[1].lstrip('*')==IMAGE]
    if len(matches)!=1 or not re.fullmatch('[0-9a-f]{64}',matches[0]):raise ValueError('Exact upstream image checksum required')
    expected=matches[0];(FOLDER/'upstream-SHA256SUMS').write_bytes(checksums);digest=hashlib.sha256();size=0
    print(json.dumps({'phase':'downloading official Ubuntu image','expectedSHA256':expected}),flush=True)
    with urllib.request.urlopen(BASE+IMAGE,timeout=90) as response,(FOLDER/'base.qcow2').open('xb') as target:
        while data:=response.read(1024*1024):
            size+=len(data)
            if size>1024**3:raise ValueError('Fixture image exceeds expected 1GiB bound')
            digest.update(data);target.write(data)
    if digest.hexdigest()!=expected:raise ValueError('Upstream image checksum mismatch; retain failed download for review')
    run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',FOLDER/'base.qcow2',FOLDER/'disk.qcow2','12G'])
    run(['ssh-keygen','-q','-t','ed25519','-N','','-C','disposable-codi-network-fixture','-f',FOLDER/'ssh-key'])
    key=(FOLDER/'ssh-key.pub').read_text().strip();token=secrets.token_hex(8)
    cloud='''#cloud-config
users:
  - name: root
    ssh_authorized_keys:
      - KEY
disable_root: false
ssh_pwauth: false
package_update: true
packages:
  - python3-venv
  - python3-pip
  - qemu-system-x86
  - nftables
  - iproute2
  - openssl
  - curl
  - ca-certificates
runcmd:
  - [touch, /var/lib/codi-fixture-ready]
'''.replace('KEY',key)
    (FOLDER/'user-data').write_text(cloud);(FOLDER/'meta-data').write_text('instance-id: codi-net-'+token+'\nlocal-hostname: codi-network-fixture\n')
    run(['genisoimage','-quiet','-output',FOLDER/'seed.iso','-volid','cidata','-joliet','-rock',FOLDER/'user-data',FOLDER/'meta-data'])
    ssh_port=port();https_port=port()
    value={'version':'codi-native-network-vm/1','created':int(time.time()),'imageURL':BASE+IMAGE,'imageSHA256':expected,'imageBytes':size,'sshPort':ssh_port,'httpsPort':https_port,'fixtureID':token,'hostFirewallChanged':False,'hostDirectoriesShared':False}
    write(FOLDER/'fixture.json',value)
    run(['qemu-system-x86_64','-name','codi-network-fixture-'+token,'-enable-kvm','-cpu','host','-smp','2','-m','3072','-display','none','-monitor','none','-serial','file:'+str(FOLDER/'console.log'),'-qmp','unix:'+str(FOLDER/'qmp.sock')+',server=on,wait=off','-drive','file='+str(FOLDER/'disk.qcow2')+',if=virtio,format=qcow2','-drive','file='+str(FOLDER/'seed.iso')+',if=virtio,format=raw,readonly=on','-netdev','user,id=fixture,hostfwd=tcp:127.0.0.1:'+str(ssh_port)+'-:22,hostfwd=tcp:127.0.0.1:'+str(https_port)+'-:8443','-device','virtio-net-pci,netdev=fixture','-pidfile',FOLDER/'qemu.pid','-daemonize'])
    print(json.dumps(status(),indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['prepare','status','ssh','stop']);parser.add_argument('command',nargs='*');args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='status':print(json.dumps(status(),indent=2))
    elif args.action=='ssh':
        status();result=subprocess.run([*ssh_args(),*args.command]);raise SystemExit(result.returncode)
    else:
        current=status();qmp('quit');print(json.dumps({'status':'STOP_REQUESTED','pid':current['pid'],'statePreserved':True}))
