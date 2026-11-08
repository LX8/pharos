<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# STATUS — current state & honest backlog

*So nothing is silently dropped. Updated 2026-11-08 (v0.7.0, the first public release).*

## 🔓 Publication gate — opened 2026-11-08, with commitments still open

The gate had two conditions: (a) planning *and* calculating done, computed, uncertainty-quantified
and verified; (b) an explicit go. The go was given and the repository was published on 2026-11-08
as a verified snapshot (see [`SNAPSHOT.md`](SNAPSHOT.md)); the software gates pass
(`make verify-offline`, 293 tests; `make dashboard`, 7/7).

> **Deviation from the pre-registered plan (recorded 2026-11-08).** The repository was published
> before three commitments this project set for publication were met. All three remain open:
> - the pre-registered **H1 bias audit by two human coders** was to run before the gate opened
>   ([`docs/BIAS_AUDIT_PREREGISTRATION.md`](docs/BIAS_AUDIT_PREREGISTRATION.md) §6 item 4); only
>   the mechanical H2/H3 parts and a non-authoritative H1 dry run exist
>   ([`docs/verifications/bias-audit-2026-07-24.md`](docs/verifications/bias-audit-2026-07-24.md));
> - no **independent second grader** has graded entries yet
>   ([`docs/GRADING_PROTOCOL.md`](docs/GRADING_PROTOCOL.md) §6);
> - the **release checklist** in [`THREAT_MODEL.md`](THREAT_MODEL.md) §7 — including the forecast
>   inversion red-team (§4.5) for the published country-level forecasts — has not been recorded.

The ethical-use covenant in [`NOTICE`](NOTICE) §7 applies.

## ✅ Done (verified, `make verify-offline` green — 293 tests)

- **Pharos local observatory (2026-09-23):** `./pharos serve` opens the study-grounded
  browser app: searchable evidence, historical indicator disagreements, forecast and
  calibration results, seven runnable mechanisms, and actual offline verification receipts.
  See [local app guide](docs/LOCAL_OBSERVATORY.md). Independent human review remains open
  (see the publication gate above).

*How to verify it all yourself (offline, deterministic, free): **[`docs/VERIFYING.md`](docs/VERIFYING.md)** —
the ladder, the seven audits, the offline determinism guarantee, and the adversarial-review regime.*

- **Ledger v0.5** — 41 graded entries (`ledger/`), 20 ROBUST / 19 CONTESTED / 1 REFUTED / 1 OPEN.
  Built via four **verify-first batches** (every citation web-confirmed before writing): **psychology**
  (SAA-016–021: RWA/SDO, Milgram, Moral Foundations, minimal-group, Asch, dehumanization), **sociology**
  (SAA-022–026: dynamics-of-contention, nonviolent-success ~2:1, social capital, repression-backfire,
  affective polarization), **recent-empirical** (SAA-027–030: the Voelkel depolarization megastudy
  [animosity reducible, anti-democratic attitudes sticky], the 2024–26 V-Dem/Freedom House democratic
  recession, anocracy+factionalism civil-war risk, and the *overestimation* of support for political
  violence), and **political-economy** (SAA-031–035, filling the REPORT's 4th lens: financial-crises→far-right
  [ROBUST], income–democracy [correlation robust / causation contested], inequality & erosion, the
  resource curse [with the Haber–Menaldo null], China-shock polarization). The verification *excluded a
  2026-retracted paper* and *corrected four mis-cited references*; layered grades throughout (measured
  trend / correlation ROBUST, causal reading CONTESTED).
- **Indicator** — 6 WGI governance dimensions with honest uncertainty (`docs/indicators/`,
  `src/indicators/wgi_governance.py`).
- **Simulators** — 7 Tier-1 validated mechanisms (`src/sims/`): threshold-cascade, network-cascade,
  committed-minority, reverse-dominance, **complex-contagion** (Centola–Macy: sweeps a clustered net,
  stalls when rewired), **civil-violence** (Epstein: the legitimacy lever + tipping point — honestly
  *not* the burst time-series, which needs a larger run), **opinion-dynamics** (Deffuant–Weisbuch:
  the ε = 1/2 consensus threshold + monotone fragmentation — the ~1/(2ε) count not asserted exactly).
