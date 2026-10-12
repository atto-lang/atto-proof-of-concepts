"""Tests of Git-blob fixture verification. These do not compile Oreslang."""
import json
from pathlib import Path
import tempfile
import unittest
from verify_blob_manifest import git_blob_sha, verify


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.dir = self.root / "src/patterns/01-demo"
        self.dir.mkdir(parents=True)
        self.src = self.dir / "example.ores"
        self.oracle = self.dir / "expected.stdout"
        self.src.write_text('pub routine main(): void {}\n')
        self.oracle.write_text('PASS:1\n')
        self.manifest = self.root / "pinned_blobs.json"
        self.write_manifest()

    def write_manifest(self):
        paths = [self.src, self.oracle]
        self.manifest.write_text(json.dumps({
            "source_commit": "0" * 40,
            "files": {p.relative_to(self.root).as_posix(): git_blob_sha(p.read_bytes()) for p in paths}
        }))

    def test_matching_files_pass(self):
        self.assertEqual(verify(self.root, self.manifest, require_full=False), [])

    def test_mutated_source_fails(self):
        self.src.write_text("changed\n")
        self.assertTrue(any("SHA mismatch" in e for e in verify(self.root, self.manifest, False)))

    def test_missing_oracle_fails(self):
        self.oracle.unlink()
        self.assertTrue(any("missing" in e for e in verify(self.root, self.manifest, False)))

    def test_new_unpinned_file_fails(self):
        extra = self.root / "src/patterns/02-extra"
        extra.mkdir()
        (extra / "example.ores").write_text("new\n")
        self.assertTrue(any("unpinned" in e for e in verify(self.root, self.manifest, False)))

    def test_full_catalog_requires_140_blobs(self):
        self.assertTrue(any("140 pinned" in e for e in verify(self.root, self.manifest, True)))

    def test_invalid_digest_fails(self):
        manifest = json.loads(self.manifest.read_text())
        key = next(iter(manifest["files"]))
        manifest["files"][key] = "not-a-sha"
        self.manifest.write_text(json.dumps(manifest))
        self.assertTrue(any("invalid manifest" in e for e in verify(self.root, self.manifest, False)))


if __name__ == "__main__":
    unittest.main()
