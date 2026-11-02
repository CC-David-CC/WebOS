# Game catalog gap plan

This plan fills the catalog's missing seats: third-to-fifth-grade skills games,
a turn-based territory strategy with a bounded local AI, and pattern/word
reasoning. It assumes the existing desktop contract from the game preview
review: synchronous `mount`, one owner per instance, deterministic seeded
rules, account save/open through My files, pause on focus loss, and no new
server compute.

## Coverage recommendation

Four games are the minimum to cover every gap named in the review:

1. A number-facts or arithmetic path game.
2. A visual fractions game.
3. A Risk-like territory game with a dumb-but-legal AI.
4. A pattern or rule-discovery game.

Six games are the comfortable target, adding a word-building game and a
grade-five money/decimals game so each of grades 3, 4, and 5 has its own
anchor rather than borrowing from a neighboring band.

## Category

The four existing directories are engine/product groups, and none is the right
home for these titles. Arcade implies reflex/action, Physics and World carry XR
requirements, and Interactive implies Rive-first presentation. The new games
are seated, rule-first, flat-screen games that should not inherit XR or an
engine merely for membership.

Add one new group:

`05-core-learning-strategy`

- Mode: Screen only; no XR plan.
- Engine: DOM + Canvas2D where a board or tiles are needed. No new runtime.
- Presentation: clean visual model first. A small Rive guide is optional for
  two titles later and never substitutes for the rules.
- Registry and Files identity: stable IDs and `.game.json` saves exactly like
  the existing previews.

The total then becomes 28 existing + 4 core additions, with two optional
follow-ups for a 34-game catalog.

## Wave A: four required games

### 1. Math Path — number facts, grades 3–4

Core loop: a seeded path of 18–24 spaces presents one generated expression per
space. The player picks the value, an estimate band, or a number-line target
before moving. Correct moves advance; a miss shows a worked model, then
re-asks a related problem.

- Content: addition/subtraction, multiplication/division tables, mixed facts.
- Difficulty: per-skill accuracy raises or lowers the fact pool.
- Clock: no global timer by default; an optional practice timer is separate
  from scoring.
- Win/fail: reach the end with stars per section; no dead-end failure.
- State: seeded route, fact pool, difficulty profile, stars, RNG.
- Grade labeling is explicit and used only for difficulty, never player
  humiliation.

### 2. Fraction Farm — visual fractions, grades 4–5

Core loop: a small farm board presents fraction tasks as bars, circles, and
number lines: shade a fraction, find equivalent fractions, compare, order, and
add/subtract simple same-denominator cases.

- Content generation derives problems from small bounded denominators (2–12).
- Every answer has a visual model, not just numerals.
- Progress: unlocked plots; no economy or speed requirement.
- State: lesson track, generated task, visual choices, RNG, stars.

### 3. Pocket Conquest — Risk-like territory, grades 4–5+

Core loop: 24–30 connected regions, 2–3 AI rivals, region bonuses, and bounded
dice battles. A turn is reinforce, attack, fortify. Win by owning the map.

- Rules first: adjacency, army counts, region control bonuses, one defender
  versus up-to-three attackers, integer outcomes, no hidden rolls.
- AI: one greedy one-ply policy built on the same legal-move interface as the
  player. It takes the best expected-value attack or reinforcement each turn,
  never teleports, and cannot exceed its budget.
- Seeded RNG and exact logical snapshot; the AI is revision-guarded so pause,
  undo, save, close, or load invalidates stale work like Chess Study does.
- Session scope: one map with 3 difficulties rather than a long campaign.
- Presentation: simple polygons and labels; adjacency is drawn from the model.

### 4. Rule Detective — pattern and logic, grades 3–5

Core loop: a hidden rule over visible attributes (shape, color, count, size,
pattern) is presented with fitting and non-fitting examples. The player tests
cards, proposes the rule, and receives a scored explanation.

- Generator produces rules from an explicit attribute grammar, never arbitrary
  strings.
- Difficulty: number of attributes, noise examples, and rule negation.
- Win: identify the rule within a bounded test budget; replayable seeds.
- State: rule, tested cards, guesses, budget, score, RNG.

## Wave B: two optional games

### 5. Word Weaver — spelling and vocabulary, grades 3–4

Build target words from letter tiles with sound-out hints and definitions.
Session is short, seeded, and forgiving: letters stay visible, and a wrong
placement explains itself rather than locking.

### 6. Market Math — money and decimals, grade 5

Give change, compare prices, estimate totals, and solve two-step shopping
problems with coin and receipt visual models. Decimal arithmetic stays within
bounded two-place money.

## Sequencing

1. Write each rules model and its pure tests before any view.
2. Bring up the desktop loop, pause/resume, and phone-sized controls.
3. Add save/open, invalid-save recovery, and two-window independence.
4. Finish accessibility (labels, keyboard, reduced motion) and a short visual
   pass.
5. Then decide whether a Rive guide or extra modes are worth the cost.

Do not add content levels, art, or another game until the four required models
are playable and tested. The success test is a parent or student completing a
seated 10-minute session where the decisions, not timing or luck, carry the
outcome.

## Core-first staging

The six cores are now defined in
[game-core-plans/](game-core-plans/README.md) as pure models with state,
actions, invariants, seeded RNG, snapshots, and pre-view tests. They are
intentionally separate from the original 28-app handoff validator until the
models are reviewed and the handoff is extended to 34 designs. No view, audio,
save adapter, Rive brief, or engine choice exists for them yet.

The wider learner-experience contract, accessibility, privacy, and per-game
feedback needs are in
[EXPERIENCE-NEEDS.md](game-core-plans/EXPERIENCE-NEEDS.md).
