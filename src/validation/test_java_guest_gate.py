"""Preflight checks for Java guest gate; these do NOT execute Oreslang."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

GATE = Path(__file__).with_name("run_java_guest_gate.sh")
VERIFY = Path(__file__).with_name("verify_source_tree.sh")


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


class JavaGuestGatePreflightTests(unittest.TestCase):
    def setUp(self):
        if any(shutil.which(binary) is None for binary in ("bash", "git", "realpath")):
            self.skipTest("bash, git, and realpath required")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.poc = root / "poc"
        self.java = root / "java"
        self.poc.mkdir()
        self.java.mkdir()
        for directory in (self.poc, self.java):
            git(directory, "init", "-q")
            git(directory, "config", "user.name", "tester")
            git(directory, "config", "user.email", "tester@example.invalid")
        target = self.poc / "src" / "validation"
        target.mkdir(parents=True)
        shutil.copy2(GATE, target / "run_java_guest_gate.sh")
        shutil.copy2(VERIFY, target / "verify_source_tree.sh")
        (target / "verify_source_tree.sh").chmod(0o755)
        (target / "run_java_guest_gate.sh").chmod(0o755)
        (self.poc / "src" / "libraries").mkdir(parents=True)
        (self.poc / "src" / "libraries" / "check_prototypes.py").write_text("# fixture\n")
        (self.java / ".gitignore").write_text("target/\n")
        (self.java / "pom.xml").write_text("<project/>\n")
        for directory in (self.poc, self.java):
            git(directory, "add", ".")
            git(directory, "commit", "-qm", "fixture")
        self.ptree = git(self.poc, "rev-parse", "HEAD^{tree}")
        self.jtree = git(self.java, "rev-parse", "HEAD^{tree}")

    def run_gate(self, destination):
        return subprocess.run(
            ["bash", str(self.poc / "src" / "validation" / "run_java_guest_gate.sh"),
             str(self.java), self.jtree, self.ptree, "a" * 40, str(destination)],
            capture_output=True, text=True, check=False)

    def test_evidence_inside_poc_rejected_before_creation(self):
        dest = self.poc / "generated" / "evidence"
        result = self.run_gate(dest)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("outside protected source trees", result.stderr)
        self.assertFalse(dest.exists())

    def test_evidence_inside_java_rejected_before_creation(self):
        dest = self.java / "generated" / "evidence"
        result = self.run_gate(dest)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("outside protected source trees", result.stderr)
        self.assertFalse(dest.exists())

    def test_symlinked_evidence_into_java_rejected(self):
        link = self.poc.parent / "java-evidence-link"
        link.symlink_to(self.java, target_is_directory=True)
        dest = link / "nested"
        result = self.run_gate(dest)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(dest.exists())

    def test_nonempty_evidence_directory_rejected_before_build(self):
        dest = self.poc.parent / "external-evidence"
        dest.mkdir()
        (dest / "java-runtime.json").write_text('{"faked":true}\n')
        result = self.run_gate(dest)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("evidence directory must be empty", result.stderr)
        self.assertEqual((dest / "java-runtime.json").read_text(), '{"faked":true}\n')

    def test_linked_worktree_git_metadata_is_not_an_evidence_destination(self):
        # The actual Git database lives outside this linked worktree's source
        # root, as in a mirror hosted inside a larger CI repository.
        linked = self.poc.parent / "linked-poc"
        git(self.poc, "worktree", "add", "-q", "-b", "linked-validation", str(linked))
        git_dir = Path(git(linked, "rev-parse", "--absolute-git-dir"))
        dest = git_dir / "evidence"
        result = subprocess.run(
            ["bash", str(linked / "src" / "validation" / "run_java_guest_gate.sh"),
             str(self.java), self.jtree, self.ptree, "a" * 40, str(dest)],
            capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("outside Git metadata", result.stderr)
        self.assertFalse(dest.exists())

    def test_wrong_tree_rejected_before_creating_evidence(self):
        dest = self.poc.parent / "external-evidence"
        result = subprocess.run(
            ["bash", str(self.poc / "src" / "validation" / "run_java_guest_gate.sh"),
             str(self.java), self.jtree, "0" * 40, "a" * 40, str(dest)],
            capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(dest.exists())


if __name__ == "__main__":
    unittest.main()
