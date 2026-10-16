#!/usr/bin/env python3
"""Validate the catalog layout only; no compiler/runtime claim."""
from pathlib import Path
import re
src = Path(__file__).resolve().parents[1]
libraries = sorted(d for d in (src / "libraries").iterdir() if d.is_dir() and d.name.startswith("oreslang-"))
patterns = sorted(d for d in (src / "patterns").iterdir() if d.is_dir() and re.match(r"^[0-9][0-9]-", d.name))
assert len(libraries) == 60, f"Expected 60 library briefs, found {len(libraries)}"
assert len(patterns) >= 70, f"Expected at least 70 pattern briefs, found {len(patterns)}"
assert [int(p.name[:2]) for p in patterns] == list(range(1, len(patterns) + 1))
for p in libraries + patterns:
    body = (p / "README.md").read_text(encoding="utf-8")
    assert "Status:" in body and "##" in body, p
for name in ["README.md", "libraries/README.md", "patterns/README.md", "validation/README.md"]:
    assert (src / name).is_file(), name
print(f"Catalog layout verified: 60 libraries and {len(patterns)} patterns; no compiled result implied")
