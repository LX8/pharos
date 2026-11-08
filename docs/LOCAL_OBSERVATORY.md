# Pharos local observatory

Pharos is the observatory within **Science Against Authoritarianism**. The local app
uses that name consistently while retaining the repository and research identity.

From the repository root, run `./pharos serve`, then open
<http://127.0.0.1:8796/>. Python 3.9+ is sufficient: no package installation, account,
cloud service, or frontend build. Running the verification also needs `make`, `git` and a git
clone (not a ZIP download). `./pharos serve --port 8800` selects another local
port. Stop with Ctrl+C; a check already running is allowed its bounded time to finish.
The app is private and local. This does not deploy the separate landing page.

## What works

- **Overview:** live reads of the committed evidence counts, historical coverage,
  measurement floor, negative forecast result, and eight source documents.
- **Evidence ledger:** search by title/domain/ID, filter by grade and review status,
  read the full entry, open its citations, and inspect its falsification trigger.
  Grades remain ROBUST / CONTESTED / REFUTED / OPEN.
- **Institutional signals:** search countries or territories, filter agreement,
  inspect three separate instruments with their scales and flag rules. Missing
  observations remain unavailable. Both improvements and declines are visible.
  Inspect, download or copy the exact committed comparison and WGI CSVs.
- **Forecast evaluation:** switch between the original backtest and the held-out
  evaluation; inspect every model's CRPS, Brier, skill and calibration bins; download
  either source JSON (with inspect and copy alternatives). No model result or scientific conclusion is improved by the UI.
- **Mechanism lab:** execute the seven existing fixed-input demonstrations, one at a
  time or together. These are synthetic educational models, not operational forecasts.
- **Verification:** actually execute `make verify-offline`: recompute from pinned
  inputs, compare derived data with Git, run the unit tests, the seven-audit components,
  and generated-report freshness checks. No network refresh or repinning is invoked.

Historical indicators compare 2014–2024. The source snapshot was fetched on
2026-06-18. Review age is evaluated from the local date. Reopening the app does not
change source dates or manufacture new verification results.

## Receipts and limits

Each run has actual start/end times, exit status, bounded output, before/after source
fingerprints and a file-hash manifest. A nonzero exit, timeout, execution error, or
changed source cannot display as a verification pass. A simulation's zero exit says
**completed**, not that the underlying social claim is proven. Evidence grades are
unchanged by software tests.

Receipts are saved to ignored `build/pharos-runs/`. The browser lists up to 50 runs in
the current server session and can inspect, download or copy them. Restarting clears that session list;
saved JSON receipts remain on disk. Source fingerprints cover root project files and
`src`, `tests`, `data` (excluding raw/cache), `ledger`, `docs`, and `site`; generated run
receipts and Python bytecode are excluded. A digest is a local reproducibility aid,
not an independent attestation or a cryptographic signature.

The backend serves only selected app assets, research documents and exports. It binds
127.0.0.1, validates the Host and Origin, and requires a per-session token for runs.
There is one active run at a time, with fixed commands and bounded execution times;
no shell, user-supplied arguments, live data fetches or arbitrary file browser are
exposed. It is a trusted-local-checkout tool, not a hardened multi-user server.

The browser displays missing-data and request failures explicitly, supports keyboard
navigation, native reader dialogs and narrow screens, and loads no remote fonts,
analytics or scripts. HTTP and runner boundaries are covered by
`tests/test_pharos_server.py`; browser controls are exercised separately in the dated
implementation verification record. The existing unit suite tests the model behavior;
it cannot establish real-world causality, forecast usefulness or publication readiness.

The public-launch gate, independent second-grader work and human threat review remain
as documented in `STATUS.md` and `THREAT_MODEL.md`. This app does not mark them complete.

Implementation evidence and browser coverage: [2026-09-23 verification record](PHAROS_IMPLEMENTATION_2026-09-23.md).
