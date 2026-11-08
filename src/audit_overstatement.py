#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Overstatement audit — guard the project's own honesty discipline.

An honesty-first project's worst regression is claim-creep: a future edit slips an
absolute ("definitively proven", "beyond doubt", "mathematically proves") into a
graded claim that the evidence cannot carry. This scans the load-bearing prose —
the ledger entries, the article, REPORT.md and the public landing page in all four of its
languages (English, Spanish, German, Portuguese) — for that language.

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

# The public landing page is published in four languages (src/build_site.py builds site/es/,
# site/de/ and site/pt/ from one template). The English patterns above run on every page; these
# add each language's own unconditional-certainty phrases, applied to the page in that language.
# Calibrated like the English list: zero hits on today's pages, so the gate bites only on a new
# overclaim slipped into a translation.
SERIOUS_I18N = {
    "es": [
        (re.compile(r"\bdefinitivamente\b", re.I), "absolute-certainty adverb"),
        (re.compile(r"\bconcluyentemente\b", re.I), "absolute-certainty adverb"),
        (re.compile(r"\birrefutables?\b", re.I), "claims irrefutability"),
        (re.compile(r"\bincontrovertibles?\b", re.I), "claims incontrovertibility"),
        (re.compile(r"\bm[áa]s all[áa] de (?:toda |cualquier )?duda\b", re.I), "absolute-certainty phrase"),
        (re.compile(r"\bsin (?:ninguna|lugar a) dudas?\b", re.I), "absolute-certainty phrase"),
        (re.compile(r"\b100\s*%\s*(?:segur|ciert|demostrad|probad)[oa]s?\b", re.I), "false precision of certainty"),
        (re.compile(r"\bmatem[áa]ticamente\s+(?:demostrad|probad|demuestra|prueba)\w*", re.I),
         "claims mathematical proof of an empirical matter"),
        (re.compile(r"\b(?:es|son)\s+imposibles?\b", re.I), "unconditional impossibility", "needs_conditional"),
    ],
    "de": [
        (re.compile(r"\bdefinitiv\b", re.I), "absolute-certainty adverb"),
        (re.compile(r"\bendgültig\s+(?:bewiesen|belegt|nachgewiesen|geklärt)\b", re.I), "absolute-certainty phrase"),
        (re.compile(r"\bzweifelsfrei\w*", re.I), "absolute-certainty adverb"),
        (re.compile(r"\bohne (?:jeden|jeglichen|den geringsten) Zweifel\b", re.I), "absolute-certainty phrase"),
        (re.compile(r"\bunwiderlegba\w*", re.I), "claims irrefutability"),
        (re.compile(r"\bunumstößlich\w*", re.I), "claims incontrovertibility"),
        (re.compile(r"\b100\s*%\s*(?:sicher|bewiesen|belegt)\b", re.I), "false precision of certainty"),
        (re.compile(r"\bmathematisch\s+(?:bewiesen|beweisbar|belegt|nachgewiesen)\b", re.I),
         "claims mathematical proof of an empirical matter"),
        (re.compile(r"\b(?:ist|sind)\s+unmöglich\b", re.I), "unconditional impossibility", "needs_conditional"),
    ],
    "pt": [
        (re.compile(r"\bdefinitivamente\b", re.I), "absolute-certainty adverb"),
        (re.compile(r"\bconclusivamente\b", re.I), "absolute-certainty adverb"),
        (re.compile(r"\birrefut[áa]ve(?:l|is)\b", re.I), "claims irrefutability"),
        (re.compile(r"\b(?:incontrovers[oa]s?|incontest[áa]ve(?:l|is))\b", re.I), "claims incontrovertibility"),
        (re.compile(r"\bal[ée]m de (?:qualquer|toda) d[úu]vida\b", re.I), "absolute-certainty phrase"),
        (re.compile(r"\bsem (?:sombra de|nenhuma) d[úu]vida\b", re.I), "absolute-certainty phrase"),
        (re.compile(r"\b100\s*%\s*(?:cert|segur|provad|comprovad)[oa]s?\b", re.I), "false precision of certainty"),
        (re.compile(r"\bmatematicamente\s+(?:provad|comprovad|demonstrad|prova|comprova|demonstra)\w*", re.I),
         "claims mathematical proof of an empirical matter"),
        (re.compile(r"\b(?:é|são)\s+imposs[íi]ve(?:l|is)\b", re.I), "unconditional impossibility", "needs_conditional"),
    ],
}
MEDIUM_I18N = {
    "es": [(re.compile(r"\bobviamente\b", re.I), "rhetorical certainty"),
           (re.compile(r"\b(?:innegabl|indiscutibl)\w*", re.I), "rhetorical certainty")],
    "de": [(re.compile(r"\boffensichtlich\w*", re.I), "rhetorical certainty"),
           (re.compile(r"\b(?:unbestreitbar|unleugbar)\w*", re.I), "rhetorical certainty")],
    "pt": [(re.compile(r"\bobviamente\b", re.I), "rhetorical certainty"),
           (re.compile(r"\b(?:ineg[áa]ve|indiscut[íi]ve)\w*", re.I), "rhetorical certainty")],
}
# The same scoped-claim exemption ("impossible WITHOUT a coalition"), in the page's language.
_CONDITIONAL_I18N = re.compile(
    r"\b(?:sin|si|bajo|salvo|cuando|ohne|wenn|falls|unter|au(?:ß|ss)er|sofern|solange"
    r"|sem|se|sob|caso|quando)\b", re.I)


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


def scan_text(text, filename, lang="en"):
    """Pure. Return [(severity, filename, lineno, phrase, why)] for one document.

    YAML frontmatter (the first --- … --- block) is skipped entirely. `lang` adds that
    language's patterns (SERIOUS_I18N / MEDIUM_I18N) to the English ones.
    """
    serious = SERIOUS + SERIOUS_I18N.get(lang, [])
    medium = MEDIUM + MEDIUM_I18N.get(lang, [])
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
        for entry in serious:
            rx, why = entry[0], entry[1]
            for m in rx.finditer(line):
                if _is_exempt(line, m.start()):
                    continue
                tail = line[m.end():m.end() + 40]
                if len(entry) == 3 and entry[2] == "needs_conditional" and (
                        _CONDITIONAL.search(tail) or (lang != "en" and _CONDITIONAL_I18N.search(tail))):
                    continue   # "impossible under X" is a scoped, legitimate claim
                findings.append(("SERIOUS", filename, n, m.group(0), why))
        for rx, why in medium:
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
        # the translated landing pages (src/build_site.py), one directory down, scanned in their language
        out += [os.path.join(sit, code, "index.html") for code in sorted(SERIOUS_I18N)
                if os.path.exists(os.path.join(sit, code, "index.html"))]
    return out


def _lang_of(path):
    """The language a scoped file is written in: a translated page lives at site/<lang>/index.html."""
    parts = os.path.normpath(path).split(os.sep)
    if len(parts) >= 3 and parts[-3] == "site" and parts[-2] in SERIOUS_I18N:
        return parts[-2]
    return "en"


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
        findings += scan_text(text, os.path.relpath(path, args.repo), _lang_of(path))

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
