"""Pattern-runner contract tests. No Oreslang backend is executed."""
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock
import run_examples

FAKE = [(1, Path("01-factory-method"), Path("example.ores"), "PASS:1\n")]
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
        self.assertEqual(len(patterns), 70)
        self.assertEqual([n for n, _, _, _ in patterns], list(range(1, 71)))

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

    def test_malformed_filter_fails_closed(self):
        code, output, calls = check_run(["--filter", "[", "--runner-command", COMMAND], None)
        self.assertEqual(code, 2)
        self.assertEqual(calls, 0)

    def test_list_does_not_run_compiler(self):
        code, output, calls = check_run(["--list"], None)
        self.assertEqual(code, 0)
        self.assertEqual(calls, 0)
        self.assertIn("UNVERIFIED", output)

if __name__ == "__main__":
    unittest.main()
