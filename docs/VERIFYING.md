<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Verifying this repository

> **The claim this project makes about itself:** *every load-bearing property is
> machine-checked, and you can run the check yourself, offline, deterministically, for free.*
> This page is how. Knowledge that asks to be trusted must be checkable — so the verification
> here is a first-class artifact, not an afterthought.

A clone reproduces the entire quantitative pillar and passes every gate with **no network, no
paid CI, and nothing but the Python standard library**. There is no `pip install`. Any
Python ≥ 3.9 works — the full gate is verified green on the stock macOS `/usr/bin/python3`
(3.9.6) and on 3.12 (the Dockerfile's pin), so "runs anywhere" is a tested property, not a hope.

```bash
make dashboard       # one GREEN/RED report across every offline audit  (start here)
make verify-offline  # deterministic, NO network — recompute from pinned snapshots + all gates
make verify          # the full gate, including a LIVE refresh of the indicators from source
make hooks           # install the free local CI (pre-commit → dashboard, pre-push → verify-offline)
```

---

## 1. The verification ladder

Four rungs, fastest first. Each is idempotent and self-contained.

| Command | Network | What it does | When |
| --- | --- | --- | --- |
| **`make dashboard`** | none | Runs all seven audits below in sequence and prints a single GREEN/RED verdict (`--json` for machines). | The everyday check — seconds. |
| **`make verify-offline`** | **none** | Recomputes the indicators, divergence, and forecast **from pinned snapshots**, fails on any drift from the committed `data/derived/*`, then runs the full audit suite. | The reproducibility gate — proves a clone gets byte-identical results. |
| **`make verify`** | live | Everything in the audits, then a **live** refetch of the World Bank / OWID sources to recompute the indicators (catches upstream schema changes). | The release-candidate moment. |
| **`make hooks`** | none | Sets `core.hooksPath .githooks`: **pre-commit** runs `make dashboard`, **pre-push** runs `make verify-offline`. | Once per clone — free local CI. |

---

## 2. The seven audits (what `make dashboard` checks)

Each is a pure-core + thin-CLI Python module under [`src/`](../src), independently runnable
(`python3 src/<audit>.py`) and individually exposed as a `make` target.

| Audit | `make` target | Gate — fails the build if… |
| --- | --- | --- |
| **Unit tests** | `test` | any of the offline tests fail (the load-bearing calculations, the simulator validations against published results, and every audit's own self-test). |
| **Ledger structure** | `validate` | any ledger entry violates [`GRADING_PROTOCOL.md`](GRADING_PROTOCOL.md) — missing field, invalid grade, no falsification trigger, no sources, or disagreement with `ledger/index.json`. |
| **Ledger freshness** | `staleness` | any entry is past its grade-based review interval (ROBUST/REFUTED 540 d, CONTESTED 270 d, OPEN 180 d) — so maintainer lapse is **loud**, not silent rot. |
| **Overstatement** | `overstatement` | graded prose makes an unconditional-certainty claim the evidence can't carry (`definitively`, `proven`, bare `impossible`, …). Calibrated to **0 SERIOUS** on the hedged corpus. |
| **Doc counts** | `counts` | a headline number (entry count, per-grade tally, test count) in the README / STATUS / site drifts from what the repo actually contains. |
| **Threat model** | `threat-model` | any published `data/derived/*` or `data/snapshots/*` file carries a column or key **below country/institution level** — the [`THREAT_MODEL.md`](../THREAT_MODEL.md) §4.3 spatial floor, *watch power not people*, enforced in code. |
| **Ledger index** | `index` | the committed [`ledger/INDEX.md`](../ledger/INDEX.md) (the human read surface + falsification watch) has drifted from the entries — `make index` regenerates it from the frontmatter, so the browseable view can never silently lie about the source of truth. |

`make verify` adds the live indicator/divergence/forecast recompute on top of these.

---

## 3. Offline determinism (the reproducibility guarantee)

The default `make verify` hits three live sources (World Bank WGI; V-Dem and Freedom House via
Our World in Data). To make the gate **deterministic and runnable by anyone**, the raw inputs are
pinned:

- **Snapshots** live in [`data/snapshots/`](../data/snapshots) — the WGI JSON, the V-Dem and
  Freedom House CSVs — each committed and stamped with its source URL, a **sha256** of the input,
  and `fetched_utc`.
- **`--offline` / `SAA_OFFLINE=1`** makes every indicator read the snapshot instead of the network.
  `make snapshot` is the deliberate *re-pin* step (refetch + regenerate, then review the diff).
- **`make verify-offline`** recomputes `data/derived/*` from the snapshots and **fails on any diff**
  against the committed outputs. So a clone gets byte-identical numbers, and any change to a
  load-bearing calculation must be deliberately re-pinned and committed — the drift gate doubles as
  a regression test for the math.
- A stdlib **[`Dockerfile`](../Dockerfile)** (`docker build -t pharos . && docker run --rm pharos`)
  runs the same offline gate on any machine.

**Free local CI.** `make hooks` installs git hooks that run the dashboard on commit and the offline
gate on push — no cloud, no billing, the same checks a reviewer would run. Since publication the
GitHub Actions workflow (`.github/workflows/verify.yml`) also runs the offline gate on every push to
`main` and on pull requests.

**Is the pin still fresh?** Offline determinism means the numbers never drift by accident — but it
also means they only reflect the world *as of the pin*. **`make drift`** answers whether upstream has
moved: it recomputes the indicators and forecast from the **live** sources, compares the substantive
numbers against the committed pin (ignoring the `mode`/`fetched_utc` stamps), reports any change, and
then **restores the pin byte-for-byte** — it *reads* the live world, it never adopts it. Drift is not
an error; it means a re-pin (`make snapshot`, human-reviewed) is due, because adopting new upstream
data shifts the published numbers. (For the last recorded check and what it found, see
[`verifications/LIVE_DRIFT_2026-07-24.md`](verifications/LIVE_DRIFT_2026-07-24.md).)

---

## 4. Adversarial review regime (verification beyond the gates)

The automated gates prove the repo is internally consistent and reproducible. On top of them, the
ledger and code have been put through repeated **adversarial review** — independent agents tasked to
*break* a claim, each finding then verified by a separate skeptic before it is acted on. The record:

| Round | Surface swept | Outcome |
| --- | --- | --- |
| **1** | The threat-model data gate's own coverage | Denylist gaps fixed (snake-case PII, arbitrary admin levels). |
| **2** | The whole repo (code · sims · tests · ledger · licensing) | 5 test-scope / not-overclaim defects fixed; **0 correctness bugs**. |
| **3** | **Every citation** across the ledger + `REPORT.md`, web-verified | **No fabricated, no retracted sources**; 6 attribution slips corrected. |
| **4** | **Every load-bearing formula**, differentially | 5 of 6 reproduced **bit-exactly** by an independent reimplementation; 1 real rounding bug fixed. |
| **5** | **Every grade**, recalibrated against the rubric | **0 rubric violations** — the grading holds; the composition convention was documented. |
| **6** | **Each new entry on addition** (citations re-checked, grade vs rubric, overclaim) | ongoing: e.g. SAA-036/037 clean, one "cite only what is measured" slip in SAA-038 caught and fixed. |
| **7** | **The tooling & summary layer** (generators, client, scorer, gates, site prose) | 10 confirmed defects fixed — incl. two *unequal-significance-bar overclaims in our own generated prose and on the site* (the canonical indicator doc was always right; the drift arose in summarization), a blind pack that leaked grade words, and gate gaps (encoded geolocation, national-ID columns). |

The discipline is the point: adversarial re-checks have repeatedly caught real errors (a fabricated
citation, a mis-scoped falsification trigger, a forecast-skill rounding bug), and each fix is recorded in
[`CHANGELOG.md`](../CHANGELOG.md). See [`CHRONICLE.md`](CHRONICLE.md) for the full narrative.

---

## 5. What is *not* claimed

Verification proves the numbers are reproducible and the prose doesn't overstate — **not** that the
underlying science is settled. The honest tiering of every claim, from machine-verified down to
untestable-in-principle, is in [`what-is-tested.md`](what-is-tested.md); the grading rubric is
[`GRADING_PROTOCOL.md`](GRADING_PROTOCOL.md). A green `make verify` is a floor on honesty and
reproducibility, not a ceiling on doubt.
