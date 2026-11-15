# WebOS local assembly — migration in progress

This is a new Git superproject. Component source is represented by submodules. The existing workspace and deployment remain unchanged.

## Current state

Only ACAD is attached, unchanged at `4085c5e22b035de638df2feaf533ac0540cf4c7e`, retaining its independent history. No functional rebuild changes are included. ACAD is distinct from historical JSketcher, CADCraft, and SolidCraft. Its unfinished CAD gates remain open.

Runtime, Desktop, Login, Accounts, Storage, Files, and WordCraft are pending ownership separation and integration. Server-backed account files and existing-user compatibility are mandatory and unverified. This assembly has no bootable minimum yet. Linux/v86 is excluded from that minimum.

Local sibling bare origins are under `../.webos-local-git/`. They are not an off-device backup. External publication and production changes have not been authorized or attempted.

For a trusted local recursive clone only, use a command-scoped file-transport exception:

```sh
git -c protocol.file.allow=always clone --recurse-submodules ../.webos-local-git/workspace.git /a/new/disposable/path
```

The parent pins component commits; do not use moving upstream branches as release inputs. Do not build against the old source directory. Read each component's instructions before building. Baseline and whole-system tests are separate; neither has yet been run for this assembly.

Private evidence and recovery are in `/home/dflanag3/Projects/.webos-migration/run-20261114-01/`. Read its RESUME.md and checkpoint.json to continue. Do not commit raw evidence, private account data, credentials, or recovery material.
