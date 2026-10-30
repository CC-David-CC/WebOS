#!/usr/bin/env python3
"""Compare bounded scratch screening against the browser's content codec."""
import base64,copy,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from steward.official_content import validate_scratch_node

def ident(s):return base64.urlsafe_b64encode(hashlib.sha256(s.encode()).digest()).rstrip(b'=').decode()
channel,genesis,other=map(ident,['channel','genesis','other']);p='codi-channel-content/1'
link={'cid':ident('link'),'bytes':4,'height':0}
base=[{'profile':p,'kind':'chunk','data':'dGVzdA'},{'profile':p,'kind':'blob','bytes':4,'tree':link},{'profile':p,'kind':'parts','links':[link]},{'profile':p,'kind':'head','channel':channel,'genesisHash':genesis,'height':1,'head':ident('head'),'parent':None,'block':ident('block')}]
cases=[]
def add(v):cases.append(v if isinstance(v,str) else json.dumps(v,separators=(',',':')))
for n in base:
 add(n)
 for key in list(n):
  x=copy.deepcopy(n);del x[key];add(x)
  x=copy.deepcopy(n);x[key]=None;add(x)
 x=copy.deepcopy(n);x['extra']=1;add(x)
for data in ['', 'A','AB','dGVzdA=', '!', 'eA', 'é','eA'*6000]:
 x=copy.deepcopy(base[0]);x['data']=data;add(x)
for val in [0,-1,1.5,1.0,True,9007199254740992]:
 x=copy.deepcopy(base[3]);x['height']=val;add(x)
for field in ['channel','genesisHash']:
 x=copy.deepcopy(base[3]);x[field]=other;add(x)
for val in [[],[link]*65,[{**link,'bytes':0}],[{**link,'height':3}],[link,{**link,'height':1}]]:
 x=copy.deepcopy(base[2]);x['links']=val;add(x)
add('{"profile":"codi-channel-content/1","kind":"chunk","data":"eA","data":"eQ"}')
for raw in ['{}','null','[]','{"profile":NaN}','{"profile":"codi-channel-content/1","kind":"chunk","data":"\\ud800"}'] :add(raw)
x=copy.deepcopy(base[3]);x['height']=10**400;add(x)
rows=[{'wire':w,'channel':channel,'genesis':genesis} for w in cases]
node=ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node';result=subprocess.run([str(node),str(ROOT/'scripts/fixtures/official-content-browser-parity.mjs')],input=json.dumps(rows),text=True,capture_output=True,check=True);browser=json.loads(result.stdout)
server=[]
for w in cases:
 try:validate_scratch_node(w,channel,genesis);server.append(True)
 except (ValueError,UnicodeError):server.append(False)
diff=[{'case':i,'browser':browser[i],'server':server[i],'wire':cases[i][:400]} for i in range(len(cases)) if browser[i]!=server[i]]
print(json.dumps({'status':'PASS' if not diff else 'FAIL','cases':len(cases),'differences':diff},indent=2));raise SystemExit(bool(diff))
