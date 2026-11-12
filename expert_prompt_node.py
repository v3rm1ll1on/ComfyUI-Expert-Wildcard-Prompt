import json
import random
import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("ComfyUI-ExpertTextPrompt")

try:
    from .prompt_parser import (
        parse_prompt_to_ast,
        resolve_ast_to_prompt,
        resolve_ast_by_groups,
        collect_group_children_map,
        combine_negative_prompts,
        check_prompt_syntax,
        count_ast_combinations
    )
except ImportError:
    from prompt_parser import (
        parse_prompt_to_ast,
        resolve_ast_to_prompt,
        resolve_ast_by_groups,
        collect_group_children_map,
        combine_negative_prompts,
        check_prompt_syntax,
        count_ast_combinations
    )

DEFAULT_MOSS_DIMENSION = 1024.0

JSON_STRUCTURAL_KEYS = frozenset({
    "bbox_coord_space",
    "bbox_format",
    "canvas",
    "borders",
})


def _to_centralized_bbox(box2d: List[Any], width: float, height: float) -> List[int]:
    """Maps normalized [ymin, xmin, ymax, xmax] (0..1000) to centralized pixel yxyx coords."""
    ymin, xmin, ymax, xmax = (float(box2d[0]), float(box2d[1]), float(box2d[2]), float(box2d[3]))
    return [
        round(((ymin - 500.0) / 1000.0) * height),
        round(((xmin - 500.0) / 1000.0) * width),
        round(((ymax - 500.0) / 1000.0) * height),
        round(((xmax - 500.0) / 1000.0) * width),
    ]


