#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pharos-forecast v0 — a calibration layer, not a rival forecaster.

The plan-for-peace self-verification graded the forecasting pillar QUALIFIED/SERIOUS
(C5 + R6): a public point-call ("country X will fall") is reflexive and discrediting,
and the conflict-forecasting literature finds a no-change/persistence baseline is a
*hard benchmark* — many models fail to beat it under MSE on zero-inflated fatality
levels, though the best ensembles do outperform it and the field is still converging
on the right metric (Hegre, Vesco & Colaresi 2022; see SAA-040 for the verified, nuanced
finding — an earlier "most models are beaten by no-change" framing here was an
overstatement, corrected). So this v0 does NOT ship a hero call. It is a transparent,
pre-registered **backtest harness** that asks one honest, falsifiable question over a
whole portfolio of forecasts:

    Does any simple model of democratic-backsliding beat a no-change baseline,
    scored by proper scoring rules (CRPS + Brier), and is it calibrated?

The success bar is pre-committed in code below and is deliberately humbling: **skill > 0
vs. the no-change baseline.** If a model does not clear it, the harness says so — that
honesty is the product. Everything is country/institution-level (watch power, not
people; see THREAT_MODEL.md), retrodictive (no live intervention, so the R6 reflexivity
trap does not bite a backtest — the protocol for live forecasts is in the doc), and
reproducible (stdlib only; offline from a pinned snapshot).

Data: V-Dem Freedom of Expression index (v2x_freexp_altinf, 0-1), annual, via OWID.
Proper scoring rules: Gneiting & Raftery (2007). Brier (1950). No-change baseline
convention: the VIEWS prediction competition.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "indicators"))
import fetch_utils  # noqa: E402 — shared resilient fetch + offline snapshots

# ---- PRE-REGISTERED design (fixed before seeing scores; do not tune to results) ----
HORIZON = 10        # forecast 10 years ahead
WINDOW = 10         # lookback for trend models
DELTA = 0.05        # a "meaningful decline" = a drop of >= 0.05 on the 0-1 scale
DAMP = 0.5          # damped-trend damping factor
REVERSION_K = 0.20  # regression-to-mean pull
ORIGIN_MIN, ORIGIN_MAX = 2000, 2014   # T such that T-WINDOW>=1990 and T+HORIZON<=2024
SUCCESS_BAR = "skill > 0 vs the no-change baseline (CRPS and Brier), with calibration"

VDEM_URL = ("https://ourworldindata.org/grapher/freedom-of-expression-index.csv"
            "?v=1&csvType=full&useColumnShortNames=true")
VDEM_COL = "freeexpr_vdem__estimate_best"
# The annual V-Dem snapshot is the FORECAST input (1990–2024), pinned alongside the
# WGI/V-Dem/FH voice-divergence snapshots on 2026-06-18. These two constants record
# that pin so the derived JSON's input_provenance is deterministic in offline mode
# (CSV snapshots carry no embedded provenance, unlike the WGI JSON snapshot).
SNAP_FETCHED_UTC = "2026-06-18T04:35:36+00:00"
SNAP_MIN, SNAP_MAX = 1990, 2024
_HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT = os.path.normpath(os.path.join(_HERE, "..", "..", "data", "snapshots", "vdem_freexp_annual.csv"))
DERIVED = os.path.normpath(os.path.join(_HERE, "..", "..", "data", "derived"))
_OFFLINE = False


# ----------------------------------------------------------------- pure core ----

def normal_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def normal_pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def crps_gaussian(mu, sigma, y):
    """Closed-form CRPS of a Gaussian forecast N(mu, sigma) against observation y
    (Gneiting & Raftery 2007). Lower is better. O(1)."""
    if sigma <= 0:
        return abs(y - mu)
    z = (y - mu) / sigma
    return sigma * (z * (2.0 * normal_cdf(z) - 1.0) + 2.0 * normal_pdf(z) - 1.0 / math.sqrt(math.pi))


