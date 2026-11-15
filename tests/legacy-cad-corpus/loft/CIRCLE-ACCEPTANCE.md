# Signed two-circle loft acceptance — frozen oracle preparation

Native volume/point truth derives independently from the saved source circles,
frames and explicit seam angles. For coaxial same-orientation circles,
V=pi*h*(r0^2+r1^2+r0*r1*cos(delta))/3. The cross-section follows the ruled
correspondence, not a guessed cone when seam angles differ.

First fixtures: radii2 and4mm on XY planes at0 and30mm, delta0 andpi/2.
Expected volumes280pi and200pi respectively. Source radius2→3 must regenerate;
Undo/Redo must restore each expected physical result. Exactly6 analytic probe
points cover inside/outside/cap/lateral boundary. Source plane placement edits
remain required for full E15; initial fixtures do not waive that requirement.

Use genuine public New/create-empty-sketch-plane/append-sketch-primitive,
inspect-worker-lofts/inspect-worker-loft-regions and create-worker-loft.
Discover IDs/seams instead of inferring ID spelling. Save through ordinary
MyFiles, verify exact synced server bytes, fresh-login/Open and re-query native
geometry. Compare source/history/IDs/counters and preserve readonly query state.
No model seed, fake native result, sampled display-mesh classification or caller
supplied geometry. Pin exact served core/outer/native assets and all driver code.
Keep original failure receipts. No full Gate1 or human parity claim.

Oracle tests PASS3 groups: analytic cylinder/frustum/twist volumes independently
checked by numerical section integration, descending plane placement, and7
unsupported/identity/degenerate refusal variants. The first test-fixture generated
negative zero at elevation0 on descending planes, failing deepStrictEqual;
fixture now writes authored zero explicitly. This was not a native kernel defect.
No signed app run has been performed for these new fixtures yet.
