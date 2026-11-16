"""Execute only genuine noncandidate-byte refusal with browser-denial guard."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--drivers',type=Path,required=True);p.add_argument('--node',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();here=Path(__file__).resolve().parent
records=json.loads((a.drivers/'driver-pins.json').read_bytes());settings=json.loads((a.drivers/'public-test-env.json').read_bytes());a.output.mkdir(parents=True,exist_ok=True);rows=[]
for name,meta in records['records'].items():
 metrics=a.output/(name+'.gate.json');log=a.output/(name+'.gate.log')
 with tempfile.TemporaryDirectory(prefix='codi-public-gate-no-browser-') as temp:
  env={**os.environ,**settings,'CODI_TEST_CDP':'http://127.0.0.1:1/','CODI_RECEIPT':str(Path(temp)/'refusal.json'),'CODI_OUTPUT_DIR':temp,'CODI_GATE_PUPPETEER':meta['testDependency']['modulePath'],'CODI_GATE_OUTPUT':str(metrics.resolve())}
  r=subprocess.run([str(a.node),'-r',str(here/'gate-preload.cjs'),str((a.drivers/name).resolve())],env=env,text=True,capture_output=True,timeout=60);log.write_text(r.stdout+r.stderr)
  data=json.loads(metrics.read_bytes());assert r.returncode==1,(name,r.returncode,r.stdout,r.stderr);assert 'R4 candidate must be active before browser connection or test-account registration: /app.js?simplified=1' in r.stdout+r.stderr,(name,r.stdout,r.stderr)
  assert data['browserConnectAttempts']==data['browserContextsCreated']==data['accountsCreated']==0
  assert len(data['requests'])>=1 and all(x['method']=='GET' for x in data['requests'])
  rows.append({'driver':name,'result':'EXPECTED_NONCANDIDATE_REFUSAL','exitCode':r.returncode,'actualReadOnlyRequests':data['requests'],'browserConnectAttempts':0,'accountsCreated':0})
result={'status':'PASS','scope':'Real current public static GETs refuse before browser/account activity; no public functional test executed','targetArtifact':records['artifact'],'rows':rows}
(a.output/'gate-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
