---
id: SAA-040
title: "Conflict/backsliding forecasting has a real, peer-reviewed out-of-sample track record — but 'beats a no-change baseline' is metric- and task-dependent, not a settled fact"
grade: CONTESTED
domain: conflict-risk
verified: 2026-07-25
last_reviewed: 2026-07-25
review_interval_days: 270
sources:
  - "Hegre, H., Allansson, M., Basedau, M., et al. (2019). ViEWS: A political violence early-warning system. Journal of Peace Research, 56(2), 155-174. — https://doi.org/10.1177/0022343318824350"
  - "Hegre, H., Nygård, H. M., & Landsverk, P. (2021). Can We Predict Armed Conflict? How the First 9 Years of Published Forecasts Stand Up to Reality. International Studies Quarterly, 65(3), 660-668. — https://doi.org/10.1093/isq/sqaa094"
  - "Hegre, H., Vesco, P., & Colaresi, M. (2022). Lessons from an Escalation Prediction Competition. International Interactions, 48(4), 521-554. — https://doi.org/10.1080/03050629.2022.2070745"
  - "Hegre, H., Vesco, P., Colaresi, M., et al. (2025). The 2023/24 VIEWS Prediction Challenge: Predicting the Number of Fatalities in Armed Conflict, with Uncertainty. Journal of Peace Research, 62(6), 2070-2087. — https://doi.org/10.1177/00223433241300862 (preprint arXiv:2407.11045)"
  - "Goldstone, J. A., Bates, R. H., Epstein, D. L., Gurr, T. R., Lustik, M. B., Marshall, M. G., Ulfelder, J., & Woodward, M. (2010). A Global Model for Forecasting Political Instability. American Journal of Political Science, 54(1), 190-208. — https://doi.org/10.1111/j.1540-5907.2009.00426.x"
falsification_trigger: "Two-layer downgrade rule. ROBUST layer (the infrastructure + the published out-of-sample track record) downgrades only if ViEWS/VIEWS ceases operation or its replication code is shown non-reproducible, or if the Hegre et al. (2021) retrospective finding ('reasonably accurate' predictions, ISQ) is overturned by a re-evaluation against a longer realized series. The CONTESTED headline layer ('beats baseline' is metric-dependent) moves to ROBUST only if a future VIEWS Challenge converges on a single skill metric under which the best models *robustly* beat no-change across both fatality levels AND escalation/changes; it moves toward REFUTED-of-skill if convergence instead shows ensemble models *cannot* beat the persistence baseline under any standard metric over a multi-year realized horizon."
---

## Claim

Modern conflict/backsliding forecasting is a real, peer-reviewed, *out-of-sample* enterprise —
not a black box. Three findings carry the weight, and the third corrects an earlier overclaim in
this ledger (SAA-007) and the project's own forecast docstring.

**1. The infrastructure is open, operational, and uncertainty-honest (ROBUST).** Uppsala/PRIO's
**ViEWS** (operational since 2018) publishes monthly forecasts of organized violence up to 36 months
ahead, at country *and* sub-national resolution, across the three UCDP violence types, built on open
datasets with open replication code (Hegre et al. 2019, JPR). Its successor **VIEWS** made
uncertainty quantification first-class: the 2023/24 Challenge scored forecasts of fatalities *as
probability distributions* by **CRPS** (Hegre, Vesco et al. 2025, JPR).

**2. The out-of-sample track record is real but qualified (ROBUST that it is meaningful; the
precision/recall trade-off is the honest qualifier).** Hegre, Nygård & Landsverk (2021, ISQ)
evaluated the first 9 years of published conflict forecasts against what actually happened and
found them "meaningful and reasonably accurate" — but worse at predicting *low-level* conflict
incidence than *major* armed conflict, and subject to a hard precision/recall trade-off (to reach
a recall of ~0.8, estimated precision is ~0.6). PITF's global instability model (Goldstone et al.
2010, AJPS) retrospectively forecast ~80%+ of instability onsets at a 2-year lead, with **partial
democracy with factionalism** as the single strongest risk factor (disproportionately
over-represented among onsets), alongside low development and conflict history.

**3. "Beats a no-change baseline" is metric- and task-dependent — the correction (CONTESTED).** An
earlier version of this ledger (SAA-007) and the project's forecast docstring claimed that in the
VIEWS prediction competitions "*most models are beaten by a no-change baseline*." The primary
sources support a **narrower, more nuanced** finding. In the 2022 escalation competition (Hegre,
Vesco & Colaresi 2022, *International Interactions*): an **ensemble of the contributions performed
well and better than the average model, though worse than the best individual contribution**, and
**almost all participant models scored better than the benchmark models for most metrics** — but
the **no-change model nonetheless has a better mean-squared-error than several models because the
outcome is heavily zero-inflated**. So "models are beaten by no-change" is true *under MSE on
zero-inflated fatality levels specifically*, not as a blanket statement, and the field has
explicitly called for **new evaluation metrics** to capture genuine improvements rather than
declaring the baseline the winner. (This is precisely why Pharos scores on CRPS + Brier against
*three* no-skill references — no-change, global and per-country climatology — rather than asserting
the baseline is unbeatable.)

## Why it matters

This entry is the direct prior art for the project's own forecasting pillar, and it does two things
at once: (a) it documents that conflict/backsliding forecasting is a legitimate, measured, openly
reproducible science — the strongest possible warrant for the Pharos bet — and (b) it **corrects an
overclaim in this ledger**, replacing a sweeping "most models are beaten by no-change" with the
verified, metric-conditional truth. The honesty lesson is the point: the same discipline this
project applies to fascism's disinformation engine applies to itself — an unverified load-bearing
claim, once found, is corrected in the open. The corrected framing also *strengthens* the forecast
pillar: it is no longer leaning on an overstatement, and it competes against the strongest honest
baselines under the metric the field now treats as first-class (CRPS).

## Honest limits

- **Metric-conditionality is the whole finding.** "Beats baseline" is not a property of a model; it
  is a property of a (model, metric, task) triple. The field is still converging on the right
  metric, which is itself a form of open contestation.
- **The 2025 Challenge's full CRPS-vs-baseline tables were not re-read line-by-line for this
  entry** (the publisher PDFs are paywalled/bot-protected); the quantified claims above are those
  verifiable from the 2022 competition's primary text and the 2021 retrospective. Any specific
  "model X beat the baseline by Y" figure should be sourced from the full Challenge results before
  being asserted.
- **Backsliding ≠ fatalities.** The track record here is for *organized violence / fatalities*.
  Forecasting *democratic-backsliding* (the project's target) is a younger, less-validated task —
  the transfer of these accuracy results to backsliding is plausible but not measured here.
