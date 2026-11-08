<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# DATA_CONTRACT.md — the stable-format contract for reusers (v1)

If you build on this project's data — a paper, a dashboard, a newsroom analysis — this page
is the promise you are building on: what each published file contains, what is guaranteed to
stay stable, what may change, and how to verify all of it without trusting us.

**License:** the data is **CC0-1.0** (no permission needed, attribution appreciated); the code
is GPL-3.0-or-later. **Cite:** [`CITATION.cff`](../CITATION.cff). **Fastest start:** vendor the
one-file, stdlib-only reader [`src/pharos_client.py`](../src/pharos_client.py) — copy it into
your project and every table below loads in one line (`python3 src/pharos_client.py` runs a
smoke demo). **Ethical floor:** everything is country/institution-level only — *watch power,
not people* — enforced in code ([`THREAT_MODEL.md`](../THREAT_MODEL.md)).

---

## The files

All live under [`data/derived/`](../data/derived/) (plus the ledger index under
[`ledger/`](../ledger/)). CSVs are UTF-8 with CRLF row endings (Python `csv` default); JSON is
UTF-8 with LF. Both are pinned by `.gitattributes`, so a clone on any platform gets identical
bytes.

### `wgi_governance.csv` — governance change, per country × dimension (1 row each)

| column | meaning |
|---|---|
| `iso3`, `country` | ISO-3166 alpha-3 code and World Bank display name |
| `dimension`, `dimension_name` | one of `VA` `RL` `CC` `GE` `RQ` `PV` (Voice & Accountability, Rule of Law, Control of Corruption, Government Effectiveness, Regulatory Quality, Political Stability) |
| `year_base`, `year_latest` | the comparison window (currently 2014 → 2024) |
| `sc_base`, `lb_base`, `ub_base` / `sc_latest`, `lb_latest`, `ub_latest` | score (0–100) with published 90% CI bounds at each end of the window |
| `change` | `sc_latest − sc_base` |
| `se_diff`, `z`, `p_two_sided` | SE of the difference (from the CIs), z statistic, two-sided p |
| `verdict` | `DECLINE` / `IMPROVE` only when \|z\| ≥ 1.6449 (90%); otherwise `NO_SIG_CHANGE` — **moves within measurement noise are never flagged** |

Companion: **`wgi_governance_summary.json`** — method, per-dimension counts, the overall
tallies (`dimension_country_cells`, `within_noise`, `meaningful_declines`/`_improvements`,
`decline_to_improve_ratio`), and the `va_robustness` block (95% bar + alternative window).

### `voice_divergence.csv` — three instruments compared, per country (1 row each)

Shared columns: `iso3`, `country_name`, then **three instrument blocks** with a common shape —
prefixes `wgi_` (WGI Voice & Accountability, 0–100), `vdem_` (V-Dem freedom of expression,
0–1), `fh_` (Freedom House civil liberties, 0–60):

| per-instrument column | meaning |
|---|---|
| `*_available` | `True`/`False` — the instrument covers this country in the window |
| `*_v_start`, `*_v_end`, `*_delta` | values at the window ends (instrument's native unit) and the change |
| `*_direction` | `-1` decline / `0` flat / `1` improve |
| `*_flag` | `SIG` / `NS` / `NA` — significant per that instrument's own basis |
| `*_flag_basis` | what "significant" means there (`CI` for WGI; threshold-based otherwise) |
| `wgi_z` | z statistic — WGI only, since only WGI publishes the CIs a z-test needs |

Agreement columns: `label` ∈ `CONCUR-DECLINE` · `CONCUR-IMPROVE` · `CONFLICT` · `MIXED-WEAK` ·
`ALL-FLAT` · `INSUFFICIENT`; `n_available`, `n_sig`, `concurring`, `dissenting`,
`flag_basis_mix` (which significance bases the agreement rests on),
`evidence_strength` ∈ `HIGH`/`MEDIUM`/`LOW`/`NONE`/`CONFLICT`. **There is deliberately no
blended score column** — disagreement is published, never averaged away.

Companion: **`voice_divergence.json`** — the same per-country data nested, plus `counts`,
`headline_concur_decline_n_sig_3` (the full-concurrence ISO3 list), and thresholds.

### `forecast_backtest.csv` — per model (1 row each)

`model`, `crps`, `crps_skill`, `brier`, `brier_skill` — skill is relative to the `no_change`
baseline row (skill 0.0 by construction). Companion **`forecast_backtest.json`** adds the
pre-registration terms, `result` (σ, base rate, `n_forecasts`) and the honest `verdict`
string. **Read the verdict before using the forecasts: v0 does not beat the baseline.**

### `ledger/index.json` — the graded evidence entries

`entries`: `[{id, grade, domain, file, title}, …]` with `grade` ∈ `ROBUST` / `CONTESTED` /
`REFUTED` / `OPEN`; `grades` holds the vocabulary. Each entry's full text (claim, evidence,
sources, `falsification_trigger`) is the markdown file under [`ledger/`](../ledger/).

---

## What is guaranteed (within contract v1)

1. **Additive-only evolution.** Existing columns/keys are never renamed, removed, or
   re-typed; new ones may appear. Categorical vocabularies above only grow, never mutate.
   A breaking change bumps the contract version at the top of this file (and in
   `pharos_client.CONTRACT_VERSION`) with a deprecation note in the CHANGELOG.
2. **Every number is reproducible.** `make verify-offline` recomputes every file above from
   pinned snapshots, offline, and fails unless the result is **byte-identical** to what is
   committed. Provenance travels with the data: each JSON companion carries an
   `input_provenance` block — `{source_url, fetched_utc, input_sha256}` of the pinned snapshot
   file (or one such block per input, for the multi-input `voice_divergence.json`) — so a
   swapped or edited upstream snapshot is detectable from the derived file alone. The raw
   inputs themselves live in [`data/snapshots/`](../data/snapshots/).
3. **Uncertainty is part of the schema.** CIs, z-scores, significance flags, and
   agreement labels ship in the tables; a reuse that drops them misrepresents the data.
4. **The spatial floor holds.** No file will ever contain sub-national, geolocated,
   group-attributed, or person-level columns — the build fails if one appears
   (`make threat-model`).
5. **Consistency is machine-checked.** The counts and figures quoted in the docs and site
   are pinned to these files by the audit gate; if you find a mismatch, it is a bug — the
   gate should have caught it.

**Not guaranteed:** the volatile provenance stamps (`mode`, `fetched_utc`) vary between live
and snapshot recomputes by design; prose documents may be reworded freely; row *counts*
change when upstream data or the window is re-pinned (that is the point — see `make drift`).

---

## Verifying a claim you built on

```bash
make verify-offline   # recompute everything from pinned inputs, byte-exact, no network
make drift            # check the pinned inputs against the live upstream sources
python3 src/pharos_client.py   # smoke-load every surface in this contract
```

Independent instruments, honest flags, published conflicts — if your analysis needs a single
blended "democracy score," this is the wrong dataset, on purpose.
