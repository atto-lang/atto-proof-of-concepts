#!/usr/bin/env python3
"""Inventory or execute independent library behavioral probes (not compiler CI)."""
import argparse
import hashlib
import json
import math
import runpy
from pathlib import Path
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
HYGIENE = runpy.run_path(str(HERE.parent / "patterns" / "tip_syntax_hygiene.py"))["violations"]
EXPECTED_NAMES = frozenset(["oreslang-vec","oreslang-linked-list","oreslang-deque","oreslang-hashmap","oreslang-trees","oreslang-graphs","oreslang-arena","oreslang-btree","oreslang-trie","oreslang-persistent","oreslang-interval-tree","oreslang-iter","oreslang-closures","oreslang-parser-combinators","oreslang-ast","oreslang-interpreter","oreslang-di","oreslang-cache","oreslang-serialize","oreslang-regex","oreslang-event-log","oreslang-compiler","oreslang-bytecode-vm","oreslang-dop","oreslang-property","oreslang-fuzz","oreslang-modelcheck","oreslang-bench","oreslang-scheduler","oreslang-work-stealing","oreslang-channels","oreslang-testkit"])

def inventory(root=HERE):
    cases = []
    for d in sorted(root.glob("oreslang-*")):
        if not d.is_dir():
            continue
        s, e = d / "example.ores", d / "expected.stdout"
        if not s.exists() and not e.exists():
            continue
        if not s.is_file() or not e.is_file():
            raise ValueError(f"{d.name}: missing source or oracle")
        body, expected = s.read_text(), e.read_text()
        if expected != f"PASS:{d.name}\n":
            raise ValueError(f"{d.name}: invalid exact output oracle")
        if body.count("pub routine main(") != 1 or body.count("{") != body.count("}"):
            raise ValueError(f"{d.name}: invalid entrypoint or brace structure")
        try:
            problems = HYGIENE(body)
        except ValueError as exc:
            raise ValueError(f"{d.name}: lexical hygiene: {exc}") from exc
        if problems:
            raise ValueError(f"{d.name}: lexical hygiene: {problems}")
        if ('stdio.stdout.println("PASS:' + d.name + '")') not in body:
            raise ValueError(f"{d.name}: missing PASS print")
        if f"FAIL:{d.name}:" not in body:
            raise ValueError(f"{d.name}: missing visible FAIL marker")
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
    p.add_argument("--compiler-revision", default="unknown")
    p.add_argument("--timeout", type=float, default=40)
    p.add_argument("--report")
    a = p.parse_args()
    try:
        cases = inventory()
        if a.list:
            if a.runner_command:
                raise ValueError("--list and --runner-command are mutually exclusive")
            for name, _, _, _ in cases:
                print("UNVERIFIED", name)
            print(f"Inventory: {len(cases)} probes; NOT a compiler/runtime check")
            return 0
        if not a.runner_command:
            raise ValueError("use --list, or pass a real --runner-command")
        if not math.isfinite(a.timeout) or a.timeout <= 0:
            raise ValueError("timeout must be finite positive")
        argv = shlex.split(a.runner_command)
        if sum(x.count("{source}") for x in argv) != 1:
            raise ValueError("runner must contain {source} exactly once")
        results = []
        for name, source, oracle, expected in cases:
            sh, eh = digest(source), digest(oracle)
            cmd = [x.replace("{source}", str(source.resolve())) for x in argv]
            try:
                proc = subprocess.run(cmd, cwd=HERE.parent.parent, capture_output=True,
                                      text=True, timeout=a.timeout, check=False)
                unchanged = digest(source) == sh and digest(oracle) == eh
                ok = unchanged and proc.returncode == 0 and proc.stdout == expected
                item = dict(name=name, success=ok, returncode=proc.returncode,
                            inputs_unchanged=unchanged, stdout=proc.stdout, stderr=proc.stderr)
            except (OSError, subprocess.TimeoutExpired) as exc:
                item = dict(name=name, success=False, error=str(exc))
            item.update(source_sha256=sh, oracle_sha256=eh)
            results.append(item)
            print(("PASS " if item["success"] else "FAIL ") + name)
        if a.report:
            Path(a.report).write_text(json.dumps(dict(backend=a.backend,
                compiler_revision=a.compiler_revision,
                provenance="caller-supplied labels; verify separately",
                results=results), indent=2)+"\n")
        return 0 if all(item["success"] for item in results) else 1
    except (ValueError, OSError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
