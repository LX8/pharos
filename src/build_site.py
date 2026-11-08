#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the public landing page — one template, four languages, one set of figures.

`site/index.html` (English) and `site/<lang>/index.html` (Spanish, German, Portuguese) are
GENERATED from `site/template.html` plus the per-language strings in `site/i18n/<lang>.json`.
Every headline figure on the pages — the noise floor, the decline:improvement ratio, the
concurring-country counts, the forecast count, the ledger tallies, the release version — is
injected here from the committed derived data, the same source of truth the counts audit pins.
So a translation cannot carry a stale number: all four pages are built from the same figures. A
strings file that drops, adds or misspells a key fails the build loudly, and so does a translated
string whose literal numbers, links, commands or placeholders differ from the English string of
the same key (`check_parity`) — translators change the words, never what the words point at.

Like brief.py: `--write` (re)generates the pages; no arguments verifies that the committed pages
are byte-identical to a fresh build and exits 1 on drift; `--list` prints the page paths (the
Pages workflow stages exactly those files). Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_counts  # noqa: E402  (the figures come from the same code the counts gate uses)

BASE_URL = "https://lx8.github.io/pharos/"
REPO_URL = "https://github.com/LX8/pharos"

# (code, <html lang>, og:locale, the language's own name for the switcher, page path under site/).
# The English page stays at the root so the published address does not change; every other
# language lives one directory down and shares the one stylesheet.
LANGS = (
    ("en", "en", "en_US", "English", "index.html"),
    ("es", "es", "es_ES", "Español", "es/index.html"),
    ("de", "de", "de_DE", "Deutsch", "de/index.html"),
    ("pt", "pt-BR", "pt_BR", "Português", "pt/index.html"),
)

# Links the strings may embed as {{url_*}} — kept here, once, so a translation can never point
# at a different document than the English page does.
URLS = {
    "url_repo": REPO_URL,
    "url_zip": REPO_URL + "/archive/refs/heads/main.zip",
    "url_issues": REPO_URL + "/issues/new/choose",
    "url_status": REPO_URL + "/blob/main/STATUS.md",
    "url_contributing": REPO_URL + "/blob/main/CONTRIBUTING.md",
    "url_trust": REPO_URL + "/blob/main/docs/TRUST_SIGNALS.md",
    "url_ledger_index": REPO_URL + "/blob/main/ledger/INDEX.md",
    "url_brief": REPO_URL + "/blob/main/docs/BRIEF.md",
    "url_watch_report": REPO_URL + "/blob/main/docs/WATCH_REPORT.md",
    "url_local_observatory": REPO_URL + "/blob/main/docs/LOCAL_OBSERVATORY.md",
    "url_python": "https://www.python.org/downloads/",
}

# Values the generator computes per page; a strings file may not define these.
PAGE_KEYS = ("lang", "html_lang", "og_locale", "css_href", "canonical", "alternates", "lang_links",
             "n_forecasts_fmt")

# Thousands separator per language (the decimal separator is never needed in visible prose:
# the one-decimal bar widths are CSS values and keep the dot).
_THOUSANDS = {"en": ",", "es": ".", "de": ".", "pt": "."}

PLACEHOLDER = re.compile(r"\{\{([a-z][a-z0-9_]*)\}\}")
_TAG = re.compile(r"<[^>]+>")
_ENTITY = re.compile(r"&(?:[A-Za-z]+|#\d+|#x[0-9A-Fa-f]+);")
_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
_HREF = re.compile(r'href="([^"]*)"')
_CODE = re.compile(r"<code>(.*?)</code>", re.S)


def page_paths():
    """The generated pages, relative to site/ — what the Pages workflow stages."""
    return [path for *_, path in LANGS]


def fmt_int(n, lang):
    """2600 -> '2,600' (en) / '2.600' (es, de, pt)."""
    return f"{int(n):,}".replace(",", _THOUSANDS[lang])


