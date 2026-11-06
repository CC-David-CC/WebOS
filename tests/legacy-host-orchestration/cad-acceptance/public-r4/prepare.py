"""Prepare fixed-R4 HTTPS drivers; never executes browser/account tests."""
import argparse,hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCES={
 'agent-tools-public.cjs':('ec4da121d822a594ab2ac3c58b052240ab87037e','research/beta-cad-agent-tools-20261106/browser.cjs','e79278314e52cdd8fd5b35d5f8e110fbf94668c8689a54994f2682697062ba3e'),
 'recipes-public.cjs':('6ff4261b199636d85965e37671f95e161fc85e15','research/beta-cad-agent-recipes-20261106/browser.cjs','50e23ce5f772951d46d241bc41f996a6d57ff703096823b896f6b2480a25a32a')}
sha=lambda b:hashlib.sha256(b).hexdigest()
def prepare(repo,package,out):
 repo=repo.resolve(strict=True);package=package.resolve(strict=True);out=out.absolute()
 if out.exists() or out.is_symlink():raise ValueError('Fresh output directory required')
 metadata=json.loads((package/'package.json').read_bytes());assert metadata['version']=='24.35.0'
 module=(package/metadata['exports']['.']['require']).resolve(strict=True);assert module.is_file() and module.is_relative_to(package)
 dependency={'package':'puppeteer-core','version':metadata['version'],'modulePath':str(module),'moduleURI':module.as_uri(),'moduleSHA256':sha(module.read_bytes())}
 out.mkdir(mode=0o700);records={}
 for name,(commit,file,pin) in SOURCES.items():
  raw=subprocess.check_output(['git','-C',str(repo),'show',commit+':'+file]);assert sha(raw)==pin
  text=raw.decode();changes=[]
  def replace(before,after,count=1):
   nonlocal text
   assert text.count(before)==count,(name,before,text.count(before),count)
   text=text.replace(before,after);changes.append({'before':before,'after':after,'count':count})
  replace('require(process.env.PUPPETEER_CORE_PATH)','require('+json.dumps(str(module))+')')
  header="const {assertPublicCandidate,requiredPublicInputs,verifyMountedCad}=require("+json.dumps(str(HERE/'preflight.cjs'))+");requiredPublicInputs();\n"
  if name=='agent-tools-public.cjs':
   replace("for(const u of[base,cdp])assert.equal(u.hostname,'127.0.0.1');","assert.equal(base.href,'https://beta.ksu.codes/');assert.ok(['127.0.0.1','localhost','[::1]'].includes(cdp.hostname));")
   replace('(async()=>{const browser=await puppeteer.connect(', '(async()=>{const preflight=await assertPublicCandidate();receipt.preflight=preflight;const browser=await puppeteer.connect(')
   launch="await p.evaluate(()=>surfaces.get('Desktop').launch('jsketcher'));await p.waitForFunction(()=>document.querySelector('.jsketcher-app .app-status')?.textContent.startsWith('New model.'),{timeout:90000});"
   actual="await p.locator('.app-menu-button').click();await click(p,'.menu-pane button','3D Printing');await click(p,'.menu-pane button','CAD Modeler (JSketcher inspired)');await p.waitForFunction(()=>document.querySelector('.jsketcher-app .app-status')?.textContent.startsWith('New model.'),{timeout:90000});assert.equal(await p.$eval('.jsketcher-app',e=>e.closest('.window').querySelector('.caption-text').textContent),'CAD Modeler (JSketcher inspired)');receipt.runtime=await verifyMountedCad(p);"
   replace(launch,actual)
  else:
   replace("assert.equal(base.href,'http://127.0.0.1:20415/');","assert.equal(base.href,'https://beta.ksu.codes/');")
   for before,after in [('a6ed7b3986010e56c2cc52b6e8cef07febaaa7b5dcb17f5cb625627e5bf6397d','337b69de24aa84f726a5d3cedb8f16f7ade026baa206b4faa31281ff380d827e'),('e80f04ca34f3e6b011714cb32709e824b0f00a07','29fea20659f27f0cb212bf520b210f0311ad962f'),('0e537d784b197a4bf92e48566a79fe56888d8915bf3e4e25f43aaa8b5c038d28','d90e75bbb67daa69ca1479ecb21165bfb0f0762dc87cf2caf7a5f2265db465ac'),('eefb4209cd1c26611ab54844d6de4518cf4ab47ac3567c447c4024b6de6f1cce','966dc8f53c2968e6598cb804bfc947241dc01ea087627fa64e4d81124a006c99'),('Exact R3 shell/registry checked before test-account registration','Exact R4 shell/registry checked before test-account registration')]:replace(before,after)
   replace(' const preflight=[];',' await assertPublicCandidate();\n const preflight=[];')
   launch="async function launch(p){await p.evaluate(()=>surfaces.get('Desktop').launch('jsketcher'));await p.waitForFunction(()=>document.querySelector('.jsketcher-app .app-status')?.textContent.startsWith('New model.'),{timeout:90000});}"
   actual="async function launch(p){await p.locator('.app-menu-button').click();for(const label of ['3D Printing','CAD Modeler (JSketcher inspired)']){let found=false;for(const button of await p.$$('.menu-pane button'))if((await button.evaluate(e=>e.textContent)).trim()===label){await button.click();found=true;break;}assert.ok(found,'Actual Applications control: '+label);}await p.waitForFunction(()=>document.querySelector('.jsketcher-app .app-status')?.textContent.startsWith('New model.'),{timeout:90000});assert.equal(await p.$eval('.jsketcher-app',e=>e.closest('.window').querySelector('.caption-text').textContent),'CAD Modeler (JSketcher inspired)');(receipt.runtimes??=[]).push(await verifyMountedCad(p));}"
   replace(launch,actual)
  # Add only prerequisites outside the preserved source body. Every transform
  # is recorded and reversible; no geometry/file/refusal assertion is removed.
  text=header+text;output=text.encode();(out/name).write_bytes(output)
  assert text.count('assert.')>=raw.decode().count('assert.')
  assert 'browser.close(' not in text
  records[name]={'sourceCommit':commit,'sourceFile':file,'sourceSHA256':pin,'driverSHA256':sha(output),'header':header,'transformations':changes,'originalAssertionReferences':raw.decode().count('assert.'),'preparedAssertionReferences':text.count('assert.'),'testDependency':dependency}
 packet={'status':'PREPARED_NOT_EXECUTED','origin':'https://beta.ksu.codes/','source':'29fea20659f27f0cb212bf520b210f0311ad962f','artifact':'337b69de24aa84f726a5d3cedb8f16f7ade026baa206b4faa31281ff380d827e','helperSHA256':sha((HERE/'preflight.cjs').read_bytes()),'records':records}
 (out/'driver-pins.json').write_text(json.dumps(packet,indent=2)+'\n')
 env={'CODI_TEST_URL':packet['origin'],'CODI_TEST_CDP':'http://127.0.0.1:19329/','CODI_SOURCE_PIN':packet['source'],'CODI_ARTIFACT_PIN':packet['artifact'],'CODI_DESKTOP_REPO':str(repo)}
 (out/'public-test-env.json').write_text(json.dumps(env,indent=2)+'\n');return packet
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--puppeteer-package',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(prepare(a.repo,a.puppeteer_package,a.out),indent=2))
