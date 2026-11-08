#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Voice & Accountability, triangulated — publish *divergence*, not a single score.

Tier-0 ④ of the plan-for-peace launch gates, and the C5/R6 "calibration layer"
posture: a single backsliding number can be gamed (capture one survey, one coder)
and then launders a false green. So we never publish one. Instead, for each country
we reduce three freedom-of-expression instruments to a *signed, significant
decade change* and publish where they **concur** vs where they **conflict** — a captured
single input can flip at most one sign, which then surfaces as CONFLICT (with the
dissenter named) instead of dragging a blended average.

The three instruments (2014→2024), each kept in its own native scale — we make them
commensurable ONLY at sign and significance, never by rescaling values onto a shared axis:

  • WGI Voice & Accountability (World Bank, 0–100, ships a 90% CI) — the CI-backed gold
    input; we reuse its already-computed 90% z-test verdict (`wgi_governance.py`).
  • V-Dem Freedom of Expression index (v2x_freexp_altinf, 0–1) — material-change threshold
    (0.05); OWID's grapher surfaces no CI, so flag_basis = THRESHOLD.
  • Freedom House Civil Liberties score (0–60) — no published CI at all, so a deliberately
    conservative dead-band (3 pts ≈ 5 on a 0–100 scale); flag_basis = THRESHOLD-NO-CI.

Honesty invariants: (1) no blended score, ever; (2) disagreement beats majority — a 2-vs-1
split is CONFLICT, not a vote (a vote would re-hide a single number); (3) every sign carries
its flag_basis so CI-backed evidence is never confused with a threshold guess; (4) missing
instruments are shown, never imputed.

Pure stdlib. Pure core (`reduce_*`, `combine_agreement`, `triangulate_country`) is fully
unit-tested offline; only the fetch/`main` layer touches the network and filesystem.
"""
from __future__ import annotations

import csv
import json
import os
import sys

# Reuse the WGI module's pure helpers (Z90, compute_change, se_from_ci) — one test, one engine.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wgi_governance as wgi  # noqa: E402
import fetch_utils  # noqa: E402 — shared resilient fetch (backoff+jitter) + offline snapshots

VDEM_URL = ("https://ourworldindata.org/grapher/freedom-of-expression-index.csv"
            "?v=1&csvType=full&useColumnShortNames=true")
VDEM_COL = "freeexpr_vdem__estimate_best"
FH_URL = ("https://ourworldindata.org/grapher/civil-liberties-score-fh.csv"
          "?v=1&csvType=full&useColumnShortNames=false")
FH_COL = "Civil liberties score"

BASELINE_YEAR, LATEST_YEAR = 2014, 2024
VDEM_THRESHOLD = 0.05        # material move on the 0–1 V-Dem scale
FH_THRESHOLD = 3.0           # 5 pts on 0–100 rescaled to the 0–60 CL score: 5*60/100 = 3
LABELS = ("CONCUR-DECLINE", "CONCUR-IMPROVE", "CONFLICT",
          "MIXED-WEAK", "ALL-FLAT", "INSUFFICIENT")

# Offline mode reads committed snapshot CSVs instead of the live OWID endpoints.
# CSV snapshots carry no embedded provenance (unlike the WGI JSON snapshot), so the
# fetch time is recorded here — pinned alongside the WGI/V-Dem inputs on 2026-06-18.
_HERE = os.path.dirname(os.path.abspath(__file__))
VDEM_SNAPSHOT = os.path.normpath(os.path.join(_HERE, "..", "..", "data", "snapshots", "vdem_freexp.csv"))
FH_SNAPSHOT = os.path.normpath(os.path.join(_HERE, "..", "..", "data", "snapshots", "fh_civlibs.csv"))
SNAP_FETCHED_UTC = "2026-06-18T04:35:36+00:00"
_OFFLINE = False


# ----------------------------------------------------------------- pure core ----

def _direction(delta, deadband):
    """Sign with a dead-band: moves below the instrument's noise floor read as flat (0)."""
    if abs(delta) < deadband:
        return 0
    return 1 if delta > 0 else -1


def reduce_wgi(va_row):
    """Map an existing WGI VA row → instrument triple. Reuses WGI's own CI-backed 90%
    verdict (DECLINE/IMPROVE/NO_SIG_CHANGE); no recomputation. O(1)."""
    verdict = va_row["verdict"]
    direction = {"DECLINE": -1, "IMPROVE": 1}.get(verdict, 0)
    return {"available": True, "v_start": float(va_row["sc_base"]),
            "v_end": float(va_row["sc_latest"]), "delta": float(va_row["change"]),
            "unit": "score_0_100", "direction": direction,
            "flag": "SIG" if direction else "NS", "flag_basis": "CI",
            "z": float(va_row["z"]), "ci_level": 0.90}


