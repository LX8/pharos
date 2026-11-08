<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# IMPACT.md — the evidence-backed impact strategy

> **Status: strategy proposal, awaiting founder adjudication.** Nothing in this document
> opens the publication gate, changes a grade, or authors new scientific claims. It answers
> one question with the project's own discipline: *given what is verifiably known about how
> evidence tools achieve real-world impact, what should this project do — and refuse to do —
> to matter?*

**Provenance.** Produced 2026-07-10 by a 47-agent research + adversarial-verification run:
one repo ground-truth audit, six parallel research angles (evidence-to-action science, peer
projects, distribution channels, credibility, ethics/backfire risk, funding/sustainability),
then each angle's three most load-bearing claims independently attacked by two adversarial
verifiers (evidence-quality lens + counterexample-hunting lens). **18 claims verified: 9
SUPPORTED, 9 MIXED, 0 REFUTED.** Recommendations below cite their evidence status honestly —
a MIXED tag means the direction held but the headline number or generality did not survive
scrutiny. The synthesis was adjudicated from the verified corpus.

---

## 1. The theory of change, made falsifiable

The repo already states the causal story (README §How it works, site §04): backsliding is
partly an *epistemic* phenomenon, so the antidote is knowledge anyone can audit — a trusted
information feedback loop that defenders gather around voluntarily.

The verified literature adds one hard correction to that story:

> **Passive availability reliably fails.** Making a rigorous tool public and findable is not
> a theory of change; it is the null hypothesis. Evidence crosses into action only when it is
> simultaneously credible, legitimate, **and salient** — and salience is the axis this project
> has invested least in. (Cash et al. 2003 PNAS, trade-offs replicated by Sarkki et al. 2014 —
> **SUPPORTED**; Grimshaw et al. 2012 on dissemination-vs-uptake — direction **MIXED**, the
> "~30% per added strategy" odds-ratio folklore did not survive scrutiny and is not relied on
> here.)

So the falsifiable impact chain is:

**IF** the ledger, indicators, and forecast are public, citable, machine-reusable, and their
trustworthiness is *legibly signaled* — **AND** each asset is attached to a named audience and
a recurring decision it informs (not just "published") — **THEN** specific defenders
(journalists, watchdogs, researchers) adopt them into real work, which is the measurable
precondition for the feedback-loop role the mission claims.

**Falsification trigger for the strategy itself:** if, 18 months after the publication gate
opens, no external party has cited, forked, or built on the project despite the levers below
being executed, the strategy — not just the execution — is wrong and must be re-graded.

---

## 2. What the verified evidence actually supports

The full 18-claim verification record, compressed. SUPPORTED = held under two adversarial
lenses; MIXED = direction held, magnitude/generality overstated.

