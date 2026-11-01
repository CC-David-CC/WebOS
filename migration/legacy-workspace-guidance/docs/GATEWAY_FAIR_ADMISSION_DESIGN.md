# Gateway admission compatibility experiment

This is a protocol design and unwired local experiment, not a deployed
security boundary. The live gateway retains its shared pre-authentication
fixed-minute ceiling. An authenticated-account limit inserted after the current
one-use grant was verified would not prevent one client from consuming that
shared ceiling first. It was tested and removed; do not deploy that partial cap
as a fairness solution.

The gateway currently receives traffic through a loopback socket proxy. Its peer
address is the proxy, and `/gateway/` does not overwrite a dedicated client-IP
header at Caddy. Browser-provided forwarding headers are untrusted. A single IP
is also a poor account identifier for a classroom behind shared NAT. Issuer
session tokens are opaque to the gateway; an arbitrary public key in an unsigned
challenge request is not evidence of account ownership.

## Candidate protocol and compatibility

1. Add an issuer endpoint that validates the existing live registered session,
   password generation and session-bound key using the normal signed one-use
   issuer proof. It issues a short-lived admission ticket signed by a pinned
   issuer authority. Its exact audience is the gateway, and its subject,
   session ID, session public key, expiry and random ticket ID are bound to the
   verified session. An admission ticket is not a file authorization and grants
   no path or operation permission. Limit response size and lifetime.
2. Add an enhanced gateway challenge accepting that ticket plus a short-lived
   signature by the ticket-bound browser key. The signature binds the exact
   gateway challenge route, request hash and a fresh random proof ID. Verify
   authority, audience, expiry, proof, request binding and replay before using
   the verified subject for an account budget. Do not trust a forwarded header
   or claim supplied without the issuer signature. Revalidate the eventual
   existing one-use file grant, proof, session and permissions as today.
3. Keep a strict overall bound, bounded request/crypto queues, a bounded number
   of tracked accounts and replay IDs, and separate rate shares for verified,
   malformed/unverified, and legacy traffic. Track accounts by issuer-verified
   subject so multiple devices share a budget and unrelated accounts behind the
   same NAT do not. Expire state; fail closed when full rather than evicting a
   live subject to let attackers reset it. Determine useful, configurable
   thresholds from real workload measurements, not the model's tiny test values.
4. Roll out issuer support first, then a gateway accepting both protocols,
   then clients. A new client uses enhanced admission only after an explicit,
   versioned capability response; it falls back to the old flow only when an
   old server explicitly lacks the capability, never on a 429, signature error,
   timeout or ambiguous response. Keep the old protocol in a separately bounded
   legacy share until old clients are retired. Gate the rollout and inverse with
   the existing protected operator, preserving state and testing older clients.

An **unwired issuer-side experiment** now lives in
`active-system/origin_service/experimental_gateway_admission.py`. Its two POST
routes issue a short-lived admission ticket only after the existing issuer's
one-use proof and registered-session, key, SID, disabled-account and session
generation checks. A capability GET is provided, and existing issuer/gateway
routes pass through the existing authority. Experimental per-account and
aggregate issuer budgets are bounded; the proposed values are not qualified
for deployment. The actual loopback WSGI test
`tests/gateway-admission-issuer-review.py` verifies ticket signatures and
bindings, forged keys, one-use proof, revocation before issuance, shared-NAT
account buckets, old gateway RPC compatibility and a `/hidden` mount prefix.
It does not test the gateway consuming tickets or a real browser negotiation.
Once issued, an offline-verifiable ticket is not instantly revoked on logout or
account disable; it remains valid for up to 20 seconds unless the final protocol
adds a revocation mechanism. That tradeoff requires an explicit security review.