def reduce_vdem(v_start, v_end):
    """0–1 scale, material-change threshold (OWID grapher surfaces no CI). O(1)."""
    delta = v_end - v_start
    direction = _direction(delta, VDEM_THRESHOLD)
    return {"available": True, "v_start": v_start, "v_end": v_end, "delta": delta,
            "unit": "prob_0_1", "direction": direction,
            "flag": "SIG" if direction else "NS",
            "flag_basis": "THRESHOLD", "threshold": VDEM_THRESHOLD}


def reduce_fh(v_start, v_end):
    """0–60 CL score, NO published CI → conservative dead-band only. O(1)."""
    delta = v_end - v_start
    direction = _direction(delta, FH_THRESHOLD)
    return {"available": True, "v_start": v_start, "v_end": v_end, "delta": delta,
            "unit": "score_0_60", "direction": direction,
            "flag": "SIG" if direction else "NS",
            "flag_basis": "THRESHOLD-NO-CI", "threshold": FH_THRESHOLD}


def absent(unit):
    return {"available": False, "unit": unit, "direction": None,
            "flag": "NA", "flag_basis": "NONE"}


def combine_agreement(wgi_i, vdem_i, fh_i):
    """The honesty core. Combine ONLY the signs of available-and-significant instruments.

    Resolution order is deliberate: INSUFFICIENT, then CONFLICT (a sign disagreement is
    NEVER overridden by a majority vote — that would re-hide a single number), then CONCUR,
    then MIXED-WEAK, then ALL-FLAT. O(1).
    """
    insts = {"wgi_va": wgi_i, "vdem_foe": vdem_i, "fh": fh_i}
    available = [k for k, x in insts.items() if x.get("available")]
    sig = [k for k in available if insts[k]["flag"] == "SIG"]
    signs = {k: insts[k]["direction"] for k in sig if insts[k]["direction"]}
    distinct = set(signs.values())

    if len(available) < 2:
        label, concurring, dissenting = "INSUFFICIENT", [], []
    elif len(distinct) >= 2:                      # both +1 and -1 present → contradiction
        label = "CONFLICT"
        pos = [k for k in signs if signs[k] == 1]
        neg = [k for k in signs if signs[k] == -1]
        majority = pos if len(pos) >= len(neg) else neg   # descriptive only — NOT a vote
        concurring = majority
        dissenting = [k for k in signs if k not in majority]
    elif len(sig) >= 2 and len(distinct) == 1:    # ≥2 SIG, one shared nonzero sign
        d = next(iter(distinct))
        label = "CONCUR-DECLINE" if d < 0 else "CONCUR-IMPROVE"
        concurring, dissenting = list(signs), []
    elif len(sig) == 1:                           # signal in one, only noise in the others
        label, concurring, dissenting = "MIXED-WEAK", list(signs), []
    else:                                         # ≥2 available, none significant
        label, concurring, dissenting = "ALL-FLAT", [], []

    basis_mix = {}
    for k in sig:
        b = insts[k]["flag_basis"]
        basis_mix[b] = basis_mix.get(b, 0) + 1
    has_ci = basis_mix.get("CI", 0) >= 1

    if label in ("CONCUR-DECLINE", "CONCUR-IMPROVE") and len(sig) >= 2 and has_ci:
        strength = "HIGH"
    elif label == "CONFLICT":
        strength = "CONFLICT"
    elif label in ("CONCUR-DECLINE", "CONCUR-IMPROVE"):
        strength = "MEDIUM"          # concurs, but no CI-backed instrument among them
    elif label == "MIXED-WEAK":
        strength = "LOW"
    else:
        strength = "NONE"

    return {"label": label, "n_available": len(available), "n_sig": len(sig),
            "concurring": concurring, "dissenting": dissenting,
            "flag_basis_mix": basis_mix, "evidence_strength": strength}


