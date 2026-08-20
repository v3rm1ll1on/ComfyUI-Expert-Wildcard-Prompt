# 02 - Intermediate Groups & Weights

Demonstrates prompt organization using groups `[GRP:NAME]`, percentage weighting (`X% option`), skip chances (`X%? option`), and group muting (`//[GRP:]`).

---

### Example 1: Character Portrait with Relative Weights & Skip Chance

**Positive Prompt**
```text
[GRP:STYLE], RAW photo, 8k resolution, photorealistic, professional photography,
[GRP:SUBJECT], portrait of a young woman with {70% blue eyes | 20% green eyes | 10% brown eyes}, {20%? glowing neon face tattoos},
[GRP:CLOTHING], wearing a {60% leather jacket | 40% denim jacket},
//[GRP:ENVIRONMENT], standing in a rainy city street at night
```

**Negative Prompt**
```text
(3d render, cgi, illustration, plastic skin:1.3), $negative, (deformed hands:1.2), blur, watermark
```

---

### Example 2: Fantasy Castle Architecture with Skip Features

**Positive Prompt**
```text
[GRP:STYLE], epic fantasy concept art, digital painting, trending on artstation,
[GRP:BUILDING], massive stone castle on a cliff, {80% gothic towers | 20% crystal spires}, {30%? glowing magic runes on walls},
[GRP:WEATHER], {50% thunderstorm with lightning | 30% sunny golden hour | 20% dense fog},
[GRP:EXTRAS], {40%? flying dragons in distance | 10%? floating magical islands}
```

**Negative Prompt**
```text
photo, realistic, low contrast, $negative
```

---

### Example 3: Cyberpunk Street Alleyway

**Positive Prompt**
```text
[GRP:ENVIRONMENT], narrow cyberpunk alleyway, {80% wet reflective pavement | 20% steam rising from grates},
[GRP:LIGHTING], {60% neon blue and pink lighting | 40% warm amber lantern glow},
[GRP:DETAILS], holograms, wires overhead, {50%? neon signboards in japanese text},
//[GRP:PASSERSBY], crowded street with pedestrians walking
```

**Negative Prompt**
```text
daylight, sun, trees, nature, $negative
```
