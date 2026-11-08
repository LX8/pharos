# SPDX-FileCopyrightText: 2026 The Pharos contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Contracts and safety boundaries for the real local observatory (no network data)."""
from datetime import date
import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import pharos_server as app
import pharos_client


class ResearchContractTests(unittest.TestCase):
    def test_browser_reads_existing_research_without_regrading(self):
        state = app.load_state(ROOT)
        self.assertEqual(state["forecast"], pharos_client.forecast(ROOT))
        self.assertEqual(state["divergence"], pharos_client.divergence(ROOT))
        self.assertEqual([(e["id"], e["grade"]) for e in state["ledger"]],
                         [(e["id"], e["grade"]) for e in pharos_client.ledger(ROOT)])
        self.assertTrue(all(e["falsification_trigger"] for e in state["ledger"]))

    def test_review_status_uses_requested_date_not_static_passes(self):
        state = app.load_state(ROOT, date(2100, 1, 1))
        self.assertTrue(all(e["review"]["stale"] for e in state["ledger"]))
        self.assertEqual(state["as_of"], "2100-01-01")

    def test_missing_instruments_remain_missing(self):
        state = app.load_state(ROOT)
        aruba = next(c for c in state["divergence"]["countries"] if c["country"] == "ABW")
        self.assertFalse(aruba["instruments"]["fh"]["available"])
        self.assertNotIn("delta", aruba["instruments"]["fh"])

    def test_all_document_and_download_targets_exist(self):
        for relative in [*app.DOCUMENTS.values(), *app.DOWNLOADS.values(), *app.ASSETS.values()]:
            self.assertTrue(app.safe_file(ROOT, relative).is_file(), relative)

    def test_file_reader_rejects_escape_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (Path(tmp) / "private").write_text("private")
            with self.assertRaises(FileNotFoundError):
                app.safe_file(root, "../private")
            (root / "link").symlink_to(Path(tmp) / "private")
            with self.assertRaises(FileNotFoundError):
                app.safe_file(root, "link")
            (root / "nested").symlink_to(Path(tmp), target_is_directory=True)
            with self.assertRaises(FileNotFoundError):
                app.safe_file(root, "nested/private")


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "input.py").write_text("original")

    def result(self, code=0, timed_out=False):
        return {"exit_code": code, "timed_out": timed_out, "output": "actual output", "output_truncated": False}

    def completed(self, executor, kind="verify"):
        runner = app.Runner(self.root, executor)
        job = runner.start(kind)
        runner.worker.join(5)
        self.assertFalse(runner.worker.is_alive())
        return runner, runner.get(job["id"])

    def test_success_has_real_output_hashes_and_saved_receipt(self):
        _, job = self.completed(lambda *_: self.result())
        self.assertEqual(job["status"], "passed")
        self.assertEqual(job["output"], "actual output")
        self.assertTrue(job["source_unchanged"])
        self.assertIn("src/input.py", job["inputs"]["files"])
        saved = json.loads((self.root / "build/pharos-runs" / (job["id"] + ".json")).read_text())
        self.assertEqual(saved["status"], "passed")
        self.assertTrue(saved["receipt_saved"])
        self.assertEqual(saved["inputs"], job["inputs"])

    def test_nonzero_exit_never_reports_pass(self):
        _, job = self.completed(lambda *_: self.result(7))
        self.assertEqual(job["status"], "failed")
        self.assertEqual(job["exit_code"], 7)

    def test_timeout_has_distinct_outcome(self):
        _, job = self.completed(lambda *_: self.result(-9, True))
        self.assertEqual(job["status"], "timed_out")

    def test_spawn_error_is_visible_and_releases_slot(self):
        def fail(*_):
            raise OSError("executable missing")
        runner, job = self.completed(fail)
        self.assertEqual(job["status"], "error")
        self.assertIn("executable missing", job["output"])
        self.assertIsNone(runner.active)

    def test_changed_input_invalidates_zero_exit_result(self):
        def change(*_):
            (self.root / "src/input.py").write_text("changed")
            return self.result()
        _, job = self.completed(change)
        self.assertEqual(job["status"], "source_changed")
        self.assertFalse(job["source_unchanged"])

    def test_demo_completion_is_not_a_verification_pass(self):
        _, job = self.completed(lambda *_: self.result(), "threshold_cascade")
        self.assertEqual(job["status"], "completed")

    def test_only_one_check_can_run_at_once(self):
        entered, release = threading.Event(), threading.Event()
        def block(*_):
            entered.set()
            release.wait(3)
            return self.result()
        runner = app.Runner(self.root, block)
        runner.start("verify")
        try:
            self.assertTrue(entered.wait(2))
            with self.assertRaises(app.BusyError):
                runner.start("simulations")
        finally:
            release.set()
            runner.worker.join(4)
        self.assertIsNone(runner.active)

    def test_arbitrary_commands_are_rejected(self):
        runner = app.Runner(self.root)
        for command in ("shell", "verify; touch owned", "../../script"):
            with self.assertRaises(ValueError):
                runner.start(command)
        self.assertFalse((self.root / "owned").exists())

    def test_real_executor_captures_exit_and_output(self):
        result = app.execute((sys.executable, "-c", "import sys; print('evidence'); sys.exit(3)"), self.root, 3)
        self.assertEqual(result["exit_code"], 3)
        self.assertIn("evidence", result["output"])
        self.assertFalse(result["timed_out"])

    def test_real_executor_stops_a_timed_out_process(self):
        result = app.execute((sys.executable, "-c", "import time; time.sleep(30)"), self.root, .1)
        self.assertTrue(result["timed_out"])
        self.assertNotEqual(result["exit_code"], 0)

    def test_real_executor_bounds_returned_output(self):
        result = app.execute((sys.executable, "-c", "print('x' * 210000)"), self.root, 3)
        self.assertTrue(result["output_truncated"])
        self.assertLessEqual(len(result["output"]), 200000)

    def test_receipt_write_failure_is_reported(self):
        (self.root / "build").write_text("not a directory")
        _, job = self.completed(lambda *_: self.result())
        self.assertFalse(job["receipt_saved"])
        self.assertIn("Could not save", job["receipt_warning"])


class HTTPContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = unittest.mock.Mock()
        cls.runner.list.return_value = []
        cls.runner.get.side_effect = KeyError
        cls.runner.start.return_value = {"id": "test", "status": "running"}
        cls.server = app.ObservatoryServer(0, ROOT, cls.runner)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path, method="GET", body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=4)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        data = response.read()
        result = response.status, dict(response.getheaders()), data
        connection.close()
        return result

    def authorization(self):
        return {"Origin": f"http://127.0.0.1:{self.server.server_port}",
                "X-Pharos-Token": self.server.token, "Content-Type": "application/json"}

    def test_real_state_endpoint_preserves_source_data(self):
        status, headers, raw = self.request("/api/state")
        self.assertEqual(status, 200)
        data = json.loads(raw)
        self.assertEqual(data["forecast"], pharos_client.forecast(ROOT))
        self.assertEqual(data["run_token"], self.server.token)
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_only_selected_files_are_served(self):
        for path in ("/.git/config", "/README.md", "/../REPORT.md", "/%2e%2e/REPORT.md", "/src/pharos.py", "/api/document/../../REPORT.md"):
            self.assertEqual(self.request(path)[0], 404, path)
        for path in app.ASSETS:
            status, headers, _ = self.request(path)
            self.assertEqual(status, 200)
            self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])

    def test_bad_host_and_foreign_origin_cannot_run_checks(self):
        self.assertEqual(self.request("/api/state", headers={"Host": "evil.example"})[0], 403)
        headers = self.authorization()
        headers["Origin"] = "https://evil.example"
        self.assertEqual(self.request("/api/jobs", "POST", '{"kind":"verify"}', headers)[0], 403)

    def test_token_is_required_even_for_local_origin(self):
        headers = self.authorization()
        del headers["X-Pharos-Token"]
        self.assertEqual(self.request("/api/jobs", "POST", '{"kind":"verify"}', headers)[0], 403)
        headers["X-Pharos-Token"] = "é"
        self.assertEqual(self.request("/api/jobs", "POST", '{"kind":"verify"}', headers)[0], 403)

    def test_valid_request_starts_real_runner_contract(self):
        status, _, body = self.request("/api/jobs", "POST", '{"kind":"verify"}', self.authorization())
        self.assertEqual(status, 202)
        self.assertEqual(json.loads(body)["status"], "running")
        self.runner.start.assert_called_with("verify")

    def test_busy_runner_returns_conflict(self):
        with patch.object(self.runner, "start", side_effect=app.BusyError("already running")):
            status, _, body = self.request("/api/jobs", "POST", '{"kind":"verify"}', self.authorization())
        self.assertEqual(status, 409)
        self.assertIn("already running", json.loads(body)["error"])

    def test_invalid_payloads_and_commands_are_rejected(self):
        for body in ('[]', 'null', '{"kind":[]}', '{"kind":"verify","argv":"unsafe"}', '{broken', 'x'*1025):
            self.assertEqual(self.request("/api/jobs", "POST", body, self.authorization())[0], 400)
        with patch.object(self.runner, "start", side_effect=ValueError("unknown check")):
            self.assertEqual(self.request("/api/jobs", "POST", '{"kind":"unknown"}', self.authorization())[0], 400)

    def test_unknown_entries_and_runs_are_not_found(self):
        for path in ("/api/entry/SAA-999", "/api/jobs/missing", "/api/document/missing"):
            self.assertEqual(self.request(path)[0], 404)

    def test_documents_and_exports_match_exact_files(self):
        for key, relative in app.DOCUMENTS.items():
            status, _, raw = self.request("/api/document/" + key)
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(raw)["text"], (ROOT / relative).read_text())
        for name, relative in app.DOWNLOADS.items():
            status, headers, data = self.request("/downloads/" + name)
            self.assertEqual(status, 200)
            self.assertEqual(data, (ROOT / relative).read_bytes())
            self.assertIn(name, headers["Content-Disposition"])

    def test_missing_research_file_returns_actionable_error(self):
        with patch.object(app, "load_state", side_effect=FileNotFoundError("private path")):
            status, _, raw = self.request("/api/state")
        self.assertEqual(status, 503)
        self.assertIn("local checkout", json.loads(raw)["error"])
        self.assertNotIn("private path", raw.decode())

    def test_cli_rejects_invalid_ports(self):
        import argparse
        import pharos
        for value in ("-1", "0", "65536"):
            with self.assertRaises(argparse.ArgumentTypeError):
                pharos._port_arg(value)

    def test_cli_exposes_local_server(self):
        import pharos
        with patch.object(app, "serve", return_value=0) as serve:
            self.assertEqual(pharos.main(["serve", "--port", "9999"]), 0)
        serve.assert_called_once_with(9999)


if __name__ == "__main__":
    unittest.main()