def _version(repo):
    with open(os.path.join(repo, "CITATION.cff"), encoding="utf-8") as f:
        m = re.search(r"^version:\s*\"?([0-9][0-9A-Za-z.\-]*)\"?\s*$", f.read(), re.M)
    if not m:
        raise RuntimeError("CITATION.cff: no `version:` line to put in the page footer")
    return m.group(1)


def figures(repo):
    """Every number the pages cite, straight from the committed data (never typed by hand)."""
    fig = audit_counts.compute_derived_figures(repo)
    counts = audit_counts.compute_actual(repo)
    return {
        "within_noise_pct": fig["within_noise_pct"],
        "meaningful_declines": fig["meaningful_declines"],
        "meaningful_improvements": fig["meaningful_improvements"],
        "concur_decline": fig["concur_decline"],
        "concur_decline_full3": fig["concur_decline_full3"],
        # CSS widths for the stacked bar — a dot decimal in every language
        "bar_noise_pct1": fig["bar_noise_pct1"],
        "bar_decline_pct1": fig["bar_decline_pct1"],
        "bar_improve_pct1": fig["bar_improve_pct1"],
        # the rounded shares the bar's accessible label speaks
        "decline_pct_round": round(fig["bar_decline_pct1"]),
        "improve_pct_round": round(fig["bar_improve_pct1"]),
        "n_forecasts": fig["n_forecasts"],
        "ledger_entries": counts["ledger_entries"],
        "robust": counts["robust"],
        "contested": counts["contested"],
        "refuted": counts["refuted"],
        "open": counts["open"],
        "sim_count": counts["sim_count"],
        "version": _version(repo),
    }


def load_strings(repo, code):
    path = os.path.join(repo, "site", "i18n", f"{code}.json")
    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"{path}: invalid JSON ({e})") from e
    if not isinstance(data, dict) or not all(isinstance(v, str) for v in data.values()):
        raise RuntimeError(f"{path}: must be a flat object of string values")
    return data


def check_strings(template, strings, reserved):
    """Fail loudly on a translation that drifts from the English key set, on a key no page uses
    (a typo would otherwise silently drop a paragraph), or on a key that shadows a generated value."""
    en = set(strings["en"])
    for code, s in strings.items():
        if set(s) != en:
            raise KeyError(f"site/i18n/{code}.json keys differ from en.json — "
                           f"missing {sorted(en - set(s))}, extra {sorted(set(s) - en)}")
    clash = en & set(reserved)
    if clash:
        raise KeyError(f"site/i18n/*.json define generated keys: {sorted(clash)}")
    referenced = set(PLACEHOLDER.findall(template))
    for s in strings.values():
        for v in s.values():
            referenced |= set(PLACEHOLDER.findall(v))
    unused = en - referenced
    if unused:
        raise KeyError(f"site/i18n keys never used by the template: {sorted(unused)}")


def _numbers(s):
    """The literal numbers in a string, separator-insensitive ('1,200' == '1.200'), ignoring
    placeholders, tags and entities — so a translation may localise the format, not the value."""
    text = _ENTITY.sub(" ", _TAG.sub(" ", PLACEHOLDER.sub(" ", s)))
    return sorted(re.sub(r"[.,]", "", n) for n in _NUMBER.findall(text))


def fingerprint(s):
    """What a translation must carry over unchanged from the English string of the same key."""
    return {
        "numbers": _numbers(s),
        "placeholders": sorted(PLACEHOLDER.findall(s)),
        "links": sorted(_HREF.findall(s)),
        "commands": sorted(_CODE.findall(s)),
    }


def check_parity(strings):
    """Fail if any translated string states a different number, figure, link or command than the
    English string of the same key. Translators change the words; never what the words point at."""
    en = strings["en"]
    problems = []
    for code, table in strings.items():
        if code == "en":
            continue
        for key, value in table.items():
            want, got = fingerprint(en[key]), fingerprint(value)
            problems += [f"site/i18n/{code}.json `{key}`: {part} {got[part]} != en {want[part]}"
                         for part in want if want[part] != got[part]]
    if problems:
        raise ValueError("a translation drifted from the English page:\n  " + "\n  ".join(problems))


