# Files installer input bootstrap and legacy-entrypoint review

**Source candidate for independent review. No live installation, root source copy, service change or floor write was performed.** This packet is separate from the guarded-installer candidate `8953bbcc5`. The installed `84c09e08…` CLI candidate cannot yet be described as protecting every legacy entrypoint.

## Exact bootstrap preparation

`ops/files_bootstrap_candidate.py` SHA-256 `00e608cfa4d405a280368cb4af248e7c9ab414930db4b328bb94ad5758c6c785` imports only Python standard-library modules. It never imports, compiles or executes code from the source tree. It reads an explicit source closure from `ops/files_bootstrap_pins.txt`, whose pinned SHA-256 is `3fbabe6cd71b8d11e4347c0b8bb4a4d3df89263126a327e1ca368ca87d953667`; the list includes the exact operator modules, `3ad` candidate manifest, route table, installer launcher/helper and its installer manifest. It hashes every regular source file before copying, refuses symlinks, hard links, extended ACLs, unsafe owner/mode/ancestors, duplicate or unsafe paths, stages root-owned data files under a root-owned parent, fsyncs them and their directories, checks the entire staged closure, and publishes with `renameat2(RENAME_NOREPLACE)`. Re-running verifies an existing complete generation without replacing it; an incomplete or modified generation is refused. Killed/failed stages are left as unselected temporary directories for separately reviewed cleanup.

Fixed candidate paths are `/srv/codi-connected/operators/files-bootstrap-v1.py` for the reviewed bootstrap, `/srv/codi-connected/operators/files-bootstrap-source` for a root-owned data-only prepared source, and `/srv/codi-connected/operators/files-install-input-ce18b7794adc2472` for the published input. All ancestors must be root-owned, non-group/other-writable, free of extended ACLs and symlinks; the bootstrap refuses a different hostname, UID or entrypoint. It does not provision probe credentials, modify hosting, call the installer or activate a service.

For a future reviewable preparation, obtain the exact source checkpoint as **data**, establish a new root-owned, non-overwriting scratch tree under the trusted operators parent, and copy only `files_bootstrap_pins.txt` and its listed regular source files into it. Do not run checkout scripts, import them as Python, copy account data, or follow source symlinks. The preparer must reject unsafe source path components and metadata while copying, verify the pin list and file contents before use, preserve the intended root ownership and perform no replacement of an existing source tree. Independently verify the bootstrap's exact hash after making a root-owned copy in a non-overwriting fixed path; the bootstrap itself cannot verify code before Python starts executing it. The bootstrap's own custody checks are defense in depth, not a substitute for this external verification. The exact post-preparation invocation, **not to run until that preparation and all gates are independently reviewed**, is:

```sh
sudo -n /srv/codi-connected/venvs/517179c/bin/python -I -B /srv/codi-connected/operators/files-bootstrap-v1.py
```

Then independently verify the complete published generation and its root custody; only afterward could the separate reviewed installer candidate be considered. This is not an instruction to install a guard or write a floor. The manual creation of the protected bootstrap executable and data-only source staging remains a separate bootstrap-of-trust step; the source helper intentionally does not grant authority to run an unverified checkout or make an unchecked root copy. All files here are public code/manifest data; do not stage keys, credentials or private runtime state.

Fixture command:

```sh
sudo -n python3 -B research/beta-isolated-hosting/tests/files-bootstrap-test.py
```

Passed in a root-owned disposable `/run` tree with only fixed path/hostname substitutions: full exact closure and idempotence; mismatched file, symlink, owner and extended ACL refusals; real SIGKILL during staging and immediately after directory publication; refusal to replace a corrupted existing generation. This is not an actual production path or power-loss proof. The test-only fault injection changes the mapped fixture script, not production source.

## Actual invocation inventory and quiescence gate

Read-only box-webhost search on 2026-11-04 found:

- `ops/webctl.py` is the normal administrative CLI documented in the host README, RUNBOOK and AGENTS.md. Installed legacy hash is `e012fb1d…`; its `main()` calls `load()` before taking the existing nonblocking `.controller.lock` flock.
- `ops/activate-codi.py` imports `webctl` as `w`, takes that lock, then calls `w.caddy_apply` and other methods directly. This bypasses guard checks placed only in `webctl.main()`. It asserts the historical Codi domain is absent, but that assertion is not a durable floor guard.
- `ops/finalize-codi.py` imports `webctl` and directly calls `w.deploy(w.site(w.load(), 'codi.codes'))`; its source does not take the controller flock. Host `AGENTS.md` identifies both Codi scripts as historical one-off records, not repeatable supported deployment commands. Their existence still means they must be explicitly retired or covered by a reviewed shared boundary rather than counted as guarded.
- `ops/acceptance.py` imports helpers and launches `webctl.py`; host AGENTS.md explicitly says not to run its disruptive acceptance test in production. `probe-firewall.py` and `install-firewall.py` import helper functions; their complete effects need review before classifying them as harmless after a floor. `push-site-repos.py` emits documentation invoking the normal CLI.
- A search of `/etc/systemd`, `/lib/systemd/system`, `/usr/lib/systemd/system`, `/etc/cron*` and `/usr/local/bin` found no direct webctl/importer invocation. This is a bounded text search, not proof that arbitrary service code cannot import it. The active `codi-ksu-live-root-renew.timer` invokes a separate pinned root-renewal operator with the same hosting lock, not a direct textual webctl invocation; it must be coordinated without interfering with main service state. The renewal service was observed failed at this read-only snapshot; this document does not diagnose or modify it.

Run the actual legacy-controller negative control:

```sh
python3 -B research/beta-isolated-hosting/tests/legacy-preloaded-controller-test.py
```

It passed: a forked process executes the pinned old `webctl.main()` through its actual pre-lock `load()` (fixture callback pauses there); a second actor takes the real fixture flock, atomically replaces the controller with the guarded source and records a floor; the old process then resumes, acquires the lock, and dispatches the old `render` callback. No real Caddy or production paths are touched. Thus rename and a held flock alone do not fence already-loaded Python code.

Before any v2 floor, the necessary operational invariant is: every invocation capable of affecting hosting has been prevented from starting an old unguarded path, every already-loaded old process and pending importer has finished or been safely retired, and any remaining supported mutation goes through an independently verified floor-preserving boundary that acquires the same lock before operative state is read. This includes CLI invocations, direct module callers, recovery and administrator-run scripts. A cooperative maintenance window coordinated with the trusted administrators, explicit retirement/guarding of historical direct importers, identification and draining of relevant existing processes under the managed lock, and verification of the installed guard and exact state are a possible procedure, but process-name scanning alone cannot prove the absence of code already loaded under another name. Automatic timers and unknown transactions must be accounted for rather than casually stopped. The exact supported-entrypoint fence and any host changes require review; intentional privileged administrator bypass remains outside the guarantee. Do not write the v2 floor until this invariant is established and independently checked.
