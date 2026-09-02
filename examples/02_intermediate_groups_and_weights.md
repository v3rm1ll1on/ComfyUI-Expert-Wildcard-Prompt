# 02 - Intermediate Weights, Ranges, Skip-Chances & Groups

Learn intermediate prompt features progressively: custom percentage weighting, numeric ranges, skip chances (`%?`), and how to organize complex prompts into Groups (`[GRP:]`).

---

### Step 1: Weighted Probabilities & Skip-Chances (Without Groups)

Customize selection odds and add optional elements without using groups:

**Positive Prompt**
```text
RAW photo of a young woman with {70% blue eyes | 20% green eyes | brown eyes}, wearing a {60% leather jacket | denim jacket}, {25%? glowing neon face tattoos}, photorealistic
```

> [!NOTE]
> **Smart Weight Balancing (Auto-Rest Distribution)**
> You don't have to specify percentages for every single option!
> - In `{70% blue eyes | 20% green eyes | brown eyes}`, explicit weights sum to **90%**. The unweighted option `brown eyes` automatically receives the remaining **10%**.
> - In `{60% leather jacket | denim jacket}`, `denim jacket` automatically receives the remaining **40%**.

**Negative Prompt**
```text
(3d render, cgi, illustration, plastic skin:1.3), (deformed hands:1.2), blur
```

---

### Step 2: Numeric Ranges & Step Increments (Without Groups)

Dynamic numeric value generation across custom ranges:

**Positive Prompt**
```text
RAW photo, portrait of a {18-50} yo woman born in {1970-2010:5}, camera height {1-3} meters, ISO {100-800:100}
```

**Negative Prompt**
```text
(3d render, cgi, illustration:1.3), blur, watermark
```

---

### Step 3: Introducing Prompt Groups (`[GRP:NAME]`)

Once prompts grow larger, wrap sections in `[GRP:NAME]` blocks to maintain structure and enable group-level muting (`//[GRP:]`) or soloing (`![GRP:]`):

**Positive Prompt**
```text
[GRP:STYLE], RAW photo, 8k resolution, photorealistic, professional photography,
[GRP:SUBJECT], portrait of a {18-40}yo woman with {70% blue eyes | 30% hazel eyes}, {20%? neon face tattoos},
[GRP:CLOTHING], wearing a {60% leather jacket | 40% denim jacket},
//[GRP:ENVIRONMENT], standing in a rainy city street at night
```

**Negative Prompt**
```text
(3d render, cgi, illustration, plastic skin:1.3), (deformed hands:1.2), blur, watermark
```

---

### Step 4: Fantasy Concept Art (Combining Weights, Skips & Groups)

**Positive Prompt**
```text
[GRP:STYLE], epic fantasy concept art, digital painting, trending on artstation,
[GRP:BUILDING], massive stone castle on a cliff, {80% gothic towers | 20% crystal spires}, {30%? glowing magic runes on walls},
[GRP:WEATHER], {50% thunderstorm with lightning | 30% sunny golden hour | 20% dense fog},
[GRP:EXTRAS], {40%? flying dragons in distance | 10%? floating magical islands}
```

**Negative Prompt**
```text
photo, realistic, low contrast
```
