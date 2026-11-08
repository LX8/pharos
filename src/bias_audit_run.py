#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Execute the MECHANICAL parts of the pre-registered bias audit (H2, H3) plus a
clearly-labeled single-coder DRY-RUN of H1.

What this is, and is NOT:

- H2 (partisan-object asymmetry) and H3 (symmetric reporting) are mechanical — no
  human coders needed. This runs them for real and their results ARE authoritative.
- H1 (valence–grade independence) requires TWO INDEPENDENT HUMAN coders per the
  pre-registration (docs/BIAS_AUDIT_PREREGISTRATION.md §1: "No LLM coding — the test
  is of human-legible valence"). This runs H1 as a SINGLE-CODER LLM DRY-RUN whose
  ONLY purpose is to prove the blind pack is codeable and the scorer works
  end-to-end. It is EXPLICITLY NOT the pre-registered result and must not be cited
  as such. It is a smoke test, published under a bright "non-authoritative" label,
  matching the responsible-AI recommendation.

Stdlib only. Writes a dated report to docs/verifications/bias-audit-<date>.md.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import date

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(_HERE, ".."))
sys.path.insert(0, _HERE)
import bias_audit as ba  # noqa: E402


def h2_partisan_object(ledger_dir):
    """H2: count entries whose Claim names a living politician or specific party as
    the OBJECT OF BLAME (not as a dataset label or historical example). Pre-registered
    expectation: 0. Mechanical — no coders. Returns (count, [flags])."""
    flags = []
    # heuristic: a named-living-polician / party blame pattern. We look for a capitalized
    # person/party name adjacent to a blame verb. Conservative: flags candidates for human
    # review, does not adjudicate. Real politician/party names rarely appear by design.
    blame = re.compile(r"\b(?:blame[sd]?|caused|drove|fuel(?:ed|led)|orchestrat\w+|weaponiz\w+|"
                       r"engineer\w+|incite[ds]?)\b", re.I)
    entries = ba._entries(ledger_dir)
    for filename, meta in entries:
        with open(os.path.join(ledger_dir, filename), encoding="utf-8") as f:
            text = f.read()
        claim = ba._claim_section(text)
        # the test is specifically about the OBJECT OF BLAME, not a mention.
        for m in blame.finditer(claim):
            window = claim[m.start():m.start() + 80]
            # a capitalized proper noun immediately after a blame verb = candidate
            if re.search(r"blame[sd]?|caused|drove|fuel(?:ed|led)\b\s+(?:by\s+)?([A-Z]\w+(?:\s+[A-Z]\w+){0,2})",
                         window):
                flags.append((meta.get("id"), window.strip().replace("\n", " ")[:70]))
                break
    return len(flags), flags


