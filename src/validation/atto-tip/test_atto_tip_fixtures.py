"""Source-only AttoLang tip contract: Git blob identity, never compiler evidence."""
import hashlib
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
# SHA-1 Git blob IDs copied from Java main 6d8eb70048eafc9a84c5aebe9c1bb06104f16e76.
EXPECTED = {
    "positive/canonical-add.atto": "015f8b0f79aafa796a148d2adeff1574e8d6c491",
    "positive/type-first-readonly.atto": "75ff4afc98fc65a774611eb7686e893f3d28a6da",
    "positive/pure-call.atto": "e5ab32f7d8f684d655a83a3df989f16c52090c05",
    "negative/type-first-reassignment.atto": "b118f53e68565dcb9e6acd58deb8ee47dca67606",
    "negative/removed-modulo.atto": "45d5794870e93074d9b11b90833a849e96aaa4c1",
}

class TipFixtureContract(unittest.TestCase):
    def test_exact_upstream_git_blob_identity(self):
        for name, expected in EXPECTED.items():
            with self.subTest(name=name):
                file = HERE / name
                self.assertFalse(file.is_symlink())
                self.assertTrue(file.is_file())
                payload = file.read_bytes()
                preimage = f"blob {len(payload)}".encode("ascii") + bytes([0]) + payload
                self.assertEqual(hashlib.sha1(preimage).hexdigest(), expected)

    def test_no_legacy_extension_or_extra_fixtures(self):
        actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob("*.atto")}
        self.assertEqual(actual, set(EXPECTED))
        self.assertEqual(list(HERE.rglob("*.ores")), [])

if __name__ == "__main__":
    unittest.main()