def triangulate_country(iso3, name, wgi_row, vdem_pair, fh_pair):
    """Pure. WGI is the universe (always present); V-Dem/FH attach if joined, else absent."""
    w = reduce_wgi(wgi_row)
    v = reduce_vdem(*vdem_pair) if vdem_pair else absent("prob_0_1")
    f = reduce_fh(*fh_pair) if fh_pair else absent("score_0_60")
    return {"country": iso3, "country_name": name,
            "window": {"requested": [BASELINE_YEAR, LATEST_YEAR]},
            "instruments": {"wgi_va": w, "vdem_foe": v, "fh": f},
            "agreement": combine_agreement(w, v, f)}


# ----------------------------------------------------------------------- I/O ----

def _read_csv_file(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _owid_rows(url, snapshot_path):
    """Rows for an OWID grapher CSV — from the committed snapshot when offline, else
    live via the shared resilient fetcher (backoff + jitter)."""
    if _OFFLINE:
        return _read_csv_file(snapshot_path)
    return fetch_utils.fetch_csv_rows(url, timeout=60)


def write_snapshot():
    """Fetch the OWID inputs LIVE and freeze the rows we actually use (target years,
    real countries, the three needed columns) to data/snapshots/*.csv — the deliberate
    pin step (`make snapshot`). Keeps the snapshot small and the same shape as live rows."""
    specs = [(VDEM_URL, VDEM_SNAPSHOT, "code", "year", VDEM_COL),
             (FH_URL, FH_SNAPSHOT, "Code", "Year", FH_COL)]
    for url, path, code_key, year_key, value_col in specs:
        kept = []
        for r in fetch_utils.fetch_csv_rows(url, timeout=60):
            code = (r.get(code_key) or "").strip()
            if not _is_country(code):
                continue
            try:
                year = int(r.get(year_key) or r.get("year") or r.get("Year"))
            except (TypeError, ValueError):
                continue
            if year in (BASELINE_YEAR, LATEST_YEAR) and r.get(value_col) not in (None, ""):
                kept.append({code_key: code, year_key: year, value_col: r[value_col]})
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[code_key, year_key, value_col])
            w.writeheader()
            for row in sorted(kept, key=lambda x: (x[code_key], x[year_key])):
                w.writerow(row)
        print(f"wrote {os.path.relpath(path)}  ({len(kept)} rows)")


def _is_country(code):
    """OWID region/aggregate/historical rows carry empty or OWID_* codes — drop them."""
    return bool(code) and not code.startswith("OWID")


def threshold_sensitivity(wgi_va, vdem, fh, vdem_mults=(0.8, 1.0, 1.2), fh_mults=(0.8, 1.0, 1.2)):
    """How much do the concurrence counts depend on the (judgment-call) V-Dem and FH
    thresholds? The WGI input is CI-backed (not a threshold), so it is fixed; the V-Dem
    0.05 and FH 3.0 dead-bands are the two judgment calls. This re-triangulates at ±20%
    of each and reports the CONCUR-DECLINE / CONCUR-IMPROVE / CONFLICT counts, so a
    reader can see whether the 45 / 8 / 5 headline is a knife-edge or stable. O(countries).

    The three instruments are NOT independent measurements of one latent construct: V-Dem
    feeds WGI, and V-Dem/FH share expert-coder networks. So concurrence is "multi-source
    agreement," not "independent corroboration" — this sweep quantifies robustness to the
    *threshold* axis; the residual coder-overlap is disclosed in the doc, not solved here.
    """
    sweep = []
    for vm in vdem_mults:
        for fm in fh_mults:
            vt, ft = VDEM_THRESHOLD * vm, FH_THRESHOLD * fm
            counts = {lab: 0 for lab in LABELS}
            for iso3, row in wgi_va.items():
                w = reduce_wgi(row)                       # CI-backed, threshold-invariant
                vp, fpair = vdem.get(iso3), fh.get(iso3)
                v = ({"available": True, "direction": _direction(vp[1] - vp[0], vt),
                      "flag": "SIG" if _direction(vp[1] - vp[0], vt) else "NS",
                      "flag_basis": "THRESHOLD"} if vp else absent("prob_0_1"))
                f = ({"available": True, "direction": _direction(fpair[1] - fpair[0], ft),
                      "flag": "SIG" if _direction(fpair[1] - fpair[0], ft) else "NS",
                      "flag_basis": "THRESHOLD-NO-CI"} if fpair else absent("score_0_60"))
                counts[combine_agreement(w, v, f)["label"]] += 1
            sweep.append({"vdem_threshold": round(vt, 3), "fh_threshold": round(ft, 2),
                          "vdem_mult": vm, "fh_mult": fm, "counts": counts})
    return sweep


