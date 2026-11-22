# Electronics simulators from Files

Verified on ksu.codes November 22, 2026. Open each simulator from **Apps → Electronics**, save its example in Documents, close the app, then double-click the saved document in **Files**. The desktop opens the matching simulator with the saved revision.

| Project | Proof after reopening | Anon | Signed in |
|---|---|---|---|
| Arduino Simulator · .hex | Blink firmware ran and the D13 LED changed between on and off. The reopened firmware matched the saved 496 bytes. | [Screenshot](arduino-simulator-anon-reopened.png) | [Screenshot](arduino-simulator-signed-reopened.png) |
| Digital Logic · .logic.json | The AND circuit reopened with two inputs. Toggling the switches changed its output. The reopened project matched the saved 793 bytes. | [Screenshot](digital-logic-anon-reopened.png) | [Screenshot](digital-logic-signed-reopened.png) |
| CircuitJS · .circuit | The RC low-pass filter reopened with the same native circuit design. Simulation time advanced. The reopened project matched its own saved 550 bytes. | [Screenshot](circuitjs-anon-reopened.png) | [Screenshot](circuitjs-signed-reopened.png) |

Each signed-in test synced the save, closed its browser context, signed back in from a fresh context and reopened through Files. Each Anon test stayed in the same browser session, closed the simulator and reopened through Files without private file requests. All six checks ran against the production viewer with no candidate file overrides. Native revisions, file sizes and hashes are in the [release receipt](release.json).

The viewer digest is `3c5e7d361f288ffda7ee7bb1b444d8c95e403125dab7abc2962ee1872ff663df`. All four component commits and their Git mode 160000 pins were fetched independently. The hosted pins are on the release branch. WebOS main still had the previous component pins at this check. [WebOS release commit](https://github.com/CC-David-CC/WebOS/commit/45f18c85e9f9db4f381d0ecfda73a307ed5b2a5a)

**Open issues:** CircuitJS shows expanded menu lists over the schematic. Its pinned upstream includes a stylesheet that its WebOS build preparation removes. Arduino LED placement and Digital Logic's large-window layout have separate findings. These Files checks ran with Chromium mouse input. Physical touch remains open.
