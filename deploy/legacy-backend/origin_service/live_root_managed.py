"""Managed live renewal adapter, source-only until packaged and tested."""
from pathlib import Path
from origin_service.expired_root_managed import ManagedExpiredRoot
from origin_service.live_root_renewal import inspect
from steward.protocol import jose
from steward.root_authority import RootAuthority


class ManagedLiveRenewal(ManagedExpiredRoot):
 def __init__(self,*args,renewal_window=21600,**kwargs):
  super().__init__(*args,**kwargs)
  if type(renewal_window) is not int or not 1<=renewal_window<self.seconds:raise ValueError('Invalid live renewal window')
  self.renewal_window=renewal_window
 def initial(self):
  record=super().initial();c=self._config();baseline=RootAuthority(Path(c['stateRoot'])/'operator/root').provision()
  return {**record,'version':'codi-live-root-renewal/1','baseline':jose.dumps(baseline),'renewalWindow':self.renewal_window}
 def _config(self,record=None):
  if record and record.get('renewalWindow')!=self.renewal_window:raise ValueError('Journaled renewal window changed')
  return super()._config(record)
 def classify(self,record,root,staged,live,fence,running):
  return inspect(jose.loads(record['baseline']),root,staged,live,record['checkpoint'],fence_revision=fence,now=int(self.clock()),steward_running=running,ledger_verified=True,renewal_window=self.renewal_window)
 def renew(self,record):
  c,_,_,action=self._snapshot(record)
  if action!='renew-once':raise ValueError('Live authority changed before renewal')
  self.op.publish(c,'renew',self.seconds,self.path)
 def export(self,record):
  c,_,_,action=self._snapshot(record)
  if action!='export-committed':raise ValueError('Live authority changed before export')
  self.op.publish(c,'export',None,self.path)
 def receipt(self,record):
  target=self.path.parent/('live-root-'+str(record['checkpoint']['baseRevision']+1)+'-receipt.json')
  raw=(jose.dumps({'version':'codi-live-root-renewal-receipt/1','rootRevision':record['checkpoint']['baseRevision']+1,'configSHA256':record['configSHA256'],'releaseSHA256':record['releaseSHA256'],'publisherFloor':record['publisherRevision'],'rootKeyId':record['checkpoint']['rootKeyId']})+'\n').encode()
  if target.exists() or target.is_symlink():
   if self.op.read_owned(target,0,0o600)!=raw:raise ValueError('Existing live renewal receipt differs')
  else:self.op.atomic(target,raw)
