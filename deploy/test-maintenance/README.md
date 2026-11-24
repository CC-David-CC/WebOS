# Test account maintenance

The scheduled ksu.codes test reset selects disposable WebOS accounts. The Files cleanup records the selected subjects, retires their access, removes their private home directories, and retries interrupted cleanup. This source is an operator tool with access to private state.

The browser assembly and the running backend can pin different Storage revisions. The reset uses the hosted Storage cleanup implementation at `51dc679f00086c1e9e2900442812d49e050ef18e`. The adjacent tests use disposable directories. [Hosted Storage source](https://github.com/CC-David-CC/storage/tree/51dc679f00086c1e9e2900442812d49e050ef18e/src/webos_storage) · [Cleanup tests](test_reset_files.py)

The systemd timer runs every four hours at midnight, 04:00, 08:00, 12:00, 16:00 and 20:00 UTC. For a separate test installation, render the service template with its service user and absolute test root. Install the wrapper and driver together in the libexec directory named in the unit. File cleanup needs the installed backend packages and configured state paths. The wrapper supports a read-only preview before enabling the timer. [Service template](webos-ksu-test-account-reset.service.in) · [Timer](webos-ksu-test-account-reset.timer)
