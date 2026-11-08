#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Doc-count consistency audit — keep the headline numbers honest.

The project sprinkles counts across prose — "15 graded entries", "9 ROBUST / 4
CONTESTED / 1 REFUTED / 1 OPEN", "make verify green — N tests". Hand-copied, these
silently drift the moment an entry is added or a test is written. This computes the
**actual** state from the repo itself (the source of truth) and fails if either the
pinned `data/expected_counts.json` or the claims in README / STATUS / the site drift
from it.

`--update` re-pins `expected_counts.json` from the live repo (review the diff, then
commit). Pure core (`compute_actual`, `check_docs`) + thin CLI.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

GRADES = ("ROBUST", "CONTESTED", "REFUTED", "OPEN")


def compute_actual(repo):
    """The ground truth, read straight from the repo. O(files)."""
    led = os.path.join(repo, "ledger")
    entry_files = [f for f in os.listdir(led) if f.startswith("SAA-") and f.endswith(".md")]
    idx_path = os.path.join(led, "index.json")
    with open(idx_path, encoding="utf-8") as f:
        try:
            index = json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"{idx_path}: invalid JSON ({e})") from e
    by_grade = {g: 0 for g in GRADES}
    for e in index.get("entries", []):
        if e.get("grade") in by_grade:
            by_grade[e["grade"]] += 1

    sims = [f for f in os.listdir(os.path.join(repo, "src", "sims"))
            if f.startswith("sim_") and f.endswith(".py")]

    tests_dir = os.path.join(repo, "tests")
    test_count = 0
    for f in os.listdir(tests_dir):
        if f.startswith("test_") and f.endswith(".py"):
            with open(os.path.join(tests_dir, f), encoding="utf-8") as fh:
                test_count += len(re.findall(r"^\s+def test_\w+", fh.read(), re.M))

    return {"ledger_entries": len(entry_files), "sim_count": len(sims),
            "test_count": test_count, **{g.lower(): by_grade[g] for g in GRADES}}


# (file, regex with one numeric capture, key into the actual-counts dict). A pattern
# that isn't present is skipped (docs get reworded); a present-but-wrong number fails.
DOC_CHECKS = [
    ("README.md", r"(\d+) graded, falsifiable evidence entries", "ledger_entries"),
    ("README.md", r"\*\*(\d+) offline tests\*\*", "test_count"),
    ("STATUS.md", r"`make verify-offline` green — (\d+) tests", "test_count"),
    ("STATUS.md", r"(\d+) graded entries", "ledger_entries"),
    # the by-grade breakdown drifts independently of the total (a regrade moves two numbers,
    # a new entry moves one) — pin each grade tally, anchored to the breakdown sequence
    ("STATUS.md", r"(\d+) ROBUST / \d+ CONTESTED", "robust"),
    ("STATUS.md", r"ROBUST / (\d+) CONTESTED", "contested"),
    ("STATUS.md", r"CONTESTED / (\d+) REFUTED", "refuted"),
    ("STATUS.md", r"REFUTED / (\d+) OPEN", "open"),
    ("site/index.html", r"(\d+) graded, falsifiable evidence entries", "ledger_entries"),
    # the footer states the count in a different phrase — pin it too (it drifted once: said 35 at 38)
    ("site/index.html", r"(\d+)-entry evidence ledger", "ledger_entries"),
    # TRUST_SIGNALS.md promises its own numbers are gate-pinned (its closing note) — keep that true
    ("docs/TRUST_SIGNALS.md", r"\*\*(\d+) offline tests\*\*", "test_count"),
    ("docs/TRUST_SIGNALS.md", r"\*\*(\d+) graded, falsifiable evidence entries\*\*", "ledger_entries"),
]