def _resolve_moss_ide_envelope(
    raw_prompt: str,
    spatial_layout: Dict[str, Any],
    rng: random.Random,
    debug_lines: List[str],
) -> Tuple[str, str, int]:
    """Resolves a raw IDE prompt via AST + group routing and builds compact native MOSS JSON."""
    syntax_pos = check_prompt_syntax(raw_prompt)
    if not syntax_pos.is_valid:
        logger.warning("Positive prompt syntax issues:\n%s", "\n".join(syntax_pos.errors))
        debug_lines.append("[Positive Prompt Syntax Issues]:\n" + "\n".join(syntax_pos.errors))

    pos_ast = parse_prompt_to_ast(raw_prompt)
    group_outputs, group_order, extracted_negative = resolve_ast_by_groups(pos_ast, rng)
    children_map = collect_group_children_map(pos_ast)
    pos_combos = count_ast_combinations(pos_ast)

    outputs_by_lower = {k.strip().lower(): v for k, v in group_outputs.items()}
    target_width = float(spatial_layout.get("targetWidth") or DEFAULT_MOSS_DIMENSION)
    target_height = float(spatial_layout.get("targetHeight") or DEFAULT_MOSS_DIMENSION)
    boxes = [b for b in (spatial_layout.get("boxes") or []) if isinstance(b, dict) and not b.get("localMuted")]
    boxes.sort(key=lambda b: float(b.get("zIndex", 0)))

    items: List[Dict[str, Any]] = []
    boxed_keys = set()

    for box in boxes:
        raw_group = box.get("groupName")
        group_key = raw_group.strip().lower() if isinstance(raw_group, str) and raw_group.strip() else ""
        if group_key:
            direct_text = outputs_by_lower.get(group_key, "").strip()
            child_keys = children_map.get(group_key, [])
            if direct_text:
                text = direct_text
            elif child_keys:
                child_parts = [
                    outputs_by_lower.get(ck, "").strip()
                    for ck in child_keys
                    if outputs_by_lower.get(ck, "").strip()
                ]
                text = ", ".join(child_parts)
                for ck in child_keys:
                    boxed_keys.add(ck)
            else:
                text = ""

            if not text and not (box.get("role") == "text" and box.get("textContent")):
                continue
            boxed_keys.add(group_key)
        else:
            text = str(box.get("customCaption") or "").strip()
            if not text and not (box.get("role") == "text" and box.get("textContent")):
                continue

        role = str(box.get("role") or "object")
        item: Dict[str, Any] = {
            "label": role,
            "caption": text,
        }
        palette = box.get("palette")
        if isinstance(palette, list) and len(palette) > 0:
            item["palette"] = palette
        if role == "text" and box.get("textContent"):
            item["text"] = str(box["textContent"])
        box2d = box.get("box2d")
        if isinstance(box2d, list) and len(box2d) == 4:
            item["bbox"] = _to_centralized_bbox(box2d, target_width, target_height)
        items.append(item)

    caption_parts: List[str] = []
    base_caption = str(spatial_layout.get("baseCaption") or "").strip()
    if base_caption:
        caption_parts.append(base_caption)

    for gname in group_order:
        if gname.strip().lower() in boxed_keys:
            continue
        grp_text = group_outputs.get(gname, "").strip()
        if grp_text:
            caption_parts.append(grp_text)

    if not items:
        return ", ".join(caption_parts), extracted_negative, pos_combos

    payload: Dict[str, Any] = {
        "summary": {
            "caption": ", ".join(caption_parts),
        },
        "items": items,
        "bbox_coord_space": "abs_centralized",
        "bbox_format": "yxyx",
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")), extracted_negative, pos_combos


def _resolve_json_value(
    value: Any,
    rng: random.Random,
    field_path: str,
    extracted_negatives: List[str],
    debug_lines: List[str],
    combos_acc: List[int],
    current_key: str = "",
) -> Any:
    """Recursively resolves prompt syntax inside JSON string fields while preserving structure."""
    if isinstance(value, dict):
        return {
            key: _resolve_json_value(
                val,
                rng,
                f"{field_path}.{key}" if field_path else key,
                extracted_negatives,
                debug_lines,
                combos_acc,
                current_key=key,
            )
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [
            _resolve_json_value(
                item,
                rng,
                f"{field_path}[{idx}]",
                extracted_negatives,
                debug_lines,
                combos_acc,
                current_key=current_key,
            )
            for idx, item in enumerate(value)
        ]

    if not isinstance(value, str) or current_key in JSON_STRUCTURAL_KEYS or not value.strip():
        return value

    syntax_res = check_prompt_syntax(value)
    if not syntax_res.is_valid:
        logger.warning("JSON field '%s' syntax issues:\n%s", field_path, "\n".join(syntax_res.errors))
        debug_lines.append(f"[JSON '{field_path}' Syntax Issues]:\n" + "\n".join(syntax_res.errors))

    ast = parse_prompt_to_ast(value)
    resolved_pos, extracted_neg = resolve_ast_to_prompt(ast, rng)
    if extracted_neg:
        extracted_negatives.append(extracted_neg)

    field_combos = count_ast_combinations(ast)
    if field_combos > 0:
        combos_acc[0] *= field_combos

    return resolved_pos


def _try_parse_json_dict(raw_text: str) -> Tuple[bool, Any, str]:
    """Attempts to parse a raw string as a JSON object, returning (is_dict, payload, error_msg)."""
    stripped = raw_text.lstrip()
    if not stripped.startswith("{"):
        return False, None, "Input does not start with '{'"
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        return False, None, str(exc)
    if not isinstance(parsed, dict):
        return False, None, "Top-level JSON value must be an object"
    return True, parsed, ""


class ExpertTextPromptNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive_prompt": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": "$negative"}),
                "negative_mode": (["auto (use $negative)", "prepend", "append", "replace"], {"default": "auto (use $negative)"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "control_after_generate": True}),
            },
            "optional": {
                "json_mode": (["auto", "on", "off"], {"default": "auto"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("positive", "negative", "combinations", "debug_info")
    FUNCTION = "process"
    CATEGORY = "prompt/expert"

    def process(self, positive_prompt: str, negative_prompt: str, negative_mode: str, seed: int, json_mode: str = "auto"):
        syntax_neg = check_prompt_syntax(negative_prompt)
        debug_lines: List[str] = []
        if not syntax_neg.is_valid:
            logger.warning("Negative prompt syntax issues:\n%s", "\n".join(syntax_neg.errors))
            debug_lines.append("[Negative Prompt Syntax Issues]:\n" + "\n".join(syntax_neg.errors))

        rng = random.Random(seed)
        use_json = False
        json_payload: Dict[str, Any] = {}

        if json_mode in ("auto", "on"):
            is_valid_json, parsed_payload, json_error = _try_parse_json_dict(positive_prompt)
            if is_valid_json:
                use_json = True
                json_payload = parsed_payload
            elif json_mode == "on":
                logger.warning("JSON mode enabled, but positive_prompt is invalid JSON: %s", json_error)
                debug_lines.append(f"[JSON Parse Error]: {json_error}")
                final_negative = combine_negative_prompts(
                    extracted_neg="",
                    base_neg_input=negative_prompt,
                    mode=negative_mode,
                    rng=rng,
                )
                debug_info = (
                    "\n\n".join(debug_lines) + "\n\n"
                    f"Combinations: 0\n\n"
                    f"[Resolved Positive Output]:\n{positive_prompt}\n\n"
                    f"[Resolved Negative Output]:\n{final_negative}"
                )
                return (positive_prompt, final_negative, 0, debug_info)

        if use_json:
            if isinstance(json_payload.get("__moss_ide_prompt__"), str) and isinstance(
                json_payload.get("spatial_layout"), dict
            ):
                final_positive, extracted_negative, pos_combos = _resolve_moss_ide_envelope(
                    json_payload["__moss_ide_prompt__"],
                    json_payload["spatial_layout"],
                    rng,
                    debug_lines,
                )
            else:
                extracted_negatives: List[str] = []
                combos_acc = [1]
                resolved_payload = _resolve_json_value(
                    json_payload,
                    rng,
                    "",
                    extracted_negatives,
                    debug_lines,
                    combos_acc,
                )
                final_positive = json.dumps(resolved_payload, ensure_ascii=False, separators=(",", ":"))
                extracted_negative = ", ".join(extracted_negatives)
                pos_combos = combos_acc[0]
        else:
            syntax_pos = check_prompt_syntax(positive_prompt)
            if not syntax_pos.is_valid:
                logger.warning("Positive prompt syntax issues:\n%s", "\n".join(syntax_pos.errors))
                debug_lines.append("[Positive Prompt Syntax Issues]:\n" + "\n".join(syntax_pos.errors))

            pos_ast = parse_prompt_to_ast(positive_prompt)
            final_positive, extracted_negative = resolve_ast_to_prompt(pos_ast, rng)
            pos_combos = count_ast_combinations(pos_ast)

        # Combine extracted negative tags with negative_prompt field
        final_negative = combine_negative_prompts(
            extracted_neg=extracted_negative,
            base_neg_input=negative_prompt,
            mode=negative_mode,
            rng=rng
        )

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
