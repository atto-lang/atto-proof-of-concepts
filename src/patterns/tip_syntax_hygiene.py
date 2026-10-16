#!/usr/bin/env python3
"""Conservative syntax-hygiene guards derived from the pinned Java grammar.

This is NOT the Oreslang parser, semantic checker, or LLVM compiler.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent


def code_only(source: str) -> str:
    """Remove strings and nested comments while retaining positions/newlines."""
    out = []
    i = 0
    depth = 0
    quoted = False
    while i < len(source):
        c = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        if quoted:
            if c == "\\" and nxt:
                out.extend((" ", " "))
                i += 2
                continue
            if c == '"':
                quoted = False
            out.append("\n" if c == "\n" else " ")
            i += 1
            continue
        if depth:
            if c == "/" and nxt == "*":
                depth += 1
                out.extend((" ", " "))
                i += 2
                continue
            if c == "*" and nxt == "/":
                depth -= 1
                out.extend((" ", " "))
                i += 2
                continue
            out.append("\n" if c == "\n" else " ")
            i += 1
            continue
        if c == "/" and nxt == "/":
            end = source.find("\n", i)
            if end == -1:
                out.extend(" " * (len(source) - i))
                break
            out.extend(" " * (end - i))
            i = end
            continue
        if c == "/" and nxt == "*":
            depth = 1
            out.extend((" ", " "))
            i += 2
            continue
        if c == '"':
            quoted = True
            out.append(" ")
            i += 1
            continue
        out.append(c)
        i += 1
    if depth or quoted:
        raise ValueError("unterminated block comment or string")
    return "".join(out)


def violations(source: str) -> list[str]:
    stripped = code_only(source)
    errors = []
    if "&&" in stripped or re.search(r"\|\|(?!\s*->)", stripped):
        errors.append("C-style &&/|| used; use condition comma/pipe or And()/Or()")
    if re.search(r"^\s*(?:if|elseif|elif)\b[^\n]*;\s*do\b", stripped, re.M):
        errors.append("deprecated conditional '; do'; canonical spelling is 'then'")
    if re.search(r"\bisoactor\b", stripped):
        errors.append("legacy isoactor spelling; use canonical private 'actor'")
    if re.search(r"\basync\s+fnc\s+\w+_blocking\s*\(", stripped):
        errors.append("async function misleadingly uses synchronous-looking _blocking suffix")
    if re.search(r"\b(?:fnc|routine)\s+\w+\([^;\n]*\)\s*=>", stripped):
        errors.append("executable function uses type-only => instead of : or ->")
    return errors


def main() -> int:
    folders = sorted(p for p in ROOT.iterdir() if p.is_dir() and re.match(r"^[0-9]{2}-", p.name))
    if len(folders) != 80:
        print(f"expected 80 folders, found {len(folders)}", file=sys.stderr)
        return 1
    failures = []
    for folder in folders:
        source_path = folder / "example.ores"
        golden = folder / "expected.stdout"
        if not source_path.is_file() or not golden.is_file():
            failures.append(f"{folder.name}: missing example.ores or expected.stdout")
            continue
        number = int(folder.name[:2])
        body = source_path.read_text(encoding="utf-8")
        try:
            errors = violations(body)
        except ValueError as exc:
            errors = [str(exc)]
        if golden.read_text(encoding="utf-8") != f"PASS:{number}\n":
            errors.append("expected.stdout is not the numbered PASS oracle")
        if len(re.findall(r"\bpub\s+(?:async\s+)?routine\s+main\s*\(", code_only(body))) != 1:
            errors.append("expected one public main routine")
        if f"FAIL:{number}:" not in body:
            errors.append("expected explicit FAIL marker")
        failures.extend(f"{folder.name}: {error}" for error in errors)
    for failure in failures:
        print(f"FAIL {failure}", file=sys.stderr)
    if failures:
        return 1
    print("80 pattern sources passed grammar-aligned hygiene checks (NOT compilation)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
