# Pharos local observatory — implementation and verification

**2026-09-23.** Pharos now has a working local browser application in addition to
its existing research and command-line tools. Start it with `./pharos serve` and
open <http://127.0.0.1:8796/>. Usage and boundaries are in
[LOCAL_OBSERVATORY.md](LOCAL_OBSERVATORY.md).

## Implementation

`src/pharos_server.py` serves the app in `site/app/`. It reads the existing
`pharos_client` data and shared ledger review rules. The interface adds no new
scientific formulas, scores, grades, forecasts or repinned input data.

Six views provide the overview, searchable evidence ledger, institutional
comparisons, forecast/calibration evaluation, seven mechanism demonstrations, and
actual offline verification. Eight research documents are readable locally.
Exports offer a full contents reader, copy and select-all actions, and a file
download. Execution receipts provide timestamps, actual exit status/output, and
before/after fingerprints of the inputs, code, tests, documents and interface.

The backend binds loopback only, serves a fixed file allowlist, validates Host and
Origin, requires a per-session run token, runs fixed commands without a shell,
permits one active job, bounds run time, and limits returned output. Runs that
fail, time out or see changed source cannot produce a verification pass.

## Verification performed

| Surface | Evidence and outcome |
|---|---|
| Starting research baseline | `make verify-offline`: all 264 original tests and research audits passed before implementation. |
| Expanded suite | 293 tests, including 29 new server/runner/CLI contract tests; the complete offline gate passed through the actual browser Run verification action. |
| Python minimum | All 29 new tests also passed on Python 3.9.6. |
| Real execution | All seven model demos completed together, and every individual model button completed with exit 0 and unchanged input fingerprints. These are execution results, not proofs of social claims. |
| Research fidelity | All 56 pre-existing files under `data/snapshots/`, `data/derived/`, and `ledger/`, plus the founding `REPORT.md` and `THREAT_MODEL.md` (58 files in all), retained their starting SHA-256 hashes at that stage. |
| Evidence UI | All four grade filters; ID search; review-due and overdue filters; clear/reset; no-result states; full entry, falsifier and cited links; native dialog and Escape. |
| Indicator UI | All six agreement categories, country name/code search, missing observations, an explicit dissenting instrument, empty/reset states, source/scale/license disclosure. No combined country risk score. |
| Forecast UI | Both evaluation windows; all six models' calibration bins in each window, with bin counts summing to 2,600 and 522 respectively; negative verdict retained. |
| Source readers | All eight documents opened with real source text. |
| Exports | Both forecast JSONs (2,600/522 forecasts), comparison CSV (203 rows), WGI CSV (1,222 rows), and a real run receipt were inspected in the browser. Copying the complete holdout JSON was independently checked against clipboard contents; Select all selected every character. HTTP tests compare every export byte with its source file. |
| History | Nine completed runs remained visible after reloading the same server session. |
| Failure boundaries | Nonzero exit, timeout, spawn error, changed input, receipt write failure, duplicate active run, invalid commands/payloads, foreign origin, bad/missing token, bad Host, traversal, symlink escape and missing research file are exercised by unit/API tests. |
| UI recovery | A separate local test fixture returned one simulated data-loading error; the app displayed the error and Try again recovered the real research. |
| Layout and keyboard | All six views rendered at an actual 390-pixel frame width with zero document overflow; source dialog fit; keyboard skip link retained the active view; Escape closed the reader. A comparison-table accessibility label overflow found during testing was fixed. |
| Main browser errors | No application console errors or warnings were observed in the main app during the recorded checks. |

Browser verification used an embedded in-app browser. Its outer viewport override
was limited by the host window, so a separate loopback fixture framed the actual
production assets at exactly 390 pixels. Only that fixture allowed same-origin
framing; production retains `frame-ancestors 'none'`. A browser-tool
MutationObserver error appeared during iframe inspection; the visible mobile
checks succeeded, and the app itself contains no MutationObserver code.

Native download completion could not be confirmed in the embedded browser.
The export contents reader and tested copy/select alternatives provide access to
the entire source file there; regular file-download links remain available.
The verification did not open external citation sites or reassess their claims.

## Reproduction and receipts

- `make verify-offline` — full research recomputation, tests and audit gates.
- `python3 -m unittest discover -s tests -p 'test_pharos_server.py' -v` — new local app boundaries.
- `./pharos serve` — run the browser workflow; Run verification creates a real receipt.
- `build/pharos-runs/*.json` — ignored receipts from actual app executions.
- `build/pharos-implementation-2026-09-23/source-before.json` — tracked-file baseline hashes.
- `build/pharos-implementation-2026-09-23/final-verification.json` — final verification receipt copied from the app's run result.
- `build/pharos-implementation-2026-09-23/browser-checks.json` — recorded UI coverage and export observations.

The `build/` receipts are local, git-ignored files; they are not part of the public repository.

No research claim was promoted. Historical indicators remain 2014–2024 with the
2026-06-18 source snapshot; the forecast still fails its joint success bar. Human
review and public-launch gates remain as documented. No repository rename,
publication, live data fetch, commit or push was performed at that stage.
