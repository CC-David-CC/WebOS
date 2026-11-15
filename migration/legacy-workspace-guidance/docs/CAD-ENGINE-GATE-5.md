# Gate 5 Engineering intent experimentation and system synthesis

User-defined next gate, 2026-11-04. **QUEUED after Gates 1–4.** The goal is an
engineering environment where geometry, physical models, requirements, decisions
and evidence remain explicitly connected. Reliable sketch solving, modeling,
parametric history, Files and manufacturing handoff remain indispensable.

This gate contains several independently qualified stages, including open
research. Recording a research objective does not establish its feasibility or
promise autonomous engineering correctness. Later needs inform early contracts;
current implementation remains Files and Gate 1.

## Conceptual capability ladder

| Era | Central activity |
|---|---|
| CAD 1.0 | Draw geometry |
| CAD 2.0 | Model parametric geometry |
| CAD 3.0 | Simulate and optimize designs |
| CAD 4.0 | Generate designs from requirements |
| CAD 5.0 | Autonomously investigate and validate engineering alternatives |
| CAD 6.0 | Discover and synthesize new physical systems |

These are the user's conceptual stages, not official industry classifications or
predictions. Each retains the instruments and correctness obligations below it.
Three planning horizons distinguish emerging assistance, next-generation intent
and experimentation systems, and longer-term mechanism/system synthesis research.
They are scope categories, not claims about named papers or available products.

## N01 Requirements and traceable decisions

- [ ] Represent quantities, units, domains, operating cases, bounds, objectives,
  priorities and evidence needed to judge a requirement.
- [ ] Distinguish authored requirements, assumptions, inferred interpretations
  awaiting confirmation and unresolved questions. Human validation can use
  parametric rendering, calculations and simulation; a plausible rendering alone
  cannot prove a physical requirement.
- [ ] Gripper example: payload up to 2 kg, 150 mm envelope, 24 V supply, gripping
  range, available processes/tools, cost, safety margins and reliability.
- [ ] Link each design decision to applicable requirements, considered
  alternatives, rationale, assumptions and supporting or contradictory evidence.
- [ ] Answer why a dimension or mechanism was selected without inventing a
  calculation: for example, thinner candidates exceeded the modeled deflection
  limit, conditional on stated material and boundary data.
- [ ] Changing a requirement invalidates affected conclusions and schedules
  appropriate checks; it does not silently certify the old design.

## N02 Functional semantics

- [ ] Give features explicit roles: fastener clearance, bearing seat,
  lubrication passage, locating feature, access opening or other defined use.
- [ ] Preserve mating, load-transfer, manufacturing and clearance relationships
  separately from geometric coincidence or visual similarity.
- [ ] A shaft-size edit identifies dependent bearing, housing, seal and process
  requirements; unresolved functional relationships become actionable failures.
- [ ] Equal geometry does not imply interchangeable function. An inferred role
  remains a proposal until accepted or supported by an explicit authored rule.

## N03 Inverse design and representation conversions

- [ ] Desired behavior defines a bounded search over allowed dimensions,
  positions, geometry, material choices and other declared design variables.
- [ ] Track feasibility separately from objective quality; preserve operating
  cases, forbidden changes and resource limits for every candidate.
- [ ] Qualify sensitivity, differentiable geometry, constrained and
  multi-objective optimization where supported, with uncertainty and failure
  behavior appropriate to each method.
- [ ] Keep B-rep, implicit geometry and meshes behind explicit conversion
  contracts: source revision, units, tolerance/error, topology/material identity,
  approximation and supported round-trip meaning.
- [ ] Preserve one authority for authored parameters and intent. Converted
  geometry cannot silently become a competing editable source.
- [ ] Reconstruct and independently reanalyze the accepted final candidate.
  State whether the result is a better feasible candidate, a local optimum,
  a tradeoff set or an unresolved search; never imply an unproved global optimum.

## N04 Physics within design decisions

- [ ] Connect geometry/material/condition revisions to applicable forward studies
  and requested outputs, with explicit missing properties or assumptions.
- [ ] Separate interactive estimates or surrogates, numerically verified studies
  and physical validation. Their authority and uncertainty remain visible.
- [ ] Make predicted mass, deflection, stress, natural frequency or process
  feasibility attributable to the method and supported domain that produced it.
