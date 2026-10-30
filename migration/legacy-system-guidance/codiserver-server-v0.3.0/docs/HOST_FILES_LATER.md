# Owner host files — later capability boundary, not current server scope

David's goal is access from his account to the actual files on the Linux host,
not merely a v86 guest directory or a client-side file picker. Retain that goal;
do not silently substitute browser storage. It is excluded from the initial
bootstrap/login service so that the public anonymous path cannot inherit it.

Implement later as a separate broker process with a distinct resource audience,
explicit owner subject provisioning, and current server-side authorization.
The owner mapping is the immutable server account UUID, never the display name
`owner`, `admin`, `root`, or whichever account registered first. Require explicit
out-of-band provisioning by David and reauthentication for sensitive grants.
A P2P identity certificate is not accepted as a host-files bearer token.

Start read-only with individually approved root directories. No default `/`,
`/home` or entire project-root export. The broker runs under the narrow UID/group
necessary for those files, independent of the public authority user. A virtual
browser guest receives no credentials and cannot invoke the broker on its own.
Avoid exposing raw host paths unnecessarily in errors or anonymous metadata.

Path operations must remain below an opened approved directory, reject escapes,
symlink/magic-link tricks and races, and bound file size/request rates. On Linux,
consider openat2 with RESOLVE_BENEATH/NO_MAGICLINKS and the selected symlink policy;
canonicalizing a string and later opening it is not sufficient against races.
Test concurrent rename/symlink attacks, encoded separators, dot segments, NUL,
permission denial, mount changes, revoked grants and interrupted transfers.

Writes are a separate explicit grant after read-only correctness: version/etag
precondition, atomic temporary-write-and-rename in the permitted directory,
conflict handling, quotas and provenance. No arbitrary shell endpoint is added
just to implement file operations. UI distinguishes browser guest files,
client-selected files and actual host files at every operation.

Before implementation, bind the real host, approved paths, account subject,
allowed operations and revocation/lifetime policy. This document does not infer
those values or authorize public exposure. The minimal server ZIP has no such
endpoint and cannot grant itself the owner's home privileges.
