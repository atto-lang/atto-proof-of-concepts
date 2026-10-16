"""Pattern-runner contract tests. No Oreslang backend is executed."""
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock
import run_examples

CASE = run_examples.PATTERNS / "01-factory-method"
FAKE = [(1, CASE, CASE / "example.ores", "PASS:1\n")]
COMMAND = "python3 fake.py {source}"

def check_run(args, result):
    stdout = io.StringIO()
    with mock.patch.object(run_examples, "discover", return_value=FAKE):
        with mock.patch.object(sys, "argv", ["run_examples.py", *args]):
            with mock.patch.object(run_examples.subprocess, "run", return_value=result) as runner:
                with contextlib.redirect_stdout(stdout):
                    exit_code = run_examples.main()
    return exit_code, stdout.getvalue(), runner.call_count

class RunnerContractTests(unittest.TestCase):
    def test_all_pattern_files_have_oracles(self):
        patterns = run_examples.discover()
        self.assertGreaterEqual(len(patterns), 78)
        self.assertEqual([n for n, _, _, _ in patterns], list(range(1, len(patterns) + 1)))

    def test_exact_runtime_output_required(self):
        good = subprocess.CompletedProcess([], 0, "PASS:1\n", "")
        wrong = subprocess.CompletedProcess([], 0, "PASS:2\n", "")
        self.assertEqual(check_run(["--runner-command", COMMAND], good)[0], 0)
        self.assertEqual(check_run(["--runner-command", COMMAND], wrong)[0], 1)

    def test_nonzero_exit_never_passes(self):
        failed = subprocess.CompletedProcess([], 2, "PASS:1\n", "compiler failed")
        self.assertEqual(check_run(["--runner-command", COMMAND], failed)[0], 1)

    def test_compile_only_does_not_require_runtime_stdout(self):
        compile_ok = subprocess.CompletedProcess([], 0, "", "")
        self.assertEqual(check_run(["--runner-command", COMMAND, "--mode", "compile"], compile_ok)[0], 0)
        self.assertEqual(check_run(["--runner-command", COMMAND, "--mode", "run"], compile_ok)[0], 1)

    def test_require_revision_rejects_unpinned_metadata(self):
        fake = subprocess.CompletedProcess([], 0, "PASS:1\n", "")
        for revision in ("unknown", "a" * 39, "g" * 40):
            code, _, calls = check_run(
                ["--runner-command", COMMAND, "--require-revision",
                 "--compiler-revision", revision], fake)
            self.assertEqual((code, calls), (2, 0))
        code, _, calls = check_run(
            ["--runner-command", COMMAND, "--require-revision",
             "--compiler-revision", "a" * 40], fake)
        self.assertEqual((code, calls), (0, 1))

    def test_malformed_filter_fails_closed(self):
        code, output, calls = check_run(["--filter", "[", "--runner-command", COMMAND], None)
        self.assertEqual(code, 2)
        self.assertEqual(calls, 0)

    def test_default_without_runner_fails_closed(self):
        code, _, calls = check_run([], None)
        self.assertEqual((code, calls), (2, 0))

    def test_list_with_runner_is_rejected(self):
        code, _, calls = check_run(["--list", "--runner-command", COMMAND], None)
        self.assertEqual((code, calls), (2, 0))

    def test_nonfinite_timeout_is_rejected(self):
        for value in ("0", "-1", "nan", "inf", "-inf"):
            code, _, calls = check_run(
                ["--runner-command", COMMAND, "--timeout=" + value], None)
            self.assertEqual((code, calls), (2, 0), value)

    def test_report_records_fixture_hashes(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            report_path = Path(folder) / "evidence.json"
            good = subprocess.CompletedProcess([], 0, "PASS:1\n", "")
            code, _, calls = check_run(
                ["--runner-command", COMMAND, "--report", str(report_path)], good)
            self.assertEqual((code, calls), (0, 1))
            report = json.loads(report_path.read_text())
            self.assertEqual(report["inventory_total"], 1)
            self.assertFalse(report["complete_catalog"])
            self.assertIn("caller-supplied", report["provenance"])
            self.assertEqual(len(report["results"][0]["source_sha256"]), 64)
            self.assertTrue(report["results"][0]["inputs_unchanged"])

    def test_list_does_not_run_compiler(self):
        code, output, calls = check_run(["--list"], None)
        self.assertEqual(code, 0)
        self.assertEqual(calls, 0)
        self.assertIn("UNVERIFIED", output)

if __name__ == "__main__":
    unittest.main()