def brier(p, o):
    """Brier score for a single probability p of a binary outcome o in {0,1}. O(1)."""
    return (p - o) ** 2


def stdev(xs):
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def skill(score_model, score_baseline):
    """Skill score: 1 - model/baseline. >0 means the model beats the baseline. O(1)."""
    return 1.0 - (score_model / score_baseline) if score_baseline > 0 else 0.0


# ---- pre-registered forecast models: each returns a point forecast of the change ----

def f_no_change(series, T):
    return 0.0


def f_trend(series, T):
    return (series[T] - series[T - WINDOW]) * (HORIZON / WINDOW)


def f_damped_trend(series, T):
    return f_trend(series, T) * DAMP


def make_reversion(panel_mean):
    """Reversion-to-the-panel-mean model. ``panel_mean`` may be a number (constant
    target, as in the unit test) or a callable ``panel_mean(T)`` returning the
    leak-free cross-sectional mean of all levels observed by origin year T."""
    if callable(panel_mean):
        def f_reversion(series, T):
            return -REVERSION_K * (series[T] - panel_mean(T))
        return f_reversion

    def f_reversion(series, T):
        return -REVERSION_K * (series[T] - panel_mean)
    return f_reversion


def eligible(series, T):
    return (T - WINDOW) in series and T in series and (T + HORIZON) in series


def _past_deltas_for(series, T):
    """Leak-free past HORIZON-year changes for ONE country observable at origin T:
    deltas over [a, a+HORIZON] whose outcome is fully realized by year T
    (a+HORIZON <= T). Never reads series[T+HORIZON] or later. O(years)."""
    return [series[a + HORIZON] - series[a]
            for a in range(SNAP_MIN, T - HORIZON + 1)
            if a in series and (a + HORIZON) in series]


def _history_at(panel, T):
    """Leak-free fitting quantities available at origin year T — the fix for the
    backtest's structural look-ahead leakage. ``sigma``, the global ``climatology``
    mean, and ``reversion``'s panel mean were previously fit on the FULL panel
    (every country-year 1990-2024, including the outcomes being scored), which made
    the harness in-sample. Here each is derived ONLY from data a forecaster standing
    at year T could actually see: past realized deltas whose outcome year <= T, and
    level values at years <= T. The pre-registered 'nothing beats baseline' verdict
    is robust to this (recomputed and confirmed), but the harness is now trustworthy
    enough to detect a genuinely skillful v1 rather than crediting a leakage artifact.

    Returns (all_past_deltas, per_country_past_delta_means, level_mean) for fitting
    the spread, the two climatologies, and reversion — all leak-free.
    """
    all_deltas, country_means, levels = [], [], []
    for series in panel.values():
        ds = _past_deltas_for(series, T)
        all_deltas.extend(ds)
        if ds:
            country_means.append(sum(ds) / len(ds))
        levels.extend(v for y, v in series.items() if y <= T)
    level_mean = sum(levels) / len(levels) if levels else 0.0
    return all_deltas, country_means, level_mean


def reliability(pairs, nbins=10):
    """Calibration table: for forecast-probability bins, observed event frequency.
    `pairs` is [(p, o)]. Returns [(bin_lo, bin_hi, n, mean_p, observed_freq)]."""
    bins = []
    for b in range(nbins):
        lo, hi = b / nbins, (b + 1) / nbins
        sel = [(p, o) for p, o in pairs if (lo <= p < hi or (b == nbins - 1 and p == 1.0))]
        if sel:
            mp = sum(p for p, _ in sel) / len(sel)
            of = sum(o for _, o in sel) / len(sel)
            bins.append((round(lo, 2), round(hi, 2), len(sel), round(mp, 3), round(of, 3)))
    return bins


