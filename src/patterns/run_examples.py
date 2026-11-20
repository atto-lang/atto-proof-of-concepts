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
import math
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
PATTERNS = Path(__file__).resolve().parent
# Reuse the bounded subprocess and fixture-integrity primitives from libraries.
# These detect drift but do not sandbox malicious toolchains.
sys.path.insert(0, str(ROOT / "src" / "libraries"))
from check_prototypes import bounded_run, fingerprint, unchanged, publish_report


def discover():
    result = []
    for directory in sorted(PATTERNS.iterdir()):
        if re.match(r"^[0-9]{2}-", directory.name) is None:
            continue
        if directory.is_symlink():
            raise ValueError(f"{directory.name}: pattern directories must not be symlinks")
        if not directory.is_dir():
            raise ValueError(f"{directory.name}: expected a pattern directory")
        number = int(directory.name[:2])
        source = directory / "example.ores"
        oracle = directory / "expected.stdout"
        if source.is_symlink() or oracle.is_symlink():
            raise ValueError(f"{directory.name}: source and oracle must not be symlinks")
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
    if len(result) < 70 or [item[0] for item in result] != list(range(1, len(result) + 1)):
        raise ValueError("expected at least 70 contiguous numbered pattern directories starting at 01")
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runner-command", help="argv template for compiler+runner; must contain {source}")
    ap.add_argument("--backend", default="unspecified", help="backend name for report")
    ap.add_argument("--mode", choices=("run", "compile"), default="run",
                    help="run compares stdout; compile only checks compiler exit 0")
    ap.add_argument("--require-revision", action="store_true",
                    help="Require a full 40-hex compiler commit SHA for provenance")
    ap.add_argument("--compiler-revision", default="unknown",
                    help="exact Java/LLVM commit SHA of the tested compiler")
    ap.add_argument("--timeout", type=float, default=40.0)
    ap.add_argument("--max-output-bytes", type=int, default=65536,
                    help="per-stream limit, 1..16777216 bytes")
    ap.add_argument("--allow-stderr", action="store_true",
                    help="allow guest stderr in run mode (default is fail closed)")
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
    if args.list and args.runner_command:
        print("--list cannot be combined with --runner-command", file=sys.stderr)
        return 2
    if args.list:
        for number, directory, _, _ in selected:
            print(f"UNVERIFIED {number:02d} {directory.name}")
        print(f"Inventory: {len(selected)} examples. No compiler/runtime execution performed.")
        return 0
    if not args.runner_command:
        print("Missing --runner-command: use --list for inventory only", file=sys.stderr)
        return 2
    try:
        argv_template = shlex.split(args.runner_command)
    except ValueError as exc:
        print(f"Invalid runner command: {exc}", file=sys.stderr)
        return 2
    if not argv_template or sum(token.count("{source}") for token in argv_template) != 1:
        print("Runner command must contain {source} exactly once.", file=sys.stderr)
        return 2
    if args.require_revision and not re.fullmatch(r"[0-9a-fA-F]{40}", args.compiler_revision):
        print("A full 40-character compiler revision is required", file=sys.stderr)
        return 2
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        print("--timeout must be a finite positive number", file=sys.stderr)
        return 2
    if not (1 <= args.max_output_bytes <= 16 * 1024 * 1024):
        print("--max-output-bytes must be 1..16777216", file=sys.stderr)
        return 2
    try:
        # Report destination cannot alias any fixture, selected or otherwise.
        if args.report:
            destination = Path(args.report).resolve()
            protected = [p for _, d, src, _ in fixtures
                         for p in (src, d / "expected.stdout")]
            if any(destination == p.resolve() or
                   (destination.is_file() and destination.samefile(p))
                   for p in protected):
                raise ValueError("report destination aliases a source/oracle fixture")
        # Pin ALL inputs before executing ANY toolchain command.
        pinned = {d.name: (fingerprint(src), fingerprint(d / "expected.stdout"))
                  for _, d, src, _ in fixtures}
    except (ValueError, OSError) as exc:
        print(f"INPUT ADMISSION FAILURE: {exc}", file=sys.stderr)
        return 2

    results = []
    for number, directory, source, expected in selected:
        oracle = directory / "expected.stdout"
        sh, eh = pinned[directory.name]
        started = time.monotonic()
        stable_before = unchanged(source, sh) and unchanged(oracle, eh)
        if not stable_before:
            result = {
                "pattern": directory.name, "backend": args.backend, "mode": args.mode,
                "source_sha256": sh[0], "oracle_sha256": eh[0],
                "inputs_unchanged": False, "success": False,
                "error": "source or oracle changed before invocation",
            }
        else:
            argv = [token.replace("{source}", str(source.resolve())) for token in argv_template]
            try:
                exit_code, stdout, stderr, oversized = bounded_run(
                    argv, ROOT, args.timeout, args.max_output_bytes)
                stable = unchanged(source, sh) and unchanged(oracle, eh)
                stderr_ok = args.mode == "compile" or args.allow_stderr or not stderr
                ok = (exit_code == 0 and stable and not oversized and stderr_ok
                      and (args.mode == "compile" or stdout == expected.encode("utf-8")))
                result = {
                    "pattern": directory.name, "backend": args.backend, "mode": args.mode,
                    "source_sha256": sh[0], "oracle_sha256": eh[0],
                    "inputs_unchanged": stable, "success": ok, "exit_code": exit_code,
                    "output_truncated": oversized,
                    "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
                    "stdout": stdout.decode("utf-8", errors="replace"),
                    "stderr": stderr.decode("utf-8", errors="replace"),
                    "expected_stdout": expected,
                }
            except (subprocess.TimeoutExpired, OSError) as exc:
                result = {
                    "pattern": directory.name, "backend": args.backend, "mode": args.mode,
                    "source_sha256": sh[0], "oracle_sha256": eh[0],
                    "inputs_unchanged": unchanged(source, sh) and unchanged(oracle, eh),
                    "success": False, "error": str(exc),
                }
        result["seconds"] = round(time.monotonic() - started, 3)
        print(f'{"PASS" if result["success"] else "FAIL"} {directory.name}')
        results.append(result)

    # Retroactive modifications to previously checked cases, or unselected
    # fixtures, invalidate the entire run.
    catalog_unchanged = True
    for _, directory, source, _ in fixtures:
        sh, eh = pinned[directory.name]
        stable = unchanged(source, sh) and unchanged(directory / "expected.stdout", eh)
        catalog_unchanged = catalog_unchanged and stable
        if not stable:
            for item in results:
                if item["pattern"] == directory.name:
                    item["inputs_unchanged"] = False
                    item["success"] = False
    if not catalog_unchanged:
        print("FAIL CATALOG INPUTS MUTATED", file=sys.stderr)
    passes = sum(int(item["success"]) for item in results)
    report = {
        "backend": args.backend, "mode": args.mode,
        "compiler_revision": args.compiler_revision,
        "provenance": "caller-supplied labels; verify compiler revision independently",
        "runner_command_sha256": hashlib.sha256(args.runner_command.encode("utf-8")).hexdigest(),
        "revision_format_verified": args.require_revision,
        "selected": len(selected), "inventory_total": len(fixtures),
        "complete_catalog": len(selected) == len(fixtures),
        "catalog_inputs_unchanged": catalog_unchanged,
        "output_oracle_matched": args.mode == "run" and catalog_unchanged
                                  and passes == len(selected),
        "allow_stderr": args.allow_stderr, "max_output_bytes": args.max_output_bytes,
        "passed": passes, "failed": len(selected) - passes,
        "results": results,
    }
    if args.report:
        try:
            publish_report(args.report, report)
        except OSError as exc:
            print(f"Failed to atomically publish evidence report: {exc}", file=sys.stderr)
            return 2
    print(f'Executed {len(selected)}; passed {passes}; failed {len(selected) - passes}')
    return 0 if catalog_unchanged and passes == len(selected) else 1

if __name__ == "__main__":
    raise SystemExit(main())
