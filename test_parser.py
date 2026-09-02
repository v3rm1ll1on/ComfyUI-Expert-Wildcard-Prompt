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
        """Test number range wildcards {min-max} and {min-max:step}."""
        text = "{18-50} yo, {0-10:2} step, {0-10:3} step3"
        ast = parse_prompt_to_ast(text)
        rng = random.Random(42)
        pos, _ = resolve_ast_to_prompt(ast, rng)
        # {18-50} -> 25, {0-10:2} -> 0 (from [0,2,4,6,8,10]), {0-10:3} -> 6 (from [0,3,6,9])
        self.assertEqual(pos, "25 yo, 0 step, 6 step3")

    def test_negative_tag_starting_with_digit(self):
        """Test negative extraction tags starting with digits like -3d render."""
        text = "photo, -3d render, -2D art"
        ast = parse_prompt_to_ast(text)
        pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertEqual(pos, "photo")
        self.assertEqual(neg, "3d render, 2D art")

    def test_wildcard_leftover_and_overcommitment_distribution(self):
        """Test partial percentage distribution and over-commitment normalization."""
        text_partial = "{50% red | 30% green | black | white}"
        ast_p = parse_prompt_to_ast(text_partial)
        # Test statistical distribution across multiple random seeds
        counts = {"red": 0, "green": 0, "black": 0, "white": 0}
        for seed in range(1000):
            pos, _ = resolve_ast_to_prompt(ast_p, random.Random(seed))
            counts[pos] += 1
        # red ~ 500 (50%), green ~ 300 (30%), black ~ 100 (10%), white ~ 100 (10%)
        self.assertTrue(450 <= counts["red"] <= 550, f"red count {counts['red']} expected ~500")
        self.assertTrue(250 <= counts["green"] <= 350, f"green count {counts['green']} expected ~300")
        self.assertTrue(60 <= counts["black"] <= 140, f"black count {counts['black']} expected ~100")
        self.assertTrue(60 <= counts["white"] <= 140, f"white count {counts['white']} expected ~100")

    def test_overcommitted_wildcard_weights(self):
        """Test over-committed percentage wildcards like {50% red | 30% green | black | 50% white}."""
        text_over = "{50% red | 30% green | black | 50% white}"
        ast_o = parse_prompt_to_ast(text_over)
        counts = {"red": 0, "green": 0, "black": 0, "white": 0}
        for seed in range(1000):
            pos, _ = resolve_ast_to_prompt(ast_o, random.Random(seed))
            counts[pos] += 1
        # red ~ 323 (32.3%), green ~ 194 (19.4%), black ~ 161 (16.1%), white ~ 323 (32.3%)
        self.assertTrue(250 <= counts["red"] <= 380, f"red count {counts['red']} expected ~323")
        self.assertTrue(140 <= counts["green"] <= 250, f"green count {counts['green']} expected ~194")
        self.assertTrue(120 <= counts["black"] <= 210, f"black count {counts['black']} expected ~161")
        self.assertTrue(250 <= counts["white"] <= 380, f"white count {counts['white']} expected ~323")

    def test_lora_syntax_check(self):
        """Test syntax check for angle brackets in LoRA syntax."""
        from prompt_parser import check_prompt_syntax
        res_valid = check_prompt_syntax("<lora:my_lora:1.0>, 8k")
        self.assertTrue(res_valid.is_valid)
        res_invalid = check_prompt_syntax("<lora:my_lora:1.0, 8k")
        self.assertFalse(res_invalid.is_valid)

    def test_count_ast_combinations(self):
        """Test calculation of total unique prompt combinations."""
        from prompt_parser import count_ast_combinations
        
        ast1 = parse_prompt_to_ast("photo, 8k")
        self.assertEqual(count_ast_combinations(ast1), 1)

        ast2 = parse_prompt_to_ast("{red | green | blue}")
        self.assertEqual(count_ast_combinations(ast2), 3)

        ast3 = parse_prompt_to_ast("{red | blue} female, {photorealistic | anime}")
        self.assertEqual(count_ast_combinations(ast3), 4)

        ast4 = parse_prompt_to_ast("{1-5}")
        self.assertEqual(count_ast_combinations(ast4), 5)

        ast5 = parse_prompt_to_ast("[GRP:A] {red|blue}, //[GRP:B] {shirt|pants}")
        self.assertEqual(count_ast_combinations(ast5), 2)  # GRP B is muted

        # Skip chance (+1 state for empty string)
        ast6 = parse_prompt_to_ast("{50%? sunglasses}")
        self.assertEqual(count_ast_combinations(ast6), 2)  # sunglasses OR skipped

        ast7 = parse_prompt_to_ast("{50%? {red | blue}}")
        self.assertEqual(count_ast_combinations(ast7), 3)  # red, blue OR skipped

        # Node-level solo flag
        ast8 = parse_prompt_to_ast("! {red | blue}, {shirt | pants}")
        self.assertEqual(count_ast_combinations(ast8), 2)  # Only solo block is counted

        # Solo flag INSIDE wildcard option
        ast9 = parse_prompt_to_ast("{ ! red dress | blue jeans }")
        self.assertEqual(count_ast_combinations(ast9), 1)  # Only ! red dress option is active

        # Range step with skip chance: {0-10:2} -> [0, 2, 4, 6, 8, 10] (6 choices) + 1 skip state = 7
        ast_range_step = parse_prompt_to_ast("{50%? {0-10:2}}")
        self.assertEqual(count_ast_combinations(ast_range_step), 7)

    def test_soft_skip_mute_reset(self):
        """Test that //_S_ resets inherited mute state inside an inline block."""
        ast = parse_prompt_to_ast("{ //[GRP:FOO] armor, //_S_ active_tag }")
        pos, _ = resolve_ast_to_prompt(ast, random.Random(1))
        self.assertEqual(pos, "active_tag")

    def test_all_zero_weights_fallback(self):
        """Test wildcard with all zero weights does not crash and falls back gracefully."""
        text = "{0% cat | 0% dog}"
        ast = parse_prompt_to_ast(text)
        pos, _ = resolve_ast_to_prompt(ast, random.Random(42))
        self.assertIn(pos, ["cat", "dog"])

    # -------------------------------------------------------------
    # 7. Node Integration & Boundary Edge Cases
    # -------------------------------------------------------------

    def test_empty_inputs_and_whitespace(self):
        """Test completely empty or whitespace-only inputs return empty strings without crashing."""
        for empty_text in ["", "   ", "\n\t"]:
            ast = parse_prompt_to_ast(empty_text)
            pos, neg = resolve_ast_to_prompt(ast, random.Random(42))
            self.assertEqual(pos, "")
            self.assertEqual(neg, "")

            combined = combine_negative_prompts("", empty_text, "auto (use $negative)", random.Random(42))
            self.assertEqual(combined, "")

    def test_empty_wildcard_and_empty_options(self):
        """Test empty wildcard blocks {} and empty branches {cat|} resolve gracefully."""
        # Leere Klammer
        ast_empty = parse_prompt_to_ast("photo, {}, dog")
        pos_empty, _ = resolve_ast_to_prompt(ast_empty, random.Random(42))
        self.assertEqual(pos_empty, "photo, dog")

        # Option mit leerem Fallback
        ast_branch = parse_prompt_to_ast("photo, {100% cat | 0%}, dog")
        pos_branch, _ = resolve_ast_to_prompt(ast_branch, random.Random(42))
        self.assertEqual(pos_branch, "photo, cat, dog")

    def test_seed_determinism(self):
        """Test identical seeds yield strictly identical prompt outputs."""
        prompt = "{red | blue | green | yellow} {car | bike | plane}, {10-99} speed"
        ast = parse_prompt_to_ast(prompt)
        
        res1, _ = resolve_ast_to_prompt(ast, random.Random(1337))
        res2, _ = resolve_ast_to_prompt(ast, random.Random(1337))
        self.assertEqual(res1, res2)

    def test_comfyui_node_execution(self):
        """Test full pipeline pass-through via ExpertTextPromptNode."""
        from expert_prompt_node import ExpertTextPromptNode

        node = ExpertTextPromptNode()
        pos, neg, combos = node.process(
            positive_prompt="warrior, {-shield | sword}",
            negative_prompt="blurry, $negative, deformed",
            negative_mode="auto (use $negative)",
            seed=42
        )

        self.assertIsInstance(pos, str)
        self.assertIsInstance(neg, str)
        self.assertIsInstance(combos, int)
        self.assertEqual(combos, 2)
        self.assertIn("warrior", pos)
        self.assertIn("blurry", neg)

    def test_comfyui_node_execution_with_negative_wildcards(self):
        """Test combinations multiply correctly when negative_prompt field also contains wildcards."""
        from expert_prompt_node import ExpertTextPromptNode

        node = ExpertTextPromptNode()
        pos, neg, combos = node.process(
            positive_prompt="hero {red | blue}",           # 2 pos combos
            negative_prompt="{deformed | blurry| mutated}", # 3 neg combos
            negative_mode="auto (use $negative)",
            seed=42
        )
        self.assertEqual(combos, 6)  # 2 * 3 = 6

if __name__ == '__main__':
    unittest.main()