def render(template, values):
    """Substitute {{key}} placeholders. A string may itself embed a key (a URL, a figure), so the
    pass repeats until stable; an unknown key raises instead of leaking `{{...}}` into the page."""
    out = template
    for _ in range(5):
        missing = []

        def sub(m):
            key = m.group(1)
            if key not in values:
                missing.append(key)
                return m.group(0)
            return str(values[key])

        new = PLACEHOLDER.sub(sub, out)
        if missing:
            raise KeyError(f"unknown placeholder(s): {sorted(set(missing))}")
        if new == out:
            return out
        out = new
    raise ValueError("placeholders nested too deeply")


def _alternates():
    lines = [f'  <link rel="alternate" hreflang="{html_lang}" href="{BASE_URL}{path[:-len("index.html")]}">'
             for _code, html_lang, _loc, _name, path in LANGS]
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{BASE_URL}">')
    return "\n".join(lines)


def _lang_links(current, depth):
    out = []
    for code, html_lang, _loc, name, path in LANGS:
        href = "../" * depth + path[:-len("index.html")] or "./"
        cur = ' aria-current="page"' if code == current else ""
        out.append(f'<a href="{href}" hreflang="{html_lang}" lang="{html_lang}"{cur}>{name}</a>')
    return "".join(out)


def build_all(repo):
    """{page path under site/: html} for every language — pure, deterministic."""
    with open(os.path.join(repo, "site", "template.html"), encoding="utf-8") as f:
        template = f.read()
    strings = {code: load_strings(repo, code) for code, *_ in LANGS}
    fig = figures(repo)
    check_strings(template, strings, set(URLS) | set(fig) | set(PAGE_KEYS))
    check_parity(strings)
    pages = {}
    for code, html_lang, og_locale, _name, path in LANGS:
        depth = path.count("/")
        values = dict(URLS)
        values.update(fig)
        values.update(strings[code])
        values.update({
            "lang": code,
            "html_lang": html_lang,
            "og_locale": og_locale,
            "css_href": "../" * depth + "style.css",
            "canonical": BASE_URL + path[:-len("index.html")],
            "alternates": _alternates(),
            "lang_links": _lang_links(code, depth),
            "n_forecasts_fmt": fmt_int(fig["n_forecasts"], code),
        })
        pages[path] = render(template, values)
    return pages


def _default_repo():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate/verify the landing page in every language.")
    ap.add_argument("--repo", default=_default_repo())
    ap.add_argument("--write", action="store_true", help="(re)write site/index.html and site/<lang>/index.html")
    ap.add_argument("--list", action="store_true", help="print the generated page paths (relative to site/)")
    args = ap.parse_args(argv)

    if args.list:
        print("\n".join(page_paths()))
        return 0

    pages = build_all(args.repo)
    if args.write:
        for rel, html in pages.items():
            out = os.path.join(args.repo, "site", rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8", newline="\n") as f:
                f.write(html)
            print(f"wrote site/{rel}")
        return 0

    stale = []
    for rel, html in pages.items():
        out = os.path.join(args.repo, "site", rel)
        try:
            # universal newlines: a CRLF checkout (core.autocrlf on Windows) is not drift
            with open(out, encoding="utf-8") as f:
                committed = f.read()
        except FileNotFoundError:
            committed = None
        if committed != html:
            stale.append(rel)
    if stale:
        print("FAIL: committed landing page(s) differ from a fresh build — run `make pages` and commit:")
        for rel in stale:
            print(f"  ✗ site/{rel}")
        return 1
    print(f"site: ok — {len(pages)} pages ({', '.join(code for code, *_ in LANGS)}) match a fresh build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
