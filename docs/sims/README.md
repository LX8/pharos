# The simulator corpus — validated mechanisms of social change

*Reproducible, seeded, stdlib-only simulators of the cascade/tipping mechanisms
behind the verified critical-mass theory. Each one is **validated by a unit test
that asserts it reproduces a published result** — a falsifiable-science
discipline, applied to social dynamics. Run them: `make sims`.
Validate them: `make verify` (the tests).*

> **What a simulation here is — and is not.** These explain **how** a mechanism
> behaves under stated assumptions. They do **not** predict **which** real event
> will happen. Social systems are reflexive (people react to forecasts — the
> Lucas critique), only observationally calibrated, and have no universal
> constants. A simulator that reproduces a known result is a *validated
> mechanism*; pointed at a real situation it is, at best, a *labeled scenario
> under assumptions*. See [`../what-is-tested.md`](../what-is-tested.md) and the project
> [`../../ledger/`](../../ledger/).

## Two tiers (leave nothing mislabeled)

- **Tier 1 — VALIDATED-MECHANISM** *(built, below).* Classic agent-based / network
  models that reproduce an exact published result. Cheap (laptop, no GPU),
  deterministic with seeds, falsifiable: a sim that can't reproduce its known
  result is wrong.
- **Tier 2 — SCENARIO-SPECULATION** *(deliberately NOT built).* LLM-agent
  "societies" (e.g. OASIS, generative-agent populations). Real new capability,
  but in a documented **validity crisis** (black-box, irreproducible,
  stereotype-amplifying, expensive). If ever explored, it would be labeled
  SPECULATION and used only for hypothesis generation — never as evidence.

## Tier-1 corpus