- [ ] Preserve convergence, mesh/domain sensitivity, reference comparisons,
  software/settings and relevant material-data evidence.
- [ ] Fast viewing/play physics cannot silently certify a design. A failed or
  stale study cannot pass a requirement or score as a successful candidate.

## N05 Adaptive parametrics

- [ ] Distinguish: A, regenerate with the same authored construction; B, propose
  an approved reorganization preserving functional requirements; C, no feasible
  result established within the stated permitted family.
- [ ] An enclosure shrinking from 120 to 80 to 50 mm exposes boss/rib collisions
  or packaging limits, rather than silently deleting required structure.
- [ ] Reorganization is a reviewable transaction with changed decisions,
  preserved requirements and repeatable verification; it is not an automatic
  overwrite of the accepted design.
- [ ] A failed search or numerical nonconvergence is not proof of impossibility.
  Scope infeasibility claims to the actual family, assumptions and method.

## N06 Experimental engineering

- [ ] Maintain hypothesis → experiment → evidence → updated model → next
  experiment as explicit linked records.
- [ ] Propose simulations, material comparisons, friction sweeps, coupons,
  force measurements or load cases to reduce a named uncertainty.
- [ ] Define expected observations, controls, repeatability, cost and stopping
  rules before choosing or executing an experiment.
- [ ] Compare expected information gain or another declared selection criterion;
  retain failed, inconclusive and contradictory observations.
- [ ] Stop or request missing evidence when current tools cannot establish a
  conclusion. More explanation cannot substitute for obtaining evidence.

## N07 Mechanism and architecture synthesis

- [ ] Compare mechanism families as well as dimensions: cam/follower, Geneva
  with linkage, crank/slider, gear actuator or electromechanical alternatives.
- [ ] Separate geometry, material topology, mechanism, multidisciplinary
  architecture and requirements-level changes in candidate descriptions.
- [ ] Preserve comparable functional interfaces, operating cases and evaluation
  criteria across alternatives; changing the problem is an explicit proposal.
- [ ] Explore whether another handling method, such as magnetism or vacuum,
  better meets the accepted objective. Do not assume a gripper is required merely
  because an initial proposal used one.
- [ ] Research acceptance: independently reproduce a bounded synthesis exercise,
  account for rejected alternatives and identify unresolved assumptions.

## N08 Specialized engineering agents

- [ ] Define tool-backed responsibility for mechanical, structural,
  manufacturing, materials, electrical, controls, reliability, verification and
  coordination work. Roles need evidence and permissions, not just personas.
- [ ] Assign exact base revisions, owned paths/model operations, inputs, outputs,
  bounded resources, tests and review conditions to each independent package.
- [ ] Conflicting proposals are compared against requirements and evidence;
  agreement or agent votes cannot establish engineering truth.
- [ ] Browser, workstation and service execution share attributable job contracts
  without requiring all agents or providers to open/edit an ordinary project.
- [ ] Coordinator integrates reviewed transactions serially; rejected or stale
  results cannot alter an accepted model or another account's files.

## N09 Physical feedback

- [ ] Keep nominal design, manufactured geometry, observations and inferred
  material/contact/process parameters as distinct versioned records.
- [ ] Calibration carries units, sensor/procedure identity, alignment, operating
  conditions, uncertainty and applicable revision/range.
- [ ] Compare predicted and observed behavior, explain discrepancies through
  testable hypotheses, and propose explicit model revisions.
- [ ] A measurement never silently overwrites nominal geometry. Corrections and
  revised assumptions remain inspectable, reversible and independently checked.

## N10 Shared machine and human operations

- [ ] Human UI, scripts, agents, simulators and optimizers discover and invoke the
  same authorized validated operations against stable IDs and revisions.
- [ ] Use explicit transactions, typed constraints, dependency inspection,
  deterministic behavior where possible, undo/redo and structured failures.
- [ ] Bind asynchronous jobs to account, document, revision and window lifetime;
  recheck before commit and reject expired or cancelled results.
- [ ] A failure leaves accepted authored state intact and explains which of the
  five Gate 1 subsystems failed. No unofficial agent-only mutation bypass.
- [ ] Save/reopen and export preserve intent and provenance without an AI provider
  connection. Provider integration remains unsupported until separately supplied.

## N11 Spatial interaction

- [ ] Spatial workcell views can expose reachability, collisions, motion,
  constraints, experiments and candidate comparisons from the same system model.
