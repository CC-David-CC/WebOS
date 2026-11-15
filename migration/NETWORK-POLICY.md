# Shared network policy

`libraries/network-policy/` independently owns access-policy validation, trusted-proxy address parsing, incoming-login/guest guards, configuration management and rule rendering. It is a reusable library, not another deployment service. The parent selects it as a submodule; Accounts, Runtime and Linux do not receive copied policy implementations.

Eleven original source/config/documentation/test paths from desktop snapshot `4f72ea86928666189b32f6f05c2c697a37341d06` retain history and exact baseline bodies/modes. Mechanical baseline `b58e555de27c800ff2bfccbb6ba70af1fc8af206`; selected package `5bba00d90a8aea770e2ffb73299c241a73812519`. Public namespace is `webos_network_policy`. Packaging/test fixture paths changed separately. A further generic fix delays the optional maxminddb import until the download command executes, after argument parsing and before network activity.

Original and installed-wheel tests:10 pass,1 existing optional-country-database test skips. Assertions are unchanged. Eight modules and the captured default JSON load from the installed wheel with source/original/primary/recovery hidden and network isolated. Download command help works without the optional dependency. Actual GeoIP lookup remains unverified: dependency/database pin, licensing/provenance and real lookup testing remain required. No database or download was substituted.

No policy is enabled in the first desktop/backend. No real listener, firewall rule, user/account state or host configuration changed. Live proxy/guest integration and human/agent workflow qualification remain open. Shared human/agent operations must reach the same protected domain implementation; this module does not itself grant identity/file permissions. Current tests prove core validation/guards/rule rendering, not an operational network deployment.

Private maps, baseline/installed logs, retained failed initial import probe, clean build proof and checkpoint: `/path/to/workspace/Projects/.webos-migration/run-20261115-38-network-policy/`. External publication and license review are separate gates.
