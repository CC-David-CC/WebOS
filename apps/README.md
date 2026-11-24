# WebOS apps and server components

The directories in this catalog are Git submodules. Each opens the source revision selected by WebOS. Some are browser launchers, while others provide app packaging, demos, or source under development. A directory in this catalog does not imply a live launcher.

The component matrix lists all 143 app sources, eight platform services, and 33 engines, libraries, assets, tooling and legacy components. It identifies the 130 launchers reported by the hosted viewer. [Component and launcher matrix](CATALOG.md)

## Account, Files, and mail

| Component | Responsibility | Source |
| --- | --- | --- |
| Account Management | One browser app serves signed-in **My account** and permission-scoped **Manage users**. Account, retention and mail lifecycle checks have run on staging. | [Account Management](./account-management) |
| Accounts and Login | Registration, sign-in, session policy, and the sign-in interface. | [Accounts](../platform/accounts) · [Login](../platform/login) |
| Files and Storage | Files browser, per-account home access, file operations, and transfers. The scheduled test-account reset coordinates with Storage. | [Files](./files) · [Storage](../platform/storage) · [Reset and cleanup source](../deploy/test-maintenance) |
| MailCraft | Mail browser, server-side mailbox grants, and WebOS-to-JMAP sign-in. Stalwart stores and delivers mail. | [MailCraft](./mailcraft) · [Mail integration](../deploy/mailcraft) |
| WebOS Chat | Registered Chat frontend, conversation membership, messages, live delivery, and read positions. The repository owns its Python backend under `server/`. | [WebOS Chat](./webos-chat) |

## Compute, networking, and platform services

| Component | Responsibility | Source |
| --- | --- | --- |
| GPU Monitor and Image Studio | Each app owns its browser interface and its `server/` adapter. The shared queue coordinates jobs. Worker services run probes and renderers. | [GPU Monitor](./gpu-monitor) · [Image Studio](./image-studio) · [Job queue](../scripts/webos_compute) · [Worker services](../platform/services) |
| Remote Desktop | The owner-authorized browser client, session checks, and monitor relay live together in the app repository. | [Remote Desktop](./remote-desktop) |
| Weather | Shared server-side forecasts, location lookup, provider cache, and attribution. | [Weather service](../scripts/webos_weather) |
| Browser and Linux guests | Browser relay admission and session leases, guest networking, and worker source. Availability depends on the selected deployment. | [Browser](./browser) · [Linux guest](./linux) |
| Desktop and Runtime | Desktop launchers, shared app contracts, session integration, and runtime policy. | [Desktop](../platform/desktop) · [Runtime](../platform/runtime) |
| Rendezvous and Publication | Independent service source for peer coordination and publication. | [Rendezvous](../platform/rendezvous) · [Publication](../platform/publication) |
| Backend assembly | Wires the platform packages and app-owned adapters into the server process. Packages source independently of live account or mail data. | [Server entry point](../scripts/run_development.py) · [Backend packager](../scripts/package_viewer_backend.py) |

App-specific server code travels with the app. Shared services have a single owner and can serve several apps. Operator credentials, account databases, mailboxes, and Files homes belong to the installation.

## Release source differences

The November 24 viewer was assembled from `b2384408`. Seven components use public source commits that preserve the reviewed source distribution. The public commits for DesignCraft, FigCraft, LightCraft and VectorCraft incorporate the release updates on their existing public integration histories. The two geometry engines and Microduck retain their published source snapshots. Build receipts identify the revisions used by each build.

| Component | Assembly revision | Public source revision |
| --- | --- | --- |
| apps/designcraft | `8e5f309bed61` | [cc32dbacb362](https://github.com/CC-David-CC/designcraft/tree/cc32dbacb36278c0283538366db8d5a2dc522c16) |
| apps/figcraft | `2837cfdc32e3` | [db8862f37ffa](https://github.com/CC-David-CC/figcraft/tree/db8862f37ffaaebe51bcdbd1ea042751a2ec1720) |
| apps/lightcraft | `b1988c539ee9` | [585054909ef7](https://github.com/CC-David-CC/lightcraft/tree/585054909ef7cdcf4b8b93cb4878cf7b85da424e) |
| apps/microduck | `bad23452a2bb` | [daabd956b96f](https://github.com/CC-David-CC/microduck/tree/daabd956b96fe93a1bead77cdf23b1f7c770c417) |
| apps/vectorcraft | `c54691a43f7a` | [480d7edb9c56](https://github.com/CC-David-CC/vectorcraft/tree/480d7edb9c56b8527f8ce3515fcbf32c6fc0de3d) |
| engines/manifold | `9056c1fab8f5` | [4f7e212191d0](https://github.com/CC-David-CC/engine-manifold/tree/4f7e212191d0756428a44927ef82828243a2f23c) |
| engines/occt-interpreter | `530f4b99b867` | [1a3fe7de54bd](https://github.com/CC-David-CC/engine-opencascade/tree/1a3fe7de54bd1449f99682bdcce7588be91a38a2) |

The viewer manifest separately records the delivered Weather app (Pohoda) at `aa8687e87bf8` and Pico Simulator at `65c313213b14`. The source assembly selects `f76f997926c3` and `84f451dfeeac`, respectively. [Live viewer manifest](https://ksu.codes/viewer-release.json)

The server package retains three platform revisions independently of the viewer. Use the server revisions to examine the code running on the mail and Files host.

- [Accounts backend at c53a2f64b287](https://github.com/CC-David-CC/accounts/tree/c53a2f64b287b1f59bd90cdcd355766c5d713e63)
- [Runtime backend at f461ab03bdf6](https://github.com/CC-David-CC/runtime/tree/f461ab03bdf6595ac76927b427f9e8f130353e51)
- [Storage backend at 51dc679f0008](https://github.com/CC-David-CC/storage/tree/51dc679f00086c1e9e2900442812d49e050ef18e)
