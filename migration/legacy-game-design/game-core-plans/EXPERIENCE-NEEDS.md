# Experience needs — 3rd-to-5th-grade learning games

This discovery pass describes what the six planned games need as experiences,
not just what their rules models can compute. It is intentionally wider than
the current core plans and the 28-game desktop review. Anything marked
**core-visible** belongs in the model layer and can be tested without a UI;
everything else is a later presentation, desktop, or classroom decision.

## Audience principles

The player is 8–11 years old, may be playing independently, in a classroom, or
beside a parent. That means:

1. The child succeeds quickly and understands why.
2. Difficulty is about the problem, never about the child.
3. A wrong answer is information, not failure.
4. Decisions matter more than reflexes; there is no required timer.
5. Progress and mistakes are private by default.

No game should introduce accounts, avatars with contact, public names,
leaderboards, social feeds, or a login step for the child. The platform account
already exists for persistence; the game must not create a second identity.

## Universal experience contract

Every game, regardless of subject, must provide these five moments:

- **Enter:** a 30-second-or-less introduction that names the goal and the one
  thing the player will practice.
- **Play:** a seated, finite activity with visible controls and no dead ends.
- **Understand:** after a miss, a worked example or model for that exact
  problem before the next attempt.
- **Finish:** a private result screen with stars, what was practiced, and one
  encouraging next step.
- **Return:** a saved session opens paused at the same logical boundary.

The model must therefore be able to answer, without any view:

- what skill or learning target this session practices;
- whether the current step was a first try;
- what the next step is after a correct answer and after a miss;
- a stable end-of-session report for the player and, later, a parent or
  teacher;
- how much of the bounded content remains.

This is currently missing from the models: each has phase and stars, but no
common report or learning-target contract.

## Feedback and assessment needs

- Immediate feedback distinguishes "correct" from "correct after help".
- Feedback text is concrete and names the math or rule, not the player:
  "That misses by 3," not "You are wrong."
- A miss triggers one worked model, then a nearby problem in the same skill.
  It never replays the identical item immediately.
- Hints are bounded, do not lower the learning target, and are recorded so the
  final report can distinguish independent work from supported work.
- Stars represent first-try mastery, not speed. Practice time is optional and
  excluded from scoring.
- A session can be completed with low stars; completion is never blocked by a
  mistake count.

## Adaptation needs

- Adaptation operates per skill (facts, fractions, territory tactics, rules),
  never on a single global score.
- The difficulty ceiling is the grade band. A child can move down, but the
  game never drifts above the selected grade without an explicit adult or
  player choice.
- Changes should be visible enough to explain ("Now I'm getting these right,
  so the next problems use bigger numbers.").
- Randomness is seeded. Two children with the same seed and choices see the
  same session, which keeps replays reviewable and testable.

## Per-game experience needs

### Math Path

- Visual model per skill: number line or ten-frame for add/subtract, equal
  groups for multiply/divide, and a two-step order for mixed facts.
- Hint removes one distractor and marks the hint used.
- Report lists each skill, answered, correct, and current difficulty.
- A "facts I know" screen is more motivating than a global percentage.
- Timer is opt-in and separate from stars.

### Fraction Farm

- Shading, equivalent, compare, order, and addition each get a distinct visual:
  bar, circle, number line, or side-by-side model.
- Equivalent choices must show the same amount visually, never only numerals.
- Explanation must display the common denominator used by the rule model.
- Hints can remove one wrong choice for choice-based tasks.

### Pocket Conquest

- Turn feedback names the phase (Reinforce, Attack, Fortify) and shows what the
  AI did, including the dice values.
- Before a battle, the game can show the exact odds from the bounded dice
  model; the odds are informational and never decide the roll.
- Captures and eliminations are explained with the armies before and after.
- There is no gore, weapon, or real-war imagery. Defeated units are returned
  to a "garage" or "table edge," not destroyed.
- AI difficulty is labeled Easy/Normal/Determined, not Dumb/Smart.

### Rule Detective

- Examples are cards the child can compare attribute by attribute, not dense
  tables.
- Testing a card gives a "fits / does not fit" result with the matched
  attributes highlighted.
- A hint reveals one tested attribute of the rule, records the cost, and is
  never free text.
- The structured guess control should offer attributes and values so a child
  never has to type a rule.

### Word Weaver

- Sound-out hint requires audio only after a user gesture; a text alternative
  spells the syllable or shows the definition when audio is unavailable.
- Definition and part of speech are shown before a hint is spent.
- Wrong letters return to the tray with an explanation of the first mismatch.
- The final report separates solved words, hints used, and first-try words.

### Market Math

- Every question has a receipt or coin model; cents are shown with real
  denominations, not a single number.
- Estimate bands are drawn on a number line or price chart.
- Change is explained coin by coin, and two-step problems show both steps.
- Decimal display never reveals floating-point error; it is derived from the
  integer-cents model.

## Desktop and platform needs

- Synchronous mount and independent instances, as in the existing games.
- Pause on focus loss, minimize, workspace switch, and hidden tab; resume is
  explicit.
- Save to My files at a phase boundary, restore paused, and reject malformed
  or foreign saves without replacing the live session.
- Phone and desktop are both first class. For the two board-like games, large
  touch targets; for word/math games, no tiny text fields.
- Sound starts muted and is unlocked by a user gesture. Visual feedback never
  depends on sound.
- No XR requirement for these six games.

## Accessibility needs

- Keyboard-only play for every action.
- Screen-reader labels on every control, state, dice result, and worked model.
- Color is never the only information carrier.
- Reduced motion disables decorative animation; gameplay state remains
  unchanged.
- High-contrast mode remains readable.
- Fonts and line spacing are comfortable for early readers; no all-caps
  paragraphs or low-contrast microtext.

## Privacy and classroom needs

- All six games run locally. There is no network AI, leaderboard, analytics,
  or third-party asset fetch.
- Save files contain the logical session and learning report, no personal
  narrative, photo, or executable content.
- A teacher view, if added later, would read the child's own My files only
  with the platform's existing account rules; no new server service.
- Difficulty selection and grade label are visible to the parent/teacher, but
  the player is never publicly ranked.

## Gaps to close in the core models next

These are testable without any UI. The core foundation branch has now closed
items 1, 2, 3, 4, 5, and 6:

1. **Done:** a stable `report()` contract exists on every model: learning
   target, grade,
   phase, stars, attempts, first-try count, hints used, and remaining content.
2. **Done:** bounded, recorded hint actions exist in Math Path, Fraction Farm,
   Rule Detective, and Word Weaver. Market Math exposes a receipt/coin
   breakdown in its explanation data.
3. **Done:** Pocket Conquest exposes exact `battleOdds` and a before/after
   battle summary.
4. **Done:** difficulty and skill profiles are observable in the reports.
5. **Done:** malformed-save tests cover hint, attempt, and report state.
6. **Done:** a shared pure validator covers the common report shape.

The next branch should implement these model changes and tests first. Views,
audio, Rive guides, and desktop registration remain out of scope until the
models and their experience contracts pass.

## Snapshot compatibility before launch

The experience-rule changes add required state fields. Initial snapshots from
before these changes were tested against this version: Math Path, Fraction
Farm, Word Weaver, Market Math, and Rule Detective reject them; Pocket Conquest
accepted its tested initial snapshot. These games are not yet playable and no
production saves are known. The five changed cores now identify their snapshots as `*-core-2` and reject
old versions explicitly; Pocket Conquest retains `core-1` pending a full
compatibility review. No migration is provided. Before exposing persistence,
test all saved phases and malformed input, not only initial snapshots, and
provide a migration if existing snapshots must be retained.
