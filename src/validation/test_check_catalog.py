"""Adversarial structural catalog tests; no Oreslang guest compiler is used."""
import tempfile
from pathlib import Path
import unittest

from check_catalog import validate_catalog


def fixture(root: Path):
    for child in ("libraries", "patterns", "validation"):
        (root / child).mkdir()
    (root / "README.md").write_text("# Catalog\n", encoding="utf-8")
    for area in ("libraries", "patterns", "validation"):
        (root / area / "README.md").write_text("# Index\n", encoding="utf-8")
    for name in ("oreslang-a", "oreslang-b"):
        d = root / "libraries" / name
        d.mkdir()
        (d / "README.md").write_text("## Status: planned\n", encoding="utf-8")
    for name in ("01-alpha", "02-beta"):
        d = root / "patterns" / name
        d.mkdir()
        (d / "README.md").write_text("## Status: prototype\n", encoding="utf-8")


class CatalogContractTests(unittest.TestCase):
    def test_exact_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            self.assertEqual(validate_catalog(root, 2, 2), (2, 2))

    def test_missing_and_extra_entries_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            self.assertRaisesRegex(ValueError, "expected 3 libraries",
                                   validate_catalog, root, 3, 2)
            (root / "patterns" / "03-gamma").mkdir()
            self.assertRaisesRegex(ValueError, "expected 2 patterns",
                                   validate_catalog, root, 2, 2)

    def test_number_gap_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            (root / "patterns" / "02-beta").rename(root / "patterns" / "03-beta")
            self.assertRaisesRegex(ValueError, "pattern numbers",
                                   validate_catalog, root, 2, 2)

    def test_symlinked_library_or_pattern_directory_fails(self):
        for area, name in (("libraries", "oreslang-a"), ("patterns", "01-alpha")):
            with self.subTest(area=area), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                fixture(root)
                moved = root / "real-entry"
                entry = root / area / name
                entry.rename(moved)
                entry.symlink_to(moved, target_is_directory=True)
                self.assertRaisesRegex(ValueError, "symlinked",
                                       validate_catalog, root, 2, 2)

    def test_symlinked_readme_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            readme = root / "libraries" / "oreslang-a" / "README.md"
            real = root / "actual-readme"
            readme.rename(real)
            readme.symlink_to(real)
            self.assertRaisesRegex(ValueError, "symlinked README",
                                   validate_catalog, root, 2, 2)

    def test_missing_required_index_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            (root / "validation" / "README.md").unlink()
            self.assertRaisesRegex(ValueError, "catalog reference",
                                   validate_catalog, root, 2, 2)


if __name__ == "__main__":
    unittest.main()
