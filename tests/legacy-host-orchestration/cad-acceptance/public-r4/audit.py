"""Reconstruct every prepared body from pinned accepted originals; no execution."""
import argparse,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--drivers',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();sha=lambda b:hashlib.sha256(b).hexdigest();here=Path(__file__).resolve().parent
packet=json.loads((a.drivers/'driver-pins.json').read_bytes());assert sha(a.manifest.read_bytes())==packet['artifact'];manifest=json.loads(a.manifest.read_bytes());assert manifest['desktopSource']==packet['source'];rows=[]
helper=(here/'preflight.cjs').read_text();assert sha(helper.encode())==packet['helperSHA256']
for url,key in [('/app.js?simplified=1','shell/app.js'),('/desktop-apps.js?simplified=1','shell/desktop-apps.js')]:assert "['"+url+"','"+manifest['files'][key]['sha256']+"']" in helper
assert manifest['commandRegistrySHA256'] in helper and "redirect:'error'" in helper and "pins.origin" in helper
for name,row in packet['records'].items():
 raw=subprocess.check_output(['git','-C',str(a.repo),'show',row['sourceCommit']+':'+row['sourceFile']]);assert sha(raw)==row['sourceSHA256'];text=raw.decode()
 for change in row['transformations']:assert text.count(change['before'])==change['count'];text=text.replace(change['before'],change['after'])
 expected=row['header']+text;actual=(a.drivers/name).read_text();assert actual==expected and sha(actual.encode())==row['driverSHA256']
 assert actual.count('assert.')==row['preparedAssertionReferences']>=row['originalAssertionReferences'];assert actual.index('await assertPublicCandidate()')<actual.index('puppeteer.connect(')
 assert 'browser.close(' not in actual and 'browser.disconnect()' in actual and 'browser.createBrowserContext()' in actual
 dependency=row['testDependency'];assert dependency['version']=='24.35.0';assert sha(Path(dependency['modulePath']).read_bytes())==dependency['moduleSHA256']
 rows.append({'driver':name,'sourceSHA256':row['sourceSHA256'],'driverSHA256':row['driverSHA256'],'originalAssertionReferences':row['originalAssertionReferences'],'preparedAssertionReferences':row['preparedAssertionReferences'],'onlyRecordedTransforms':True})
result={'status':'PASS','scope':'Read-only exact body/dependency/preflight audit, not functional browser execution','artifact':packet['artifact'],'helperSHA256':packet['helperSHA256'],'rows':rows}
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
