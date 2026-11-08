<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Chronicle — how this work was built

*The factual record of the project's construction: what was built, when, with which commit,
and what each step found. Written so the work is reconstructable and auditable — the same
standard the project applies to its claims. The repo stayed **private** until its publication on
2026-11-08 ([`STATUS.md`](../STATUS.md) lists the commitments still open). Commit ids below refer to
the non-public pre-publication history, so they cannot be checked from this repository.*

## Origin

The project began from one question: *how can science contain political violence and the growth
of fascism/authoritarianism, and support long-term peace & prosperity?* A four-lens deep-research
run (epistemic defense · social science of violence · systems & technology · political economy)
swept **29 sources**, extracted **137 claims**, adversarially verified **25**, and confirmed
**21 / refuted 4**, synthesized into [`REPORT.md`](../REPORT.md) with the design of the **Pharos**
initiative ("watch power, not people"). — commit `6d64703`; scaffold `c5b4faf`.

## The theory (verified)

The project's founding thesis — *gather a critical mass of aligned people and change cascades* — was
put to verification. Verdict: the **core is real** (Granovetter thresholds → Watts cascades →
Centola–Macy complex contagion → Centola's 25% tipping experiment → Chenoweth's ~3.5%; applied at
civilizational scale by Otto et al. 2020), with **three corrections** ("energy" = measurable
reinforcement + network clustering, *not* mystical; no universal threshold; cascades are rare and
beatable) and **myths refuted** (100th-monkey, morphic resonance). This became ledger entries
SAA-008–011 and the integrating insight: *the open information commons is the substrate the
cascade runs on.*

## What was built

| Pillar | What | Commits |
|---|---|---|
| **Evidence ledger** | graded, falsifiable entries (ROBUST/CONTESTED/REFUTED/OPEN + falsification triggers) | v0.1 (11 entries) `35e17ac` → v0.2 (15, + anthropology) `5e928c0` |
| **Indicator** | WGI governance change vs published 90% CI — honest uncertainty | v0 (Voice & Accountability) `da6bac6` → all 6 dimensions `c14ab09` |
| **Simulators** | Tier-1 *validated-mechanism* corpus, each reproducing a published result via a unit test | Granovetter+Watts `5d41ac7`; committed-minority `6777714`; reverse-dominance `6e9cb53` |
| **Article** | "Watch Power, Not People" — long-form draft (every number cross-checked 8/8) | `def5653` |
| **Testability map** | `docs/what-is-tested.md` — T1 machine-verified → T6 untestable | `5319368` |

**The indicator's headline finding:** across 6 WGI dimensions × ~204 countries, 2014→2024
(**1,222 country-dimension cells**), **88% of changes are within measurement noise**; of the
measurable changes, declines lead 88:54, and the erosion is **concentrated in Voice &
Accountability** — corroborated independently by V-Dem 2026 and Freedom House 2026.

**The simulators** (4 validated, `make verify` runs **37 tests**): Granovetter's 100-vs-1
knife-edge; Watts's cascade window (global cascades only inside a band of mean degree); the
committed-minority ~10% tipping point (Xie); and **reverse-dominance** — Boehm/Gavrilets via
Lanchester's square law (a coalition levels a dominator iff **k²>r**; the egalitarian revolution
is bistable at that critical mass), which links the anthropology of resisting tyranny to the
project's own critical-mass theory.

## Method lessons (recorded because they matter)

The project's discipline — *adversarially re-check before committing* — repeatedly caught **real
errors**, which is the strongest evidence the method works:
- the Voelkel megastudy venue was **Science, not PNAS** (caught in re-check);
- **Boehm's reverse dominance hierarchy** was downgraded **ROBUST → CONTESTED** (Graeber–Wengrow,
  Erdal–Whiten dispute its universality) — I had over-promoted it;
- several **over-refutations** of classics were softened to be fair (Adorno F-scale: *instrument*
  refuted but *construct* survives in RWA; Milgram: *effect* robust, *interpretation* debated;
  Moral Foundations Theory: CONTESTED not refuted);
