<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Pharos-forecast v0 — a calibration layer, not a hero call

*Computed from open data; reproduce with `make forecast` (or `make verify`). Country/
institution level only — **watch power, not people** ([`NOTICE`](../../NOTICE) §7,
[`THREAT_MODEL.md`](../../THREAT_MODEL.md)).*

This is the project's **second pillar** in honest, falsifiable v0 form, and it implements
the plan-for-peace fixes the self-verification graded SERIOUS/QUALIFIED — **C5** ("be a
calibration/evidence layer, not a rival forecaster") and **R6** (a public point-call is
reflexive and discrediting). It deliberately does **not** predict that any particular
country will fall. It is a transparent, pre-registered **backtest** that asks one honest
question over a whole portfolio:

> **Does any simple model of democratic backsliding beat a no-change baseline — scored by
> proper scoring rules (CRPS + Brier) — and is it calibrated?**

## Why this shape (the R6 / C5 fix)

A legible "they said X would fall and it didn't" clip can burn the whole trust asset, and
in the VIEWS prediction competitions beating a no-change baseline is metric- and task-dependent
(ledger entry SAA-040). So
the only thing this ships is a **portfolio score against that baseline**, with the success
bar pre-committed:

> **Success bar (pre-registered): skill > 0 vs. the no-change baseline, with calibration.**

If a model doesn't clear it, the harness says so. That honesty is the product — it converts
the field's brutal base rate from an exposé into a documented, expected datum.

## The pre-registered design (fixed before scoring; not tuned to results)

- **Data:** V-Dem Freedom of Expression index (`v2x_freexp_altinf`, 0–1), annual, via Our
  World in Data; 174 countries, 1990–2024.
- **Task:** at each origin year *T* ∈ [2000, 2014], for every country, forecast the change
  over the next **10 years**. The binary event is a **meaningful decline**: Δ ≤ −0.05.
