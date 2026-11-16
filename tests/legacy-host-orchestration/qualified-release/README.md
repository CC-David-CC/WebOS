# Historical release and asset transition fixtures — port before execution

Forty unchanged source files preserve release/asset transition tests, disposable
signed/static fixtures and namespace bootstraps/runners. They retain selected
histories and assertions. No file is imported or registered by supported WebOS
test/build commands, and no historical test or fixture ran during extraction.

Do not run broad discovery or these scripts. Some create mount namespaces,
invoke sudo, start browsers/Caddy, call literal installers, mutate root-owned
disposable paths or kill child processes. Other controls explicitly use simulated
host/systemd adapters. Their historical PASS/FAIL and simulation scope are not
current release, custody, browser, storage or host compatibility acceptance.

Old source paths and package/asset/configuration pins are deliberately unchanged.
Review input closure, public component APIs, privilege/side-effect boundaries,
explicit actor/resource/revision authority and disposable account/key state before
any separate port. No fixture is a real account migration, permission bypass or
implicit authority to contact a host. Do not use real credentials, reuse prior
account state, make missing persistence appear successful or weaken assertions.

The related25 deployment source/template/note files remain under
`deploy/legacy-backend/qualified-release/`. Earlier copied helper sources keep
their existing owners; no new helper repository or duplicate live service was
created. Mechanical extraction precedes documentation and future functional work.
See `migration/QUALIFIED-RELEASE-SOURCE.md` and the private phase90 source/commit,
copy-context, syntax, byte/mode and independent-restore proofs.
