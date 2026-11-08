#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Forward prediction registry — turn "we can't beat baseline" into an actively-tested claim.

The committed backtest is retrodictive: it scores past forecasts against realized outcomes.
That is honest but static. This registry records **dated, frozen forecasts made NOW** from the
latest pinned data (2024), to be scored LATER when new V-Dem data realizes. It is the
pre-registration that makes the project's forecasting pillar genuinely falsifiable going
forward, not just in hindsight.

Design (falsifiability-first, watch-power-not-people):
- For every country with enough history, emit a probabilistic forecast of the change in
  V-Dem freedom-of-expression over SHORT, scoreable horizons (1 and 3 years) from 2024.
- The model is the leak-free climatology/no-change posture the backtest showed is the honest
  bar: predict no change (the baseline that beat everything), with the leak-free spread.
- Each forecast carries a frozen timestamp, the input sha256 (so it can't be silently re-fit),
  and a pre-registered scoring rule (CRPS + Brier on the decline event, same as the backtest).
- A `--score` mode scores a registry against a newer panel once outcomes realize.

This does NOT ship a hero call (the R6 reflexivity fix). It ships a *measurable, time-stamped
commitment* that the honest "no-change is the best forecast" posture will be tested against the
real future, in the open, on a fixed cadence. Stdlib only; offline from the pinned snapshot.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
from datetime import date, timezone, datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import pharos_forecast as pf  # noqa: E402
import fetch_utils  # noqa: E402

# Short, scoreable horizons (not the backtest's 10yr — those won't realize for a decade).
HORIZONS = (1, 3)
ORIGIN_YEAR = 2024   # the latest pinned year; forecasts are of (2024+H)
DERIVED = os.path.normpath(os.path.join(_HERE, "..", "..", "data", "derived"))
REGISTRY_PATH = os.path.join(DERIVED, "prediction_registry.json")
SCORES_PATH = os.path.join(DERIVED, "prediction_registry_scores.json")
SNAPSHOTS = os.path.normpath(os.path.join(_HERE, "..", "..", "data", "snapshots"))


def _forecast_one(series, horizon, sigma, panel_hist_mean):
    """A leak-free probabilistic forecast of series[ORIGIN+horizon] - series[ORIGIN].

    Model = the honest baseline (no-change), with the leak-free spread sigma. We also
    emit the climatology point (panel historical mean drift) for transparency, but the
    registry's scored forecast is no-change — the bar the backtest set."""
    mu = 0.0   # no-change: the baseline that beat every model in the backtest
    clim = panel_hist_mean  # the global climatology point, recorded for reference
    # P(decline) = P(realized <= -DELTA) under N(mu, sigma)
    p_decline = pf.normal_cdf((-pf.DELTA - mu) / sigma) if sigma > 0 else (1.0 if mu <= -pf.DELTA else 0.0)
    return {"horizon_years": horizon, "target_year": ORIGIN_YEAR + horizon,
            "mu": round(mu, 5), "sigma": round(sigma, 5), "climatology_mu": round(clim, 5),
            "p_decline_event": round(p_decline, 4)}


def build_registry(panel):
    """Build dated forecasts for every country with a 2024 value. Leak-free sigma from
    the history observable at 2024 (no future data)."""
    # global leak-free sigma from past 1-year changes realized by 2024
    one_yr_deltas = []
    for series in panel.values():
        for a in range(pf.SNAP_MIN, ORIGIN_YEAR):
            if a in series and (a + 1) in series:
                one_yr_deltas.append(series[a + 1] - series[a])
    sigma1 = pf.stdev(one_yr_deltas) or 1e-6
    # 3yr sigma from past 3-year changes
    three_yr_deltas = []
    for series in panel.values():
        for a in range(pf.SNAP_MIN, ORIGIN_YEAR - 2):
            if a in series and (a + 3) in series:
                three_yr_deltas.append(series[a + 3] - series[a])
    sigma3 = pf.stdev(three_yr_deltas) or 1e-6
    panel_hist_mean = sum(one_yr_deltas) / len(one_yr_deltas) if one_yr_deltas else 0.0

    forecasts = {}
    for iso, series in sorted(panel.items()):
        if ORIGIN_YEAR not in series:
            continue
        forecasts[iso] = {
            "country": iso, "origin_year": ORIGIN_YEAR, "origin_value": round(series[ORIGIN_YEAR], 4),
            "horizons": {
                1: _forecast_one(series, 1, sigma1, panel_hist_mean),
                3: _forecast_one(series, 3, sigma3, panel_hist_mean),
            },
        }
    return forecasts, {"sigma_1yr": round(sigma1, 5), "sigma_3yr": round(sigma3, 5),
                       "panel_hist_mean_1yr": round(panel_hist_mean, 5),
                       "n_countries": len(forecasts)}


def score_registry(registry, realized_panel, clim_mu=None):
    """Score a registry against realized outcomes. Returns per-horizon CRPS/Brier for the
    scored no-change forecast and, for reference, for the climatology point the registry
    recorded (same spread), plus how much the source revised the origin-year values.
    Only countries with a realized value at target_year are scored."""
    results = {}
    for h in HORIZONS:
        target = ORIGIN_YEAR + h
        if not any(target in s for s in realized_panel.values()):
            results[h] = {"scored": 0, "note": f"no realized data at {target} yet"}
            continue
        crps_sum = brier_sum = crps_clim = brier_clim = 0.0
        n = declines = 0
        revisions = []
        for iso, fc in registry["forecasts"].items():
            s = realized_panel.get(iso)
            if not s or target not in s or fc["origin_year"] not in s:
                continue
            # The change is taken inside the newer release (both years from the same vintage),
            # so a revision of the origin value is not counted as a forecast error.
            y = s[target] - s[fc["origin_year"]]
            # horizons keys are int in memory, str after JSON round-trip — accept either
            fh = fc["horizons"].get(str(h)) or fc["horizons"].get(h)
            if not fh:
                continue
            o = 1 if y <= -pf.DELTA else 0
            crps_sum += pf.crps_gaussian(fh["mu"], fh["sigma"], y)
            brier_sum += pf.brier(fh["p_decline_event"], o)
            c_mu = (clim_mu or {}).get(h, fh.get("climatology_mu", 0.0))
            p_clim = (pf.normal_cdf((-pf.DELTA - c_mu) / fh["sigma"]) if fh["sigma"] > 0
                      else float(c_mu <= -pf.DELTA))
            crps_clim += pf.crps_gaussian(c_mu, fh["sigma"], y)
            brier_clim += pf.brier(p_clim, o)
            declines += o
            if "origin_value" in fc:
                revisions.append(abs(s[fc["origin_year"]] - fc["origin_value"]))
            n += 1
        r = {"scored": n, "target_year": target,
             "crps": round(crps_sum / n, 5) if n else None,
             "brier": round(brier_sum / n, 5) if n else None,
             "crps_climatology": round(crps_clim / n, 5) if n else None,
             "brier_climatology": round(brier_clim / n, 5) if n else None,
             "decline_events": declines}
        if n:
            if clim_mu and h in clim_mu:
                used = clim_mu[h]
            else:
                first = next(iter(registry["forecasts"].values()), {})
                hz = first.get("horizons", {})
                used = (hz.get(str(h)) or hz.get(h) or {}).get("climatology_mu", 0.0)
            r["climatology_mu"] = round(used, 5)
        if n and crps_clim > 0:
            # > 0: no-change beat the climatology point on this realization; < 0: it did not.
            r["crps_skill_vs_climatology"] = round(1.0 - crps_sum / crps_clim, 4)
        if revisions:
            r["origin_revision_mean_abs"] = round(sum(revisions) / len(revisions), 5)
            r["origin_revision_max_abs"] = round(max(revisions), 5)
        results[h] = r
    return results


def leakfree_climatology(registry):
    """{h: mean h-year change} from the pinned input the registry was issued from (changes that
    ended by the origin year). None when that pin no longer matches the registry's recorded hash,
    in which case scoring falls back to the 1-year drift the registry recorded."""
    want = (registry.get("input_provenance") or {}).get("input_sha256")
    if not want or not os.path.exists(pf.SNAPSHOT) or fetch_utils.sha256_file(pf.SNAPSHOT) != want:
        return None
    panel = _load_pinned(pf.SNAPSHOT)
    out = {}
    for h in HORIZONS:
        deltas = [s[a + h] - s[a] for s in panel.values() for a in range(pf.SNAP_MIN, ORIGIN_YEAR - h + 1)
                  if a in s and (a + h) in s]
        out[h] = sum(deltas) / len(deltas) if deltas else 0.0
    return out


def first_public(target_year):
    """V-Dem publishes once a year, in March, with data through the previous year (an assumption
    about the source's schedule, stated so the "prospective" flag can be checked)."""
    return f"{target_year + 1}-03-01"


def vintage_vs_pin(panel):
    """Compare the realized panel with the June 2026 pin on every year both hold (<= the cap)."""
    pinned = _load_pinned(pf.SNAPSHOT) if os.path.exists(pf.SNAPSHOT) else {}
    diffs, n = [], 0
    for iso, s in pinned.items():
        for y, v in s.items():
            if y in panel.get(iso, {}):
                n += 1
                if abs(panel[iso][y] - v) > 0:
                    diffs.append(abs(panel[iso][y] - v))
    return {"compared": n, "differing": len(diffs), "max_abs_diff": round(max(diffs), 5) if diffs else 0.0}


def _panel_csv(panel):
    rows = ["code,year,value"]
    for iso in sorted(panel):
        for y in sorted(panel[iso]):
            rows.append(f"{iso},{y},{panel[iso][y]}")
    return ("\r\n".join(rows) + "\r\n").encode("utf-8")


def _load_pinned(path):
    panel = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            panel.setdefault(r["code"], {})[int(r["year"])] = float(r["value"])
    return panel


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    pf._OFFLINE = "--live" not in args

    if "--score" in args:
        # Score the committed registry once its target years have realized. The pinned
        # forecast snapshot stops at the origin year, so a score needs either a fresh pull
        # (--live, which pins what it used) or an earlier pinned realization (--panel PATH).
        if not os.path.exists(REGISTRY_PATH):
            print("prediction-registry: no registry to score — run without --score first.")
            return 2
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            registry = json.load(f)
        history = {"scorings": []}
        if os.path.exists(SCORES_PATH):
            with open(SCORES_PATH, encoding="utf-8") as f:
                history = json.load(f)
        if "--panel" in args:
            path = args[args.index("--panel") + 1]
            panel = _load_pinned(path)
            sha = fetch_utils.sha256_file(path)
            live = False
        elif "--live" in args:
            panel = pf._load_panel(max_year=None)
            sha = "sha256:" + __import__("hashlib").sha256(_panel_csv(panel)).hexdigest()
            path, live = None, True
        else:
            print("prediction-registry: the pinned snapshot ends at the origin year, so nothing can be "
                  "scored from it. Use --live (fetch the newest release and pin it) or --panel PATH.")
            return 2
        covered = sum(1 for iso in registry["forecasts"] if ORIGIN_YEAR in panel.get(iso, {}))
        if covered < len(registry["forecasts"]) // 2:
            print(f"prediction-registry: the realized panel has the origin year for only {covered} of "
                  f"{len(registry['forecasts'])} registry countries (schema change or failed fetch?) — "
                  "nothing written.")
            return 1
        clim = leakfree_climatology(registry)
        results = score_registry(registry, panel, clim_mu=clim)
        for h, r in results.items():
            if r.get("scored"):
                r["prospective"] = registry.get("issued", "") < first_public(r["target_year"])
                r["climatology_source"] = ("leak-free mean change over the same horizon, from the pinned input "
                                           "the registry was issued from" if clim else
                                           "the 1-year drift the registry recorded (its pinned input changed)")
        print(f"prediction-registry (issued {registry.get('issued')}) scored on {date.today()}:")
        for h, r in results.items():
            print(f"  horizon {h}yr ({r.get('target_year')}): {r}")
        if not any(r.get("scored") for r in results.values()):
            print("  nothing has realized yet — no record written.")
            return 0
        results_out = {str(h): r for h, r in results.items()}
        same = [s for s in history.get("scorings", []) if s.get("realized_input", {}).get("input_sha256") == sha]
        if same:
            rec = same[-1]
            if rec.get("results") != results_out:
                print("  WARNING: same input, different results — the scoring code changed; results updated.")
                rec["results"] = results_out
                rec["rescored_on"] = date.today().isoformat()
            if live:
                rec["last_confirmed"] = date.today().isoformat()
        else:
            fetched = datetime.now(timezone.utc).isoformat(timespec="seconds") if live else "unknown"
            if live:
                path = os.path.join(SNAPSHOTS, f"vdem_freexp_realized_{fetched[:10]}_{sha[7:15]}.csv")
                if not os.path.exists(path):
                    os.makedirs(SNAPSHOTS, exist_ok=True)
                    with open(path, "wb") as f:
                        f.write(_panel_csv(panel))
                print(f"  pinned the realization used: {os.path.relpath(path)}")
            rec = {"registry_issued": registry.get("issued"), "scored_on": date.today().isoformat(),
                   "realized_input": {"source_url": pf.VDEM_URL, "fetched_utc": fetched,
                                      "input_sha256": sha, "path": os.path.relpath(path, os.path.join(_HERE, "..", ".."))},
                   "vintage_vs_pin": vintage_vs_pin(panel),
                   "results": results_out}
            history.setdefault("scorings", []).append(rec)
        history["note"] = ("Scores of the frozen forward registry. The scored forecast is no-change. The "
                           "climatology columns score a reference point with the same spread: the leak-free "
                           "mean change over the same horizon, from the pinned input the registry was issued "
                           "from. A result is prospective only if the source published the target year after "
                           "the registry's issue date (V-Dem publishes each March with data through the "
                           "previous year); otherwise it is blind but retrospective. vintage_vs_pin compares "
                           "the realized panel with the June 2026 pin on every year both hold.")
        with open(SCORES_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
            f.write("\n")
        print(f"  wrote {os.path.relpath(SCORES_PATH)}")
        return 0

    if os.path.exists(REGISTRY_PATH) and "--reissue" not in args:
        # The issue date is what the blind/forward claims rest on: never overwrite it by accident.
        print("prediction-registry: a frozen registry already exists — refusing to re-issue it. "
              "Pass --reissue to issue a new one deliberately, or score it with `make score` "
              "(--score --live, or --score --panel PATH).")
        return 2

    panel = pf._load_panel()
    forecasts, fit = build_registry(panel)
    registry = {
        "test": "pharos forward prediction registry — dated, frozen, falsifiable forecasts",
        "issued": date.today().isoformat(),
        "issued_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "origin_year": ORIGIN_YEAR,
        "horizons": list(HORIZONS),
        "model": "no-change baseline (the bar the backtest set) with leak-free spread; "
                 "climatology point recorded for reference, not scored as a hero call",
        "scoring_rule": "CRPS (Gneiting&Raftery 2007) + Brier on the decline event (Δ<=-0.05); "
                        "score with: make score (python3 src/forecast/prediction_registry.py --score --live, "
                        "or --score --panel PATH)",
        "input_provenance": fetch_utils.file_provenance(pf.SNAPSHOT, pf.VDEM_URL, pf.SNAP_FETCHED_UTC),
        "fit": fit,
        "ethical_note": "Country/institution-level probabilistic forecasts — watch power, not "
                        "people (NOTICE §7, THREAT_MODEL.md). No hero call, by design (R6).",
        "forecasts": forecasts,
    }
    os.makedirs(DERIVED, exist_ok=True)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
        f.write("\n")
    print(f"prediction-registry — issued {registry['issued']}: {len(forecasts)} countries × "
          f"{len(HORIZONS)} horizons (targets {[ORIGIN_YEAR + h for h in HORIZONS]})")
    print(f"  model: no-change baseline (σ₁={fit['sigma_1yr']}, σ₃={fit['sigma_3yr']})")
    print("  score later with: make score (or --score --live / --score --panel PATH)")
    print(f"  wrote {os.path.relpath(REGISTRY_PATH)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
