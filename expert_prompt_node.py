import random
import logging

logger = logging.getLogger("ComfyUI-ExpertTextPrompt")

try:
    from .prompt_parser import (
        parse_prompt_to_ast,
        resolve_ast_to_prompt,
        combine_negative_prompts,
        check_prompt_syntax,
        count_ast_combinations
    )
except ImportError:
    from prompt_parser import (
        parse_prompt_to_ast,
        resolve_ast_to_prompt,
        combine_negative_prompts,
        check_prompt_syntax,
        count_ast_combinations
    )

class ExpertTextPromptNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive_prompt": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": "$negative"}),
                "negative_mode": (["auto (use $negative)", "prepend", "append", "replace"], {"default": "auto (use $negative)"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("positive", "negative", "combinations", "debug_info")
    FUNCTION = "process"
    CATEGORY = "prompt/expert"

    def process(self, positive_prompt: str, negative_prompt: str, negative_mode: str, seed: int):
        # Syntax Check
        syntax_pos = check_prompt_syntax(positive_prompt)
        syntax_neg = check_prompt_syntax(negative_prompt)
        
        debug_lines = []
        if not syntax_pos.is_valid:
            logger.warning("Positive prompt syntax issues:\n%s", "\n".join(syntax_pos.errors))
            debug_lines.append("[Positive Prompt Syntax Issues]:\n" + "\n".join(syntax_pos.errors))
        if not syntax_neg.is_valid:
            logger.warning("Negative prompt syntax issues:\n%s", "\n".join(syntax_neg.errors))
            debug_lines.append("[Negative Prompt Syntax Issues]:\n" + "\n".join(syntax_neg.errors))

        rng = random.Random(seed)
        
        # Parse positive_prompt
        pos_ast = parse_prompt_to_ast(positive_prompt)
        final_positive, extracted_negative = resolve_ast_to_prompt(pos_ast, rng)
        
        # Combine extracted negative tags with negative_prompt field
        final_negative = combine_negative_prompts(
            extracted_neg=extracted_negative,
            base_neg_input=negative_prompt,
            mode=negative_mode,
            rng=rng
        )

        pos_combos = count_ast_combinations(pos_ast)
        neg_ast = parse_prompt_to_ast(negative_prompt) if negative_prompt.strip() else []
        neg_combos = count_ast_combinations(neg_ast) if neg_ast else 1
        total_combinations = pos_combos * max(neg_combos, 1)

        # Cap INT to max signed 64-bit int (0x7fffffffffffffff) to prevent PyTorch/C++/JS overflow
        safe_combinations = min(total_combinations, 0x7fffffffffffffff)

        if not debug_lines:
            debug_info = (
                f"[Syntax OK]\n"
                f"Combinations: {total_combinations:,} (Pos: {pos_combos:,}, Neg: {neg_combos:,})\n\n"
                f"[Resolved Positive Output]:\n{final_positive}\n\n"
                f"[Resolved Negative Output]:\n{final_negative}"
            )
        else:
            debug_info = (
                "\n\n".join(debug_lines) + "\n\n"
                f"Combinations: {total_combinations:,}\n\n"
                f"[Resolved Positive Output]:\n{final_positive}\n\n"
                f"[Resolved Negative Output]:\n{final_negative}"
            )

        return (final_positive, final_negative, safe_combinations, debug_info)

NODE_CLASS_MAPPINGS = {
    "ExpertTextPrompt": ExpertTextPromptNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ExpertTextPrompt": "Expert Text Prompt (Wildcards & AST)"
}
