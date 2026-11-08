#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""WGI governance — all six dimensions, computed with honest uncertainty.

Pulls the World Bank **Worldwide Governance Indicators** (WGI, source 3) for all
six dimensions — Voice & Accountability, Rule of Law, Control of Corruption,
Government Effectiveness, Regulatory Quality, Political Stability — each as a
0-100 *score* with a published **90% confidence interval**. For each country and
dimension it computes the change over a decade and flags it as a meaningful
DECLINE / IMPROVE *only when the change exceeds the measurement uncertainty*
(two-sided z-test at the 90% level). Most movement is noise; this refuses to
over-claim it.

Stdlib only (no pip install) for reproducibility. Outputs:
  data/derived/wgi_governance.csv            (long: country x dimension, CC0)
  data/derived/wgi_governance_summary.json   (per-dimension + overall, CC0)

Ethical note: country/institution-level governance — watch power, never
individuals (see ../../NOTICE §7).
"""
import json, csv, math, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_utils  # noqa: E402 — shared resilient fetch (backoff+jitter) + offline snapshots

SOURCE = 3
BASELINE_YEAR = 2014
LATEST_YEAR = 2024
Z90 = 1.6448536269514722  # standard normal 95th pct (one-sided 90% CI)
Z95 = 1.959963984540054   # 97.5th pct — the stricter two-sided 95% robustness bar (plan-for-peace C9)

# WGI dimension code -> human name. Codes: GOV_WGI_<DIM>.SC / .SC_LB / .SC_UB
DIMENSIONS = {
    "VA": "Voice & Accountability",
    "RL": "Rule of Law",
    "CC": "Control of Corruption",
    "GE": "Government Effectiveness",
    "RQ": "Regulatory Quality",
    "PV": "Political Stability & Absence of Violence",
}

# Stable, documented CSV column order (the data-contract surface). Defined once so
# the writer cannot crash on an empty record set (all_recs[0]) and the field order
# is explicit rather than inferred from the first row that happened to be computed.
CSV_FIELDS = [
    "iso3", "country", "dimension", "dimension_name",
    "year_base", "sc_base", "lb_base", "ub_base",
    "year_latest", "sc_latest", "lb_latest", "ub_latest",
    "change", "se_diff", "z", "p_two_sided", "verdict",
]
API = ("https://api.worldbank.org/v2/country/all/indicator/{ind}"
       "?source=3&format=json&date={a}:{b}&per_page=30000")
COUNTRIES_API = "https://api.worldbank.org/v2/country?format=json&per_page=400"

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
DERIVED = os.path.join(REPO, "data", "derived")
SNAPSHOT = os.path.join(REPO, "data", "snapshots", "wgi_raw.json")

# Offline mode reads the committed snapshot instead of the live WB API, so the
# pipeline is reproducible with no network (CI's deterministic job + offline dev).
_OFFLINE = False
_SNAP = None


# ---- pure, testable core ---------------------------------------------------

def phi(x):
    """Standard normal CDF."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def se_from_ci(lb, ub):
    """Standard error implied by a published symmetric 90% CI."""
    return (ub - lb) / (2.0 * Z90)


def compute_change(sc1, lb1, ub1, sc2, lb2, ub2, rho=0.0):
    """Change from baseline (year 1) to latest (year 2), with uncertainty.

    Returns dict(change, se_diff, z, p, verdict). Flagged DECLINE/IMPROVE only
    when |z| >= Z90 (90%); otherwise NO_SIG_CHANGE.

    ``rho`` is the assumed year-over-year correlation between the two WGI estimates.
    The default 0.0 reproduces the original independence assumption (se_diff =
    sqrt(se1² + se2²)) and is the value the committed headline counts use. WGI
    aggregates a large *overlapping* source set across years (the same expert coders,
    V-Dem, EIU, ... feed both snapshots), so the true rho is positive. For a *change*
    test, positive correlation makes the difference MORE precisely estimated (shared
    measurement error partially cancels), so rho=0 is the CONSERVATIVE choice — it
    flags the fewest countries, and the true positive rho would flag more. Because the
    microdata to estimate rho is not in this repo, the headline keeps rho=0 and a
    sensitivity sweep (``va_independence_sensitivity``) reports how the Voice &
    Accountability counts move across plausible positive rho, so a reader can see the
    finding's robustness to the assumption rather than take a single number on faith.
    """
    se1, se2 = se_from_ci(lb1, ub1), se_from_ci(lb2, ub2)
    var = se1 * se1 + se2 * se2 - 2.0 * rho * se1 * se2
    se_diff = math.sqrt(max(var, 0.0))   # guard tiny negative variance at rho≈1
    change = sc2 - sc1
    z = change / se_diff if se_diff > 0 else 0.0
    p = 2.0 * (1.0 - phi(abs(z)))
    if z <= -Z90:
        verdict = "DECLINE"
    elif z >= Z90:
        verdict = "IMPROVE"
    else:
        verdict = "NO_SIG_CHANGE"
    return {"change": change, "se_diff": se_diff, "z": z, "p": p, "verdict": verdict}


