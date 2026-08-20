import unittest
import random
from prompt_parser import parse_prompt_to_ast, resolve_ast_to_prompt, combine_negative_prompts, check_prompt_syntax

class TestPromptParser(unittest.TestCase):

    def test_prose_wildcard_spacing(self):
        """Test plain text with wildcards retains exact spacing without unwanted commas."""
        text = "a photo of a {cat | dog | fox} sitting on a bench"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "a photo of a dog sitting on a bench")
        self.assertEqual(neg, "")

    def test_comma_separated_tags_spacing(self):
        """Test tag lists retain comma separation."""
        text = "masterpiece, 8k, {70% blue eyes | 30% green eyes}, leather jacket"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, 8k, blue eyes, leather jacket")
        self.assertEqual(neg, "")

    def test_nested_wildcards_with_percentages(self):
        """Test nested wildcards with probabilities resolve recursively."""
        text = "a {100% female warrior with {100% knight armor | 0% cyber suit} | 0% rogue}"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "a female warrior with knight armor")
        self.assertEqual(neg, "")

    def test_skip_chance_in_wildcards(self):
        """Test {X%? tag} skip chance functionality."""
        text = "portrait of a woman, {100%? glowing neon face tattoos}"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "portrait of a woman")

        text_include = "portrait of a woman, {0%? glowing neon face tattoos}"
        ast_inc = parse_prompt_to_ast(text_include)
        pos_inc, _ = resolve_ast_to_prompt(ast_inc, random.Random(42))
        self.assertEqual(pos_inc, "portrait of a woman, glowing neon face tattoos")

        # Test option-level skip chance regex consumption (ensuring no ? leaks into text)
        text_option_skip = "{40%? flying dragons | 10%? floating magical islands}"
        ast_opt = parse_prompt_to_ast(text_option_skip)
        pos_opt, _ = resolve_ast_to_prompt(ast_opt, random.Random(42))
        self.assertNotIn("?", pos_opt)

    def test_mute_and_solo_controls(self):
        """Test inline mute (//) and solo (!) controls."""
        # Mute test
        text_mute = "masterpiece, // ruined background, leather jacket, // blurry lines"
        ast_mute = parse_prompt_to_ast(text_mute)
        pos_mute, _ = resolve_ast_to_prompt(ast_mute, random.Random(42))
        self.assertEqual(pos_mute, "masterpiece, leather jacket")

        # Multiple solo test
        text_solo = "! red dress, blue shoes, ! golden necklace"
        ast_solo = parse_prompt_to_ast(text_solo)
        pos_solo, _ = resolve_ast_to_prompt(ast_solo, random.Random(42))
        self.assertEqual(pos_solo, "red dress, golden necklace")

        # Test solo inheritance across space-connected wildcards in the same phrase
        text_phrase = "! cinematic portrait of a {100% female hacker | 0% runner}, standing in street"
        ast_phrase = parse_prompt_to_ast(text_phrase)
        pos_phrase, _ = resolve_ast_to_prompt(ast_phrase, random.Random(42))
        self.assertEqual(pos_phrase, "cinematic portrait of a female hacker")

    def test_prompt_grouping(self):
        """Test [GRP:NAME] grouping with mute and solo on groups."""
        text_grp = "[GRP:QUALITY], masterpiece, 8k, //[GRP:BACKGROUND], city skyline, [GRP:CHAR], girl"
        ast_grp = parse_prompt_to_ast(text_grp)
        pos_grp, _ = resolve_ast_to_prompt(ast_grp, random.Random(42))
        self.assertEqual(pos_grp, "masterpiece, 8k, girl")

    def test_inline_negative_prefix_extraction(self):
        """Test '-' prefix extraction within wildcards and normal tags."""
        text = "masterpiece, {100% sunny day, -sunglasses | 0% rainy day, -umbrella}, leather jacket"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, sunny day, leather jacket")
        self.assertEqual(neg, "sunglasses")

    def test_negative_placeholder_injection(self):
        """Test $negative placeholder injection in negative prompt template."""
        extracted = "sunglasses, umbrella"
        base_neg = "(3d render:1.3), $negative, (deformed hands:1.2)"
        res = combine_negative_prompts(extracted, base_neg, "auto (use $negative)", random.Random(42))
        self.assertEqual(res, "(3d render:1.3), sunglasses, umbrella, (deformed hands:1.2)")

    def test_negative_modes_without_placeholder(self):
        """Test prepend, append, and replace negative modes."""
        extracted = "umbrella, coat"
        base_neg = "3d render, cgi"

        res_prepend = combine_negative_prompts(extracted, base_neg, "prepend", random.Random(42))
        self.assertEqual(res_prepend, "umbrella, coat, 3d render, cgi")

        res_append = combine_negative_prompts(extracted, base_neg, "append", random.Random(42))
        self.assertEqual(res_append, "3d render, cgi, umbrella, coat")

        res_replace = combine_negative_prompts(extracted, base_neg, "replace", random.Random(42))
        self.assertEqual(res_replace, "umbrella, coat")

    def test_sdxl_weight_and_lora_preservation(self):
        """Test SDXL weights (tag:1.2) and <lora:name:1.0> remain intact."""
        text = "masterpiece, (leather jacket:1.2), <lora:cyberpunk_v1:0.8>"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, (leather jacket:1.2), <lora:cyberpunk_v1:0.8>")

    def test_syntax_checker(self):
        """Test syntax check for matched/unmatched brackets."""
        res1 = check_prompt_syntax("valid {wildcard | option}")
        self.assertTrue(res1.is_valid)

        res2 = check_prompt_syntax("invalid {wildcard | option")
        self.assertFalse(res2.is_valid)

if __name__ == '__main__':
    unittest.main()
