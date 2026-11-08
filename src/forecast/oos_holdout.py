#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Out-of-sample hold-out test for the pharos-forecast verdict.

The committed backtest scores every origin in [2000, 2014]. The honest verdict —
"nothing beats the no-change baseline" — is therefore over the *full* window, and a
skeptic's fair question is: **does it hold on years the headline never touched?**

This holds out the most recent origins (2012, 2013, 2014 — scored against the newest
realized country-years, 2022/2023/2024) and re-runs the leak-free `backtest` on ONLY
those origins. Because fitting is already leak-free (sigma/climatology read only
history <= T), these held-out targets never entered any fit: this is a genuine
out-of-sample test of the negative result, not a reshuffle of the in-sample window.

It writes a dated result to ``data/derived/oos_holdout.json`` (CC0) and prints the
verdict. Run with ``python3 src/forecast/oos_holdout.py`` (offline by default, from
the pinned snapshot; ``--live`` to fetch). Stdlib only.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import pharos_forecast as pf  # noqa: E402

# The hold-out set: the three most recent scored origins. Each is scored against a
# realized year (2022/2023/2024) that the headline backtest also scores, but here
# ONLY these origins contribute — so the verdict is tested on the newest data alone.
HOLDOUT_ORIGINS = (2012, 2013, 2014)
DERIVED = os.path.normpath(os.path.join(_HERE, "..", "..", "data", "derived"))


def run_holdout(panel):
    """Run the leak-free backtest on ONLY the held-out origins. Returns (result, models)."""
    def level_mean_at(T):
        levels = [v for s in panel.values() for y, v in s.items() if y <= T]
        return sum(levels) / len(levels) if levels else 0.0
    models = {"no_change": pf.f_no_change, "trend": pf.f_trend,
              "damped_trend": pf.f_damped_trend, "reversion": pf.make_reversion(level_mean_at)}
    res = pf.backtest(panel, models, score_origins=HOLDOUT_ORIGINS)
    return res, models


def verdict(res):
    """The honest verdict on the held-out years: does any candidate beat the baselines?"""
    BASELINES = ("no_change", "climatology", "climatology_per_country")
    cands = {n: m["crps_skill"] for n, m in res["per_model"].items() if n not in BASELINES}
    if not cands:
        return {"holds": None, "reason": "no candidate models on the hold-out"}
    best_name, best_skill = max(cands.items(), key=lambda kv: kv[1])
    best_baseline = max((res["per_model"][b]["crps_skill"] for b in BASELINES
                         if b in res["per_model"]), default=0.0)
    holds = not (best_skill > 0 and best_skill > best_baseline)
    return {"holds": holds,
            "best_candidate": best_name, "best_candidate_skill": best_skill,
            "best_baseline_skill": best_baseline,
            "reason": ("nothing beats the baselines on the held-out years — verdict holds"
                       if holds else
                       f"{best_name} BEATS the baselines out-of-sample (skill {best_skill}) — "
                       "the negative verdict does NOT generalize; investigate")}


def main(argv=None):
    pf._OFFLINE = "--live" not in (argv or sys.argv[1:])
    panel = pf._load_panel()
    res, _ = run_holdout(panel)
    if res["n_forecasts"] == 0:
        print("oos-holdout: no eligible forecasts on the held-out origins.")
        return 0
    v = verdict(res)

    out = {
        "test": "pharos-forecast out-of-sample hold-out (leak-free)",
        "run_date": date.today().isoformat(),
        "holdout_origins": list(HOLDOUT_ORIGINS),
        "n_forecasts": res["n_forecasts"],
        "sigma": res["sigma"],
        "base_rate": res["base_rate"],
        "per_model": res["per_model"],
        "verdict": v,
        "note": ("The committed backtest's negative verdict, re-tested on ONLY the three "
                 "most recent origins (2012/2013/2014, scored against 2022/2023/2024). "
                 "Fitting is leak-free, so these held-out targets never entered any fit."),
    }
    os.makedirs(DERIVED, exist_ok=True)
    path = os.path.join(DERIVED, "oos_holdout.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"oos-holdout — {res['n_forecasts']} forecasts on origins {HOLDOUT_ORIGINS} "
          f"(σ={res['sigma']}, decline base-rate={res['base_rate']})")
    for name, m in res["per_model"].items():
        print(f"  {name:<22} CRPS={m['crps']:.4f} (skill {m['crps_skill']:+.3f})")
    tag = "HOLDS out-of-sample" if v["holds"] else "FAILS out-of-sample"
    print(f"  VERDICT: negative result {tag} — {v['reason']}")
    print(f"  wrote {os.path.relpath(path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