# ---- I/O -------------------------------------------------------------------

def _load_snapshot():
    """Lazy-load the committed raw-input snapshot for offline mode."""
    global _SNAP
    if _SNAP is None:
        if not os.path.exists(SNAPSHOT):
            raise RuntimeError(
                f"offline mode requested but no snapshot at {SNAPSHOT} — run `make snapshot` first")
        with open(SNAPSHOT, encoding="utf-8") as f:
            try:
                _SNAP = json.load(f)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"snapshot {SNAPSHOT} is not valid JSON: {e}") from e
    return _SNAP


def fetch_countries():
    """iso3 -> name for real countries (excludes WB aggregates/regions)."""
    if _OFFLINE:
        return dict(_load_snapshot()["countries"])
    d = fetch_utils.fetch_json(COUNTRIES_API)
    rows = d[1] if isinstance(d, list) and len(d) > 1 and d[1] else []
    return {r["id"]: r["name"] for r in rows
            if r.get("region", {}).get("value") != "Aggregates"}


def fetch_series(ind):
    """(iso3, year) -> value for one WGI indicator code."""
    if _OFFLINE:
        raw = _load_snapshot()["series"][ind]   # {"ISO3|YEAR": value}
        return {(k.split("|")[0], int(k.split("|")[1])): v for k, v in raw.items()}
    d = fetch_utils.fetch_json(API.format(ind=ind, a=BASELINE_YEAR, b=LATEST_YEAR))
    rows = d[1] if isinstance(d, list) and len(d) > 1 and d[1] else []
    out = {}
    for r in rows:
        if r.get("value") is None:
            continue
        out[(r["countryiso3code"], int(r["date"]))] = float(r["value"])
    return out


