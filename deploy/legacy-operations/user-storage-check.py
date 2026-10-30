#!/usr/bin/env python3
"""Exercise private storage using real disk, SQLite, process death and races."""
import concurrent.futures
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gateway_service.policy import Denied, Principal
from gateway_service.user_store import UserStore

ALICE = Principal('user:11111111-1111-4111-8111-111111111111', 'session-a', 'registered', {}, 4102444800)
BOB = Principal('user:22222222-2222-4222-8222-222222222222', 'session-b', 'registered', {}, 4102444800)
ANON = replace(ALICE, kind='anonymous', sub='anon:33333333-3333-4333-8333-333333333333')

class Storage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='codi-storage-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = self.root / 'state';self.data = self.root / 'data'
        self.state.mkdir(mode=0o700);self.data.mkdir(mode=0o700)
        self.store = UserStore(self.state, self.data, per_user_bytes=128, per_user_entries=8, total_bytes=192, total_entries=12)

    def home(self, principal=ALICE):
        return self.data / 'users' / principal.sub[5:].replace('-', '')

    def reopen(self):
        self.set_store = UserStore(self.state, self.data, per_user_bytes=128, per_user_entries=8, total_bytes=192, total_entries=12)
        return self.set_store

    def crash(self, fn, phase):
        child = os.fork()
        if child == 0:
            try:
                fn(lambda stage: os._exit(73) if stage == phase else None)
            except BaseException:
                os._exit(74)
            os._exit(75)
        _, status = os.waitpid(child, 0)
        self.assertEqual(os.waitstatus_to_exitcode(status), 73)

    def test_anonymous_creates_no_row_or_folder(self):
        for operation in [lambda: self.store.ensure_user(ANON), lambda: self.store.put(ANON, 'file', b'private'), lambda: self.store.list(ANON)]:
            with self.assertRaises(Denied):operation()
        with self.store.db() as db:self.assertEqual(db.execute('SELECT count(*) FROM users').fetchone()[0], 0)
        self.assertEqual(list((self.data / 'users').iterdir()), [])

    def test_expired_identity_does_not_allocate(self):
        with self.assertRaises(Denied):self.store.ensure_user(replace(ALICE, deadline=0))
        self.assertFalse(self.home().exists())

    def test_stable_account_across_sessions_and_restart(self):
        first = self.store.ensure_user(ALICE)
        self.store.put(ALICE, 'note.txt', b'hello')
        other = replace(ALICE, sid='different-device')
        self.assertEqual(self.reopen().ensure_user(other), first)
        self.assertEqual(self.reopen().read(other, 'note.txt')['bytes'], b'hello')
        self.assertEqual(self.home().stat().st_mode & 0o777, 0o700)
        self.assertEqual((self.home() / 'note.txt').stat().st_mode & 0o777, 0o600)

    def test_accounts_cannot_read_each_others_files(self):
        self.store.ensure_user(ALICE);self.store.ensure_user(BOB)
        self.store.put(ALICE, 'private.txt', b'alice')
        self.store.put(BOB, 'private.txt', b'bob')
        self.assertEqual(self.store.read(ALICE, 'private.txt')['bytes'], b'alice')
        self.assertEqual(self.store.read(BOB, 'private.txt')['bytes'], b'bob')
        with self.assertRaises(Denied):self.store.read(BOB, '../' + self.home().name + '/private.txt')

    def test_unallocated_registered_user_cannot_write(self):
        with self.assertRaises(Denied):self.store.put(ALICE, 'file', b'data')
        self.assertFalse(self.home().exists())

    def test_private_admin_cli_is_idempotent_and_rejects_nonaccounts(self):
        command = [sys.executable, '-I', '-B', str(ROOT/'scripts/storage-admin.py'), '--state-root', str(self.state), '--data-root', str(self.data)]
        def invoke(subjects):
            return subprocess.run(command, input=json.dumps({'subjects': subjects}), text=True, capture_output=True, timeout=10)
        for bad in [ANON.sub, 'user:../../outside', ALICE.sub.upper()]:
            self.assertNotEqual(invoke([bad]).returncode, 0)
        self.assertFalse(self.home().exists())
        first = invoke([ALICE.sub, BOB.sub]);self.assertEqual(first.returncode, 0, first.stderr)
        second = invoke([ALICE.sub, BOB.sub]);self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(json.loads(first.stdout), json.loads(second.stdout))
        self.assertEqual(json.loads(first.stdout)['retainedRegisteredFolders'], 2)

    def test_permissions_are_durable_and_enforced(self):
        self.store.ensure_user(ALICE);self.store.put(ALICE, 'file', b'data')
        self.store.set_permission(ALICE.sub, 'read', False)
        with self.assertRaises(Denied):self.reopen().read(ALICE, 'file')
        self.store.set_permission(ALICE.sub, 'read', True)
        self.assertEqual(self.store.read(ALICE, 'file')['bytes'], b'data')
        self.store.set_permission(ALICE.sub, 'create', False)
        with self.assertRaises(Denied):self.store.put(ALICE, 'new', b'data')
        self.store.set_permission(ALICE.sub, 'delete', False)
        with self.assertRaises(Denied):self.store.delete(ALICE, 'file', previous_sha256=hashlib.sha256(b'data').hexdigest())

    def test_storage_disabled_without_deleting_data(self):
        self.store.ensure_user(ALICE);self.store.put(ALICE, 'file', b'data')
        self.store.set_enabled(ALICE.sub, False)
        for operation in [lambda: self.store.ensure_user(ALICE), lambda: self.store.read(ALICE, 'file'), lambda: self.store.list(ALICE)]:
            with self.assertRaises(Denied):operation()
        self.store.set_enabled(ALICE.sub, True)
        self.assertEqual(self.store.read(ALICE, 'file')['bytes'], b'data')

    def test_changed_version_cannot_overwrite_or_delete(self):
        self.store.ensure_user(ALICE)
        first = self.store.put(ALICE, 'file', b'first')
        with self.assertRaises(Denied):self.store.put(ALICE, 'file', b'duplicate')
        self.store.put(ALICE, 'file', b'second', previous_sha256=first['sha256'])
        for operation in [lambda: self.store.put(ALICE, 'file', b'lost', previous_sha256=first['sha256']), lambda: self.store.delete(ALICE, 'file', previous_sha256=first['sha256'])]:
            with self.assertRaises(Denied):operation()
        self.assertEqual(self.store.read(ALICE, 'file')['bytes'], b'second')

    def test_byte_quota_persists_across_reconnect(self):
        self.store.ensure_user(ALICE);self.store.put(ALICE, 'big', b'x' * 128)
        with self.assertRaises(Denied):self.reopen().put(replace(ALICE, sid='new'), 'overflow', b'x')
        self.assertFalse((self.home() / 'overflow').exists())

    def test_global_byte_quota(self):
        self.store.ensure_user(ALICE);self.store.ensure_user(BOB)
        self.store.put(ALICE, 'big', b'x' * 120)
        with self.assertRaises(Denied):self.store.put(BOB, 'big', b'x' * 80)
        self.store.put(BOB, 'fits', b'x' * 72)

    def test_entry_quotas_include_directories(self):
        self.store.ensure_user(ALICE);self.store.ensure_user(BOB)
        for n in range(8):self.store.mkdir(ALICE, 'd' + str(n))
        with self.assertRaises(Denied):self.store.put(ALICE, 'extra', b'')
        for n in range(4):self.store.put(BOB, 'file' + str(n), b'')
        with self.assertRaises(Denied):self.store.mkdir(BOB, 'extra')

    def test_account_capacity(self):
        store = UserStore(self.state, self.data, maximum_users=1)
        store.ensure_user(ALICE)
        with self.assertRaises(Denied):store.ensure_user(BOB)
        self.assertFalse(self.home(BOB).exists())

    def test_mkdir_rename_delete_and_listing(self):
        self.store.ensure_user(ALICE);self.store.mkdir(ALICE, 'drafts')
        saved = self.store.put(ALICE, 'drafts/hello', b'hello')
        self.store.rename(ALICE, 'drafts/hello', 'greeting', previous_sha256=saved['sha256'])
        self.assertEqual(self.store.list(ALICE, 'drafts'), [])
        self.store.delete(ALICE, 'drafts')
        self.assertEqual([x['name'] for x in self.store.list(ALICE)], ['greeting'])
        self.store.delete(ALICE, 'greeting', previous_sha256=saved['sha256'])
        self.assertEqual(self.store.list(ALICE), [])

    def test_rename_does_not_overwrite_destination(self):
        self.store.ensure_user(ALICE)
        first = self.store.put(ALICE, 'a', b'a');self.store.put(ALICE, 'b', b'b')
        with self.assertRaises(FileExistsError):self.store.rename(ALICE, 'a', 'b', previous_sha256=first['sha256'])
        self.assertEqual(self.store.read(ALICE, 'a')['bytes'], b'a')
        self.assertEqual(self.store.read(ALICE, 'b')['bytes'], b'b')

    def test_unsafe_paths(self):
        self.store.ensure_user(ALICE)
        for path in ['../outside', '/etc/passwd', 'a/../../outside', 'a//b', '.hidden', 'a\\b', '%2e%2e/escape', 'a\x00b']:
            with self.subTest(path=path), self.assertRaises(Denied):self.store.put(ALICE, path, b'bad')

    def test_symlink_parent_and_file_refused(self):
        self.store.ensure_user(ALICE)
        outside = self.root / 'outside';outside.mkdir(mode=0o700)
        (self.home() / 'link').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(OSError):self.store.put(ALICE, 'link/escape', b'bad')
        (self.home() / 'link').unlink()
        secret = outside / 'secret';secret.write_bytes(b'original');secret.chmod(0o600)
        (self.home() / 'link').symlink_to(secret)
        with self.assertRaises(OSError):self.store.read(ALICE, 'link')
        self.assertEqual(secret.read_bytes(), b'original')

    def test_hardlink_refused(self):
        self.store.ensure_user(ALICE)
        outside = self.root / 'secret';outside.write_bytes(b'original');outside.chmod(0o600)
        os.link(outside, self.home() / 'linked')
        with self.assertRaises(Denied):self.store.read(ALICE, 'linked')
        with self.assertRaises(Denied):self.store.put(ALICE, 'other', b'new')
        self.assertEqual(outside.read_bytes(), b'original')

    def test_fifo_refused_without_blocking(self):
        self.store.ensure_user(ALICE);os.mkfifo(self.home() / 'pipe', 0o600)
        with self.assertRaises(Denied):self.store.read(ALICE, 'pipe')

    def test_private_modes_required(self):
        self.state.chmod(0o755)
        with self.assertRaises(ValueError):self.reopen()
        self.state.chmod(0o700);self.store.database.chmod(0o644)
        with self.assertRaises(ValueError):self.reopen()

    def test_corrupt_database_is_not_recreated(self):
        self.store.database.write_bytes(b'corrupt evidence')
        with self.assertRaises(sqlite3.DatabaseError):self.reopen()
        self.assertEqual(self.store.database.read_bytes(), b'corrupt evidence')

    def test_missing_database_is_not_recreated_over_retained_homes(self):
        self.store.ensure_user(ALICE);self.store.put(ALICE,'retained',b'original')
        self.store.database.unlink()
        with self.assertRaises(ValueError):self.reopen()
        self.assertFalse(self.store.database.exists())
        self.assertEqual((self.home()/'retained').read_bytes(),b'original')

    def test_missing_database_is_not_recreated_even_before_first_registration(self):
        self.store.database.unlink()
        with self.assertRaises(ValueError):self.reopen()
        self.assertFalse(self.store.database.exists())

    def test_missing_data_root_is_not_recreated(self):
        (self.data / 'users').rmdir()
        with self.assertRaises(ValueError):self.reopen()
        self.assertFalse((self.data / 'users').exists())

    def test_missing_ready_home_is_not_recreated(self):
        self.store.ensure_user(ALICE);self.home().rmdir()
        with self.assertRaises(FileNotFoundError):self.store.ensure_user(ALICE)
        self.assertFalse(self.home().exists())

    def test_mapping_tamper_refused(self):
        self.store.ensure_user(ALICE)
        with self.store.db() as db:db.execute('UPDATE users SET home_id=? WHERE subject=?', (self.home(BOB).name, ALICE.sub))
        with self.assertRaises(ValueError):self.store.ensure_user(ALICE)
        with self.assertRaises(Denied):self.store.list(ALICE)

    def test_process_death_during_provision_recovers_same_folder(self):
        for phase in ['registered', 'directory-created', 'ready']:
            with self.subTest(phase=phase):
                self.crash(lambda hook: self.store.ensure_user(ALICE, phase=hook), phase)
                self.assertEqual(self.reopen().ensure_user(ALICE)['storageId'], self.home().name)
                with self.store.db() as db:
                    self.assertEqual(db.execute('SELECT count(*) FROM users').fetchone()[0], 1)
                    self.assertEqual(db.execute('SELECT count(*) FROM permissions').fetchone()[0], 7)
                with self.store.db() as db:db.execute('DELETE FROM permissions');db.execute('DELETE FROM users')
                self.home().rmdir()

    def test_pending_nonempty_folder_is_not_adopted(self):
        self.crash(lambda hook: self.store.ensure_user(ALICE, phase=hook), 'directory-created')
        (self.home() / 'unexpected').write_text('retain')
        with self.assertRaises(ValueError):self.store.ensure_user(ALICE)
        self.assertTrue((self.home() / 'unexpected').exists())

    def test_process_death_during_atomic_replace(self):
        self.store.ensure_user(ALICE)
        old = self.store.put(ALICE, 'file', b'original')
        self.crash(lambda hook: self.store.put(ALICE, 'file', b'new data', previous_sha256=old['sha256'], phase=hook), 'staged')
        restarted = self.reopen()
        self.assertEqual(restarted.read(ALICE, 'file')['bytes'], b'original')
        self.assertFalse(any(p.name.startswith('.save-') for p in self.home().iterdir()))
        self.crash(lambda hook: restarted.put(ALICE, 'file', b'new data', previous_sha256=old['sha256'], phase=hook), 'committed')
        self.assertEqual(self.reopen().read(ALICE, 'file')['bytes'], b'new data')

    def test_process_death_during_atomic_create(self):
        self.store.ensure_user(ALICE)
        self.crash(lambda hook: self.store.put(ALICE, 'file', b'new data', phase=hook), 'staged')
        self.assertEqual(self.reopen().list(ALICE), [])
        self.crash(lambda hook: self.store.put(ALICE, 'file', b'new data', phase=hook), 'committed')
        self.assertEqual(self.reopen().read(ALICE, 'file')['bytes'], b'new data')
        self.assertEqual((self.home() / 'file').stat().st_nlink, 1)

    def test_concurrent_versioned_saves_have_one_winner(self):
        self.store.ensure_user(ALICE);old = self.store.put(ALICE, 'file', b'original')
        def save(value):
            try:
                self.store.put(ALICE, 'file', value, previous_sha256=old['sha256']);return True
            except Denied:return False
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            results = list(pool.map(save, [b'first', b'second']))
        self.assertEqual(sorted(results), [False, True])
        self.assertIn(self.store.read(ALICE, 'file')['bytes'], [b'first', b'second'])

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Storage)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {'status': 'PASS' if result.wasSuccessful() else 'FAIL', 'tests': result.testsRun,
              'failures': len(result.failures), 'errors': len(result.errors),
              'scope': 'Actual local SQLite/files, fork process death, concurrent saves; trusted fixture principals only. No public API, live issuer, UI or network authorization exercised.',
              'sourceSHA256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in [ROOT/'gateway_service/user_store.py', ROOT/'gateway_service/policy.py', Path(__file__)]}}
    output = ROOT / '.build/checks/user-storage-result.json';output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and json.loads(output.read_text()).get('status') == 'FAIL':
        shutil.copyfile(output, output.with_name('user-storage-failed-' + str(time.time_ns()) + '.json'))
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
