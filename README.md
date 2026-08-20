# Expert Text Prompt for ComfyUI

A powerful ComfyUI custom node featuring AST-based prompt parsing, advanced wildcards, probabilistic weighting, skip chances, prompt grouping, dual positive/negative outputs, inline negative extraction (`-`), `$negative` placeholder injection, and inline Mute/Solo controls.

---

## Features

- **Advanced Wildcards**: `{option1 | option2 | option3}` with full support for nested wildcards.
  - **Equal Chances**: `{red | blue | green}` assigns an equal chance to each option.
  - **Weighted Chances**: `{70% blue | 30% green}` sets explicit relative probabilities.
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
- **Number Range Wildcards (`{MIN-MAX:STEP}`)**: `{18-50}` randomly selects a number in range. Supports optional steps like `{0-10:2}` (chooses from `0, 2, 4, 6, 8, 10`).
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

## Full Syntax Reference (Cheat Sheet)

| Feature | Syntax Example | Description |
| :--- | :--- | :--- |
| **Basic Wildcard** | `{red \| blue \| green}` | Pick one option randomly with equal chance. |
| **Weighted Wildcard** | `{70% blue \| 20% green \| 10% red}` | Assign custom percentage probabilities per option. |
| **Skip Chance (Optional)** | `{20%? sunglasses}` | 20% chance to omit tag completely (80% chance to include). |
| **Number Range** | `{18-50}` | Random integer between min (18) and max (50). |
| **Number Range with Step** | `{1980-2020:5}` | Pick random integer with step (`1980, 1985, ..., 2020`). |
| **Nested Wildcards** | `{60% female, {70% armor \| 30% suit} \| 40% male}` | Multi-level wildcard nesting with combined probabilities. |
| **Inline Mute Tag** | `// leather jacket` | Temporarily deactivates tag without deleting it. |
| **Inline Solo Tag** | `! red dress` | Isolates marked tags. Non-solo tags are ignored. |
| **Prompt Group** | `[GRP:NAME], tag1, tag2` | Groups tags into a structured, manageable block. |
| **Mute / Solo Group** | `//[GRP:NAME]` or `![GRP:NAME]` | Mutes (`//`) or Solos (`!`) an entire named group. |
| **Inline Negative Extraction** | `-sunglasses` | Automatically extracts tag to negative output (removes from positive). |
| **Negative Placeholder** | `$negative` | Specifies exact insertion point for `-` tags in `negative_prompt`. |
| **SDXL Weights & LoRAs** | `(masterpiece:1.2)`, `<lora:name:1.0>` | Preserves weight syntax and LoRA tags natively. |

---

## Usage Examples & Templates

We provide a dedicated [`examples/`](./examples) directory with detailed Markdown templates ordered from beginner to masterclass:

| Example File | Topic & Level | Description |
| :--- | :--- | :--- |
| **[`01_basic_wildcard.md`](./examples/01_basic_wildcard.md)** | Beginner | Step-by-step introduction from single wildcards to nested wildcard structures. |
| **[`02_intermediate_groups_and_weights.md`](./examples/02_intermediate_groups_and_weights.md)** | Intermediate | Percentage weighting (`70%`), skip chances (`20%?`), and introducing groups (`[GRP:]`). |
| **[`03_advanced_pony_v6_template.md`](./examples/03_advanced_pony_v6_template.md)** | Advanced | Specialized templates for Pony Diffusion V6 with score groups & anime styles. |
| **[`04_expert_photorealistic_dual_prompt.md`](./examples/04_expert_photorealistic_dual_prompt.md)** | Expert | Photorealistic templates combining `-` negative extraction and `$negative`. |
| **[`05_mute_and_solo_indepth.md`](./examples/05_mute_and_solo_indepth.md)** | In-Depth Guide | Tag-level and group-level Mute (`//`) & Solo (`!`) isolation workflows. |
| **[`06_nested_wildcards_indepth.md`](./examples/06_nested_wildcards_indepth.md)** | In-Depth Guide | 2-Level and 3-Level wildcard nesting in plain text and group contexts. |
| **[`07_masterclass_character_generator.md`](./examples/07_masterclass_character_generator.md)** | Masterclass | Full production template for multi-ethnic, hyper-realistic character generation. |

---

### Quick Syntax Summary

### 1. Basic Wildcards
Randomly choose between simple options with equal probability:
```text
a photo of a {cat | dog | fox} sitting on a bench
```

### 2. Weighted Chances
Explicitly set selection probabilities for each option:
```text
a photo of a girl with {70% blue eyes | 20% green eyes | 10% brown eyes}
```

### 3. Skip Chance (Optional Tags)
Add optional elements with a percentage chance of skipping:
```text
portrait of a woman, {20%? glowing neon face tattoos}
```
*(20% chance to omit the tag entirely, 80% chance to include it).*

### 4. Number Range Wildcards (`{MIN-MAX:STEP}`)
Generate random numeric values across a range with optional step increments:
```text
a photo of a {18-50} yo woman born in {1980-2020:5}
```
*(Chooses an age between 18 and 50, and a year from `[1980, 1985, 1990, ..., 2020]`).*

### 5. Mute & Solo Controls (`//` & `!`)
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
