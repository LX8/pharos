---
title: "Verification — the plan for peace (adversarial self-test)"
date: 2026-06-15
scope: >-
  The project's own theory of change held to the bar it holds outside claims to:
  9 load-bearing claims (Pharos's two pillars + the cascade/complex-contagion
  argument + the WGI worked example) each researched by a skeptic instructed to
  refute it before grading, plus 6 red-team angles each building the strongest
  case the whole plan fails. Steelman first, grade only what the evidence carries.
verdict: >-
  Directionally sound, honestly overstated in its headline framing — the plan
  survives its own adversarial test with zero FATAL and zero BREAKS, but only
  one claim HOLDS outright; the other eight are QUALIFIED, and the two serious
  red-team angles (solo-sustainability + reflexive/discrediting miss) force real
  redesigns of the success metric and the release posture, not cosmetic edits.
tally:
  claims: { HOLDS: 1, QUALIFIED: 8, WEAK: 0, BREAKS: 0 }
  red_team: { FATAL: 0, SERIOUS: 2, MANAGEABLE: 4 }
---

# Verification — the plan for peace (adversarial self-test)

*The project turning its own discipline on **itself**. Everywhere else in this repo
the method is pointed outward — at Hancock's lost civilization, at the backsliding
literature, at pseudoscience graded REFUTED. Here it is pointed inward, at the plan
for peace that motivates the whole project. The instruction to every skeptic was the
same one used on outside claims: **try hardest to break it first**, steelman what
survives, and grade only what the evidence carries (HOLDS / QUALIFIED / WEAK /
BREAKS for claims; FATAL / SERIOUS / MANAGEABLE for red-team angles). A plan that
asks others to downgrade their claims when replications turn has to do the same to
its own — or the credibility it stakes everything on is a double standard.*

> **Status: ✅ LANDED** (workflow `w8hvrdhqz`, 2026-06-12 → graded 2026-06-15). This
> file now records the per-claim verdicts, the red-team severities, the synthesis,
> and the priority fixes. The resulting action items flow into
> [`../../STATUS.md`](../../STATUS.md). The honest bottom line is in the frontmatter
> `verdict` and again in **§ Synthesis**: *directionally sound, oversells its headline.*

## How to read this

The good news and the bad news are the same fact: **the plan was already more honest
than its own slogans.** Almost every "QUALIFIED" below is not the discovery of a hidden
flaw — it is the finding that the plan's *headline sentence* (the quotable one) overstates
what the plan's *own body, ledger, and `what-is-tested.md` tiers* already concede. The
fixes are therefore mostly **demotions of rhetoric to the level of the evidence the project
already holds**, plus a small number of genuine structural additions (a staleness gate, a
threat model, a reflexivity scoring protocol). None of the nine claims breaks; none of the
six red-team angles is fatal. But "nothing is fatal" is not "nothing is wrong" — the two
SERIOUS angles demand real redesign, and eight QUALIFIEDs mean the plan ships honestly only
if the caveats travel with the headlines.

---

## Per-claim verdicts (9 claims)

