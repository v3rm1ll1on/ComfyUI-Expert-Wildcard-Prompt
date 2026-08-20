import random
from .prompt_parser import parse_prompt_to_ast, resolve_ast_to_prompt, check_prompt_syntax

class ExpertTextPromptNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "process"
    CATEGORY = "prompt/expert"

    def process(self, text: str, seed: int):
        syntax_check = check_prompt_syntax(text)
        if not syntax_check.is_valid:
            print(f"[ExpertTextPrompt Warning] Syntax issues detected:\n" + "\n".join(syntax_check.errors))

        rng = random.Random(seed)
        ast_groups = parse_prompt_to_ast(text)
        pos_prompt, neg_prompt = resolve_ast_to_prompt(ast_groups, rng)
        return (pos_prompt, neg_prompt)

NODE_CLASS_MAPPINGS = {
    "ExpertTextPrompt": ExpertTextPromptNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ExpertTextPrompt": "Expert Text Prompt (Wildcards & AST)"
}
