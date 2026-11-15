# Primary references checked for this handoff

Checked during preparation on 2026-10-20/21. Package designs and TTL/size choices
are this handoff's proposed policy, not requirements asserted by these sources.
No claim that an evolving API works on all browser/OS/driver combinations.

1. v86 upstream: https://github.com/copy/v86
2. Pinned serial example (constructor and actual serial API):
   https://raw.githubusercontent.com/copy/v86/cc37f35c43bf14865d74ad76879ecf9410f69eb1/examples/serial.html
3. Pinned v86 declarations (events/options, async image/Range notes):
   https://raw.githubusercontent.com/copy/v86/cc37f35c43bf14865d74ad76879ecf9410f69eb1/v86.d.ts
4. W3C WebRTC Recommendation:
   https://www.w3.org/TR/webrtc/
5. W3C Web Cryptography (latest page redirects to the Level 2 draft; this project
   uses the established P-256 ECDSA/SHA-256 primitives, not experimental additions):
   https://www.w3.org/TR/webcrypto/
6. IETF RFC 7518, ES256 wire signatures and algorithms:
   https://www.rfc-editor.org/rfc/rfc7518.html
7. IETF RFC 8725, JWT type/algorithm/issuer/audience validation practices:
   https://www.rfc-editor.org/rfc/rfc8725.html
8. OWASP Password Storage Cheat Sheet:
   https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
9. IRTF RFC 9106, Argon2 specification:
   https://www.rfc-editor.org/info/rfc9106/

Input provenance: uploaded `write a handoff(1).zip` and
`codiserver-browser-v86-auth-handoff-v0.1.0.zip`. Their supplied metadata describes
an external prepared v86/Debian workspace; its contents were not in these ZIPs.
Original desktop assets/license notices remain with the web package. No fonts,
browser binaries, authority private keys, user credentials or guest images are
redistributed. Inspect exact source-asset notices before a public release.