| ID | Claim (load-bearing sentence) | Verdict | One-line why |
|---|---|---|---|
| **C1** | Fascism is epistemic/affective, not propositional — "few falsifiable claims" — and that's why open science is *structurally hostile* to it | 🟡 **QUALIFIED** | Descriptive half holds (Paxton, Arendt); the *causal* half overstates — regimes make **many** checkable claims and use forced assent, so refuting propositions isn't the lever |
| **C2** | A committed minority past a critical mass triggers a system-flipping cascade — "convergent" across Granovetter, Watts, Centola, Chenoweth, Otto | 🟡 **QUALIFIED** | Mechanism is real and code-validated; the *"convergence"* welds 2 models to 2 contested empirics, and Otto isn't "civilizational-scale validation" — SAA-009 already says all this, the headline doesn't |
| **C3** | The energy is **complex contagion**: reinforcement density + temporal persistence + clustering, "all measurable, all buildable" | 🟡 **QUALIFIED** | Reinforcement core is robust; the **clustering/wide-bridges** prong is now contested (Wan/Lazer 2025), "all measurable" fails on observational data (Shalizi & Thomas), and "temporal persistence" is unsourced |
| **C4** | Open honest measurement is **the** substrate and **the** one high-leverage move; restoring a feedback loop changes behavior at scale cheaply (Meadows #6; TRI −40%) | 🟡 **QUALIFIED** | Mechanism + strategy hold; the **empirical bridge** overreaches on its two proofs — TRI causation is contested, Meadows is an untested heuristic, Dunning 2019/Carnegie 2024 show null-to-limited population-scale effects |
| **C5** | The robust lever is institutional: open, CRPS-scored, uncertainty-honest forecasting, **proven to exist by ViEWS** — Pharos copies that, not the contested behavioral levers | 🟡 **QUALIFIED** | The *method* to copy is robust and least-contested (HOLDS); but ViEWS forecasts **violence**, Pharos forecasts **backsliding** (a harder, rarer target) — and most challenge models lose to a no-change baseline, undisclosed in SAA-007 |
| **C6** | Self-falsifying evidence-keeping is the antidote, and the protocol **would have caught** prebunking + the epidemic-model failures *before anyone built on them* | 🟡 **QUALIFIED** | Virtue + "fascism can't practice it" hold; the **counterfactual is false on timeline** — prebunking shipped at 200M+ impressions (2020–21) before its refutations (2023–25); a 2026 ledger re-grades, it doesn't pre-empt |
| **C7** | "Watch power, not people" is a **hard architectural floor** + covenant, which makes the open tool **net-protective** | 🟡 **QUALIFIED** | The floor constrains the **wrong axis** — it blocks individual re-ID but *permits* sub-national, which is exactly the predictive-policing harm vector; covenant is non-binding by the project's own NOTICE §7 |
| **C8** | One person can build a **node that matters**; the cascade **starts** with the first node — minimal Pharos is shippable solo (OWID precedent) | 🟡 **QUALIFIED** | Feasibility HOLDS (ledger v0 already exists); "node that matters / cascade starts with one" **contradicts the project's own SAA-010** — a lone node is the single scattered exposure complex contagion calls insufficient |
| **C9** | The 2014→2024 WGI backsliding is concentrated in **Voice & Accountability** (33:6 ≈ 5.5:1), 88% within noise, reproducible via `make verify` | 🟢 **HOLDS** | Every number re-derives exactly from the repo's own data; method is conservative + unit-tested; V-Dem independently corroborates the voice-leads ordering |

**Tally:** **1 HOLDS · 8 QUALIFIED · 0 WEAK · 0 BREAKS.**

### Why eight are QUALIFIED, not HOLDS — and what each fix is

The pattern across all eight is identical and worth naming once: **a robust core welded to
an overstated headline.** In every case the grade lands on the weld, not the core.

- **C1 (epistemic/affective fascism).** Paxton's "affair of the gut" and Arendt's "the
  distinction between true and false no longer exists" are verbatim and well-anchored — that
  half is solid. The break is the inference that "few falsifiable claims" is *why* science is
  structurally hostile. Authoritarian regimes make **copious** checkable claims (inflated
  GDP — Martinez's nightlights; faked margins; Lysenkoism) and the signaling literature
  (Huang 2015; Wedeen) shows their *falsity is the point* — costly public assent, not belief.
  If the mechanism is forced assent, refuting propositions doesn't disarm it. **Fix:** replace
  "few falsifiable claims" with "treats truth as instrumental — many checkable claims, indifferent
  to their truth," and demote "structurally hostile" to its defensible form ("denies it the
  cover of manufactured ignorance; supplies institutions auditable ground"). Load shifts to the
  robust early-warning leg, off the contested behavioral one.

- **C2 (committed-minority cascade).** The mechanism is among the better-supported ideas in
  social science and is **validated in the repo's own code** (`test_sim_threshold_cascade.py`
  re-derives Granovetter's 100-vs-1 knife-edge; `test_sim_network_cascade.py` re-derives Watts's
  cascade window). The break is the rhetorical "convergent across four traditions": two of those
  (Granovetter, Watts) are *models* proving the mechanism is **possible and rare**, not empirical
  thresholds; Centola's 25% is lab-only and unreplicated; Chenoweth's 3.5% is descriptive,
  autocracy-scoped, has failed counterexamples (Bahrain, Brunei), and is **declining 65%→<34%**;
  Otto 2020 is expert elicitation that drew a PNAS rebuttal, not "civilizational-scale validation."
  **Fix:** label evidential type explicitly (2 FORMAL, 2 EMPIRICAL-but-contested), re-word Otto,
  and make the SAA-008 headline non-extractable from SAA-009's caveats (a "Read with SAA-009"
  guard *inside* the Claim block; grade label → "ROBUST (mechanism) / QUALIFIED (thresholds)").

- **C3 (complex contagion).** "Adoption needs multiple reinforcing exposures from trusted ties"
  is robust (Centola & Macy 2007; Centola 2010; Monsted 2017). Three things overreach: the
  **clustering/wide-bridges** prong is materially contested as of 2024–25 (Wan/Lazer PNAS 2025:
  clustering wins only near-deterministic thresholds, ≤5% edge in ~22% of parameter space, usually
  *loses* on reach); **"all measurable"** fails on the observational data a movement actually
  generates (homophily/contagion confound — Shalizi & Thomas 2011); and **"temporal persistence"**
  is not in the cited source. **Fix:** keep the reinforcement core ROBUST, demote the structure
  prong to a CONTESTED rider in SAA-010's `falsification_trigger` (which currently can't see the
  reach/reinforcement tradeoff), drop or source "temporal persistence," and replace "all measurable,
  all buildable" with "measurable in controlled settings; hard to identify in observational data."

