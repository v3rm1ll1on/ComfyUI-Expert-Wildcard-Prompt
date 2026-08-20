# 05 - Mute & Solo In-Depth Examples

Detailed examples demonstrating how Inline Mute (`//`), Inline Solo (`!`), and Inline Negative (`-`) interact in production scenarios.

---

### Example A: Tag & Group Muting (`//`) with Dual Output
Deactivate specific tags or entire groups without deleting them from your template. Inline negative tags (`-`) inside muted blocks are also safely ignored.

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
* **Explanation:** Muted tags (`ruined background`, `red hair`) and the muted group (`EXPERIMENTAL_LIGHTING`) are ignored. The `-dramatic shadows` tag inside the muted group is also suppressed, leaving only `-sunglasses` in `$negative`.

---

### Example B: Rapid Focus Testing with Solo (`!`)
Isolate specific tags or groups to quickly test LoRAs or detail rendering. When any `!` is active, all unflagged elements and their negative tags are bypassed.

#### Positive Prompt
```text
[GRP:QUALITY], masterpiece, ultra-detailed,
[GRP:CLOTHING], red dress, -tight clothes, ! golden necklace,
[GRP:FACE], ! blue eyes, freckles, -pale skin,
[GRP:BG], busy city street, -crowd
```

#### Negative Prompt Template
```text
(bad quality:1.4), $negative, (deformed hands:1.2)
```

#### Expected Generated Output
* **Positive Prompt:** `golden necklace, blue eyes`
* **Negative Prompt:** `(bad quality:1.4), (deformed hands:1.2)`
* **Explanation:** Only `golden necklace` and `blue eyes` have the `!` flag, so only they are included. Because non-solo groups are bypassed, negative tags in those groups (`-tight clothes`, `-crowd`) are not extracted, resulting in a clean base negative.

---

### Example C: Mute & Solo Inside Nested Wildcards
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

---

### Example D: Group-Level Solo (`![GRP:NAME]`)
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
* **Explanation:** `![GRP:SUBJECT]` solomarks the entire subject group. `GRP:STYLE` and `GRP:ENVIRONMENT` are bypassed, so `-sunlight` is suppressed while `-glasses` is routed into `$negative`.
