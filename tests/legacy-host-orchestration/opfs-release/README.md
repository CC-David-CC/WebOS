# Historical OPFS candidate tests and models — port before execution

Nine unchanged sources preserve controlled/native issuer fixtures, three browser
drivers, packaging/configuration/process-death tests and a pure transition model
with its test. They retain their selected histories and assertions. None is
registered with supported WebOS test/build commands or imported during extraction.

Several drivers launch servers, subprocesses or browsers and rely on old origin,
gateway, authentication and source paths. Do not run broad discovery or these
drivers. Their disposable-state assumptions, target isolation, dependencies,
public component APIs and side effects require review before a separate port.
Never use production account/key state or replace missing persistence with a fake
success. A pure model is not current account/browser/host acceptance.

The existing `floor_journal.py` reference belongs at
`deploy/legacy-backend/isolated-hosting/historical-inputs/floor_journal.py`.
The native-continuity fixture remains at
`tests/legacy-host-orchestration/isolated-hosting/historical-inputs/native-continuity-fixture.py`.
See the exact source map in `migration/OPFS-RELEASE-SOURCE.md`. Old sibling/import
locators are not ported; no duplicate helper or compatibility shim makes them run.

All source bytes/modes and relevant histories match the capture; Python/Node
syntax and bounded context checks pass, and every file restored independently
offline with the original workspace and assembly hidden. No old code executed.
This is preservation, not new runtime behavior or complete publication clearance.
