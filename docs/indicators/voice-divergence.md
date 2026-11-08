<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Voice & Accountability, triangulated — *publish divergence, not a single score*

*Computed 2026-06-15 from open data; reproduce with `make divergence` (or `make verify`).
Country/institution level only — **watch power, not people** ([`NOTICE`](../../NOTICE) §7,
[`THREAT_MODEL.md`](../../THREAT_MODEL.md)).*

This is **Tier-0 ④** of the plan-for-peace launch gates ([`../verifications/plan-for-peace.md`](../verifications/plan-for-peace.md)),
and the calibration-layer posture the self-verification asked for. It corroborates this project's
own headline finding — *the measurable democratic erosion of 2014→2024 is concentrated in Voice &
Accountability* ([`wgi-governance.md`](wgi-governance.md)) — by checking it against two further
instruments, and it does so **without ever publishing a single blended backsliding number.**

## Why divergence, not a score

A single index can be gamed: capture one survey house or one expert coder and a country's number
improves while reality worsens — and a blended average then *launders* that false green. So we never
blend. For each country we reduce three instruments to a **signed, significant decade change**, and
publish where they **concur** versus where they **conflict**. A captured single input can flip at most
one sign — which then surfaces as `CONFLICT` (with the dissenter named), not buried in a mean.

Four honesty guarantees, enforced in code and tests:

1. **No blended score, ever.** The three native scales (−2.5..2.5 / 0–1 / 0–60) are *never* mapped
   onto a shared axis. Commensurability lives only at **sign** and **significance**, which are scale-free.
2. **Disagreement beats majority.** A 2-vs-1 split is `CONFLICT`, not a vote — a vote would re-hide a
   single number and let two inputs bury one honest dissent.
3. **Evidence strength is transparent.** Every sign carries its `flag_basis` (`CI` / `THRESHOLD` /
   `THRESHOLD-NO-CI`), so a CI-backed significance is never confused with a threshold guess.
4. **Missingness is shown, never imputed.** An absent instrument is marked absent; a country with only
   one instrument is `INSUFFICIENT`, not a finding.

## The three instruments (2014 → 2024)

| Instrument | Source | Scale | Significance test | Basis |
|---|---|---|---|---|
| **WGI Voice & Accountability** | World Bank WGI (local, this repo) | 0–100, higher = freer | reuses its published **90% CI z-test** | `CI` (gold) |
| **V-Dem Freedom of Expression** (`v2x_freexp_altinf`) | V-Dem via Our World in Data | 0–1, higher = freer | material-change threshold **0.05** | `THRESHOLD` |
| **Freedom House Civil Liberties** | Freedom House via Our World in Data | **0–60**, higher = freer | conservative dead-band **3 pts** (= 5 on 0–100) | `THRESHOLD-NO-CI` |

FH ships **no** confidence interval; its significance is the weakest of the three and is labelled
as such on every cell. WGI is the only CI-backed input — a concurrence that includes it is `HIGH`
evidence; one without it is at most `MEDIUM`.

## Headline (203 WGI V&A countries; joined to 174 V-Dem and 197 FH)

| Label | n | Meaning |
|---|---|---|
| **CONCUR-DECLINE** | **45** | ≥2 significant instruments agree voice **declined** |
| CONCUR-IMPROVE | 8 | ≥2 significant instruments agree it **improved** |
| **CONFLICT** | **5** | instruments **contradict** — a single number would mislead |
| MIXED-WEAK | 73 | one instrument moves, the others see only noise |
| ALL-FLAT | 63 | ≥2 instruments, none beyond its noise floor |
| INSUFFICIENT | 9 | fewer than 2 instruments available — cannot triangulate |

- **Cross-instrument decline outweighs improvement ~5.6 : 1 (45 vs 8)** — multi-source concurrence on
  "the erosion is concentrated in voice," triangulated rather than asserted from one source.
- **26 countries show full 3/3 concurrence on decline** (the high-confidence backsliding signal): `AFG BDI BEN BFA BLR COM GEO HKG HTI HUN MEX MLI MMR MOZ
  NER NIC PHL RUS SLV SRB TJK TUN TUR TZA VEN YEM`.
- The large `MIXED-WEAK` + `ALL-FLAT` blocks (136 countries) are consistent with the WGI finding that
  *most of the world did not measurably move* — the method does not manufacture agreement.

## Robustness & honest limits

**Threshold sensitivity (the 45/8 is not a knife-edge).** The V-Dem 0.05 and FH 3.0 dead-bands are
judgment calls (WGI is CI-backed, so threshold-invariant). The sweep below (shipped in
`threshold_sensitivity` in [`voice_divergence.json`](../../data/derived/voice_divergence.json))
re-triangulates at ±20% of each:

| V-Dem threshold | FH dead-band | CONCUR-DECLINE | CONCUR-IMPROVE | CONFLICT |
|---|---|---|---|---|
| 0.04 | 2.4 | 45 | 8 | 7 |
| 0.05 (headline) | 3.0 | **45** | **8** | **5** |
| 0.06 | 3.6 | 40 | 8 | 3 |

