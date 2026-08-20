# Expert Text Prompt for ComfyUI

A powerful ComfyUI custom node featuring AST-based prompt parsing, advanced wildcards, probabilistic weighting, skip chances, prompt grouping, dual positive/negative outputs, inline negative extraction (`-`), `$negative` placeholder injection, and inline Mute/Solo controls.

---

## Features

- **Advanced Wildcards**: `{option1 | option2 | option3}` with full support for nested wildcards.
  - **Equal Weights**: `{red | blue | green}` assigns equal selection probability (`1.0`) to each option.
  - **Relative Weighting**: `{70% blue | 30% green}` or `{5% red | blue | green}` (unweighted options default to weight `1.0`, while `5%` sets a relative weight multiplier of `5.0`).
- **Skip Chance (Optional Tags)**: `{20%? optional sunglasses}` (20% chance to skip the tag completely).
- **Prompt Grouping**: `[GRP:NAME]` for organizing complex prompts. Groups can be muted (`//[GRP:NAME]`) or set to solo (`![GRP:NAME]`).
- **Inline Mute (`//`)**: Disable specific tags or entire prompt groups without deleting them. Multiple `//` tags can be used simultaneously.
- **Inline Solo (`!`)**: Isolate specific tags or groups, ignoring all non-solo elements. Multiple `!` tags can be used to keep a specific set of tags active.
- **Dual Outputs (`positive` & `negative`)**: Generates both positive and negative strings from a unified node setup.
- **Inline Negative Extraction (`-`)**: Prefix any tag or wildcard option with `-` (e.g., `-sunglasses`, `-umbrella`) to automatically route it into the `negative` output.
- **`$negative` Placeholder Injection**: Insert `$negative` into your negative prompt field to specify the exact location where extracted `-` tags are injected.
- **Flexible Negative Modes**:
  - `auto (use $negative)`: Injects extracted tags into the `$negative` placeholder if present, otherwise prepends them.
  - `prepend`: Places extracted negative tags at the very start.
  - `append`: Appends extracted negative tags at the very end.
  - `replace`: Overwrites the negative prompt field completely.
- **SDXL Weights & LoRAs**: Native preservation of `(tag:1.2)` weights and `<lora:name:1.0>` tags.
- **Deterministic Seed**: Reproducible wildcard resolution based on input seed.

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

## Usage Examples (From Basic to Expert)

### 1. Basic Wildcards
Randomly choose between simple options:
```text
a photo of a {cat | dog | fox} sitting on a bench
```

### 2. Equal vs. Relative Weights
Control the likelihood of specific choices:
```text
{5% rare red hair | blonde hair | brown hair | black hair}
```
*(Red hair is 5x more likely to be selected than any individual default hair color).*

### 3. Skip Chance (Optional Tags)
Add optional elements with a percentage chance of skipping:
```text
portrait of a woman, {20%? glowing neon face tattoos}
```
*(20% chance to omit the tag entirely, 80% chance to include it).*

### 4. Mute & Solo Controls (`//` & `!`)
Temporarily disable or isolate tags without editing your prompt text:
- **Mute (`//`)**: Deactivates specific tags (supports multiple `//` in one prompt):
  ```text
  masterpiece, // ruined background, leather jacket, // blurry lines
  ```
- **Solo (`!`)**: Isolates only marked tags (supports multiple `!` tags):
  ```text
  ! red dress, blue shoes, ! golden necklace
  ```
  *(Resulting output: `red dress, golden necklace`)*

### 5. Nested Wildcards & Probabilities
Combine multiple levels of wildcards for complex variation:
```text
a {60% female warrior with {70% knight armor | 30% cyber suit} | 40% cyberpunk rogue}
```

### 6. Prompt Grouping (`[GRP:NAME]`)
Structure large prompts into organized blocks that can be muted or soloed as a whole:
```text
[GRP:QUALITY], (masterpiece:1.2), ultra-detailed,

[GRP:CHARACTER], cyberpunk girl, neon hair,

//[GRP:BACKGROUND], city skyline at dusk
```

### 7. Expert Dual-Prompting with Inline Negative (`-` & `$negative`)
Combine positive wildcards, automatic negative extraction, and custom negative templates in one go:

**`positive_prompt`**:
```text
[GRP:CHARACTER], portrait of a young woman, {70% sunny day, -sunglasses | 30% rainy day, -umbrella}, leather jacket
```

**`negative_prompt`**:
```text
(3d render, cgi, plastic skin:1.3), $negative, (deformed hands:1.2), blurry
```

**Output Results:**
- If `sunny day` is selected by the seed:
  - `positive`: `portrait of a young woman, sunny day, leather jacket`
  - `negative`: `(3d render, cgi, plastic skin:1.3), sunglasses, (deformed hands:1.2), blurry`
- If `rainy day` is selected by the seed:
  - `positive`: `portrait of a young woman, rainy day, leather jacket`
  - `negative`: `(3d render, cgi, plastic skin:1.3), umbrella, (deformed hands:1.2), blurry`

---

## Node Parameters & Outputs

- **Inputs**:
  - `positive_prompt`: Main prompt text supporting wildcards, Mute/Solo, weights, and `-` negative tags.
  - `negative_prompt`: Secondary prompt field supporting the `$negative` placeholder.
  - `negative_mode`: Options: `auto (use $negative)`, `prepend`, `append`, `replace`.
  - `seed`: Random seed for reproducible wildcard selections.
- **Outputs**:
  - `positive`: Connects to `CLIP Text Encode (Positive)`.
  - `negative`: Connects to `CLIP Text Encode (Negative)`.

---

## License

MIT
