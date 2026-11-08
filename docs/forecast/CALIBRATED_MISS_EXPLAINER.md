<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# What a calibrated miss looks like

*Ships **with** any Pharos forecast, never after (the R6 reflexivity fix —
[`pharos-forecast-v0.md`](pharos-forecast-v0.md)). Read this before reading any probability
this project publishes.*

## The one-sentence version

> **A 30% warning that resolves "didn't happen" is not a failed forecast. It is exactly what
> a 30% warning is supposed to do seven times out of ten.** A forecaster is judged over many
> calls, by *calibration* — not by whether any single call "came true."

## Why this page exists

A probabilistic early-warning system has a built-in trust trap. The legible, shareable object
is a single call — "Pharos said country X had a 30% chance of backsliding" — and the legible
verdict on it is binary: *did it happen or not?* By that test, **every probability that isn't
0% or 100% is wrong about something.** A 30% that resolves true looks like an under-call; a 30%
that resolves false looks like a false alarm. Neither is a mistake. Scoring a probabilistic
system one call at a time is a category error — and it is the error most likely to either burn
the project's credibility or, worse, pressure it into making over-confident hero calls to look
"right." This page pre-commits to the correct scoring frame so that incentive never bites.

## Calibration: the actual test

Take every signal Pharos ever marks "30% chance of meaningful decline in the next decade."
The system is **calibrated** if, across all of them, *about 30% actually decline.* That's it.

| Among all "30%" calls… | what calibration requires | a single call resolving false is… |
|---|---|---|
| ~70% resolve **false** | yes — that's what 30% *means* | **expected**, not a miss |
| ~30% resolve **true** | yes — that's what 30% *means* | **expected**, not a hit to brag about |

A forecaster who issues a hundred "30%" warnings and sees ~30 of them happen is **perfectly
calibrated** and is doing exactly the job. One who sees ~70 happen was badly *under*-warning;
one who sees ~5 happen was crying wolf. The single resolved call tells you almost nothing; the
*distribution* of resolutions across many same-probability calls tells you everything. This is
why the v0 result is reported as a **reliability curve over 2,600 forecasts**, scored by CRPS
and Brier — proper scoring rules that reward honest probabilities and punish both over- and
under-confidence — and **never** as "did the wolf come for country X."

## A worked calibrated miss

Suppose Pharos flags country X at **30%** for a meaningful decline over the next decade, and
ten years pass with no decline.

- **The wrong read:** "Pharos was wrong / Pharos cried wolf." → discredit the system.
- **The calibrated read:** this is one of the ~70% of 30%-calls that are *supposed* to resolve
  false. It is evidence about calibration **only in aggregate** — pooled with every other 30%
  call. On its own it neither confirms nor refutes anything. The forecast did its job: it
  quantified a real-but-minority risk, honestly.

The symmetric trap is the **calibrated hit**: country Y is flagged 30% and *does* decline. That
is **not** a vindication to headline either — a well-calibrated 30% is *supposed* to come true
about a third of the time. Treating the hit as a triumph is the same category error as treating
the miss as a failure; both invite the system to drift toward dramatic, over-confident calls.
Calibration is judged on the whole book, in both directions.

## The reflexivity twist (why even "miss" is the wrong word for a *live* call)

For a backtest (what v0 ships), resolutions are clean: the decade already happened, nobody acted
on the forecast. A **live** forecast adds a complication the project pre-registers rather than
patches: a warning can *change* what it warned about. If Pharos flags a country and the watched
indicator then *improves*, that is **not** scored as a miss. Per the R6 protocol it is logged as
a **candidate warning-response event** — the system cannot tell whether the threat was overstated
or whether the warning helped avert it, and *that ambiguity is published*, never resolved in the
project's own favour. So a live "30% that didn't happen" splits into two honest cases, and the
forecast claims neither a clean hit nor a clean miss:

1. **a calibrated miss** — a normal 30%-resolves-false, pooled into the reliability curve; or
2. **a possible warning-response** — the warning may have moved the responder; ambiguity logged.

## What would actually count as the system failing

To keep "you can never be wrong" from becoming unfalsifiable, the failure conditions are explicit
and pre-committed — these are real, and any of them is a genuine miss:

- **Miscalibration in aggregate** — the 30% bucket resolves true far from ~30% (the reliability
  curve departs from the diagonal beyond its error bars). *This* is the real failure, and it is
  measurable on the open harness.
- **No skill** — the forecasts don't beat the no-change and climatology baselines on CRPS/Brier.
  (This is exactly the bar v0 sets — and does **not** clear; see
  [`pharos-forecast-v0.md`](pharos-forecast-v0.md). v0 is honest *because* it reports its own
  failure to clear the bar.)
- **Gaming the unfalsifiability** — hedging everything to 50%, or quietly retuning probabilities
  after seeing outcomes. The pre-registered, parameter-fixed design exists to make this detectable.

A calibrated miss is none of these. It is the system working as designed.

## See also

- [`pharos-forecast-v0.md`](pharos-forecast-v0.md) — the pre-registered backtest, baselines, and
  the honest v0 verdict (nothing beats climatology).
- [`../../THREAT_MODEL.md`](../../THREAT_MODEL.md) — why forecasts stay at country/institution
  level (watch power, not people).
- Ledger [`SAA-007`](../../ledger/SAA-007-open-early-warning-exists.md) — open early-warning
  systems exist, but most models are beaten by a naive baseline under fair scoring.
