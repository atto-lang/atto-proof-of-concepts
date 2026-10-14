#!/usr/bin/env python3
"""Inventory or execute independent library behavioral probes (not compiler CI)."""
import argparse
import hashlib
import json
import math
import re
import runpy
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
GRAMMAR = runpy.run_path(str(HERE.parent / "patterns" / "tip_syntax_hygiene.py"))
HYGIENE = GRAMMAR["violations"]
CODE_ONLY = GRAMMAR["code_only"]
EXPECTED_NAMES = frozenset(["oreslang-vec","oreslang-linked-list","oreslang-deque","oreslang-hashmap","oreslang-trees","oreslang-graphs","oreslang-arena","oreslang-btree","oreslang-trie","oreslang-persistent","oreslang-interval-tree","oreslang-iter","oreslang-closures","oreslang-parser-combinators","oreslang-ast","oreslang-interpreter","oreslang-di","oreslang-cache","oreslang-serialize","oreslang-regex","oreslang-event-log","oreslang-compiler","oreslang-bytecode-vm","oreslang-dop","oreslang-property","oreslang-fuzz","oreslang-modelcheck","oreslang-bench","oreslang-scheduler","oreslang-work-stealing","oreslang-channels","oreslang-testkit"])

def inventory(root=HERE):
    cases = []
    for d in sorted(root.glob("oreslang-*")):
        if d.is_symlink():
            raise ValueError(f"{d.name}: symlink directories are not allowed")
        if not d.is_dir():
            continue
        s, e = d / "example.ores", d / "expected.stdout"
        if not s.exists() and not e.exists():
            continue
        if s.is_symlink() or e.is_symlink():
            raise ValueError(f"{d.name}: symlink fixtures are not allowed")
        if not s.is_file() or not e.is_file():
            raise ValueError(f"{d.name}: missing source or oracle")
        body, expected = s.read_text(), e.read_text()
        if expected != f"PASS:{d.name}\n":
            raise ValueError(f"{d.name}: invalid exact output oracle")
        try:
            masked = CODE_ONLY(body)
            problems = HYGIENE(body)
        except ValueError as exc:
            raise ValueError(f"{d.name}: lexical hygiene: {exc}") from exc
        if problems:
            raise ValueError(f"{d.name}: lexical hygiene: {problems}")
        if len(re.findall(r"\bpub\s+(?:async\s+)?routine\s+main\s*\(", masked)) != 1:
            raise ValueError(f"{d.name}: expected one active public main")
        depth = 0
        for char in masked:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth < 0:
                    raise ValueError(f"{d.name}: unmatched closing brace")
        if depth != 0:
            raise ValueError(f"{d.name}: unmatched opening brace")
        print_calls = (body[m.end():] for m in re.finditer(
            r"\bstdio\s*\.\s*stdout\s*\.\s*println\s*\(\s*", masked))
        calls = list(print_calls)
        if not any(re.match(r'"PASS:' + re.escape(d.name) + r'"\s*\)', c) for c in calls):
            raise ValueError(f"{d.name}: missing active PASS print")
        if not any(re.match(r'"FAIL:' + re.escape(d.name) + r':[^"]+"\s*\)', c) for c in calls):
            raise ValueError(f"{d.name}: missing active FAIL print")
        cases.append((d.name, s, e, expected))
    actual = {name for name, _, _, _ in cases}
    if root == HERE and actual != EXPECTED_NAMES:
        raise ValueError(f"prototype inventory drift: missing={sorted(EXPECTED_NAMES - actual)}, unexpected={sorted(actual - EXPECTED_NAMES)}")
    if not cases:
        raise ValueError("empty library prototype inventory")
    return cases

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--list", action="store_true")
    p.add_argument("--runner-command", help="argv, one {source} placeholder, no shell")
    p.add_argument("--backend", default="unspecified")
    p.add_argument("--mode", choices=("run", "compile"), default="run",
                   help="compile validates compiler exit only, NEVER guest behavior")
    p.add_argument("--filter", help="optional regular expression matching library directory")
    p.add_argument("--compiler-revision", default="unknown")
    p.add_argument("--require-revision", action="store_true",
                   help="require full 40-hex caller-supplied compiler checkout revision")
    p.add_argument("--timeout", type=float, default=40)
    p.add_argument("--max-output-bytes", type=int, default=65536,
                   help="per-stream byte limit for captured stdout/stderr")
    p.add_argument("--report")
    a = p.parse_args()
    try:
        all_cases = inventory()
        try:
            selector = re.compile(a.filter) if a.filter is not None else None
        except re.error as exc:
            raise ValueError(f"invalid filter expression: {exc}") from exc
        cases = [case for case in all_cases if selector is None or selector.search(case[0])]
        if not cases:
            raise ValueError("selection contains no library experiments")
        if a.list:
            if a.runner_command:
                raise ValueError("--list and --runner-command are mutually exclusive")
            for name, _, _, _ in cases:
                print("UNVERIFIED", name)
            print(f"Inventory: {len(cases)} of {len(all_cases)} probes; NOT a compiler/runtime check")
            return 0
        if not a.runner_command:
            raise ValueError("use --list, or pass a real --runner-command")
        if not math.isfinite(a.timeout) or a.timeout <= 0:
            raise ValueError("timeout must be finite positive")
        if a.require_revision and (len(a.compiler_revision) != 40 or
                                  any(ch not in "0123456789abcdefABCDEF" for ch in a.compiler_revision)):
            raise ValueError("require full 40-hex compiler revision")
        if not (1 <= a.max_output_bytes <= 16 * 1024 * 1024):
            raise ValueError("max output bytes must be between 1 and 16777216")
        argv = shlex.split(a.runner_command)
        if not argv or sum(x.count("{source}") for x in argv) != 1:
            raise ValueError("runner must contain {source} exactly once")
        # Pin ALL inputs before executing ANY runner. Later cases cannot silently
        # inherit mutations introduced by earlier runner invocations.
        pinned = {name: (digest(source), digest(oracle))
                  for name, source, oracle, _ in all_cases}
        results = []
        for name, source, oracle, expected in cases:
            sh, eh = pinned[name]
            unchanged_before = digest(source) == sh and digest(oracle) == eh
            cmd = [x.replace("{source}", str(source.resolve())) for x in argv]
            try:
                with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
                    proc = subprocess.run(cmd, cwd=HERE.parent.parent, stdout=out,
                                          stderr=err, timeout=a.timeout, check=False)
                    stdout_bytes, stderr_bytes = out.tell(), err.tell()
                    out.seek(0)
                    err.seek(0)
                    raw_stdout = out.read(a.max_output_bytes + 1)
                    raw_stderr = err.read(a.max_output_bytes + 1)
                oversized = stdout_bytes > a.max_output_bytes or stderr_bytes > a.max_output_bytes
                actual = raw_stdout.decode("utf-8", errors="replace")
                unchanged = (unchanged_before and digest(source) == sh
                             and digest(oracle) == eh)
                ok = (not oversized and unchanged and proc.returncode == 0
                      and (a.mode == "compile" or raw_stdout == expected.encode("utf-8")))
                item = dict(name=name, success=ok, mode=a.mode, returncode=proc.returncode,
                            inputs_unchanged=unchanged, output_truncated=oversized,
                            stdout_bytes=stdout_bytes, stderr_bytes=stderr_bytes,
                            stdout=actual, stderr=raw_stderr.decode("utf-8", errors="replace"))
            except (OSError, subprocess.TimeoutExpired) as exc:
                item = dict(name=name, success=False, mode=a.mode, error=str(exc))
            item.update(source_sha256=sh, oracle_sha256=eh)
            results.append(item)
        # Detect retroactive changes to previously tested cases AND changes to
        # unselected fixtures. Per-result success remains false if its inputs drift.
        catalog_unchanged = True
        for name, src, oracle, _ in all_cases:
            sh, eh = pinned[name]
            stable = digest(src) == sh and digest(oracle) == eh
            catalog_unchanged = catalog_unchanged and stable
            for result in results:
                if result["name"] == name and not stable:
                    result["inputs_unchanged"] = False
                    result["success"] = False
        for item in results:
            print(("PASS " if item["success"] else "FAIL ") + item["name"])
        if a.report:
            Path(a.report).write_text(json.dumps(dict(backend=a.backend,
                compiler_revision=a.compiler_revision,
                provenance="caller-supplied labels; verify separately",
                revision_format_verified=a.require_revision,
                mode=a.mode, selected=len(cases), inventory_total=len(all_cases),
                complete_catalog=len(cases)==len(all_cases),
                catalog_inputs_unchanged=catalog_unchanged,
                output_oracle_matched=a.mode=="run" and catalog_unchanged
                    and all(item["success"] for item in results),
                results=results), indent=2)+"\n")
        return 0 if catalog_unchanged and all(item["success"] for item in results) else 1
    except (ValueError, OSError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
