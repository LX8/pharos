<!--
SPDX-FileCopyrightText: 2026 The Pharos contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

# THREAT_MODEL — turning "watch power, not people" into an enforced gate

*Why this file exists.* The [`NOTICE`](NOTICE) §7 covenant and [`REPORT.md`](REPORT.md) Part V
state the **intent**: forecast *power and institutions, not people*; treat the inversion of an
early-warning tool into a targeting tool as the precise abuse to forbid; and concede that
**open question #4 — how to make openness net-protective, not net-enabling — is "not solved… a
standing obligation."** Intent is not a control. The plan-for-peace self-verification graded the
safety claim **C7 QUALIFIED** and the co-option angle **R2 MANAGEABLE only with a real
differential-publication gate** ([`docs/verifications/plan-for-peace.md`](docs/verifications/plan-for-peace.md)).
This document is that gate — Tier-0 ③ of the launch preconditions. It converts the covenant from
good-faith request into a **publish/withhold decision procedure that every layer must pass before
it ships**.

> **Bottom line up front.** The covenant is **non-binding** on the underlying GPL-3.0 / CC0
> licenses (they forbid added restrictions — `NOTICE` §7 says so plainly). Therefore protection
> *cannot* live in the license. It lives in **what we choose to compute and publish** and in the
> gate below. A motivated state can still fork the code; the defense is that there is **nothing
> in the box** worth re-pointing at people — and that we never put it there.

---

## 1. The adversary

We model the **worst plausible misuser**, not the average user:

- **A capable state (or sub-national authority)** that forks the GPL code, strips the covenant,
  and re-points the pipeline at its own population — to pre-empt dissent, target a minority
  region, or manufacture a "data-driven" justification for a crackdown.
- **What that adversary already has:** national censuses, telecom/location metadata, tax and
  ID registries, and patrol/arrest records — i.e. **finer-grained data on its own people than we
  would ever publish.** This fact is load-bearing (see the marginal-value test, §4).
- **Secondary actors:** vigilante/paramilitary groups and hostile open-source analysts who could
  combine our layers with public data to build **Demographically Identifiable Information (DII)**
  about an at-risk group.

The asset we are protecting is **at-risk groups and places** — and, derivatively, the project's
credibility, which dies if it is ever the proximate cause of someone being targeted.

---

## 2. The core finding: *aggregate ≠ safe*

The intuition "we only publish aggregates, so we're fine" is **false**, and the literature names
exactly why:

- **DII — Demographically Identifiable Information** (Raymond 2017): *aggregated data points that
  enable classification, identification, or tracking of groups by ethnicity, class, religion,
  location, etc.* A fully anonymous, person-free cell that says *"this district is 90% [group] and
  trending restive"* **is** a targeting product. DII is the pivot concept of this whole document.
- **LINDDUN** privacy threat modeling: of its seven categories, **Linkability** and
  **Detectability** fire even on anonymized aggregates — a *group* is linked/detected by place
  without any individual being named. These are our primary lenses, not "Disclosure."
- **Microsoft Harms Modeling** catalogs our exact failure modes by name: *Predictive policing*
  ("an algorithm predicts area arrests, so police make sure they match or exceed that number"),
  *Social control*, and *Public shaming via aggregation* ("how might data aggregation reveal a
  group's movements?"). We score any proposed layer against these on Microsoft's four axes —
  **Severity × Scale × Probability × Frequency** — under the **Misuse** clause: *"[a malicious
  actor] could use [layer] to cause [harm] to [at-risk group]."*

---

## 3. The harm mechanism we most fear: place-level feedback

The predictive-policing literature is the proven precedent, and it operates **at place level with
no individual named** — which is precisely our risk surface:

- **Ensign et al. 2018, "Runaway Feedback Loops in Predictive Policing"**: a Pólya-urn model shows
  that feeding **discovered** incidents (found where the state already looks) back into the system
  converges to *"only sending police to the neighborhood with the most crime"* even when true
  rates are 10% vs 11%. A forked, covenant-stripped version of our indicator that outputs *"places
  trending toward unrest"* is structurally a hotspot predictor: it concentrates state attention on
  a place, and the resulting crackdown becomes **"confirming" input**.
- **Lum & Isaac 2016, "To predict and serve?"**: PredPol on Oakland was *"predicting future
  policing, not future crime."* Same lesson: biased *discovered* data launders state attention as
  objectivity.

**Control derived from this:** a hard distinction between **discovered** signal (events surfaced by
state action — patrol records, "security deployments") and **reported/independent** signal (V-Dem
expert codings, ACLED-style independent event data, published-CI survey instruments). We weight
**independent** signal and treat **discovered** signal as feedback-poisoned. Aggregation does not
neutralize this — **place-level output is itself the weapon.**

---

## 4. The publish/withhold decision procedure (the gate)

Every proposed published layer — indicator, derived table, **or forecast** — must pass **all** of
the following before it ships. Failing any one means *coarsen, tier, or withhold.*

