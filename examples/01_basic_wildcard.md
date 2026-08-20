# 01 - Basic & Nested Wildcards (Beginner Level)

Learn the core wildcard mechanics step-by-step—from simple single-level choice lists to nested wildcard combinations.

> [!NOTE]
> All wildcards use curly braces `{option A | option B}` and pick exactly one item per execution based on the seed. You do **not** need prompt groups (`[GRP:]`) or advanced syntax to start using wildcards!

---

### Step 1: Single Wildcard (Simple Option Selection)

Randomly choose one subject out of a list:

**Positive Prompt**
```text
a photo of a {cat | dog | red panda | fox} sitting on a wooden bench in a park
```

**Negative Prompt**
```text
(3d render, cgi:1.3), (deformed hands:1.2), blurry
```

---

### Step 2: Multiple Independent Wildcards

Combine multiple wildcards in one prompt to generate combinatorial variations (Subject × Weather × Environment):

**Positive Prompt**
```text
majestic mountain peak, {sunset sky | stormy dramatic clouds | misty foggy morning | aurora borealis night}, {crystal clear river | ancient pine forest | dramatic canyon}, 8k resolution, photorealistic
```

**Negative Prompt**
```text
blurry, low quality, oversaturated
```

---

### Step 3: Introduction to Nested Wildcards

Wildcards can be placed inside other wildcards. This allows sub-variations depending on which main option gets chosen!

**Positive Prompt**
```text
a sleek futuristic {sports car, {red metallic paint | neon blue stripes} | hoverbike, {chrome finish | rusty wasteland design} | space shuttle}, parked in a sci-fi hangar, cinematic lighting
```

**What happens here:**
- If `sports car` is picked, it randomly chooses between `red metallic paint` or `neon blue stripes`.
- If `hoverbike` is picked, it chooses between `chrome finish` or `rusty wasteland design`.
- If `space shuttle` is picked, no additional sub-option is added.

**Negative Prompt**
```text
low quality, 3d render, distorted
```

---

### Step 4: Multi-Level Nested Variations (Character Concept)

Build rich character variations with multi-layered details without needing complex grouping logic:

**Positive Prompt**
```text
portrait of a {fantasy elf warrior with {golden armor | leather tunic, -cape} | cyberpunk cyborg with {glowing visor | cybernetic arm}}, {autumn forest backdrop | neon city alleyway}, masterpiece, detailed face
```

**Negative Prompt**
```text
(3d render, cgi:1.3), $negative, (deformed hands:1.2), blurry
```

**Key Takeaways:**
1. Wildcards evaluate recursively from the outer level down to the inner level.
2. Inline negative extraction (`-cape`) works seamless inside nested wildcards.
3. You can scale up prompt complexity progressively before introducing Groups (`[GRP:]`) in Example 02.
