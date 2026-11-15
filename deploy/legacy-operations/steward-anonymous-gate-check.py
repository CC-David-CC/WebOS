#!/usr/bin/env python3
"""Real signed registered/anonymous WebSockets exercise the introduction gate."""
import asyncio,json,secrets,time,types,uuid,os,tempfile,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
m=types.ModuleType('steward_fixture');m.__file__=str(ROOT/'scripts/steward-network-check.py');exec((ROOT/'scripts/steward-network-check.py').read_text().split('async def main():',1)[0],m.__dict__)
async def run():
 spec=importlib.util.spec_from_file_location('serve_steward',ROOT/'scripts/serve-steward.py');operator=importlib.util.module_from_spec(spec);spec.loader.exec_module(operator);temporary=tempfile.TemporaryDirectory(prefix='codi-gate-wire-');policyfile=Path(temporary.name)/'policy';policyfile.write_text('enabled\n');policyfile.chmod(0o644)
 args,scope,port,root,seed=m.fixture();issuer=m.key();policy={'mode':'server','issuer':'https://fixture.invalid','audience':'codi-peer/1','authorityKeys':[{'kid':'issuer','jwk':m.jose.public_jwk(issuer)}]};args['identity_policy']=policy;server=m.StewardServer(**args);await server.start(port);watcher=asyncio.create_task(operator.watch_anonymous_policy(server,policyfile,owner=os.getuid()));clients=[];checks=[];result={'status':'FAIL','checks':checks,'productionChanged':False}
 def signed(kind):
  c=m.Client(args,scope);ident=c.identity;ident['kind']=kind;ident['sub']=('user:'+str(uuid.uuid4())) if kind=='registered' else ('anon:'+str(uuid.uuid4()));now=int(time.time());claims={'v':1,'iss':policy['issuer'],'aud':policy['audience'],**{k:ident[k] for k in ['sid','sub','kind','name']},'cnf':{'jwk':ident['key']},'iat':now,'nbf':now,'exp':now+600,'jti':str(uuid.uuid4())};ident['certificate']=m.jose.sign(claims,issuer,'codi-identity+jwt',kid='issuer');clients.append(c);return c
 def check(name,value):assert value,name;checks.append(name);print(name,flush=True)
 try:
  anon,registered=signed('anonymous'),signed('registered');await anon.open();await registered.open();await anon.register();await registered.register();check('anonymous and registered introductions work when enabled',len(server.registry.owners)==2)
  policyfile.write_text('disabled\n');await asyncio.sleep(1.3);check('disabling closes existing anonymous introduction sessions with a retryable code',len(server.registry.owners)==1 and anon.ws.close_code==1013 and all(c.public['kind']=='registered' for _,c in server.clients.values()))
  fresh=signed('anonymous');denied=False
  try:await fresh.open()
  except Exception:denied=True
  check('new anonymous introductions are refused with a retryable code',denied and fresh.ws.close_code==1013)
  response=await registered.call('JOIN_LOOKUP',{'lease_id':next(iter(server.registry.leases)),'limit':4});check('existing registered session remains usable',response.get('leases')==[])
  policyfile.write_text('enabled\n');await asyncio.sleep(1.3);again=signed('anonymous');await again.open();await again.register();check('re-enabling permits new anonymous introductions',len(server.registry.owners)==2)
  result['status']='PASS'
 finally:
  for client in clients:
   if hasattr(client,'ws'):await client.close()
  watcher.cancel();await asyncio.gather(watcher,return_exceptions=True);await server.close();temporary.cleanup();result['registry']=server.registry.snapshot();out=ROOT/'.build/checks/steward-anonymous-gate-r1-result.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':asyncio.run(run())
