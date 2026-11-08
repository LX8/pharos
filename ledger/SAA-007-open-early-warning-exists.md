---
id: SAA-007
title: Operational, openly-reproducible conflict early-warning systems exist
grade: ROBUST
domain: systems-and-tech
verified: 2026-06-02
last_reviewed: 2026-07-25
review_interval_days: 540
sources:
  - "Hegre, H. et al. (2019). ViEWS: a political violence early-warning system. Journal of Peace Research. — https://journals.sagepub.com/doi/full/10.1177/0022343319823860"
  - "VIEWS prediction competition (2024). arXiv:2407.11045 — https://arxiv.org/abs/2407.11045"
  - "VIEWS live system — https://viewsforecasting.org/"
falsification_trigger: "Downgrade if the operational systems cease, or are shown to be non-reproducible or closed. (That a no-change/persistence baseline is a *hard benchmark* many models fail to beat under MSE on zero-inflated fatality levels is already true — verified and nuanced in [SAA-040](SAA-040-conflict-forecasting-track-record.md) — and is NOT a downgrade trigger here: this entry grades the existence of the open, reproducible, uncertainty-honest infrastructure, not forecast skill.)"
---

## Claim
Uppsala's **ViEWS** (operational since 2018) publishes monthly forecasts of
organized violence up to 36 months ahead, at country and sub-national resolution,
built entirely on open datasets (UCDP, PRIO-GRID, ACLED, V-Dem, World Bank), with
open replication code. Its successor **VIEWS** treats *uncertainty quantification*
as first-class (probabilistic forecasts scored by CRPS).

## Evidence
Verified 3–0 against primary sources and live infrastructure. **Honest caveat (the bar this
entry is graded against):** in the conflict-forecasting competitions (Hegre, Vesco & Colaresi 2022;
Hegre, Vesco et al. 2025), a no-change / persistence baseline is a *hard benchmark* that many
submitted models fail to beat under MSE on zero-inflated fatality levels — though the best ensembles
*do* outperform it and the field has called for new metrics to capture genuine improvements. The
full verified, metric-conditional finding is in [SAA-040](SAA-040-conflict-forecasting-track-record.md).
This entry's scope deliberately **excludes** forecast skill from its claim (the trigger downgrades
on the infrastructure ceasing or closing, *not* on competitor skill). So the ROBUST claim is narrow:
the *open, reproducible, uncertainty-honest infrastructure* exists — **not** that any model
reliably beats the baseline. This is precisely why the project's own forecasting pillar scores
itself against that baseline rather than shipping a point-call (see
[`docs/forecast/pharos-forecast-v0.md`](../docs/forecast/pharos-forecast-v0.md)).

## Why it matters
The strongest, least-contested model for the Pharos bet: an open, reproducible,
uncertainty-honest feedback loop on the real world. **Interoperate, don't
rebuild it** — add a backsliding layer on top, pitched at power not people.
