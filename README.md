# Expert Text Prompt for ComfyUI

A powerful ComfyUI custom node with AST-based parsing, advanced wildcards, probabilistic weighting, skip chances, prompt grouping, dual positive/negative outputs, inline negative extraction (`-`), `$negative` placeholder injection, and inline Mute/Solo controls.

---

## Features

- **Dual Outputs**: Directly feeds both `positive` and `negative` conditioning inputs from a single prompt structure.
- **Inline Negative Prefix (`-`)**: Prefix any tag or wildcard option with `-` (e.g. `-sunglasses`, `-umbrella`) to automatically route it into the `negative` output.
- **`$negative` Placeholder Injection**: Place `$negative` anywhere in your negative prompt text field to define the exact spot where extracted `-` tags are injected.
- **Flexible Negative Modes**:
  - `auto (use $negative)`: Injects into `$negative` if present, otherwise prepends.
  - `prepend`: Always places extracted negative tags at the very start.
  - `append`: Always appends extracted negative tags at the very end.
  - `replace`: Replaces the negative prompt field completely.
- **Advanced Wildcards**: `{option1 | option2 | option3}`
- **Probabilistic Weighting**: `{70% blue eyes | 30% green eyes}`
- **Skip Chance (Optional Tags)**: `{20%? optional sunglasses}` (20% chance to skip the tag completely)
- **Prompt Grouping**: `[GRP:NAME]` for clean prompt organization. Groups can also be muted (`//[GRP:NAME]`) or set to solo (`![GRP:NAME]`).
- **Inline Mute (`//`)**: Disable specific tags or entire prompt groups without deleting them.
- **Inline Solo (`!`)**: Isolate specific tags or groups, ignoring everything else in the prompt.
- **SDXL Weights & LoRAs**: Native support for `(tag:1.2)` and `<lora:name:1.0>`.
- **Deterministic Seed**: Reproducible wildcard selection based on input seed.
- **Visual Syntax Check**: Node background highlights in dark red if brackets `()`, `{}` or `[]` are mismatched or unclosed.

---

## Installation

Navigate to your ComfyUI `custom_nodes` directory and clone this repository:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/v3rm1ll1on/comfyi_variable_prompt.git
```

Restart ComfyUI afterward.

---

## Finding the Node in ComfyUI

- **Node Name**: `Expert Text Prompt (Wildcards & AST)`
- **Category**: `prompt/expert`

---

## Syntax & Examples

### 1. Dual Prompt & Inline Negative (`-` & `$negative`)

- **`positive_prompt`**:
  ```text
  [GRP:CHARACTER], portrait of a young woman, {70% sunny day, -sunglasses | 30% rainy day, -umbrella}, leather jacket
  ```
- **`negative_prompt`**:
  ```text
  (3d render, cgi, plastic skin:1.3), $negative, (deformed hands:1.2), blurry
  ```

**Resulting Outputs:**
- If `sunny day` is selected:
  - `positive`: `portrait of a young woman, sunny day, leather jacket`
  - `negative`: `(3d render, cgi, plastic skin:1.3), sunglasses, (deformed hands:1.2), blurry`
- If `rainy day` is selected:
  - `positive`: `portrait of a young woman, rainy day, leather jacket`
  - `negative`: `(3d render, cgi, plastic skin:1.3), umbrella, (deformed hands:1.2), blurry`

---

### 2. Wildcards with Weighted Probabilities
Specify explicit chances for each option:
```text
a {70% cyberpunk female hacker | 30% futuristic street runner}
```

### 3. Skip Chance (Optional Tags)
Prepend `X%?` inside a wildcard block to specify the probability that the enclosed tags will be skipped:
```text
{20%? glowing neon face tattoos}
```
*(20% chance to omit the tag entirely, 80% chance to include it).*

### 4. Mute & Solo Controls (`//` & `!`)

- **Mute (`//`)**: Disables a tag or group without removing it from your text:
  ```text
  masterpiece, // ruined background, leather jacket
  ```
- **Solo (`!`)**: Temporarily ignores all non-solo tags in the prompt and focuses strictly on the solo tag:
  ```text
  red dress, blue shoes, ! golden necklace
  ```
  *(Resulting output: `golden necklace`)*

### 5. Grouping (`[GRP:NAME]`)
Structure your prompts into logical blocks. Groups can also be muted or set to solo:
```text
[GRP:QUALITY], (masterpiece:1.2), ultra-detailed,

[GRP:CHARACTER], cyberpunk girl, neon hair,

//[GRP:BACKGROUND], city skyline at dusk
```

---

## Node Parameters & Outputs

- **Inputs**:
  - `positive_prompt`: Main prompt text supporting wildcards, Mute/Solo, weights, and `-` negative tags.
  - `negative_prompt`: Standard negative prompt field supporting `$negative` placeholder injection.
  - `negative_mode`: Options: `auto (use $negative)`, `prepend`, `append`, `replace`.
  - `seed`: Controls the random seed for reproducible wildcard selections.
- **Outputs**:
  - `positive`: Connects to `CLIP Text Encode (Positive)`.
  - `negative`: Connects to `CLIP Text Encode (Negative)`.

---

## License

MIT
