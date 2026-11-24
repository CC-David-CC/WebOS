"""Exercise the scheduled reset and the Files store with disposable state."""

from contextlib import closing
import importlib.util
import os
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
from unittest.mock import patch
import uuid

from webos_accounts.policy_service import setup_policy
from webos_storage import Denied, Principal, UserStore
from webos_storage import account_cleanup

spec = importlib.util.spec_from_file_location("issuer_reset", Path(__file__).with_name("reset-test-accounts.py"))
issuer_reset = importlib.util.module_from_spec(spec)
spec.loader.exec_module(issuer_reset)


class ResetFilesTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name).resolve()
        for name in ("identity", "storage-state", "account-files"):
            (root / name).mkdir(mode=0o700)
        self.database = root / "identity" / "accounts.sqlite3"
        self.state = root / "storage-state"
        self.files = root / "account-files"
        with closing(sqlite3.connect(self.database)) as db:
            db.execute("CREATE TABLE accounts (username TEXT PRIMARY KEY, subject TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created INTEGER NOT NULL)")
            db.execute("CREATE TABLE registered_sessions (token_digest TEXT PRIMARY KEY, record TEXT NOT NULL, deadline INTEGER NOT NULL)")
            setup_policy(db)
            db.commit()
        self.database.chmod(0o600)
        self.store = UserStore(self.state, self.files, maximum_users=3)
        self.owner = self.account("dflanag3")
        self.test = self.account("test")

    def account(self, name, *, subject=None, home=True):
        subject = subject or f"user:{uuid.uuid4()}"
        with closing(sqlite3.connect(self.database)) as db:
            db.execute("INSERT INTO accounts VALUES (?, ?, 'test-hash', 0)", (name, subject))
            db.commit()
        principal = Principal(subject, str(uuid.uuid4()), "registered", {}, int(time.time()) + 60)
        if home:
            self.store.ensure_user(principal)
            self.store.put(principal, "document.txt", name.encode())
        return principal

    def home(self, principal):
        return self.store.users_path / uuid.UUID(principal.sub[5:]).hex

    def run_reset(self, operation="reset"):
        return issuer_reset.run(self.database, operation, cleanup_files=True)

    def identity_rows(self, query):
        with closing(sqlite3.connect(self.database)) as db:
            return db.execute(query).fetchall()

    def test_managed_reset_retries_mail_and_releases_name_only_after_completion(self):
        from webos_accounts.management import migrate
        keep = self.account("retainedqa", home=False)
        old = self.account("reuseqa")
        migrate(self.database, self.owner.sub, (keep.sub, self.test.sub))
        with closing(sqlite3.connect(self.database)) as db:
            db.execute("INSERT INTO am_mail_binding VALUES(?,?)", (old.sub, "qa-mail-id"))
            db.commit()
        preview = self.run_reset("preview")
        self.assertEqual((preview["retained"], preview["mailboxes_to_delete"]), (3, 1))
        def unavailable(subject, username, mail_id):
            self.assertEqual((subject, username, mail_id), (old.sub, "reuseqa", "qa-mail-id"))
            raise OSError("simulated unavailable mail service")
        with self.assertRaises(OSError):
            issuer_reset.run(self.database, "reset", cleanup_files=True, retire_mailbox=unavailable)
        self.assertEqual(self.identity_rows("SELECT disabled FROM accounts JOIN account_policy USING(subject) WHERE username='reuseqa'"), [(1,)])
        with self.assertRaises(sqlite3.IntegrityError):
            self.account("reuseqa", home=False)
        receipts = []
        result = issuer_reset.run(self.database, "reset", cleanup_files=True,
                                  retire_mailbox=lambda *args: receipts.append(args))
        self.assertEqual(receipts, [(old.sub, "reuseqa", "qa-mail-id")])
        self.assertEqual((result["accounts_deleted"], result["mailboxes_deleted"], result["files_homes_removed"]), (1, 1, 1))
        self.assertFalse(self.home(old).exists())
        new = self.account("reuseqa", home=False)
        self.assertNotEqual(new.sub, old.sub)
        self.assertEqual(self.identity_rows("SELECT name FROM am_reserved WHERE name='reuseqa'"), [])
        self.assertEqual(self.identity_rows("SELECT account_id FROM am_mail_binding"), [])
        self.assertEqual(self.identity_rows("SELECT count(*) FROM am_retiring"), [(0,)])
        self.assertEqual(self.identity_rows("SELECT setting FROM am_requested_mail JOIN accounts USING(subject) WHERE username='reuseqa' ORDER BY setting"),
                         [("mailbox",), ("receive_external",)])
        self.assertEqual(self.identity_rows("SELECT subject FROM accounts WHERE username='retainedqa'"), [(keep.sub,)])

    def test_exact_deletion_preserves_retained_files_and_allows_new_accounts(self):
        removed = self.account("temporary")
        orphan = self.store.users_path / uuid.uuid4().hex
        orphan.mkdir(mode=0o700)
        (orphan / "unrelated.txt").write_bytes(b"outside this reset")
        (orphan / "unrelated.txt").chmod(0o600)
        self.store.set_permission(self.owner.sub, "delete", False)
        preview = self.run_reset("preview")
        self.assertEqual((preview["accounts_to_delete"], preview["files_homes_to_delete"]), (1, 1))
        self.assertFalse(self.identity_rows("SELECT 1 FROM sqlite_schema WHERE name='files_cleanup_pending'"))
        self.assertTrue(self.home(removed).is_dir())
        result = self.run_reset()
        self.assertEqual((result["accounts_deleted"], result["files_homes_removed"]), (1, 1))
        self.assertFalse(self.home(removed).exists())
        self.assertEqual((orphan / "unrelated.txt").read_bytes(), b"outside this reset")
        for principal, contents in ((self.owner, b"dflanag3"), (self.test, b"test")):
            self.assertEqual(self.store.read(principal, "document.txt")["bytes"], contents)
        with self.store.db() as db:
            self.assertEqual(db.execute("SELECT allowed FROM permissions WHERE subject=? AND operation='delete'", (self.owner.sub,)).fetchone(), (0,))
        # The orphan counts against the filesystem quota. Move it outside the
        # users directory before proving that the retired registry row frees a slot.
        orphan.rename(self.files / "orphan")
        replacement = self.account("temporary")
        self.assertNotEqual(replacement.sub, removed.sub)
        self.assertEqual(self.store.read(replacement, "document.txt")["bytes"], b"temporary")

    def test_missing_home_still_blocks_stale_provisioning(self):
        never_opened = self.account("no-files", home=False)
        result = self.run_reset()
        self.assertEqual((result["files_homes_removed"], result["files_cleanups_completed"]), (0, 1))
        with self.assertRaises(Denied):
            self.store.ensure_user(never_opened)
        self.assertFalse(self.home(never_opened).exists())

    def test_retry_after_login_commit(self):
        deleted = self.account("interrupted")
        with patch.object(account_cleanup.AccountHomeCleanup, "retire_and_remove", side_effect=OSError):
            with self.assertRaises(OSError):
                self.run_reset()
        self.assertNotIn(("interrupted",), self.identity_rows("SELECT username FROM accounts"))
        self.assertEqual(self.run_reset("preview")["files_cleanups_pending"], 1)
        self.assertEqual(self.run_reset()["files_homes_removed"], 1)
        self.assertFalse(self.home(deleted).exists())
        self.assertEqual(self.run_reset()["files_cleanups_completed"], 0)

    def test_retry_after_access_was_revoked(self):
        deleted = self.account("interrupted-removal")
        with patch.object(account_cleanup.shutil, "rmtree", side_effect=OSError):
            with self.assertRaises(OSError):
                self.run_reset()
        self.assertTrue(self.home(deleted).exists())
        with self.assertRaises(Denied):
            self.store.read(deleted, "document.txt")
        with self.assertRaises(Denied):
            self.store.ensure_user(deleted)
        with self.assertRaises(ValueError):
            self.store.set_enabled(deleted.sub, True)
        self.assertEqual(self.run_reset()["files_homes_removed"], 1)
        self.assertFalse(self.home(deleted).exists())

    def test_retry_after_home_removal_before_journal_acknowledgement(self):
        deleted = self.account("interrupted-acknowledgement")
        with patch.object(account_cleanup.os, "fsync", side_effect=OSError):
            with self.assertRaises(OSError):
                self.run_reset()
        self.assertFalse(self.home(deleted).exists())
        self.assertEqual(self.run_reset("preview")["files_cleanups_pending"], 1)
        self.assertEqual(self.run_reset()["files_cleanups_completed"], 1)
        with self.assertRaises(Denied):
            self.store.ensure_user(deleted)

    def test_invalid_mapping_and_link_stop_before_login_deletion(self):
        deleted = self.account("unsafe")
        target = self.home(deleted)
        link = target / "external"
        link.symlink_to(self.home(self.owner))
        with self.assertRaisesRegex(ValueError, "Unexpected entry"):
            self.run_reset()
        self.assertIn(("unsafe",), self.identity_rows("SELECT username FROM accounts"))
        link.unlink()
        with self.store.db() as db:
            db.execute("UPDATE users SET home_id=? WHERE subject=?", (uuid.uuid4().hex, deleted.sub))
        with self.assertRaisesRegex(ValueError, "ownership"):
            self.run_reset()
        self.assertTrue(target.is_dir())
        self.assertEqual(self.store.read(self.owner, "document.txt")["bytes"], b"dflanag3")

    def test_pending_job_refuses_a_restored_login_subject(self):
        deleted = self.account("restored")
        with patch.object(account_cleanup.AccountHomeCleanup, "retire_and_remove", side_effect=OSError):
            with self.assertRaises(OSError):
                self.run_reset()
        self.account("restored", subject=deleted.sub, home=False)
        with self.assertRaisesRegex(ValueError, "still registered"):
            self.run_reset()
        self.assertTrue(self.home(deleted).exists())

    def test_detects_cross_mount_even_on_the_same_device(self):
        deleted = self.account("mounted")
        inode = (self.home(deleted) / "document.txt").stat().st_ino
        original = account_cleanup._mount_id

        def mount_id(descriptor):
            identity = original(descriptor)
            return identity + (os.fstat(descriptor).st_ino == inode)

        with patch.object(account_cleanup, "_mount_id", side_effect=mount_id):
            with self.assertRaisesRegex(ValueError, "Mount inside"):
                self.run_reset()
        self.assertIn(("mounted",), self.identity_rows("SELECT username FROM accounts"))

    def test_legacy_permissions_database_accepts_retired_homes_migration(self):
        with self.store.db() as db:
            db.execute("DROP TABLE retired_homes")
        self.store = UserStore(self.state, self.files)
        self.assertEqual(self.store.read(self.owner, "document.txt")["bytes"], b"dflanag3")
        deleted = self.account("old-permissions-schema")
        self.assertEqual(self.run_reset()["files_homes_removed"], 1)
        with self.assertRaises(Denied):
            self.store.ensure_user(deleted)


if __name__ == "__main__":
    unittest.main()
