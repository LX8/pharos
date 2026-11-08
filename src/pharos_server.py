# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Loopback-only Pharos observatory. Reads the existing research; runs fixed offline checks."""
from __future__ import annotations

import copy
from datetime import date, datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import tempfile
import threading
from urllib.parse import urlsplit

import pharos_client
from ledger_staleness import entry_status, parse_frontmatter

ROOT = Path(__file__).resolve().parent.parent
ASSETS = {"/": "site/app/index.html", "/app.js": "site/app/app.js", "/style.css": "site/app/style.css"}
DOCUMENTS = {
    "brief": "docs/BRIEF.md", "report": "docs/WATCH_REPORT.md",
    "study": "REPORT.md", "grading": "docs/GRADING_PROTOCOL.md",
    "threat-model": "THREAT_MODEL.md", "forecast-method": "docs/forecast/pharos-forecast-v0.md",
    "testing": "docs/what-is-tested.md", "local-app": "docs/LOCAL_OBSERVATORY.md",
}
DOWNLOADS = {
    "governance.csv": "data/derived/wgi_governance.csv",
    "divergence.csv": "data/derived/voice_divergence.csv",
    "forecast.json": "data/derived/forecast_backtest.json",
    "holdout.json": "data/derived/oos_holdout.json",
}
SIMULATIONS = (
    ("threshold_cascade", "Threshold cascades", "Granovetter · 1978", "Small threshold changes, different model outcomes."),
    ("network_cascade", "Network cascades", "Watts · 2002", "A cascade window in a synthetic random network."),
    ("committed_minority", "Committed minorities", "Xie et al. · 2011", "Consensus dynamics under the naming game's assumptions."),
    ("reverse_dominance", "Reverse dominance", "Lanchester square law · Johnson & MacKay, 2015", "An exact model threshold; the social interpretation remains contested."),
    ("complex_contagion", "Complex contagion", "Centola & Macy · 2007", "Repeated exposure in clustered and rewired networks."),
    ("civil_violence", "Civil violence", "Epstein · 2002", "Aggregate behavior in an artificial agent population."),
    ("opinion_dynamics", "Bounded confidence", "Deffuant–Weisbuch model", "Agreement and fragmentation in simulated opinions."),
)
JOBS = {"verify": (("make", "verify-offline"), 300), "simulations": (("make", "sims"), 300)}
JOBS.update({name: ((sys.executable, "src/sims/sim_" + name + ".py"), 120)
             for name, *_ in SIMULATIONS})


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def safe_file(root, relative):
    root = Path(root).resolve()
    path = root / relative
    if path.is_symlink() or root not in path.resolve().parents or not path.is_file():
        raise FileNotFoundError(relative)
    # Reject parent symlinks too: a public route must not escape its designated subtree.
    if any(parent.is_symlink() for parent in path.parents if parent != root and root in parent.parents):
        raise FileNotFoundError(relative)
    return path


def read_json(root, relative):
    return json.loads(safe_file(root, relative).read_text(encoding="utf-8"))


def source_manifest(root):
    """Fingerprint research, code, tests and interface; never include generated run receipts."""
    root = Path(root)
    paths = [p for p in root.iterdir() if p.is_file() and not p.name.startswith(".")]
    for folder in ("src", "tests", "data", "ledger", "docs", "site"):
        paths.extend(p for p in (root / folder).rglob("*")
                     if p.is_file() and not p.is_symlink()
                     and not any(part in {"__pycache__", "raw", "cache"} for part in p.relative_to(root).parts))
    files = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return {"sha256": digest, "files": files}