- **Models** (all parameter-fixed): `no_change` (baseline), `trend` (10-yr extrapolation),
  `damped_trend` (×0.5), `reversion` (regression to the panel mean). Baselines also include
  `climatology` (global mean drift) and `climatology_per_country` (each country's own mean drift).
- **Forecasts are probabilistic:** each model emits a Gaussian predictive distribution whose
  spread σ is fitted, per origin year *T*, **only from history observable at T** (see
  *Leak-free* below) — so only the mean differs, an honest like-for-like test.
- **Scoring:** **CRPS** (Gneiting & Raftery 2007, closed form) on the continuous change, and
  **Brier** (1950) on the decline event; reported as **skill vs. the no-change baseline**.

## The result (the honest, falsifiable v0 finding)

Across **2,600 pre-registered forecasts** (σ = 0.171; decline base-rate = **0.27**):

| Model | CRPS | CRPS skill | Brier | Brier skill |
|---|---|---|---|---|
| **no_change** (baseline) | 0.0772 | — | 0.2110 | — |
| reversion | 0.0780 | −0.01 | 0.2269 | −0.07 |
| damped_trend | 0.0904 | −0.17 | 0.2185 | −0.04 |
| **climatology** (baseline) | 0.0896 | −0.16 | 0.1929 | +0.09 |
| climatology_per_country (baseline) | 0.1220 | −0.58 | 0.2362 | −0.12 |
| trend | 0.1166 | −0.51 | 0.2336 | −0.11 |

> **Verdict: nothing beats the no-change baseline.** Every candidate model, and every
> climatology baseline, loses to the dumbest possible forecast ("assume nothing changes"):
> regression-to-mean is flat (−0.01), global climatology loses (−0.16), per-country drift
> loses badly (−0.58 — a country's own past change is noise, not signal), and trend
> extrapolation actively *hurts* (−0.51). This is exactly the pre-registered, expected
> outcome — and the point: **the bar is public, and v0 does not clear it.** A future model
> earns its place only by beating *all three* no-skill baselines on this same open harness.

The decline base-rate of 0.27 is itself a useful, honest number: roughly **a quarter of
country-decade windows saw a meaningful fall in freedom of expression** — backsliding is
common, but *which* country and *when* is not predictable here beyond assuming none.

### Leak-free backtest (a hardening that strengthened the finding)

The spread σ and the climatology means are fitted, per origin year *T*, from **only the
history a forecaster at *T* could see** (outcomes realized by year ≤ *T*) — never from the
future being scored. An earlier in-sample version let climatology edge out no-change
(CRPS skill +0.01); that small win was a **leakage artifact** and disappears once the
harness is leak-free (climatology then loses, −0.16). The pre-registered "nothing beats
baseline" verdict is therefore *robust to* — and strengthened by — removing the leakage,
and the harness can now be trusted to credit a genuinely skillful v1 rather than a fit on
the answers.

## The honesty guarantees

- **Portfolio, never a hero call.** The legible object is a calibration curve over 2,600
  forecasts, not "did the wolf come for country X." (Per-bin reliability is in the JSON.)
- **Beat-the-baseline is the only success claim** — pre-committed, so a poor score is a
  documented datum, not an exposé.
- **Reflexivity doesn't bite a backtest** (it is retrodictive; no live forecast was acted
  on). The protocol for any *live* forecast is the R6 fix: pre-register the Goodhart/Lucas
  pathway (a watched indicator improving after a warning is logged as a candidate
  warning-response event, ambiguity published — never claimed as a clean hit or miss), and
  ship the [**"what a calibrated miss looks like" explainer**](CALIBRATED_MISS_EXPLAINER.md)
  *with* the forecast, not after.
- **Watch power, not people.** Country/institution-level only; the cascade-timing /
  pre-emption layer is held per [`THREAT_MODEL.md`](../../THREAT_MODEL.md) §4.5.

## Toward v1 — the protocol for a *live* forecast (R1 / R4)

v0 is a backtest. A live forecast adds two commitments the self-verification asked for, recorded
here so they ship *with* any forecast, not after:

- **A calibration layer, standing on ViEWS — not a rival (R4).** ViEWS forecasts *violence*; this
  forecasts *backsliding*, a rarer, worse-instrumented target. Pharos's additive value is **not** a
  better point prediction — it is (a) the adversarially-graded ledger and (b) an open,
  backsliding-specific *calibration harness* over public signals, scored against the baselines above.
  **`OPEN` / `CONTESTED` is a hard ship-gate:** a forecast layer ships only once it beats the
  baselines in the open; until then it is labelled, not headlined.
- **Success is measured on the reachable (R1).** The warning-response gap is real: a forecast does
  not move power. So a live deployment routes each flagged signal to a **named responder**
  (journalists, organisers, builders) and instruments *adoption* — forks, citations, downstream
  reuse — as the success metric, never "did the regime respond." **"Peace" stays untestable (T6) and
  is never claimed as a deliverable.**
- **Reflexivity is pre-registered, not patched (R6).** When a watched indicator improves *after* a
  warning, it is logged as a candidate **warning-response event** and the ambiguity is published —
  never claimed as a clean hit or a miss — and the
  [**"what a calibrated miss looks like" explainer**](CALIBRATED_MISS_EXPLAINER.md) ships at launch.

## Provenance & reproduce

- **V-Dem Freedom of Expression** (`v2x_freexp_altinf`) — *V-Dem (2024), processed by Our
  World in Data* — **CC BY 4.0**. Pinned offline at
  [`data/snapshots/vdem_freexp_annual.csv`](../../data/snapshots/vdem_freexp_annual.csv).
- Pipeline: [`src/forecast/pharos_forecast.py`](../../src/forecast/pharos_forecast.py)
  (stdlib only). Output: [`data/derived/forecast_backtest.json`](../../data/derived/forecast_backtest.json)
  + `.csv`. Code GPL-3.0-or-later; derived data CC0. Reproduce: `make forecast`. Validated
  by 12 offline unit tests in `tests/test_pharos_forecast.py`.
