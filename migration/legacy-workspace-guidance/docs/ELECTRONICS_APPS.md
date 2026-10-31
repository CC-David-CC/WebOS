# Electronics apps: working scope

The electronics tools are separate, lazy-loaded apps using the desktop's
account-backed My files and their own window lifecycles. Include useful example
projects, test actual simulation behavior, and avoid describing a visual
component as an electrical model. No Web Serial or esptool integration is
part of this work.

1. **Arduino Simulator:** AVR8js executes real ATmega328P HEX firmware in a
   worker; Wokwi Elements visualize modeled pins. Start with a compiled Blink
   example, account-file firmware loading, independent windows and serial
   output. Evaluate and benchmark browser-local AVR compilation and v86 Debian
   toolchains before offering either; do not suggest a sketch was compiled
   unless it actually was.
2. **Pico Simulator:** RP2040js executes real RP2040 firmware including a
   MicroPython REPL. Its upstream currently documents missing SSI flash-write
   support, so implement and test flash programming, erasure and persistence
   before claiming arbitrary filesystem writes. Include a MicroPython GPIO
   example and explicit firmware provenance.
3. **Circuit Simulator:** evaluate and integrate a distributable, browser-local
   ngspice WASM solver, with runnable analog examples, plots and My files. An
   interactive schematic editor requires its own usable integration.
4. **PCB Designer:** evaluate tscircuit's distributable browser packages and
   code-first editing, with an example schematic/board and fabrication outputs
   saved through My files.
5. **Digital Logic:** evaluate DigitalJS and its circuit formats, and include
   working combinational and sequential examples.

CircuitJS1, CircuitVerse, EEcircuit, Circuitera, PyMCU Playground and
AVR8js-Falstad were also requested for evaluation as separate tools where
viable. Check each project's license, dependencies, offline behavior and
maintenance before adopting or distributing it. Mixed-signal
CPU/analog coupling needs an explicit time and voltage interface and is not
provided merely by embedding both tools. Each app must stop workers and release
owned resources when closed; expensive emulation must not block the desktop UI.