def load_state(root=ROOT, today=None):
    today = today or date.today()
    entries = []
    for row in pharos_client.ledger(root):
        text = safe_file(root, "ledger/" + row["file"]).read_text(encoding="utf-8")
        meta = parse_frontmatter(text)
        review = entry_status(meta, today)
        review = {key: value.isoformat() if isinstance(value, date) else value for key, value in review.items()}
        entries.append({**row, "falsification_trigger": meta.get("falsification_trigger", ""), "review": review})
    return {
        "name": "Pharos", "project": "Science Against Authoritarianism", "as_of": today.isoformat(),
        "ledger": entries, "governance": pharos_client.governance(root),
        "divergence": pharos_client.divergence(root), "forecast": pharos_client.forecast(root),
        "holdout": read_json(root, "data/derived/oos_holdout.json"),
        "simulations": [{"id": i, "name": n, "reference": r, "description": d} for i, n, r, d in SIMULATIONS],
        "documents": list(DOCUMENTS),
    }


def execute(argv, root, timeout):
    """No shell, no supplied arguments; kill the whole process group on a timeout."""
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(argv, cwd=root, stdin=subprocess.DEVNULL,
                                   stdout=output, stderr=subprocess.STDOUT, start_new_session=True,
                                   env={**os.environ, "SAA_OFFLINE": "1", "PYTHONDONTWRITEBYTECODE": "1"})
        timed_out = False
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        size = output.tell()
        output.seek(max(0, size - 200_000))
        text = output.read().decode("utf-8", errors="replace")
        return {"exit_code": process.returncode, "timed_out": timed_out,
                "output": text, "output_truncated": size > 200_000}


class BusyError(Exception):
    pass


class Runner:
    def __init__(self, root=ROOT, executor=execute):
        self.root, self.executor = Path(root), executor
        self.lock = threading.Lock()
        self.jobs = {}
        self.active = None
        self.worker = None

    def list(self):
        with self.lock:
            return copy.deepcopy(list(self.jobs.values())[::-1])

    def get(self, job_id):
        with self.lock:
            return copy.deepcopy(self.jobs[job_id])

    def start(self, kind):
        if kind not in JOBS:
            raise ValueError("Unknown check. Choose a listed Pharos check.")
        with self.lock:
            if self.active:
                raise BusyError("A check is already running. Wait for its result.")
            job_id = secrets.token_hex(12)
            job = {"id": job_id, "kind": kind, "status": "running", "started_utc": utc_now(),
                   "finished_utc": None, "exit_code": None, "output": "", "source_unchanged": None}
            self.jobs[job_id] = job
            while len(self.jobs) > 50:
                del self.jobs[next(iter(self.jobs))]
            self.active = job_id
            self.worker = threading.Thread(target=self._run, args=(job_id,), daemon=True)
            self.worker.start()
            return copy.deepcopy(job)

    def _run(self, job_id):
        job = self.get(job_id)
        try:
            before = source_manifest(self.root)
            argv, timeout = JOBS[job["kind"]]
            result = self.executor(argv, self.root, timeout)
            after = source_manifest(self.root)
            unchanged = before == after
            status = ("timed_out" if result["timed_out"] else "failed" if result["exit_code"] != 0
                      else "source_changed" if not unchanged else "passed" if job["kind"] == "verify" else "completed")
            job.update(result, status=status, source_unchanged=unchanged, inputs=before,
                       final_source_sha256=after["sha256"])
        except Exception as exc:
            job.update(status="error", output=f"{type(exc).__name__}: {exc}")
        job["finished_utc"] = utc_now()
        try:
            directory = self.root / "build" / "pharos-runs"
            directory.mkdir(parents=True, exist_ok=True)
            job["receipt_saved"] = True
            (directory / (job_id + ".json")).write_text(json.dumps(job, indent=2) + "\n", encoding="utf-8")
        except OSError:
            job["receipt_saved"] = False
            job["receipt_warning"] = "Could not save a receipt to disk. Download this session's result."
        with self.lock:
            self.jobs[job_id] = job
            self.active = None


class ObservatoryServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=8796, root=ROOT, runner=None):
        self.root = Path(root).resolve()
        self.runner = runner or Runner(self.root)
        self.token = secrets.token_urlsafe(32)
        super().__init__(("127.0.0.1", port), Handler)