| Simulator | Model | Validation target (the published result it must reproduce) | Status |
|---|---|---|---|
| [`sim_threshold_cascade`](../../src/sims/sim_threshold_cascade.py) | Granovetter (1978) | The knife-edge: thresholds 0..99 → **100** act; nudge one person 1→2 → **1** acts | ✅ validated |
| [`sim_network_cascade`](../../src/sims/sim_network_cascade.py) | Watts (2002) | The **cascade window**: a lone seed triggers global cascades only inside a band of mean degree z (frequent at z≈1.5–4 for φ=0.18; **none** by z≈8) | ✅ validated |
| [`sim_committed_minority`](../../src/sims/sim_committed_minority.py) | Xie 2011 / Centola 2018 | The sharp tipping point: **below ~10%** the minority can't flip the population; **above**, the flip time collapses | ✅ validated |
| [`sim_reverse_dominance`](../../src/sims/sim_reverse_dominance.py) | Boehm; Lanchester (Johnson & MacKay 2015); Gavrilets 2008 *(inspiration)* | A coalition levels a dominator iff **k² > r** (square law → numbers crush strength); that same critical mass is the **separatrix of a level-or-submit best-response dynamic** (by construction, not Gavrilets' emergent basin) | ✅ validated *(threshold)* |
| [`sim_complex_contagion`](../../src/sims/sim_complex_contagion.py) | Centola–Macy (2007) | A complex contagion (≥2 reinforcing contacts) **sweeps a clustered** ring lattice but **stalls once randomly rewired**; a simple contagion spreads either way, faster through long ties | ✅ validated |
| [`sim_civil_violence`](../../src/sims/sim_civil_violence.py) | Epstein (2002) | The **legitimacy lever + tipping point**: quiescent while legitimacy is high, rebellion ignites below a threshold and grows as it falls *(burst time-series needs a larger run — not asserted)* | ✅ validated |
| [`sim_opinion_dynamics`](../../src/sims/sim_opinion_dynamics.py) | Deffuant–Weisbuch (2000); Fortunato (2004) | The **consensus threshold ε = 1/2** (above it the population converges to one opinion, topology-independent) and the **monotone fragmentation** as confidence narrows *(the ~1/(2ε) cluster count is a loose rule of thumb — not asserted exactly)* | ✅ validated |

## What each validated sim establishes (and does not)

- **Granovetter** — *establishes:* outcomes can hinge on the threshold
  *distribution*, so near-identical crowds can riot or not. *Does not:* tell you
  any real crowd's thresholds.
- **Watts** — *establishes:* whether a single trigger can go system-wide is
  governed by network connectivity (the cascade window), not by the trigger's
  size. *Does not:* predict a specific real cascade.
- **Committed minority** — *establishes:* a committed fraction above a critical
  mass (~10% in this model) flips the whole population, and the flip time
  *collapses* past the threshold. *Does not:* fix any real movement's number —
  Centola measured ~25% experimentally; the threshold is model/context-dependent
  (see [`../../ledger/SAA-009-no-universal-threshold.md`](../../ledger/SAA-009-no-universal-threshold.md)).
- **Reverse dominance** — *establishes:* under Lanchester's square law a coalition of
  ~√r levellers overpowers an r-times-stronger dominator (the exact, independently-pinned
  result); the level-or-submit best-response dynamic then has that same critical mass as
  its separatrix *by construction* — linking the anthropology of resisting tyranny to the
  project's own critical-mass theory. *Does not:* reproduce Gavrilets' *emergent* bistable
  basin (we cite it as inspiration, not a result), nor show real societies achieve this;
  the empirical claim is **CONTESTED**
  ([`../../ledger/SAA-012-reverse-dominance-hierarchy.md`](../../ledger/SAA-012-reverse-dominance-hierarchy.md))
  — this is the *logic*, not reality.
- **Complex contagion** — *establishes:* a behaviour needing multiple reinforcing
  contacts spreads through clustered networks and **stalls** when random long ties
  replace local redundancy (while a simple contagion only speeds up). *Does not:* settle
  the *real-world* generality of the clustering prong, which this corpus grades CONTESTED
  ([`../../ledger/SAA-010-energy-is-complex-contagion.md`](../../ledger/SAA-010-energy-is-complex-contagion.md))
  — the reach-vs-reinforcement trade-off (arXiv:2411.07907) shows clustering wins only in a
  small parameter region.
- **Civil violence** — *establishes:* legitimacy is the lever and the response is a
  *tipping point* — a grieved population stays quiescent until legitimacy crosses a line,
  then rebels. *Does not:* reproduce Epstein's punctuated **bursts** at this compact scale
  (stated honestly, not asserted), nor predict any real unrest.
- **Opinion dynamics** — *establishes:* under bounded confidence, whether dialogue produces
  consensus or stable mutually-deaf camps turns on one parameter — above ε = 1/2 the population
  converges to a single opinion, and the number of final camps grows monotonically as confidence
  narrows (the micro-foundation under the polarization thread,
  [`SAA-026`](../../ledger/SAA-026-affective-polarization.md) / [`SAA-027`](../../ledger/SAA-027-depolarization-megastudy.md)).
  *Does not:* assert the exact ~1/(2ε) cluster count (a stochastic rule of thumb), nor claim any
  real public sorts its opinions this way.

## Honest limits & ethics

- **Mechanism, not prophecy.** No sim here forecasts a real event; reflexivity,
  calibration uncertainty, and chaos forbid it.
- **Dual-use.** A model of "how to tip a population" is what manipulation wants.
  These stay at mechanism / aggregate level — never an operational tool to move
  specific people. *Watch power, not people* ([`../../NOTICE`](../../NOTICE) §7).

## References

- Granovetter, M. (1978). Threshold Models of Collective Behavior. *AJS.*
- Watts, D. J. (2002). A simple model of global cascades on random networks. *PNAS.* https://www.pnas.org/doi/10.1073/pnas.082090499
- Centola, D. et al. (2018). Experimental evidence for tipping points in social convention. *Science.* https://www.science.org/doi/10.1126/science.aas8827
- Centola, D. & Macy, M. (2007). Complex Contagions and the Weakness of Long Ties. *AJS.*
- Epstein, J. M. (2002). Modeling civil violence. *PNAS.* https://www.pnas.org/doi/10.1073/pnas.092080199
- Larooij & Törnberg (2025). Validation is the central challenge for generative social simulation. *AI Review.* (Tier-2 caveat.)
