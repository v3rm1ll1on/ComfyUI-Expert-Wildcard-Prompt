import unittest
import random
from prompt_parser import parse_prompt_to_ast, resolve_ast_to_prompt, check_prompt_syntax

class TestPromptParser(unittest.TestCase):
    def test_wildcards_and_percentages(self):
        text = "{100% blue shirt | 0% red shirt}"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "blue shirt")
        self.assertEqual(neg, "")

    def test_skip_chance(self):
        text = "{100%? optional tag}"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "")

    def test_mute_and_solo(self):
        text = "normal tag, // muted tag, ! solo tag"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "solo tag")

    def test_negative_prefix(self):
        text = "masterpiece, -blurry, -bad hands, leather jacket"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, leather jacket")
        self.assertEqual(neg, "blurry, bad hands")

    def test_negative_inside_wildcard(self):
        text = "a photo, {100% sunny day | 0% rainy day, -umbrella}"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "a photo, sunny day")
        self.assertEqual(neg, "")

    def test_syntax_check(self):
        res1 = check_prompt_syntax("valid {wildcard | option}")
        self.assertTrue(res1.is_valid)

        res2 = check_prompt_syntax("invalid {wildcard | option")
        self.assertFalse(res2.is_valid)

if __name__ == '__main__':
    unittest.main()