- **C4 (measurement as the substrate / the one move).** The mechanism (credibility is one of
  complex contagion's four mechanisms) and the strategic posture (be checkable, watch power) are
  sound. The empirical bridge to "changes behavior at scale cheaply" overreaches on its two anchors:
  **TRI**'s ~40% drop is real but its *attribution to disclosure* is contested (Gamper-Rabindran/Finger:
  largely co-pollutant command-and-control regulation) — so "no fines, no bans, just the numbers" is
  the disputed claim asserted as settled; **Meadows** explicitly said her leverage list is "not
  empirically tested." And the best behavioral evidence cuts against the strong form (Dunning et al.
  2019: *no* overall effect of voter information across 6 countries; Carnegie 2024: "limited effects
  at population scale"; epistemic-populism: for the captured, institutional credibility is *negative*
  evidence). **Fix:** downgrade three words — "a load-bearing input for the part of the fight fought
  over shared facts" and "a genuinely available, high-leverage move (among several; organizing and
  coalitions are coequal)"; demote TRI to suggestive illustration *with* its contested attribution;
  flag Meadows as heuristic; state the scope condition up front (payoff established for audiences
  still open to evidence, null-to-limited at population scale / among the captured).

- **C5 (ViEWS as existence proof of the robust lever).** The open/reproducible/CRPS *discipline*
  is robust and genuinely the least-contested element (Gneiting & Raftery 2007 is uncontested). Two
  problems demote it: an **undisclosed performance caveat** — the 2023/24 VIEWS Challenge paper states
  most models are *beaten by a no-change baseline*, which is exactly SAA-007's own falsification
  condition and is omitted from the ledger entry; and a **target-transfer gap** — ViEWS forecasts
  *violence*, Pharos forecasts *backsliding* (≈4% two-year base rate, rarer and worse-instrumented;
  V-Dem's V-Forecast/PART is the real prior art and has no published CRPS track record). **Fix:**
  split into "method exists/sound" (HOLDS) and "robust predictive lever *for backsliding*" (OPEN);
  add the no-change-baseline caveat to SAA-007; make "beats a pre-registered no-change baseline by
  CRPS" the explicit success bar for pharos-forecast v0 — converting the weakest point into a
  falsifiable deliverable.

- **C6 (self-falsifying ledger as antidote).** The epistemic-virtue core and "fascism cannot
  practice honest self-grading" (Lysenko renouncing statistics; Benford anomalies in autocratic
  data) are well-supported. Two overstatements: the mechanism is stronger than *simple*
  preregistration/grading (which has low adherence — only Registered Reports are reliably effective,
  and the ledger sits nearer the weak end with no structural force to honor its own triggers); and the
  **"would have caught it before anyone built on it" counterfactual is essentially false** — the
  ledger *imports* disconfirming evidence rather than generating it, and prebunking deployed at 200M+
  impressions (WHO/UN/UK, 2020–21) *before* its transfer-failure replications (2023–25). **Fix:**
  keep the virtue core, promote the article's own "necessary, not sufficient" into the claim, require
  independent adversarial verification per entry, and replace the counterfactual with the honest
  version: "once a disconfirming replication lands, a *consulted* ledger re-grades and slows further
  build-out" — shortening the refutation-to-de-adoption lag, not pre-empting deployment.