def load_owid_pairs(rows, code_key, value_col):
    """Index an OWID grapher CSV → {iso3: (v_2014, v_2024)} for rows present at BOTH years."""
    by_year = {}
    for row in rows:
        code = (row.get(code_key) or "").strip()
        if not _is_country(code):
            continue
        try:
            year = int(row["year" if "year" in row else "Year"])
        except (KeyError, ValueError):
            continue
        raw = row.get(value_col)
        if year in (BASELINE_YEAR, LATEST_YEAR) and raw not in (None, ""):
            by_year.setdefault(code, {})[year] = float(raw)
    return {c: (yv[BASELINE_YEAR], yv[LATEST_YEAR])
            for c, yv in by_year.items()
            if BASELINE_YEAR in yv and LATEST_YEAR in yv}


def load_wgi_va(csv_path):
    """Read the project's own derived WGI csv → {iso3: row} for the VA dimension."""
    out = {}
    with open(csv_path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("dimension") == "VA":
                out[row["iso3"]] = row
    return out


def _default_wgi_csv():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "data", "derived", "wgi_governance.csv"))


def _derived_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "data", "derived"))


CSV_FIELDS = [
    "iso3", "country_name",
    "wgi_available", "wgi_v_start", "wgi_v_end", "wgi_delta", "wgi_direction", "wgi_flag", "wgi_flag_basis", "wgi_z",
    "vdem_available", "vdem_v_start", "vdem_v_end", "vdem_delta", "vdem_direction", "vdem_flag", "vdem_flag_basis",
    "fh_available", "fh_v_start", "fh_v_end", "fh_delta", "fh_direction", "fh_flag", "fh_flag_basis",
    "label", "n_available", "n_sig", "concurring", "dissenting", "flag_basis_mix", "evidence_strength",
]


def _flat_row(rec):
    i = rec["instruments"]
    w, v, f, a = i["wgi_va"], i["vdem_foe"], i["fh"], rec["agreement"]
    def g(d, k):
        return "" if d.get(k) is None else d.get(k)
    return {
        "iso3": rec["country"], "country_name": rec["country_name"],
        "wgi_available": w["available"], "wgi_v_start": g(w, "v_start"), "wgi_v_end": g(w, "v_end"),
        "wgi_delta": g(w, "delta"), "wgi_direction": g(w, "direction"), "wgi_flag": w["flag"],
        "wgi_flag_basis": w["flag_basis"], "wgi_z": g(w, "z"),
        "vdem_available": v["available"], "vdem_v_start": g(v, "v_start"), "vdem_v_end": g(v, "v_end"),
        "vdem_delta": g(v, "delta"), "vdem_direction": g(v, "direction"), "vdem_flag": v["flag"],
        "vdem_flag_basis": v["flag_basis"],
        "fh_available": f["available"], "fh_v_start": g(f, "v_start"), "fh_v_end": g(f, "v_end"),
        "fh_delta": g(f, "delta"), "fh_direction": g(f, "direction"), "fh_flag": f["flag"],
        "fh_flag_basis": f["flag_basis"],
        "label": a["label"], "n_available": a["n_available"], "n_sig": a["n_sig"],
        "concurring": ";".join(a["concurring"]), "dissenting": ";".join(a["dissenting"]),
        "flag_basis_mix": ";".join(f"{k}:{n}" for k, n in sorted(a["flag_basis_mix"].items())),
        "evidence_strength": a["evidence_strength"],
    }


