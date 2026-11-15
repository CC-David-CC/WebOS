"""Isolated subprocess fixture; exits at a named real store publication phase."""
import json,os,sys
from pathlib import Path
from aiohttp import web
root=Path(__file__).resolve().parents[2]/'active-system';sys.path.insert(0,str(root))
from gateway_service.user_store import UserStore
from gateway_service.http import FileGateway
state,data,policy_path,port,phase=sys.argv[1:]
store=UserStore(Path(state),Path(data));original=store.put_stream
def crash(*args,**kwargs):
 kwargs['phase']=lambda current:os._exit(73) if current==phase else None
 return original(*args,**kwargs)
store.put_stream=crash
gateway=FileGateway(store,json.loads(Path(policy_path).read_text()))
web.run_app(gateway.app(),host='127.0.0.1',port=int(port),access_log=None,print=None,handle_signals=False)