def check_docs(repo, actual):
    """Return [(file, claimed, expected, key)] for every doc number that disagrees."""
    problems = []
    for rel, pattern, key in DOC_CHECKS:
        path = os.path.join(repo, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            m = re.search(pattern, f.read())
        if m and int(m.group(1)) != actual[key]:
            problems.append((rel, int(m.group(1)), actual[key], key))
    return problems


def unmatched_doc_patterns(repo):
    """Return [(file, key)] for DOC_CHECKS whose file exists but whose pattern no longer matches.

    check_docs() intentionally SKIPS a non-matching pattern so prose can be reworded — but
    that means a count guard can silently go dark (the claim stops being compared) with no
    signal. This surfaces the darkened patterns so a test can pin that every shipped
    doc-claim is still actually guarded. O(DOC_CHECKS).
    """
    dark = []
    for rel, pattern, key in DOC_CHECKS:
        path = os.path.join(repo, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            if not re.search(pattern, f.read()):
                dark.append((rel, key))
    return dark


# Headline FIGURES the public site cites, recomputed from the committed derived data — so the
# site's own claim ("every public number is machine-checked") is true for the *computed* numbers,
# not just the entry count. (file, regex with one numeric capture, key into compute_derived_figures.)
FIGURE_CHECKS = [
    # the public site
    ("site/index.html", r'class="bignum">(\d+)<span>%', "within_noise_pct"),
    # the hero lede now carries the noise floor too — pin it or it can drift from the bignum
    ("site/index.html", r"<b>(\d+)%</b> of a decade of measured", "within_noise_pct"),
    ("site/index.html", r"improvements (\d+):\d+", "meaningful_declines"),
    ("site/index.html", r"improvements \d+:(\d+)", "meaningful_improvements"),
    ("site/index.html", r"decline in voice in\s*<b>(\d+)\s*countries", "concur_decline"),
    ("site/index.html", r"in <b>(\d+)</b> of them all three", "concur_decline_full3"),
    ("site/index.html", r'seg-noise"   style="width:([\d.]+)%', "bar_noise_pct1"),
    ("site/index.html", r'seg-decline" style="width:([\d.]+)%', "bar_decline_pct1"),
    ("site/index.html", r'seg-improve" style="width:([\d.]+)%', "bar_improve_pct1"),
    ("site/index.html", r"<b>([\d,]+) pre-registered</b>", "n_forecasts"),
    # the detailed indicator + forecast docs (where the load-bearing claims live)
    ("docs/indicators/wgi-governance.md", r"Within measurement noise\*\* \| \*\*([\d,]+)\*\*", "within_noise"),
    ("docs/indicators/wgi-governance.md", r"Within measurement noise\*\* \| \*\*[\d,]+\*\* \| \*\*(\d+)%", "within_noise_pct"),
    ("docs/indicators/wgi-governance.md", r"improvements \*\*(\d+) : \d+", "meaningful_declines"),
    ("docs/indicators/wgi-governance.md", r"improvements \*\*\d+ : (\d+)", "meaningful_improvements"),
    ("docs/forecast/pharos-forecast-v0.md", r"\*\*([\d,]+) pre-registered forecasts\*\*", "n_forecasts"),
    # the trust page's headline uncertainty claim (§4) — same pin as the site's bignum
    ("docs/TRUST_SIGNALS.md", r"\*\*(\d+)%\*\* of\s+measured changes", "within_noise_pct"),
]

# H3, the symmetric-reporting rule (docs/BIAS_AUDIT_PREREGISTRATION.md §3), as a machine gate:
# any surface that carries the meaningful-decline count must carry the improvement count too.
SYMMETRIC_SURFACES = [
    "README.md",
    "site/index.html",
    "docs/BRIEF.md",
    "docs/WATCH_REPORT.md",
    "docs/indicators/wgi-governance.md",
]


def check_symmetric_reporting(repo, figures):
    """Return [(file, reason)] for surfaces that report declines without improvements."""
    dec, imp = str(figures["meaningful_declines"]), str(figures["meaningful_improvements"])
    problems = []
    for rel in SYMMETRIC_SURFACES:
        path = os.path.join(repo, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        # the decline count as a standalone figure — NOT a percentage; today 88 (declines)
        # and 88% (within-noise) collide numerically, so a trailing % must not count
        if re.search(rf"\b{dec}\b(?!\s*%)", text) and not re.search(rf"\b{imp}\b", text):
            problems.append((rel, f"reports the {dec} declines without the {imp} improvements"))
    return problems


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"{path}: invalid JSON ({e})") from e


def compute_derived_figures(repo):
    """Recompute the site's headline figures straight from data/derived (the source of truth)."""
    der = os.path.join(repo, "data", "derived")
    w = _load_json(os.path.join(der, "wgi_governance_summary.json"))["overall"]
    voice = _load_json(os.path.join(der, "voice_divergence.json"))
    v = voice["counts"]
    fc = _load_json(os.path.join(der, "forecast_backtest.json"))["result"]
    return {
        "within_noise": w["within_noise"],
        "within_noise_pct": round(w["within_noise"] / w["dimension_country_cells"] * 100),
        "meaningful_declines": w["meaningful_declines"],
        "meaningful_improvements": w["meaningful_improvements"],
        "concur_decline": v["CONCUR-DECLINE"],
        # the STRICT all-three-significant subset — R7 found surfaces conflating this with the
        # >=2-significant CONCUR count; pinning both keeps the two bars from blurring again
        "concur_decline_full3": len(voice["headline_concur_decline_n_sig_3"]),
        # one-decimal bar-segment shares — the site's stacked bar draws these widths; they were
        # correct but unpinned, which is exactly the drift class R7 caught in this same chart
        "bar_noise_pct1": round(w["within_noise"] / w["dimension_country_cells"] * 100, 1),
        "bar_decline_pct1": round(w["meaningful_declines"] / w["dimension_country_cells"] * 100, 1),
        "bar_improve_pct1": round(w["meaningful_improvements"] / w["dimension_country_cells"] * 100, 1),
        "n_forecasts": fc["n_forecasts"],
    }


def check_figures(repo, figures):
    """Return [(file, claimed, expected, key)] for every cited figure that disagrees with the data."""
    problems = []
    for rel, pattern, key in FIGURE_CHECKS:
        path = os.path.join(repo, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            m = re.search(pattern, f.read())
        if not m:
            continue
        raw = m.group(1).replace(",", "")
        # one-decimal pins (the bar-segment widths) carry a dot; integer pins stay exact ints
        claimed = float(raw) if "." in raw else int(raw)
        if claimed != figures[key]:
            problems.append((rel, claimed, figures[key], key))
    return problems


def unmatched_figure_patterns(repo):
    """Return [(file, key)] for FIGURE_CHECKS whose file exists but whose pattern no longer matches —
    the figure-side analogue of `unmatched_doc_patterns`, so a reworded doc can't silently un-pin a
    figure from the data."""
    dark = []
    for rel, pattern, key in FIGURE_CHECKS:
        path = os.path.join(repo, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            if not re.search(pattern, f.read()):
                dark.append((rel, key))
    return dark


def _default_repo():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _expected_path(repo):
    return os.path.join(repo, "data", "expected_counts.json")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verify headline counts match the repo.")
    ap.add_argument("--repo", default=_default_repo())
    ap.add_argument("--update", action="store_true", help="re-pin expected_counts.json from the repo")
    args = ap.parse_args(argv)

    actual = compute_actual(args.repo)
    exp_path = _expected_path(args.repo)

    if args.update:
        with open(exp_path, "w", encoding="utf-8") as f:
            json.dump(actual, f, indent=2, sort_keys=True)
            f.write("\n")
        print(f"re-pinned {os.path.relpath(exp_path, args.repo)}: {actual}")
        return 0

    problems = []
    if os.path.exists(exp_path):
        with open(exp_path, encoding="utf-8") as f:
            try:
                expected = json.load(f)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"{exp_path}: invalid JSON ({e})") from e
        for k, v in actual.items():
            if expected.get(k) != v:
                problems.append(f"expected_counts.json: {k} pinned {expected.get(k)} but repo has {v}")
    else:
        problems.append("data/expected_counts.json missing — run --update")

    for rel, claimed, exp, key in check_docs(args.repo, actual):
        problems.append(f"{rel}: says {claimed} for {key}, repo has {exp}")

    # The site cites computed figures (88% within noise, 45 concur-decline, 2,600 forecasts) — pin
    # them to the derived data too, so the page can't drift from the verified computation.
    if os.path.exists(os.path.join(args.repo, "data", "derived", "wgi_governance_summary.json")):
        figures = compute_derived_figures(args.repo)
        for rel, claimed, exp, key in check_figures(args.repo, figures):
            problems.append(f"{rel}: figure `{key}` says {claimed}, derived data has {exp}")
        # the pre-registered symmetric-reporting rule, standing (never a decline without its counterpart)
        for rel, reason in check_symmetric_reporting(args.repo, figures):
            problems.append(f"{rel}: {reason}")

    print(f"count audit — actual {actual}")
    for p in problems:
        print(f"  ✗ {p}")
    if problems:
        print("FAIL: headline counts have drifted (fix the docs, or `--update` the pin).")
        return 1
    print("counts: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