An unwired gateway adapter in `active-system/gateway_service/experimental_admission.py`
and `tests/gateway-admission-gateway-review.py` exercises real signed loopback
issuer/gateway operations, legacy traffic, separate bounded shares, forged and
replayed proofs and expiry. Its random per-instance epoch is part of each
enhanced proof: a replacement gateway instance rejects the old proof and accepts
a newly signed one. This is an in-process instance replacement, not a tested OS
restart or multi-replica protocol. Separate bounded reader slots prevent slow
challenge bodies from occupying verification slots in a real TCP test. The
verification budget is also partitioned by endpoint, without trusting any
unverified identity claim; challenge verification cannot occupy the slots
reserved for file uses. In a bounded loopback test, 32 real, forged signed
challenges and a signed file operation run concurrently. A controlled stalled
challenge verifier leaves signed uses progressing. A negative control shows
that forged use requests can still saturate the reserved use lane: their identity
cannot be known until verification, so signed uses can still wait. Controlled
verifier delays are not performance measurements of cryptographic verification.
These controls do not resolve connection pressure, challenge starvation, issuer
exhaustion, or saturation within a lane. It has no production route; do not enable it.

An unwired client experiment lives in
`active-system/gateway_service/experimental_admission_client.mjs`. It validates
both issuer and gateway capabilities and the issuer-signed ticket before using
an enhanced, session-key-signed gateway challenge. A validated `stale_epoch`
response allows one capability refresh and newly signed retry. It does not fall
back after a 404, 429, malformed response, network error, authorization failure,
or other ambiguous failure. Even when explicitly enabled, legacy fallback requires
both endpoints to successfully advertise the exact legacy protocol version.
Existing old services do not advertise that signal and are deliberately
incompatible: the explicit-legacy test simulates those advertisements. A rollout
must design and deliver a trustworthy, versioned compatibility signal before
enabling fallback; do not interpret a generic 404 as permission to downgrade.

`tests/gateway-admission-client-loopback-review.py` exercises actual signed
issuer/gateway operations using Node Web Crypto. The separate
`tests/gateway-admission-browser-loopback-review.py` runs the same categories of
workflow using headless Chrome Web Crypto and an isolated same-origin loopback
proxy. They exercise simulated errors and simulated legacy advertisements; the
Chrome fixture changes the gateway epoch immediately before a signed challenge
to exercise the retry. These are not deployed proxy, multi-process, physical
phone, or sustained classroom-load tests. Run either using
`CODI_GATEWAY_RATE_ROOT=/tmp/codi-gateway-rate-v2-candidate-20261101` and
`/tmp/codi-audio-upload-19584-venv/bin/python`; the Chrome test additionally
requires the local Chromium and ChromeDriver paths configured in the fixture.

Before rollout, establish compatible signed-in clients and explicit old-server
negotiation; integrate the client without allowing downgrade on failures; make
fresh-proof retries safe after a consumed use proof; verify durable replay and
account budgets through actual process restarts, overlapping workers and
replicas; exercise signing-key rotation, revocation, issuer and gateway overload,
slow uploads, cancellation, same-NAT classrooms, and proxy origin boundaries.
Determine how to preserve admission capacity before signature verification,
measure mixed real-client load, and independently review this security design.
The epoch is per instance, not a cross-worker coordination or rate limiter.

The model test `tests/gateway-admission-protocol-model.py` uses real ES256
signatures, fixed mock time and tiny bounded budgets. It checks session/key and
request binding, two accounts behind one simulated transport, spoofed keys,
replay, bounded table pressure, expiry, and legacy/verified budget separation.
The model assumes that ticket issuance has already authenticated the issuer
session; it does not exercise the experimental issuer adapter, implement gateway
routes, browser negotiation, Caddy policy, replay ledger persistence, or a signed
file operation. It is not an end-to-end release test.

This approach does not guarantee service under attack. Signature verification
itself consumes resources before a sender can be classified; the current
four-operation queue and connection limits can still be saturated. A verified
Sybil with many accounts can consume the shared verified ceiling; a small
legacy share can be exhausted; expired or over-capacity tables can delay honest
clients. Restarts reset in-memory accounting unless replay state is made durable
or tickets are invalidated with a boot epoch. Cross-process/multi-replica
accounting, cancellation, retries with consumed proofs, token/key rotation,
reverse-proxy boundaries and shared-NAT abuse require explicit design and
adversarial tests. Do not enable an IP-based rule until ingress provenance is
established and classroom behavior is measured. A 100-user capacity claim
requires sustained mixed 100-account testing, including slow uploads, failures,
reconnects, and actual browsers, under the deployment's memory and CPU limits.
