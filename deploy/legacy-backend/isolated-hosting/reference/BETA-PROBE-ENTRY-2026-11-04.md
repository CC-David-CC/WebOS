# Protected beta Files probe entrypoint candidate

Source-only review candidate; no host installation or probe account created. `ops/beta_probe_entry.py` SHA-256 `8f700b9f88a5e8d376b9d5b3372de66218ef9a942e5efb6773828c9a88802b8e`. It is intentionally separate from the already staged 31-file installer input and existing activation bundle. The trusted operator must externally verify the exact entrypoint bytes and root-custody ancestry before invoking Python; self-checks cannot verify code before interpreter startup.

The candidate's fixed installed path is `/srv/codi-connected/operators/beta-files-probe-entry-v1.py`. It loads only the exact hash-pinned `beta_launcher.py`, `beta_files_preflight.py` and `beta_signed_probe.py` from `/srv/codi-connected/operators/files-install-input-ce18b7794adc2472/ops`, plus the JOSE module from the fully verified dd8 gateway release. It requires root, the expected hostname, safe path ownership and ACLs, root-private state, the existing host flock, no beta floor/transition journal, exact old beta issuer and gateway inventories, the existing service preflight, beta/main isolation and health, exact old beta unit hashes/identities, matching pinned beta policy and matching issuer/frontend configurations with no v2 metadata. It does not change routes, systemd, issuer, gateway, user accounts or keys other than creating its own dedicated probe account and known file. No main account is used.

`inspect` checks pre-transition dependencies and reports only whether a valid private config exists; it is not a signed health or provisioning recovery operation. `provision` creates the root-owned `0700` probe directory if absent, refuses unexpected files, and calls the existing `provision_private` once. The actual private config is root-owned `0600` at `/var/lib/webhost-ops/beta-files-probe/probe.json`; it contains credentials and must never be printed or copied into source, logs or public artifacts. Provisioning checks the same filesystem for `probe-provision.json` and `signed-probe-acceptance.json` first. The library durably journals registration and create intent before sending either mutation. An uncertain result remains journaled and blocks both further provision and inspect until explicitly reconciled; do not blindly retry. The entrypoint emits only generic state/error text and never prints the subject or credential. Existing activation health later performs the pinned signed known-file read; this entrypoint does not itself perform a create/delete acceptance cycle.

After independent review and protected placement of the exact source, the proposed commands (not executed as part of this work) are:

```sh
sudo -n /srv/codi-connected/venvs/517179c/bin/python -I -B /srv/codi-connected/operators/beta-files-probe-entry-v1.py inspect
sudo -n /srv/codi-connected/venvs/517179c/bin/python -I -B /srv/codi-connected/operators/beta-files-probe-entry-v1.py provision
```

Stop on a refusal; preserve private journal and investigate its actual phase and signed account/file state without exposing credentials. The legacy account/floor and health preconditions are intentionally fail-closed; do not work around a failed preflight by changing pins, disabling isolation, or using a real user.

## Disposable qualification

```sh
sudo -n /tmp/codi-audio-upload-19584-venv/bin/python -I -B research/beta-isolated-hosting/tests/beta-probe-entry-test.py
```

The runner accepts `CODI_PROBE_TEST_PYTHON`, `CODI_PROBE_TEST_NATIVE` and `CODI_PROBE_TEST_WORKER` overrides and defaults to the existing local sealed 166 issuer and dd8 gateway artifacts. It verifies their complete inventories before and after the test, uses newly generated disposable private state on `/tmp`, root-protected public fixtures under `/run`, dynamic loopback ports, and cleans only those fixture paths/processes. It passed real signed registration, known-file creation/read, private config custody and inspect; real signed registration and create with deliberately dropped successful responses retained their private journals and refused retries; lock contention and a floor refused before provisioning. The probe module instrumentation for dropped replies and mapped entrypoint paths, hostname, policy, origin and ports are fixture-only; real gateway verification and actual signed calls execute. Systemd unit checks, native service-manager readiness and main health are explicitly stubbed, and the frontend config endpoint is the issuer in this isolated fixture. This does not prove production systemd, actual main health, public ingress or a live account workflow. No fixture credentials or account state are preserved.
