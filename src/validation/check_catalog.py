#!/usr/bin/env python3
"""Fail-closed structural catalog gate; no compiler/runtime qualification."""
from pathlib import Path
import re
import sys


def _require_fixture(path: Path) -> None:
    """Reject missing, directory, symlink and dangling-link fixture aliases."""
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"missing, symlinked or non-regular catalog fixture: {path}")


def validate_catalog(src: Path, expected_libraries: int = 60,
                     expected_patterns: int = 90,
                     expected_library_probes: int = 32) -> tuple[int, int]:
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
    # Library briefs are allowed without a runnable example, but a partial
    # example/oracle pair must never be silently excluded from qualification.
    library_probes = 0
    for directory in libs:
        source = directory / "example.ores"
        oracle = directory / "expected.stdout"
        if any(path.exists() or path.is_symlink() for path in (source, oracle)):
            _require_fixture(source)
            _require_fixture(oracle)
            if not source.read_text(encoding="utf-8").strip():
                raise ValueError(f"empty library source: {source}")
            if oracle.read_bytes() != f"PASS:{directory.name}\\n".encode("utf-8"):
                raise ValueError(f"invalid library output oracle: {oracle}")
            library_probes += 1
    if library_probes != expected_library_probes:
        raise ValueError(f"expected {expected_library_probes} library probes; found {library_probes}")
    # Every numbered pattern is executable: directory counts alone are not a
    # trustworthy catalog gate without a paired source and exact oracle.
    for directory in patterns:
        source = directory / "example.ores"
        oracle = directory / "expected.stdout"
        _require_fixture(source)
        _require_fixture(oracle)
        if not source.read_text(encoding="utf-8").strip():
            raise ValueError(f"empty pattern source: {source}")
        if oracle.read_bytes() != f"PASS:{int(directory.name[:2])}\\n".encode("utf-8"):
            raise ValueError(f"invalid pattern output oracle: {oracle}")
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
