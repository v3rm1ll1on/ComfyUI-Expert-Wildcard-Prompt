# 05 - Mute & Solo In-Depth Examples

Detailed examples demonstrating how Inline Mute (`//`) and Inline Solo (`!`) work in practice.

---

### Example A: Temporary Tag Testing with Mute (`//`)
Deactivate specific tags or groups without deleting them from your prompt.

```text
[GRP:STYLE], RAW photo, 8k, photorealistic, // ruined background,
[GRP:SUBJECT], portrait of a young woman, // red hair, blonde hair, leather jacket,
//[GRP:EXPERIMENTAL_LIGHTING], // neon rim light, // dramatic shadows
```

**Output Result:**
- Muted tags (`ruined background`, `red hair`) and muted groups (`EXPERIMENTAL_LIGHTING`) are completely ignored.
- Result: `RAW photo, 8k, photorealistic, portrait of a young woman, blonde hair, leather jacket`

---

### Example B: Rapid Focus Testing with Single & Multi-Solo (`!`)
Isolate a specific element or a combination of elements to quickly test LORAs or details. Everything without `!` is temporarily ignored.

```text
[GRP:QUALITY], masterpiece, ultra-detailed,
[GRP:CLOTHING], red dress, blue shoes, ! golden necklace,
[GRP:FACE], ! blue eyes, freckles,
[GRP:BG], busy city street
```

**Output Result:**
- Only tags marked with `!` (`golden necklace`, `blue eyes`) will be included. All other tags are bypassed.
- Result: `golden necklace, blue eyes`

---

### Example C: Mute & Solo Inside Wildcards
Use Mute and Solo inside wildcard blocks for granular control.

```text
a photo of a woman in {70% leather jacket | 30% ! golden armor}, {// 100%? sunglasses | 100%? scarf}
```

**Output Result:**
- If `golden armor` is rolled, its `!` puts it in Solo mode.
- Muted skip-chances (`// 100%? sunglasses`) are disabled.
