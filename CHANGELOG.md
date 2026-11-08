# Changelog

All notable changes to **Science Against Authoritarianism** (the Pharos project).
Format follows [Keep a Changelog](https://keepachangelog.com). The project was **private**
until its first public release on 2026-11-08; entries before that are internal milestones, and
their tags and commit ids refer to the non-public pre-publication history.

> **Note on the two 2026-06-18 tags.** `0.3.0` and `0.4.0` were cut the same day as two
> sequential internal milestones, not a same-day re-release: `0.3.0` landed the second
> (forecast) pillar and the self-auditing repo; `0.4.0`, later that day, doubled the ledger
> (15 → 35 entries) and filled out the simulator/forecast corpus. Read them in that order.

## [Unreleased]

### Added — the landing page is live (2026-11-08)
- `site/index.html` is published with GitHub Pages at <https://lx8.github.io/pharos/> by the new
  `.github/workflows/pages.yml`, which deploys only the landing page (`index.html` + `style.css`);
  the interactive observatory needs the local server and stays local. The page now carries the
  project's name, **Pharos** (it had the working name "Aty Guasu"), drops its working-draft banner,
  links to the repository, and points `canonical` / `og:url` at the live address. The workflow first
  re-runs the page's own checks (pinned figures, overstatement guard, site tests) and deploys only if
  they pass.

### Fixed — public wording aligned with the project's own records (2026-11-08)
- An independent review before the launch found page text that claimed more than the repository
  supports. The three instruments are now described as overlapping, not independent (as in
  `docs/indicators/voice-divergence.md`), on the page and in the generated brief and watch report;
  the VIEWS Challenge gloss and `docs/forecast/pharos-forecast-v0.md` follow ledger entry SAA-040;
  "every public number" became "every headline figure", "every formula" became "every load-bearing
  formula (5 of 6 bit-exact)"; the threat-model text says which part is enforced and that its
  release checklist is open; the simulator citations list the results actually reproduced (Xie et
  al. 2011, Johnson & MacKay 2015, Fortunato 2004), with Centola et al. 2018 as the experimental
  contrast; the code licence reads GPL-3.0-or-later; the ledger card shows the OPEN grade.

## [0.7.0] — 2026-11-08 — first public release: the local observatory, the forward score, collective credit

### Published — first public release (2026-11-08)
- Published at <https://github.com/LX8/pharos> as a project for the public, built for the good of
  humanity and the environment. Credit is collective — **The Pharos contributors** — in every
  license header and in `LICENSE`, `NOTICE`, `AUTHORS`, `CITATION.cff`, `.zenodo.json` and
  `REUSE.toml`; personal names, e-mail addresses, ORCID iDs and account handles were removed.
  The licenses themselves are unchanged.
- Notes about private working setups and unrelated projects were removed or reworded
  (`docs/RFC_PARTNERSHIPS.md` and `.github/CODEOWNERS` dropped). Status lines that called the
  repository private were updated, and `.gitignore` now blocks secrets, credentials and local
  AI-assistant files.
- The repository starts from a single commit; earlier history is not public. See `SNAPSHOT.md`.
- Published before three pre-registered commitments were met (the two-coder H1 bias audit, an
  independent second grader, the `THREAT_MODEL.md` §7 release checklist); all three remain open.
  See the deviation note in `STATUS.md`.

### Added — the local Pharos observatory (2026-09-23)
- `./pharos serve` opens a loopback-only browser app (`site/app/`, served by
  `src/pharos_server.py`) over the existing research: the evidence ledger, indicator
  disagreements, forecast and calibration results, the seven mechanism demonstrations, and real
  offline verification runs with receipts. It adds no new formulas, grades or forecasts.
  29 new server/runner/CLI contract tests (264 → 293), plus 7 Node UI-control tests
  (`node tests/test_pharos_controls.cjs`). See `docs/LOCAL_OBSERVATORY.md`.

### Fixed — the forward forecast registry can now be scored (2026-10-31)
- `pharos_forecast._load_panel` capped every panel at 2024, live data included, so
  `prediction_registry.py --score` could never see a realized year and always printed
  "no realized data". The cap now applies only to the pin and the backtest.
- `--score --live` hashes the release before writing anything, pins it once under a name that
  carries its hash (`data/snapshots/vdem_freexp_realized_<date>_<sha8>.csv`, never overwritten), and
  records the score in `data/derived/prediction_registry_scores.json`. A later run on the same data
  keeps the first score's dates and adds `last_confirmed`; `--score --panel PATH` re-scores offline
  and leaves the file byte-identical. A fetch that lacks the origin year for most countries fails
  with nothing written. `--score` works in any argument order, and the frozen registry can no longer
  be re-issued by accident (`--reissue` is required).
- Each score also reports a climatology reference with the same spread, matched to the horizon (the
  leak-free mean change from the pinned input the registry was issued from), the number of decline
  events, whether the result is prospective, and a vintage check of the realized data against the
  June pin.
- `drift_check.py` reports the newest upstream V-Dem year, which the derived comparison cannot see.
  `make score` and `make cycle` (drift report, forward score, offline dashboard) run the routine in
  one command; the cycle reports drift without stopping on it. SPDX header of
  `prediction_registry.py` corrected; the realized pins are covered in `REUSE.toml`.
- The frozen registry's `scoring_rule` field (issued 2026-07-24) still says `--score`; since this
  fix, scoring needs `--live` or `--panel PATH` (`make score`). The frozen file is left unchanged.

### Measured — first score of the forward registry (2026-10-31)
- All 174 frozen 1-year forecasts (origin 2024, issued 2026-07-24) scored against the 2025 values of
  the V-Dem freedom-of-expression series (via Our World in Data). No-change: CRPS 0.02165, Brier
  0.08592. Climatology reference: CRPS 0.02195, Brier 0.08497. No-change is better on CRPS (skill
  +0.013; an ad-hoc bootstrap over countries, not part of the committed scoring code, puts this
  year's 95% interval at about +0.007 to +0.021) and
  worse on Brier. That split is expected at a one-year horizon, where both forecasts overpredict
  declines; it matches the 10-year backtest against global climatology, while the 2012-2014 hold-out
  favoured no-change on both. It is not independent confirmation. 16 of 174 countries declined by at
  least 0.05.
- Timing: the October download matches the June pin on every 1990-2024 value, so it is the same
  V-Dem release, and 2025 was very likely already in the June download; only the 2024 cap dropped
  it. The forecasts never used 2025 (μ = 0, σ from data up to 2024), so the score is blind but
  retrospective, and the record says `prospective: false`. The 3-year target (2027) is the first
  prospective test.

### Added — ledger entry SAA-041 (2026-08-28)
- **SAA-041** (`three-five-percent-rule`, CONTESTED, social-change) — the 3.5% rule is a strong
  descriptive tendency, not a law: its own author documents the exceptions and warns against
  prescriptive use (Chenoweth 2020). Ledger 40 → 41 (20 ROBUST / 19 CONTESTED / 1 REFUTED / 1 OPEN).

### Added — ledger entry SAA-040 + an in-ledger overclaim correction (the coverage gap, round 2)

The methodology audit flagged that the project's *own target domain* (conflict/backsliding
forecasting) was among its thinnest — and that the project's framing of the VIEWS baseline finding
was overstated. Both fixed in one entry:

- **SAA-040** (`conflict-forecasting-track-record`, CONTESTED, conflict-risk) — the direct prior art
  for the project's own forecasting pillar: ViEWS/VIEWS (Hegre et al. 2019, JPR), the published
  out-of-sample track record (Hegre, Nygård & Landsverk 2021, ISQ — "reasonably accurate," worse on
  low-level conflict, recall 0.8 / precision ~0.6), PITF (Goldstone et al. 2010, AJPS — factional
  partial democracy as top risk factor), and the two VIEWS competitions (2022 escalation; 2025
  fatality, CRPS-first). Five citations, every DOI web-verified by a primary-source fact-check pass.
- **The overclaim correction (the honesty payload).** SAA-007 and the forecast docstring claimed "in
  the VIEWS prediction competitions *most models are beaten by a no-change baseline*." The primary
  sources support a **narrower, metric-conditional** finding: a no-change/persistence baseline is a
  *hard benchmark* many models fail to beat under MSE on zero-inflated fatality *levels*, but in the
  2022 escalation competition an **ensemble beat the average model** and **almost all participant
  models outperformed the benchmark models for most metrics** — the field has called for *new
  metrics*, not declared the baseline the winner. SAA-007's trigger and evidence, and the forecast
  module docstring, are reworded to the verified truth and cross-reference SAA-040. The corrected
  framing *strengthens* the forecast pillar: it no longer leans on an overstatement, and the lesson
  — "the same discipline this project applies to fascism's disinformation engine applies to itself" —
  is itself the point. Ledger 39 → 40 (20 ROBUST / 18 CONTESTED / 1 REFUTED / 1 OPEN); full count
  cascade re-pinned; dashboard 7/7.

### Added — the project put to the test (four live measurements, 2026-07-24)

Turning the static v0 into something actively tested against the world. Four measurements, each
recorded (not just run), each enacting the project's falsifiability-first discipline. 252 → 264
offline tests; dashboard 7/7; verify-offline green.

- **Live-drift measurement (T1).** Ran `make drift` against the live upstream (WGI/V-Dem/FH via
  OWID) ~5 weeks after the June pin. Result, recorded in
  [`docs/verifications/LIVE_DRIFT_2026-07-24.md`](docs/verifications/LIVE_DRIFT_2026-07-24.md):
  **the indicators are current.** The flagged WGI "drift" is 6 country-name spelling revisions
  only — zero score changes, zero CI changes, zero verdict flips across all 1,222 country-dimension
  cells. The published numbers reproduce exactly from the live world.
- **Out-of-sample forecast hold-out (T2).** New `src/forecast/oos_holdout.py`: holds out the three
  most recent origins (2012/2013/2014, scored against the newest realized years 2022/2023/2024) and
  re-runs the leak-free backtest on ONLY those. Result (`data/derived/oos_holdout.json`): the
  negative verdict **HOLDS out-of-sample** — on 522 held-out forecasts, nothing beats no-change
  (the decline base-rate is higher on recent years, 0.40 vs 0.27, yet still nothing predicts
  *which* countries). The research claim survived its hardest test.
- **Bias-audit execution (T3).** New `src/bias_audit_run.py` ran the mechanical parts for real:
  **H2 (partisan-object) PASSES — 0 entries name a living politician/party as object of blame**;
  **H3 (symmetric reporting) PASSES — every surface pairs declines with improvements**. H1
  (valence–grade) was run as an explicitly-labeled **non-authoritative single-coder dry-run**
  (ΔP −0.14, no skew) that proves the pack→scorer pipeline runs cleanly — the pre-registered H1
  result still requires the two independent human coders (§8), and the report
  ([`docs/verifications/bias-audit-2026-07-24.md`](docs/verifications/bias-audit-2026-07-24.md))
  says so plainly rather than overclaiming.
- **Forward prediction registry (T4).** New `src/forecast/prediction_registry.py`: a dated, frozen
  set of 174 countries × 2 short horizons (2025, 2027), each a no-change forecast with leak-free
  spread and input provenance, scoreable later with `--score`. This turns "we can't beat baseline"
  from a retrodictive claim into an **actively-testable, time-stamped commitment** — the
  falsifiability thesis made executable going forward. No hero call (R6).

### Added — external adversarial audit → Tier A (hardening) + Tier B (methodology)

A four-specialist independent audit (engineering, methodology, responsible-AI, DX) of the whole
project, then implementation of the safe fixes (Tier A) and the methodology hardening (Tier B).
241 → 252 offline tests; dashboard 7/7; `verify-offline` green. Every headline verdict survived and,
where the science moved, it moved toward *more* honest negative results — the discipline working on
itself, entered into the self-correction record.

**Tier B — methodology (the load-bearing science):**
- **Forecast harness made leak-free.** `sigma` and the climatology means were fitted on the *full*
  panel including the outcomes being scored (structural look-ahead leakage). Refit per origin year
  from history ≤ T only. The old `climatology` +0.007 CRPS-skill "win" over no-change was a
  **leakage artifact** — it disappears (→ −0.16) once the harness stops fitting on the answers. The
  pre-registered "nothing beats the no-change baseline" verdict is therefore *strengthened*, not
  weakened, and the harness can now be trusted to credit a genuinely skillful v1.
- **Stronger baselines added.** Per-country climatology (a country's own mean drift) joins no-change
  and global climatology as a third no-skill reference; the verdict now requires beating *all three*.
  Per-country drift loses badly (CRPS skill −0.58 — a country's own past change is noise, not signal).
- **WGI cross-year independence, swept not assumed.** The change test treated the 2014/2024 estimates
  as independent (ρ=0). They share WGI's overlapping source set, so the true ρ is positive. For a
  *difference* test ρ=0 is the **conservative** choice (a counterintuitive result the sweep itself
  surfaced — the audit and the author's first instinct had the direction inverted): positive ρ makes
  the difference *more* precisely estimated, flagging *more*. The headline 33:6 VA ratio (ρ=0) is
  therefore a **lower bound**, and a new `independence_sensitivity` sweep (ρ=0→0.9, ratio holds
  2.4–5.5:1) ships in `va_robustness` so the assumption is shown, not taken on faith.
- **Triangulation reworded + threshold sensitivity.** "Independent corroboration" → "multi-source
  concurrence" (V-Dem feeds WGI; V-Dem/FH share coder networks — the instruments are *not*
  independent). A new `threshold_sensitivity` sweep (±20% on the V-Dem 0.05 / FH 3.0 judgment-call
  dead-bands) ships in `voice_divergence.json`: the 45/8 CONCUR-DECLINE/IMPROVE headline is stable
  (40–45 vs a steady 8) across the sweep.

**Tier A — hardening (no published-number changes):**
- **Closed the data-contract lie.** Every derived JSON now carries an `input_provenance` block
  (`source_url`, `fetched_utc`, `input_sha256` of the pinned snapshot) — the contract promised this
  and 2 of 3 files were missing it (`forecast_backtest.json` had none). A swapped upstream snapshot is
  now detectable from the derived file alone.
- **Closed two latent crashes** in the forecast public API: `ZeroDivisionError` on an empty panel,
  `IndexError` when no candidate models remain. `wgi_governance` `IndexError` on an empty record set
  guarded; `CSV_FIELDS` defined once (DRY).
- **The public site is now in the honesty audit** (`audit_overstatement` scans `site/index.html` with
  HTML tag-stripping) — the marketing layer where claim-creep matters most was the one place it
  wasn't policed. **The threat-model gate banners its blind spot** on every green run (name/label
  scan only; cell values and JSON leaves unchecked) so a clean build is never mistaken for a proof.
- **`verify-offline` now regenerates `BRIEF.md`/`WATCH_REPORT.md`** (no-args verify) — closes the gap
  where fresh derived data could ship with stale generated docs.
- Zenodo↔CFF date mismatch fixed (`2026-07-04`→`2026-07-16`); `.zenodo.json` license → GPL-3.0-or-later
  (matches `upload_type: software`). REUSE.toml dead globs removed; `.dockerignore` added.

### Added — ledger entry SAA-039 (the OPEN backlog, round 1 of the promised "next round")
- **SAA-039** (`institutions-prosperity`, CONTESTED, political-economy) — the Acemoglu–Johnson–Robinson
  program: the institutions–prosperity *correlation* is ROBUST (accepted even by its critics), while the
  *causal* claim (inclusive institutions → long-run prosperity) is CONTESTED — the settler-mortality IV is
  challenged on the data (Albouy 2012), the exclusion restriction and construct (Glaeser et al. 2004), and
  the reversal-of-fortune evidence (Chanda-Cook-Putterman 2014); AJR's Reply defends it; the 2024 Nobel is
  recognition, not measurement. Layered exactly like SAA-032, its sibling on the other wealth↔institutions
  arrow. Verify-first: drafted by a research agent, attacked by two independent reviewers (citation +
  grade-rubric), and every load-bearing fact re-verified by hand — which caught a real error (the draft
  said settler mortality instruments "colonial-era" institutions; it instruments *current* institutions)
  before it shipped. Ledger 38 → 39 (20 ROBUST / 17 CONTESTED / 1 REFUTED / 1 OPEN); full count cascade
  re-pinned; dashboard 7/7.
- **Held for founder review** (not committed): two more backlog drafts — Chenoweth's 3.5% rule and
  Stanton's Ten Stages — researched and twice-reviewed but held because hand re-verification could not
  confirm specific figures (Chenoweth's Brunei-1962 / 88.89% in-dataset numbers) or found a load-bearing
  clause thinly sourced (Stanton's "stage theory is contested"). The ledger admits only what fully
  survives verification.

## [0.6.0] — 2026-07-16 — the impact arc: strategy verified, every buildable lever shipped, summary layer hardened

**An adversarially-verified impact strategy (18 claims, each attacked before being relied on) and every buildable lever from it: the trust-signals surface, the generated plain-language brief, the data contract + vendorable client, the pre-registered (and now fully executable) bias self-audit, the flagship watch-report prototype, and the H3 symmetric-reporting machine gate. Then a seventh adversarial round turned on the new tooling itself — ten defects found, fixed, and entered into the self-correction record, the most instructive being unequal-significance-bar overclaims in our own summary prose. Repository governance (PR/issue templates, CODEOWNERS), cross-platform reproducibility (.gitattributes), verified Python-3.9 floor, and 166 → 240 offline tests. Still private; the publication gate, the flagship's name and cadence, and the audit's human coders remain the founder's.**

### Fixed — R7 adversarial review: the summary layer had drifted from the canonical numbers
- A seventh independent adversarial review (the tooling & summary layer) confirmed 10 defects;
  all fixed. The instructive ones: **our own generated prose and the public site presented the
  ≥2-significant concurrence count (45) as an all-three-instruments claim** — false for 19 of
  the 45 (two of those countries' third instrument moved in the *improving* direction) — while
  the canonical indicator doc was correct throughout; the Watch Report paired the strict
  26-country bar with a loose 8 as "the same full concurrence" (true same-bar figure: 5).
  Every surface now states both bars, and the strict figure is **pinned** (`concur_decline_full3`)
  so they cannot blur again.
- The bias-audit blind pack **was not blind** (uppercase-only masking left "Refuted" in a title
  and lowercase grade words in prose) — masking is now case-insensitive for the grade-loaded
  words, with the "open" residual documented. The promised exact 95% CI is now **implemented**
  (Clopper–Pearson per proportion, pure stdlib, pinned to published values).
- The spatial-floor gate gained encoded point-geolocation tokens (geohash, plus_code, quadkey,
  MGRS, what3words) and national person-ID schemes (aadhaar, cpf, curp, cnic, …); the corpus
  test caught a tokenizer gap during the fix itself. The reuse client no longer coerces
  'nan'/'inf' cells into non-finite floats. IMPACT's verification headline corrected to match
  its own table (9 SUPPORTED / 9 MIXED).

### Added — repository governance + CLI reach
- **Git design** — `.github/pull_request_template.md` (the pre-merge checklist = the gate restated),
  `.github/ISSUE_TEMPLATE/falsification-challenge.md` (the on-mission "meet a trigger with evidence"
  template), and `.github/CODEOWNERS`; new governance files covered by `REUSE.toml`. CONTRIBUTING
  gains the branch + linear-history + PR-template note.
- **App** — `pharos brief` and `pharos report` surface the generated BRIEF.md / WATCH_REPORT.md
  through the one command (header-stripped for the terminal); wired into the subcommand list and
  the README quick-start. Tested.

### Added — the impact arc: verified strategy + every buildable lever shipped
- **`docs/IMPACT.md`** — the evidence-backed impact strategy: 18 adversarially-verified claims
  (9 SUPPORTED / 9 MIXED / 0 REFUTED) → a falsifiable theory of change, 8 ranked levers tagged
  buildable-now vs founder-gated, pre-defined uptake metrics (no tracking — the watch-power law
  binds our own telemetry), and 6 red lines. Carries its own falsification trigger.
- **`docs/TRUST_SIGNALS.md`** (+ site "How to check us" fold) — every trust norm made legible:
  norm → enforcing mechanism → the command that verifies it; self-correction record first. Its
  own numbers are gate-pinned (3 new count/figure pins, bite-tested).
- **`docs/BRIEF.md`** + `src/brief.py` (`make brief`) — the plain-language read, *generated* from
  committed derived data; deterministic, freshness-gated; the noise floor leads and the negative
  forecast result survives translation.
- **`docs/DATA_CONTRACT.md`** + `src/pharos_client.py` — the reuser's on-ramp: column-by-column
  contract with additive-only guarantees, and a vendorable one-file stdlib read-only client
  (vendorability, stdlib-only, and read-only all machine-tested).
- **`docs/BIAS_AUDIT_PREREGISTRATION.md`** + `src/bias_audit.py --pack` — the pre-registered
  self-audit for directional bias (blind valence coding with fixed skew criteria; results publish
  including nulls); deterministic blind-pack generator with grade tokens masked. The run is
  founder-gated and doubles as second-grader onboarding.
- **`docs/WATCH_REPORT.md`** + `src/watch_report.py` (`make watch-report`) — the flagship-edition
  prototype: the Watch List (full three-instrument concurrence) as the single carryable object,
  symmetric movements by construction; the public name and fixed cadence remain the founder's.
- **Symmetric-reporting machine gate** (H3) in the counts audit — no surface may report the
  meaningful-decline count without its improvement counterpart; **mosaic/small-cell rule** added
  to the THREAT_MODEL release checklist (IMPACT red line 3).
- **`.gitattributes`** — generated-file line endings pinned (CSVs `-text`, JSON/INDEX `eol=lf`)
  so the byte-exact offline gate holds on autocrlf clones; policy + reality both tested.
- `src/drift_check.py` hardened after adversarial review: children forced live
  (`SAA_OFFLINE=0`) so an ambient offline env can't produce a false "current"; clean
  missing-file error. Tests 180 → 218 across the arc.

### Added — `make drift`, input-freshness reconnaissance
- The ledger has a staleness gate; the *input data* did not. New `src/drift_check.py` (+ `make drift`)
  answers "is the pin still current?" — it recomputes the indicators and forecast from the **live**
  sources, compares the substantive numbers against the committed pin (ignoring the `mode`/`fetched_utc`
  stamps), reports any change, and **restores the pin byte-for-byte**. It reads the live world, never
  adopts it (a re-pin is a human-reviewed `make snapshot` decision). Running it end-to-end caught two
  bugs before they shipped: the restore round-tripped through text mode and silently rewrote the
  derived CSVs' CRLF line endings (now byte-exact binary I/O, pinned by a regression test), and a slow
  upstream fetch crashed instead of degrading to "freshness unverified" (now caught). A `2026-07-04`
  live check confirmed upstream matches the pin exactly.

### Improved — site design details, controls, and references
- **§08 "Sources & further reading"** — the page cited findings but named no sources, off-brand for
  *cite only what is measured*. A curated, repo-verified reference list now closes the page (WGI,
  V-Dem/FH via OWID, ViEWS + the Prediction Challenge, Gneiting & Raftery, Paxton, Bermeo, the six
  simulator source papers, Wineburg & McGrew).
- **Pure-HTML disclosure controls** (`<details>`, no JS): *"How the measurement works — in one
  paragraph"* under the headline finding, and *"What the grades mean — and what would change our
  minds"* under the pillars — the grade legend (incl. a new OPEN pill) plus the falsification-trigger
  contract, previously only in the repo docs.
- **Design details**: a keyboard skip-to-content link; fold/legend/reference styling in the
  night-observatory theme; `rel="noopener"` on external links. All seven pinned site figures verified
  still matching exactly once.
- **The site's *structure* is now machine-checked too** — new `tests/test_site.py` (6 tests): every
  class used in the HTML must have a CSS rule (the OPEN grade pill once shipped without one), in-page
  anchors must resolve, external links are https-only, `role="img"` carries an aria-label, the
  disclosure controls stay balanced, and all four grade pills are styled. STATUS backlog rows brought
  current (the software build → **DONE** as `./pharos`; Tier-3 C9 → fully done incl. the alt-window).
  `make verify` grew **166 → 172** offline tests.

## [0.5.0] — 2026-07-04 — adversarially verified, hardened, and made runnable

**The whole repo swept by six independent adversarial review rounds (citations, formulas, grades — real
defects found and fixed each time), the honesty gates extended to every public number, the ledger given
its read surface and grown to 38 entries, and the project made runnable as one command (`./pharos`).**

**A read-only whole-project verification returned ZERO correctness bugs; the implementable subset
of its findings was landed as hardening — no new claims, no scope growth.**

### Added
- **Threat-model data gate** — new `src/audit_threat_model.py` enforces the
  [`THREAT_MODEL.md`](THREAT_MODEL.md) §4.3 "watch power, not people" spatial floor *in code*: every
  published `data/derived/*` and `data/snapshots/*` file is scanned, and the build **fails** if any
  column/key drops below country/institution level. A three-layer matcher — atomic token denylist,
  regexes for arbitrary admin levels (`adm3`, `admin5`, `nuts2`), and qualifier→suffix adjacency for
  snake_case person/geo fields (`first_name`, `national_id`, `state_code`) — catches real-world
  spellings while `year_latest` / `country_name` / `state_capacity` never false-positive; it also
  scans long-format *label values* (a `variable` column whose rows say `latitude`). Wired into `make
  verify`, `make verify-offline`, and `make dashboard` (now **6 audits**). Ships with a data-driven
  `tests/test_audit_threat_model.py` that pins both recall and precision. `make verify` grew **118 →
  126** offline tests.
- **`docs/forecast/CALIBRATED_MISS_EXPLAINER.md`** — the R6 reflexivity artifact the forecast doc
  twice promised: a plain-language account of why a calibrated 30%-that-resolves-false is the system
  working, not failing. Linked from both promise sites in `pharos-forecast-v0.md`.

### Changed
- **C9 robustness finished** — the Voice & Accountability decline asymmetry now also reports an
  alternative in-snapshot window (2015 → 2024) alongside the primary (2014 → 2024) at both the 90%
  and 95% bars — a tight **~4.7–5.5 : 1** band; both windows ship in `va_robustness` in the derived
  summary, surfaced in [`docs/indicators/wgi-governance.md`](docs/indicators/wgi-governance.md).
- **SAA-007 honesty caveat** — its Evidence section now names the VIEWS-competition result (most
  models are beaten by a no-change baseline under fair CRPS scoring) and cross-links the project's
  own forecast pillar, so the ROBUST grade is explicitly narrow (the *infrastructure* exists).
- **Defensive `json.load`** in `audit_counts`, `ledger_validate`, and `wgi_governance` — a malformed
  snapshot or index now raises a friendly, contextual error instead of a raw traceback.

### Hardened (second adversarial review — whole-repo, 7 dimensions)
A follow-up review across code/sims/tests/ledger/citations/consistency/licensing confirmed 5 small
real defects (all test-scope or not-overclaim honesty; no correctness bugs) — now fixed:
- **`egalitarian_revolution()` relabelled honestly** — its dynamics are a deterministic level-or-submit
  best-response whose separatrix equals the Lanchester critical mass *by construction*; it never
  reproduced Gavrilets' *emergent* basin, so the docstrings + `docs/sims/README.md` no longer imply
  that, and a new `test_revolution_is_threshold_classifier` pins the actual (modest) property.
- **Overstatement gate scans claim-bearing bullets** — `_is_exempt` no longer blanket-exempts every
  `- ` bullet (citation bullets stay covered by the URL rule), so the ledger's bullet-form prose is
  now subject to the honesty gate; regression tests pin both directions (still 0 SERIOUS).
- **Doc-count guard can't silently go dark** — new `unmatched_doc_patterns()` + a test fail if a
  reworded doc makes a count pattern stop matching (which would leave that count unguarded).
- **SAA-033** in-text citation year corrected (Rau & Stokes PNAS **2025**, matching its frontmatter).
- **`ledger_validate`**: documented why `title` is intentionally excluded from the index cross-check
  (index carries a curated short label, deliberately not byte-identical to the frontmatter title).

`make verify` now **130 tests**; `make dashboard` 6/6 GREEN; overstatement 0 SERIOUS.

### Hardened (third review — full-ledger citation-integrity web sweep)
Every source across all 35 ledger entries + `REPORT.md` was independently web-verified (PubMed /
CrossRef / arXiv / DOI), each finding double-checked before fixing. **No fabricated or retracted
sources; 6 small attribution errors corrected:**
- **SAA-030** — the Kalmoe & Mason (2022) PNAS letter carried a 2020 Voter Study Group blog-post
  title stitched onto its PMID; corrected to the real title (*"A holistic view of conditional
  American support for political violence"*, PNAS 119(32) e2207237119) and reconciled the Evidence
  prose, which had double-counted that one letter as two separate critiques.
- **SAA-017** — Hollander & Turowetz (2018) page range `293-304` → `301-309` (the range its own
  PubMed/CrossRef record gives).
- **SAA-012** — Erdal & Whiten's coined term corrected `counterdomination` → **counterdominance**.
- **REPORT.md** — three reference titles were paraphrases/slug-derived strings, not the works' real
  titles (Roozenbeek et al. 2020 cross-cultural prebunking; Seabrooke et al. 2025; the VIEWS
  *Prediction Challenge*); replaced with the published titles + authors so each resolves on search.

`last_reviewed` bumped to 2026-06-21 on the three edited entries; `make dashboard` 6/6 GREEN.

### Fixed (fourth review — differential verification of the quantitative pillar)
Every load-bearing formula was independently reimplemented and cross-checked against both the
committed outputs and its canonical published form (CRPS · Brier · the WGI 90%-CI z-test · the VA
window counts · the divergence sign-combination · the climatology baseline + decline base-rate).
**5 of 6 reproduced bit-exactly** (independent reimplementations matched to 0.00e+00) — and one real
bug surfaced:
- **`pharos_forecast.backtest()` alias-mutation** — `base = per_model["no_change"]` aliased the dict
  the display-rounding loop mutates, and `no_change` is iterated first, so later models computed
  CRPS/Brier **skill against the 5-dp-rounded baseline** instead of the full-precision one. Fixed by
  capturing `base_crps`/`base_brier` before rounding. Corrects `trend` crps_skill −0.5601 → −0.5602
  and `damped_trend` −0.1921 → −0.1922 (4th-dp; changes no verdict — both still lose to the
  baselines). The committed `data/derived/forecast_backtest.{json,csv}` are regenerated, so the
  offline drift gate now pins the corrected values.

### Documented (fifth review — independent ledger grade-calibration)
All 35 entries were independently re-graded against `docs/GRADING_PROTOCOL.md` by a second grader,
each disagreement adjudicated by a third read. **0 clear rubric violations** — the grading holds up:
no unsupportable grade, no missing required split, no grade-vs-trigger contradiction. The pass
surfaced one house-style question (how a robust-core/weaker-layer entry composes its single
frontmatter grade), resolved by **documenting the existing convention** rather than re-grading:
- **`docs/GRADING_PROTOCOL.md` rule 4 ("Compose to the headline")** — the single frontmatter grade
  is scoped to what the entry's *title* asserts, with the per-layer split living in the Claim prose +
  `falsification_trigger`; a pre-hedged title keeps the robust core's grade (SAA-025/031), a title
  that implies the contested causal reading drops to that layer (SAA-023/024, SAA-032–035). No
  published grade changed.

### Documentation — verification reference + presentation sync
- **New [`docs/VERIFYING.md`](docs/VERIFYING.md)** — a professional, detailed verification reference:
  the four-rung ladder (`dashboard` / `verify-offline` / `verify` / `hooks`), the six audits
  explained, the offline-determinism guarantee (pinned snapshots + sha256 + drift gate), the free
  local-CI hooks, and the five-round adversarial-review regime.
- **README** gains a dedicated **Verification** section + a tests/audits badge linking the reference;
  the new "130 offline tests" headline is now drift-guarded by a `DOC_CHECKS` pin in `audit_counts`.
- **Site** "Self-auditing" card surfaces the spatial-floor gate, offline reproducibility, and the
  adversarial-review sweep; **STATUS** dated 2026-06-21 with a pointer to the verification reference.

### Added — ledger read surface + falsification watch
The ledger's *write* and gate (`validate`/`staleness`) phases were covered, but its **read** phase
was not: 35 entry files with only a
machine-readable `index.json`. Now there is a human surface, generated and drift-gated:
- **New `src/ledger_digest.py` → [`ledger/INDEX.md`](ledger/INDEX.md)** — a by-grade index of every
  entry (claim · domain · verified · computed next-review date) **and a falsification watch**: each
  entry's pre-registered "what would change our minds" trigger in one place — the asset that
  distinguishes a falsifiable ledger from advocacy. Generated from the frontmatter (the source of
  truth), fully deterministic (next-review = `last_reviewed + interval`, no clock). A **coverage-by-
  domain** table shows where the evidence is concentrated (political-economy, psychology, sociology)
  and, by its thin spots, where the next entries belong.
- **`make index`** regenerates it; a **seventh dashboard audit** (`ledger index`, also in
  `verify-offline`) and a committed-file freshness test **fail on any drift**, so the browseable view
  can never silently diverge from the entries. `make verify` grew **130 → 136** offline tests.

### Added — the site's claim made true: computed figures pinned to the data
The site asserts "every public number is machine-checked" — but several of its own *computed*
headline figures were not actually checked (only the entry count was). Closed that honesty gap:
- The consistency gate (`audit_counts`) now also recomputes the site's headline figures **from the
  committed derived data** and fails on any drift — `88%` within noise (1080/1222), the `88:54`
  decline-to-improve split, `45` concur-decline countries, and `2,600` pre-registered forecasts all
  come from `data/derived/*` via `compute_derived_figures`. So a re-snapshot that shifts a number
  can no longer leave the public page quietly wrong. Tests pin both the match and that the gate bites.
  `make verify` grew **136 → 138** offline tests.
- Extended the figure gate from the site to the **detailed indicator + forecast docs** (where the
  load-bearing quantitative claims live): `wgi-governance.md` (`88%`, `1,080`, the `88 : 54` split)
  and `pharos-forecast-v0.md` (`2,600` forecasts) are now pinned to the derived data too — and a
  `unmatched_figure_patterns` guard fails if a reworded doc silently un-pins a figure.

### Added — a seventh validated simulator: bounded-confidence opinion dynamics
- **New `src/sims/sim_opinion_dynamics.py`** (Deffuant–Weisbuch 2000) — the opinion-dynamics
  mechanism the corpus was missing, and the micro-foundation under the polarization thread
  (`SAA-026`/`SAA-027`): agents adjust toward each other only within a confidence threshold ε. It
  reproduces the **published, robust** results — the **ε = 1/2 consensus threshold** (Fortunato 2004,
  topology-independent) and the **monotone fragmentation** as confidence narrows — while honestly
  **not** asserting the exact `~1/(2ε)` cluster count (a stochastic rule of thumb), the same
  scoped-validation discipline as the other sims. Stdlib, seeded, deterministic; 6 validation tests.
  The Tier-1 corpus is now **7** mechanisms; `make verify` grew **139 → 145** offline tests.

### Added — `pharos`, the project as one command
- **New `src/pharos.py` + `./pharos` wrapper + `make pharos`** — a single stdlib-only CLI that turns
  the verified components into a runnable tool: `pharos ledger [--grade --domain --search]` browses and
  searches the graded entries; `pharos show SAA-031` prints one in full; `pharos watch` is the
  falsification watch; `pharos coverage` is the by-domain map; `pharos indicators` / `divergence` /
  `forecast` print the computed results; `pharos verify` runs the seven audits. It reads only the
  committed source of truth (ledger frontmatter + `data/derived`), so every number it shows is the
  verified one, and it wraps the existing pure cores (no reimplementation, no dependencies, no install).
  11 tests cover every subcommand; `make verify` grew **145 → 156** offline tests.
- Then added **`pharos stale`** (live review status — which entries are due/overdue, the one view that
  *can't* be a committed file because it's clock-dependent) and **`pharos stats`** (a one-glance summary,
  every number derived so none can drift). `make verify` grew **156 → 159** offline tests.

### Added — ledger entry SAA-036 (systems & technology, the thinnest lens)
- A new **CONTESTED** entry on **algorithmic "rabbit-hole" radicalization** — a *myth-correcting* one,
  in the project's cite-only-what-is-measured spirit. The best recent observational + counterfactual
  work (Hosseinmardi et al. 2021 *PNAS*; Chen, Nyhan et al. 2023 *Science Advances*; Ledwich & Zaitsev
  2020 *First Monday*) finds extremist YouTube consumption is **largely demand-driven** — concentrated
  among already-resentful users arriving via subscriptions and off-platform links, not the recommender
  marching ordinary users into a rabbit hole — while a ~100k-sock-puppet audit (Haroon, Wojcieszak et
  al. 2023 *PNAS*) keeps a real-but-smaller algorithmic-amplification effect genuinely open. Graded with
  an explicit layer split; **every citation web-verified** before writing. The ledger is now **36
  entries** (18 ROBUST / 16 CONTESTED / 1 REFUTED / 1 OPEN), and the systems-and-technology lens — the
  thinnest on the coverage map — is no longer a singleton.
- **SAA-037** (democratic-backsliding, **ROBUST**) — *modern democratic backsliding is mostly gradual
  executive aggrandizement by elected incumbents, not coups.* A non-partisan, mechanism-level finding
  that two literatures converge on: Bermeo (2016, *J. of Democracy* — coups decline, aggrandizement +
  strategic manipulation rise) and Lührmann & Lindberg (2019, *Democratization* — the "third wave" is
  gradual and incumbent-led). Grades the *mechanism* (how erosion happens); the contested *magnitude*
  stays in SAA-028. Ledger now **37 entries** (19 ROBUST / 16 CONTESTED / 1 REFUTED / 1 OPEN).
- **SAA-038** (epistemic-defense, **ROBUST**) — *lateral reading is the expert strategy for evaluating
  online sources, and teaching it improves credibility judgments.* The constructive counterpart to the
  ledger's myth-corrections: Wineburg & McGrew (2019, *Teachers College Record* — fact-checkers read
  laterally and judge accurately; students and even historians read vertically and do worse) and McGrew
  & Breakstone (2023, *AERA Open* — the skill is teachable and lifts judgments vs controls). The
  durability/real-world-transfer edge is held weaker by analogy to SAA-003. The epistemic-defense thesis
  made operational. Ledger now **38 entries** (20 ROBUST / 16 CONTESTED / 1 REFUTED / 1 OPEN).

### Improved — whole-project usability sweep (CLI · docs · site · gates)
A four-dimension improvement sweep (each proposal adversarially filtered before applying) landed 20
changes across the application, docs, and site:
- **`pharos` CLI**: `--grade` now validates against the vocabulary with a proper usage error (a typo
  is no longer indistinguishable from an empty result) and accepts lowercase; a missing/corrupt
  `data/derived` file prints a one-line recovery hint instead of a traceback; `stale --today` gives a
  usage error on a malformed date; `ledger` gains `--json` for scripting, a zero-match hint, and stops
  double-scanning the ledger; `show` accepts a bare number (`pharos show 31`); help texts updated.
- **Docs**: `ledger/README.md`'s hand-kept index had silently drifted to 15 rows at 38 entries — it now
  points to the generated, drift-gated [`INDEX.md`](ledger/INDEX.md) instead of duplicating it, and its
  provenance section is brought current. The main README gains a **"Run it in 30 seconds"** block up
  top. `make` with no target now prints a **help menu** built from the targets' doc-comments.
- **Site**: footer count corrected (said "35-entry" at 38 — a phrasing the figure gate didn't cover;
  **now pinned** so it can't drift again); the simulators card lists all seven mechanisms; the
  screen-reader bar label matches the published 4%; §07 names `./pharos` as the one command; the
  evidence-ledger card mentions the falsification watch; accessibility polish (AA contrast for faint
  text, decorative emoji/section numbers hidden from screen readers).
- **Gates & code**: the threat-model gate now **fails on a vacuous pass** (scanning zero files
  certifies nothing); the "what counts as a ledger entry" scan is single-sourced in
  `ledger_staleness.read_entries` and reused by the digest and the CLI.
`make verify` grew **159 → 166** offline tests (the new behaviors are pinned).

### Added — `CONTRIBUTING.md`, the contributor on-ramp
- A single front door for contributors — and the substrate the maintainer needs to onboard a second
  grader (the standing Tier-0 item). It states the two enforced laws, the **verify-first discipline**
  for evidence entries (web-verify every citation; steelman then break; separate the layers;
  conservative grades; a fireable trigger), and — crucially — the full add-an-entry **count cascade**
  (`index.json` → `make index` → headline counts in README/STATUS/site → `audit_counts --update` →
  the `pharos` tests → `make dashboard`), the non-obvious chain a contributor would otherwise miss and
  the gates would fail on. Plus the commit/identity/licensing conventions and the publication-gate
  note. Linked from the README "Start here" table.

## [0.4.0] — 2026-06-18 — the evidence base, made comprehensive

**The ledger doubles to cover all four lenses, the simulator corpus and forecast pillar fill out,
and every new claim is added under a verify-first discipline that web-confirms each citation.**

### Added
- **Ledger 15 → 35 entries**, via four **verify-first batches** (each grade adversarially checked and
  every citation web-confirmed before writing): **psychology** (SAA-016–021), **sociology**
  (SAA-022–026), **recent-empirical** (SAA-027–030), and **political-economy** (SAA-031–035). With the
  last batch the ledger now covers **all four REPORT lenses** (epistemic defense · social science of
  violence · systems & technology · political economy) plus anthropology. The discipline **excluded a
  2026-retracted paper** (AI-fabricated references) and **corrected four mis-cited references**.
- **Two more validated simulators (4 → 6)**: `sim_complex_contagion` (Centola–Macy — sweeps a clustered
  net, stalls when rewired) and `sim_civil_violence` (Epstein — the legitimacy lever + tipping point;
  the punctuated bursts honestly *not* asserted at this scale).
- **Forecast v1**: a **climatology baseline** (the genuine skill ceiling — nothing beats it) and the
  documented live-forecast protocol (R1/R4: calibration-over-ViEWS, success-on-the-reachable, reflexivity).

### Changed
- `make verify` grew from 66 → **118** offline tests; grades carry honest **layer splits** throughout
  (correlation/measured-trend ROBUST, causal reading CONTESTED).
- The public site refreshed to surface both pillars and the forecast-honesty section.

## [0.3.0] — 2026-06-18 — both pillars + a self-auditing repo

**The forecasting pillar lands, the self-verification's punch-list is worked through, and the
foundation is hardened to free, deterministic, reproducible.**

### Added
- **pharos-forecast v0** — the second pillar, as an honest *calibration layer, not a hero call*:
  a pre-registered backtest over 2,600 probabilistic backsliding forecasts (V-Dem freedom of
  expression, 1990–2024), CRPS + Brier scored against a no-change baseline. Pre-registered bar
  `skill > 0`; the honest, published result is that v0 does **not** beat it.
- **Voice-divergence indicator** — triangulates WGI Voice & Accountability × V-Dem × Freedom House
  and publishes *divergence, not a single score* (45 concur-decline, 5 conflict; a gamed single
  input surfaces as a conflict).
- **`THREAT_MODEL.md`** — turns "watch power, not people" from intent into an enforced
  publish/withhold gate (marginal-value test, DII, spatial floor, forecasts-most-sensitive).
- **`GRADING_PROTOCOL.md` + `ledger_validate.py`** — the grading method out of one head and into
  the repo, machine-enforced.
- **Staleness gate** (`ledger_staleness.py`) — maintainer lapse becomes a loud build failure.
- **Self-auditing**: overstatement audit, doc-count audit, and a `make dashboard` GREEN/RED report.
- **Offline determinism**: pinned input snapshots + `make verify-offline` (no network, byte-stable);
  a shared resilient fetcher with backoff + jitter.
- **Free local CI**: git hooks (`make hooks`) — no cloud, no billing; a stdlib `Dockerfile`.
- **`CHANGELOG.md`** (this file).

### Changed
- **Ledger → v0.2.1**: Tier-2 honesty demotions (SAA-001/008/010) — the oversold headlines from
  the plan-for-peace self-verification demoted to what the evidence carries.
- **WGI indicator**: C9 robustness — the Voice & Accountability decline asymmetry reported at the
  stricter 95% bar (4.67:1).
- `make verify` grew from 11 → **105** offline tests; the gate now runs tests → validate →
  staleness → overstatement → counts → indicators → divergence → forecast.

### Fixed
- A fabricated citation ("Wan/Lazer 2025") caught by the discipline mid-edit and corrected to the
  real arXiv:2411.07907.
- `voice_divergence` fetch retried instantly (no backoff) — consolidated into the shared fetcher.

## [0.2.0] — 2026-06-03 — the evidence commons

### Added
- **Pharos Ledger v0.2** — 15 graded, falsifiable evidence entries (9 ROBUST / 4 CONTESTED /
  1 REFUTED / 1 OPEN), each with a pre-registered falsification trigger.
- **WGI governance indicator** — six dimensions with honest uncertainty (88% within noise; the
  decline concentrated in Voice & Accountability).
- **Four Tier-1 validated simulators** (Granovetter, Watts, committed-minority, reverse-dominance).
- The long-form article *Watch Power, Not People*; the `what-is-tested.md` testability map;
  the Graham Hancock verification (method demonstration).

## [0.1.0] — 2026-06-02 — the question, answered under discipline

### Added
- `REPORT.md` — the verified deep-research synthesis (four lenses; cite-only-what-is-measured)
  and the design of the **Pharos** initiative.
- Project scaffold: multi-licensing (CC BY-SA / GPL-3.0 / CC0), REUSE compliance, the `NOTICE`
  ethical-use covenant.

[0.3.0]: https://github.com/LX8/pharos
[0.2.0]: https://github.com/LX8/pharos
[0.1.0]: https://github.com/LX8/pharos