| # | Verified claim (compressed) | Status |
|---|---|---|
| 1 | Evidence crosses into action only when credible + legitimate + salient; these trade off (Cash 2003) | SUPPORTED |
| 2 | The famous "17 years, 14%" research-to-practice lag is context-stripped folklore — cite only with caveats | SUPPORTED |
| 3 | Active, tailored knowledge translation beats passive dissemination (direction only; magnitudes contested) | MIXED |
| 4 | Free, machine-reusable, permissively-licensed data is the dominant reach mechanism (OWID ~89M visitors/yr anchor) | MIXED |
| 5 | A rigorous free dataset can become the citable infrastructure of its field (V-Dem) | SUPPORTED |
| 6 | A named, single-object metric on a fixed annual cadence is what media and the public carry (Doomsday Clock; Free/Partly Free/Not Free) | SUPPORTED |
| 7 | Being the free, non-partisan, machine-readable source others build on drives adoption (ACLED, V-Dem) | MIXED |
| 8 | Wikipedia/Wikidata embedding multiplies reach ~10× over one's own site (OWID's claim; self-reported) | MIXED |
| 9 | A DOI is a prerequisite for citation, not a driver of use (~4.3% open-data citation advantage) | MIXED |
| 10 | The strongest answer to "your index is biased" is testing for the bias and publishing the result, including nulls (Bright Line Watch / V-Dem) | SUPPORTED |
| 11 | Publishing uncertainty/margins of error strengthens credibility (WGI's decades-tested defense) | SUPPORTED |
| 12 | Trust rises when norm-adherence is visibly *signaled* (data/methods/funding/self-correction); pre-registration **alone** does not move reader trust | SUPPORTED |
| 13 | Person-/group-level data has been a decisive enabler of atrocity (Rwanda ID cards; Dutch registry) — the spatial floor is load-bearing | MIXED* |
| 14 | Early-warning systems risk predicting *visibility* rather than *vulnerability* and creating feedback loops | MIXED |
| 15 | A disclosure decision procedure exists (Shevlane–Dafoe marginal-value test); "open is safer" cannot be assumed | SUPPORTED |
| 16 | Marquee open-source sustainability funders (CZI EOSS, OTF FOSS fund) require demonstrated adoption first — do not apply pre-adoption | SUPPORTED |
| 17 | Fiscal sponsorship beats incorporating a nonprofit for a solo founder (weeks vs months; grant eligibility) | MIXED |
| 18 | US-government democracy money carries a documented perceived-independence cost + political volatility | MIXED |

\* MIXED only on the *mono-causal strength* of the historical claims; no verifier disputed
that person-level data materially enabled atrocity, which is why the spatial floor stays a
red line (§5), not a lever.

---

## 3. Ranked levers

Ordered by impact-per-effort. Scope tags: **[now]** = implementable and verifiable inside the
constraints at the time of writing (private repo, no charged content, no gate opened); **[founder]** = the
founder's call, cannot and should not be done solo; **[hybrid]** = prototype now, launch at
the gate.

> **Execution status (2026-07-10):** every [now] piece below is shipped and gate-verified —
> L3 ([`TRUST_SIGNALS.md`](TRUST_SIGNALS.md)), L4 ([`BRIEF.md`](BRIEF.md)), L5
> ([`DATA_CONTRACT.md`](DATA_CONTRACT.md) + `src/pharos_client.py`), L6 design
> ([`BIAS_AUDIT_PREREGISTRATION.md`](BIAS_AUDIT_PREREGISTRATION.md) + the blind-pack
> generator), the L2 prototype ([`WATCH_REPORT.md`](WATCH_REPORT.md)), the H3
> symmetric-reporting machine gate, and the red-line-3 mosaic rule in the THREAT_MODEL
> checklist. Everything still open is [founder]. Tracking lives in [`STATUS.md`](../STATUS.md).

### L1 — Open + citable, at the gate [founder]
Flip public, mint the Zenodo DOI (`.zenodo.json`/`CITATION.cff` are ready), keep code
GPL-3.0, license the ledger + derived data CC-BY (data CC0 where feasible). This is not a
lever among levers; it is the **precondition every other lever assumes** (claims 4, 5, 9).
Honestly: the DOI itself buys little (~4.3%, claim 9) — the openness and reusability buy the
reach. *Everything below is sequenced so that when the founder says go, impact machinery is
already in place rather than starting that day.*

### L2 — One named signal on a fixed cadence [hybrid]
The single strongest verified media/public mechanism (claim 6): a named, legible artifact —
a "state of the watch" — published on a fixed annual (or semiannual) date, compressing the
ledger + indicators into one carryable object, with the rich machinery underneath. The
Doomsday Clock, Freedom in the World, and V-Dem's March report all run on this pattern.
**[now]:** prototype the artifact from committed data (the falsification watch + tally +
divergence counts are already computed and drift-gated). **[founder]:** the name (decided 2026-11-08: **Pharos** — an unsettled
name was a tax on every citation, claim 6 seeds), the cadence commitment, and the editorial voice.

### L3 — A legible trust-signals surface [now]
Claim 12 (SUPPORTED) says trust follows *signaled* norms, not merely practiced ones. The
project practices nearly every norm in the Jamieson et al. (PNAS) framework — reproducible
recompute, pre-registered falsification triggers, a self-correction record (a REFUTED entry,
a published negative forecast result), web-verified citations, an enforced threat model —
but nowhere *enumerates* them as a single legible surface. Build that page (site section +
doc): each norm, the mechanism enforcing it, and the command that lets a stranger check it.
Include the caveat the evidence demands: lead with the **self-correction record**, not with
pre-registration alone (claim 12's registered-report finding).

### L4 — The salience layer [now]
The CRELE diagnosis (claim 1): this project is credibility- and legitimacy-rich and
salience-poor. Radical honesty ("88% within noise", "the forecast does not beat baseline")
maximizes credibility at a *direct cost* to salience — worth paying, but only if a
plain-language layer sits on top so the honesty reaches anyone. **[now]:** a generated
"what changed and why it matters" brief — computed from committed derived data, drift-gated
like everything else — plus, per asset, a one-paragraph statement of *who* uses it for
*which recurring decision* (the productive-interactions discipline). No new claims; a new
register.

### L5 — Machine reuse: tidy exports + a one-line client [now]
The ACLED/V-Dem adoption mechanism (claims 5, 7): be the source others build on directly.
The data is already tidy CSV/JSON and drift-gated; what's missing is the *reuser's* on-ramp:
a documented stable-format contract (column meanings, guarantees, versioning), and a thin
one-file stdlib Python client (mirroring the `pharos` CLI's read paths) a researcher can
vendor in one line. **[hybrid]:** Wikidata/Wikipedia ingestion (claim 8's multiplier) waits
for the gate and the settled name.

### L6 — The pre-registered bias self-audit [hybrid]
Claim 10 (SUPPORTED): the winning defense against "you're just partisan pessimists" is to
pre-register a directional-bias test of one's own instrument and publish the result, nulls
included — the Bright Line Watch / V-Dem playbook. **[now]:** design the test and write the
pre-registration (what would count as directional skew in grading and in indicator framing;
what data answers it). **[founder]:** sign off the methodology and run it — the grades are
a human maintainer's judgement, so the audit of their bias must be signed off and run by
a human, not by an AI.

### L7 — Sustainability sequencing [founder]
Claims 16–18: do **not** apply to CZI EOSS / OTF FOSS-sustainability first — the project
fails their explicit adoption-maturity bars. The evidenced sequence: fiscal sponsorship
(Code for Science & Society is the closest mission fit) → early-stage-friendly bridges →
maturity funds only after demonstrated adoption. Decide the funding-independence policy
*before* going public (disclosure norms, single-source caps, which money to refuse) — with
claim 18's caveat that US-government democracy money carries a real perceived-independence
cost this project's non-partisan posture cannot afford.

### L8 — The human second grader [founder]
Already Tier-0; the impact research independently re-derived it twice: a multi-person
commons is itself an adoption signal partners evaluate (distribution angle), and the
brokering relationship it creates is the KT mechanism that works (claim 3). The
`CONTRIBUTING.md` on-ramp is ready. Nothing about this is automatable, by design.

---

## 4. Uptake metrics — defined now, before going public

The project's own discipline applied to itself: "did anyone use it" must be a falsifiable
question, with the instruments named *before* the treatment. All privacy-respecting,
aggregate, and passive:

- **Citations** of the Zenodo DOI / CITATION.cff (Crossref + Google Scholar).
- **Forks/stars/clones** of the public repo (GitHub-provided aggregates only).
- **Independent reuse events**: a third party's published artifact (article, dataset,
  dashboard) that ingests the derived data or cites a ledger entry.
- **Fired-trigger responses**: falsification triggers that fire and are engaged by someone
  other than the founder.
- **Second-grader count**: humans who have completed an end-to-end grade.

No tracking scripts, no visitor analytics beyond what the host provides in aggregate — the
"watch power, not people" law binds the project's own telemetry too.

---

## 5. Red lines — impact moves this project must refuse

Ranked levers tempt scope drift; these are the boundaries the ethics verification says are
load-bearing, restated as standing refusals:

1. **The spatial floor never lowers.** No sub-national, geolocated, group-attributed, or
   person-level layer, ever — regardless of how much "richer" it would make the product
   (claim 13; enforced by `src/audit_threat_model.py`, and that gate is immovable).
2. **The forecast is never marketed as operational early warning.** It does not beat
   baseline; it is a calibration artifact and says so. Any outreach copy implying Pharos
   "predicts" or "flags at-risk countries" is a violation, not a simplification (claim 14).
3. **Mosaic guard:** before publishing any new derived table, apply a small-cell /
   re-identification check so no aggregate can expose a small at-risk population — the
   spatial floor's companion rule (ethics angle; candidate for a future audit extension).
4. **No salience purchase with certainty inflation.** The plain-language layer (L4) may
   simplify register, never confidence — "88% within noise" appears in the headline read,
   not the footnote.
5. **Funding that compromises the non-partisan posture is refused**, and all funding is
   disclosed (claims 17–18).
6. **Coverage honesty:** data-sparse countries are flagged as unobserved, never allowed to
   read as "stable" — the early-warning field's visibility-vs-vulnerability failure mode
   (claim 14).

---

## 6. Open questions for the founder

1. **The name.** Decided 2026-11-08: **Pharos** (the landing page is live under that name).
2. **The cadence.** Annual or semiannual flagship? Which month becomes the fixed date?
3. **The gate.** The three long-standing founder-only steps (open publication, second
   grader, article refresh) are now also the top of the impact-lever ranking — the
   strategy adds sequencing, not new obligations.
4. **SAA-028 engagement.** The credibility research surfaced that the coder-bias critique
   (and its published rebuttal) bears directly on the democratic-recession entry —
   re-grading it to engage that objection explicitly would itself model the L6 behavior.
   Founder's call: it is a grade.
5. **Funding-independence policy.** Which sources are refused on principle, and what is the
   single-source cap?

---

*This document follows the project's own law: every recommendation above rests on a claim
that was independently attacked before being relied on, statuses are reported honestly, and
the strategy carries its own falsification trigger (§1). It is a map, not a mandate — the
founder's adjudication is the next step.*
