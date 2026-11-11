"""Pattern-runner contract tests. No Oreslang backend is executed."""
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import run_examples

CASE = run_examples.PATTERNS / "01-factory-method"
FAKE = [(1, CASE, CASE / "example.atto", "PASS:1\n")]
COMMAND = "python3 fake.py {source}"

def check_run(args, result, fixtures=None):
    stdout = io.StringIO()
    with mock.patch.object(run_examples, "discover", return_value=FAKE if fixtures is None else fixtures):
        with mock.patch.object(sys, "argv", ["run_examples.py", *args]):
            fake = None if result is None else (
                result.returncode, result.stdout.encode("utf-8"),
                result.stderr.encode("utf-8"), False)
            with mock.patch.object(run_examples, "bounded_run", return_value=fake) as runner:
                with contextlib.redirect_stdout(stdout):
                    exit_code = run_examples.main()
    return exit_code, stdout.getvalue(), runner.call_count

class RunnerContractTests(unittest.TestCase):
    def test_all_pattern_files_have_oracles(self):
        patterns = run_examples.discover()
        self.assertGreaterEqual(len(patterns), 70)
        self.assertEqual([n for n, _, _, _ in patterns], list(range(1, len(patterns) + 1)))

    def test_symlinked_source_or_oracle_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "outside.atto"
            target.write_text('pub routine main(): void { return; }')
            case = root / "01-symlink"
            case.mkdir()
            oracle = case / "expected.stdout"
            oracle.write_text("PASS:1\\n")
            (case / "example.atto").symlink_to(target)
            with mock.patch.object(run_examples, "PATTERNS", root):
                with self.assertRaisesRegex(ValueError, "symlinks"):
                    run_examples.discover()
            (case / "example.atto").unlink()
            (case / "example.atto").write_text('pub routine main(): void { return; }')
            oracle.unlink()
            oracle.symlink_to(target)
            with mock.patch.object(run_examples, "PATTERNS", root):
                with self.assertRaisesRegex(ValueError, "symlinks"):
                    run_examples.discover()

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
                ["--runner-command", COMMAND, "--filter", "^01-", "--report", str(report_path)], good,
                fixtures=FAKE + [(2, CASE.with_name("02-abstract-factory"),
                                  CASE.with_name("02-abstract-factory") / "example.atto", "PASS:2\n")])
            self.assertEqual((code, calls), (0, 1))
            report = json.loads(report_path.read_text())
            self.assertEqual(report["inventory_total"], 2)
            self.assertEqual(report["selected"], 1)
            self.assertFalse(report["complete_catalog"])
            self.assertIn("caller-supplied", report["provenance"])
            self.assertEqual(len(report["results"][0]["source_sha256"]), 64)
            self.assertTrue(report["results"][0]["inputs_unchanged"])

    def test_evidence_does_not_store_raw_runner_credentials(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            report = Path(folder) / "receipt.json"
            private_command = "python3 fake.py --token=PRIVATE_SENTINEL {source}"
            result = subprocess.CompletedProcess([], 0, "PASS:1\n", "")
            self.assertEqual(check_run(
                ["--runner-command", private_command, "--report", str(report)], result)[0], 0)
            content = report.read_text()
            self.assertNotIn("PRIVATE_SENTINEL", content)
            self.assertEqual(len(json.loads(content)["runner_command_sha256"]), 64)

    def test_stderr_is_rejected_by_default(self):
        noisy = subprocess.CompletedProcess([], 0, "PASS:1\n", "diagnostic")
        self.assertEqual(check_run(["--runner-command", COMMAND], noisy)[0], 1)
        self.assertEqual(check_run(["--runner-command", COMMAND, "--allow-stderr"], noisy)[0], 0)
        self.assertEqual(check_run(["--runner-command", COMMAND, "--mode", "compile"], noisy)[0], 0)

    def test_live_output_limit_failure_is_not_a_pass(self):
        with mock.patch.object(run_examples, "discover", return_value=FAKE):
            with mock.patch.object(sys, "argv", ["run_examples.py", "--runner-command", COMMAND]):
                with mock.patch.object(run_examples, "bounded_run",
                                       return_value=(0, b"PASS:1\n", b"", True)):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(run_examples.main(), 1)
        for value in ("0", "-1", "16777217"):
            self.assertEqual(check_run(["--runner-command", COMMAND,
                                        "--max-output-bytes", value], None)[0], 2)

    def test_filtered_run_rejects_unselected_fixture_mutation(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cases = []
            for n in (1, 2):
                d = root / f"{n:02d}-case"
                d.mkdir()
                source = d / "example.atto"
                source.write_text("example", encoding="utf-8")
                (d / "expected.stdout").write_text(f"PASS:{n}\n", encoding="utf-8")
                cases.append((n, d, source, f"PASS:{n}\n"))
            report = root / "evidence.json"
            def mutate(_argv, _cwd, _timeout, _max_bytes):
                cases[1][2].write_text("tampered", encoding="utf-8")
                return (0, b"PASS:1\n", b"", False)
            with mock.patch.object(run_examples, "discover", return_value=cases):
                with mock.patch.object(run_examples, "bounded_run", side_effect=mutate) as runner:
                    with mock.patch.object(sys, "argv", [
                        "run_examples.py", "--runner-command", COMMAND,
                        "--filter", "^01-", "--report", str(report)]):
                        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                            self.assertEqual(run_examples.main(), 1)
            self.assertEqual(runner.call_count, 1)
            evidence = json.loads(report.read_text())
            self.assertFalse(evidence["catalog_inputs_unchanged"])
            self.assertFalse(evidence["complete_catalog"])
            self.assertFalse(evidence["output_oracle_matched"])

    def test_report_hardlink_alias_rejected_before_runner(self):
        with tempfile.TemporaryDirectory() as folder:
            report = Path(folder) / "report.json"
            oracle = CASE / "expected.stdout"
            try:
                report.hardlink_to(oracle)
            except OSError:
                self.skipTest("cross-device hardlinks not supported")
            code, _, calls = check_run(
                ["--runner-command", COMMAND, "--report", str(report)],
                subprocess.CompletedProcess([], 0, "PASS:1\n", ""))
            self.assertEqual((code, calls), (2, 0))
            self.assertEqual(report.read_text(), "PASS:1\n")

    def test_pattern_directory_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "target"
            target.mkdir()
            (root / "01-linked").symlink_to(target, target_is_directory=True)
            with mock.patch.object(run_examples, "PATTERNS", root):
                with self.assertRaisesRegex(ValueError, "pattern directories must not be symlinks"):
                    run_examples.discover()

    def test_list_does_not_run_compiler(self):
        code, output, calls = check_run(["--list"], None)
        self.assertEqual(code, 0)
        self.assertEqual(calls, 0)
        self.assertIn("UNVERIFIED", output)

if __name__ == "__main__":
    unittest.main()
