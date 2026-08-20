# 05 - Mute & Solo In-Depth Examples

Detailed examples demonstrating how Inline Mute (`//`), Inline Solo (`!`), and Inline Negative (`-`) interact in production scenarios—both with and without Groups.

---

### Step 1: Tag-Level Muting (`//`) without Groups
Deactivate specific tags directly in the prompt flow without needing groups. Inline negative tags (`-`) on muted items are also safely ignored.

#### Positive Prompt
```text
RAW photo, 8k, photorealistic, // ruined background, portrait of a young woman, // red hair, blonde hair, leather jacket, -sunglasses
```

#### Negative Prompt Template
```text
(3d render, cgi, illustration:1.3), $negative, (deformed:1.2), blur
```

#### Expected Generated Output
* **Positive Prompt:** `RAW photo, 8k, photorealistic, portrait of a young woman, blonde hair, leather jacket`
* **Negative Prompt:** `(3d render, cgi, illustration:1.3), sunglasses, (deformed:1.2), blur`
* **Explanation:** Muted tags (`// ruined background`, `// red hair`) are completely skipped during resolution.

---

### Step 2: Tag-Level Solo (`!`) for Rapid Detail Testing (without Groups)
Isolate specific tags to quickly test LoRAs or specific detail rendering. When any `!` is active anywhere in the prompt, all unflagged elements and their negative tags are bypassed.

#### Positive Prompt
```text
masterpiece, ultra-detailed, red dress, -tight clothes, ! golden necklace, ! blue eyes, freckles, -pale skin, busy city street, -crowd
```

#### Negative Prompt Template
```text
(bad quality:1.4), $negative, (deformed hands:1.2)
```

#### Expected Generated Output
* **Positive Prompt:** `golden necklace, blue eyes`
* **Negative Prompt:** `(bad quality:1.4), (deformed hands:1.2)`
* **Explanation:** Only `golden necklace` and `blue eyes` have the `!` flag. Non-solo tags (`freckles`, `red dress`) and non-solo negative tags (`-tight clothes`, `-crowd`) are bypassed.

---

### Step 3: Tag & Group Muting (`//[GRP:NAME]`)
Structure larger prompts into groups and mute entire sections at once:

#### Positive Prompt
```text
[GRP:STYLE], RAW photo, 8k, photorealistic, // ruined background,
[GRP:SUBJECT], portrait of a young woman, // red hair, blonde hair, leather jacket, -sunglasses,
//[GRP:EXPERIMENTAL_LIGHTING], neon rim light, -dramatic shadows
```

#### Negative Prompt Template
```text
(3d render, cgi, illustration:1.3), $negative, (deformed:1.2), blur
```

#### Expected Generated Output
* **Positive Prompt:** `RAW photo, 8k, photorealistic, portrait of a young woman, blonde hair, leather jacket`
* **Negative Prompt:** `(3d render, cgi, illustration:1.3), sunglasses, (deformed:1.2), blur`
* **Explanation:** Muted tags (`ruined background`, `red hair`) and the muted group (`EXPERIMENTAL_LIGHTING`) are ignored. The `-dramatic shadows` tag inside the muted group is suppressed, leaving only `-sunglasses` in `$negative`.

---

### Step 4: Group-Level Solo (`![GRP:NAME]`)
Isolate an entire functional area (like character features or lighting) with a single `!` on the group header.

#### Positive Prompt
```text
[GRP:STYLE], RAW photo, 35mm lens,
![GRP:SUBJECT], cybernetic warrior, glowing eyes, -glasses,
[GRP:ENVIRONMENT], neon city street, -sunlight
```

#### Negative Prompt Template
```text
(low quality:1.4), $negative, (blurry:1.2)
```

#### Expected Generated Output
* **Positive Prompt:** `cybernetic warrior, glowing eyes`
* **Negative Prompt:** `(low quality:1.4), glasses, (blurry:1.2)`
* **Explanation:** `![GRP:SUBJECT]` solomarks the entire subject group. `GRP:STYLE` and `GRP:ENVIRONMENT` are bypassed, so `-sunlight` is suppressed while `-glasses` is extracted into `$negative`.

---

### Step 5: Mute & Solo Inside Nested Wildcards
Apply Mute (`//`), Solo (`!`), and Negative (`-`) directly onto wildcard options for granular control.

#### Positive Prompt
```text
masterpiece, RAW photo of a woman in {70% leather jacket, -glasses | 30% !{100% golden cybernetic armor, -helmet | 0% silver suit}}, {50% standing in alley | 50% //{100% inside server room, -wires}}
```

#### Negative Prompt Template
```text
(3d render:1.3), $negative, (deformed:1.2)
```

#### Expected Generated Output (Scenario 1 - Golden Cybernetic Armor Solo Rolled):
* **Positive Prompt:** `golden cybernetic armor`
* **Negative Prompt:** `(3d render:1.3), helmet, (deformed:1.2)`

#### Expected Generated Output (Scenario 2 - Standard Leather Jacket Rolled):
* **Positive Prompt:** `masterpiece, RAW photo of a woman in leather jacket, standing in alley`
* **Negative Prompt:** `(3d render:1.3), glasses, (deformed:1.2)`
