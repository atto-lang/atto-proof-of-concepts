#!/usr/bin/env python3
"""Run independent Oreslang pattern programs against a user-provided toolchain.

Without --runner-command this is an inventory report, NOT a test run.
Supply an executable argv template containing {source}, for example:
  python3 src/patterns/run_examples.py --runner-command 'oreslang run {source}'
No shell is invoked; each file is run in its own process. Stdout and exit code
must match the fixture exactly. Empty/missing expectations are errors.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
PATTERNS = Path(__file__).resolve().parent


def discover():
    result = []
    for directory in sorted(PATTERNS.iterdir()):
        if not directory.is_dir() or re.match(r"^[0-9]{2}-", directory.name) is None:
            continue
        number = int(directory.name[:2])
        source = directory / "example.ores"
        oracle = directory / "expected.stdout"
        if not source.is_file() or not oracle.is_file():
            raise ValueError(f"{directory.name}: missing example.ores or expected.stdout")
        expected = oracle.read_text(encoding="utf-8")
        if expected != f"PASS:{number}\n":
            raise ValueError(f"{directory.name}: invalid or empty expected.stdout")
        body = source.read_text(encoding="utf-8")
        if body.count("{") != body.count("}"):
            raise ValueError(f"{directory.name}: unbalanced source braces")
        if body.count("pub routine main(") + body.count("pub async routine main(") != 1:
            raise ValueError(f"{directory.name}: expected exactly one Oreslang entrypoint")
        if f"PASS:{number}" not in body or f"FAIL:{number}:" not in body:
            raise ValueError(f"{directory.name}: no visible behavioral assertion/marker")
        result.append((number, directory, source, expected))
    if [item[0] for item in result] != list(range(1, 71)):
        raise ValueError("expected exactly the numbered pattern directories 01..70")
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runner-command", help="argv template for compiler+runner; must contain {source}")
    ap.add_argument("--backend", default="unspecified", help="backend name for report")
    ap.add_argument("--mode", choices=("run", "compile"), default="run",
                    help="run compares stdout; compile only checks compiler exit 0")
    ap.add_argument("--require-revision", action="store_true", help="Require exact 40-hex compiler SHA")
    ap.add_argument("--compiler-revision", default="unknown",
                    help="exact Java/LLVM commit SHA of the tested compiler")
    ap.add_argument("--timeout", type=float, default=40.0)
    ap.add_argument("--filter", help="regex against pattern folder name")
    ap.add_argument("--report", help="JSON report output path")
    ap.add_argument("--list", action="store_true", help="structural inventory only (no execution)")
    args = ap.parse_args()
    try:
        fixtures = discover()
    except (ValueError, OSError) as exc:
        print(f"STRUCTURAL FAILURE: {exc}", file=sys.stderr)
        return 2
    try:
        pattern_filter = re.compile(args.filter) if args.filter is not None else None
    except re.error as exc:
        print(f"Invalid --filter regular expression: {exc}", file=sys.stderr)
        return 2
    selected = [it for it in fixtures if pattern_filter is None or pattern_filter.search(it[1].name)]
    if args.filter and not selected:
        print("No examples match --filter", file=sys.stderr)
        return 2
    if args.list or not args.runner_command:
        for number, directory, _, _ in selected:
            print(f"UNVERIFIED {number:02d} {directory.name}")
        print(f"Inventory: {len(selected)} examples. No compiler/runtime execution performed.")
        if not args.list and not args.runner_command:
            print("Use --runner-command to run the examples.", file=sys.stderr)
        return 0
    try:
        argv_template = shlex.split(args.runner_command)
    except ValueError as exc:
        print(f"Invalid runner command: {exc}", file=sys.stderr)
        return 2
    if sum(token.count("{source}") for token in argv_template) != 1:
        print("Runner command must contain {source} exactly once.", file=sys.stderr)
        return 2
    if args.require_revision and not re.fullmatch(r"[0-9a-fA-F]{40}", args.compiler_revision):
        print("A full 40-character compiler commit SHA is required", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        print("--timeout must be positive", file=sys.stderr)
        return 2
    results = []
    for number, directory, source, expected in selected:
        source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
        argv = [token.replace("{source}", str(source.resolve())) for token in argv_template]
        started = time.monotonic()
        try:
            proc = subprocess.run(argv, cwd=ROOT, capture_output=True,
                                  text=True, encoding="utf-8", errors="replace",
                                  timeout=args.timeout, check=False)
            ok = proc.returncode == 0 and (args.mode == "compile" or proc.stdout == expected)
            result = {
                "pattern": directory.name, "backend": args.backend, "mode": args.mode,
                "source_sha256": source_sha256,
                "success": ok, "exit_code": proc.returncode,
                "stdout": proc.stdout, "stderr": proc.stderr,
                "expected_stdout": expected,
                "seconds": round(time.monotonic() - started, 3),
            }
        except (subprocess.TimeoutExpired, OSError) as exc:
            result = {
                "pattern": directory.name, "backend": args.backend, "mode": args.mode,
                "source_sha256": source_sha256,
                "success": False, "error": str(exc),
                "seconds": round(time.monotonic() - started, 3),
            }
        print(f'{"PASS" if result["success"] else "FAIL"} {directory.name}')
        results.append(result)
    passes = sum(int(item["success"]) for item in results)
    report = {
        "backend": args.backend, "mode": args.mode,
        "compiler_revision": args.compiler_revision,
        "command": args.runner_command,
        "evidence_level": "compile" if args.mode == "compile" else "runtime",
        "selected": len(selected),
        "passed": passes, "failed": len(selected) - passes,
        "results": results,
    }
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f'Executed {len(selected)}; passed {passes}; failed {len(selected) - passes}')
    return 0 if passes == len(selected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
