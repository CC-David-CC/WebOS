# ACAD clean repository cutover

User decision: ACAD (Agent Computer-Aided Design) is a separate project. The
public JSketcher `webos-integration` fork is the endpoint of the earlier
JSketcher work. ACAD must start without inherited Git history. Test ACAD before
rolling box-git's JSketcher back to its public integration revision.

## Current state

- Independent working source: `/tmp/codi-acad-main-20261107`, branch `main`.
- Primary: `box-git:/srv/data/git/ACAD.git`.
- Backup: `r730:/mnt/data10tb/git/ACAD.git`.
- Parentless initial commit: `c700cac92b6a88aa10df416d7d7ae93e28bd015d`.
- Both bare repositories initially read back exactly one commit and16MiB.
- Initial snapshot comparison:6062 prior tracked files /6064 ACAD files; every
  retained blob/mode/path matches except declared new README and repository/
  provenance notes. No dependency directory or generated runtime is tracked.
- Original source tree/commit are recorded in ACAD `SOURCE-SNAPSHOT.json`;
  historical evidence keeps its actual producing refs in the separate original
  repository. No old commits were fetched/merged into ACAD.

## Fresh build issue

A fresh ACAD checkout with shared pinned caches exposed a real build-path bug:
Webpack resolves resource symlinks before testing the raw NVIDIA glue loader,
while the loader predicate used the unresolved requested cache path. The browser
transform was skipped, leaving a build-machine file URL. The existing exact
worker-output pin refused the result. ACAD62019cc canonicalizes the requested
input path before alias/loader matching; native input and output pins remain.
The first failure log is retained on R730 under the fresh ACAD build `.build/`.

## Pending cutover checks

- [ ] Fresh ACAD normal application build with exact qualified Native inputs.
- [ ] Actual full shell model/edit/history/native Save/Open workflow.
- [ ] Actual full shell material/core3MF/save/reopen/export workflow and independent
      artifact oracle, including edited/reopened identity and geometry.
- [ ] Actual atomic source-dimension/region-reselection workflow.
- [ ] Back up source, notes and actual results to both LAN repositories.
- [ ] Only after ACAD checks pass: roll box-git's JSketcher source back to the
      public `webos-integration` revision, remove ACAD-ahead branch exposure there,
      and verify readback. No GitHub write is authorized by this rollback.

Read-only public head observed2026-11-07:
`518a4666cfc5c94acb153f0cd315a2ca1625eb2f` at
`https://github.com/CC-David-CC/jsketcher`, branch `webos-integration`.
Re-read the public head before rollback; this observation does not perform it.
Full CAD Gate1 remains open and is separate from repository-cutover acceptance.
