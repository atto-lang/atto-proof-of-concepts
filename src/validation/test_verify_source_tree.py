"""Real local Git adversarial tests for the exact-source gate, not Oreslang CI."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

VERIFY = Path(__file__).with_name("verify_source_tree.sh")


def git(directory, *args):
    p = subprocess.run(["git", "-C", str(directory), *args], text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return p.stdout.strip()


class ExactSourceTreeTests(unittest.TestCase):
    def setUp(self):
        if shutil.which("git") is None or shutil.which("bash") is None:
            self.skipTest("git and bash required")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "fixture")
        git(self.root, "config", "user.email", "fixture@example.invalid")
        self.mirror = self.root / "mirror"
        self.mirror.mkdir()
        (self.mirror / "example.txt").write_text("original\n")
        (self.root / "outside.txt").write_text("CI wrapper not part of source tree\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "fixture")
        self.tree = git(self.root, "rev-parse", "HEAD:mirror")
        self.root_tree = git(self.root, "rev-parse", "HEAD^{tree}")

    def verify(self, expected=None, directory=None):
        return subprocess.run(["bash", str(VERIFY), str(directory or self.mirror),
                               expected or self.tree], text=True,
                              capture_output=True, check=False)

    def test_subtree_match_succeeds_with_ci_files_outside(self):
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SOURCE_TREE_VERIFIED", result.stdout)

    def test_repo_root_match_succeeds(self):
        self.assertEqual(self.verify(self.root_tree, self.root).returncode, 0)

    def test_wrong_tree_fails_closed(self):
        result = self.verify("0" * 40)
        self.assertEqual(result.returncode, 1)
        self.assertIn("source tree mismatch", result.stderr)

    def test_invalid_hash_rejected(self):
        self.assertEqual(self.verify("bad").returncode, 2)

    def test_tracked_mutation_rejected(self):
        (self.mirror / "example.txt").write_text("different\n")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tracked source differs", result.stderr)

    def test_staged_mutation_rejected(self):
        (self.mirror / "example.txt").write_text("different\n")
        git(self.root, "add", "mirror/example.txt")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)

    def test_untracked_source_file_rejected(self):
        (self.mirror / "additional.txt").write_text("unexpected\n")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("untracked source", result.stderr)

    def test_missing_subtree_rejected(self):
        child = self.mirror / "untracked-subdirectory"
        child.mkdir()
        result = self.verify(directory=child)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