- a **garbled Lanchester formula** from a research agent was caught and corrected (`k²>r`, derived
  from first principles) *before* the simulator was built.

## Verifications (the method, demonstrated)

- [`verifications/graham-hancock.md`](verifications/graham-hancock.md) — a fair, steelmanned,
  evidence-graded verification of Hancock's 10 major claims (0 supported / 5 refuted), as an
  external worked example of the discipline.
- [`verifications/plan-for-peace.md`](verifications/plan-for-peace.md) — an adversarial
  verification of the project's *own* plan for peace (graded 2026-06-15): 9 load-bearing claims
  → **1 HOLDS / 8 QUALIFIED / 0 WEAK / 0 BREAKS**, plus 6 red-team angles → **0 FATAL / 2 SERIOUS
  / 4 MANAGEABLE**. Verdict: *directionally sound, honestly overstated in its headline framing.*
  The one claim that HOLDS is the WGI worked example (the part that actually computes); the rest
  qualify because the *headline* oversells what the body and ledger already concede. Yields a
  16-item priority punch-list (Tier 0 gates public launch).

## Acting on the verdict — Tier-0 fixes

The self-verification is only worth anything if its fixes get built. First one shipped
(2026-06-15):

- **Staleness gate** *(Tier-0 ①, the R5 SERIOUS fix)* — `src/ledger_staleness.py` + `make staleness`,
  wired into `verify`. Every ledger entry now carries `last_reviewed` + a grade-based
  `review_interval_days` (CONTESTED/OPEN reviewed soonest); the gate fails the build once any entry
  is past its interval, turning silent maintainer lapse into a *loud* failure instead of stale
  authority wearing the credibility uniform. `make verify` now runs **51 tests** (was 37; +14
  deterministic staleness tests), and the gate is proven to bite (exit 1) on a future date.
- **Grading protocol** *(Tier-0 ②, the R5 bus-factor fix)* — [`GRADING_PROTOCOL.md`](GRADING_PROTOCOL.md)
  moves the grading method out of the author's head and private notes into the repo: the grade
  vocabularies, the rubric (cite-only-what-is-measured; steelman-then-break; separate the layers),
  the reusable adversarial prompts, the re-grade workflow (triggered by new evidence, a falsifier, or
  the staleness gate), and the second-grader reconciliation rule (conservative grade wins ties). Made
  *runnable* by [`../src/ledger_validate.py`](../src/ledger_validate.py) (`make validate`, in `verify`),
  which machine-enforces required fields, a valid grade, a falsifier, a sources block, and
  ledger/`index.json` agreement — so a contributor's malformed entry fails the build. `make verify`
  now runs **66 tests** (was 51; +15), and the validator is proven to bite (exit 1) on a grade that
  disagrees with the index. (Human residual: onboarding an actual second grader.)
- **Voice triangulation** *(Tier-0 ④, the divergence-not-score fix + the long-pending V-Dem
  corroboration)* — [`indicators/voice-divergence.md`](indicators/voice-divergence.md) +
  [`../src/indicators/voice_divergence.py`](../src/indicators/voice_divergence.py) (`make divergence`)
  triangulates WGI Voice & Accountability × V-Dem freedom-of-expression × Freedom House civil-liberties
  over 2014→2024. It reduces each instrument to a *signed, significant decade change* and combines only
  the signs — **never a blended score** — so a gamed single input surfaces as CONFLICT (dissenter named)
  rather than a false green. Result: **45 countries CONCUR-DECLINE** (26 at full 3/3, incl. Hungary,
  Russia, Belarus, Turkey, Venezuela, Myanmar, Hong Kong, Nicaragua), **5 CONFLICT**, the rest
  weak-or-flat — independently corroborating "the erosion is concentrated in voice" at ~5.6:1
  decline:improve across instruments. Data: V-Dem + Freedom House via Our World in Data (both CC-BY,
  endpoints verified live). `make verify` now runs **82 tests** (was 66; +16). With this, all four
  Tier-0 launch gates are built.
