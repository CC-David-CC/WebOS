"""Journaled one-epoch recovery coordinator, with explicit backend boundary.

The backend must hold the installed instance lock for the entire run and
independently enforce protected paths, pins, signatures, fence, key custody,
publisher floor and service identity. This module never restores data. It is
not an installed-system adapter or a command to run against a live server.
"""
import ctypes,json,os,re,stat,tempfile
from pathlib import Path
from steward.protocol import jose

_HEX=re.compile(r'[0-9a-f]{64}\Z')

class RecoveryJournal:
    """One immutable write-ahead record under an owner-only directory."""
    def __init__(self,path):
        self.path=Path(path)
        if not self.path.is_absolute() or '..' in self.path.parts:raise ValueError('Absolute journal path required')
        p=self.path.parent;info=p.lstat()
        if p.is_symlink() or not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.geteuid() or stat.S_IMODE(info.st_mode)!=0o700:raise ValueError('Owner-only journal directory required')
    @staticmethod
    def validate(record):
        if not isinstance(record,dict) or set(record)!={'version','checkpoint','configSHA256','releaseSHA256','publisherRevision','seconds'} or record['version']!='codi-expired-root-recovery/1':raise ValueError('Invalid recovery journal')
        checkpoint=record['checkpoint']
        if not isinstance(checkpoint,dict) or set(checkpoint)!={'version','baseRevision','seedHash','payloadHash','bindingHash','grantHash','rootKeyId','realm'} or checkpoint['version']!='codi-expired-root-checkpoint/1':raise ValueError('Invalid signed checkpoint')
        if type(checkpoint['baseRevision']) is not int or not 1<=checkpoint['baseRevision']<2**53-2 or type(record['publisherRevision']) is not int or not 1<=record['publisherRevision']<2**53-1:raise ValueError('Invalid durable revision')
        if type(record['seconds']) is not int or not 30<=record['seconds']<=86400:raise ValueError('Bounded journaled authority lifetime required')
        if any(not isinstance(record[k],str) or not _HEX.fullmatch(record[k]) for k in ['configSHA256','releaseSHA256']):raise ValueError('Exact immutable pins required')
        if any(not isinstance(checkpoint[k],str) or not _HEX.fullmatch(checkpoint[k]) for k in ['seedHash','bindingHash','grantHash']):raise ValueError('Exact checkpoint hashes required')
        if not isinstance(checkpoint['payloadHash'],str) or not re.fullmatch(r'[A-Za-z0-9_-]{43}',checkpoint['payloadHash']):raise ValueError('Exact publisher seed fingerprint required')
        if any(not isinstance(checkpoint[k],str) or not 1<=len(checkpoint[k])<=256 for k in ['rootKeyId','realm']):raise ValueError('Bounded checkpoint identity required')
        return record
    def load(self):
        fd=os.open(self.path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
        try:
            info=os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_uid!=os.geteuid() or stat.S_IMODE(info.st_mode)!=0o600 or info.st_size>16384:raise ValueError('Protected recovery journal required')
            with os.fdopen(fd,'rb') as file:fd=-1;raw=file.read(16385)
            if len(raw)>16384:raise ValueError('Recovery journal too large')
            return self.validate(jose.loads(raw))
        finally:
            if fd>=0:os.close(fd)
    def create(self,record):
        raw=(json.dumps(self.validate(record),sort_keys=True,indent=2)+'\n').encode()
        # Write and fsync the complete file, then install it without replacing
        # an existing journal. Linux renameat2 makes the name change atomic.
        fd,name=tempfile.mkstemp(prefix='.expired-root-',dir=self.path.parent)
        try:
            with os.fdopen(fd,'wb') as out:os.fchmod(out.fileno(),0o600);out.write(raw);out.flush();os.fsync(out.fileno())
            libc=ctypes.CDLL(None,use_errno=True);rename=libc.renameat2;rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];rename.restype=ctypes.c_int
            if rename(-100,os.fsencode(name),-100,os.fsencode(self.path),1)!=0:
                error=ctypes.get_errno();raise OSError(error,os.strerror(error),str(self.path))
            self._sync()
        finally:
            try:os.unlink(name)
            except FileNotFoundError:pass
    def remove(self,expected):
        if self.load()!=expected:raise ValueError('Recovery journal changed')
        self.path.unlink();self._sync()
    def _sync(self):
        fd=os.open(self.path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
        try:os.fsync(fd)
        finally:os.close(fd)

def execute(backend,journal,*,resume=False,phase=lambda name:None):
    """Run one explicitly scoped epoch; a failure leaves its journal intact.

    backend.initial() returns a verified journal record, decide(record) returns
    a validated next action, verify(record) checks all preserved invariants,
    and receipt(record) idempotently and durably records success. Mutations occur only under its
    lock. Resume observes signed state anew; it never retries a committed epoch.
    """
    with backend.locked():
        if resume:record=journal.load()
        else:
            record=RecoveryJournal.validate(backend.initial())
            if backend.decide(record)!='renew-once':raise ValueError('Fresh recovery requires one expired, stopped authority')
            journal.create(record);phase('prepared')
        for _ in range(4):
            action=backend.decide(record)
            if action=='verify-running':
                backend.verify(record);phase('verified');backend.receipt(record);phase('receipt');journal.remove(record)
                return {'status':'recovered','rootRevision':record['checkpoint']['baseRevision']+1}
            if action not in ('renew-once','export-committed','start-steward'):raise ValueError('Unsupported recovery step')
            phase('before-'+action)
            getattr(backend,{'renew-once':'renew','export-committed':'export','start-steward':'start'}[action])(record)
            phase('after-'+action)
        raise ValueError('Recovery did not converge within the bounded steps')