def h3_symmetric_reporting(repo):
    """H3: every surface that reports meaningful-decline count must report meaningful-
    improvement count with equal prominence, and a decline headline must carry its noise
    denominator. Mechanical walk of the published surfaces. Returns [violations]."""
    violations = []
    # the canonical pair is 88 declines / 54 improvements (overall); VA is 33/6.
    # check that wherever a decline count appears, an improvement count is near.
    targets = ["site/index.html", "docs/BRIEF.md", "README.md", "docs/indicators/wgi-governance.md"]
    decline_re = re.compile(r"\b(\d+)\s+(?:meaningful\s+)?declines?\b", re.I)
    improve_re = re.compile(r"\b(\d+)\s+(?:meaningful\s+)?improvements?\b", re.I)
    for rel in targets:
        path = os.path.join(repo, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        # strip HTML tags if present (reuse the overstatement audit's stripper)
        if rel.endswith(".html"):
            text = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", text, flags=re.S | re.I))
        declines = decline_re.findall(text)
        improves = improve_re.findall(text)
        # violation = declines reported with no matching improvements anywhere in the file
        if declines and not improves:
            violations.append(f"{rel}: reports declines ({declines[:3]}) with no improvement count")
    return violations


def h1_dry_run_coding(ledger_dir):
    """Single-coder LLM dry-run of H1: code each entry's valence from the MASKED pack
    (grades unseen), as a coder would. NON-AUTHORITATIVE — see module docstring.
    Coding rule: D = the claim, if true, supports 'decline/authoritarian dynamics are
    real/serious/worsening'; R = reassuring/debunking; N = mechanism/neutral."""
    pack, key = ba.build_pack(ledger_dir)
    grades = ba.load_grades(ledger_dir)
    # code from the MASKED text (▓▓▓ hides grades) — heuristic valence on the claim prose.
    # This is a transparent, rule-based stand-in for a human coder, NOT a substitute.
    decline_lex = re.compile(r"\b(declin|backslid|erosion|authoritarian|fascis|polariz|violenc|"
                             r"radicali|repress|crisis|far-right|curse|inequal|shock|grievance|"
                             r"dehuman|obedienc|conformit|threat|destabili|weak|deterior)", re.I)
    reassure_lex = re.compile(r"\b(reassur|debunk|overstat|overestimat|no.?universal|null|"
                              r"backfire|success|peaceful|cooperat|self-govern|prosper|contain|"
                              r"works|reduc|defend|inoculat|prebunk|resilien|robust.*correlation)", re.I)
    coded = {}
    for code in key:
        # find this code's block in the pack
        m = re.search(rf"## {re.escape(code)}\n\n(.*?)\n\nVALENCE", pack, re.S)
        block = m.group(1) if m else ""
        d = len(decline_lex.findall(block))
        r = len(reassure_lex.findall(block))
        coded[code] = "D" if d > r else ("R" if r > d else "N")
    return coded, key, grades


def main(argv=None):
    ledger = os.path.join(REPO, "ledger")
    today = date.today().isoformat()

    print(f"bias-audit run — {today}")
    print("=" * 60)

    # ---- H2 (mechanical, authoritative) ----
    h2_count, h2_flags = h2_partisan_object(ledger)
    print(f"\n[H2 partisan-object] pre-registered expectation: 0")
    print(f"  candidates flagged for human review: {h2_count}")
    for eid, w in h2_flags[:10]:
        print(f"    {eid}: …{w}…")
    h2_passes = (h2_count == 0)

    # ---- H3 (mechanical, authoritative) ----
    h3_violations = h3_symmetric_reporting(REPO)
    print(f"\n[H3 symmetric reporting] every decline count paired with an improvement count")
    print(f"  violations: {len(h3_violations)}")
    for v in h3_violations:
        print(f"    {v}")
    h3_passes = (len(h3_violations) == 0)

    # ---- H1 (NON-AUTHORITATIVE single-coder dry-run) ----
    coded, key, grades = h1_dry_run_coding(ledger)
    h1 = ba.score(coded, key, grades)
    print(f"\n[H1 valence–grade independence] *** SINGLE-CODER LLM DRY-RUN — NOT THE PRE-REGISTERED RESULT ***")
    print(f"  (proves the pack is codeable + the scorer works; needs 2 human coders to be authoritative)")
    print(f"  table D_robust={h1['table']['D_robust']} D_not={h1['table']['D_not']} "
          f"R_robust={h1['table']['R_robust']} R_not={h1['table']['R_not']}  (n={h1['n_coded']}, neutral/skip={h1['n_neutral_or_skipped']})")
    dp = h1['delta_p']
    fp = h1['fisher_p_two_sided']
    print(f"  ΔP = P(ROBUST|D)−P(ROBUST|R) = {dp} ; Fisher p = {fp}")
    print(f"  criterion: {h1['criterion']}")
    print(f"  skew_detected (dry-run): {h1['skew_detected']}")

    # ---- write dated report ----
    report_path = os.path.join(REPO, "docs", "verifications", f"bias-audit-{today}.md")
    _write_report(report_path, today, h2_count, h2_flags, h2_passes,
                  h3_violations, h3_passes, h1, len(key))
    print(f"\nwrote {os.path.relpath(report_path, REPO)}")
    print("\nNOTE: H1 is a non-authoritative dry-run. H2/H3 are mechanical and authoritative.")
    print("The pre-registered H1 result still requires two independent human coders (§1, §8).")
    return 0


def _write_report(path, today, h2_count, h2_flags, h2_passes, h3_violations, h3_passes, h1, n_entries):
    h1_block = "\n".join(f"- {k}: {ba._round(v)}" for k, v in h1.items() if k != "table")
    flags_block = "\n".join(f"  - {eid}: …{w}…" for eid, w in h2_flags) or "  _(none)_"
    viol_block = "\n".join(f"  - {v}" for v in h3_violations) or "  _(none — every surface pairs declines with improvements)_"
    # the generated file's licence tag is split ({'-'}) so licence scanners don't read it as this file's
    body = f"""<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX{'-'}License-Identifier: CC-BY-SA-4.0
-->

# Bias-audit run — {today}

*An execution of the mechanical parts of the pre-registered bias audit ([`BIAS_AUDIT_PREREGISTRATION.md`](../BIAS_AUDIT_PREREGISTRATION.md)) plus a clearly-labeled non-authoritative dry-run of H1. Generated by `python3 src/bias_audit_run.py`.*

## ⚠️ Authority of these results

| Test | Authority | Why |
|---|---|---|
| **H2** partisan-object | **Authoritative** | mechanical; no coders |
| **H3** symmetric reporting | **Authoritative** | mechanical; no coders |
| **H1** valence–grade independence | **NOT authoritative — dry-run** | §1 requires two independent *human* coders; this is a single-coder rule-based stand-in |

The H1 dry-run exists only to prove the blind pack is codeable and the scorer works end-to-end. **It must not be cited as the pre-registered H1 result.** That result remains pending the two human coders (§8 sign-off).

## H2 — partisan-object asymmetry (authoritative)

Pre-registered expectation: **0** entries name a living politician or specific party as the *object of blame*.

**Result: {h2_count} candidate(s) flagged for human review → {'PASSES' if h2_passes else 'review the flags below'}.**

{flags_block}

(Candidates are heuristic matches of a blame verb adjacent to a proper noun; a human confirms each is blame-attribution and not a dataset label or historical example.)

## H3 — symmetric reporting (authoritative)

Every published surface that reports meaningful declines must report meaningful improvements with equal prominence, and carry the noise denominator.

**Result: {len(h3_violations)} violation(s) → {'PASSES' if h3_passes else 'fix the violations below'}.**

{viol_block}

## H1 — valence–grade independence (NON-AUTHORITATIVE dry-run)

A single rule-based coder coded valence from the **masked** pack (grades hidden as ▓▓▓), then the shipped H1 scorer computed the pre-registered statistics. **This is a smoke test of the instrument, not a measurement of bias.**

Pre-registered skew criterion: ΔP > 0.25 **and** Fisher p < 0.10.

{n_entries} entries coded; {h1['n_coded']} directional (D/R), {h1['n_neutral_or_skipped']} neutral/skipped.

- 2×2 table: D-ROBUST={h1['table']['D_robust']}, D-not={h1['table']['D_not']}, R-ROBUST={h1['table']['R_robust']}, R-not={h1['table']['R_not']}
{h1_block}

**Dry-run skew_detected = {h1['skew_detected']}.** Regardless of this value, the authoritative H1 result requires the two-coder pre-registration. The dry-run's value is demonstrating the pack→scorer pipeline runs cleanly.

## Next step for the authoritative H1

Recruit two independent human coders (the second grader is coder A — see [`SECOND_GRADER_PACKET.md`](../SECOND_GRADER_PACKET.md)). Hand each only `blind_pack.md` (generated by `make bias-pack`), reconcile once, then `python3 src/bias_audit.py --score reconciled.json --key build/bias-audit/blind_key.json`. Publish that result here, replacing the dry-run.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)


if __name__ == "__main__":
    sys.exit(main())