- **C7 ("watch power, not people" as hard architectural floor).** Both legs are real design
  choices and accurately restated — but the safety *conclusion* doesn't follow. Aggregation genuinely
  destroys *individual* re-identification (the floor isn't vacuous), but state repression operates at
  **group/place** resolution, which the floor *explicitly permits* (PRIO-GRID 0.5° cells) — and the
  project's own cited cautionary tale, **predictive policing**, is precisely place-level area
  forecasting (EFF 2020; Ensign et al. runaway feedback loops). The covenant is **non-binding by the
  project's own NOTICE §7** ("relies on the reader's good faith"; GPL/CC0 "forbid added restrictions").
  Part V of the REPORT is already more honest than C7 ("not solved… a standing obligation"). **Fix:**
  replace "net-protective" with "reduces individual-targeting risk; group/place dual-use unsolved";
  make the floor bite on the *exploited* axis (coarsen/suppress sub-national outputs below a population
  threshold, never localize a single minority community); stop leaning on the covenant as architecture
  and move protection into release governance (tiered access, published abuse threat model); add a
  falsification trigger for the safety claim itself.

- **C8 (one person, a node that matters).** Feasibility **HOLDS** — ledger v0 already exists as 15
  graded entries and one CRPS-scored V-Dem forecast is a genuine solo task. The theory-of-change half
  is QUALIFIED and in tension with the project's own **SAA-010**: complex contagion says a single,
  scattered node is *necessary but radically insufficient* — the cascade is a property of a connected
  cluster, not the first node. Watts's single-seed cascades require adjacency to a percolating cluster
  and are explicitly **rare**; the OWID precedent took ~5–7 years, a team, and Oxford/Gates/Y-Combinator
  backing before it "mattered" (so it supports "start solo," not "solo is enough"). **Fix:** keep
  feasibility as stated; re-word the theory half to "the first node is a necessary seed, not a sufficient
  cause — it matters only if a reinforcing cluster later forms and willing actors receive it; lone
  artifacts cascade rarely (Watts 2002)." This removes the internal contradiction with SAA-010.

- **C9 (the WGI "voice decline" worked example) — HOLDS.** This is the one claim that survives
  outright, and it survives because it does what the rest of the plan promises but hasn't always
  delivered: it computes, the numbers re-derive exactly from `data/derived/wgi_governance_summary.json`
  (noise 1080/1222 = 88.4%; VA 33:6 = exactly 5.5:1; Control of Corruption *improved* 17:9), the method
  carries the published 90% CI through a two-sided z-test *stricter* than the World Bank's own CI-overlap
  rule of thumb, 11 offline tests pin the math, the 2025 WGI absolute-scale revision defuses the
  percentile-artifact objection, and **V-Dem independently corroborates** that freedom of expression is
  the first and most-targeted dimension of autocratization. The only asks are robustness hardening, not
  corrections: report one alternative window + the 95% bar so 5.5:1 isn't an endpoint artifact, soften
  "broad decline" to "most concentrated decline of any dimension (33 of 203)," and disclose per-dimension
  *n* and dropped-country counts. Convergence of two independent measurement systems is genuine strength.

---

## Red-team verdicts (6 angles)

| Angle | Severity | One-line |
|---|---|---|
| **R1** Warning-response gap — honest signal stalls at "the reachable now know," frees no prisoner | 🟠 **MANAGEABLE** | Survives because the failure mode is the *binding constraint Pharos targets* — but forces re-baselining success on **the reachable, not the captured**, + a response-hook + grading TRI down |
| **R2** Co-option / weaponization — a state forks the GPL code, strips the covenant, re-points it at people | 🟠 **MANAGEABLE** (leaning SERIOUS) | Marginal-value test defeats the leak (states already own person-level data; aggregate model adds little) — *but only if* the floor becomes a real differential-publication + tiered-access gate and the **stage-transition clock** is treated as dual-use-critical |
| **R3** The cascade never ignites — "build the lighthouse, crowd finds it" is the unpriced dependency | 🟠 **MANAGEABLE** | Doesn't touch the **N=1 value floor** (an honest node exists either way); kills only the grandiose ceiling — fix is to *parasitize existing dense clusters* (ViEWS/V-Dem/Bellingcat) + pre-register an adoption metric + **actually light it** |
| **R4** Thin/borrowed robust leg, contested/refuted actionable leg — mission rests on a small partly-borrowed base | 🟠 **MANAGEABLE** | Not fatal because the fragility *is the thesis* (README already concedes it) — survives only if Pharos reframes as a **calibration/evidence layer**, not a rival forecaster, and gates claims on its own grades |
| **R5** Infeasibility + Goodhart capture — existence depends on one un-stoppable human; the trusted indicator becomes a target | 🔴 **SERIOUS** | Sinks the plan *as framed* (solo, private, "sustain without burnout," OWID-as-precedent); survivable only with a **staleness gate**, an **opened grading substrate**, and **divergence-not-score** publishing |
| **R6** Reflexivity + a discrediting miss — a published forecast alters the system; a legible "they cried wolf" burns the whole trust asset | 🔴 **SERIOUS** | Real and unremovable at the margin; forces **portfolio-not-hero-call**, beat-the-baseline as the only success claim, a **reflexivity scoring protocol**, affective pre-inoculation, and the **ledger as the lit beacon** with the forecaster as a labeled experiment |

**Tally:** **0 FATAL · 2 SERIOUS · 4 MANAGEABLE.**

### The two SERIOUS angles — why they don't kill the plan, and what they demand

These are the two that draw blood. Neither is fatal, but each is fatal *to the plan as
currently framed* and survivable only with a real structural change. They are the priority.

**R5 — Solo-sustainability + Goodhart capture (SERIOUS).** The attack lands two blows that
a lone maintainer is structurally least-equipped to absorb. First, **silent rot**: a living,
self-falsifying ledger is a perpetual-maintenance object by construction — its whole value is
that it's never finished. The moment maintainer capacity lapses (illness, money, attention to
other projects, ordinary life), it doesn't fail loudly; it **freezes mid-update
and rots into the exact "stale authority" the project was built to oppose** — still wearing the
credibility uniform, but with a last grade that's now a lie because the replication that should
have downgraded it never got entered. A self-falsifying instrument that stops self-falsifying is
*worse than none*. Second, **Goodhart bites a high-trust indicator harder**: the same influence
that makes Pharos valuable makes it a target, and a motivated regime games the observable inputs
(perception surveys, public feeds) to manufacture a **false green that the project's own authority
launders**. The OWID-as-precedent claim compounds it — OWID is a funded ~20-person Oxford nonprofit
(~£2.45M/yr), so citing it to license a *solo* project is survivorship bias twice over.
**Why not fatal:** the attack refutes the *delivery vehicle's durability and capture-resistance*,
not the theory of change — and the ledger's own write → **manage** → read
design already demands the fix, just hasn't applied it to
itself. **What it demands (non-negotiable):** (a) kill the OWID feasibility claim — reframe OWID as
the *exit target* (funded, institutional), not the starting analogy; (b) **make rot loud** — a
machine-checked staleness gate in `make verify`: every entry carries `last_reviewed` + `review_interval`,
and CI fails or the site auto-banners "STALE — unmaintained" past the interval, so lapse becomes
self-announcing honest silence instead of false authority (this is the single highest-value fix and
directly applies that write→manage→read design to the ledger itself); (c) **bus-factor the substrate
before lighting the lighthouse** — the grading rubric, adversarial prompts, and re-grade workflow ship
as open runnable artifacts (not in the author's head or private notes), and recruit one second grader before
public launch; (d) **publish divergence, not a single score** — never a headline backsliding number,
only multi-source divergence (V-Dem + Freedom House + WGI), so a gamed input shows up as a *conflict*
across instruments (the alarm), and weight gameable perception surveys *below* harder behavioral signals
(ACLED repression events a regime cannot fake without committing the measured acts). **Without (b) and
(c) specifically, the attack is effectively fatal** — a private, solo, silently-rotting ledger is
strictly worse than nothing.

**R6 — Reflexivity + a discrediting miss (SERIOUS).** The base rate is brutal and one-directional:
in the VIEWS competitions *most models are beaten by a no-change baseline*, and Pharos's chosen target
(backsliding/Paxton-stage transitions, upstream of violence) is **harder** than ViEWS's fatality counts.
A v0 that picks one V-Dem sub-indicator on a small country set is a single low-*n* bet with a high prior
of visible failure on first scoring. Worse, **reflexivity is the modal case, not a tail risk**: the
project *wants* the forecast acted on, so success and falsification collapse into each other — if a
warning provokes counter-mobilization or a regime cosmetically improves the one watched indicator while
accelerating capture elsewhere (the Goodhart/Lucas move), the indicator improves, the forecast "misses
high," and the project can't distinguish "we were wrong" from "we worked." And the **audience asymmetry
is the kill shot**: CRPS calibration is read correctly by a tiny technical community, but the public and
adversaries read a binary point-call — *"the science guys said Country X would fall and it didn't"* is a
clean, viral, decontextualizable artifact, and the project's own SAA-001 predicts the affective frame
("they cried wolf") beats the propositional rebuttal ("our interval was well-calibrated and the downgrade
is on the record"). The transparent self-downgrade the design is proud of *is* the discrediting screenshot.
**Why not fatal:** the attack equivocates on "wrong" — a CRPS-scored probabilistic forecast with a published
interval has no "missed prediction" in the binary sense the attack needs; a calibrated 30% that resolves
false is a *success* of the system if 30%-events happen ~30% of the time across the portfolio, and the design
already forbids point-calls. **What it demands:** (a) **portfolio, never a hero call** — score a calibration
curve over many simultaneous pre-registered forecasts and lead every public artifact with the aggregate
Brier/CRPS-vs-baseline, so the legible object is "are we calibrated across N bets," not "did the wolf come";
(b) **beat-the-baseline as the only success claim** — pre-commit publicly that the bar is no-change-baseline,
converting the field's brutal base rate from an exposé into a documented, expected datum; (c) **make reflexivity
a scored outcome** — pre-register the Goodhart/Lucas pathway: when a watched indicator improves after a warning,
log it as a candidate warning-response event and publish the ambiguity rather than claim a clean hit or miss
(this is the one protocol the design doesn't yet have, and it's load-bearing); (d) **pre-inoculate the affective
frame** — ship the "here is what a calibrated miss looks like and why it means the system is *working*" explainer
as a launch artifact, not a post-hoc defense; (e) **lean on the ledger as the credibility anchor** — sequence the
lighthouse so the *ledger* (grading settled evidence, no reflexivity exposure) is the lit beacon and the forecaster
ships as an explicitly *labeled, riskier, in-public experiment*, so a forecast stumble damages a labeled experiment,
not the whole asset. The residual no mitigation removes — a motivated adversary can always manufacture a
decontextualized "they were wrong" clip, and the affective channel may beat the calibrated rebuttal — is real, and
is exactly why this stays SERIOUS: the plan must treat forecast communication as an adversarial information
operation from day one, which the plan as written under-resources.

### The four MANAGEABLE angles — in one line each

- **R1 (warning-response gap).** Survives because the field's own thirty-year lesson ("failure is political
  will, not warning") *is* the variable Pharos targets via complex contagion — its theory of change is bottom-up
  cascade-feeding, not top-down shaming, so the "fox effect" (the shameless don't shame) misses. Re-baseline
  success on **the reachable** (forks, citations, downstream reuse), add a per-artifact **response hook** routing
  each flagged decline to a named responder, and grade the TRI analogy down to CONTESTED-under-authoritarian-conditions.
- **R2 (co-option/weaponization).** The marginal-value test defeats the fork-and-strip move — a regime already
  owns the person-level substrate; an aggregate, never-sub-group model adds ~nothing, and the person-level
  prohibition can't be "stripped into existence" because the data isn't in the box. **But** the residual is real:
  a calibrated *stage-transition clock* is the highest-inversion-value artifact in the design. Survives **only**
  with a `THREAT_MODEL.md` that makes the "floor" an enforced differential-publication + tiered-access gate, holds
  the cascade-timing layer at resolutions that deny pre-emption lead time (or defers it until open-question #4 has
  an *answer*), and ships every forecast with a logged inversion red-team. Absent those three, this escalates to
  FATAL *for the forecasting pillar specifically*.
- **R3 (cascade never ignites).** Can't be fatal to a plan whose floor is "a true, checkable signal now exists
  and is scored in public" — the cascade is upside, not the deliverable. Fix is to stop treating distribution as
  "light it and wait": parasitize existing dense clusters (ship as a layer/PR into ViEWS/V-Dem/ACLED workflows,
  target investigative-journalism + metascience networks), own the FIND/process/USE step with a translation layer,
  pre-register an adoption metric with its own falsification trigger, and **actually open the gate** to a small
  pre-identified set of high-trust users (the lighthouse is currently built-but-not-lit — a node of *zero*).
- **R4 (thin/borrowed evidence base).** Lethal only to projects whose fragility is *hidden*; here the fragility
  is the headline (README leads with "the robust leg is forecasting + honest evidence-keeping; the behavioral levers
  are contested"). Survives by repositioning Pharos as a **calibration/evidence layer** standing on ViEWS
  (interoperation is the explicit SAA-007 instruction, not a hidden dependency), making "OPEN/CONTESTED" a hard
  ship-gate enforced in code, and ensuring "lit" means "publicly scored and calibrated," never "publishing confident
  calls." *Lit-but-uncalibrated* is the version this attack correctly sinks.

---

## Synthesis — the honest bottom line

**Directionally sound; honestly overstated in its headline framing.** That is the whole verdict in
six words, and the project should be able to accept it because it is the same verdict the project
hands outside claims that have a real kernel wrapped in an oversold gloss.

What this self-test actually found:

1. **The architecture is sound and the project already knew most of what's wrong with it.** Eight of
   nine claims grade QUALIFIED, but the qualification is almost always that the *headline sentence*
   overstates what the *body, ledger tiers, and `what-is-tested.md`* already concede. The plan's
   epistemic machinery — graded entries, falsification triggers, tiered testability, "cite only what
   is measured" — is genuinely the moat. A project that downgrades its own claims when replications
   turn cannot be caught over-claiming, *because the concession is the product*. The honesty the
   red-team tried to weaponize (R4, R6) is the same honesty that makes the plan survivable.

2. **The single thing that HOLDS is the thing that computes (C9).** The WGI worked example is the
   plan in miniature done right: it computes, the numbers re-derive, the method is conservative and
   tested, and an independent instrument (V-Dem) corroborates it. Everywhere the plan *computes and
   cites what is measured*, it holds; everywhere it *asserts a causal bridge or a quotable slogan*, it
   qualifies. That is the cleanest possible map of where to spend effort: **build and measure, don't
   declaim.**

3. **The two real risks are both about durability under pressure, not about whether the idea is
   right.** R5 (will it still be honestly maintained in two years, by one person, against a motivated
   gamer?) and R6 (will one legible miss burn the whole trust asset?) are the SERIOUS pair. Neither
   refutes the theory of change; both attack the *delivery vehicle*. Both are survivable — but only
   with structural additions the plan currently gestures at and must now make load-bearing: a staleness
   gate, an opened grading substrate, divergence-not-score publishing, a portfolio-not-hero-call posture,
   a reflexivity scoring protocol, and the ledger (not the forecaster) as the lit beacon.

4. **The honest one-line reframe a skeptic would accept** — and the one the plan should adopt as its
   own public framing:

   > *Supplying open, checkable, uncertainty-honest signal is a genuinely available, low-cost,
   > high-leverage move a small actor can make — **for the part of the fight fought over shared facts,
   > among audiences still open to evidence**. It is necessary, not sufficient; it does not move the
   > captured, it does not by itself close the warning-response gap, and a lone node cascades rarely.
   > Built honestly — ledger first and lit, forecaster as a labeled, calibrated, baseline-beating
   > experiment, and rot made loud — it is a real contribution. Sold as **the** substrate, **the** one
   > move, or a cascade that **starts** with one person, it oversells exactly the links its own ledger
   > grades CONTESTED, OPEN, and unproven.*

The plan does not need to become less ambitious. It needs to let its caveats travel with its
headlines — which is the discipline it already enforces on everyone else.

---

## Priority fixes (ordered punch-list)

Ordered by leverage: the SERIOUS-angle structural fixes first (without them the plan is worse than
nothing), then the headline demotions that close the eight QUALIFIEDs, then robustness hardening.
Each ties back to a claim/angle ID. These become entries in [`../../STATUS.md`](../../STATUS.md).

**Tier 0 — structural, do before lighting the lighthouse (gates public launch):**

1. **Staleness gate in `make verify`** *(R5)* — every ledger entry carries `last_reviewed` +
   `review_interval`; CI fails / the site auto-banners "STALE — unmaintained" past the interval.
   Makes maintainer lapse self-announcing. *Single highest-value fix.*
   **✅ DONE (2026-06-15)** — `src/ledger_staleness.py` + `make staleness` (wired into `verify`);
   grade-based intervals (CONTESTED/OPEN reviewed soonest); 14 deterministic tests; the gate is
   proven to bite (exit 1) once any entry passes its interval. *(Residual: the site auto-banner is
   not yet wired — the static page would need to read the freshness data; tracked as a follow-up.)*
2. **Open the grading substrate + break bus-factor-1** *(R5, R3)* — ship the grading rubric,
   adversarial prompts, and re-grade workflow as open runnable artifacts (not in private notes); recruit
   one second grader. Invert "lit, then crowd" to "open and reproducible **before** lit."
   **✅ SUBSTRATE DONE (2026-06-15)** — [`../GRADING_PROTOCOL.md`](../GRADING_PROTOCOL.md) (vocabularies,
   rubric, the reusable adversarial prompts, re-grade workflow, second-grader reconciliation rule) +
   [`../../src/ledger_validate.py`](../../src/ledger_validate.py) (`make validate`, machine-enforces the
   protocol; 15 tests). *Residual human step: actually onboard one second grader and have them grade an
   entry end-to-end before launch — that is the part code cannot do.*
3. **`THREAT_MODEL.md` as a release gate** *(R2, C7)* — state the adversary, the marginal-value test,
   the differential-publication rule, and a per-layer inversion red-team logged in the ledger. Make the
   "architectural floor" an enforced tiered-access + spatial-coarsening policy (suppress sub-national
   outputs below a population threshold; never localize a single minority community). Treat the
   stage-transition/cascade-timing layer as dual-use-critical — hold it at non-pre-emption resolution or
   defer until open-question #4 has an answer, not just an operationalization.
   **✅ DONE (2026-06-15)** — [`../../THREAT_MODEL.md`](../../THREAT_MODEL.md): adversary model, the
   Shevlane-Dafoe marginal-value test (which *formally derives* "watch power, not people"), DII +
   LINDDUN + Microsoft-harms lenses, the spatial-resolution floor (with the honest "<5 has no
   scientific basis" + DP-harms-small-populations caveats), HDX sensitivity→access tiers, forecasts
   tiered most-sensitive (cascade-timing layer held/deferred), a per-PR release checklist, and a
   falsification trigger for the safety claim itself.
4. **Publish divergence, not a single score** *(R5)* — never a headline backsliding number; publish
   multi-source divergence (V-Dem + Freedom House + WGI), weight perception surveys below ACLED
   behavioral events. A gamed input becomes a detectable conflict, not a false green.
   **✅ DONE (2026-06-15)** — [`../indicators/voice-divergence.md`](../indicators/voice-divergence.md)
   + [`../../src/indicators/voice_divergence.py`](../../src/indicators/voice_divergence.py)
   (`make divergence`): WGI V&A × V-Dem × Freedom House reduced to signed-significant decade changes,
   combined only at sign (no blended score; disagreement beats majority; flag_basis transparency;
   missingness shown). 45 CONCUR-DECLINE / 5 CONFLICT (dissenter named) / rest weak-or-flat; 16 tests.
   *(Residual from the original note — down-weighting perception surveys below ACLED behavioral events —
   applies to the future forecasting pillar, not this corroboration layer.)*

**Tier 1 — reposition the value proposition (forecasting posture):**

> **✅ C5/R6 APPLIED (2026-06-18) as pharos-forecast v0** — [`../forecast/pharos-forecast-v0.md`](../forecast/pharos-forecast-v0.md)
> + [`../../src/forecast/pharos_forecast.py`](../../src/forecast/pharos_forecast.py): a calibration layer
> (#5), beat-a-no-change-baseline by CRPS as the pre-registered success bar (#6), portfolio-not-hero-call +
> a documented reflexivity protocol (#7). Honest v0 result: across 2,600 forecasts, **nothing beats the
> no-change baseline** — the bar is public and not yet cleared. (R1/R4 refinements — response hooks, the
> explicit "calibration over ViEWS" framing — remain for a v1.)

5. **Pharos = calibration/evidence layer, not rival forecaster** *(R4, C5)* — its additive value over
   ViEWS is the adversarial ledger + a backsliding-specific calibration harness over open V-Dem signals;
   make "OPEN/CONTESTED" a hard ship-gate enforced in code; "lit" means "publicly scored and calibrated."
6. **Beat-a-pre-registered-no-change-baseline by CRPS = the explicit v0 success bar** *(C5, R6)* —
   disclose in SAA-007 that most VIEWS-challenge models lose to a no-change baseline; adopt that as the
   public bar, turning the weakest point into a falsifiable deliverable.
7. **Portfolio-not-hero-call + reflexivity scoring protocol** *(R6)* — score a calibration curve over
   many simultaneous pre-registered forecasts, lead with aggregate Brier/CRPS-vs-baseline; pre-register
   the Goodhart/Lucas pathway and log post-warning indicator improvements as candidate warning-response
   events (publish the ambiguity). Ship the "what a calibrated miss looks like" explainer at launch.
8. **Re-baseline success on the reachable + add response hooks** *(R1)* — declare the target population
   (journalists, organizers, builders) and instrument adoption (forks, citations, downstream reuse);
   route each flagged decline to a named responder. "Peace" stays T6 and is never claimed as a deliverable.

**Tier 2 — headline demotions that close the eight QUALIFIEDs (mostly prose, high credibility payoff):**

> **✅ APPLIED (2026-06-18).** C1–C4, C7, C8 demoted in the ledger (`SAA-001/008/010`, `last_reviewed`
> bumped) and the article; C6's "necessary, not sufficient" was already in the article; C5 is the Tier-1
> forecasting item. The overstatement audit stays 0 SERIOUS and `make verify` is green. (One honesty note:
> the contested-clustering citation was corrected from a mis-remembered "Wan/Lazer 2025 PNAS" to the real
> *"Diffusion of complex contagions is shaped by a trade-off between reach and reinforcement"*, arXiv:2411.07907.)

9. **C1** — replace "few falsifiable claims" with "treats truth as instrumental — many checkable claims,
   indifferent to their truth (Huang 2015; Wedeen; Martinez)"; demote "structurally hostile" to "denies it
   the cover of manufactured ignorance." Add the signaling/forced-assent falsification trigger.
10. **C2** — in SAA-008, label evidential type (2 FORMAL / 2 EMPIRICAL-contested), re-word Otto to
    "proposed intervention framework (expert elicitation; see Smith et al. 2020 reply)," add an inline
    "Read with SAA-009" guard, and change the grade label to "ROBUST (mechanism) / QUALIFIED (thresholds)."
11. **C3** — keep the reinforcement core ROBUST; demote clustering/wide-bridges to a CONTESTED rider in
    SAA-010's `falsification_trigger` (cite Wan/Lazer 2025); drop or source "temporal persistence"; replace
    "all measurable, all buildable" with the observational-data caveat (Shalizi & Thomas 2011).
12. **C4** — soften "the substrate"/"the one move" to "a load-bearing input … among several (organizing,
    coalitions coequal)"; demote TRI to suggestive illustration *with* its contested attribution; flag
    Meadows as an untested heuristic; state the open-to-evidence scope condition up front (Dunning 2019;
    Carnegie 2024).
13. **C6** — promote "necessary, not sufficient" into the claim; require independent adversarial
    verification per entry; replace the false "would have caught it before anyone built on it" counterfactual
    with "a consulted ledger re-grades on replication and slows further build-out."
14. **C7** — replace "net-protective" with "reduces individual-targeting risk; group/place dual-use
    unsolved"; state plainly the covenant is non-binding on GPL/CC0 data; add a falsification trigger for
    the safety claim ("if a published output localizes a targetable group at actionable resolution, pull
    the layer"). *(folds into the Tier-0 threat model.)*
15. **C8** — keep feasibility as stated; re-word the theory-of-change half to "the first node is a
    necessary seed, not a sufficient cause … lone artifacts cascade rarely (Watts 2002)"; cite the OWID
    timeline honestly (~5–7 yrs + team + institutional backing) — supports "start solo," not "solo is enough."

**Tier 3 — robustness hardening on the one HOLDS:**

> **✅ C9 APPLIED (2026-06-18)** — the stricter two-sided 95% bar is computed (`counts_95pct_bar` in the WGI
> summary) and shows the VA asymmetry holds: **28 : 6 = 4.67 : 1** (vs 33 : 6 = 5.5 : 1 at 90%); "broad
> decline" softened to "most concentrated decline of any dimension (33 of 203)" in
> [`../indicators/wgi-governance.md`](../indicators/wgi-governance.md). The alternative *window* needs extra
> WGI vintages and is noted there as the remaining step.

16. **C9** — add one robustness line to Appendix A / the indicator doc: report the VA decline:improve
    ratio for an alternative window (2013→2023 or 2015→2024) and at the stricter 95% bar; soften "broad
    decline" to "most concentrated decline of any dimension (33 of 203)"; state per-dimension *n* and the
    count of countries dropped for missing 2014/2024 data. Presentation only — the core finding holds.

---

*Method note: 9 claims + 6 red-team angles, each researched by an independent skeptic instructed to
refute before grading; steelmanned, then graded only on what the evidence carries — the same workflow
applied to the [Hancock claims](graham-hancock.md) and the [backsliding ledger](../../ledger/). Full
machine output retained off-repo. Tally: claims 1 HOLDS / 8 QUALIFIED / 0 WEAK / 0 BREAKS; red-team
0 FATAL / 2 SERIOUS / 4 MANAGEABLE.*
