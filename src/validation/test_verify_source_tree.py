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
        (self.mirror / ".gitignore").write_text("target/\n*.cache\n")
        (self.root / "outside.txt").write_text("CI wrapper not part of source tree\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "fixture")
        self.tree = git(self.root, "rev-parse", "HEAD:mirror")
        self.root_tree = git(self.root, "rev-parse", "HEAD^{tree}")

    def verify(self, expected=None, directory=None, option=None):
        argv = ["bash", str(VERIFY), str(directory or self.mirror),
                expected or self.tree]
        if option is not None:
            argv.append(option)
        return subprocess.run(argv, text=True, capture_output=True, check=False)

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

    def test_ignored_source_contamination_rejected(self):
        (self.mirror / "hidden.cache").write_text("injected\n")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ignored source", result.stderr)

    def test_index_staged_blob_must_match_head_even_when_worktree_matches_index(self):
        path = self.mirror / "example.txt"
        path.write_text("changed\n")
        git(self.root, "add", "mirror/example.txt")
        git(self.root, "update-index", "--skip-worktree", "mirror/example.txt")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stderr, "tracked source differs|Git index differs")

    def test_missing_index_entry_cannot_look_like_complete_tree(self):
        git(self.root, "rm", "--cached", "-q", "mirror/example.txt")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)

    def test_assume_unchanged_cannot_hide_mutation(self):
        git(self.root, "update-index", "--assume-unchanged", "mirror/example.txt")
        (self.mirror / "example.txt").write_text("hidden mutation\n")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source blob", result.stderr)

    def test_skip_worktree_cannot_hide_mutation(self):
        git(self.root, "update-index", "--skip-worktree", "mirror/example.txt")
        (self.mirror / "example.txt").write_text("hidden mutation\n")
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source blob", result.stderr)

    def test_symlinked_source_rejected_even_with_identical_bytes(self):
        outside = self.root / "copy.txt"
        outside.write_text("original\n")
        (self.mirror / "example.txt").unlink()
        (self.mirror / "example.txt").symlink_to(outside)
        result = self.verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertRegex(result.stderr, "symlink|tracked source differs")

    def test_executable_mode_change_rejected(self):
        (self.mirror / "example.txt").chmod(0o755)
        self.assertNotEqual(self.verify().returncode, 0)

    def test_target_ignored_without_allowance_rejected(self):
        target = self.mirror / "target"
        target.mkdir()
        (target / "classes.class").write_text("generated\n")
        self.assertNotEqual(self.verify().returncode, 0)

    def test_target_allowance_after_build_only(self):
        target = self.mirror / "target"
        target.mkdir()
        (target / "classes.class").write_text("generated\n")
        self.assertEqual(self.verify(None, None, "--allow-generated-target").returncode, 0)

    def test_target_allowance_does_not_allow_other_ignored_content(self):
        target = self.mirror / "target"
        target.mkdir()
        (target / "classes.class").write_text("generated\n")
        (self.mirror / "hidden.cache").write_text("injected\n")
        self.assertNotEqual(self.verify(None, None, "--allow-generated-target").returncode, 0)

    def test_target_allowance_rejects_untracked_normal_file(self):
        target = self.mirror / "target"
        target.mkdir()
        (target / "classes.class").write_text("generated\n")
        (self.mirror / "untracked.txt").write_text("unexpected\n")
        self.assertNotEqual(self.verify(None, None, "--allow-generated-target").returncode, 0)

    def test_invalid_allowance_argument_rejected(self):
        self.assertEqual(self.verify(None, None, "--ignore-everything").returncode, 2)


if __name__ == "__main__":
    unittest.main()
