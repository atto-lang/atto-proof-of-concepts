"""Python driver regression tests; mocks do not validate Oreslang compiler semantics."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import run_native

REV = "a" * 40

def ok(text="", code=0):
    return subprocess.CompletedProcess([], code, text, "")

class NativeDriverContractTests(unittest.TestCase):
    def check(self, responses, source_present=True, change_at=None, extra=()):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            source = path / "case.ores"
            if source_present:
                source.write_text("pub fnc main(): int { return 42; }")
            report = path / "result.json"
            argv = ["run_native.py", "--compiler", "fake", "--clang", "clang",
                    "--compiler-revision", REV, "--report", str(report), *extra]
            calls = []
            stream = iter(responses)
            def invoke(argv, timeout, **kwargs):
                calls.append(argv)
                if change_at == len(calls):
                    source.write_text("tampered")
                result = next(stream)
                if isinstance(result, Exception):
                    raise result
                return result
            with mock.patch.object(run_native, "HERE", path), \
                 mock.patch.object(run_native, "EXPECTED", {"case.ores": 42}), \
                 mock.patch.object(run_native, "run_command", side_effect=invoke), \
                 mock.patch.object(sys, "argv", argv), \
                 contextlib.redirect_stdout(io.StringIO()):
                status = run_native.main()
            return status, json.loads(report.read_text()) if report.exists() else None, len(calls)

    def test_fake_success_and_metadata(self):
        code, r, n = self.check([ok("define i32 @main() { ret i32 42 }"),
                                  ok(), ok(code=42)])
        self.assertEqual((code, r["passed"], n), (0, 1, 3))
        self.assertTrue(r["results"][0]["inputs_unchanged"])
        self.assertFalse(r["checkout_verified"])
        self.assertEqual(len(r["results"][0]["source_sha256"]), 64)
        self.assertIn("caller supplied", r["provenance"])

    def test_compiler_fails(self):
        code, r, n = self.check([ok("", 1)])
        self.assertEqual((code, r["passed"], n), (1, 0, 1))

    def test_empty_ir_fails(self):
        code, r, n = self.check([ok()])
        self.assertEqual((code, r["passed"], n), (1, 0, 1))

    def test_linker_fails(self):
        code, r, n = self.check([ok("IR"), ok("", 1)])
        self.assertEqual((code, r["passed"], n), (1, 0, 2))

    def test_native_exit_mismatch(self):
        code, r, n = self.check([ok("IR"), ok(), ok(code=41)])
        self.assertEqual((code, r["passed"], n), (1, 0, 3))

    def test_unexpected_stdout_rejected(self):
        code, r, n = self.check([ok("IR"), ok(), ok("unexpected", 42)])
        self.assertEqual((code, r["passed"], n), (1, 0, 3))

    def test_unexpected_stderr_rejected(self):
        code, r, n = self.check([ok("IR"), ok(),
                                  subprocess.CompletedProcess([], 42, "", "unexpected")])
        self.assertEqual((code, r["passed"], n), (1, 0, 3))

    def test_mutated_source_rejected(self):
        code, r, n = self.check([ok("IR"), ok(), ok(code=42)], change_at=3)
        self.assertEqual((code, r["passed"], n), (1, 0, 3))
        self.assertFalse(r["results"][0]["inputs_unchanged"])

    def test_missing_fixture_rejected(self):
        code, r, n = self.check([], source_present=False)
        self.assertEqual((code, r["passed"], n), (1, 0, 0))

    def test_timeout_rejected(self):
        code, r, n = self.check([subprocess.TimeoutExpired("fake", 1)])
        self.assertEqual((code, r["passed"], n), (1, 0, 1))

    def test_checkout_mismatch_rejected(self):
        code, r, n = self.check([ok("b" * 40 + "\n"), ok("")],
                                extra=("--compiler-checkout", "/tmp/wrong"))
        self.assertEqual((code, r, n), (2, None, 2))

    def test_checkout_verified_label_on_match(self):
        code, r, n = self.check([ok(REV + "\n"), ok(""), ok("IR"), ok(), ok(code=42)],
                                extra=("--compiler-checkout", "/tmp/sample"))
        self.assertEqual((code, n), (0, 5))
        self.assertTrue(r["checkout_verified"])

    @unittest.skipUnless(shutil.which("clang"), "clang is unavailable")
    def test_real_clang_on_synthetic_ir_not_oreslang(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            (path / "case.ores").write_text("pub fnc main(): int { return 42; }")
            fake = path / "fake-compiler"
            fake.write_text("#!/usr/bin/env python3\nprint('define i32 @main() { ret i32 42 }')\n")
            fake.chmod(0o755)
            report = path / "output.json"
            argv = ["run_native.py", "--compiler", str(fake), "--clang",
                    shutil.which("clang"), "--compiler-revision", REV, "--report", str(report)]
            with mock.patch.object(run_native, "HERE", path), \
                 mock.patch.object(run_native, "EXPECTED", {"case.ores": 42}), \
                 mock.patch.object(sys, "argv", argv), \
                 contextlib.redirect_stdout(io.StringIO()):
                code = run_native.main()
            self.assertEqual(code, 0, report.read_text() if report.exists() else "no report")
            self.assertEqual(json.loads(report.read_text())["passed"], 1)

if __name__ == "__main__":
    unittest.main()
