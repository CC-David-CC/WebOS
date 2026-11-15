#!/usr/bin/env python3
"""Retain exact existing UI cleanup oracle and capture both budget samples."""
import argparse
import importlib.util
import json
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('directory_ui_probe',ROOT/'scripts/hosted-native-ui-check.py');ui=importlib.util.module_from_spec(s);s.loader.exec_module(ui)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
samples=[];original=ui.driver.call
def capture(path,data=None,method=None):
 value=original(path,data,method)
 if path.endswith('/execute/async') and data and 'return await desktopNetwork.stats();' in data.get('script',''):
  samples.append(value)
 return value
ui.driver.call=capture
value=ui.run(a.release.resolve());value['lifecycleBudgetSamples']=samples;value['diagnosticSourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
a.output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':value['status'],'checks':len(value['checks']),'error':value.get('error'),'samples':samples},indent=2))
raise SystemExit(0 if value['status']=='PASS' else 1)
