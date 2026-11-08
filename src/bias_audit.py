# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Blind-pack generator for the pre-registered bias self-audit.

Implements the coding materials of docs/BIAS_AUDIT_PREREGISTRATION.md §1 (H1): every ledger
entry's title + Claim section with the uppercase grade tokens masked, pseudo-shuffled under
opaque codes, plus a separate key file the coder never opens. Deterministic by construction
(ordering = SHA-256 of the entry id; no clock, no randomness) so two people generating the
pack from the same commit get identical bytes — the pack itself is auditable.

This tool only PREPARES the audit. Running it — recruiting coders, coding, analysis,
publication — is founder-gated per the pre-registration.
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
LEDGER = os.path.join(REPO, "ledger")

# CASE-INSENSITIVE for the three grade-loaded words — adversarial review demonstrated the
# uppercase-only v1 leaked ("Refuted pseudoscience" in a TITLE announced its own grade, plus
# ~40 lowercase 'robust'/'contested' in claim prose). Ordinary-English readability loses;
# blindness wins. OPEN stays uppercase-only as a DOCUMENTED residual: 'open' is ubiquitous
# ("open data", "open science") and masking it would shred the text for one OPEN-graded entry.
GRADE_TOKENS = re.compile(r"\b(ROBUST|CONTESTED|REFUTED)\b", re.IGNORECASE)
GRADE_TOKENS_UPPER = re.compile(r"\bOPEN\b")
MASK = "▓▓▓"


def _entries(ledger_dir):
    # reuse the single-sourced "what counts as an entry" rule
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ledger_staleness import read_entries
    return read_entries(ledger_dir)


def _claim_section(text):
    m = re.search(r"^## Claim\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def build_pack(ledger_dir):
    """Pure-ish: ledger dir -> (pack_markdown, key_dict). Deterministic; masks grade tokens."""
    items = []
    for filename, meta in _entries(ledger_dir):
        with open(os.path.join(ledger_dir, filename), encoding="utf-8") as f:
            text = f.read()
        entry_id = meta.get("id", filename)
        title = meta.get("title", "")
        claim = _claim_section(text)
        blinded = GRADE_TOKENS_UPPER.sub(MASK, GRADE_TOKENS.sub(MASK, f"**{title}**\n\n{claim}"))
        # pseudo-shuffle: stable, non-alphabetical, reproducible from content ids alone
        items.append((hashlib.sha256(entry_id.encode()).hexdigest(), entry_id, blinded))
    items.sort()

    key, blocks = {}, []
    for i, (_, entry_id, blinded) in enumerate(items, 1):
        code = f"E{i:02d}"
        key[code] = entry_id
        blocks.append(f"## {code}\n\n{blinded}\n\n"
                      f"VALENCE (circle one): D — decline-affirming · R — reassuring/debunking · "
                      f"N — mechanism/neutral    CONFIDENCE: high / low\n")

    pack = ("# Blind coding pack — bias self-audit (H1)\n\n"
            "Protocol: docs/BIAS_AUDIT_PREREGISTRATION.md §1. Code each item's VALENCE from the\n"
            "text below alone. Grade words are masked as " + MASK + ". Do NOT open the key file.\n\n"
            + "\n".join(blocks))
    return pack, key


# ---- H1 analysis (docs/BIAS_AUDIT_PREREGISTRATION.md §1) ----------------------------------------
# Pre-registered decision rule, frozen here in code so the criterion can't drift post-hoc.
SKEW_DELTA_P = 0.25
SKEW_P = 0.10


def _hyper(a, r1, r2, c1):
    """Hypergeometric P(top-left cell == a) for a 2x2 table with fixed margins."""
    n = r1 + r2
    return math.comb(r1, a) * math.comb(r2, c1 - a) / math.comb(n, c1)


def fisher_exact(a, b, c, d):
    """Two-sided Fisher exact p for [[a,b],[c,d]], pure stdlib. Small-N exact; fine for ~38 entries."""
    r1, r2, c1 = a + b, c + d, a + c
    lo, hi = max(0, c1 - r2), min(r1, c1)
    p_obs = _hyper(a, r1, r2, c1)
    # two-sided: sum probabilities of all tables at least as extreme (<= observed, with tolerance)
    return min(1.0, sum(p for x in range(lo, hi + 1)
                        if (p := _hyper(x, r1, r2, c1)) <= p_obs * (1 + 1e-9)))


def _binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k, n, alpha=0.05):
    """Exact (Clopper–Pearson) two-sided CI for a binomial proportion — pure-stdlib bisection.

    The pre-registration commits to publishing an exact 95% CI on each proportion regardless
    of outcome; this makes that commitment executable. Endpoints are exact by construction
    (k=0 -> lower 0; k=n -> upper 1)."""
    if n == 0:
        return None
    def _bisect(g, rising):
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if (g(mid) < 0) == rising:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else _bisect(lambda p: (1 - _binom_cdf(k - 1, n, p)) - alpha / 2, rising=True)
    upper = 1.0 if k == n else _bisect(lambda p: _binom_cdf(k, n, p) - alpha / 2, rising=False)
    return (lower, upper)


