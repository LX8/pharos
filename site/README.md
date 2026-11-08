<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# `site/` — the public landing page (built, **not deployed**)

A static, dependency-free landing page (`index.html` + `style.css`) presenting the project
honestly: the finding (88% within noise; the decline is in *voice*), the open commons (ledger ·
indicator · simulators · what-is-tested), the theory of change (the lighthouse), the method
(verifications), and the ethical covenant (*watch power, not people*).

## 🔒 It is NOT live

**GitHub Pages is OFF**, so this landing page is not deployed. Deploying it is a separate
decision from publishing the repository (see [`../STATUS.md`](../STATUS.md)).

## Interactive local observatory

Run `./pharos serve` from the repository root and open <http://127.0.0.1:8796/>.
The app lives in `site/app/` and is served by `src/pharos_server.py`; a plain static
file server does not provide its research or verification API. See
[LOCAL_OBSERVATORY.md](../docs/LOCAL_OBSERVATORY.md). The original landing page below
remains separate and undeployed.

## Preview the landing page locally

Just open `site/index.html` in a browser (no build step, no dependencies), or:
```bash
python3 -m http.server -d site 8000   # then visit http://localhost:8000
```

## If it is deployed (one of)

- **Simplest:** Settings → Pages → Source = "Deploy from a branch" → `main` / `/site` *(after moving
  or symlinking, since Pages serves root or `/docs`, not `/site`)*; **or** put the site in `/docs` and
  serve from there; **or** add a Pages Action that publishes `site/`.
- Then point a domain (e.g. `atyguasu.org` — check availability first) at it.

## Notes

- The static landing page retains its earlier **"Aty Guasu"** working name.
  The implemented local observatory is **Pharos**, as named in `REPORT.md`;
  these are separate interfaces.
- The page names repository documents by path; it does not link to them yet.
- The page embodies the brand: lead with the finding *and* its uncertainty; honesty is the product.
