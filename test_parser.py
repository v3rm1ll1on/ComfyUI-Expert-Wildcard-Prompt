import unittest
import random
from prompt_parser import parse_prompt_to_ast, resolve_ast_to_prompt

class TestPromptParser(unittest.TestCase):
    def test_wildcards_and_percentages(self):
        text = "{100% blue shirt | 0% red shirt}"
        ast = parse_prompt_to_ast(text)
        prompt = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(prompt, "blue shirt")

    def test_skip_chance(self):
        text = "{100%? optional tag}"
        ast = parse_prompt_to_ast(text)
        prompt = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(prompt, "")

    def test_mute_and_solo(self):
        text = "normal tag, // muted tag, ! solo tag"
        ast = parse_prompt_to_ast(text)
        prompt = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(prompt, "solo tag")

    def test_sdxl_weight(self):
        text = "(masterpiece:1.2), normal tag"
        ast = parse_prompt_to_ast(text)
        prompt = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(prompt, "(masterpiece:1.2), normal tag")

    def test_nested_wildcards(self):
        text = "{100% {100% inner_tag | 0% ignored} | 0% outer_ignored}"
        ast = parse_prompt_to_ast(text)
        prompt = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(prompt, "inner_tag")


if __name__ == '__main__':
    unittest.main()