- **Threat model** *(Tier-0 ③, the C7/R2 fix)* — [`../THREAT_MODEL.md`](../THREAT_MODEL.md) turns the
  "watch power, not people" covenant from `NOTICE` §7 good-faith request into an **enforced
  publish/withhold gate**, grounded in named frameworks: the Shevlane-Dafoe offense-defense test
  (which formally *derives* watch-power, because a state already owns finer data on its own people),
  DII / LINDDUN / Microsoft harms modeling (aggregate ≠ safe), the predictive-policing runaway-feedback
  precedent (Ensign 2018; Lum & Isaac 2016 — place-level output *is* the weapon), a spatial-resolution
  floor with honest caveats (the "<5" suppression rule has no scientific basis; differential privacy
  disproportionately harms small populations), HDX sensitivity→access tiers, forecasts tiered
  most-sensitive by default, a per-PR release checklist, and a falsification trigger for the safety
  claim itself.

## Reliability & efficiency hardening (2026-06-18)

With the science in place, a pass to make the *foundation* as disciplined as the claims —
informed by an audit of this repo:

- **Offline determinism + resilient fetch** (`2f7776b`) — the `make verify` gate used to depend on
  three live APIs with weak/again-buggy retry (`voice_divergence._fetch_csv` retried *instantly*).
  Now `src/indicators/fetch_utils.py` is one resilient fetcher (exponential backoff + jitter), the
  raw inputs are pinned to `data/snapshots/`, and `make verify-offline` recomputes the indicators
  with **no network**, byte-for-byte identical to the committed derived data. Reproducible anywhere.
- **Claim-integrity audits + dashboard** (`52943cc`) — calibrated for social-science prose: an **overstatement audit** (flags unconditional-certainty
  language; 0 in the current hedged corpus), a **doc-count consistency checker** (caught STATUS
  claiming 82 tests when the repo had 94), and `make dashboard` — one GREEN/RED report.
- **Free local CI + Docker** — the live gate is **free local git hooks** (`make hooks`:
  pre-commit → `make dashboard`, pre-push → `make verify-offline`), because the project uses free
  technology only. The Actions workflow (`verify.yml`) was kept manual (`workflow_dispatch`) until
  publication. Plus a stdlib-only `Dockerfile`, and confirmation that flat versioned Markdown plus
  the audit gates is the right ledger backend.

## The forecasting pillar + the last plan-for-peace fixes (2026-06-18)

