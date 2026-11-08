# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Local gate for the Pharos quantitative pillar. Stdlib only — no pip install.
.PHONY: help test indicators divergence forecast sims validate staleness overstatement counts threat-model index brief watch-report pages bias-pack pharos drift dashboard hooks snapshot verify-offline verify score cycle

.DEFAULT_GOAL := help

help:        ## show this menu (every target with its one-line description)
	@grep -hE '^[a-zA-Z0-9_.-]+:.*## ' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN{FS=":.*## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

test:        ## run offline unit tests (calculations + simulator validation + ledger gates)
	python3 -m unittest discover -s tests -p "test_*.py" -v

indicators:  ## fetch WGI (6 dimensions) + (re)compute the open indicators with uncertainty (LIVE)
	python3 src/indicators/wgi_governance.py

divergence:  ## triangulate WGI V&A × V-Dem × Freedom House — publish divergence, not a single score (LIVE)
	python3 src/indicators/voice_divergence.py

forecast:    ## pharos-forecast v0 — pre-registered backsliding backtest, CRPS/Brier vs a no-change baseline (LIVE)
	python3 src/forecast/pharos_forecast.py

score:       ## score the frozen forward forecasts against the newest V-Dem release (LIVE); pins the data used, appends to data/derived/prediction_registry_scores.json
	python3 src/forecast/prediction_registry.py --score --live

cycle:       ## the monthly routine in one command: upstream drift recon, forward score (LIVE), then the offline dashboard
	-python3 src/drift_check.py --warn
	$(MAKE) score
	$(MAKE) dashboard

drift:       ## recon: has upstream data moved since the pin? recompute LIVE, diff vs pin, restore (adopts nothing)
	python3 src/drift_check.py

snapshot:    ## refresh the pinned inputs from live sources, then regenerate derived offline (the deliberate pin step)
	python3 src/indicators/wgi_governance.py --snapshot
	python3 src/indicators/voice_divergence.py --snapshot
	SAA_OFFLINE=1 python3 src/indicators/wgi_governance.py
	SAA_OFFLINE=1 python3 src/indicators/voice_divergence.py
	@echo "snapshot: refreshed — review 'git diff', then commit data/snapshots + data/derived"

verify-offline: ## deterministic gate, NO network — recompute from pinned snapshots; must match committed derived
	SAA_OFFLINE=1 python3 src/indicators/wgi_governance.py
	SAA_OFFLINE=1 python3 src/indicators/voice_divergence.py
	SAA_OFFLINE=1 python3 src/forecast/pharos_forecast.py
	@git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "verify-offline: not a git checkout — clone the repository (git clone https://github.com/LX8/pharos); the drift step needs git"; exit 2; }
	@git diff --quiet -- data/derived || { echo "DRIFT: offline recompute changed data/derived — run 'make snapshot' and commit"; git --no-pager diff --stat -- data/derived; exit 1; }
	python3 -m unittest discover -s tests -p "test_*.py"
	python3 src/ledger_validate.py
	python3 src/ledger_staleness.py
	python3 src/audit_overstatement.py
	python3 src/audit_counts.py
	python3 src/audit_threat_model.py
	python3 src/ledger_digest.py
	@# generated-doc freshness: the brief + watch-report must agree with the committed
	@# derived data (no-args = verify, exit 1 on drift). Closes the gap where a contributor
	@# could regenerate data/derived and commit stale BRIEF/WATCH_REPORT alongside it.
	python3 src/brief.py
	python3 src/watch_report.py
	@# the landing pages (all four languages) must equal a fresh build from template + strings + data
	python3 src/build_site.py
	@echo "verify-offline: ok"

sims:        ## run the Tier-1 validated mechanism simulators (demos)
	python3 src/sims/sim_threshold_cascade.py
	python3 src/sims/sim_network_cascade.py
	python3 src/sims/sim_committed_minority.py
	python3 src/sims/sim_reverse_dominance.py
	python3 src/sims/sim_complex_contagion.py
	python3 src/sims/sim_civil_violence.py
	python3 src/sims/sim_opinion_dynamics.py

validate:    ## structural gate: every ledger entry conforms to the grading protocol + agrees with index.json
	python3 src/ledger_validate.py

staleness:   ## freshness gate: fail if any ledger entry is past its review interval (is the light lit, or stale?)
	python3 src/ledger_staleness.py

overstatement: ## honesty gate: fail if graded prose makes an unconditional claim the evidence can't carry
	python3 src/audit_overstatement.py

counts:      ## consistency gate: fail if headline counts (entries/grades/tests) OR the site's computed figures drift from the data
	python3 src/audit_counts.py

threat-model: ## covenant gate: fail if any published data file drops below country/institution level (watch power, not people)
	python3 src/audit_threat_model.py

index:       ## (re)generate the human ledger index + falsification watch (ledger/INDEX.md) from the entries
	python3 src/ledger_digest.py --write

brief:       ## (re)generate the plain-language brief (docs/BRIEF.md) from the committed derived data
	python3 src/brief.py --write

watch-report: ## (re)generate the flagship watch-report prototype (docs/WATCH_REPORT.md)
	python3 src/watch_report.py --write

pages:       ## (re)generate the landing page in all four languages (site/index.html + site/{es,de,pt}/index.html) from site/template.html + site/i18n/
	python3 src/build_site.py --write

bias-pack:   ## generate the blind coding pack for the bias self-audit into build/bias-audit/ (founder-gated run)
	python3 src/bias_audit.py --pack build/bias-audit

pharos:      ## the project as one command — e.g. `make pharos ARGS="ledger --grade ROBUST"` or `./pharos watch`
	python3 src/pharos.py $(ARGS)

dashboard:   ## one GREEN/RED report across every offline audit (tests + structure + freshness + honesty + counts)
	python3 src/audit_dashboard.py

hooks:       ## install the FREE local git hooks (pre-commit -> dashboard, pre-push -> verify-offline). No cloud, no billing.
	git config core.hooksPath .githooks
	@echo "hooks: installed — pre-commit runs 'make dashboard', pre-push runs 'make verify-offline' (bypass with --no-verify)"

verify: test validate staleness overstatement counts threat-model indicators divergence forecast  ## the gate: tests + structure + freshness + honesty + counts + covenant, then recompute (LIVE)
	@echo "verify: ok"
