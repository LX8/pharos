<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# `site/` — the public landing page (live at <https://lx8.github.io/pharos/>)

A static, dependency-free landing page (`index.html` + `style.css`) presenting the project
honestly: the finding (88% within noise; the decline is in *voice*), the open commons (ledger ·
indicator · simulators · what-is-tested), the theory of change (the lighthouse), the method
(verifications), and the ethical covenant (*watch power, not people*).

## 🌐 It is live

The landing page is published with GitHub Pages at <https://lx8.github.io/pharos/>. Every push to
`main` that changes `site/index.html` or `site/style.css` redeploys it through
[`../.github/workflows/pages.yml`](../.github/workflows/pages.yml). That workflow first re-runs the
page's own checks (the pinned figures, the overstatement guard and the site tests) and then publishes
only those two files: the interactive observatory in `site/app/` needs the local server and is not
published.

## Interactive local observatory

Run `./pharos serve` from the repository root and open <http://127.0.0.1:8796/>.
The app lives in `site/app/` and is served by `src/pharos_server.py`; a plain static
file server does not provide its research or verification API. See
[LOCAL_OBSERVATORY.md](../docs/LOCAL_OBSERVATORY.md). The landing page is a separate,
static interface.

## Preview the landing page locally

Just open `site/index.html` in a browser (no build step, no dependencies), or:
```bash
python3 -m http.server -d site 8000   # then visit http://localhost:8000
```

## A custom domain (optional)

To serve the page from a domain of the project's own, add it under Settings → Pages and update the
page's `canonical` and `og:url` tags to match.

## Notes

- The landing page and the local observatory are both named **Pharos**, as in `REPORT.md`;
  they are separate interfaces.
- The page links to the public repository and to two of its documents (`docs/TRUST_SIGNALS.md`,
  `STATUS.md`).
- The page embodies the brand: lead with the finding *and* its uncertainty; honesty is the product.
