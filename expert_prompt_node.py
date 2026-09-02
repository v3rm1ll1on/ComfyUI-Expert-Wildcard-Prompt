import random
try:
    from .prompt_parser import (
        parse_prompt_to_ast,
        resolve_ast_to_prompt,
        combine_negative_prompts,
        check_prompt_syntax
    )
except ImportError:
    from prompt_parser import (
        parse_prompt_to_ast,
        resolve_ast_to_prompt,
        combine_negative_prompts,
        check_prompt_syntax
    )

class ExpertTextPromptNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive_prompt": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": "(3d render, cgi:1.3), $negative, (deformed hands:1.2)"}),
                "negative_mode": (["auto (use $negative)", "prepend", "append", "replace"], {"default": "auto (use $negative)"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "process"
    CATEGORY = "prompt/expert"

    def process(self, positive_prompt: str, negative_prompt: str, negative_mode: str, seed: int):
        # Syntax Check
        syntax_pos = check_prompt_syntax(positive_prompt)
        syntax_neg = check_prompt_syntax(negative_prompt)
        
        if not syntax_pos.is_valid:
            print(f"[ExpertTextPrompt Warning] Positive prompt syntax issues:\n" + "\n".join(syntax_pos.errors))
        if not syntax_neg.is_valid:
            print(f"[ExpertTextPrompt Warning] Negative prompt syntax issues:\n" + "\n".join(syntax_neg.errors))

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

        return (final_positive, final_negative)

NODE_CLASS_MAPPINGS = {
    "ExpertTextPrompt": ExpertTextPromptNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ExpertTextPrompt": "Expert Text Prompt (Wildcards & AST)"
}
