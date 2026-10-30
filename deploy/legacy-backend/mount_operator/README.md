# Managed desktop mount migration

This offline root operator moves the existing native, file and guest service
contexts together. It does not configure hosting, open ports, enable boot,
initialize accounts, copy private folders or restore databases. The underlying
native16 and independently sealed file/guest operators remain immutable.

`scripts/migrate-desktop-mount.py` requires an explicit protected native release,
its manifest digest and the existing managed configuration. `plan` is read-only.
`apply --base-path '' --seconds 86400` explicitly issues a bounded new signed root
revision for the same keys/realm and moves services to root. `recover` resumes
the retained `maintenance.json` operation with the same signed bytes. A rollback
is a new `apply --base-path /hidden` with a higher root revision; it is never a
database or user-file restore.

The native/global instance locks protect the outer transition. Separate helper
interpreters hold the existing file/guest backend locks across planning, stopped
metadata edits and backend start. This avoids importing different `guest_service`
packages in one interpreter. Requests and responses are bounded. EOF releases
helper locks; it does not perform a rollback. Only stopped services and exact
journaled old/new metadata bytes can be edited. The output paths, service users,
trust keys, policies, quotas and unit contents are derived and validated.

The root recovery fence advances before authority commit. Both existing publisher
ledgers change their endpoint/seed binding without replacing counters or cached
tokens. The online ledger is accessed as the steward user; root-owned unused
staging state may remain at zero publication count across repeated migrations.
Publisher-plan version2 hashes canonical JSON so journal sorting does not change
its binding. Runtime publication creates the next signed descriptor. Recovery
also recognizes an already advanced, correctly signed new-context descriptor.

The existing maintenance slot blocks ordinary native starts and root renewal
while pending. On failure, retain the journal and inspect/recover explicitly;
do not initialize ledgers, delete the journal, restore an old root database or
force unit settings under a live guest guard. Expired uncommitted delegation
plans are refused. No unattended root signing or unbounded delegation is added.

Native/file/guest services restart and streams can close. Only already saved
server files are durable. Browser RAM, unsaved drafts and a Linux VM snapshot are
not saved by this operator. A production deployer must coordinate the tested
hosting/cache transition and truthful maintenance notice separately.

Current verification is the retained private VM, including real root HTTPS
browser workflows and process deaths. See `evidence/configurable-mount.md` for
exact artifacts, retained failures, evidence and remaining production work.
