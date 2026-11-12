import json
import unittest

from expert_prompt_node import ExpertTextPromptNode


class TestExpertTextPromptNodeJsonMode(unittest.TestCase):
    def setUp(self):
        self.node = ExpertTextPromptNode()

    def test_auto_json_mode_resolves_wildcards_and_preserves_box_2d(self):
        payload = {
            "caption": "cinematic evening photograph, {warm|moody} lighting, -blurry",
            "layout": [
                {
                    "label": "35 yo woman, {blonde|red} curly hair, -watermark",
                    "box_2d": [60, 500, 620, 830],
                },
                {
                    "label": "dark brown leather sofa",
                    "box_2d": [430, 440, 710, 990],
                },
            ],
        }
        raw_json = json.dumps(payload)

        pos, neg, combos, debug_info = self.node.process(
            positive_prompt=raw_json,
            negative_prompt="$negative, lowres",
            negative_mode="auto (use $negative)",
            seed=42,
        )

        resolved = json.loads(pos)
        self.assertIn(
            resolved["caption"],
            {
                "cinematic evening photograph, warm lighting",
                "cinematic evening photograph, moody lighting",
            },
        )
        self.assertEqual(resolved["layout"][0]["box_2d"], [60, 500, 620, 830])
        self.assertEqual(resolved["layout"][1]["box_2d"], [430, 440, 710, 990])
        self.assertIn(
            resolved["layout"][0]["label"],
            {
                "35 yo woman, blonde curly hair",
                "35 yo woman, red curly hair",
            },
        )
        self.assertEqual(neg, "blurry, watermark, lowres")
        self.assertEqual(combos, 4)
        self.assertIn("[Syntax OK]", debug_info)

    def test_auto_json_mode_preserves_summary_items_metadata(self):
        payload = {
            "summary": {
                "meta": ["poster"],
                "canvas": "single",
                "caption": "modern {loft|studio}",
            },
            "items": [
                {
                    "label": "object",
                    "caption": "tall {monstera|ficus} plant",
                    "bbox": [-192, -288, 384, 288],
                }
            ],
            "bbox_coord_space": "abs_centralized",
            "bbox_format": "yxyx",
        }

        pos, neg, combos, _ = self.node.process(
            positive_prompt=json.dumps(payload),
            negative_prompt="$negative",
            negative_mode="auto (use $negative)",
            seed=7,
        )

        resolved = json.loads(pos)
        self.assertNotIn("\n", pos)
        self.assertEqual(resolved["summary"]["canvas"], "single")
        self.assertEqual(resolved["bbox_coord_space"], "abs_centralized")
        self.assertEqual(resolved["bbox_format"], "yxyx")
        self.assertEqual(resolved["items"][0]["bbox"], [-192, -288, 384, 288])
        self.assertIn(resolved["summary"]["caption"], {"modern loft", "modern studio"})
        self.assertIn(
            resolved["items"][0]["caption"],
            {"tall monstera plant", "tall ficus plant"},
        )
        self.assertEqual(neg, "")
        self.assertEqual(combos, 4)

    def test_auto_mode_falls_back_cleanly_for_leading_wildcard(self):
        pos, neg, combos, debug_info = self.node.process(
            positive_prompt="{red | blue} jacket, -ugly",
            negative_prompt="$negative",
            negative_mode="auto (use $negative)",
            seed=1,
            json_mode="auto",
        )

        self.assertIn(pos, {"red jacket", "blue jacket"})
        self.assertEqual(neg, "ugly")
        self.assertEqual(combos, 2)
        self.assertIn("[Syntax OK]", debug_info)

    def test_explicit_json_mode_on_reports_invalid_json_gracefully(self):
        broken_json = '{"caption": "hello", "layout": ['
        pos, neg, combos, debug_info = self.node.process(
            positive_prompt=broken_json,
            negative_prompt="bad quality",
            negative_mode="auto (use $negative)",
            seed=1,
            json_mode="on",
        )

        self.assertEqual(pos, broken_json)
        self.assertEqual(neg, "bad quality")
        self.assertEqual(combos, 0)
        self.assertIn("[JSON Parse Error]:", debug_info)

    def test_explicit_json_mode_off_bypasses_json_parsing(self):
        simple_json = '{"caption": "test"}'
        _, _, _, debug_info = self.node.process(
            positive_prompt=simple_json,
            negative_prompt="$negative",
            negative_mode="auto (use $negative)",
            seed=1,
            json_mode="off",
        )
        # Normal parser strips outer braces as a single-option wildcard
        self.assertIn("[Resolved Positive Output]:", debug_info)


if __name__ == "__main__":
    unittest.main()

