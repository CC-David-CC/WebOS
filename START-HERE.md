# WebOS rebuild — entire suite, in progress

The goal is a working, independently reproducible assembly of the entire existing WebOS suite and all 17 selected maintained upstream forks. Runtime, Desktop, Login, Accounts, Storage, Files, and WordCraft are the first milestone. They do not define the final scope.

Read `migration/scope.json` for the registered catalog, source ownership candidates, asset gaps, and remaining requirements. The old builder registers 75 IDs including 28 games; those counts describe that registry, not all discovered source or qualified applications. Nonregistered source and historical WIP remain in scope.

## Verified source assembly

The assembly currently pins 27 source components. ACAD, original JSketcher, and four engines retain their independent histories. All 17 selected upstream fork histories are attached as source baselines; they are not qualified releases. Help, Calculator, and Files were mechanically extracted from verified recovery copies, preserving earlier source paths and commit maps. Their current app trees retain the exact original Git tree identities. Six existing unit scripts passed in the recovered monorepo, extracted repositories, and a fresh recursive clone. Help has no extracted unit script. A fresh recursive local clone passed for the first 26 source components and was advanced to include Runtime. Organized-layout clone verification is recorded separately. WordCraft passed its unmodified WASM compile check; its isolated fresh-clone check also passed with the original workspace hidden and networking disabled. These results do not prove browser integration, full asset builds, persistence, or human/agent parity.

The `.gitmodules` entries and Git links select component commits. They are the source version authority. Component source is never copied into parent-owned files. Whole-system tests and composition belong to this parent. Mechanical extraction and functional changes are separate commits.

## Remaining scope

Preserve and account for every existing app, game, tool, library, required asset, and WIP state. Keep ACAD, original JSketcher, old editors, and the selected replacement forks distinct. All 17 selected maintained forks now have source submodules with original histories, licenses, and structures retained on local `webos/integration` branches. Their browser builds and host operations still require individual qualification. Source presence does not establish support.

Build real server-backed account files with existing identity and file ownership compatibility. Human, authorized agent, and test operations share the same domain implementations. One authoritative live document per session and server-authoritative saved revisions are mandatory. No browser cache may masquerade as a confirmed server save. Linux/v86, Terminal, MailCraft, and Craft Anything are not minimum dependencies; preserve existing excluded source separately.

This assembly has no bootable minimum yet. No whole-system or existing-user continuity result is claimed.

## Local Git and recovery

Local sibling bare origins are under `../.webos-local-git/`. They are not an off-device backup. For a trusted fresh local clone, use:

```sh
git -c protocol.file.allow=always clone --recurse-submodules ../.webos-local-git/workspace.git /a/new/disposable/path
```

Private recovery/evidence is under `/path/to/workspace/Projects/.webos-migration/`. Start with `run-20261114-02/phase-checkpoint.json` and its evidence reports, then the earlier `run-20261114-01/checkpoint.json`. Raw capture includes tracked source/Git metadata, not all ignored assets or live account data. Do not publish private logs, credentials, account databases, or user documents.

The original workspace and deployment stay unchanged. No external publication, production change, service restart, or account-data migration is authorized. Continue local work while separately gated actions remain pending.

SolidCraft includes a separate brand/interface license. Preserve its notices and resolve the distribution gate before publishing or deploying it. No legal conclusion or distribution permission is implied by the local source checkout.

## Disk layout and source checks

The seven core component paths stay at the root: `runtime/`, `desktop/`, `login/`, `accounts/`, `storage/`, `files/`, `wordcraft/`. Additional apps are individual submodules under `apps/`; engines under `engines/`; original JSketcher under `legacy/jsketcher/`. These grouping directories are not grouped source repositories. `tests/`, `scripts/`, and `deploy/` belong to the parent. Deployment definitions are still pending a real development composition.

Run `python3 scripts/inspect_assembly.py` to inspect actual source wiring without network calls. Add `--require-core` to require all seven core sources. Run `python3 -m unittest discover -s tests -v` for source composition acceptance. The required-core test currently fails on missing Desktop, Login, Accounts, and Storage; no test has been skipped to conceal that incomplete state. Browser/backend acceptance remains separate.

The original app inventory default is 1GiB per app bundle. It is not the suite disk budget. The new release must configure installation policy from actual artifact graphs and keep code, assets, downloads, browser cache, memory, and account-file budgets distinct. The stale 512MiB Runtime regression was corrected against the historical approved policy, with exact/over-1GiB coverage, in a commit after mechanical extraction.