- [ ] A viewport or spatial scene is an interaction surface; opening or closing
  it cannot change engineering correctness or become the document authority.
- [ ] XR remains a deferred side-branch opportunity below foundational work;
  see `planning/CAD-LEARNING-CSG-XR.md`. This gate does not activate it.

## N12 Learning from outcomes

- [ ] Reuse attributable passed/failed designs, discrepancies, defects, assembly
  observations, revisions and tradeoffs with their applicable operating domains.
- [ ] Distinguish learned statistical promise, physical laws, numerical results
  and verified measurements. Record out-of-domain use and unresolved uncertainty.
- [ ] Evaluate learned proposals against independent held-out tasks and current
  requirements; retain counterexamples and prevent training/test leakage.
- [ ] Prior experience may prioritize a candidate but cannot certify it for a
  new load case without the required evidence.

## N13 Multidisciplinary system synthesis

- [ ] Describe geometry, software, control logic, power, sensing, physical models,
  maintenance and operational requirements in one connected system definition.
- [ ] Greenhouse example: compare harvesting architectures spanning perception,
  navigation, mechanisms, controls, manufacturing and plant-damage requirements.
- [ ] Each alternative lists unverified assumptions and useful discriminating
  experiments. Interface failures and discipline-specific limits stay explicit.
- [ ] Bound the task and independently reproduce the claimed system behavior;
  open research remains open when no defensible result has been established.

## N14 Capability and maturity records

- [ ] Track semantic design, intent-to-CAD, inverse/differentiable/physics-native
  design, adaptive parametrics, mechanism synthesis and experimentation
  independently from multi-agent, feedback, learning and system-synthesis work.
- [ ] Give each package its demonstrated scope, emerging/research status,
  prerequisites, unsupported cases and evidence, rather than a single maturity
  percentage or a promised date for all autonomous engineering.
- [ ] Keep modeling breadth, parametric reliability and engineering validity
  independent throughout this gate, as defined in Gate 4.

## N15 Connected intent and evidence model

Five concepts connect specialized representations; they do not replace them:

| Concept | Meaning |
|---|---|
| Entity | Identified part, feature, body, mechanism or system with its specialized data. |
| Relationship | Authored dependency, functional interface or physical interaction. |
| Requirement | Typed condition/objective and its applicable cases and verification rule. |
| Decision | Selected alternative, rationale and affected requirements/revision. |
| Evidence | Attributable calculation, simulation, observation or validation result. |

- [ ] Connect goals → accepted intent → constraints/decisions → design graph →
  geometry/systems/behavior → evaluation → evidence → reviewed design revision.
- [ ] Keep the sketch solver, geometry kernels, topology, feature graph, assembly,
  physical study and Files contracts specialized and independently testable.
- [ ] Answer which questions remain open, assumptions need testing, alternatives
  are physically plausible, tradeoffs are unavoidable and results actually
  demonstrated. A disproved candidate remains a useful recorded outcome.
- [ ] Preserve evidence applicability and invalidate dependent conclusions after
  design/material/condition/solver changes; no stale result appears current.

## Qualification slices and current boundary

| Slice | Observable result | Required prior capability |
|---|---|---|
| 5A | Requirements and functional roles drive a reviewable parametric change with traceable decisions. | Gate 1 identities/transactions and relevant Gates 2–4 operations. |
| 5B | A reproducible forward study evaluates a bounded candidate search and the final accepted revision. | Qualified physical-system/material/study contracts and reference-checked solver. |
| 5C | The environment chooses and records an informative experiment and updates a model explicitly. | Evidence applicability, uncertainty and experiment/job contracts. |
| 5D | Different mechanism or system architectures are compared under common requirements. | Qualified component interfaces and discipline-specific evaluation methods. |
| 5E | Physical feedback and learned experience improve independently verified candidates. | Measurement provenance, separation of nominal/observed state and held-out evaluation. |
| 5F | A bounded multidisciplinary synthesis produces defensible system-level evidence. | All relevant qualified slices; unresolved research may block this outcome. |

The existing magnetic sensor fixture and material-aware enclosure remain useful
bounded workflows; this horizon does not replace them or require every physics
branch before they can be qualified. No printer or Bambu Studio is required for
the current core 3MF milestone. See `CAD-ENGINE-END-TO-END.md` for execution and
failure handoffs across the full program.