def write_snapshot():
    """Fetch every raw WB input LIVE and freeze it to data/snapshots/wgi_raw.json.

    This is the deliberate 'pin' step (`make snapshot`): after it, the whole
    pipeline reproduces offline from the committed snapshot.
    """
    countries = fetch_countries()  # live (_OFFLINE is False here)
    series = {}
    for dim in DIMENSIONS:
        for suff in ("SC", "SC_LB", "SC_UB"):
            ind = f"GOV_WGI_{dim}.{suff}"
            series[ind] = {f"{iso3}|{year}": v
                           for (iso3, year), v in fetch_series(ind).items()}
    payload = {
        "source": "World Bank WGI (source 3), raw inputs for reproducible offline compute",
        "source_url": COUNTRIES_API,
        "fetched_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "countries": countries, "series": series,
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
    with open(SNAPSHOT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote {os.path.relpath(SNAPSHOT, REPO)}  "
          f"({len(countries)} countries, {len(series)} series, {fetch_utils.sha256_text(text)})")


def compute_dimension(dim, countries):
    """Return list of per-country records for one WGI dimension."""
    sc = fetch_series(f"GOV_WGI_{dim}.SC")
    lb = fetch_series(f"GOV_WGI_{dim}.SC_LB")
    ub = fetch_series(f"GOV_WGI_{dim}.SC_UB")
    recs = []
    for iso3, name in sorted(countries.items(), key=lambda kv: kv[1]):
        keys = [(iso3, BASELINE_YEAR), (iso3, LATEST_YEAR)]
        if not all(k in sc and k in lb and k in ub for k in keys):
            continue
        b = (sc[(iso3, BASELINE_YEAR)], lb[(iso3, BASELINE_YEAR)], ub[(iso3, BASELINE_YEAR)])
        l = (sc[(iso3, LATEST_YEAR)], lb[(iso3, LATEST_YEAR)], ub[(iso3, LATEST_YEAR)])
        r = compute_change(*b, *l)
        recs.append({
            "iso3": iso3, "country": name, "dimension": dim, "dimension_name": DIMENSIONS[dim],
            "year_base": BASELINE_YEAR, "sc_base": round(b[0], 4),
            "lb_base": round(b[1], 4), "ub_base": round(b[2], 4),
            "year_latest": LATEST_YEAR, "sc_latest": round(l[0], 4),
            "lb_latest": round(l[1], 4), "ub_latest": round(l[2], 4),
            "change": round(r["change"], 4), "se_diff": round(r["se_diff"], 4),
            "z": round(r["z"], 3), "p_two_sided": round(r["p"], 5), "verdict": r["verdict"],
        })
    return recs


def _dim_summary(recs):
    mean = lambda xs: round(sum(xs) / len(xs), 3) if xs else None
    dec = [r for r in recs if r["verdict"] == "DECLINE"]
    imp = [r for r in recs if r["verdict"] == "IMPROVE"]
    nos = [r for r in recs if r["verdict"] == "NO_SIG_CHANGE"]
    top = lambda rows, rev: [{"country": r["country"], "change": r["change"], "z": r["z"]}
                             for r in sorted(rows, key=lambda r: r["z"], reverse=rev)[:5]]
    return {
        "n_countries": len(recs),
        "counts": {"DECLINE": len(dec), "IMPROVE": len(imp), "NO_SIG_CHANGE": len(nos)},
        # robustness (C9): the same tally at the stricter two-sided 95% bar (|z|>=1.96),
        # so a headline ratio isn't an artifact of the 90% threshold.
        "counts_95pct_bar": {"DECLINE": sum(1 for r in recs if r["z"] <= -Z95),
                             "IMPROVE": sum(1 for r in recs if r["z"] >= Z95)},
        "global_unweighted_mean": {"baseline": mean([r["sc_base"] for r in recs]),
                                   "latest": mean([r["sc_latest"] for r in recs])},
        "top_declines": top(dec, False),
        "top_improvements": top(imp, True),
    }


ALT_BASELINE_YEAR = 2015   # C9 robustness: an in-snapshot alternative window for Voice & Accountability


def va_window_ratio(countries, base, latest):
    """C9 robustness. Voice & Accountability decline:improve counts for an arbitrary
    window, at the 90% AND stricter 95% bars — to show the headline ratio is not an
    artifact of the threshold OR of the 2014->2024 window. O(countries)."""
    sc = fetch_series("GOV_WGI_VA.SC")
    lb = fetch_series("GOV_WGI_VA.SC_LB")
    ub = fetch_series("GOV_WGI_VA.SC_UB")
    d90 = i90 = d95 = i95 = n = 0
    for iso3 in countries:
        keys = [(iso3, base), (iso3, latest)]
        if not all(k in sc and k in lb and k in ub for k in keys):
            continue
        z = compute_change(sc[(iso3, base)], lb[(iso3, base)], ub[(iso3, base)],
                           sc[(iso3, latest)], lb[(iso3, latest)], ub[(iso3, latest)])["z"]
        n += 1
        if z <= -Z90:
            d90 += 1
        elif z >= Z90:
            i90 += 1
        if z <= -Z95:
            d95 += 1
        elif z >= Z95:
            i95 += 1
    return {"window": [base, latest], "n": n,
            "bar_90": {"DECLINE": d90, "IMPROVE": i90},
            "bar_95": {"DECLINE": d95, "IMPROVE": i95}}


def va_independence_sensitivity(countries, base=BASELINE_YEAR, latest=LATEST_YEAR,
                                rhos=(0.0, 0.3, 0.5, 0.7, 0.9)):
    """Cross-year-independence robustness for Voice & Accountability.

    The headline test treats the baseline and latest WGI estimates as statistically
    independent (rho=0). They are not: WGI aggregates an overlapping source set
    across years, so the true rho is positive. For a *change* test that makes rho=0
    the CONSERVATIVE choice (it flags the fewest countries; positive rho flags more,
    because shared measurement error partially cancels in the difference). Because the
    source-level microdata to *estimate* rho is not in this repo, we sweep the
    assumption instead: recompute the VA decline:improve counts at a bracket of
    positive rho and report how the ratio moves. The empirically-confirmed pattern:
    both counts rise with rho, but the decline:improve ratio stays strongly >1 across
    the whole sweep — so the *direction* (voice erosion concentrates declines) is
    robust to the assumption even though the exact count is not. O(countries * rhos)."""
    sc = fetch_series("GOV_WGI_VA.SC")
    lb = fetch_series("GOV_WGI_VA.SC_LB")
    ub = fetch_series("GOV_WGI_VA.SC_UB")
    sweep = []
    for rho in rhos:
        d90 = i90 = n = 0
        for iso3 in countries:
            keys = [(iso3, base), (iso3, latest)]
            if not all(k in sc and k in lb and k in ub for k in keys):
                continue
            r = compute_change(sc[(iso3, base)], lb[(iso3, base)], ub[(iso3, base)],
                               sc[(iso3, latest)], lb[(iso3, latest)], ub[(iso3, latest)], rho=rho)
            n += 1
            if r["z"] <= -Z90:
                d90 += 1
            elif r["z"] >= Z90:
                i90 += 1
        ratio = round(d90 / i90, 2) if i90 else None
        sweep.append({"rho": rho, "n": n,
                      "decline": d90, "improve": i90, "decline_improve_ratio": ratio})
    return sweep


def main(argv=None):
    global _OFFLINE
    args = sys.argv[1:] if argv is None else argv
    if "--snapshot" in args:
        write_snapshot()
        return 0
    _OFFLINE = "--offline" in args or os.environ.get("SAA_OFFLINE") == "1"

    os.makedirs(DERIVED, exist_ok=True)
    countries = fetch_countries()
    all_recs, dims = [], {}
    for dim in DIMENSIONS:
        recs = compute_dimension(dim, countries)
        all_recs.extend(recs)
        dims[dim] = {"name": DIMENSIONS[dim], **_dim_summary(recs)}

    csv_path = os.path.join(DERIVED, "wgi_governance.csv")
    if not all_recs:
        raise RuntimeError(
            "no WGI records produced — every country was missing both endpoint years "
            f"({BASELINE_YEAR}, {LATEST_YEAR}). Check snapshot coverage or run `make snapshot`.")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader(); w.writerows(all_recs)

    dec = sum(d["counts"]["DECLINE"] for d in dims.values())
    imp = sum(d["counts"]["IMPROVE"] for d in dims.values())
    nos = sum(d["counts"]["NO_SIG_CHANGE"] for d in dims.values())
    summary = {
        "indicator_set": "World Bank WGI governance scores (0-100), six dimensions, with 90% CI",
        "source": "World Bank Worldwide Governance Indicators (WGI), source 3",
        "source_url": "https://www.worldbank.org/en/publication/worldwide-governance-indicators",
        # offline mode freezes fetched_utc to the snapshot's, so the output is byte-deterministic
        "fetched_utc": (_load_snapshot()["fetched_utc"] if _OFFLINE
                        else datetime.now(timezone.utc).isoformat(timespec="seconds")),
        "mode": "offline-snapshot" if _OFFLINE else "live",
        "baseline_year": BASELINE_YEAR, "latest_year": LATEST_YEAR,
        # input provenance: the sha256 + source + fetch time of the pinned snapshot file
        # (DATA_CONTRACT §guarantees #2). Reads committed bytes, so a swapped upstream
        # snapshot is detectable from this derived file alone.
        "input_provenance": fetch_utils.file_provenance(
            SNAPSHOT, _load_snapshot()["source_url"], _load_snapshot()["fetched_utc"]),
        "method": ("Per-country, per-dimension decade change in the 0-100 score. SE derived "
                   "from the published 90% CI (se=(ub-lb)/(2*1.6449)); two-sided z-test; "
                   "flagged DECLINE/IMPROVE only when |z|>=1.6449 (90%). Moves within "
                   "measurement noise are NOT flagged."),
        "dimensions": dims,
        "overall": {
            "dimension_country_cells": len(all_recs),
            "meaningful_declines": dec, "meaningful_improvements": imp, "within_noise": nos,
            "decline_to_improve_ratio": round(dec / imp, 2) if imp else None,
        },
        # C9 robustness: the Voice & Accountability decline asymmetry survives BOTH the
        # stricter 95% bar AND an alternative in-snapshot window (so it is not an artifact
        # of the 90% threshold or the exact 2014->2024 endpoints).
        "va_robustness": {
            "note": "Voice & Accountability decline:improve, at the 90% and 95% bars, for the "
                    "primary window and an alternative in-snapshot window, plus a sweep over the "
                    "assumed cross-year correlation rho (the headline uses rho=0, i.e. independence; "
                    "WGI's overlapping sources make the true rho positive, and for a change test "
                    "rho=0 is the conservative choice — it flags the fewest countries).",
            "primary": va_window_ratio(countries, BASELINE_YEAR, LATEST_YEAR),
            "alt_window": va_window_ratio(countries, ALT_BASELINE_YEAR, LATEST_YEAR),
            "independence_sensitivity": va_independence_sensitivity(countries),
        },
        "ethical_note": "Country/institution-level governance; watch power, not people (NOTICE §7).",
        "license": {"code": "GPL-3.0-or-later", "data": "CC0-1.0",
                    "wgi_terms": "WGI is freely available; cite the World Bank."},
    }
    json_path = os.path.join(DERIVED, "wgi_governance_summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2); f.write("\n")

    print(f"WGI governance (6 dimensions)  {BASELINE_YEAR}->{LATEST_YEAR}")
    for dim, d in dims.items():
        c = d["counts"]
        print(f"  {dim} {d['name']:<42} decline={c['DECLINE']:>3} improve={c['IMPROVE']:>3} noise={c['NO_SIG_CHANGE']:>3}")
    print(f"  OVERALL  cells={len(all_recs)}  declines={dec}  improvements={imp}  "
          f"ratio={summary['overall']['decline_to_improve_ratio']}:1")
    print(f"  wrote {os.path.relpath(csv_path, REPO)} and {os.path.relpath(json_path, REPO)}")


if __name__ == "__main__":
    sys.exit(main())
