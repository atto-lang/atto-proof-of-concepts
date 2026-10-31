#!/usr/bin/env python3
"""Fail-closed structural catalog gate; no compiler/runtime qualification."""
from pathlib import Path
import re
import sys


def validate_catalog(src: Path, expected_libraries: int = 60,
                     expected_patterns: int = 90) -> tuple[int, int]:
    """Check exact inventory, directory/file type and linked README contracts."""
    libs_dir, patterns_dir = src / "libraries", src / "patterns"
    for directory in (libs_dir, patterns_dir):
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"missing or symlinked catalog root: {directory}")
    libs = []
    for entry in sorted(libs_dir.iterdir()):
        if not entry.name.startswith("oreslang-"):
            continue
        if entry.is_symlink() or not entry.is_dir():
            raise ValueError(f"invalid or symlinked library directory: {entry}")
        libs.append(entry)
    patterns = []
    for entry in sorted(patterns_dir.iterdir()):
        if not re.match(r"^[0-9]{2}-", entry.name):
            continue
        if entry.is_symlink() or not entry.is_dir():
            raise ValueError(f"invalid or symlinked pattern directory: {entry}")
        patterns.append(entry)
    if len(libs) != expected_libraries:
        raise ValueError(f"expected {expected_libraries} libraries; found {len(libs)}")
    if len(patterns) != expected_patterns:
        raise ValueError(f"expected {expected_patterns} patterns; found {len(patterns)}")
    numbers = sorted(int(p.name[:2]) for p in patterns)
    if numbers != list(range(1, expected_patterns + 1)):
        raise ValueError(f"missing/duplicate/out-of-order pattern numbers: {numbers}")
    for directory in libs + patterns:
        readme = directory / "README.md"
        if readme.is_symlink() or not readme.is_file():
            raise ValueError(f"missing or symlinked README: {readme}")
        body = readme.read_text(encoding="utf-8")
        if "Status:" not in body or "##" not in body:
            raise ValueError(f"missing catalog status/heading: {readme}")
    for relative in ("README.md", "libraries/README.md",
                     "patterns/README.md", "validation/README.md"):
        required = src / relative
        if required.is_symlink() or not required.is_file():
            raise ValueError(f"missing or symlinked catalog reference: {required}")
    return len(libs), len(patterns)


def main() -> int:
    try:
        libraries, patterns = validate_catalog(Path(__file__).resolve().parents[1])
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"FAIL catalog integrity: {exc}", file=sys.stderr)
        return 1
    print(f"Catalog layout verified: {libraries} libraries and {patterns} patterns; "
          "NO compiler/runtime qualification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