def load_grades(ledger_dir):
    with open(os.path.join(ledger_dir, "index.json"), encoding="utf-8") as f:
        return {e["id"]: e["grade"] for e in json.load(f)["entries"]}


def score(coded, key, grades):
    """coded: {code -> 'D'/'R'/'N'}; key: {code -> id}; grades: {id -> grade}. Returns the H1 result.

    Builds the 2x2 valence(D vs R) x grade(ROBUST vs not) table, ΔP, Fisher p, and the fire verdict.
    Neutral (N) codes are excluded from the table by design (they carry no directional implication).
    """
    cells = {("D", 1): 0, ("D", 0): 0, ("R", 1): 0, ("R", 0): 0}
    skipped = []
    for code, valence in coded.items():
        entry_id = key.get(code)
        grade = grades.get(entry_id)
        if valence == "N" or entry_id is None or grade is None:
            skipped.append(code)
            continue
        if valence not in ("D", "R"):
            raise ValueError(f"{code}: valence must be D/R/N, got {valence!r}")
        cells[(valence, 1 if grade == "ROBUST" else 0)] += 1
    a, b = cells[("D", 1)], cells[("D", 0)]   # D-ROBUST, D-notROBUST
    c, d = cells[("R", 1)], cells[("R", 0)]   # R-ROBUST, R-notROBUST
    p_d = a / (a + b) if a + b else None
    p_r = c / (c + d) if c + d else None
    delta = (p_d - p_r) if (p_d is not None and p_r is not None) else None
    p_value = fisher_exact(a, b, c, d) if (a + b and c + d) else None
    fires = (delta is not None and p_value is not None
             and delta > SKEW_DELTA_P and p_value < SKEW_P)
    return {
        "table": {"D_robust": a, "D_not": b, "R_robust": c, "R_not": d},
        "n_coded": a + b + c + d, "n_neutral_or_skipped": len(skipped),
        "p_robust_given_D": p_d, "p_robust_given_R": p_r,
        "ci95_robust_given_D": clopper_pearson(a, a + b),
        "ci95_robust_given_R": clopper_pearson(c, c + d),
        "delta_p": delta, "fisher_p_two_sided": p_value,
        "criterion": f"skew if delta_p > {SKEW_DELTA_P} AND fisher_p < {SKEW_P}",
        "skew_detected": fires,
    }


def _round(v, n=4):
    if isinstance(v, float):
        return round(v, n)
    if isinstance(v, tuple):
        return [_round(x, n) for x in v]
    return v


def main(argv=None):
    ap = argparse.ArgumentParser(description="Blind pack + H1 scorer for the bias self-audit.")
    ap.add_argument("--pack", metavar="DIR", help="write blind_pack.md + blind_key.json into DIR")
    ap.add_argument("--score", metavar="CODED.json", help="score coded valences {code: D/R/N} against --key")
    ap.add_argument("--key", metavar="KEY.json", help="the sealed code->id key (with --score)")
    args = ap.parse_args(argv)

    if args.score:
        if not args.key:
            print("bias-audit: --score needs --key <blind_key.json>")
            return 2
        try:
            with open(args.score, encoding="utf-8") as f:
                coded = json.load(f)
            with open(args.key, encoding="utf-8") as f:
                key = json.load(f)
            grades = load_grades(LEDGER)
        except FileNotFoundError as e:
            print(f"bias-audit: {os.path.basename(e.filename or '?')} not found")
            return 2
        result = score(coded, key, grades)
        print(json.dumps({k: _round(v) for k, v in result.items()}, indent=2))
        print("\nVERDICT:", "SKEW DETECTED — founder re-grade pass (see §6)" if result["skew_detected"]
              else "no directional skew at the pre-registered criterion (report with the power caveat, §5)")
        return 0

    try:
        pack, key = build_pack(LEDGER)
    except FileNotFoundError:
        print("bias-audit: ledger not found — run from a checkout with ledger/")
        return 2

    if not args.pack:
        print(f"bias-audit: pack ready for {len(key)} entries; write it with --pack <dir> "
              f"(see docs/BIAS_AUDIT_PREREGISTRATION.md)")
        return 0

    os.makedirs(args.pack, exist_ok=True)
    with open(os.path.join(args.pack, "blind_pack.md"), "w", encoding="utf-8") as f:
        f.write(pack)
    with open(os.path.join(args.pack, "blind_key.json"), "w", encoding="utf-8") as f:
        json.dump(key, f, indent=1, sort_keys=True)
    print(f"bias-audit: wrote blind_pack.md ({len(key)} blinded entries) + blind_key.json to {args.pack}\n"
          f"Give the coder ONLY blind_pack.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