- **Article draft** — `docs/article/watch-power-not-people.md` (working draft, public with the repository since 2026-11-08).
- **Testability map** — `docs/what-is-tested.md`.
- **Verifications** — Graham Hancock (done); **plan-for-peace (done — graded 2026-06-15: 1 HOLDS /
  8 QUALIFIED / 0 WEAK / 0 BREAKS · 0 FATAL / 2 SERIOUS / 4 MANAGEABLE; verdict: directionally sound,
  headline oversold)** → [`docs/verifications/plan-for-peace.md`](docs/verifications/plan-for-peace.md).
- **Record** — `docs/CHRONICLE.md`, this file.
- **Website** — `site/` (static landing page, dependency-free) — **built, NOT deployed** (GitHub
  Pages OFF; deploying it is a separate decision from publishing the repository). Working name "Aty Guasu" (to be confirmed).
  Refreshed to **v0.3.0**: both pillars (evidence ledger + forecast), the forecast-honesty section
  ("we don't beat the baseline yet — and we say so"), the triangulation, the enforced threat model,
  and the self-auditing/reproducible framing.
- **Staleness gate** *(plan-for-peace Tier-0 ①)* — `src/ledger_staleness.py` + `make staleness`
  (wired into `verify`): every ledger entry carries `last_reviewed` + grade-based
  `review_interval_days`; the gate fails once any entry is past its interval, so maintainer lapse
  becomes **loud** instead of rotting into stale authority (the R5 SERIOUS fix). 14 deterministic tests.
- **Threat model** *(plan-for-peace Tier-0 ③)* — [`THREAT_MODEL.md`](THREAT_MODEL.md): turns the
  "watch power, not people" covenant from good-faith request into an **enforced publish/withhold
  gate** (the C7 / R2 fix). Marginal-value test (Shevlane-Dafoe) that *formally derives* watch-power;
  DII + LINDDUN + Microsoft-harms lenses (aggregate ≠ safe); spatial-resolution floor with the honest
  "<5 has no scientific basis" + DP-harms-small-populations caveats; HDX sensitivity→access tiers;
  forecasts highest-sensitivity by default (cascade-timing layer held/deferred); a per-PR release
  checklist; and a falsification trigger for the safety claim itself.
- **Grading protocol** *(plan-for-peace Tier-0 ②)* — [`docs/GRADING_PROTOCOL.md`](docs/GRADING_PROTOCOL.md)
  + [`src/ledger_validate.py`](src/ledger_validate.py) (`make validate`, in `verify`): the grade
  vocabularies, the rubric, the reusable adversarial prompts, the re-grade workflow, and the
  second-grader reconciliation rule (conservative grade wins ties) — the method out of one head and
  into the repo. The validator machine-enforces it (required fields, valid grade, falsifier, sources,
  index agreement) so a contributor's entry that violates the protocol fails the build. 15 tests.
  *(Bus-factor partly broken: the substrate is open + enforced; the human step — actually onboarding
  one second grader — remains open.)*
- **Voice triangulation** *(plan-for-peace Tier-0 ④ + the long-pending V-Dem corroboration)* —
  [`docs/indicators/voice-divergence.md`](docs/indicators/voice-divergence.md) +
  [`src/indicators/voice_divergence.py`](src/indicators/voice_divergence.py) (`make divergence`, in
  `verify`): triangulates WGI Voice & Accountability × V-Dem freedom-of-expression × Freedom House
  civil-liberties and **publishes divergence, not a single score** — **45 CONCUR-DECLINE** (26 at full
  3/3: HUN RUS BLR TUR VEN MMR HKG NIC … ), **5 CONFLICT** (named dissenter), the rest MIXED-WEAK /
  ALL-FLAT. Independently corroborates "the erosion is concentrated in voice" (~5.6:1 decline:improve
  across instruments) while making a gamed single input surface as CONFLICT, not a false green.
  16 deterministic tests. **→ All four Tier-0 launch gates (①②③④) are now built.**
