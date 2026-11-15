# Storage legacy mirror reference tests

Seven captured cache-unit test sources now live in Storage under `tests/legacy-mirror/`, with original capture histories preserved. Only their import locator changes to the repository’s own mirror module. Full assertion AST comparison confirms no assertions were altered or dropped. Production source and production dependencies are unchanged.

## Observed result: 3 pass, 4 fail

The exact captured-source snapshot and locator-ported owned source both report seven Node source-file subtests: three pass, four fail, none skipped/cancelled. The same four source files fail in each. The reference command genuinely exits with code1; there is no shell success override or omitted failing case. This qualifies source/port fidelity, not an all-green test suite.

The mismatches include bounded-read materialization counts and offline versus not-found/initial-sync expectations. Their appropriate current contract requires review before changing code or assertions. These are outcomes under a newly selected controlled dependency environment, not a claim about the exact historical test environment or a diagnosed current production regression.

## Dependency and reproducibility

The original fake-indexeddb version was not verified. The new test-only reference environment explicitly pins fake-indexeddb6.2.8 from public npm, with registry SHA512/tarball verification and a generated two-entry lockfile. The release has no runtime dependencies or install lifecycle scripts. Tests/package manifest and lock are separate from the production Accounts dependency, so standalone test setup does not query a private runtime package on public npm. Install scripts are disabled; clean verification installs only from the captured public-package cache.

Setup in Storage: `npm ci --prefix tests --ignore-scripts --workspaces=false`. Run: `npm run test:legacy-mirror-reference`. Test node_modules are ignored and not committed. Root production dependency maps and the existing owned-reference command remain unchanged.

Upstream documents an in-memory IndexedDB API implementation for Node tests, without disk persistence: https://github.com/dumbmatter/fakeIndexedDB#readme . The package license metadata is Apache-2.0; this is dev tooling, not a new runtime storage provider. No original environment version, browser equivalence, publisher-signature audit or account synchronization is inferred from a registry integrity check.

## Scope and independence

Tests run with all /home hidden and network, process, IPC and UTS namespaces isolated. Server objects are supplied doubles; no real browser, backend account storage, disk durability, physical second-machine or agent transport is exercised. The present minimum frontend build graph uses `src/webos_storage/client.mjs`/UserFiles, not this legacy mirror module. Its real server-backed acceptance remains separate.

A complete clean assembly repeats the same3-pass/4-fail outcome after pinned offline dependency setup. Seven source-assembly checks pass. Only Storage’s pin changes;123 other pins remain unchanged and124 independent repos remain represented. Mechanical source extraction precedes the separate locator/test-environment commit. No implementation, production dependency, source workspace, deployment or unrelated local edits changed.

Private phase59 retains registry/tarball/lock/notice hashes, original/current module bytes, initial and clean failure outcomes, full assertion-AST proofs, path/history/commit maps, commands/exit codes and resume state. This work leaves legacy cache compatibility and full suite organization/integration open.

| Original source | Owned test |
|---|---|
| `tests/mirror-archive-worker.test.mjs` | `platform/storage/tests/legacy-mirror/mirror-archive-worker.test.mjs` |
| `tests/mirror-bounded-read.test.mjs` | `platform/storage/tests/legacy-mirror/mirror-bounded-read.test.mjs` |
| `tests/mirror-commit-uncertainty.test.mjs` | `platform/storage/tests/legacy-mirror/mirror-commit-uncertainty.test.mjs` |
| `tests/mirror-idle-scheduling.test.mjs` | `platform/storage/tests/legacy-mirror/mirror-idle-scheduling.test.mjs` |
| `tests/mirror-migration-metadata.test.mjs` | `platform/storage/tests/legacy-mirror/mirror-migration-metadata.test.mjs` |
| `tests/mirror-verified-content.test.mjs` | `platform/storage/tests/legacy-mirror/mirror-verified-content.test.mjs` |
| `tests/mirrored-files.test.mjs` | `platform/storage/tests/legacy-mirror/mirrored-files.test.mjs` |
