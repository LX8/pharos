#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Overstatement audit — guard the project's own honesty discipline.

An honesty-first project's worst regression is claim-creep: a future edit slips an
absolute ("definitively proven", "beyond doubt", "mathematically proves") into a
graded claim that the evidence cannot carry. This scans the load-bearing prose —
the ledger entries, the article, and REPORT.md — for that language.

It is deliberately calibrated to the *current, carefully-hedged* corpus: the SERIOUS
patterns are unconditional-certainty phrases that appear **nowhere** today (so the
gate is green now and bites only on new overclaims); softer rhetoric is MEDIUM
(reported, non-failing). Citations, quotations, and YAML frontmatter are exempt — an
entry may *quote* a strong word, and a REFUTED entry may say "debunked". Narrowed for
social-science prose.

Exit 1 if any SERIOUS finding; pure core (`scan_text`) + thin CLI.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

# Unconditional-certainty language an empirical social-science claim must never use.
SERIOUS = [
    (re.compile(r"\bdefinitively\b", re.I), "absolute-certainty adverb"),
    (re.compile(r"\bconclusively\b", re.I), "absolute-certainty adverb"),
    (re.compile(r"\birrefutabl\w*\b", re.I), "claims irrefutability"),
    (re.compile(r"\bincontrovertibl\w*\b", re.I), "claims incontrovertibility"),
    (re.compile(r"\bbeyond (?:any |all )?doubt\b", re.I), "absolute-certainty phrase"),
    (re.compile(r"\b100\s*%\s*(?:certain|sure|proven|proof)\b", re.I), "false precision of certainty"),
    (re.compile(r"\bmathematically\s+prov(?:es|en|able)\b", re.I), "claims mathematical proof of an empirical matter"),
    (re.compile(r"\b(?:is|are)\s+impossible\b", re.I), "unconditional impossibility", "needs_conditional"),
]
# Softer rhetoric — reported but does not fail the gate.
MEDIUM = [
    (re.compile(r"\bobviously\b", re.I), "rhetorical certainty"),
    (re.compile(r"\bundeniabl\w*\b", re.I), "rhetorical certainty"),
    (re.compile(r"\bdebunk\w*\b", re.I), "loaded framing ('debunk')"),
]
# A conditional within this many chars after "is/are impossible" exempts it.
_CONDITIONAL = re.compile(r"\b(?:under|given|if|unless|without|absent|barring|outside|when|assuming)\b", re.I)


def _in_quotes(line, idx):
    """True if the char at idx sits inside a double-quoted span (odd quotes before it)."""
    return line[:idx].count('"') % 2 == 1


def _is_exempt(line, idx):
    """Citations, quotes, blockquotes, frontmatter fields — not prose claims.

    Markdown bullets are deliberately NOT blanket-exempt: claim-bearing prose in the
    ledger is overwhelmingly written as `- ` bullets, and exempting all of them un-scans
    the corpus that most needs scanning. A *citation* bullet is already covered by the URL
    rule (source bullets carry a link), so dropping the bullet exemption keeps citations
    safe while making claim bullets subject to the gate.
    """
    s = line.lstrip()
    if s.startswith(">") or "http" in line:
        return True            # blockquote / any line with a URL (covers source bullets)
    if "falsification_trigger" in line:
        return True            # the trigger *describes* what would withdraw the claim
    return _in_quotes(line, idx)


def scan_text(text, filename):
    """Pure. Return [(severity, filename, lineno, phrase, why)] for one document.

    YAML frontmatter (the first --- … --- block) is skipped entirely.
    """
    findings = []
    in_front = False
    seen_front = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip() == "---" and not seen_front:
            in_front = not in_front
            if not in_front:
                seen_front = True
            continue
        if in_front:
            continue
        for entry in SERIOUS:
            rx, why = entry[0], entry[1]
            for m in rx.finditer(line):
                if _is_exempt(line, m.start()):
                    continue
                if len(entry) == 3 and entry[2] == "needs_conditional" and \
                        _CONDITIONAL.search(line[m.end():m.end() + 40]):
                    continue   # "impossible under X" is a scoped, legitimate claim
                findings.append(("SERIOUS", filename, n, m.group(0), why))
        for rx, why in MEDIUM:
            for m in rx.finditer(line):
                if _is_exempt(line, m.start()):
                    continue
                findings.append(("MEDIUM", filename, n, m.group(0), why))
    return findings


def _scope(repo):
    """The load-bearing graded prose: ledger entries + the article + REPORT + the
    public site.

    Verification docs and plan-for-peace are excluded — they legitimately use verdict
    words ('REFUTED', 'FATAL', 'BREAKS') as graded labels, not as claims. The public
    site IS included: it is the page a stranger lands on, so claim-creep there is the
    most credibility-defining regression of all. HTML is reduced to its text nodes
    before scanning (tags/attributes are not prose).
    """
    out = []
    led = os.path.join(repo, "ledger")
    if os.path.isdir(led):
        out += [os.path.join(led, f) for f in sorted(os.listdir(led))
                if f.startswith("SAA-") and f.endswith(".md")]
    art = os.path.join(repo, "docs", "article")
    if os.path.isdir(art):
        out += [os.path.join(art, f) for f in sorted(os.listdir(art)) if f.endswith(".md")]
    rep = os.path.join(repo, "REPORT.md")
    if os.path.exists(rep):
        out.append(rep)
    # the public site — the marketing layer where overclaim matters most.
    sit = os.path.join(repo, "site")
    if os.path.isdir(sit):
        out += [os.path.join(sit, f) for f in sorted(os.listdir(sit)) if f.endswith((".html", ".md"))]
    return out


def _strip_html(text):
    """Reduce HTML to its visible text nodes, so regexes scan prose not markup.

    Drops everything inside <style>/<script> (not prose), then tags and their
    attributes (an `alt="definitively"` on an image is not a claim). Entity-decodes
    the common ones so 'beyond&nbsp;doubt' is still caught. Conservative: it may leave
    some non-prose (e.g. JSON-LD), but the SERIOUS patterns are sentence-shaped and
    won't false-positive on structured data.
    """
    # remove <style>...</style> and <script>...</script> blocks entirely
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", text, flags=re.S | re.I)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)            # HTML comments
    text = re.sub(r"<[^>]+>", " ", text)                            # all remaining tags
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">")
                .replace("&#39;", "'").replace("&quot;", '"'))
    return text


def _default_repo():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Flag overstated/absolute language in graded prose.")
    ap.add_argument("--repo", default=_default_repo())
    args = ap.parse_args(argv)

    findings = []
    for path in _scope(args.repo):
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        text = _strip_html(raw) if path.endswith(".html") else raw
        findings += scan_text(text, os.path.relpath(path, args.repo))

    serious = [f for f in findings if f[0] == "SERIOUS"]
    medium = [f for f in findings if f[0] == "MEDIUM"]
    print(f"overstatement audit — {len(serious)} SERIOUS, {len(medium)} MEDIUM")
    for sev, fn, n, phrase, why in serious + medium:
        print(f"  [{sev:>7}] {fn}:{n}  «{phrase}» — {why}")
    if serious:
        print("FAIL: graded prose makes an unconditional claim the evidence cannot carry.")
        return 1
    print("overstatement: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
