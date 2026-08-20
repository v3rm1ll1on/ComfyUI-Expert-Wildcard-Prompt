import unittest
import random
from prompt_parser import parse_prompt_to_ast, resolve_ast_to_prompt, combine_negative_prompts, check_prompt_syntax

class TestPromptParser(unittest.TestCase):
    def test_wildcards_and_percentages(self):
        text = "{100% blue shirt | 0% red shirt}"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "blue shirt")
        self.assertEqual(neg, "")

    def test_negative_prefix_extraction(self):
        text = "masterpiece, -blurry, -bad hands, leather jacket"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, leather jacket")
        self.assertEqual(neg, "blurry, bad hands")

    def test_negative_placeholder_injection(self):
        extracted = "umbrella, coat"
        base_neg = "(3d render:1.3), $negative, (deformed hands:1.2)"
        res = combine_negative_prompts(extracted, base_neg, "prepend", random.Random(42))
        self.assertEqual(res, "(3d render:1.3), umbrella, coat, (deformed hands:1.2)")

    def test_negative_modes_without_placeholder(self):
        extracted = "umbrella, coat"
        base_neg = "3d render, cgi"

        res_prepend = combine_negative_prompts(extracted, base_neg, "prepend", random.Random(42))
        self.assertEqual(res_prepend, "umbrella, coat, 3d render, cgi")

        res_append = combine_negative_prompts(extracted, base_neg, "append", random.Random(42))
        self.assertEqual(res_append, "3d render, cgi, umbrella, coat")

        res_replace = combine_negative_prompts(extracted, base_neg, "replace", random.Random(42))
        self.assertEqual(res_replace, "umbrella, coat")

    def test_syntax_check(self):
        res1 = check_prompt_syntax("valid {wildcard | option}")
        self.assertTrue(res1.is_valid)

        res2 = check_prompt_syntax("invalid {wildcard | option")
        self.assertFalse(res2.is_valid)

if __name__ == '__main__':
    unittest.main()
