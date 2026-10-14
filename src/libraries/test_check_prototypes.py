"""Contract regressions for catalog structure; no Oreslang execution."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import shlex
import contextlib
import io
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_prototypes as subject

def fixture(root, name="oreslang-testkit", oracle=None, source=None):
    directory = root / name
    directory.mkdir()
    (directory / "example.ores").write_text(source if source is not None else
        'pub routine main(): void { stdio.stdout.println("FAIL:'+name+':1"); stdio.stdout.println("PASS:'+name+'"); }')
    (directory / "expected.stdout").write_text(oracle if oracle is not None else "PASS:"+name+"\n")
    return directory

class PrototypeInventoryTests(unittest.TestCase):
    def test_actual_inventory_exactly_pinned(self):
        cases = subject.inventory()
        self.assertEqual({name for name, *_ in cases}, subject.EXPECTED_NAMES)
    def test_temporary_valid_pair(self):
        with tempfile.TemporaryDirectory() as path:
            fixture(Path(path))
            self.assertEqual(len(subject.inventory(Path(path))), 1)
    def test_reject_wrong_output(self):
        with tempfile.TemporaryDirectory() as path:
            fixture(Path(path), oracle="PASS:another\n")
            with self.assertRaises(ValueError):
                subject.inventory(Path(path))
    def test_reject_missing_oracle(self):
        with tempfile.TemporaryDirectory() as path:
            d = fixture(Path(path))
            (d / "expected.stdout").unlink()
            with self.assertRaises(ValueError):
                subject.inventory(Path(path))
    def test_reject_unbalanced_source(self):
        with tempfile.TemporaryDirectory() as path:
            fixture(Path(path), source='pub routine main(): void { stdio.stdout.println("PASS:oreslang-testkit"); stdio.stdout.println("FAIL:oreslang-testkit:1");')
            with self.assertRaises(ValueError):
                subject.inventory(Path(path))
    def test_hash_changes_on_mutation(self):
        with tempfile.TemporaryDirectory() as path:
            p = fixture(Path(path)) / "example.ores"
            original = subject.digest(p)
            p.write_text(p.read_text() + "\n// mutation")
            self.assertNotEqual(original, subject.digest(p))


    def test_reject_c_style_boolean_syntax(self):
        with tempfile.TemporaryDirectory() as path:
            d = fixture(Path(path))
            p = d / "example.ores"
            p.write_text(p.read_text() + "\nfnc broken(): bool { return true && false; }")
            with self.assertRaisesRegex(ValueError, "lexical hygiene"):
                subject.inventory(Path(path))
    def test_reject_symlink_oracle(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            d = fixture(root)
            target = root / "external.txt"
            target.write_text("PASS:oreslang-testkit\\n")
            (d / "expected.stdout").unlink()
            (d / "expected.stdout").symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symlink"):
                subject.inventory(root)
    def test_reject_symlink_library_directory(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            outside = root / "other"
            outside.mkdir()
            (root / "oreslang-evil").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                subject.inventory(root)
    def test_reject_missing_actual_pass_print(self):
        with tempfile.TemporaryDirectory() as path:
            d = fixture(Path(path))
            p = d / "example.ores"
            p.write_text(p.read_text().replace("stdio.stdout.println", "stdout.fake_print"))
            with self.assertRaisesRegex(ValueError, "missing PASS print"):
                subject.inventory(Path(path))
    def test_reject_unterminated_comment(self):
        with tempfile.TemporaryDirectory() as path:
            d = fixture(Path(path))
            p = d / "example.ores"
            p.write_text(p.read_text() + "\n/* unclosed")
            with self.assertRaisesRegex(ValueError, "lexical hygiene"):
                subject.inventory(Path(path))

    def test_runner_accepts_exact_stdout_and_rejects_different_output(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            case = fixture(root)
            script = root / "runner.py"
            script.write_text('import sys\\nfrom pathlib import Path\\nprint("PASS:" + Path(sys.argv[1]).parent.name)\\n')
            selected = subject.inventory(root)
            command = f"{shlex.quote(sys.executable)} {shlex.quote(str(script))} {{source}}"
            argv = ["runner", "--runner-command", command]
            with patch.object(subject, "inventory", return_value=selected), patch.object(sys, "argv", argv):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(subject.main(), 0)
            script.write_text('print("INCORRECT")\\n')
            with patch.object(subject, "inventory", return_value=selected), patch.object(sys, "argv", argv):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(subject.main(), 1)

    def test_compile_mode_is_not_stdout_verification(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            fixture(root)
            script = root / "check.py"
            script.write_text('print("compiler accepted")\\n')
            command = f"{shlex.quote(sys.executable)} {shlex.quote(str(script))} {{source}}"
            argv = ["runner", "--runner-command", command, "--mode", "compile"]
            with patch.object(subject, "inventory", return_value=subject.inventory(root)), patch.object(sys, "argv", argv):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(subject.main(), 0)

    def test_filter_empty_selection_fails_closed(self):
        with tempfile.TemporaryDirectory() as path:
            fixture(Path(path))
            argv = ["runner", "--list", "--filter", "does-not-exist"]
            with patch.object(subject, "inventory", return_value=subject.inventory(Path(path))), patch.object(sys, "argv", argv):
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(subject.main(), 2)

    def test_execution_rejects_mutated_source(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            folder = fixture(root)
            script = root / "mutator.py"
            script.write_text('import sys\\nfrom pathlib import Path\\np=Path(sys.argv[1])\\np.write_text(p.read_text()+"\\\\n// changed")\\nprint("PASS:"+p.parent.name)\\n')
            command = f"{shlex.quote(sys.executable)} {shlex.quote(str(script))} {{source}}"
            argv = ["runner", "--runner-command", command]
            with patch.object(subject, "inventory", return_value=subject.inventory(root)), patch.object(sys, "argv", argv):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(subject.main(), 1)

if __name__ == "__main__":
    unittest.main()
