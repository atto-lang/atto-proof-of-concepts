#!/usr/bin/env python3
"""Inventory or execute independent library behavioral probes (not compiler CI)."""
import argparse
import hashlib
import json
import math
import os
import re
import selectors
import signal
import runpy
import stat
from pathlib import Path
import shlex
import subprocess
import sys
import time
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
        s, e = d / "example.atto", d / "expected.stdout"
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
            r"\bstdio\s*\.\s*stdout\s*\.\s*println\s*\(", masked))
        calls = list(print_calls)
        if not any(re.match(r'\s*"PASS:' + re.escape(d.name) + r'"\s*\)', c) for c in calls):
            raise ValueError(f"{d.name}: missing active PASS print")
        if not any(re.match(r'\s*"FAIL:' + re.escape(d.name) + r':[^"]+"\s*\)', c) for c in calls):
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

def fingerprint(path):
    """Bind bytes, inode, file type and mode; reject replacement by symlinks."""
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError(f"{path}: symlink fixture replacement")
    metadata = path.stat()
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"{path}: non-regular fixture replacement")
    return (digest(path), metadata.st_dev, metadata.st_ino,
            stat.S_IMODE(metadata.st_mode))

def unchanged(path, original):
    try:
        return fingerprint(path) == original
    except (OSError, ValueError):
        return False

def bounded_run(argv, cwd, timeout, max_bytes):
    """POSIX subprocess with live stdout/stderr caps and group-wide termination.

    Caller-provided runner remains untrusted. This is NOT an OS sandbox or a
    guarantee against subprocesses that deliberately detach from their group.
    """
    if os.name != "posix":
        raise OSError("bounded runner requires a POSIX process-group capable host")
    proc = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True)
    sel = selectors.DefaultSelector()
    output = [bytearray(), bytearray()]
    deadline = time.monotonic() + timeout
    reason = None
    try:
        for i, stream in enumerate((proc.stdout, proc.stderr)):
            os.set_blocking(stream.fileno(), False)
            sel.register(stream, selectors.EVENT_READ, data=i)
        while sel.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                reason = "timeout"
                break
            events = sel.select(remaining)
            if not events:
                reason = "timeout"
                break
            for key, _ in events:
                i = key.data
                data = os.read(key.fileobj.fileno(),
                               min(65536, max_bytes + 1 - len(output[i])))
                if not data:
                    sel.unregister(key.fileobj)
                    continue
                output[i].extend(data)
                if len(output[i]) > max_bytes:
                    reason = "output limit"
                    break
            if reason:
                break
        if reason is None:
            remaining = max(deadline - time.monotonic(), 0)
            try:
                proc.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                reason = "timeout"
        if reason:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            if reason == "timeout":
                raise subprocess.TimeoutExpired(argv, timeout)
        return (proc.returncode, bytes(output[0]), bytes(output[1]),
                reason == "output limit")
    finally:
        sel.close()
        for pipe in (proc.stdout, proc.stderr):
            pipe.close()
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()

def publish_report(path, report):
    """Atomically replace the report path; never follow a late symlink."""
    target = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=target.parent,
                prefix=".oreslang-report-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(report, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

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
    p.add_argument("--allow-stderr", action="store_true",
                   help="explicitly permit stderr in run mode; default fails closed")
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
        # The optional report must never overwrite any fixture, including an
        # unselected one or a hardlink/symlink alias to a protected path.
        if a.report:
            report_path = Path(a.report).resolve()
            protected = [p for _, src, oracle, _ in all_cases
                         for p in (src, oracle)]
            if any(report_path == p.resolve() or
                   (report_path.is_file() and report_path.samefile(p))
                   for p in protected):
                raise ValueError("report destination aliases a protected fixture")
        # Pin ALL inputs before executing ANY runner. Later cases cannot silently
        # inherit mutations introduced by earlier runner invocations.
        pinned = {name: (fingerprint(source), fingerprint(oracle))
                  for name, source, oracle, _ in all_cases}
        results = []
        for name, source, oracle, expected in cases:
            sh, eh = pinned[name]
            unchanged_before = unchanged(source, sh) and unchanged(oracle, eh)
            if not unchanged_before:
                results.append(dict(name=name, success=False, mode=a.mode,
                    inputs_unchanged=False, error="source or oracle changed before invocation",
                    source_sha256=sh[0], oracle_sha256=eh[0]))
                continue
            cmd = [x.replace("{source}", str(source.resolve())) for x in argv]
            try:
                returncode, raw_stdout, raw_stderr, oversized = bounded_run(
                    cmd, HERE.parent.parent, a.timeout, a.max_output_bytes)
                stable = unchanged(source, sh) and unchanged(oracle, eh)
                stderr_ok = a.mode == "compile" or a.allow_stderr or not raw_stderr
                ok = (not oversized and stable and returncode == 0 and stderr_ok
                      and (a.mode == "compile" or raw_stdout == expected.encode("utf-8")))
                item = dict(name=name, success=ok, mode=a.mode, returncode=returncode,
                            inputs_unchanged=stable, output_truncated=oversized,
                            stdout_bytes=len(raw_stdout), stderr_bytes=len(raw_stderr),
                            stdout=raw_stdout.decode("utf-8", errors="replace"),
                            stderr=raw_stderr.decode("utf-8", errors="replace"))
            except (OSError, subprocess.TimeoutExpired) as exc:
                item = dict(name=name, success=False, mode=a.mode, error=str(exc))
            item.update(source_sha256=sh[0], oracle_sha256=eh[0])
            results.append(item)
        # Detect retroactive changes to previously tested cases AND changes to
        # unselected fixtures. Per-result success remains false if its inputs drift.
        catalog_unchanged = True
        for name, src, oracle, _ in all_cases:
            sh, eh = pinned[name]
            stable = unchanged(src, sh) and unchanged(oracle, eh)
            catalog_unchanged = catalog_unchanged and stable
            for result in results:
                if result["name"] == name and not stable:
                    result["inputs_unchanged"] = False
                    result["success"] = False
        for item in results:
            print(("PASS " if item["success"] else "FAIL ") + item["name"])
        if not catalog_unchanged:
            print("FAIL CATALOG INPUTS MUTATED", file=sys.stderr)
        if a.report:
            publish_report(a.report, dict(backend=a.backend,
                compiler_revision=a.compiler_revision,
                provenance="caller-supplied labels; verify separately",
                revision_format_verified=a.require_revision,
                allow_stderr=a.allow_stderr,
                mode=a.mode, selected=len(cases), inventory_total=len(all_cases),
                complete_catalog=len(cases)==len(all_cases),
                catalog_inputs_unchanged=catalog_unchanged,
                output_oracle_matched=a.mode=="run" and catalog_unchanged
                    and all(item["success"] for item in results),
                results=results))
        return 0 if catalog_unchanged and all(item["success"] for item in results) else 1
    except (ValueError, OSError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
