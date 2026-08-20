import re
import random
from typing import List, Optional, Tuple, Dict, Any


class ASTNode:
    def __init__(self, is_muted: bool = False, is_solo: bool = False, is_negative: bool = False, prefix_separator: str = ""):
        self.is_muted = is_muted
        self.is_solo = is_solo
        self.is_negative = is_negative
        self.prefix_separator = prefix_separator  # "", " ", ","


class ASTTag(ASTNode):
    def __init__(self, text: str, weight: float = 1.0, is_lora: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.weight = weight
        self.is_lora = is_lora


class ASTWildcardOption:
    def __init__(self, prob_weight: Optional[float], nodes: List[ASTNode]):
        self.prob_weight = prob_weight
        self.nodes = nodes


class ASTWildcard(ASTNode):
    def __init__(self, skip_chance: Optional[float], options: List[ASTWildcardOption], **kwargs):
        super().__init__(**kwargs)
        self.skip_chance = skip_chance
        self.options = options


class ASTGroup:
    def __init__(self, name: str, nodes: List[ASTNode], is_muted: bool = False, is_solo: bool = False, is_negative: bool = False):
        self.name = name
        self.nodes = nodes
        self.is_muted = is_muted
        self.is_solo = is_solo
        self.is_negative = is_negative


def parse_sdxl_weight(text: str) -> Tuple[str, float]:
    match = re.match(r"^\((.+):([0-9.]+)\)$", text.strip())
    if match:
        return match.group(1), float(match.group(2))
    return text.strip(), 1.0


def format_sdxl_weight(text: str, weight: float) -> str:
    if abs(weight - 1.0) < 1e-6:
        return text
    formatted_weight = f"{weight:.2f}".rstrip('0').rstrip('.')
    return f"({text}:{formatted_weight})"


class SyntaxCheckResult:
    def __init__(self, is_valid: bool, errors: List[str]):
        self.is_valid = is_valid
        self.errors = errors


def check_prompt_syntax(text: str) -> SyntaxCheckResult:
    errors = []
    stack = []
    
    for idx, char in enumerate(text):
        if char in "({[":
            stack.append((char, idx))
        elif char in ")}]":
            expected = {"}": "{", ")": "(", "]": "["}[char]
            if not stack:
                errors.append(f"Unmatched closing bracket '{char}' at position {idx}")
            elif stack[-1][0] != expected:
                errors.append(f"Mismatched bracket '{char}' at position {idx}, expected closing for '{stack[-1][0]}' from position {stack[-1][1]}")
                stack.pop()
            else:
                stack.pop()
                
    for char, idx in stack:
        errors.append(f"Unclosed opening bracket '{char}' at position {idx}")
        
    return SyntaxCheckResult(is_valid=len(errors) == 0, errors=errors)


class PromptParser:
    def __init__(self, input_str: str):
        self.input = input_str
        self.pos = 0

    def peek(self) -> Optional[str]:
        return self.input[self.pos] if self.pos < len(self.input) else None

    def advance(self):
        self.pos += 1

    def match(self, target: str) -> bool:
        if self.input.startswith(target, self.pos):
            self.pos += len(target)
            return True
        return False

    def skip_whitespace(self):
        while self.pos < len(self.input) and self.input[self.pos].isspace():
            self.pos += 1

    def parse_nodes_until(self, stop_tokens: List[str]) -> List[ASTNode]:
        nodes = []
        self.skip_whitespace()
        last_char = ""
        inherited_solo = False
        inherited_muted = False
        inherited_negative = False

        while self.pos < len(self.input):
            should_stop = any(self.input.startswith(tok, self.pos) for tok in stop_tokens)
            if should_stop:
                break

            if self.match(","):
                last_char = ","
                inherited_solo = False
                inherited_muted = False
                inherited_negative = False
                self.skip_whitespace()
                continue

            node = self.parse_node(last_char, inherited_solo, inherited_muted, inherited_negative)
            if node:
                nodes.append(node)
                inherited_solo = node.is_solo
                inherited_muted = node.is_muted
                inherited_negative = node.is_negative

            prev_pos = self.pos
            self.skip_whitespace()

            if self.match(","):
                last_char = ","
                inherited_solo = False
                inherited_muted = False
                inherited_negative = False
                self.skip_whitespace()
            else:
                was_whitespace = prev_pos > 0 and self.input[prev_pos - 1].isspace()
                last_char = " " if (self.pos > prev_pos or was_whitespace) else ""

        return nodes

    def parse_node(self, last_char: str = "", inherited_solo: bool = False, inherited_muted: bool = False, inherited_negative: bool = False) -> Optional[ASTNode]:
        prefix_separator = last_char if last_char in " \t\n\r," else ""
        self.skip_whitespace()

        if self.pos >= len(self.input):
            return None

        is_muted = inherited_muted
        is_solo = inherited_solo
        is_negative = inherited_negative

        if self.match("!"):
            is_solo = True
            self.skip_whitespace()
        elif self.match("//_S_"):
            self.skip_whitespace()
        elif self.match("//"):
            is_muted = True
            self.skip_whitespace()

        if self.match("-") and not (self.peek() and self.peek().isdigit()):
            is_negative = True
            self.skip_whitespace()

        if self.peek() == "{":
            wildcard = self.parse_wildcard()
            if wildcard:
                wildcard.is_muted = is_muted
                wildcard.is_solo = is_solo
                wildcard.is_negative = is_negative
                wildcard.prefix_separator = prefix_separator
                return wildcard

        text = ""
        paren_depth = 0

        while self.pos < len(self.input):
            char = self.peek()
            if char == "(":
                paren_depth += 1
            elif char == ")":
                if paren_depth > 0:
                    paren_depth -= 1

            if char in "{}" or char == "\n" or self.input.startswith("[GRP:", self.pos):
                break
            if char in ",|" and paren_depth == 0:
                break

            text += char
            self.advance()

        text = text.strip()
        if not text:
            return None

        is_lora = text.startswith("<lora:") and text.endswith(">")
        base_text, weight = parse_sdxl_weight(text)

        return ASTTag(
            text=text if is_lora else base_text,
            weight=1.0 if is_lora else weight,
            is_lora=is_lora,
            is_muted=is_muted,
            is_solo=is_solo,
            is_negative=is_negative,
            prefix_separator=prefix_separator
        )

    def parse_wildcard(self) -> Optional[ASTWildcard]:
        self.match("{")
        self.skip_whitespace()

        skip_chance = None
        remaining = self.input[self.pos:]
        skip_match = re.match(r"^(\d+)%\?\s*", remaining)
        if skip_match:
            skip_chance = float(skip_match.group(1))
            self.pos += len(skip_match.group(0))

        options = []
        while self.pos < len(self.input) and self.peek() != "}":
            self.skip_whitespace()

            prob_weight = None
            rem_opt = self.input[self.pos:]
            prob_match = re.match(r"^(\d+)%\??\s*", rem_opt)
            if prob_match:
                prob_weight = float(prob_match.group(1))
                self.pos += len(prob_match.group(0))

            nodes = self.parse_nodes_until(["|", "}"])
            options.append(ASTWildcardOption(prob_weight=prob_weight, nodes=nodes))

            if self.peek() == "|":
                self.advance()

        if self.peek() == "}":
            self.advance()

        return ASTWildcard(skip_chance=skip_chance, options=options)


def parse_prompt_to_ast(text: str) -> List[ASTGroup]:
    group_regex = re.compile(r"(?:(-|\/\/_S_\s*|\/\/\s*|!))?\[GRP:([^\]]+)\]")
    matches = list(group_regex.finditer(text))
    parsed_groups = []
    last_idx = 0

    for m in matches:
        if m.start() > last_idx:
            content = text[last_idx:m.start()]
            if parsed_groups:
                parsed_groups[-1]["content"] += content
            elif content.strip():
                parsed_groups.append({"prefix": "", "name": "GENERAL", "content": content})

        parsed_groups.append({"prefix": m.group(1) or "", "name": m.group(2), "content": ""})
        last_idx = m.end()

    if last_idx < len(text):
        content = text[last_idx:]
        if parsed_groups:
            parsed_groups[-1]["content"] += content
        elif content.strip():
            parsed_groups.append({"prefix": "", "name": "GENERAL", "content": text})

    if not parsed_groups:
        parsed_groups.append({"prefix": "", "name": "GENERAL", "content": text})

    groups = []
    for g in parsed_groups:
        parser = PromptParser(g["content"])
        nodes = parser.parse_nodes_until([])

        is_solo = g["prefix"].startswith("!")
        is_muted = g["prefix"].startswith("//") and not g["prefix"].startswith("//_S_")
        is_negative = g["prefix"].startswith("-")

        groups.append(ASTGroup(name=g["name"], nodes=nodes, is_muted=is_muted, is_solo=is_solo, is_negative=is_negative))

    return groups


def build_text_with_separators(items: List[Tuple[str, str]]) -> str:
    """
    Kombiniert (Text, Separatortyp)-Tupel zu einem sauberen Satz oder Tag-String.
    Verhindert doppelte Kommas oder ungewollte Kommas in Fließtexten.
    """
    result = ""
    for idx, (text, sep) in enumerate(items):
        if not text:
            continue
        if idx == 0:
            result += text
        else:
            if sep == ",":
                result = result.rstrip(" ,") + ", " + text.lstrip(" ,")
            else:
                result = result.rstrip() + " " + text.lstrip()

    # Nachbereinigung von mehrfachen Kommas/Leerzeichen
    result = re.sub(r"\s*,\s*", ", ", result)
    result = re.sub(r" +,", ",", result)
    result = re.sub(r" +", " ", result)
    return result.strip(" ,")


def resolve_ast_to_prompt(groups: List[ASTGroup], rng: random.Random) -> Tuple[str, str]:
    has_solo = any(
        g.is_solo or any(n.is_solo for n in g.nodes)
        for g in groups
    )

    def is_node_active(node: ASTNode, group_is_solo: bool, group_is_muted: bool) -> bool:
        if group_is_muted or node.is_muted:
            return False
        if has_solo:
            return node.is_solo or group_is_solo
        return True

    resolved_positive: List[Tuple[str, str]] = []
    resolved_negative: List[Tuple[str, str]] = []

    for group in groups:
        if group.is_muted and not (has_solo and group.is_solo):
            continue

        for node in group.nodes:
            if not is_node_active(node, group.is_solo, group.is_muted):
                continue

            pos_tags, neg_tags = resolve_node(node, group.is_solo, group.is_muted, group.is_negative, rng, has_solo)
            resolved_positive.extend(pos_tags)
            resolved_negative.extend(neg_tags)

    pos_str = build_text_with_separators(resolved_positive)
    neg_str = build_text_with_separators(resolved_negative)
    return pos_str, neg_str


def resolve_node(node: ASTNode, parent_solo: bool, parent_muted: bool, parent_negative: bool, rng: random.Random, has_solo: bool) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    is_neg = node.is_negative or parent_negative
    sep = node.prefix_separator or " "

    if isinstance(node, ASTTag):
        text = node.text if node.is_lora else format_sdxl_weight(node.text, node.weight)
        if is_neg:
            return [], [(text, sep)]
        else:
            return [(text, sep)], []

    elif isinstance(node, ASTWildcard):
        if node.skip_chance is not None:
            roll = rng.uniform(0, 100)
            if roll < node.skip_chance:
                return [], []

        if not node.options:
            return [], []

        weights = [opt.prob_weight if opt.prob_weight is not None else 1.0 for opt in node.options]
        chosen_option = rng.choices(node.options, weights=weights, k=1)[0]

        sub_pos = []
        sub_neg = []
        for idx, child in enumerate(chosen_option.nodes):
            if child.is_muted:
                continue
            if has_solo and not (child.is_solo or parent_solo or node.is_solo):
                continue

            pos_tags, neg_tags = resolve_node(child, parent_solo or node.is_solo, parent_muted, is_neg, rng, has_solo)
            
            # Für das erste Kind in einer Wildcard übernehmen wir den Separator der Wildcard selbst
            if idx == 0 and pos_tags:
                pos_tags[0] = (pos_tags[0][0], sep)
            if idx == 0 and neg_tags:
                neg_tags[0] = (neg_tags[0][0], sep)

            sub_pos.extend(pos_tags)
            sub_neg.extend(neg_tags)

        return sub_pos, sub_neg

    return [], []


def combine_negative_prompts(extracted_neg: str, base_neg_input: str, mode: str, rng: random.Random) -> str:
    """
    Kombiniert extrahierte Negativ-Tags mit dem zweiten Negativ-Textfeld.
    Unterstützt den `$negative` Platzhalter sowie prepend, append, replace.
    """
    # 1. Parse base_neg_input durch AST
    if base_neg_input.strip():
        base_ast = parse_prompt_to_ast(base_neg_input)
        base_pos, extra_base_neg = resolve_ast_to_prompt(base_ast, rng)
        base_text = ", ".join(filter(None, [base_pos, extra_base_neg]))
    else:
        base_text = ""

    def clean_commas(text: str) -> str:
        text = re.sub(r"\s*,\s*,+", ",", text)
        text = re.sub(r"\s*,\s*", ", ", text)
        return text.strip(" ,")

    # Wenn der User explizit prepend, append oder replace wählt, $negative Platzhalter aus base_text entfernen
    if mode in ["prepend", "append", "replace"]:
        base_text = clean_commas(re.sub(r"\$negative\b", "", base_text))

    if not extracted_neg:
        return clean_commas(re.sub(r"\$negative\b", "", base_text))

    # Mode Handling:
    if mode == "auto (use $negative)" or mode == "auto":
        if "$negative" in base_text:
            res = base_text.replace("$negative", extracted_neg)
            return clean_commas(res)
        return clean_commas(f"{extracted_neg}, {base_text}")
    elif mode == "replace":
        return clean_commas(extracted_neg)
    elif mode == "append":
        return clean_commas(f"{base_text}, {extracted_neg}")
    else:  # prepend
        return clean_commas(f"{extracted_neg}, {base_text}")

