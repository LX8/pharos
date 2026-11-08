# Science Against Authoritarianism

[![verify: offline · deterministic](https://img.shields.io/badge/verify-make%20verify--offline%20%C2%B7%20local%20hooks-brightgreen.svg)](docs/VERIFYING.md)
[![tests: offline · 7 audits](https://img.shields.io/badge/tests-offline%20%C2%B7%207%20audits-brightgreen.svg)](docs/VERIFYING.md)
[![Content: CC BY-SA 4.0](https://img.shields.io/badge/Content-CC%20BY--SA%204.0-orange.svg)](LICENSES/CC-BY-SA-4.0.txt)
[![Code: GPL-3.0-or-later](https://img.shields.io/badge/Code-GPL--3.0--or--later-blue.svg)](LICENSES/GPL-3.0-or-later.txt)
[![Data: CC0 1.0](https://img.shields.io/badge/Data-CC0%201.0-lightgrey.svg)](LICENSES/CC0-1.0.txt)
[![REUSE compliant](https://img.shields.io/badge/REUSE-compliant-green.svg)](https://reuse.software)
[![Report: v1 complete](https://img.shields.io/badge/report-v1%20complete-brightgreen.svg)](REPORT.md)
[![Evidence: cite-what-is-measured](https://img.shields.io/badge/evidence-cite%20what%20is%20measured-informational.svg)](#method)

> **A project for the public.** Pharos is built for the good of humanity and the
> environment. It is free of charge, it carries no personal credit, and anyone may use,
> study, share and improve it under the licenses below. It was verified before
> publication; see [`SNAPSHOT.md`](SNAPSHOT.md).

> **Authoritarianism and organised political violence are, in part,
> *epistemic* phenomena** — they run on disinformation, manufactured
> grievance, and the deliberate rejection of measurable truth. This
> project asks, in the open and under falsifiable discipline, **what
> science can demonstrably do to contain them** — and turns the
> defensible answers into reproducible, openly-licensed tools.

*"Science Against Authoritarianism" is the umbrella project. Its first
deliverable — the verified research synthesis in
**[`REPORT.md`](REPORT.md)** — proposed, and this repository now builds in
honest v0 form, the concrete initiative: **Pharos**, an open, falsifiable
early-warning observatory for democratic resilience. Its design rule:
**watch power, not people.***

---

## Run it in 30 seconds

Stdlib-only Python — no `pip install`, no build step, runs offline.

```bash
./pharos serve      # browser observatory at http://127.0.0.1:8796/
./pharos stats      # one-glance summary of the whole project
./pharos ledger     # browse the graded, falsifiable evidence entries
./pharos watch      # the falsification watch — every entry's "what would change our minds"
./pharos brief      # the plain-language read of what the data says (also: pharos report)
make dashboard      # one GREEN/RED report across every offline audit
```

The **[local Pharos observatory](docs/LOCAL_OBSERVATORY.md)** connects the evidence ledger,
three-instrument comparison, forecast evaluation, model demonstrations and actual offline
verification runs. It uses the committed historical data and runs entirely on your computer.

Landed here for something specific? The **[Start here](#start-here)** table
below routes you by what you came for.

---

## Status

🟢 **Built in honest v0 form — verified, reproducible, and public.**
What began as a verified research synthesis (**[`REPORT.md`](REPORT.md)** —
an adversarial deep-research run: 29 sources → 137 claims → 25 verified →
**21 confirmed, 4 refuted** → 7 high-confidence findings, authored to the
*cite-only-what-is-measured* standard) is now a working open-science commons:

- a **graded, falsifiable evidence ledger** — every entry sourced, graded,
  and carrying the exact condition that would withdraw it (browse it with
  `./pharos ledger` or [`ledger/INDEX.md`](ledger/INDEX.md));
- two **computed pillars** — open governance [indicators](docs/indicators/)
  with honest uncertainty, triangulated across three instruments, and a
  pre-registered backsliding [forecast](docs/forecast/pharos-forecast-v0.md)
  that reports plainly it does *not* yet beat a no-change baseline;
- **validated mechanism simulators**, each reproducing a *published* result
  via a unit test;
- a **verification suite** that machine-checks every public number
  ([`docs/VERIFYING.md`](docs/VERIFYING.md)); and
- **`pharos`**, one stdlib-only command (below) that ties it all together.

Everything is stdlib-only and reproducible offline. The landing page is live at
<https://lx8.github.io/pharos/> in English, Spanish, German and Portuguese, with a one-click download
of the whole project; the interactive observatory (`./pharos serve`) runs entirely on your
computer.

**Headline:** science contains authoritarianism along two axes — as a
*method* (open, falsifiability-first knowledge attacks the epistemic
substrate fascism runs on) and as an *institution* (open,
uncertainty-honest early-warning forecasting). The robust leg is
**forecasting + honest evidence-keeping**; the behavioral levers
(prebunking, intergroup contact) are real but **contested**, and are
treated as hypotheses to test, not solutions to ship. The report
culminates in the design of **Pharos** (Part IV).

> ⚠️ **Coverage is deliberately partial.** Much canonical literature
> (Chenoweth's 3.5%, Walter on anocracy, Stanton's genocide stages, the
> Polanyi/Piketty/Acemoglu political-economy canon) did **not** survive
> verification in this pass and is marked OPEN — a backlog for the next
> round, not a verdict against it. See the report's scope warning.

---

## The question

> *How can science — both as a method (falsifiability, reproducibility,
> open data) and as an institution — measurably contain political
> violence and the growth of fascism / authoritarianism worldwide?*

"Fascism" is used here in the precise sense of the scholarship
(Robert Paxton's *Anatomy of Fascism*; Umberto Eco's *Ur-Fascism*;
Jason Stanley's *How Fascism Works*) — a mobilising politics of
manufactured decline, in-group purity, cultivated grievance, and the
subordination of truth to power — **not** as a loose epithet. The
project is non-partisan, evidence-first, and globally scoped, not
tied to any single country's politics.

---

## Four lenses

The synthesis treats each of these as a distinct, measurable body of
evidence:

1. **Epistemic defense / open science** — how falsifiability,
   reproducibility, open data, and prebunking ("inoculation") counter
   the disinformation engine authoritarian movements run on.
2. **Social science of violence & democratic backsliding** — what
   political science, peace-and-conflict studies, and the psychology
   of authoritarianism empirically find drives *and* de-escalates
   political violence and democratic erosion.
3. **Systems & technology** — network science of radicalisation,
   computational early-warning and conflict forecasting, the epidemic
   model of violence, and AI's dual role as amplifier and defense.
4. **Political economy & institutions** — how inequality, economic
   shocks, status threat, and institutional design feed or starve
   authoritarian movements, and which interventions actually work.

---

## Method

This project holds itself to a falsifiable-science discipline:

- **Compute / prove everything derivable; cite only what is measured.**
  Every claim carries its evidentiary status. Robust, replicated
  findings are separated from contested or speculative ones, and the
  live debates (e.g. status-threat vs. economic-anxiety; whether
  counter-messaging durably works) are flagged as open, not resolved.
- **Falsifiability first.** Any tool this project builds must make
  predictions that could be shown wrong against open conflict and
  democracy datasets (ACLED, V-Dem, UCDP, GDELT, Freedom House).
- **Open and reproducible.** Multi-licensed (below), REUSE-compliant,
  reproducible end-to-end. Knowledge that asks to be trusted must be
  checkable.

This is itself the thesis in miniature: the antidote to a politics
that subordinates truth to power is knowledge that anyone can audit.

---

## Verification

> **Every load-bearing property is machine-checked, and you can run the
> check yourself — offline, deterministically, for free.** Stdlib-only;
> there is no `pip install`. Full reference:
> **[`docs/VERIFYING.md`](docs/VERIFYING.md)**.

- **`make dashboard`** — one GREEN/RED report across **seven audits**: unit
  tests, ledger structure, freshness, an overstatement guard, a doc-count
  consistency gate, the *watch-power-not-people* threat-model gate (no
  published data may drop below country level), and a generated-index
  freshness check that keeps the [falsification watch](ledger/INDEX.md) in
  sync with the entries.
- **`make verify-offline`** — **306 offline tests** plus a full recompute
  of every indicator from **pinned snapshots with no network**, failing on
  any drift from the committed results. A clone gets byte-identical
  numbers; the drift gate doubles as a regression test for the math.
- **`make hooks`** — free local CI (pre-commit → dashboard, pre-push →
  verify-offline). No cloud, no billing.
- **`make drift`** — freshness recon: is the pinned data still current? It
  recomputes from the **live** sources, diffs against the pin, reports any
  change, and restores the pin byte-for-byte — reads the live world, never
  adopts it (a re-pin is a deliberate `make snapshot` step).
- **Adversarial review, beyond the gates.** The ledger and code have been
  swept by repeated independent adversarial review: every citation
  web-verified (**no fabricated or retracted sources**), every load-bearing
  formula differentially re-derived (**5 of 6 bit-exact**, one rounding bug
  fixed), and every grade recalibrated against the rubric (**0 violations**).
  The record is in [`docs/VERIFYING.md`](docs/VERIFYING.md) §4 and
  [`docs/CHRONICLE.md`](docs/CHRONICLE.md).

---

## Start here

| If you are… | Start with |
|---|---|
| **Here to just run it** | **`./pharos`** — the whole project as one stdlib-only command: `./pharos stats` (one-glance summary), `./pharos ledger --grade ROBUST` (browse/search the graded entries), `./pharos watch` (the falsification watch), `./pharos stale` (what's due for re-review), `./pharos indicators` / `divergence` / `forecast` (the computed results), `./pharos verify` (the seven audits). No install, no dependencies. |
| **Here to build on it** | **[`ledger/`](ledger/)** — the **Pharos Ledger**: 41 graded, falsifiable evidence entries (spanning epistemics, social science, anthropology, psychology, sociology, political economy, systems & technology, and recent empirical findings) you can cite and fork. Browse them in **[`ledger/INDEX.md`](ledger/INDEX.md)** — a generated by-grade index + **falsification watch** (every entry's "what would change our minds" trigger in one place). Grading rules, the adversarial prompts, and how to add/re-grade an entry: **[`docs/GRADING_PROTOCOL.md`](docs/GRADING_PROTOCOL.md)** (enforced by `make validate`) |
| **Here to contribute** | **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — the on-ramp: the two laws, the verify-first discipline for evidence entries (every citation web-verified), the full add-an-entry workflow incl. the count cascade, and the commit conventions. The most valuable contribution is *meeting a falsification trigger with evidence*. |
| **Here for the numbers** | **[`docs/indicators/`](docs/indicators/)** — open indicators computed with honest uncertainty: **WGI governance, 6 dimensions, 2014→2024** (88% of changes are within noise; the measurable decline is concentrated in *Voice & Accountability*) — now **triangulated** against V-Dem + Freedom House in [`voice-divergence.md`](docs/indicators/voice-divergence.md), which **publishes divergence, not a single score** (45 countries where every significant instrument concurs on voice decline; 5 conflicts surfaced, never blended away). Reproduce: `make verify` |
| **Here for the plain-language read** | **[`docs/BRIEF.md`](docs/BRIEF.md)** — the same verified numbers, translated: what changed, where the instruments agree, and what the honest forecast means — generated from the committed data (`make brief`), so it can never drift from what was computed |
| **Here to build on the data** | **[`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md)** — the stable-format contract: every column and vocabulary documented, additive-only evolution guaranteed, CC0 data. Vendor the one-file stdlib client [`src/pharos_client.py`](src/pharos_client.py) and every table loads in one line |
| **Here to read the case** | **[`docs/article/watch-power-not-people.md`](docs/article/watch-power-not-people.md)** — long-form draft (theory → method → finding → invitation) for practitioners, journalists, activists *(working draft)* |
| **Here for the honesty** | **[`docs/what-is-tested.md`](docs/what-is-tested.md)** — exactly what *is* and *isn't* tested, claim by claim, tiered by how far (T1 machine-verified → T6 untestable) |
| **Here to check us** | **[`docs/TRUST_SIGNALS.md`](docs/TRUST_SIGNALS.md)** — every trust signal made checkable: the norm, the mechanism enforcing it, and the command that verifies it *without trusting us* — self-correction record first, then reproducibility, falsifiability, uncertainty, citation integrity, the honesty gates, do-no-harm, independence |
| **Here for the record** | **[`docs/CHRONICLE.md`](docs/CHRONICLE.md)** (how it was built) · **[`STATUS.md`](STATUS.md)** (state + honest backlog) · **[`docs/verifications/`](docs/verifications/)** (the method turned on the plan itself, and on Graham Hancock's claims) |
| **Here for the flagship** | **[`docs/WATCH_REPORT.md`](docs/WATCH_REPORT.md)** — the report-edition prototype carrying **the Watch List** (countries where all three instruments concur on voice decline) as its single object; generated from committed data (`make watch-report`) *(prototype — the public name and fixed cadence are the maintainers' open decisions)* |
| **Here for what's next** | **[`docs/IMPACT.md`](docs/IMPACT.md)** — the evidence-backed impact strategy: 18 adversarially-verified claims about how evidence tools achieve real use, ranked levers (each tagged buildable-now vs maintainer-gated), uptake metrics defined *before* going public, and the red lines an impact push must never cross. Every buildable-now lever is shipped; the rest is founder-gated |
| **Here for the public face** | **[`site/`](site/)** — the static landing page, in English, Spanish, German and Portuguese (live at <https://lx8.github.io/pharos/>; generated by `make pages` from one template, see [`site/README.md`](site/README.md)) |
| **Here for the findings** | **[`REPORT.md`](REPORT.md)** — the cited synthesis, 7 findings graded ROBUST / CONTESTED / REFUTED / OPEN |
| **Here for the proposed tool** | **Pharos** — [`REPORT.md`](REPORT.md) Part IV: an open, falsifiable backsliding early-warning observatory + evidence ledger. The forecasting pillar now has an honest v0: **[`docs/forecast/pharos-forecast-v0.md`](docs/forecast/pharos-forecast-v0.md)** — a calibration layer (not a hero call) that CRPS/Brier-scores backsliding forecasts against a no-change baseline, and reports plainly that v0 does *not* yet beat it |
| **A skeptic / reviewer** | The *Risks & Limits* section of `REPORT.md` — dual-use, surveillance abuse, techno-solutionism, and what science **cannot** do |
| **Here for the ethics** | **[`NOTICE`](NOTICE)** §7 — the project's ethical-use covenant — and **[`THREAT_MODEL.md`](THREAT_MODEL.md)**, which turns it into an enforced publish/withhold gate (*watch power, not people*, in code not just intent) |
| **Here to verify / reproduce it** | **[`docs/VERIFYING.md`](docs/VERIFYING.md)** — the full verification reference (the ladder, the seven audits, offline determinism, the adversarial-review regime). The short version: `make dashboard` (one GREEN/RED report across every audit) · `make verify-offline` (deterministic, **no network** — recomputes the indicators from pinned snapshots) · `make verify` (live refresh) · or `docker build -t pharos . && docker run --rm pharos`. Stdlib-only. **Free local CI:** `make hooks` (pre-commit → dashboard, pre-push → verify-offline) — no cloud, no billing. |

---

## Scope & non-goals

- **Non-goal: techno-solutionism.** Software does not defeat fascism.
  The report is explicit about the limits of measurement and tooling,
  and about the political and human work no model can replace.
- **Non-goal: a surveillance instrument.** Anything built here is
  oriented toward *early warning and accountability of power*, never
  toward monitoring, scoring, or policing people. See `NOTICE` §7.
- **Non-goal: partisanship.** The unit of analysis is the *mechanism*
  (how violence and backsliding propagate and de-escalate), not any
  party or leader.

---

## License

Multi-licensed, matching content type (see [`LICENSE`](LICENSE) and
[`REUSE.toml`](REUSE.toml) for the canonical, machine-readable map):

- **Prose, reports, manuscripts** → CC BY-SA 4.0
- **Code** → GPL-3.0-or-later
- **Numerical outputs / fact tables** → CC0 1.0

The [`NOTICE`](NOTICE) file carries the project's **ethical-use
covenant** — a good-faith request, not a licence condition — that this work never be used for weapons, for harm to any
form of life, or for mass surveillance, predictive policing, social
scoring, or the persecution of minorities. Building a defense against
authoritarianism with tools that could serve it would defeat the
entire purpose.

---

## Acknowledgements

Research and tools developed with AI assistance (Claude by Anthropic, and other
AI coding assistants) under human direction and verification. AI assistants are not authors and
hold no copyright. All retained claims are checked against cited,
measured sources per the [Method](#method) above.

Credit: **The Pharos contributors** — a project for the public, for the good of
humanity and the environment. No personal recognition is sought; see [`AUTHORS`](AUTHORS).
