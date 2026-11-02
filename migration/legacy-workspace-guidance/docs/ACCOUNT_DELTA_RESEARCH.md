# Account file transfer research

This is a source-only candidate, not a deployment or a storage backup system.
Normal same-origin account authorization, per-user folders, quotas, pacing and
one-use signed operation proofs remain in force. Servers advertise optional
binary-read and delta capabilities; clients fall back to existing signed
base64 reads and full-file uploads when the corresponding capability is absent.

A replacement starts from the server's already stored version: the signed
signature request supplies the exact prior SHA-256 and receives bounded 64 KiB
block signatures. The browser uses rolling Adler-32 to locate matching blocks,
including after insertions/deletions, and confirms each match with SHA-256.
It sends a signed, hash-bound, bounded binary sequence of copy/literal records.
The gateway verifies the patch hash, account and prior version, reconstructs to
a temporary file with range/operation/output limits, verifies the whole result's
SHA-256, then rechecks the prior version and atomically publishes. The weak
checksum is only a matching hint. No cross-account chunk store is used.

Reads can stream raw binary instead of base64; the browser validates the
response length and SHA-256 before returning it or installing it in the mirror.
Each active transfer is admitted and charged under existing quota/pacing rules.
Four active gateway slots bound concurrent scratch use; a maximum-size delta can
use up to two bounded temporary files plus the normal atomic save file.

An interrupted delta is retried from the start, and a lost response after commit
is reconciled against the server's current version. This is **not** persisted
byte-offset resumption: an interrupted initial full upload restarts in full.
A remote concurrent edit produces a conflict rather than being overwritten.
Local-first and old-server fallback behavior remain unchanged.

The real isolated signed-account Chromium test uses fetch-body byte counters,
not DevTools interception; totals exclude HTTP/TLS overhead. A 104 MiB example
sent 109,054,230 bytes for initial upload, 4,408 for an unchanged save, and
71,469 for a one-byte edit (139,789 bytes received for the edit, mainly block
signatures). Random-data 8 MiB testing showed a one-byte insertion also sends
about 69 KiB; binary reading reduced received bytes from about 11.19 MiB of
base64 JSON to 8.39 MiB. The test checks disconnect retry, lost commit reply,
malformed signed patch, version conflict, another account, corrupt hash/length,
mid-stream truncation, rejection before mirror installation, recovery, legacy
fallback and transfer quota accounting. See `tests/file-delta-account-browser.test.mjs`,
`tests/file-delta-large-browser.test.mjs`, and `tests/gateway-delta-test.py`.
The browser tests require the isolated preview/account fixture and a local
Chromium CDP endpoint. They do not qualify public deployment, real-world mobile
networks or behavior under arbitrary external filesystem mutation.

The measured 104 MiB result was repeated after integrating the browser-byte
snapshot fix; no generated bundles, dependencies, or fixture accounts are
part of this source branch. A real implementation review and broader failure,
resource and concurrency qualification remain before any deployment.

The follow-up responsiveness and cancellation fix yields periodically while
scanning unmatched blocks and checks whether the session is still valid. Disk
worker results are retained through repeated cancellation so snapshot file
descriptors can be closed before releasing admission. Focused tests cover a
128 MiB unmatched scan in headless Chromium and Node, cancellation, shifted
block reconstruction, and repeated cancellation of fd-producing disk work.
This does not substitute for the signed-account integration test on the final
candidate, concurrent load testing, or physical-phone performance testing.

The final `be6283c1` code was retested with a freshly created loopback-only
issuer and private account store. The signed 16 MiB account test passed edit,
insertion, conflicts, corrupted reads, retries, lost reply and account isolation.
A signed 104 MiB test passed: the initial upload sent 109,054,230 bytes and a
one-byte change sent 71,469 bytes, excluding transport overhead. Two distinct
accounts also ran overlapping 8 MiB uploads and simultaneous delta saves. An
in-flight full-upload abort sometimes happened after the server had received the
whole upload; the test waited, checked the exact result hash and reconciled
either a committed replacement or the prior version. Proxy connection-reset logs
were observed for intentionally aborted browser requests. The isolated fixture,
accounts, browser contexts and temporary test dependencies were removed. These
checks do not establish performance on a physical phone or full server capacity.