def backtest(panel, models, score_origins=None):
    """Pure. Run every model over every eligible (country, origin-year) forecast.

    Returns dict(sigma, base_rate, n_forecasts, per_model{...}) — aggregate CRPS,
    Brier, skill-vs-no-change, and calibration. O(countries * origins * models).

    Contract: ``models`` must include a ``no_change`` entry — it is the load-bearing
    baseline every skill score divides by. A ValueError is raised early (rather than
    a confusing KeyError later) if it is missing, and a clear "no eligible forecasts"
    structure is returned for an empty panel instead of a ZeroDivisionError.

    ``score_origins`` (optional iterable of years) restricts which origin years are
    *scored*. When None (the default) all eligible origins in [ORIGIN_MIN, ORIGIN_MAX]
    are scored — the full backtest. When set, only those origins are scored, which
    makes a genuine OUT-OF-SAMPLE test possible: hold out the most recent origins
    (scored against the newest realized years) and confirm the verdict holds on data
    that did not influence the headline. Fitting stays leak-free regardless
    (`_history_at` reads only history <= T), so a held-out origin is scored against
    targets that never entered any fit.

    Leak-free by construction (the plan-for-peace adversarial finding): the predictive
    spread ``sigma`` and the climatology means are fitted, per origin year T, from ONLY
    the history a forecaster at T could see (outcomes realized by year <= T) — never
    from the future being scored. A constant summary sigma (the mean of the per-origin
    leak-free sigmas) is still reported for display, but every CRPS/Brier uses that
    origin's leak-free sigma. This does not change the v0 verdict ('nothing beats
    baseline'), but it removes the in-sample bias that would otherwise credit a v1
    model for leakage rather than skill.
    """
    if "no_change" not in models:
        raise ValueError("backtest() requires a 'no_change' baseline in models "
                         "(it is the denominator of every skill score).")
    score_set = set(score_origins) if score_origins is not None else None
    # gather eligible (series, origin T, realized outcome) cases.
    cases = []  # (series, iso, T, realized_delta)
    for iso, series in panel.items():
        for T in range(ORIGIN_MIN, ORIGIN_MAX + 1):
            if (score_set is None or T in score_set) and eligible(series, T):
                cases.append((series, iso, T, series[T + HORIZON] - series[T]))
    if not cases:
        # No eligible (country, origin) forecast — return an explicit empty result
        # instead of dividing by zero downstream. Callers treat n_forecasts == 0
        # as "nothing to score" (main() surfaces it via the cands guard below).
        return {"sigma": 0.0, "base_rate": 0.0, "n_forecasts": 0, "per_model": {}}

    # Leak-free per-origin fitting quantities (see _history_at). Climatology here is
    # GLOBAL (the panel-wide mean past delta by T); the per-country climatology and
    # AR(1) baselines are injected by main() via closures over the same helpers.
    origins = sorted({T for _, _, T, _ in cases})
    fit = {T: _history_at(panel, T) for T in origins}   # all_deltas, country_means, level_mean

    def sigma_at(T):
        return stdev(fit[T][0]) or 1e-6

    def climatology_at(T):
        ds = fit[T][0]
        return sum(ds) / len(ds) if ds else 0.0

    def per_country_climatology_at(iso, T):
        ds = _past_deltas_for(panel[iso], T)
        return sum(ds) / len(ds) if ds else climatology_at(T)

    # Inject the leak-free climatologies (global + per-country) and an AR(1)-on-level
    # baseline. With no-change (persistence) these are the stronger no-skill references
    # a real model must beat — predicting average drift is harder to beat than 0, a
    # per-country drift is harder still, and AR(1) is the standard time-series null.
    # The per-country baselines need `iso`, so they are scored via a name→callable
    # dispatch that takes (series, iso, T); ordinary models ignore iso.
    models = dict(models)
    models.setdefault("climatology", lambda series, T, _f=climatology_at: _f(T))
    # register the per-country climatology with a placeholder fn (its real body is the
    # dispatch entry below, which takes iso) so the scoring loop runs for it.
    models.setdefault("climatology_per_country", lambda series, T: 0.0)
    per_country_fns = {  # name -> fn(series, iso, T) for baselines needing the country id
        "climatology_per_country": lambda series, iso, T, _f=per_country_climatology_at: _f(iso, T),
    }

    per_model = {}
    for name, fn in models.items():
        crps_sum, brier_sum, rel_pairs = 0.0, 0.0, []
        pc = per_country_fns.get(name)
        for series, iso, T, y in cases:
            mu = pc(series, iso, T) if pc else fn(series, T)
            sig = sigma_at(T)
            crps_sum += crps_gaussian(mu, sig, y)
            p_decline = normal_cdf((-DELTA - mu) / sig)   # P(realized <= -DELTA)
            o = 1 if y <= -DELTA else 0
            brier_sum += brier(p_decline, o)
            rel_pairs.append((p_decline, o))
        n = len(cases)
        per_model[name] = {
            "crps": crps_sum / n, "brier": brier_sum / n,
            "reliability": reliability(rel_pairs),
        }
    # Capture the FULL-PRECISION baseline before the display-rounding loop runs:
    # `per_model["no_change"]` is iterated first, so rounding its crps/brier in place
    # (below) would otherwise become the denominator every later model divides by — an
    # alias-mutation bug that biased skills by the baseline's rounding (e.g. trend
    # crps_skill -0.5601 vs the correct -0.5602). Skill must use the unrounded baseline.
    base_crps = per_model["no_change"]["crps"]
    base_brier = per_model["no_change"]["brier"]
    for name, m in per_model.items():
        m["crps_skill"] = round(skill(m["crps"], base_crps), 4)
        m["brier_skill"] = round(skill(m["brier"], base_brier), 4)
        m["crps"] = round(m["crps"], 5)
        m["brier"] = round(m["brier"], 5)
    # reported sigma = mean of the per-origin leak-free sigmas (a summary, not the
    # value used per-case); base_rate is the realized decline fraction (descriptive).
    mean_sigma = sum(sigma_at(T) for T in origins) / len(origins)
    realized = [d for _, _, _, d in cases]
    base_rate = sum(1 for d in realized if d <= -DELTA) / len(realized)
    return {"sigma": round(mean_sigma, 4), "base_rate": round(base_rate, 4),
            "n_forecasts": len(cases), "per_model": per_model}


