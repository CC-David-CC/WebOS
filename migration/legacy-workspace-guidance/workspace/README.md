# CodiServer — simplified development branch

This is a separate working copy on the `simplified` Git branch. It does not
change or deploy the other branches or the current live site.

- `apps/system/`: independently built system desktop apps (Files, Text,
  Terminal, Calculator and Help).
- `apps/individual/`: template source for account-specific apps. Directory
  names alone do not enforce permissions.
- `active-system/`: desktop, browser VM, signed account and file services,
  guest network service, and build tools.
- `active-system/storage/`: browser mirror source and notes on private server
  account and system state. The `accounts/data/` and `accounts/state/` folders
  are ignored, empty examples; they are not a configured server.
- `tests/`: focused browser-storage and Files/Text workflow tests.

The desktop requires registration or sign-in. Files and Text use an
account-scoped local-first mirror; Linux's browser VM filesystem remains
separate and temporary. Browser storage may be cleared or evicted; the server
needs its own protected backups. Files are private through signed gateway
requests and service-side authorization, with private Linux permissions for the
service's state and account folders. The server does not give each website
account a separate Linux UID.

Chat, Chess and Rooms were removed from the desktop, together with their active
browser peer transport. Audio/video WebRTC is only a possible future feature.
This branch is still a work in progress: legacy deployment, historical tests
and backend code need further removal or adaptation before a standalone
simplified server can be deployed. Existing `HANDOFF` and older docs describe
historical branches and deployments, not the state of this branch.

See `SIMPLIFIED_HANDOFF.md` for build and verification notes. Generated assets,
dependencies, real user data, private databases and keys must not be committed.
