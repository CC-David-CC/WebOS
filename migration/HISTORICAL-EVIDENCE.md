# Preserved historical output — separate from current acceptance

A bounded review of1,413 pending output/report candidates identified315 historical records in the captured Desktop-Preview source snapshot `4f72ea86928666189b32f6f05c2c697a37341d06`. Their exact Git blobs were read and hashed from the self-contained private recovery store. Current scoped tracked WIP was checked before assigning a historical-output disposition. Nothing was deleted or copied into active component/release source.

| Historical record role | Count |
|---|---:|
| Recognizable terminal/test/compiler output | 189 |
| Outcome report with explicit report/evidence context and metadata | 105 |
| Empty captured output channel | 21 |
| Total | 315 |

Reported PASS/FAIL is unverified historical text, not a result for the new assembly. File-role/preservation verification does not establish command execution, fidelity, accepted signatures, compatibility or present runtime behavior. If a record becomes a required fixture/provenance/build input, review that use explicitly and restore it with its identity; this disposition does not waive that gate. Possible inputs, schemas, ambiguous records, large content and newly dirty outputs remain pending. No source code was reclassified as disposable merely because its directory looked old.

The private per-file index records original path, Git object ID, file mode, detector and recovery commit. Three representative records (one per role) were restored byte-for-byte with their Git modes while the original workspace and primary assembly were hidden. Raw output remains owner-only outside Git/web roots. The original recovery set retains full filesystem metadata, histories and WIP; a same-disk recovery set is not an off-device backup.

Evidence: owner-only `/path/to/workspace/Projects/.webos-migration/run-20261115-32-historical-evidence/`, especially `historical-output-index.json`, `source-owner-summary.json`, `commands.json` and `restore-proof.json`. The first conservative pass and subsequent ANSI/Node/Rust terminal-format recognition are retained separately for audit. Source bytes were never rewritten by classification. No source/operator commands or old report-producing workflows were executed.

The122 component repositories and current runtime selection are unchanged by this documentation/evidence phase. Whole source organization and full-suite functional acceptance remain incomplete.