def main(argv=None):
    global _OFFLINE
    args = sys.argv[1:] if argv is None else argv
    if "--snapshot" in args:
        write_snapshot()
        return 0
    _OFFLINE = "--offline" in args or os.environ.get("SAA_OFFLINE") == "1"

    wgi_csv = _default_wgi_csv()
    if not os.path.exists(wgi_csv):
        print(f"ERROR: {wgi_csv} not found — run `make indicators` first.", file=sys.stderr)
        return 2

    src = "snapshot" if _OFFLINE else "OWID"
    print("loading WGI Voice & Accountability (local) …")
    wgi_va = load_wgi_va(wgi_csv)
    print(f"  {len(wgi_va)} VA countries")
    print(f"loading V-Dem freedom-of-expression ({src}) …")
    vdem = load_owid_pairs(_owid_rows(VDEM_URL, VDEM_SNAPSHOT), "code", VDEM_COL)
    print(f"  {len(vdem)} countries with 2014 & 2024")
    print(f"loading Freedom House civil-liberties score ({src}) …")
    fh = load_owid_pairs(_owid_rows(FH_URL, FH_SNAPSHOT), "Code", FH_COL)
    print(f"  {len(fh)} countries with 2014 & 2024")

    records = []
    for iso3 in sorted(wgi_va):
        row = wgi_va[iso3]
        records.append(triangulate_country(
            iso3, row.get("country", iso3), row, vdem.get(iso3), fh.get(iso3)))

    counts = {lab: 0 for lab in LABELS}
    for rec in records:
        counts[rec["agreement"]["label"]] += 1
    concur3 = [r["country"] for r in records
               if r["agreement"]["label"] == "CONCUR-DECLINE" and r["agreement"]["n_sig"] == 3]
    conflicts = [{"country": r["country"], "country_name": r["country_name"],
                  "dissenting": r["agreement"]["dissenting"]}
                 for r in records if r["agreement"]["label"] == "CONFLICT"]

    out_dir = _derived_dir()
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "voice_divergence.csv")
    json_path = os.path.join(out_dir, "voice_divergence.json")
    with open(csv_path, "w", newline="", encoding="utf-8") as fhandle:
        w = csv.DictWriter(fhandle, fieldnames=CSV_FIELDS)
        w.writeheader()
        for rec in records:
            w.writerow(_flat_row(rec))
    summary = {
        "indicator_set": "Voice & Accountability triangulation — divergence, not a single score",
        "window": [BASELINE_YEAR, LATEST_YEAR],
        "mode": "offline-snapshot" if _OFFLINE else "live",
        "thresholds": {"vdem": VDEM_THRESHOLD, "fh_on_0_60": FH_THRESHOLD,
                       "wgi": "reuses WGI's published 90% CI z-test"},
        "sources": {
            "wgi_va": {"name": "World Bank WGI — Voice & Accountability", "scale": "0-100",
                       "via": "local data/derived/wgi_governance.csv"},
            "vdem_foe": {"name": "V-Dem Freedom of Expression (v2x_freexp_altinf)", "scale": "0-1",
                         "url": VDEM_URL, "license": "CC BY 4.0 (V-Dem, processed by Our World in Data)"},
            "fh": {"name": "Freedom House — Civil Liberties score", "scale": "0-60",
                   "url": FH_URL, "license": "CC BY 4.0 (Freedom House, processed by Our World in Data)"},
        },
        "counts": counts,
        "headline_concur_decline_n_sig_3": concur3,
        # threshold sensitivity: the V-Dem 0.05 and FH 3.0 dead-bands are judgment calls;
        # this re-triangulates at ±20% of each and reports how the concurrence counts move,
        # so the 45/8/5 headline is shown to be stable (or not) rather than taken on faith.
        "threshold_sensitivity": threshold_sensitivity(wgi_va, vdem, fh),
        # input provenance per input (DATA_CONTRACT §guarantees #2): each upstream
        # snapshot's sha256 + source + fetch time, so a swapped/edited input is
        # detectable from this derived file alone. WGI is local-derived (its own
        # summary carries the WGI snapshot provenance), so its sha pins that dependency.
        "input_provenance": {
            "wgi_va": fetch_utils.file_provenance(
                wgi_csv, "local: data/derived/wgi_governance.csv (recomputes WGI VA)",
                "derived from data/snapshots/wgi_raw.json"),
            "vdem_foe": fetch_utils.file_provenance(VDEM_SNAPSHOT, VDEM_URL, SNAP_FETCHED_UTC),
            "fh": fetch_utils.file_provenance(FH_SNAPSHOT, FH_URL, SNAP_FETCHED_UTC),
        },
        "conflicts": conflicts,
        "ethical_note": "Country/institution level only — watch power, not people (NOTICE §7, THREAT_MODEL.md).",
        "license": {"code": "GPL-3.0-or-later", "data": "CC0-1.0"},
        "countries": records,
    }
    with open(json_path, "w", encoding="utf-8") as fhandle:
        json.dump(summary, fhandle, indent=2)
        fhandle.write("\n")

    print("\n— divergence (publish conflict, never a single score) —")
    for lab in LABELS:
        print(f"  {lab:<16} {counts[lab]}")
    print(f"\n  high-confidence backsliding (3/3 instruments concur on decline): {len(concur3)}")
    print(f"  cross-instrument CONFLICTS (audit these — a single number would mislead): {len(conflicts)}")
    print(f"\nwrote {os.path.relpath(csv_path)} and {os.path.relpath(json_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
