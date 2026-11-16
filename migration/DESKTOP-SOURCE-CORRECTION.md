# Existing Desktop/Workspace viewer source

User decision: the existing viewer shown at beta.ksu.codes is the intended desktop component. It needed organization into its independent source silo, not a rewrite. The replacement was unsolicited and is not retained as an alternate source implementation.

`platform/desktop/active-system/` owns the existing app.js, desktop-apps.js, reference.js, bootstrap.js, index.html, style.css and visual assets. All92 files were compared byte-for-byte with the original Desktop-Preview source before and after correction. No original viewer code or assets were modified or recopied.

Removed from the Desktop working tree: src/controller.mjs, src/index.mjs, src/style.css and the two replacement-only tests. Removed the replacement's ESM exports/test command; package metadata now identifies the existing classic-script source entry. No replacement backup or archive was made; ordinary Git history was not rewritten.

The parent formerly imported the removed mount/controller interface. Its development builder now stops before creating output rather than constructing the wrong viewer. Existing parent browser tests for that interface are obsolete, not passing evidence for the intended source. No shim, restyling or new viewer implementation was added. Future assembly wiring is separate from this source organization task.

Known bootstrap dependencies have separate owners: Runtime desktop modules, Terminal, v86 and account/file/application components. Keeping the old source does not mean enabling a Linux dependency in a new minimum or copying other owners into Desktop. The source is not advertised as a standalone deployable tree. Full beta parity is not a completion gate.

No website, service, worker, route, account state, remote or original source was changed. Existing parent artifacts/input-files.json and untracked tests/wordcraft_baseline_browser.mjs were left unchanged. Private desktop-source-correction-20261116 records source hashes and preservation checks.
