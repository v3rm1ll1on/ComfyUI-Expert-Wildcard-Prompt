# Expert Text Prompt Examples Library

Welcome to the official example library for the **ComfyUI Expert Text Prompt Node**. 
This directory contains production-ready templates and step-by-step guides ranging from basic wildcard usages to advanced masterclass prompt structures.

---

## 📚 Examples Directory

| File | Level | Focus / Features Demonstrated |
| :--- | :--- | :--- |
| **[01 - Basic Wildcards](./01_basic_wildcard.md)** | 🟢 Beginner | Simple options `{cat \| dog}`, probabilities `{70% A \| 30% B}`, skip-chances `{30%? tag}`. |
| **[02 - Groups & Weights](./02_intermediate_groups_and_weights.md)** | 🟡 Intermediate | Grouping `[GRP:NAME]`, SDXL weights `(tag:1.2)`, LoRAs `<lora:name:1.0>`. |
| **[03 - Pony V6 Template](./03_advanced_pony_v6_template.md)** | 🟠 Advanced | Pony V6 score tags, source rating wildcards, dual-output negative routing (`-`). |
| **[04 - Photorealistic Dual-Prompt](./04_expert_photorealistic_dual_prompt.md)** | 🔴 Expert | High-end 35mm photorealism, `$negative` placeholder injection, group muting. |
| **[05 - Mute & Solo In-Depth](./05_mute_and_solo_indepth.md)** | 🔬 In-Depth | Detailed guide on Inline Muting (`//`) and Rapid Focus Testing (`!`). |
| **[06 - Nested Wildcards In-Depth](./06_nested_wildcards_indepth.md)** | 🔬 In-Depth | 2-level and 3-level deep wildcard nesting, option-level probabilities, and skip-chances. |
| **[07 - Masterclass Character Generator](./07_masterclass_character_generator.md)** | 👑 Masterclass | Full character generator combining all node features into a single modular template. |

---

## 🚀 How to Use These Examples

1. **Copy the Positive Prompt** block into the `positive_prompt` field of your Expert Text Prompt Node.
2. **Copy the Negative Prompt** block into the `negative_prompt` field.
3. Keep `negative_mode` set to `auto (use $negative)` so that any inline negative tags prefixed with `-` (e.g. `-glasses`) are automatically injected into the `$negative` placeholder!
