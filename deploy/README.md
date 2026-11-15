# Fresh ksu.codes test composition

The user identifies ksu.codes as a test site with test users only. The fresh
rebuild uses one loopback process assembling Accounts, signed file authority,
Storage and built static assets. Calculator → Files → Text → WordCraft has
passed local browser acceptance; hosted acceptance remains separate.

`backend-requirements.lock` pins the third-party backend dependencies. Component
source comes from the parent Git links, never from the old laptop workspace.
Prepare a new external environment with `scripts/bootstrap_backend.py`.

For a trusted HTTPS proxy that preserves the original Host and Origin headers:

```sh
/path/to/backend-env/bin/python scripts/run_development.py \
  --public-root /a/new/release/public \
  --private-root /a/new/private/test-state \
  --port 18140 --origin https://ksu.codes
```

The socket still binds127.0.0.1. Without `--origin`, the selected loopback URL is
the identity origin, preserving local development behavior. Credentials, URL
paths, queries, invalid ports and non-loopback plain HTTP origins are refused.
The server does not trust forwarded headers to invent its identity origin.

New private state uses `webos-development-state/2` and binds its origin. Existing
state from another origin or older unbound development markers is refused and
preserved; no migration, repair or reset runs automatically. Keys, databases and
account documents stay outside the release/source/public directories.

The current server is a test/development composition, not an official identity
service. Before activating the test deployment, verify the exact Caddy site
block, selected artifact receipt, loopback port, filesystem ownership, separate
state and rollback. Preserve beta.ksu.codes routing and existing service state.
Do not publish Git repositories or infer authorization to alter unrelated sites.

`tests/test_development_origin.py` checks canonical origins and uses a real
loopback HTTP server to verify HTTPS identity plus Host/Origin rejection and
state-origin binding. Existing browser tests remain the account/document
acceptance authority. Deployment files and local tests alone are not proof that
the hosted system works.

## Staged service definition

`webos-test.service.in` is an uninstalled template for the new test service.
Render `@SERVICE_USER@` and `@TEST_ROOT@` only from verified deployment identity
and an owned, migration-marked staging directory. Create a new0700 `private/`
parent there; leave `private/account-state` absent for explicit initialization.
Refuse existing service-name/path collisions. The template has no automatic
restart policy and does not alter any old service. Starting it is a separate
step from staging files; switching Caddy is separate again.

The first package was verified locally and staged under the dedicated server
user's `webos-rebuild-test` directory. Offline installation and imports passed
on target Python3.12. The package contains55 files (105,646,592bytes), no account
state and no source Git histories. Its receipt records the exact parent/child
commits and complete WordCraft artifact hashes. Remote staging evidence stays
in the private migration checkpoint. Staging is not hosted acceptance.

The test route is now active. See `TEST-STATUS.md` for the hosted four-stage
results, service identity and rollback. A supplemental third-concurrent-editor
startup timeout remains open; it is not hidden by the passing core workflows.
