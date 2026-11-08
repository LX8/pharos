# Indicator — WGI governance (6 dimensions), computed with honest uncertainty

*Computed 2026-06-02 from World Bank Worldwide Governance Indicators (latest year
2024). Reproducible: `make verify`. Country/institution-level — **watch power,
not people** ([`../../NOTICE`](../../NOTICE) §7).*

## Headline (2014 → 2024)

Across **six governance dimensions × ~204 countries** (1,222 dimension-country
cells):

| | Cells | Share |
|---|---:|---:|
| ⚪ **Within measurement noise** | **1,080** | **88%** |
| 🔻 Meaningful decline | **88** | 7% |
| 🔺 Meaningful improvement | **54** | 4% |

**Most governance scores did not move beyond their own error bars in a decade.**
Of the changes that *are* measurable, declines lead improvements **88 : 54
(1.63 : 1)** — but the erosion is **not** across-the-board. It is concentrated in
one place.

## Where the decline actually is

| Dimension | mean 2014→2024 | 🔻 decline | 🔺 improve | reading |
|---|---|---:|---:|---|
| **Voice & Accountability** | 56.9 → 55.0 | **33** | 6 | the most concentrated decline of any dimension, 33 of 203 (5.5 : 1) |
| **Political Stability / Absence of Violence** | 66.3 → 65.3 | **19** | 7 | notable decline — *but see caveat* |
| Rule of Law | 55.9 → 56.0 | 13 | 13 | balanced |
| Regulatory Quality | 54.1 → 54.3 | 7 | 7 | balanced / mostly noise |
| Government Effectiveness | 52.6 → 52.1 | 7 | 4 | mostly noise |
| Control of Corruption | 46.3 → 47.1 | 9 | **17** | *improved* in more countries |

**The measurable backsliding of the decade is specifically in democratic *voice
and accountability*** — free expression, free media, political participation,
the accountability of power — not in technical state capacity (which is mostly
flat) and not in corruption control (which improved in more places than it
worsened). That is precisely the dimension the rest of this project is about.

**Robustness (the 5.5 : 1 is neither a threshold nor a window artifact).** The Voice &
Accountability decline asymmetry survives *two* independent stress tests, both computed and
shipped in `va_robustness` in
[`wgi_governance_summary.json`](../../data/derived/wgi_governance_summary.json):

| Window | 90% bar (decline : improve) | 95% bar (|z| ≥ 1.96) |
|---|---|---|
| **2014 → 2024** (primary) | **33 : 6 = 5.5 : 1** | 28 : 6 = 4.67 : 1 |
| **2015 → 2024** (alternative) | 30 : 6 = 5.0 : 1 | 22 : 4 = 5.5 : 1 |

Across both windows and both confidence bars (n = 203), the ratio stays in a tight **~4.7–5.5 : 1**
band — strongly decline-dominated however you slice it. (The alternative window is computed from the
same pinned snapshot, which holds 2014–2024 annually; a pre-2014 window would need an additional WGI
vintage and is left as a future check.) The per-dimension 95% counts also ship in `counts_95pct_bar`.

**Robustness to the independence assumption.** The test treats the 2014 and 2024 estimates as
statistically independent (ρ = 0). They are not: WGI aggregates an *overlapping* source set across
years (the same expert coders, V-Dem, EIU, … feed both snapshots), so the true ρ is positive. For a
*change* test this makes ρ = 0 the **conservative** choice — positive correlation means shared
measurement error partially cancels in the difference, so the test gets *more* sensitive as ρ rises
and flags *more*, not fewer. Because the source-level microdata to estimate ρ is not in this repo,
the sweep below (shipped in `va_robustness.independence_sensitivity`) reports how the counts move:

| Assumed ρ | decline : improve | ratio |
|---|---|---|
| 0.0 (headline, conservative) | 33 : 6 | **5.5 : 1** |
| 0.3 | 48 : 13 | 3.7 : 1 |
| 0.5 | 57 : 16 | 3.6 : 1 |
| 0.7 | 66 : 25 | 2.6 : 1 |
| 0.9 | 88 : 37 | 2.4 : 1 |

Both counts rise as the test gets more sensitive, but the decline:improve ratio stays **well above
1 across the entire sweep** — the *direction* (voice erosion is concentrated in declines) is robust
to the independence assumption. The headline 33 : 6 is therefore a *lower bound* on how many
countries show meaningful voice decline, not an overcount.

Selected meaningful movers (full table:
[`../../data/derived/wgi_governance.csv`](../../data/derived/wgi_governance.csv)):

- **Voice & Accountability** ▼ Nicaragua −19, Mali −17, Tunisia −14, Afghanistan,
  Hong Kong, Myanmar, Russia · ▲ The Gambia +18, Sri Lanka, Armenia
- **Rule of Law** ▼ Nicaragua, Hong Kong, Mexico · ▲ Lithuania, The Gambia
- **Control of Corruption** ▼ Türkiye, Malta, Nicaragua · ▲ (from low bases) Angola, Kazakhstan

## Caveats (what this does **not** say)

- **WGI is a perception-based composite** of expert and survey sources — it
  measures *perceptions* of governance, with real uncertainty (which is exactly
  why the 90% CI is carried through every comparison).
- **Do NOT read "Political Stability" improvements as democratic gains.** That
  dimension mixes *stability* with *absence of violence*, and **repressive
  authoritarian stability scores well on it.** Its top computed "improvements"
  include counterintuitive cases (e.g. Ukraine, North Korea) driven by relative
  percentile scoring and very low/disrupted baselines. Stability ≠ freedom; this
  dimension is the least aligned with the project's aim and is reported only for
  completeness.
- **Absence of a flag ≠ stability.** 1,080 "noise" cells are *not measurably
  changed*, not *confirmed steady*.
- **Unweighted country means are a rough gauge**, not population-weighted.
- **No causal claim.** This is measurement, not explanation; pair it with the
  evidence ledger ([`../../ledger/`](../../ledger/)) for *why*.

## Method

For each country and dimension, the change in the 0–100 score from baseline to
latest year. The published **90% CI** gives the standard error
(`se = (upper − lower) / (2 × 1.6449)`); the difference is tested with a
two-sided z-test, `z = Δ / √(se_base² + se_latest²)`, flagged **DECLINE /
IMPROVE only when |z| ≥ 1.6449** (90%). Deliberately conservative — moves within
measurement noise are left unflagged. The load-bearing calculation is a pure
function with offline unit tests
([`../../tests/test_wgi_governance.py`](../../tests/test_wgi_governance.py)).

## Provenance

- **Source:** World Bank, Worldwide Governance Indicators (WGI), source 3 —
  https://www.worldbank.org/en/publication/worldwide-governance-indicators
- **Indicators:** `GOV_WGI_{VA,RL,CC,GE,RQ,PV}.SC` with `.SC_LB` / `.SC_UB` (90% CI).
- **Fetched:** 2026-06-02 · latest WGI year: 2024.
- **Pipeline:** [`../../src/indicators/wgi_governance.py`](../../src/indicators/wgi_governance.py) · **reproduce:** `make indicators` · **verify:** `make verify`.
- **License:** code GPL-3.0-or-later; derived data CC0-1.0; WGI is freely available (cite the World Bank).
