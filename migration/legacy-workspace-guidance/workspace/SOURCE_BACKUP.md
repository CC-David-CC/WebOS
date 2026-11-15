# Desktop preview: source-only Git snapshot

This snapshot tracks the desktop source, public app source, build and test
scripts, dependency manifests and documentation. It includes the separate
`active-system/`, `desktop-lab/` and `served_apps_public/` trees; their similarly
named app folders are distinct and must not be synchronized automatically.

It deliberately excludes generated builds and releases (`.build/`, compiled
app bundles, cache manifests and generated offline workers), installed packages
(`node_modules/`, `.venv/`), downloaded runtime libraries and models (including
v86, Whisper and Stockfish binaries), generated guest boot images and the
binary image/font resources. It also excludes private keys, account databases,
user files and local secrets. Existing tracked files from earlier repository
history are not removed by these ignore rules. Exclusions leave the local files
untouched; they are not backed up by this source-only snapshot.

A fresh checkout will require dependencies and runtime assets to be fetched or
rebuilt before it can run. Keep the pinned manifests, lockfiles, licenses and
build scripts: for example `active-system/scripts/vendor-chess.py`, the
`active-system/tools/*-builder/package-lock.json` files, the app builder, the
v86 preparation scripts and `served_apps_public/chess/engine/manifest.json`.
The manifest describes the Stockfish files but does not itself download them.
Runtime state, account data, service credentials and the live server's database
need their own authorized backup; this Git snapshot does not provide one.

The most recent operating notes are in `PAUSE_HANDOFF_2026-10-29.md` and the
latest entries at the end of `HANDOFF.md`. Check those against current service
state before deployment; older statements in the documentation can be stale.
