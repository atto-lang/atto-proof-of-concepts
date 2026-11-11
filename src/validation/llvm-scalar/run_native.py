#!/usr/bin/env python3
"""Compile and execute restricted Oreslang LLVM scalar fixtures.

Needs an existing oreslang-llvmc binary and a working clang. No silent skips.
The compiler's stdout must contain LLVM IR; stderr is diagnostic.
Actual processes must exit with fixture-defined small positive exit status.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
EXPECTED = {
    "forward-call.atto": 42,
    "arithmetic-precedence.atto": 42,
    "nested-calls.atto": 42,
    "unary-negative.atto": 42,
    "module-scoped.atto": 42,
    "call-chain.atto": 42,
}


def run_command(argv, timeout, **kw):
    return subprocess.run(argv, capture_output=True, timeout=timeout,
                          check=False, **kw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, help="Path to oreslang-llvmc")
    parser.add_argument("--clang", default="clang")
    parser.add_argument("--compiler-revision", required=True,
                        help="Full git SHA of compiler binary, supplied by operator")
    parser.add_argument("--report", help="JSON report output path")
    parser.add_argument("--compiler-checkout",
                        help="Optional compiler source checkout to verify Git HEAD and tracked-tree cleanliness")
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-fA-F]{40}", args.compiler_revision) is None:
        parser.error("--compiler-revision requires a full 40-digit hexadecimal git SHA")
    if args.timeout < 1:
        parser.error("timeout must be positive")
    checkout_verified = False
    if args.compiler_checkout:
        try:
            revision = run_command(["git", "-C", args.compiler_checkout, "rev-parse", "HEAD"],
                                   args.timeout, text=True)
            changes = run_command(["git", "-C", args.compiler_checkout, "status", "--porcelain",
                                   "--untracked-files=no"], args.timeout, text=True)
        except (OSError, subprocess.TimeoutExpired) as err:
            print(f"Cannot verify compiler checkout: {err}", file=sys.stderr)
            return 2
        if (revision.returncode != 0 or revision.stdout.strip().lower() != args.compiler_revision.lower()
                or changes.returncode != 0 or changes.stdout.strip()):
            print("Compiler checkout revision mismatch or modified tracked source", file=sys.stderr)
            return 2
        checkout_verified = True
    results = []
    with tempfile.TemporaryDirectory(prefix="oreslang-llvm-smoke-") as temp:
        temp = Path(temp)
        for name, expected in EXPECTED.items():
            source = HERE / name
            report = {"source": name, "expected_exit": expected, "pass": False}
            try:
                source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
                report["source_sha256"] = source_sha
                compiled = run_command([args.compiler, str(source)], args.timeout, text=True)
                report["compiler_exit"] = compiled.returncode
                report["compiler_stderr"] = compiled.stderr
                if compiled.returncode != 0 or not compiled.stdout.strip():
                    report["failure"] = "compiler failed or emitted no IR"
                else:
                    ir_path = temp / (source.stem + ".ll")
                    exe_path = temp / (source.stem + ".bin")
                    ir_path.write_text(compiled.stdout, encoding="utf-8")
                    linked = run_command([args.clang, "-x", "ir", str(ir_path), "-o", str(exe_path)],
                                         args.timeout, text=True)
                    report["clang_exit"] = linked.returncode
                    report["clang_stderr"] = linked.stderr
                    if linked.returncode != 0:
                        report["failure"] = "clang failed to compile LLVM IR"
                    else:
                        executed = run_command([str(exe_path)], args.timeout, text=True)
                        report["actual_exit"] = executed.returncode
                        report["stdout"] = executed.stdout
                        report["stderr"] = executed.stderr
                        report["pass"] = (executed.returncode == expected
                                          and executed.stdout == "" and executed.stderr == "")
                        if not report["pass"]:
                            report["failure"] = "native executable mismatch"
            except (OSError, subprocess.TimeoutExpired) as err:
                report["failure"] = str(err)
            try:
                report["inputs_unchanged"] = (
                    source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest()
                    == report.get("source_sha256")
                )
            except OSError:
                report["inputs_unchanged"] = False
            if not report["inputs_unchanged"]:
                report["pass"] = False
                report["failure"] = "fixture changed during run or became unreadable"
            results.append(report)
            print(f'{"PASS" if report["pass"] else "FAIL"} {name}')
    summary = {"compiler_revision": args.compiler_revision, "compiler": args.compiler,
               "checkout_verified": checkout_verified,
               "provenance": "caller supplied compiler identity; checkout only verifies source HEAD, not built binary",
               "total": len(results), "passed": sum(int(v["pass"]) for v in results),
               "results": results}
    if args.report:
        try:
            Path(args.report).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        except OSError as err:
            print(f"Cannot write LLVM evidence report: {err}", file=sys.stderr)
            return 2
    print(f'Passed {summary["passed"]}/{summary["total"]} LLVM scalar smoke cases')
    return 0 if summary["passed"] == len(EXPECTED) else 1


if __name__ == "__main__":
    raise SystemExit(main())
