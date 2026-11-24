"""Single WebOS coordinator. Pending jobs survive restart; uncertain jobs keep their account slot."""
from contextlib import closing, contextmanager
import json
from pathlib import Path
import secrets
import sqlite3
import threading
import time
from webos_storage.transfers import AllowanceExceeded
from webos_storage.policy import Denied


class Jobs:
    def __init__(self, directory, render):
        self.path=Path(directory)/'compute-jobs.sqlite3'
        self.render=render
        self.wake=threading.Event()
        self.stop=threading.Event()
        with self.db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS jobs(
                id TEXT PRIMARY KEY, owner TEXT NOT NULL, state TEXT NOT NULL,
                input TEXT, output TEXT, finished REAL)""")
            db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS active_owner ON jobs(owner)
                       WHERE state IN ('queued','running','uncertain')""")
            db.execute("UPDATE jobs SET state='uncertain' WHERE state='running'")
        self.thread=threading.Thread(target=self.run,daemon=True,name='webos-image-worker')
        self.thread.start()

    @contextmanager
    def db(self):
        with closing(sqlite3.connect(self.path,timeout=8)) as conn:
            with conn: yield conn

    def submit(self, owner, payload):
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('DELETE FROM jobs WHERE finished < ?', (time.time()-600,))
            if db.execute("SELECT 1 FROM jobs WHERE owner=? AND state IN ('queued','running','uncertain')",(owner,)).fetchone():
                raise AllowanceExceeded('Finish your current compute request before submitting another')
            if db.execute("SELECT count(*) FROM jobs WHERE state='queued'").fetchone()[0]>=16:
                raise AllowanceExceeded('Compute queue full')
            job=secrets.token_urlsafe(18)
            db.execute("INSERT INTO jobs VALUES(?,?,'queued',?,NULL,NULL)",(job,owner,json.dumps(payload)))
        self.wake.set()
        return {'job':job,'state':'queued'}

    def status(self, owner, job):
        with self.db() as db:
            row=db.execute('SELECT state,output FROM jobs WHERE owner=? AND id=?',(owner,job)).fetchone()
        if not row: raise Denied('Job unavailable')
        return {'job':job,'state':row[0],**(json.loads(row[1]) if row[1] else {})}

    def counts(self):
        with self.db() as db:
            counts=dict(db.execute('SELECT state,count(*) FROM jobs GROUP BY state'))
        return {'waiting':counts.get('queued',0),'running':counts.get('running',0),'uncertain':counts.get('uncertain',0)}

    def run(self):
        while not self.stop.is_set():
            self.wake.clear()
            with self.db() as db:
                db.execute('BEGIN IMMEDIATE')
                db.execute('DELETE FROM jobs WHERE finished < ?', (time.time()-600,))
                # This first worker is exclusive to the image GPU. An unconfirmed
                # remote exit keeps that worker unavailable until operator reconciliation.
                row=db.execute("""SELECT id,input FROM jobs WHERE state='queued'
                     AND NOT EXISTS (SELECT 1 FROM jobs WHERE state='uncertain')
                     ORDER BY rowid LIMIT 1""").fetchone()
                if row: db.execute("UPDATE jobs SET state='running' WHERE id=?",(row[0],))
            if not row:
                self.wake.wait(20); continue
            job, payload=row
            try:
                result=self.render(json.loads(payload)); state='done'
            except ConnectionError:
                result=None; state='uncertain'
            except Exception:
                result=None; state='failed'
            with self.db() as db:
                db.execute('UPDATE jobs SET state=?,input=NULL,output=?,finished=? WHERE id=?',
                           (state,json.dumps(result) if result else None,None if state=='uncertain' else time.time(),job))
                db.execute("""DELETE FROM jobs WHERE id IN (SELECT id FROM jobs WHERE finished IS NOT NULL
                            ORDER BY finished DESC LIMIT -1 OFFSET 32)""")

    def close(self):
        self.stop.set()
        self.wake.set()
