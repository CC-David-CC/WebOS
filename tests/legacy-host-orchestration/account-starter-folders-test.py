import sys
import tempfile
import time
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'active-system'))
from gateway_service.policy import Principal, Denied
from gateway_service.user_store import UserStore, DEFAULT_ACCOUNT_FOLDERS

class StarterFolders(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.state, self.data = root / 'state', root / 'data'
        self.state.mkdir(mode=0o700); self.data.mkdir(mode=0o700)
        self.a = Principal('user:' + str(uuid.uuid4()), 'a', 'registered', {}, int(time.time()) + 600)
        self.b = Principal('user:' + str(uuid.uuid4()), 'b', 'registered', {}, int(time.time()) + 600)
        self.store = UserStore(self.state, self.data, initial_folders=DEFAULT_ACCOUNT_FOLDERS)
    def tearDown(self): self.temp.cleanup()
    def test_once_private_isolated_and_user_controlled(self):
        self.store.ensure_user(self.a); self.store.ensure_user(self.b)
        a = self.data / 'users' / uuid.UUID(self.a.sub[5:]).hex
        b = self.data / 'users' / uuid.UUID(self.b.sub[5:]).hex
        self.assertEqual({p.name for p in a.iterdir()}, set(DEFAULT_ACCOUNT_FOLDERS))
        self.assertTrue(all(p.is_dir() and p.stat().st_mode & 0o777 == 0o700 for p in a.iterdir()))
        self.store.put(self.a, 'Digital Projects/note.txt', b'hello')
        with self.assertRaises(FileNotFoundError): self.store.read(self.b, 'Digital Projects/note.txt')
        self.store.delete(self.a, 'Games'); self.store.ensure_user(self.a)
        self.assertFalse((a / 'Games').exists()); self.assertTrue((b / 'Games').is_dir())
    def test_interrupted_setup_resumes_without_adopting_data(self):
        def crash(phase):
            if phase == 'starter-folder-created': raise RuntimeError('interrupted')
        with self.assertRaises(RuntimeError): self.store.ensure_user(self.a, phase=crash)
        self.store.ensure_user(self.a)
        a = self.data / 'users' / uuid.UUID(self.a.sub[5:]).hex
        self.assertEqual({p.name for p in a.iterdir()}, set(DEFAULT_ACCOUNT_FOLDERS))
        with self.assertRaises(RuntimeError): self.store.ensure_user(self.b, phase=crash)
        b = self.data / 'users' / uuid.UUID(self.b.sub[5:]).hex
        (next(b.iterdir()) / 'unexpected').write_text('keep')
        with self.assertRaises(ValueError): self.store.ensure_user(self.b)
        self.assertTrue((next(b.iterdir()) / 'unexpected').exists())
    def test_capacity_checked_before_seed(self):
        with self.assertRaises(ValueError): UserStore(self.state, self.data, per_user_entries=2, initial_folders=DEFAULT_ACCOUNT_FOLDERS)
        store = UserStore(self.state, self.data, per_user_entries=7, total_entries=7, initial_folders=DEFAULT_ACCOUNT_FOLDERS)
        store.ensure_user(self.a)
        with self.assertRaises(Denied): store.ensure_user(self.b)

if __name__ == '__main__': unittest.main()
