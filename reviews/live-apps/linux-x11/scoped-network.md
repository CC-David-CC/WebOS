# Terminal and Linux X11 guest networking

On ksu.codes the Accounts service now has the handler for issuing short-lived guest network grants. The operator restarted this service once to install the handler. A fresh registered account signed in before the restart and renewed the same session afterward. Public issuer and configuration responses matched across the restart. The public relay returned HTTP 403 for a request without an admission cookie. Zero production grants were active during these checks.

The backend archive was built from WebOS `63541d0aa67a85fc26792603577675ee8a9d7643`. Its SHA-256 is `3067f69b84a92f871ebe3069b323bd08f8bb8693ab8fc2aaefc4531ba6e25f1f`. Its retained Accounts, Storage and Runtime packages matched the previous backend receipt before the scoped modules were added. The static desktop has a separate release and test record. [Chromium and Files](chromium-input.md)

In an isolated network namespace on the production host, the packaged handler admitted a temporary test subject and launched QEMU. Ordinary and anonymous sessions were denied. Revocation ended the connection and terminated QEMU in 1.028 seconds with 298 seconds left on the grant. The registered session could still renew. An earlier integration check reached the designated SSH server from both guests and verified its host key.

The remaining hosted check is to connect from the normal desktop menu using a temporary signed-in account, revoke that connection while it is active, and verify ordinary users and Anon retain loopback. Owner enablement follows that check.
