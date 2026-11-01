# Simplified desktop: app guide

This beta desktop is intended for students exploring engineering, computing and creative work. Sign in, open **Applications**, and choose a tool. Use **Files → Upload** to bring in a computer file; open and save app work in **My files**. My files keeps a browser copy and synchronizes it to the account service when available. A synchronization or conflict notice needs attention: keep both versions and resolve the conflict in Files. Linux's temporary home is a separate drive and resets with the guest; copy work explicitly if you need to keep it. The desktop account does not grant access to unrelated outside services.

The table describes useful starting points, not a promise that every feature or file format has been reviewed. The detailed [review tracker](APP_UNIFICATION_PROGRESS.md) records tests and remaining work. Simulated results and exports must be independently checked before use on real equipment.

| App | Start here | Current boundary |
| --- | --- | --- |
| Files | Browse My files, upload, create, copy, rename and sync. To move a file, select it and choose **Move to…**. | Temporary Linux files are separate; folder moves are not supported. Dragging several files can be unreliable; if a move stops, check the destination before retrying. |
| Terminal | Explore the temporary Linux shell; use `nano` to edit. | Its files reset with the guest and are not automatically mounted into My files. |
| Text | Open or create a text/code file, edit and save. | Very large files can be slow and memory-intensive. |
| Help | Read beta contact and Linux information. | Help is not an exhaustive manual. |
| Calculator | Enter an expression or use the keypad; choose angle units and save a result as a text note. | Results are floating-point approximations; notes do not restore a calculator session. |
| Browser | Open a supported website or save a download to My files. | Experimental; temporary profile and no audio. |
| Document Editor | Write and save a report; export a PDF. | Not a Word editor. |
| PDF Viewer | Open, search and navigate a PDF. | Read-only; image-only scans need OCR. |
| Spreadsheet | Edit a workbook; import/export supported CSV or XLSX. | Advanced Excel compatibility is limited. |
| Data Explorer | Create the synthetic resistor example or open CSV, query with SQL, and configure a chart; save a project or CSV. | Large inputs can consume substantial memory. |
| Python Notebook | Run the measurement example with Shift+Enter or Run, edit it, then save to My files. The getting-started guide explains the two Python environments. | Untrusted notebooks are not isolated. Browser Python differs from the temporary Linux environment. |
| Image Editor | Create a blank image or open an image, edit, and save a copy. | Animated GIF editing is unsupported. |
| Audio Editor | Try the generated 440 Hz tone, or open or record audio; edit and export WAV. | Physical microphone behavior and multitrack project saving need more work. |
| diagrams.net | Open or create a diagram and save it. | Broader format and touch behavior remain under review. |
| Excalidraw | Draw a sketch, insert images from My files, save the drawing, or export a PNG. | Large embedded images use more memory and count toward the drawing size limit; physical touch needs testing. |
| SVG Editor | Try the example or draw vector artwork, then save an SVG. | Complex SVG and physical touch remain unverified. |
| Replicad | Choose a box or cylinder, dimensions and optional offset hole; inspect volume and surface area, then export a model. | This is a limited model generator, not a full CAD system; validate manufacturing dimensions. |
| Kiri:Moto | Open a model, configure slicing and export; save a workspace. | Check printer profiles and output independently before printing. |
| Mesh:Tool | Import and manipulate meshes; save a workspace or export geometry. | Undo history is not saved in workspace snapshots; verify geometry independently. |
| G-code Preview | Open printer G-code and inspect the path. | Supports a documented subset; it does not validate machine safety. |
| Arduino Simulator | Run an example or open supported HEX; inspect serial output and save an example’s C source. | Executes AVR firmware, but is not an electrical simulation. Browser compilation is not live. |
| Pico Simulator | Run Blink or load supported RP2040 firmware and inspect serial. | Firmware and peripheral support are partial; no physical-board validation. |
| Digital Logic | Try gates, adder and comparator examples, toggle inputs and inspect or save a truth table. | JSON combinational circuits only; no sequential circuits or full schematic editor. |
| Circuit Simulator | Try the voltage divider, RC filter or rectifier and inspect simulated output. | CircuitJS simulation is not a substitute for measurement or hardware validation. |
| Electronics Design | Work with breadboard, schematic and PCB views; save the project. | Component coverage and production-board validation remain incomplete. |
| Embroidery Studio | Create and save a project and export stitches. | Pre-release editor; machine compatibility and physical sewing are unverified. |
| Stitch Converter | Open SVG artwork, create a stitch preview, save editable artwork separately, then export a machine file. | Conversion may omit unsupported SVG; inspect the design and test-sew. |
| Falling Blocks | Play the preview, save a game and reopen it from Files. | Still in development. |
| Personal template | Example for app authors. | Not a finished end-user app. |

### Try a model-to-toolpath workflow

In **Replicad**, set the box dimensions, save the project and select **Create model** to save an STL in My files. In **Kiri:Moto**, use **Open from My files** to choose that STL, then select a printer profile and use its slicing and export controls. Save the resulting G-code to My files. Open that file in **G-code Preview** to inspect the drawn path; you can reopen it in another signed-in browser after it has synced.

This is an example of moving work between apps, not approval to run a printer. The G-code viewer omits homing movement and supports only a subset of controller behavior. Check the profile and toolpath with tools appropriate to the actual machine before using it.

Items shown disabled under System Tools are shared capabilities for apps, not independent applications. Third-party and AI features deferred from these apps are tracked in [Deferred app features](DEFERRED_APP_FEATURES.md).
