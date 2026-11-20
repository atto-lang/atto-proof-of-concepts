import unittest
from tip_syntax_hygiene import code_only, violations


class SyntaxHygieneTests(unittest.TestCase):
    def test_canonical_if_and_boolean_intrinsic(self):
        src = 'pub routine main(): void { if a, b then return; fi return And(a, b); }'
        self.assertEqual(violations(src), [])

    def test_zero_argument_closure_is_not_boolean_or(self):
        self.assertEqual(violations("fnc factory() { val f = || -> { return 1; }; }"), [])

    def test_invalid_c_style_boolean(self):
        self.assertTrue(violations('if a && b then return; fi'))
        self.assertTrue(violations('return x || y;'))

    def test_comments_and_strings_are_not_source_tokens(self):
        src = '// && \n /* || /* && */ || */ fnc x(): int { return 1; }'
        self.assertEqual(violations(src), [])
        self.assertNotIn('&&', code_only(src))
        self.assertEqual(violations('stdio.println("&& ||");'), [])

    def test_deprecated_conditional(self):
        self.assertTrue(violations('if true; do return; fi'))

    def test_old_actor_spelling(self):
        self.assertTrue(violations('isoactor Old { }'))

    def test_misnamed_async_io(self):
        self.assertTrue(violations('pub async fnc read_blocking(int fd): int { return fd; }'))

    def test_executable_fat_arrow(self):
        self.assertTrue(violations('fnc f(int x) => int { return x; }'))

    def test_unterminated_comment(self):
        with self.assertRaises(ValueError):
            code_only('fnc x() { /* broken')


if __name__ == "__main__":
    unittest.main()
