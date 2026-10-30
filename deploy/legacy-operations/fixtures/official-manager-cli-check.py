#!/usr/bin/env python3
"""Exercise candidate CLI parsing and dispatch without changing system services."""
import contextlib,importlib.util,io,sys
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];release=ROOT/'.build/releases/official-recovery-profile26-candidate-r4'
sys.path.insert(0,str(release));sys.path.insert(0,str(release/'codiserver-server-v0.3.0'))
spec=importlib.util.spec_from_file_location('official_manager_fixture',release/'scripts/manage-services.py');manager=importlib.util.module_from_spec(spec);sys.modules[spec.name]=manager;spec.loader.exec_module(manager)
from origin_service import official_management,signin_migration,maintenance
base=['manage-services.py','configure-official-channels','--config','/fixture/config']
def invoke(args,result=None):
 with patch.object(sys,'argv',base+args),patch.object(manager.os,'geteuid',return_value=0),patch.object(manager,'path'),patch.object(manager,'locked',return_value=contextlib.nullcontext()),patch.object(manager,'load',return_value={'version':'codi-managed-instance/5'}),patch.object(signin_migration,'guard'),patch.object(maintenance,'require_clean'),patch.object(official_management,'configure',return_value=result or {'status':'official-switch-configured'}) as configure,contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
  try:manager.main();code=0
  except SystemExit as e:code=e.code
  return code,configure.call_args
code,call=invoke([]);assert code!=0 and call is None
code,call=invoke(['--disable','--backend-port','8888']);assert code!=0 and call is None
code,call=invoke(['--disable']);assert code==0 and call.args[3] is False
args=['--backend-port','8888','--backend-unit','official.service','--backend-unit-path','/unit','--backend-unit-sha256','0'*64,'--backend-uid','123','--backend-argv=/python','--backend-argv=-I']
code,call=invoke(args);assert code==0 and call.args[3] is True and call.kwargs['backend_custody']['argv']==['/python','-I']
code,call=invoke(args,{'status':'official-switch-rolled-back'});assert code==1
print('PASS: enable and disable dispatch, missing/conflicting pins, rollback exit status (mocked system effects)')
