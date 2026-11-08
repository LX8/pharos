---
id: SAA-029
title: "Anocracy + factionalism robustly forecasts instability, but the causal 'anocracy causes civil war' reading is partly a Polity coding artifact"
grade: CONTESTED
domain: conflict-risk
verified: 2026-06-18
last_reviewed: 2026-06-18
review_interval_days: 270
sources:
  - "Goldstone, J. A., Bates, R. H., Epstein, D. L., Gurr, T. R., Lustik, M. B., Marshall, M. G., Ulfelder, J., & Woodward, M. (2010). A Global Model for Forecasting Political Instability. American Journal of Political Science, 54(1), 190-208. — https://doi.org/10.1111/j.1540-5907.2009.00426.x"
  - "Vreeland, J. R. (2008). The Effect of Political Regime on Civil War: Unpacking Anocracy. Journal of Conflict Resolution, 52(3), 401-425. — https://doi.org/10.1177/0022002708315594"
  - "Hegre, H., Ellingsen, T., Gates, S., & Gleditsch, N. P. (2001). Toward a Democratic Civil Peace? Democracy, Political Change, and Civil War, 1816-1992. American Political Science Review, 95(1), 33-48. — https://www.cambridge.org/core/journals/american-political-science-review/article/abs/toward-a-democratic-civil-peace-democracy-political-change-and-civil-war-18161992/49244FF48139A3516DB45FF294902F6A"
  - "Fjelde, H., Knutsen, C. H., & Nygård, H. M. (2021). Which Institutions Matter? Re-Considering the Democratic Civil Peace. International Studies Quarterly, 65(1), 223-237. — https://academic.oup.com/isq/article/65/1/223/5990223"
falsification_trigger: "A downgrade to REFUTED for the causal layer would be triggered by broad replication showing the anocracy/factionalism→civil-war relationship holds with endogeneity-purged measures (X-Polity, V-Dem horizontal/vertical constraints) across datasets. Conversely, the forecasting layer would be downgraded if the PITF model's out-of-sample accuracy failed to replicate on post-2003 data. An upgrade of the overall entry toward ROBUST would require defenders to show the ~30x factionalism odds survive removal of the PARCOMP/PARREG components."
---

## Claim
As a forecasting result the claim is strong: the Political Instability Task Force model (Goldstone et al. 2010) predicts instability onsets ~2 years out with >80% accuracy, and partial democracy with factionalism carries odds of instability roughly 30x a full autocracy — the finding Walter (2022) popularized. But the causal/institutional interpretation — that being an anocracy with factions *causes* civil war — is genuinely contested. Vreeland (2008) shows the Polity-based anocracy category and the specific factionalism indicator (PARCOMP=3) are defined with reference to "intense, hostile, and frequently violent" competition, so they partly ENCODE the violence they predict; purging these components (X-Polity) makes the inverted-U and the regime-civil-war relationship vanish.

## Evidence
FOR: The inverted-U / intermediate-regime risk is a decades-old, repeatedly estimated pattern (Hegre et al. 2001 APSR; Goldstone et al. 2010 AJPS), and the PITF model's predictive accuracy (>80%, two-year lead) is real and operationally used by the US government. AGAINST: Vreeland (2008, JCR) demonstrates that the result is driven by two Polity components (PARREG, PARCOMP) coded with explicit reference to violent factional competition — when removed, the relationship disappears. This critique is corroborated, not isolated: Fjelde, Knutsen & Nygård (2021, ISQ) confirm the curvilinear relationship does not survive purging Polity of its endogenous component, and state-capacity reanalyses find the inverted-U non-robust to alternative democracy measures. Crucially, the very "factionalism" warning sign Goldstone/Walter elevate IS the PARCOMP=3 indicator Vreeland flags — so the measurement critique strikes the headline directly, not a side claim.

## Why it matters
This is the single most-cited empirical basis for claims that the US (downgraded to "anocracy" after Jan 6) is at elevated civil-war risk. If the relationship is partly a coding artifact, the alarm rests on a measure that mistakes the symptom (factional, sometimes-violent competition) for an institutional cause — overstating both predictive transfer to specific cases and the policy lever (institutions vs. underlying factional violence).