- **Reliability & efficiency hardening** — **free local CI** via git hooks (`make hooks`: pre-commit →
  `make dashboard`, pre-push → `make verify-offline`) — no cloud, no billing (the workflow
  [`.github/workflows/verify.yml`](.github/workflows/verify.yml) runs the same gate on pushes since
  publication); **offline determinism**
  — pinned input snapshots (`data/snapshots/`) + `make verify-offline`
  recompute the indicators with **no network**, byte-for-byte; a **shared resilient fetcher**
  ([`src/indicators/fetch_utils.py`](src/indicators/fetch_utils.py), backoff+jitter, dedup); **claim-integrity
  audits** ([`src/audit_overstatement.py`](src/audit_overstatement.py), [`src/audit_counts.py`](src/audit_counts.py))
  + a **`make dashboard`** GREEN/RED report; and a **`Dockerfile`** for run-anywhere reproducibility.
- **Forecasting pillar — pharos-forecast v0** *(plan-for-peace Tier-1 C5/R6; the project's second pillar)* —
  [`docs/forecast/pharos-forecast-v0.md`](docs/forecast/pharos-forecast-v0.md) +
  [`src/forecast/pharos_forecast.py`](src/forecast/pharos_forecast.py) (`make forecast`, in `verify`): a
  **calibration layer, not a hero call** — 2,600 pre-registered probabilistic backsliding forecasts (V-Dem
  freedom-of-expression, 1990–2024), CRPS + Brier scored against a **no-change baseline**. Honest result:
  **nothing beats no-change** (the pre-registered, expected finding; trend even hurts, skill −0.56) — the bar
  to clear is public. Portfolio-not-hero-call; reflexivity protocol documented; watch-power-only. 11 tests.
- **C9 robustness** *(plan-for-peace Tier-3)* — the WGI Voice & Accountability decline asymmetry holds at the
  stricter two-sided 95% bar: **28 : 6 = 4.67 : 1** (vs 33 : 6 = 5.5 : 1 at 90%), n = 203; `counts_95pct_bar`
  ships in the derived summary; an alternative decade window is noted as a future step.

## ⏳ Pending (researched / scoped, not yet built)

| Item | State |
|---|---|
| ~~**Ledger batches 2–4**~~ | ✅ **DONE (2026-06-18)** — all three written via verify-first workflows (SAA-016–030, 15 new entries); ledger 15→30. See the Done section. |
| ~~**V-Dem triangulation**~~ | ✅ **DONE** — delivered (and extended to Freedom House) as the Tier-0 ④ voice-divergence indicator; see the Done section. Corroborates the "voice decline" finding across three instruments (45 CONCUR-DECLINE vs 8 CONCUR-IMPROVE). |
| ~~**`sim_complex_contagion`** + **`sim_civil_violence`** + **`sim_opinion_dynamics`**~~ | ✅ **DONE** — all built and validated against their published results (Centola–Macy stall; Epstein legitimacy tipping point; Deffuant ε=1/2 consensus threshold). The Tier-1 corpus is now **7** mechanisms. See the Done section + [`docs/sims/README.md`](docs/sims/README.md). |
| **plan-for-peace fixes** — 16-item ordered punch-list now written (in [`docs/verifications/plan-for-peace.md`](docs/verifications/plan-for-peace.md)); none applied yet | **Tier 0 — gates public launch** (the two SERIOUS angles): ① ✅ **DONE** — staleness gate in `make verify` (`src/ledger_staleness.py`; `last_reviewed`+`review_interval_days` on every entry; gate fails when past interval); ② ✅ **substrate DONE** ([`docs/GRADING_PROTOCOL.md`](docs/GRADING_PROTOCOL.md) + `make validate`); human step (onboard 1 second grader) still pending; ③ ✅ **DONE** — [`THREAT_MODEL.md`](THREAT_MODEL.md) (enforced publish/withhold gate: marginal-value test, DII/spatial floor, HDX tiers, forecasts-most-sensitive, safety falsification trigger); ④ ✅ **DONE** — publish *divergence-not-score* ([`docs/indicators/voice-divergence.md`](docs/indicators/voice-divergence.md) + `make divergence`; WGI×V-Dem×FH, CONFLICT surfaced never a blended score). **→ all 4 Tier-0 code gates built; only the human 2nd-grader onboarding (②) remains.** **Tier 1:** ✅ **C5/R6 DONE (2026-06-18)** — pharos-forecast v0 is a calibration layer (not a rival forecaster), beat-a-no-change-baseline by CRPS is the pre-registered success bar, portfolio-not-hero-call, reflexivity protocol documented (see [`docs/forecast/pharos-forecast-v0.md`](docs/forecast/pharos-forecast-v0.md)). *(R1/R4 forecasting-posture refinements remain for a v1.)* **Tier 2:** ✅ **DONE (2026-06-18)** — headline demotions applied to the ledger (SAA-001/008/010) + article (C1–C4, C7, C8; C6 already hedged); overstatement audit 0 SERIOUS. **Tier 3:** ✅ **C9 FULLY DONE** — the 95% robustness bar (28:6 = 4.67:1) *and* the alternative window (2015→2024) both ship in `va_robustness`; the asymmetry holds in a tight ~4.7–5.5:1 band however sliced. |
| **Article refresh** | fold in the V-Dem triangulation + new ledger entries |
| **Impact strategy — adjudication** | [`docs/IMPACT.md`](docs/IMPACT.md) written (2026-07-10): 18 adversarially-verified claims → 8 ranked levers, uptake metrics pre-defined, red lines. **L3 trust-signals surface ✅ DONE (2026-07-10)** — [`docs/TRUST_SIGNALS.md`](docs/TRUST_SIGNALS.md) (norm → mechanism → check-it command, self-correction record first) + site "How to check us" fold; its numbers gate-pinned. **L4 salience layer ✅ DONE (2026-07-10)** — [`docs/BRIEF.md`](docs/BRIEF.md), the plain-language read *generated* from the committed derived data (`make brief`, `src/brief.py`): noise floor leads, the negative forecast survives translation, conflicts surfaced not blended, per-audience "who uses this for which decision" section; freshness-gated by the test suite (a stale brief fails the dashboard). **L5 reuse on-ramp ✅ DONE (2026-07-10)** — [`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md) (every column + categorical vocabulary documented, additive-only guarantee, CC0, verify-it-yourself commands) + [`src/pharos_client.py`](src/pharos_client.py), the vendorable one-file stdlib reader (typed tables, read-only; vendorability + stdlib-only machine-tested). **L6 bias-audit ✅ FULLY EXECUTABLE (2026-07-10)** — [`docs/BIAS_AUDIT_PREREGISTRATION.md`](docs/BIAS_AUDIT_PREREGISTRATION.md) (H1 blind valence–grade independence with fixed skew criteria, H2 partisan-object count, H3 symmetric-reporting rule, H4 trigger-firability; honest small-N/scope limits; publish-including-nulls commitment; **§7 operator runbook — the run in an afternoon**) + `src/bias_audit.py`: `--pack` (deterministic blind pack, grade tokens masked, sha256 pseudo-shuffle, sealed key; `make bias-pack`) **and `--score`** (the pre-registered H1 statistics computed for you — 2×2 table, ΔP, **exact two-sided Fisher test in pure stdlib**, frozen fire-verdict). **Only the two human coders are missing** — which is exactly the founder-gated, second-grader-onboarding step the audit requires (sign-off §8). **The recruiting friction is now zero too:** [`docs/SECOND_GRADER_PACKET.md`](docs/SECOND_GRADER_PACKET.md) is the one-send onboarding packet — copy-paste invitation, self-contained blind-coding brief (synthetic examples so it can't pre-expose a coder), deliverable format, and the coder→second-grader path. **L2 [now]-half ✅ DONE (2026-07-10)** — [`docs/WATCH_REPORT.md`](docs/WATCH_REPORT.md) flagship-edition prototype (`make watch-report`): the **Watch List** as the single carryable object, symmetric movements by construction, freshness-gated; name + cadence stay founder decisions. Plus: **H3 symmetric-reporting machine gate** in the counts audit and the **mosaic/small-cell rule** in THREAT_MODEL §7. → **Every buildable piece of the impact strategy is complete.** The gate/name/cadence/funding questions (IMPACT.md §6) are founder-only. |
| ~~**Software build**~~ | ✅ **DONE (2026-06-28)** — the maintainer picked the **CLI**; shipped as **`./pharos`** (`src/pharos.py`), one stdlib-only command with ten subcommands (`ledger`/`show`/`watch`/`coverage`/`stale`/`stats`/`indicators`/`divergence`/`forecast`/`verify`) reading only the committed source of truth. See the Done section + the README "Run it in 30 seconds". |

## Conventions

- Multi-licensed, REUSE-compliant; `make verify` is the gate (tests + indicator recompute).
- "Cite only what is measured"; "leave nothing mislabeled"; "watch power, not people."
