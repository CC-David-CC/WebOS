# What this model does and does not prove

The small Python module tests stable node-derived room IDs, acyclic fixture moves,
atomic global peer admission, fixed-size replay windows and verified bounded blob
cache behavior. Its graph helper centrally constructs two cycles and floods a
single idealized public event. It has NO distributed discovery/repair, sockets,
browser tasks, cryptography, key epochs, game logic, queue scheduler, clock skew,
Byzantine proof or realistic traffic timing. No production app imports it.

The pure model is intentionally a separate test oracle, not a compatibility runtime.
Port the required invariants into the actual single browser implementation, then
run independent real RTC/lifecycle/negative witnesses. Do not count model success
as completion of the production gates.