### 4.1 The marginal-value / counterfactual test (Shevlane & Dafoe 2020)

> **Publish a layer only if its marginal value to defenders (civil society, journalists,
> watchdogs, researchers) exceeds its marginal value to an attacker who already has the data.**

Because the state adversary already holds far finer data on its own people (§1), our **marginal
offensive contribution to people/place targeting is ≈ zero *and* redundant** — while our marginal
*defensive* contribution for **watching power** (elite behavior, institutional decay, the conduct
of the powerful) is real, because that is the data the *public* lacks. The offense-defense test
therefore **formally derives "watch power, not people"** rather than merely asserting it. Factors,
applied per layer: counterfactual possession · absorption/application capacity · whether the layer
yields a deployable *defense* · transferability of the knowledge to offense.

### 4.2 The DII test

Withhold or coarsen the moment a layer becomes **DII for an at-risk group** — even if it names no
one and is fully aggregate. Triggers: **(a)** a group attribute (ethnicity/religion/dissident
status) × a small geography; **(b)** an active-repression context (the same layer is non-sensitive
in a stable democracy and lethal under a crackdown — sensitivity is *context- and time-dependent*);
**(c)** a layer that, **combined with a public layer**, yields targetable DII (linkability).

### 4.3 The spatial-resolution floor

- **Current published surface is national-level only** (the WGI indicator is per-country —
  millions per unit, inherently non-DII). This floor is *already met* today; the gate exists for
  the moment a **sub-national or forecast** layer is proposed.
- **Enforced in code, not just prose.** [`src/audit_threat_model.py`](src/audit_threat_model.py)
  (run by `make verify`, `make verify-offline`, and `make dashboard`) scans every published
  `data/derived/*` and `data/snapshots/*` file and **fails the build** if any column name or JSON
  key resolves below country level — sub-national admin units (`district`, `adm3`, `region_code`),
  coordinates (`lat`/`lon`), or person fields (`first_name`, `national_id`). *Documented limits, so
  a green run is never mistaken for a proof:* it checks names and long-format label *values*, not
  arbitrary cell values or JSON string leaves; and genuinely ambiguous **bare** columns (`region`
  or `state` alone — which can mean a coarser continent grouping or a finer province) are flagged
  only when carrying a locational suffix, so a bare one still needs the human review below.
- **For any future sub-national layer:** never publish below first-level administrative units;
  **never attach a protected-group attribute** to a sub-national output; in active-repression
  contexts **drop one resolution tier**. Where counts are used, adopt a **stated** population
  floor with its **stated re-identification probability** (k-anonymity: max re-id ≈ 1/k) — *as a
  documented policy choice, not a law of nature.*
- **Honesty footnote (required, so no reviewer mistakes a number for science):** the ubiquitous
  *"suppress cells < 5"* rule has **no documented scientific basis** (a 2020 review found none);
  jurisdictions use 3–30. And **differential privacy is not a free lunch** — the 2020 US Census DP
  method produced a **median 52% count error for populations of 1–499**, *disproportionately
  harming the small/marginalized groups we most care about.* Therefore: **coarsen geography
  *before* adding noise, and never publish a small-area count that DP has made both noisy *and*
  targetable.**

### 4.4 The HDX sensitivity tier → access tier

Classify every layer on the OCHA/HDX four-level ladder and bind it to release:

| Sensitivity | Harm if disclosed | Release |
|---|---|---|
| **Low / none** | unlikely to harm | **Public** (default for national, power-facing layers) |
| **Moderate** | minor harm to a group | **Restricted** — aggregate-up or gated access |
| **High** | serious harm / aids repression | **Confidential** — withhold or vetted access only |
| **Severe** | severe harm | **Do not publish** |

**Any Moderate-or-above triggers a safeguard** (aggregation, tiered access, or withholding). This
is differential publication: not everything true gets published the same way.

### 4.5 Forecasts are the highest-sensitivity tier *by default*

A place-level "backsliding/unrest forecast" is functionally an **atrocity-early-warning output**
and inherits its inversion risk: *the same indicators that warn protectors warn perpetrators.*
(This dual-use of conflict/atrocity forecasting is real but **under-theorized in the literature** —
we flag it as reasoned extrapolation from §3 + §4.1, not settled consensus.) Therefore:

- Forecast **power-holders and institutions at coarse units a regime already monitors**
  (national / first-sub-national institutional level), **never populations or minority
  concentrations**.
- Treat the **cascade-timing / stage-transition layer as dual-use-critical**: a calibrated clock
  of *when* an institution will tip is the **highest-inversion-value artifact** in the design (it
  hands a regime pre-emption lead time). Hold it at **non-pre-emption resolution**, or **defer it
  entirely until open question #4 has an *answer*, not just an operationalization.**
- **Log a per-layer inversion red-team** before any forecast ships: *"how would a hostile state
  use exactly this output, and what does that change?"*

---

