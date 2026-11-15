# Development composition inputs

`backend-requirements.lock` pins the 15 third-party packages needed by the current Accounts/Storage implementation. It derives from the captured backend lock and excludes unrelated chess, WebSocket, and geolocation dependencies. Component source versions come from the parent Git links.

Prepare a new environment outside the checkout:

```sh
python3 scripts/bootstrap_backend.py --venv /absolute/new/private/environment
```

This command installs the trusted local Runtime, Accounts and Storage packages plus locked dependencies. It refuses an existing environment and starts no services. It must never be pointed at the original workspace. Account keys/databases/files belong in separately configured private directories outside source and public asset roots.

`scripts/run_development.py` supplies an executable loopback HTTP composition of Accounts, file authority, Storage, and explicit built public assets. It requires a separate private state directory. The signed-file browser test builds its own component harness and verifies persistence across restart. Production deployment definitions are still pending. This directory does not constitute a deployment or a working assembled desktop. Existing-user compatibility, delegated agents, full editor save confirmation, release provenance and full-suite browser acceptance remain separate gates. No production changes or external publication are authorized.
