#!/usr/bin/env python3
"""Run the active computer and its guest Internet relay on loopback."""
import argparse,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=8130);args=p.parse_args()
if not 1<=args.port<=65535:p.error('Port must be 1..65535')
python=ROOT/'.venv/bin/python'
if not python.exists():p.error('Create .venv and install requirements.lock first; see README.md')
os.chdir(ROOT)
os.execv(str(python),[str(python),str(ROOT/'guest-relay/server.py'),'--port',str(args.port),'--origin','http://127.0.0.1:'+str(args.port)])
