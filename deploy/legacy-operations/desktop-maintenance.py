#!/usr/bin/env python3
"""Publish a root-controlled public notice; never restart services or save a VM."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import stat
import tempfile
import time
import uuid

def publish(directory,phase,seconds,message,duration):
    if os.geteuid()!=0:raise ValueError('Run as the maintenance operator (root)')
    directory=Path(directory)
    if not directory.is_absolute() or '..' in directory.parts:raise ValueError('Absolute operator directory required')
    for parent in [directory,*directory.parents]:
        info=parent.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=0 or info.st_mode&0o022:raise ValueError('Root-owned protected directory required')
    lock=os.open(directory/'.desktop-maintenance.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,0o600)
    try:
        info=os.fstat(lock)
        if not stat.S_ISREG(info.st_mode) or info.st_uid!=0 or stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1:raise ValueError('Protected maintenance lock required')
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        now=int(time.time());value={'version':'codi-maintenance-notice/1','id':uuid.uuid4().hex,'phase':phase,'deadline':now+seconds,'expiresAt':now+seconds+duration,'message':message}
        fd,name=tempfile.mkstemp(prefix='.desktop-maintenance-',dir=directory)
        try:
            with os.fdopen(fd,'w') as output:output.write(json.dumps(value)+'\n');output.flush();os.fchmod(output.fileno(),0o644);os.fsync(output.fileno())
            os.replace(name,directory/'desktop-maintenance.json')
            folder=os.open(directory,os.O_RDONLY|os.O_DIRECTORY);os.fsync(folder);os.close(folder)
        finally:
            if Path(name).exists():Path(name).unlink()
        return {'status':'published','notice':value,'servicesRestarted':False,'workSaved':False}
    finally:os.close(lock)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True,type=Path);p.add_argument('phase',choices=['scheduled','active','cancelled']);p.add_argument('--in-seconds',type=int,default=0);p.add_argument('--duration',type=int,default=3600);p.add_argument('--message',default='Server restarting for maintenance. Please save your work.');a=p.parse_args()
    if not 0<=a.in_seconds<=86400 or not 1<=a.duration<=86400 or not 1<=len(a.message)<=500:p.error('Bounded countdown, duration and message required')
    print(json.dumps(publish(a.directory,a.phase,a.in_seconds,a.message,a.duration),indent=2))
