#!/usr/bin/env python3
"""Run the exact sealed issuer with test-only short session lifetimes."""
import os,runpy,sys
from pathlib import Path
release=Path(os.environ['CODI_ISSUER']).resolve(strict=True)
sys.path.insert(0,str(release/'codiserver-server-v0.3.0'));sys.path.insert(0,str(release))
import codiauth.service as service
original=service.Config
def config(*args,**kwargs):return original(*args,certificate_seconds=40,session_seconds=90,**kwargs)
service.Config=config
script=release/'scripts/serve-connected.py';sys.argv[0]=str(script);runpy.run_path(str(script),run_name='__main__')
