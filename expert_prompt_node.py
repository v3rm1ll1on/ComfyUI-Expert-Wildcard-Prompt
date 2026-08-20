import random
from .prompt_parser import parse_prompt_to_ast, resolve_ast_to_prompt

class ExpertTextPromptNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "process"
    CATEGORY = "prompt/expert"

    def process(self, text: str, seed: int):
        rng = random.Random(seed)
        ast_groups = parse_prompt_to_ast(text)
        final_prompt = resolve_ast_to_prompt(ast_groups, rng)
        return (final_prompt,)

NODE_CLASS_MAPPINGS = {
    "ExpertTextPrompt": ExpertTextPromptNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ExpertTextPrompt": "Expert Text Prompt (Wildcards & AST)"
}