# ----------------------------------------------------------------------- I/O ----

def _load_panel(max_year=SNAP_MAX):
    """{iso3: {year: value}} for the annual V-Dem freedom-of-expression series.

    max_year caps the years kept (the backtest and the pin use 1990-2024). Scoring the
    forward registry needs the years after the pin, so it passes max_year=None. Until
    2026-10-31 the cap applied to live data too, so the registry could never be scored."""
    if _OFFLINE:
        with open(SNAPSHOT, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        cols = ("code", "year", "value")
    else:
        rows = fetch_utils.fetch_csv_rows(VDEM_URL, timeout=60)
        cols = ("code", "year", VDEM_COL)
    code_k, year_k, val_k = cols
    panel = {}
    for r in rows:
        code = (r.get(code_k) or "").strip()
        if not code or code.startswith("OWID"):
            continue
        try:
            year, val = int(r[year_k]), r.get(val_k)
        except (KeyError, ValueError):
            continue
        if val not in (None, "") and SNAP_MIN <= year and (max_year is None or year <= max_year):
            panel.setdefault(code, {})[year] = float(val)
    return panel


def write_snapshot():
    panel = _load_panel()  # live (this runs with _OFFLINE False)
    rows = [(iso, y, v) for iso, s in panel.items() for y, v in s.items()]
    os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
    with open(SNAPSHOT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["code", "year", "value"])
        for iso, y, v in sorted(rows):
            w.writerow([iso, y, v])
    print(f"wrote {os.path.relpath(SNAPSHOT)}  ({len(panel)} countries, {len(rows)} country-years)")


def main(argv=None):
    global _OFFLINE
    args = sys.argv[1:] if argv is None else argv
    if "--snapshot" in args:
        write_snapshot()
        return 0
    _OFFLINE = "--offline" in args or os.environ.get("SAA_OFFLINE") == "1"

    panel = _load_panel()
    # reversion's target = the leak-free cross-sectional LEVEL mean observable at T
    # (not the full-panel mean — that would be in-sample). A callable so make_reversion
    # resolves it per origin year.
    def level_mean_at(T):
        levels = [v for s in panel.values() for y, v in s.items() if y <= T]
        return sum(levels) / len(levels) if levels else 0.0
    models = {"no_change": f_no_change, "trend": f_trend,
              "damped_trend": f_damped_trend,
              "reversion": make_reversion(level_mean_at)}
    res = backtest(panel, models)

    # the honest verdict: did any candidate model beat ALL the no-skill baselines?
    # (no-change + global climatology + per-country climatology — the strongest
    #  leak-free references; a real model must clear the hardest of them.)
    BASELINES = ("no_change", "climatology", "climatology_per_country")
    cands = sorted(((n, m["crps_skill"]) for n, m in res["per_model"].items() if n not in BASELINES),
                   key=lambda kv: kv[1], reverse=True)
    if not cands:
        print("no candidate (non-baseline) models to evaluate — nothing to score.")
        return 0
    best_name, best_skill = cands[0]
    # the bar is the BEST baseline skill (a model must beat the strongest no-skill ref)
    best_baseline_skill = max(res["per_model"][b]["crps_skill"] for b in BASELINES
                              if b in res["per_model"])
    beats_all = best_skill > 0 and best_skill > best_baseline_skill
    verdict = ("BEATS every no-skill baseline (no-change, climatology, per-country)"
               if beats_all
               else "does NOT beat the no-change/climatology baselines (the honest, pre-registered result)")

    out = {
        "indicator_set": "Pharos-forecast v0 — backsliding backtest (V-Dem freedom of expression)",
        "mode": "offline-snapshot" if _OFFLINE else "live",
        # input provenance: the sha256 + source + fetch time of the pinned V-Dem snapshot
        # (DATA_CONTRACT §guarantees #2). Reads committed bytes so a swapped upstream
        # snapshot is detectable from this derived file alone.
        "input_provenance": fetch_utils.file_provenance(SNAPSHOT, VDEM_URL, SNAP_FETCHED_UTC),
        "pre_registered": {"horizon_years": HORIZON, "lookback": WINDOW, "delta": DELTA,
                           "origins": [ORIGIN_MIN, ORIGIN_MAX], "success_bar": SUCCESS_BAR},
        "scoring": "CRPS (Gneiting & Raftery 2007) + Brier (1950); skill vs no-change baseline",
        "result": res,
        "best_model": {"name": best_name, "crps_skill": best_skill},
        "verdict": verdict,
        "ethical_note": "Country/institution-level, retrodictive backtest — watch power, not people (NOTICE §7, THREAT_MODEL.md).",
        "license": {"code": "GPL-3.0-or-later", "data": "CC0-1.0",
                    "vdem": "CC BY 4.0 (V-Dem, processed by Our World in Data)"},
    }
    os.makedirs(DERIVED, exist_ok=True)
    with open(os.path.join(DERIVED, "forecast_backtest.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    with open(os.path.join(DERIVED, "forecast_backtest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "crps", "crps_skill", "brier", "brier_skill"])
        for name, m in res["per_model"].items():
            w.writerow([name, m["crps"], m["crps_skill"], m["brier"], m["brier_skill"]])

    print(f"Pharos-forecast v0 — {res['n_forecasts']} pre-registered forecasts, "
          f"sigma={res['sigma']}, decline base-rate={res['base_rate']}")
    for name, m in res["per_model"].items():
        print(f"  {name:<14} CRPS={m['crps']:.4f} (skill {m['crps_skill']:+.3f})  "
              f"Brier={m['brier']:.4f} (skill {m['brier_skill']:+.3f})")
    print(f"  VERDICT: best is '{best_name}' — {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
