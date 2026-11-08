<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# `site/` — the public landing page (live at <https://lx8.github.io/pharos/>)

A static, dependency-free landing page that explains the project to the general public: what it
is and is not, in plain words; the finding (88% within noise; the decline is in *voice*); what is
inside (ledger · indicators · forecast · simulators · self-audits); how to download and use it,
from just reading to full verification; the forecast's honest negative result; the theory of
change (the lighthouse); the ethical covenant (*watch power, not people*); and the sources.

It is published in four languages:

| Language | Address | Strings |
|---|---|---|
| English | <https://lx8.github.io/pharos/> | [`i18n/en.json`](i18n/en.json) |
| Español | <https://lx8.github.io/pharos/es/> | [`i18n/es.json`](i18n/es.json) |
| Deutsch | <https://lx8.github.io/pharos/de/> | [`i18n/de.json`](i18n/de.json) |
| Português | <https://lx8.github.io/pharos/pt/> | [`i18n/pt.json`](i18n/pt.json) |

## How the pages are built

`index.html` and `es/`, `de/`, `pt/index.html` are **generated** — do not edit them by hand. The
generator, [`../src/build_site.py`](../src/build_site.py), fills one template,
[`template.html`](template.html), with each language's strings and with every figure computed from
the committed data (the same source of truth the counts audit pins). So:

- **To change the wording**, edit `i18n/<lang>.json` (and the same key in every other language),
  then run `make pages` and commit the template/strings together with the regenerated pages.
- **To change the layout**, edit `template.html` (and `style.css`), then `make pages`.
- **Figures are never typed in the strings.** They are placeholders (`{{within_noise_pct}}`,
  `{{concur_decline}}`, …) filled from the data, so all four pages always carry the same numbers.

The build fails loudly when a language file misses, misspells or adds a key, and when a
translated string's literal numbers, links, commands or placeholders differ from the English
string of the same key: translators change the words, never what the words point at.
`make verify-offline` (and the unit tests, hence `make dashboard`) fails if the committed pages are
not exactly a fresh build. The overstatement guard scans every page in its own language.

To **add a language**: add it to `LANGS` in `src/build_site.py`, create `i18n/<code>.json` with every
key, add its unconditional-certainty phrases to `SERIOUS_I18N`/`MEDIUM_I18N` in
`src/audit_overstatement.py` and its page to the `paths` filter in
[`../.github/workflows/pages.yml`](../.github/workflows/pages.yml), then `make pages`. The site
tests fail until each of those steps is done.

## 🌐 How it is published

GitHub Pages serves the site from [`../.github/workflows/pages.yml`](../.github/workflows/pages.yml).
Every push to `main` that changes a page or `style.css` redeploys it. The workflow first re-runs the
page's own checks — the pages equal a fresh build, the pinned figures, the overstatement guard (all
four languages) and the site tests — and then publishes only the generated pages and `style.css`.
The interactive observatory in `app/` needs the local server and is not published.

## Downloading the project

The page links the whole repository as one ZIP file
(<https://github.com/LX8/pharos/archive/refs/heads/main.zip>) from the hero, from the top of the
"Download and use" section and from the footer, in every language.

## Interactive local observatory

Run `./pharos serve` (or `python3 src/pharos.py serve`) from the repository root and open
<http://127.0.0.1:8796/>. The app lives in `app/` and is served by `src/pharos_server.py`; a plain
static file server does not provide its research or verification API. See
[LOCAL_OBSERVATORY.md](../docs/LOCAL_OBSERVATORY.md). The landing page is a separate, static
interface, and the app's interface is in English.

## Preview the landing page locally

```bash
python3 -m http.server -d site 8000   # then visit http://localhost:8000 (and /es/, /de/, /pt/)
```

Opening `index.html` straight from disk also works, but the language links point at folders
(`es/`), which a browser shows as a file listing without a server.

## A custom domain (optional)

To serve the page from a domain of the project's own, add it under Settings → Pages and update
`BASE_URL` in `src/build_site.py` (it sets every page's `canonical`, `og:url` and `hreflang`
addresses), then `make pages`.

## Notes

- The landing page and the local observatory are both named **Pharos**, as in `REPORT.md`;
  they are separate interfaces.
- The page links to the public repository and to documents in it (`docs/BRIEF.md`,
  `ledger/INDEX.md`, `docs/WATCH_REPORT.md`, `docs/LOCAL_OBSERVATORY.md`, `docs/TRUST_SIGNALS.md`,
  `CONTRIBUTING.md`, `STATUS.md`); those documents are in English, which the translated pages say.
- The page embodies the brand: lead with the finding *and* its uncertainty; honesty is the product.
