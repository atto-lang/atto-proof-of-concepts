"""Contract regressions for catalog structure; no Oreslang execution."""
from pathlib import Path
import sys
import tempfile
import unittest
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

if __name__ == "__main__":
    unittest.main()
