# Expert Text Prompt for ComfyUI

A powerful ComfyUI custom node with AST-based parsing, advanced wildcards, probabilistic weighting, skip chances, prompt grouping, and inline Mute/Solo controls.

---

## Features

- Advanced Wildcards: `{option1 | option2 | option3}`
- Probabilistic Weighting: `{70% blue eyes | 30% green eyes}`
- Skip Chance (Optional Tags): `{20%? optional sunglasses}` (20% chance to skip the tag completely)
- Prompt Grouping: `[GRP:NAME]` for clean prompt organization
- Inline Mute (`//`): Disable specific tags or entire prompt groups without deleting them
- Inline Solo (`!`): Isolate specific tags or groups, ignoring everything else in the prompt
- SDXL Weights & LoRAs: Native support for `(tag:1.2)` and `<lora:name:1.0>`
- Deterministic Seed: Reproducible wildcard selection based on input seed

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

- Node Name: `Expert Text Prompt (Wildcards & AST)`
- Category: `prompt/expert`

---

## Syntax & Examples

### 1. Wildcards with Weighted Probabilities
Specify explicit chances for each option:
```text
a {70% cyberpunk female hacker | 30% futuristic street runner}
```

### 2. Skip Chance (Optional Tags)
Prepend `X%?` inside a wildcard block to specify the probability that the enclosed tags will be skipped:
```text
{20%? glowing neon face tattoos}
```
*(20% chance to omit the tag entirely, 80% chance to include it).*

### 3. Mute & Solo Controls (`//` & `!`)

- Mute (`//`): Disables a tag or group without removing it from your text:
  ```text
  masterpiece, // ruined background, leather jacket
  ```
- Solo (`!`): Temporarily ignores all non-solo tags in the prompt and focuses strictly on the solo tag:
  ```text
  red dress, blue shoes, ! golden necklace
  ```
  *(Resulting output: `golden necklace`)*

### 4. Grouping (`[GRP:NAME]`)
Structure your prompts into logical blocks. Groups can also be muted or set to solo:
```text
[GRP:QUALITY], (masterpiece:1.2), ultra-detailed,

[GRP:CHARACTER], cyberpunk girl, neon hair,

//[GRP:BACKGROUND], city skyline at dusk
```

---

## Complex Prompt Example

```text
[GRP:QUALITY], (masterpiece:1.2), (best quality:1.2), ultra-detailed, 8k resolution, photorealistic, <lora:cyberpunk_style_v1:0.8>,

[GRP:CHARACTER], a {60% cyberpunk female hacker | 40% futuristic street runner}, (detailed face:1.15), {70% glowing cybernetic eye implants | 30% futuristic visor}, {15%? glowing neon face tattoos}, {50% neon blue hair, braided ponytail | 35% short pink undercut hair | 15% silver bob hair},

[GRP:CLOTHING], wearing {50% high-tech tactical jacket, leather straps | 50% sleek sci-fi bodysuit, illuminated seams}, // old ruined jacket, {30%? fingerless cyber gloves},

[GRP:SETTING], standing in a {80% rain-slicked cyberpunk alleyway, neon signs reflections | 20% high-tech server control room, holographic displays}, volumetric lighting, fog, dramatic rim light, cinematic night scene
```

---

## Node Parameters

- `text`: Your prompt string leveraging the extended syntax.
- `seed`: Controls the random number generator for wildcard resolutions. Using the same seed guarantees identical wildcard selections.

---

## License

MIT
