#!/usr/bin/env python3
"""Git blob identity checks for pattern fixtures; NOT compiler/runtime tests."""
import hashlib
import json
from pathlib import Path
import re
import sys

PATH_RE = re.compile(r"^src/patterns/([0-9]{2})-[a-z0-9-]+/(example\.ores|expected\.stdout)$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verify(root: Path, manifest_path: Path, require_full: bool = True) -> list[str]:
    errors = []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"cannot read manifest: {exc}"]
    if not isinstance(data, dict) or set(data) != {"source_commit", "files"}:
        return ["manifest must contain exactly source_commit and files"]
    if not isinstance(data["source_commit"], str) or not SHA_RE.fullmatch(data["source_commit"]):
        errors.append("invalid source_commit SHA")
    pinned = data["files"]
    if not isinstance(pinned, dict):
        return errors + ["files must be a path-to-git-sha object"]
    actual = set()
    for folder in (root / "src/patterns").glob("[0-9][0-9]-*"):
        if not folder.is_dir():
            continue
        for name in ("example.ores", "expected.stdout"):
            if (folder / name).exists() or (folder / name).is_symlink():
                actual.add((folder / name).relative_to(root).as_posix())
    expected = set(pinned)
    for path in sorted(actual - expected):
        errors.append(f"unpinned pattern file: {path}")
    for path in sorted(expected - actual):
        errors.append(f"pinned file missing: {path}")
    for path, sha in sorted(pinned.items()):
        match = PATH_RE.fullmatch(path)
        if match is None or not isinstance(sha, str) or SHA_RE.fullmatch(sha) is None:
            errors.append(f"invalid manifest path or digest: {path}")
            continue
        candidate = root / path
        if candidate.is_symlink():
            errors.append(f"symlink is forbidden: {path}")
            continue
        if not candidate.is_file():
            continue
        if git_blob_sha(candidate.read_bytes()) != sha:
            errors.append(f"Git blob SHA mismatch: {path}")
    if require_full:
        if len(pinned) != 140:
            errors.append(f"expected 140 pinned source/oracle files, found {len(pinned)}")
        for i in range(1, 71):
            prefix = f"src/patterns/{i:02d}-"
            for filename in ("example.ores", "expected.stdout"):
                if len([p for p in pinned if p.startswith(prefix) and p.endswith("/" + filename)]) != 1:
                    errors.append(f"missing/duplicate pattern {i:02d} {filename}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    manifest = Path(__file__).with_name("pinned_blobs.json")
    issues = verify(root, manifest)
    for issue in issues:
        print("FAIL " + issue, file=sys.stderr)
    if issues:
        return 1
    print("Verified 140 pinned Git blobs (70 sources + 70 oracles); no compiler executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
