# WebOS rebuild — entire suite, in progress

The goal is a working, independently reproducible assembly of the entire existing WebOS suite and all 17 selected maintained upstream forks. Runtime, Desktop, Login, Accounts, Storage, Files, and WordCraft are the first milestone. They do not define the final scope.

Read `migration/scope.json` for the registered catalog, source ownership candidates, asset gaps, and remaining requirements. The old builder registers 75 IDs including 28 games; those counts describe that registry, not all discovered source or qualified applications. Nonregistered source and historical WIP remain in scope.

## Verified source assembly

ACAD retains its original independent history. Help, Calculator, and Files were mechanically extracted from verified recovery copies, preserving earlier source paths and commit maps. Their current app trees retain the exact original Git tree identities. Six existing unit scripts passed in the recovered monorepo, extracted repositories, and a fresh recursive clone. Help has no extracted unit script. These results do not prove browser integration, full asset builds, persistence, or human/agent parity.

The `.gitmodules` entries and Git links select component commits. They are the source version authority. Component source is never copied into parent-owned files. Whole-system tests and composition belong to this parent. Mechanical extraction and functional changes are separate commits.

## Remaining scope

Preserve and account for every existing app, game, tool, library, required asset, and WIP state. Keep ACAD, original JSketcher, old editors, and the selected replacement forks distinct. Establish all 17 selected maintained forks with original histories, licenses, and structures, then qualify their browser builds and host operations individually. Source presence does not establish support.

Build real server-backed account files with existing identity and file ownership compatibility. Human, authorized agent, and test operations share the same domain implementations. One authoritative live document per session and server-authoritative saved revisions are mandatory. No browser cache may masquerade as a confirmed server save. Linux/v86, Terminal, MailCraft, and Craft Anything are not minimum dependencies; preserve existing excluded source separately.

This assembly has no bootable minimum yet. No whole-system or existing-user continuity result is claimed.

## Local Git and recovery

Local sibling bare origins are under `../.webos-local-git/`. They are not an off-device backup. For a trusted fresh local clone, use:

```sh
git -c protocol.file.allow=always clone --recurse-submodules ../.webos-local-git/workspace.git /a/new/disposable/path
```

Private recovery/evidence is under `/home/dflanag3/Projects/.webos-migration/`. Start with `run-20261114-02/phase-checkpoint.json` and its evidence reports, then the earlier `run-20261114-01/checkpoint.json`. Raw capture includes tracked source/Git metadata, not all ignored assets or live account data. Do not publish private logs, credentials, account databases, or user documents.

The original workspace and deployment stay unchanged. No external publication, production change, service restart, or account-data migration is authorized. Continue local work while separately gated actions remain pending.
