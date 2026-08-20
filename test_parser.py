import unittest
import random
from prompt_parser import parse_prompt_to_ast, resolve_ast_to_prompt, combine_negative_prompts, check_prompt_syntax

class TestPromptParser(unittest.TestCase):

    # -------------------------------------------------------------
    # 1. Basic & Prose Formatting
    # -------------------------------------------------------------

    def test_prose_wildcard_spacing(self):
        """Test plain text with wildcards retains exact spacing without unwanted commas."""
        text = "a photo of a {100% cat | 0% dog} sitting on a bench"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "a photo of a cat sitting on a bench")
        self.assertEqual(neg, "")

    def test_comma_separated_tags_spacing(self):
        """Test tag lists retain comma separation."""
        text = "masterpiece, 8k, {100% blue eyes | 0% green eyes}, leather jacket"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, 8k, blue eyes, leather jacket")
        self.assertEqual(neg, "")

    def test_multiline_prompts(self):
        """Test prompts with line breaks retain group and line structure."""
        text = "masterpiece, 8k,\n[GRP:CHAR], 1girl, red hair,\n[GRP:BG], sunset sky"
        ast = parse_prompt_to_ast(text)
        pos, _ = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertIn("1girl, red hair", pos)
        self.assertIn("sunset sky", pos)

    # -------------------------------------------------------------
    # 2. Wildcards: Probabilities, Skip Chance & Nesting
    # -------------------------------------------------------------

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

        # Option-level skip chance regex consumption
        text_option_skip = "{40%? flying dragons | 10%? floating magical islands}"
        ast_opt = parse_prompt_to_ast(text_option_skip)
        pos_opt, _ = resolve_ast_to_prompt(ast_opt, random.Random(42))
        self.assertNotIn("?", pos_opt)

    def test_three_level_nested_wildcards(self):
        """Test 3-level deep wildcard nesting."""
        text = "{100% {100% {100% ultra deep tag | 0% inner} | 0% mid} | 0% outer}"
        ast = parse_prompt_to_ast(text)
        pos, _ = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "ultra deep tag")

    # -------------------------------------------------------------
    # 3. Solo (!), Mute (//) & Inheritance Logic
    # -------------------------------------------------------------

    def test_mute_and_solo_controls(self):
        """Test inline mute (//) and solo (!) controls on individual tags."""
        text_mute = "masterpiece, // ruined background, leather jacket, // blurry lines"
        ast_mute = parse_prompt_to_ast(text_mute)
        pos_mute, _ = resolve_ast_to_prompt(ast_mute, random.Random(42))
        self.assertEqual(pos_mute, "masterpiece, leather jacket")

        text_solo = "! red dress, blue shoes, ! golden necklace"
        ast_solo = parse_prompt_to_ast(text_solo)
        pos_solo, _ = resolve_ast_to_prompt(ast_solo, random.Random(42))
        self.assertEqual(pos_solo, "red dress, golden necklace")

    def test_solo_phrase_inheritance_across_spaces(self):
        """Test solo (!) inherits across space-connected wildcards in a phrase, ending at comma."""
        text = "[GRP:STYLE], RAW photo, [GRP:SUBJ], ! cinematic portrait of a {100% female hacker | 0% runner}, standing in street"
        ast = parse_prompt_to_ast(text)
        pos, _ = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "cinematic portrait of a female hacker")

    def test_mute_phrase_inheritance_across_spaces(self):
        """Test mute (//) inherits across space-connected wildcards, ending at comma."""
        text = "masterpiece, // ugly portrait of a {100% monster | 0% demon}, highly detailed face"
        ast = parse_prompt_to_ast(text)
        pos, _ = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, highly detailed face")

    def test_group_level_solo_and_mute(self):
        """Test group-level ![GRP:NAME] and //[GRP:NAME]."""
        text = "![GRP:CHAR], 1girl, red hair, [GRP:BG], sunset sky, //[GRP:EXTRA], fireworks"
        ast = parse_prompt_to_ast(text)
        pos, _ = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "1girl, red hair")

    def test_group_solo_with_internal_mute(self):
        """Test muted tags inside a soloed group remain muted."""
        text = "![GRP:CHAR], 1girl, // deformed face, red hair"
        ast = parse_prompt_to_ast(text)
        pos, _ = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "1girl, red hair")

    # -------------------------------------------------------------
    # 4. Inline Negative (-) & $negative Routing
    # -------------------------------------------------------------

    def test_inline_negative_prefix_extraction(self):
        """Test '-' prefix extraction within wildcards and normal tags."""
        text = "masterpiece, {100% sunny day, -sunglasses | 0% rainy day, -umbrella}, leather jacket"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, sunny day, leather jacket")
        self.assertEqual(neg, "sunglasses")

    def test_negative_extraction_inheritance_across_spaces(self):
        """Test '-' prefix inherits across space-connected wildcards into negative output."""
        text = "masterpiece, - ugly features of {100% monster eyes | 0% demon teeth}, beautiful face"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, beautiful face")
        self.assertEqual(neg, "ugly features of monster eyes")

    def test_negative_extraction_suppressed_when_muted(self):
        """Test '-' tags inside muted groups or muted tags are NOT extracted into negative prompt."""
        text = "masterpiece, //[GRP:MUTED], -sunglasses, [GRP:MAIN], // -umbrella, valid tag"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, valid tag")
        self.assertEqual(neg, "")

    def test_negative_extraction_suppressed_when_not_soloed(self):
        """Test '-' tags in inactive groups are NOT extracted into negative when another tag is soloed."""
        text = "! active tag, [GRP:OTHER], -unwanted_tag"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "active tag")
        self.assertEqual(neg, "")

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

    def test_direct_prefix_on_wildcard_block(self):
        """Test direct prefixes //, !, and - applied directly onto a wildcard block {...}."""
        # Mute whole wildcard
        text_mute = "masterpiece, //{cat | dog | fox}, leather jacket"
        ast_mute = parse_prompt_to_ast(text_mute)
        pos_mute, _ = resolve_ast_to_prompt(ast_mute, random.Random(42))
        self.assertEqual(pos_mute, "masterpiece, leather jacket")

        # Solo whole wildcard
        text_solo = "masterpiece, !{100% cat | 0% dog}, leather jacket"
        ast_solo = parse_prompt_to_ast(text_solo)
        pos_solo, _ = resolve_ast_to_prompt(ast_solo, random.Random(42))
        self.assertEqual(pos_solo, "cat")

        # Negative route whole wildcard
        text_neg = "masterpiece, -{100% cat | 0% dog}, leather jacket"
        ast_neg = parse_prompt_to_ast(text_neg)
        pos_neg, neg_neg = resolve_ast_to_prompt(ast_neg, random.Random(42))
        self.assertEqual(pos_neg, "masterpiece, leather jacket")
        self.assertEqual(neg_neg, "cat")

    # -------------------------------------------------------------
    # 5. SDXL Weights, LoRAs & Syntax
    # -------------------------------------------------------------

    def test_sdxl_weight_and_lora_preservation(self):
        """Test SDXL weights (tag:1.2) and <lora:name:1.0> remain intact."""
        text = "masterpiece, (leather jacket:1.2), <lora:cyberpunk_v1:0.8>"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, (leather jacket:1.2), <lora:cyberpunk_v1:0.8>")

    def test_sdxl_weight_inside_inline_negative(self):
        """Test SDXL weighted tag with negative prefix - (deformed eyes:1.2)."""
        text = "masterpiece, - (deformed eyes:1.2)"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece")
        self.assertEqual(neg, "(deformed eyes:1.2)")

    # -------------------------------------------------------------
    # 6. Advanced Edge Cases
    # -------------------------------------------------------------

    def test_negative_lora_weight(self):
        """Test LoRA with negative weight <lora:name:-0.5> is preserved in positive prompt."""
        text = "masterpiece, <lora:cyberpunk_style:-0.5>"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "masterpiece, <lora:cyberpunk_style:-0.5>")
        self.assertEqual(neg, "")

    def test_hyphenated_words_vs_negative_prefix(self):
        """Test hyphenated words like shoulder-length hair are not misidentified as negative extraction."""
        text = "shoulder-length hair, high-waisted jeans, - -sunglasses"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "shoulder-length hair, high-waisted jeans")
        self.assertEqual(neg, "-sunglasses")

    def test_mixed_explicit_and_default_wildcard_weights(self):
        """Test wildcards mixing explicit probabilities (70%) with default ones."""
        text = "{70% option A | option B}"
        ast = parse_prompt_to_ast(text)
        pos, _ = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertIn(pos, ["option A", "option B"])

    def test_whitespace_in_group_prefixes(self):
        """Test group prefixes handling accidental whitespace like '// [GRP:NAME]'."""
        text = "// [GRP:TEST], tag"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "")
        self.assertEqual(neg, "")

    def test_number_range_wildcards(self):
        """Test number range wildcards {min-max} and {min-max:count}."""
        text = "portrait of a {18-50} yo woman with {1-5:3} items"
        ast = parse_prompt_to_ast(text)
        rng = random.Random(42)
        pos, _ = resolve_ast_to_prompt(ast, rng)
        # Verify 25 is generated for {18-50} and 3 numbers for {1-5:3}
        self.assertEqual(pos, "portrait of a 25 yo woman with 1 3 2 items")

if __name__ == '__main__':
    unittest.main()