## 5. The capability checklist (DURC governance shape)

Borrowing the *structure* of Dual-Use Research of Concern governance (a named trigger list + a
pre-publication review gate — not the biology specifics), **any "yes" triggers mandatory review**
before a layer ships:

1. Does the layer **increase spatial resolution** to a level where a group/place becomes
   targetable?
2. Does it **add a group attribute** (ethnicity, religion, dissident status, migration status)?
3. Can it be **linked to another published layer** to yield DII?
4. Does it **lower the cost** to a state of locating a person, group, or place?
5. Is it built on **discovered** (state-action) signal rather than independent signal (§3)?

---

## 6. Honest limits & the standing obligation

- **The covenant cannot be enforced by license.** GPL-3.0 and CC BY-SA 4.0 forbid added use-restrictions, and CC0 waives all rights;
  `NOTICE` §7 relies on good faith. This gate is the *real* mitigation, and it works by
  **starving the box** — we do not compute or publish the targetable layer in the first place.
- **A determined fork can still strip the code and re-collect data itself.** Our defense is the
  marginal-value test (§4.1): against a state that already owns the population's data, our
  *additional* offensive contribution is ~zero. We do **not** add the one thing it lacks
  (a sanctioned, "objective"-looking place-level target list).
- **Residual risk is real and is not solved here.** This is **open question #4**, encoded as a
  standing obligation, not a closed problem. The gate lowers the risk; it does not zero it.

### Falsification trigger for the safety claim itself

> **If any published output is shown to localize a targetable group at actionable resolution — or
> to have been used to do so — the layer is pulled immediately, the incident is logged in this
> file, and the gate is revised before anything else ships.** A safety claim with no falsification
> condition is just a slogan; this is the condition.

---

## 7. How this gates a release (checklist)

Before merging/publishing **any new layer**, the author (or a contributor) records in the PR:

- [ ] **Target is power/institutions, not people/places** (or, if sub-national, §4.3 floor met).
- [ ] **Marginal-value test passed** (§4.1) — defensive value > offensive value vs a state that has the data.
- [ ] **DII test passed** (§4.2) — not DII alone or in combination with an existing public layer.
- [ ] **HDX tier assigned** (§4.4) and access set accordingly; Moderate+ has a safeguard.
- [ ] **If a forecast:** coarse power-facing unit only; cascade-timing held/deferred; **inversion red-team logged** (§4.5).
- [ ] **Capability checklist** (§5) — every item answered; any "yes" went through review.
- [ ] **Mosaic / small-cell check** — no published aggregate, alone or joined with an existing
      public layer, can isolate or expose a small at-risk population (small counts cross-tabbed
      with a sensitive attribute are suppressed or coarsened before release). The spatial floor
      (§4.3) is necessary but not sufficient; this is its companion rule (IMPACT.md red line 3).

---

## References

- Raymond, N. (2017). *Beyond "Do No Harm" and Individual Consent: Reckoning with the Emerging Ethical Challenges of Civil Society's Use of Data* / HDX **DII** glossary — https://centre.humdata.org/glossary-2/demographically-identifiable-information-dii/
- **LINDDUN** privacy threat modeling — https://www.linddun.org · https://threat-modeling.com/linddun-threat-modeling/
- Microsoft, **Harms Modeling** ("Foundations of Assessing Harm"), Azure Architecture Center, 2025-04-03 — https://learn.microsoft.com/en-us/azure/architecture/guide/responsible-innovation/harms-modeling/
- Ensign, Friedler, Neville, Scheidegger, Venkatasubramanian (2018). *Runaway Feedback Loops in Predictive Policing.* PMLR 81:160–171 — https://proceedings.mlr.press/v81/ensign18a.html
- Lum & Isaac (2016). *To predict and serve?* *Significance* 13(5):14–19 — https://rss.onlinelibrary.wiley.com/doi/full/10.1111/j.1740-9713.2016.00960.x
- Shevlane & Dafoe (2020). *The Offense-Defense Balance of Scientific Knowledge.* AIES — https://arxiv.org/abs/2001.00463
- OCHA/HDX **Data Responsibility Guidelines** (2021) — https://www.unocha.org/publications/report/world/data-responsibility-guidelines-october-2021
- k-anonymity & the contested "<5" rule: *Less than five is less than ideal* — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7501321 · 2020 Census DP small-population harm — https://link.springer.com/article/10.1007/s11113-022-09698-3
- DURC governance (NIH/NSABB) — https://oir.nih.gov/sourcebook/ethical-conduct/special-research-considerations/dual-use-research
- USHMM Early Warning Project, *Taking Stock of Early Warning for Atrocity Prevention* — https://earlywarningproject.ushmm.org/

*This is a living document. It is bound by, and operationalizes, the [`NOTICE`](NOTICE) §7
covenant and [`REPORT.md`](REPORT.md) Part V. Revisions are logged in
[`docs/CHRONICLE.md`](docs/CHRONICLE.md).*
