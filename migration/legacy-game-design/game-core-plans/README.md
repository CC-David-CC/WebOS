# Core-only staging for the six new games

This folder follows the earlier implementation ladder: define the canonical
rules model and its pure tests before any view, audio, save adapter, or
presentation work. These documents intentionally contain no UI decisions and
no claims about the desktop or phone surface.

Each core file records:

- audience and learning target;
- canonical state and what is explicitly excluded;
- the only legal actions and their preconditions;
- deterministic rules and invariants;
- win, loss, and retry outcomes;
- seeded random-number use and bounds;
- the logical snapshot for later save/load work;
- pure model tests that must pass before a view is started.

Once a core is reviewed, the next stage is the same order used for the original
games: pure model tests, then desktop loop, then phone controls, then save/open
and invalid-save recovery, then presentation and accessibility, and only then
optional Rive guides.

Games:

1. [math-path](math-path.md)
2. [fraction-farm](fraction-farm.md)
3. [pocket-conquest](pocket-conquest.md)
4. [rule-detective](rule-detective.md)
5. [word-weaver](word-weaver.md)
6. [market-math](market-math.md)
