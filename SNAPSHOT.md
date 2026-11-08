<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# About this repository

Pharos — Science Against Authoritarianism — is a project for the public, built for the good
of humanity and the environment. It is offered free of charge and carries no personal credit:
every notice credits **The Pharos contributors**.

This repository was published on **2026-11-08** as a verified snapshot (release 0.7.0). Its
earlier development history is not public; the repository starts from a single commit.

## What it contains

- **The research:** the graded evidence ledger (41 entries), the governance indicators, the
  pre-registered forecast and the seven validated mechanism simulators. See the [README](README.md).
- **The local Pharos observatory** (`./pharos serve`, built 2026-09-23): a loopback-only browser
  app over that research, including real offline verification runs with receipts.
- **The forward score** (2026-10-31): the frozen 1-year forecasts scored against the 2025 V-Dem
  release (`make score`, `make cycle`; see the [CHANGELOG](CHANGELOG.md)).

## Changes made for publication

- **Credit made collective.** Personal names, e-mail addresses, ORCID iDs and account handles were
  replaced by "The Pharos contributors" in every license header and in `LICENSE`, `NOTICE`,
  `AUTHORS`, `CITATION.cff`, `.zenodo.json`, `REUSE.toml`, the README, the report and the landing
  page. The licenses themselves are unchanged.
- **Private material removed.** Notes about private working setups and unrelated projects were
  removed or reworded; one internal survey document and the code-owners file were dropped.
  `.gitignore` now blocks secrets, credentials and local AI-assistant files.
- **Accuracy fixes from an independent pre-publication review** (privacy, integration and honesty
  lenses; each finding re-checked by a separate skeptic): status lines that called the repository
  private were updated; the publication gate now records the pre-registered commitments that are
  still open (see [STATUS.md](STATUS.md)); the licensing text now names the datasets actually
  analysed, says that small pinned extracts are redistributed under their upstream licences, and
  describes the covenant as a good-faith request; the missing `LICENSES/CC-BY-4.0.txt` was added;
  one test that reached the network during the offline gate was made hermetic; and the release is
  numbered 0.7.0 throughout.
- **Continuous integration enabled.** `.github/workflows/verify.yml` now runs on pushes and pull
  requests (it was manual-only while the repository was private).

## Verification before publication (2026-11-08)

Run on the files as published (macOS, Python 3.14.6, Node 26):

| Check | Result |
|---|---|
| `make verify-offline`: recompute every indicator and the forecast from the pinned snapshots and fail on any drift; unit tests; ledger structure and freshness, honesty, counts and threat-model audits; generated-doc freshness | ✅ ok: 293 tests pass; the recompute is byte-identical to the committed `data/derived` |
| `make dashboard`: one GREEN/RED report across the offline audits | ✅ GREEN, 7/7 |
| `node tests/test_pharos_controls.cjs`: the observatory's UI controls | ✅ 7/7 |
| `reuse lint` (reuse 6.3.0) | ✅ compliant with REUSE 3.3: 165 / 165 files carry copyright and license information |
| `./pharos serve` in a browser: all six views, then **Run verification** inside the app | ✅ views render with no console errors; the run passed (exit 0, sources unchanged during the run) |
| Personal-data and secret scan (names, e-mail addresses, account handles, local paths, devices, tokens, private keys) | ✅ no findings |

## Open items (known, not hidden)

- **Pre-registered commitments still open:** the two-coder H1 bias audit, an independent second
  grader, and the `THREAT_MODEL.md` §7 release checklist (including the forecast inversion
  red-team). The deviation is recorded in [STATUS.md](STATUS.md).
- **The ledger freshness audit reads today's date.** Entry SAA-006 (OPEN, last reviewed 2026-06-02,
  180-day interval) becomes stale on 2026-11-30, and from then the audit — and CI — fail until it
  is genuinely re-reviewed. That is the design, not a bug. To reproduce today's result later, run
  `python3 src/ledger_staleness.py --today 2026-11-08`.
- **Role wording.** Planning documents (the impact strategy, the bias-audit pre-registration, the
  watch-report banner and older CHANGELOG and CHRONICLE entries) still refer to a "founder" role. It
  names no one; it is kept where a test or a pre-registration depends on it. Sign-offs that the
  pre-registration asks for will be recorded by role and credited to The Pharos contributors (the
  pre-registration text itself is not edited after registration).
- **Upstream licence labels** for the pinned snapshots in `data/snapshots/` (World Bank WGI; V-Dem
  and Freedom House via Our World in Data) are as recorded in `REUSE.toml`; they were not
  re-checked against each producer's current terms for this release.
- **Not run for this release:** the live gates (`make verify`, `make score`, `make drift` fetch
  upstream data over the network), the Docker image (`.dockerignore` was corrected so the image
  contains what the gate needs, but the image was not built), and the human review that
  [`THREAT_MODEL.md`](THREAT_MODEL.md) §4.3 requires. A green run is not a proof.

## Check it yourself

```bash
git clone https://github.com/LX8/pharos.git
cd pharos
make verify-offline        # stdlib-only Python 3: no install, no network
make dashboard
./pharos serve             # the local observatory at http://127.0.0.1:8796/
```
