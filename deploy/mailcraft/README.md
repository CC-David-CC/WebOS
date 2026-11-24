# MailCraft server integration

MailCraft uses the signed WebOS session to open a registered user's approved mailbox over JMAP. The gateway and its tests live here. The WebOS backend packager includes the gateway as `mailcraft_sso.py`. [Gateway](sso_gateway.py) · [Tests](test_sso_gateway.py) · [Packager](../../scripts/package_viewer_backend.py)

Stalwart owns mailbox content and delivery. The mail policy module maps mailbox IDs and SQLite grants to service permissions. The relay and ingress tools configure the host from operator-supplied settings and credentials. Production bindings, relay credentials, account state, and message contents live on the installation. [Mail policy](policy.py) · [Relay configuration](configure_relay.py)

After approving an existing mailbox, an operator can bind it to a registered account for automatic WebOS sign-in. Run the binding tool on the mail host with the username, private login file and `--accounts-db` path. Use `--check` to preview the binding. A binding takes effect when the backend reloads its private credentials. [Mailbox binding tool](bind_webos_mailbox.py)
