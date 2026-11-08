# What is tested — and what is not

*The explicit map. Every load-bearing claim in this project, tiered by exactly how
far it has actually been tested — from machine-reproducible, down to chosen
commitments, down to what is untestable in principle. The answer to "can we test
everything?" is **no**; this page is where we say so, claim by claim.*

> **One rule:** *leave nothing mislabeled.* A claim may rest on an assumption — as
> long as the assumption is named and the claim never dresses itself up as more
> tested than it is.

## The tiers

| Tier | Meaning | How you check it |
|---|---|---|
| **T1 · Machine-verified** | Re-derived and asserted by code | `make verify` — reruns the complete offline unit-test suite + recomputes every indicator number |
| **T2 · Source-corroborated** | Checked against primary sources; not re-derived here | follow the citation; graded in the ledger |
| **T3 · Trusted input** | Third-party data/findings we rely on but do not produce | cite the source — we test our *use*, not their *production* |
| **T4 · Documented assumption** | A defensible modelling/analysis choice, not a tested fact | stated in the method; vary it and see what moves |
| **T5 · Commitment** | A chosen value; not an empirical claim at all | named as such; not for testing |
| **T6 · Untestable in principle / not built** | What no amount of work here can establish | named, with the reason |

---

## The map

### The indicator — `docs/indicators/wgi-governance.md`

| Claim | Tier | Where / how |
|---|---|---|
| "88% of changes are within measurement noise; 88 declines vs 54; VA 33:6" | **T1** | recomputed by `make indicators`; cross-checked 8/8 against the article |
| the z-test on the published 90% CI, and the code | **T1** | `tests/test_wgi_governance.py` (11 tests) |
| the raw WGI perception scores + their confidence intervals | **T3** | World Bank WGI — we don't re-survey the world |
| "the 0–100 score tracks real governance" | **T4** | WGI is perception-based; stated in the caveats |
| "the decade decline is concentrated in *voice*" | **T2** | a reading of the T1 numbers, corroborated by the literature; **not** a causal claim (stated at `:63`) |

### The ledger — `ledger/`

| Item | Tier | Note |
|---|---|---|
| ROBUST entries (SAA-001, 002, 004, 007, 008, 009, 010) | **T2** | verified against primary sources; each carries a falsification trigger |
| CONTESTED / OPEN / REFUTED (SAA-003, 005 / 006 / 011) | **T2, labelled down** | the grade *is* the statement of what is **not** established |
| the grading + falsification protocol itself | **T1 (of method)** | `ledger/README.md` |

### The simulators — `src/sims/`

| Item | Tier | Note |
|---|---|---|
| Granovetter knife-edge (100 act vs 1 act) | **T1** | exact, deterministic; `tests/test_sim_threshold_cascade.py` |
| Watts cascade window (z=2.5 → global, z=10 → none) | **T1** | validated stochastically with a fixed seed; `tests/test_sim_network_cascade.py` |
| φ=0.18, the ER-graph topology, the model rules | **T4** | modelling choices — vary them |
| "what a real crowd will actually do" | **T6** | mechanism, not prediction (stated in every sim docstring) |
| LLM-agent "societies" (Tier-2 sims) | **T6 · not built** | documented validity crisis; would be labelled SPECULATION, hypothesis-only |

### The theory of change & the bet

| Claim | Tier | Note |
|---|---|---|
| "committed minorities can tip systems; change cascades" | **T2** | ledger SAA-008; convergent literature |
| "open information → accountability → peace & prosperity" | **T4 + open** | the weakest link (the *warning-response gap*) is named in the article |
| "this project will measurably help" | **T6** | unprovable in advance; survivorship bias is named, not hidden |

---

## What is untestable *in principle* (and why)

No amount of work in this repository can establish these — and the reasons are
themselves well-established:

- **You can corroborate, never *verify*, an open-system model.** — Oreskes, Shrader-Frechette & Belitz (1994), *Science*.
- **You never test a hypothesis alone.** — the Duhem–Quine thesis: every test rides on untested auxiliaries.
- **Some systems can only be simulated, not shortcut.** — Wolfram, computational irreducibility.
- **Reflexivity.** People react to forecasts about themselves (the Lucas critique), so a social prediction can invalidate itself.
- **Chaos + incomplete state.** Sensitive dependence on unmeasured initial conditions forbids long-range social prediction.
- **Measurement carries error bars.** Even what we *do* measure is uncertain — which is exactly why the indicator flags only what beats its 90% CI.
- **Normative claims are not empirical.** "Watch power, not people"; "open societies are worth defending" — these are chosen (T5), not tested.

## Commitments (T5) — named, not tested

- **Watch power, not people** — never any person-level use ([`NOTICE`](../NOTICE) §7).
- Open, reproducible, falsifiable by default.
- Publish uncertainty; **cite only what is measured.**

## How to check any of this yourself

- **T1** → `make verify` (reruns the tests and recomputes every number).
- **T2** → follow the citation in the ledger entry or the article's references.
- **T3** → go to the named third-party source.
- **T4 / T5 / T6** → read the stated assumption / commitment / limit — and hold us to it.

---

*The point of this page is not that everything is tested. It is that **nothing here
claims a tier above the one it has earned.***