class Handler(BaseHTTPRequestHandler):
    server_version = "PharosLocal/1"

    def log_message(self, *_args):
        pass

    def reply(self, status, body, content_type="application/json; charset=utf-8", filename=None):
        data = json.dumps(body).encode() if isinstance(body, (dict, list)) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(data)

    def permitted_host(self):
        port = self.server.server_port
        return self.headers.get("Host") in (f"127.0.0.1:{port}", f"localhost:{port}")

    def do_GET(self):
        if not self.permitted_host():
            return self.reply(403, {"error": "Use this app's local address."})
        path = urlsplit(self.path).path
        try:
            if path in ASSETS:
                mime = "text/html" if path == "/" else "text/javascript" if path.endswith(".js") else "text/css"
                return self.reply(200, safe_file(self.server.root, ASSETS[path]).read_bytes(), mime + "; charset=utf-8")
            if path == "/api/state":
                return self.reply(200, {**load_state(self.server.root), "run_token": self.server.token})
            if path.startswith("/api/entry/"):
                entry_id = path.removeprefix("/api/entry/")
                entry = next(e for e in pharos_client.ledger(self.server.root) if e["id"] == entry_id)
                return self.reply(200, {"text": safe_file(self.server.root, "ledger/" + entry["file"]).read_text(encoding="utf-8")})
            if path.startswith("/api/document/"):
                relative = DOCUMENTS[path.removeprefix("/api/document/")]
                return self.reply(200, {"text": safe_file(self.server.root, relative).read_text(encoding="utf-8")})
            if path == "/api/jobs":
                return self.reply(200, self.server.runner.list())
            if path.startswith("/api/jobs/"):
                return self.reply(200, self.server.runner.get(path.removeprefix("/api/jobs/")))
            if path.startswith("/downloads/"):
                name = path.removeprefix("/downloads/")
                return self.reply(200, safe_file(self.server.root, DOWNLOADS[name]).read_bytes(),
                                  "text/csv; charset=utf-8" if name.endswith(".csv") else "application/json", name)
            return self.reply(404, {"error": "Page not found."})
        except (KeyError, StopIteration):
            return self.reply(404, {"error": "Item not found."})
        except (OSError, ValueError, TypeError):
            return self.reply(503, {"error": "A research file could not be loaded. Check the local checkout, then retry."})

    def do_POST(self):
        expected_origin = "http://" + self.headers.get("Host", "")
        if (not self.permitted_host() or self.headers.get("Origin") != expected_origin
                or not secrets.compare_digest(self.headers.get("X-Pharos-Token", "").encode(), self.server.token.encode())):
            return self.reply(403, {"error": "Run checks from the local Pharos app."})
        if self.path != "/api/jobs":
            return self.reply(404, {"error": "Page not found."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if (not 0 < length <= 1024 or self.headers.get("Transfer-Encoding")
                    or self.headers.get_content_type() != "application/json"):
                raise ValueError("Send a small JSON check request.")
            self.connection.settimeout(5)
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict) or set(data) != {"kind"} or not isinstance(data["kind"], str):
                raise ValueError("Choose one listed check.")
            return self.reply(202, self.server.runner.start(data["kind"]))
        except BusyError as exc:
            return self.reply(409, {"error": str(exc)})
        except (ValueError, OSError) as exc:
            return self.reply(400, {"error": str(exc)})


def serve(port=8796):
    try:
        with ObservatoryServer(port) as server:
            print(f"Pharos local observatory: http://127.0.0.1:{server.server_port}/", flush=True)
            print("Historical research data. Local checks only. Press Ctrl+C to stop.", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            # A started check owns its receipt; give it its bounded time to finish on clean shutdown.
            if server.runner.worker:
                server.runner.worker.join()
        return 0
    except OSError as exc:
        print(f"Pharos could not start: {exc}. Try another --port.", file=sys.stderr)
        return 1