The decline asymmetry holds in a tight **~40–45 CONCUR-DECLINE vs a steady 8 CONCUR-IMPROVE** band —
robust to the threshold judgment calls. (Only the CONFLICT count wobbles, as expected for
near-threshold cells; full 9-cell grid in the JSON.)

**These instruments are NOT independent — concurrence, not corroboration.** V-Dem feeds the WGI
aggregate, and V-Dem/FH draw on overlapping expert-coder networks. So a 3/3 concurrence is
*multi-source agreement*, not three independent measurements of one latent construct, and a
coordinated shift in the shared coder pool could move two of three instruments together. "Robust to
the capture of a *single non-overlapping source*; the V-Dem↔WGI coder overlap is a residual." This is
why the design rule is *publish divergence and surface dissent* (a captured input flips one sign and
shows as CONFLICT) rather than claim independence — and why the headline is "concurrence," not
"corroboration."

## How to read a cell

- **Hungary (HUN) — `CONCUR-DECLINE`, strength `HIGH`, 3/3.** WGI VA SIG-decline (CI), V-Dem −0.43
  (threshold), FH −14 (threshold-no-CI): all three concur on decline.
- **United States (USA) — `CONCUR-DECLINE`, strength `MEDIUM`, 2/3.** WGI VA was *not* significant at
  90% (so no CI-backed flag), but V-Dem (0.963→0.904) and FH (55→50) both crossed their thresholds
  down. Real, but weaker evidence than a 3/3 — and the schema says so rather than rounding it up.
- **Honduras (HND) — `CONFLICT`, dissenter `fh`.** V-Dem SIG-down while FH SIG-up; WGI not significant.
  Exactly the cell where a blended score would invent a false consensus. Published as a conflict to
  audit, never resolved by a vote. (The five conflicts: HND, MDG, MDV, SVN, ZMB.)

## Method

For each country, each instrument answers one falsifiable yes/no — *did V&A move materially up, down,
or stay flat 2014→2024, beyond this instrument's own noise?* — in its **own units**:

- **WGI**: reuses [`wgi_governance.py`](../../src/indicators/wgi_governance.py)'s `compute_change`
  90% CI z-test verdict (`DECLINE`/`IMPROVE`/`NO_SIG_CHANGE`) — no recomputation, one engine.
- **V-Dem**: `|Δ| ≥ 0.05` on the 0–1 scale → significant (OWID's grapher exposes no CI; if the raw
  V-Dem posterior SE is ever wired in, the same z-test upgrades it from threshold to CI).
- **FH**: `|Δ| ≥ 3` on the 0–60 score → significant. (FH publishes no uncertainty at all.)

Only the **signs** of the available-and-significant instruments are combined, in a fixed resolution
order: `INSUFFICIENT` → `CONFLICT` → `CONCUR` → `MIXED-WEAK` → `ALL-FLAT`. Magnitudes stay native and
are reported for the reader but never compared across instruments.

## Caveats (read these)

- **FH is 0–60, not 0–100.** The dead-band is rescaled to 3 points accordingly; a future maintainer
  who swaps in the 0–100 `freedom-score-fh` total must restore a 5-point band.
- **Thresholds (0.05, 3/60) are conservative judgment calls** — deliberately biased toward `NS` so the
  pipeline never manufactures agreement. Sensitivity-test before reading too much into near-threshold cells.
- **Partial independence.** V-Dem and FH share parts of the expert-coder ecosystem, so a coordinated
  coding capture could move two signs together; WGI aggregates many non-expert sources, which is why a
  **3/3 concurrence including WGI's CI flag** is the genuinely robust cell.
- **Non-stationary WGI CIs** widen for data-poor autocracies, pushing some toward `NS`/`INSUFFICIENT` —
  *absence of a significant decline is not evidence of stability.*
- **Coverage gaps are shown, not filled.** Taiwan is absent from WGI VA entirely (so never appears);
  Hong Kong (HKG), West Bank & Gaza (PSE) and Kosovo (code mismatch) often land `INSUFFICIENT`.

## Provenance & licensing

- **WGI Voice & Accountability** — World Bank Worldwide Governance Indicators, via this repo's
  [`data/derived/wgi_governance.csv`](../../data/derived/wgi_governance.csv).
- **V-Dem Freedom of Expression** (`v2x_freexp_altinf`) — *V-Dem (2026), processed by Our World in Data,*
  `https://ourworldindata.org/grapher/freedom-of-expression-index.csv` — **CC BY 4.0**.
- **Freedom House Civil Liberties** — *Freedom House, "Freedom in the World", processed by Our World in
  Data,* `https://ourworldindata.org/grapher/civil-liberties-score-fh.csv` — **CC BY 4.0**.

Pipeline: [`src/indicators/voice_divergence.py`](../../src/indicators/voice_divergence.py) (stdlib only).
Outputs: [`data/derived/voice_divergence.csv`](../../data/derived/voice_divergence.csv) and
`voice_divergence.json` (per-country triples + agreement labels). Code GPL-3.0-or-later; derived data CC0.
Reproduce: `make divergence`. Validated by 16 offline unit tests in `tests/test_voice_divergence.py`.
