# Legacy backend deployment composition

Thirty source/documentation paths retain the original root/host maintenance, deployment/release/cutover, ingress and old entrypoint code. These are parent-owned deployment composition, not copied application implementations. Domain authority/configuration sources are separately owned by Browser, Linux, Storage, publication, rendezvous, Microduck and unused Rooms.

Legacy source only, not a current supported import path or command. Original cross-package namespaces, private imports, target paths, key/account custody, host/network/process actions and fixtures must be ported deliberately before use. Do not add sys.path shims, privileged globals, fake storage or automatic service/firewall actions to make it run. No old module/driver is imported or executed by this extraction; no active backend or minimum dependency changes.

No existing deployment definitions or build entrypoints consume this directory. Do not import it or run broad legacy discovery. Some modules can perform host/network operations at top level. Current Accounts/Storage assembly remains unchanged. See migration/BACKEND-OWNERSHIP.md and private phase41 maps.

An additional26 historical isolated-host deployment helpers, including a separately retained copied journal ancestor, are organized under `isolated-hosting/`. They are inactive source references, not a runnable release. Read that directory's README and migration/ISOLATED-HOST-OPERATOR-SOURCE.md before any deliberate port. No operator ran or gained host authority.

Four historical candidate builder/fetch/verifier scripts and2 historical notes are preserved under `opfs-release/`; current README restrictions apply. They are inactive references, not supported WebOS builders or deployment authority. See migration/OPFS-RELEASE-SOURCE.md.