- **pharos-forecast v0** *(Tier-1 C5/R6 — the project's second pillar, in honest form)* —
  [`forecast/pharos-forecast-v0.md`](forecast/pharos-forecast-v0.md) +
  [`../src/forecast/pharos_forecast.py`](../src/forecast/pharos_forecast.py). Not a hero call: a
  transparent, pre-registered backtest over **2,600** probabilistic forecasts of democratic
  backsliding (V-Dem freedom of expression, 1990–2024), scored by **CRPS + Brier against a
  no-change baseline**. The pre-registered success bar is `skill > 0` vs that baseline — and the
  honest, expected result is that **nothing clears it** (trend extrapolation actively hurts,
  skill −0.56). That is the deliverable: the bar is public, v0 doesn't yet beat it, and a future
  model earns its place only by beating it on the same open harness. Reflexivity is handled by
  staying retrodictive + documenting the live protocol; everything is country-level (watch power).
- **Tier-2 honesty demotions** — the eight QUALIFIED headlines demoted to what the evidence
  carries (C1–C4, C7, C8 in the ledger + article; see `verifications/plan-for-peace.md`). The
  overstatement audit caught a fabricated citation mid-edit (a mis-remembered "Wan/Lazer 2025")
  and it was corrected to the real arXiv:2411.07907 — the discipline working on its own author.
- **C9 robustness** *(Tier-3)* — the Voice & Accountability decline asymmetry survives the
  stricter 95% bar (28 : 6 = 4.67 : 1 vs 33 : 6 at 90%) **and** an alternative in-snapshot window
  (2015 → 2024: 30 : 6 at 90%, 22 : 4 at 95%) — a tight **~4.7–5.5 : 1** band however you slice it;
  the per-dimension 95% counts and both windows now ship in the derived summary (`va_robustness`).
- **Two more validated simulators** *(the simulator backlog, closed)* — `sim_complex_contagion`
  (Centola–Macy: a complex contagion sweeps a clustered ring lattice but **stalls at 1%** once
  rewired, while a simple contagion only speeds up — a faithful complement to SAA-010's contested
  clustering edge) and `sim_civil_violence` (Epstein: the **legitimacy lever + tipping point** —
  quiescent above ~0.9, igniting below; the punctuated *bursts* are honestly **not** asserted, as
  they need a larger-scale run). The corpus is now 6 Tier-1 mechanisms; `make verify` = 118 tests.

## Verification follow-through (post-0.4.0 hardening)

A read-only, five-dimension adversarial verification of the whole repo returned a clean verdict —
**architecturally sound, ZERO correctness bugs, clean licensing/security**; the remaining gaps were
governance/completeness, not code. The implementable subset was then landed as honesty- and
enforcement-strengthening hardening (no new claims, no scope growth):

- **The threat model, enforced on the data.** [`THREAT_MODEL.md`](../THREAT_MODEL.md)'s "watch power,
  not people" spatial floor was documented but nothing machine-checked it. New
  [`src/audit_threat_model.py`](../src/audit_threat_model.py) scans every published `data/derived/*`
  and `data/snapshots/*` and **fails the build** if any column or key drops below country/institution
  level. A three-layer matcher (atomic tokens · `adm\d+`/`admin\d+`/`nuts` regexes · qualifier→suffix
  adjacency) catches real-world spellings — `first_name`, `national_id`, `state_code`, `adm3` — while
  `year_latest` / `country_name` / `state_capacity` never false-positive, and it scans long-format
  label *values* too. Wired into `make verify`, `verify-offline`, and the dashboard; a data-driven
  test pins both recall and precision so a too-narrow denylist fails immediately.
- **The "calibrated miss" explainer shipped.** The forecast doc had twice promised the R6 reflexivity
  artifact; [`docs/forecast/CALIBRATED_MISS_EXPLAINER.md`](forecast/CALIBRATED_MISS_EXPLAINER.md) now
  exists and is linked from both sites — a 30% that resolves false is the system working, not failing.
- **C9 finished** (alt-window above), **SAA-007 honesty caveat** (the no-change-baseline result named
  in its own Evidence section), and **defensive `json.load`** in the audits (a friendly error, never a
  raw traceback). A **second** adversarial review (whole-repo, 7 dimensions: code · sims · tests ·
  ledger · citations · consistency · licensing) then confirmed 5 more small defects — all test-scope
  or not-overclaim honesty, no correctness bugs: the `egalitarian_revolution()` sim relabelled as the
  deterministic threshold-classifier it actually is (not Gavrilets' emergent basin); the overstatement
  gate narrowed to scan claim-bearing bullets; a guard so a reworded doc can't silently un-pin a count;
  an SAA-033 citation year; and a documented reason `title` is excluded from the index cross-check.
  `make verify` = **130 tests**; dashboard 6/6 GREEN. A **third** review then web-verified *every*
  source across all 35 entries + `REPORT.md` against PubMed/CrossRef/arXiv/DOI: **no fabricated or
  retracted sources**, and 6 small attribution slips corrected — a stitched-on wrong title (SAA-030
  Kalmoe & Mason, plus a double-counted critique reconciled), a wrong page range (SAA-017), a coined
  term (`counterdominance`, SAA-012), and three paraphrased/slug-derived reference titles in REPORT.
  A **fourth** review then differential-verified the quantitative pillar — every load-bearing formula
  (CRPS, Brier, the WGI 90%-CI z-test, the VA window counts, the divergence sign-combination, the
  climatology baseline) independently reimplemented and matched against the committed outputs: **5 of
  6 reproduced bit-exactly**, and one real bug fixed — an alias-mutation in `pharos_forecast.backtest()`
  that computed skill against the rounded (not full-precision) no-change baseline (`trend` crps_skill
  −0.5601 → −0.5602; no verdict changes). A **fifth** review independently re-graded all 35 entries
  against the rubric (second grader + adjudicator): **0 clear rubric violations** — the grading holds
  — and the one surfaced house-style question was resolved by *documenting* the existing convention
  (`GRADING_PROTOCOL.md` rule 4, "compose to the headline"), not by re-grading anything. Repo stays
  **private**.

## Build-out: the read surface, the CLI, and ledger growth (post-review)

With the review arc clean, the same session built on the verified base (commits through `ff3bdc5`;
every step gate-green, repo private throughout):

- **The ledger's read phase** — `src/ledger_digest.py` generates `ledger/INDEX.md`: a by-grade index,
  the **falsification watch** (every entry's trigger in one place), and a **coverage-by-domain** map.
  Generated from the frontmatter, deterministic, and drift-gated by a **seventh audit** (`ledger index`)
  — the browseable view can never silently diverge from the entries.
- **Every public number machine-checked** — the consistency gate was extended to recompute the site's
  *and* the indicator/forecast docs' headline figures (88% within noise, the 88:54 split, 45
  concur-decline, 2,600 forecasts) straight from `data/derived`, with a darkening guard so a reworded
  doc can't silently un-pin a figure. The site's own "every public number is machine-checked" claim is
  now true for the computed ones, not just the entry count.
- **A seventh validated simulator** — `sim_opinion_dynamics` (Deffuant–Weisbuch bounded confidence),
  the polarization micro-foundation: it reproduces the **ε = 1/2 consensus threshold** (Fortunato 2004)
  and monotone fragmentation, honestly *not* asserting the stochastic ~1/(2ε) cluster count. A
  follow-on audit then checked the **whole 7-sim corpus** for the tautology trap a prior round found in
  reverse-dominance — only opinion-dynamics had it (its consensus test passed on no-op random data);
  fixed to assert genuine convergence.
- **`pharos`, the software** — `src/pharos.py` + a `./pharos` wrapper: ten stdlib-only subcommands
  (`ledger`/`show`/`watch`/`coverage`/`stale`/`stats`/`indicators`/`divergence`/`forecast`/`verify`)
  that read only the committed source of truth, so every number printed is the verified one.
- **Ledger 35 → 38**, filling the thinnest lenses, each verify-first with every citation web-verified
  then **independently reviewed**: **SAA-036** (algorithmic "rabbit-hole" radicalization, CONTESTED,
  systems-and-tech), **SAA-037** (executive aggrandizement is the modal backsliding pathway, ROBUST,
  democratic-backsliding), **SAA-038** (lateral reading is the expert source-evaluation strategy,
  ROBUST, epistemic-defense). The review of the three caught one "cite only what is measured" slip in
  SAA-038 ("versus controls" on studies with no control group), fixed.
- **`CONTRIBUTING.md`** — the contributor on-ramp and the second-grader substrate: the two enforced
  laws, the verify-first discipline, and the full add-an-entry *count cascade* (the non-obvious chain
  a contributor would otherwise miss). State at session close: **38 entries** (20 ROBUST / 16 CONTESTED
  / 1 REFUTED / 1 OPEN), 7 simulators, 7 audits, **159 tests**; `make dashboard` 7/7 GREEN;
  `verify-offline` deterministic; **PRIVATE, Pages OFF, publication gate closed.**

## The impact arc (2026-07-10)

Asked "how can this cause more impact," the project answered with its own method instead of
opinion: a 47-agent research + adversarial-verification run (six angles: evidence-to-action
science, peer projects, distribution, credibility, ethics/backfire, funding) verified 18
load-bearing claims (9 SUPPORTED / 9 MIXED / 0 REFUTED — each attacked by two independent
lenses before being relied on). The adjudicated synthesis is
[`IMPACT.md`](IMPACT.md): a falsifiable theory of change (the verified core finding —
passive availability reliably fails; salience is the under-invested axis), eight ranked
levers each tagged buildable-now vs founder-gated, uptake metrics defined *before* going
public, and six red lines.

Every buildable-now lever then shipped the same day, each drift-gated and bite-tested:
**L3** [`TRUST_SIGNALS.md`](TRUST_SIGNALS.md) (every norm → mechanism → check-it command;
self-correction record first, per the verified caveat that pre-registration alone doesn't
move trust) + the site's "How to check us" fold; **L4** [`BRIEF.md`](BRIEF.md), the
plain-language read *generated* from committed data (noise floor leads; the negative
forecast survives translation); **L5** [`DATA_CONTRACT.md`](DATA_CONTRACT.md) + the
vendorable one-file stdlib client (vendorability proven in tests by importing a copied
file); **L6** [`BIAS_AUDIT_PREREGISTRATION.md`](BIAS_AUDIT_PREREGISTRATION.md) — the
Bright Line Watch playbook turned on ourselves, with a deterministic blind-pack generator
(grade tokens masked, sha256 pseudo-shuffle) so the protocol is executable; the run itself
is founder-gated and doubles as second-grader onboarding. Closing pieces: the **L2 [now]
prototype** [`WATCH_REPORT.md`](WATCH_REPORT.md) (the named-flagship shape, carrying the
Watch List as its single object, name/cadence left to the founder), the pre-registration's
**H3 symmetric-reporting rule as a machine gate** in the counts audit, and the **mosaic /
small-cell rule** added to the THREAT_MODEL release checklist (IMPACT red line 3).

Tests 185 → **218** across the arc; dashboard 7/7 GREEN throughout; the repo stayed
PRIVATE, Pages OFF, gate closed.

The arc closed the way this project closes everything: by turning the review machinery on
the arc itself. A seventh adversarial round over the new tooling confirmed ten defects —
including the most instructive finds to date: **the summary layers (the generated brief and
watch report, and the public site) had drifted into presenting the ≥2-significant
concurrence count as an all-three-instruments claim**, while the canonical indicator doc
stayed correct. All fixed, both significance bars now pinned, the blind pack's masking made
genuinely blind, the promised exact CI implemented, and the spatial-floor gate extended to
encoded geolocation and national-ID columns. The lesson entered the record: every
summarization away from the canonical document is an overclaim opportunity — which is why
the summaries are generated, gated, and now double-pinned. Tests ended at **240**. What remains on the impact ranking is founder-only: the
public name, the flagship cadence, the funding-independence policy, running the bias
audit, the human second grader, and the gate itself.

## After the impact arc (2026-07-24 → 2026-11-08)

- **Ledger 39 → 41** — SAA-040 (the conflict-forecasting track record) and SAA-041 (the 3.5% rule
  as a tendency, not a law), both CONTESTED. See [`CHANGELOG.md`](../CHANGELOG.md).
- **The local Pharos observatory (2026-09-23)** — `./pharos serve`: a loopback-only browser app
  over the existing research, with real offline verification runs and receipts (+29 tests).
- **The first forward score (2026-10-31)** — the frozen 1-year forecasts scored against the 2025
  V-Dem release; blind, but not prospective (see the CHANGELOG for the timing caveat).
- **Publication (2026-11-08, 0.7.0)** — published as a verified snapshot with collective credit;
  the commitments still open are listed in [`STATUS.md`](../STATUS.md).

## Honest scope

This is a *partial* synthesis by design: much canonical literature (Chenoweth/Walter/Stanton/the
political-economy canon) and several planned increments are not yet built — see
[`../STATUS.md`](../STATUS.md). Nothing here claims more than it has earned.
