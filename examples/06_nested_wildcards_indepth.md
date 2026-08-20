# 06 - Nested Wildcards In-Depth Examples

Comprehensive examples showcasing deep wildcard nesting, combined probabilities, skip-chances (`X%?`), and inline negative tag routing (`-`)—both in plain text prompts and structured groups.

---

### Step 1: Pure Nested Wildcards (Without Groups)

Demonstrates 2-level and 3-level nesting in a clean, continuous prompt line without any group tags:

#### Positive Prompt
```text
RAW photorealistic portrait of a {60% female warrior with {70% full plate knight armor, -dress | 30% cybernetic power suit, -glasses} | 40% cyberpunk rogue wearing {50% a leather coat, -hood | 50% a hooded cloak, -hat}}, {60% standing in ancient ruins | 40% inside a neon alleyway}
```

#### Negative Prompt Template
```text
(3d render, cgi, illustration:1.3), $negative, (deformed hands:1.2), blur
```

---

### Step 2: Character Archetype & Armor Generator (2-Level Nesting with Groups)
Organize deep wildcard structures into dedicated group headers:

#### Positive Prompt
```text
[GRP:STYLE], RAW photorealistic portrait, 35mm lens,
[GRP:SUBJECT], a {60% female warrior with {70% full plate knight armor, -dress | 30% cybernetic power suit, -glasses} | 40% cyberpunk rogue wearing {50% a leather coat, -hood | 50% a hooded cloak, -hat}},
[GRP:ENVIRONMENT], standing in ancient ruins
```

#### Negative Prompt Template
```text
(3d render, cgi, illustration:1.3), $negative, (deformed hands:1.2), blur
```

#### Expected Output Scenarios
* **Scenario 1 (Warrior - Knight Armor):**
  * **Positive:** `RAW photorealistic portrait, 35mm lens, a female warrior with full plate knight armor, standing in ancient ruins`
  * **Negative:** `(3d render, cgi, illustration:1.3), dress, (deformed hands:1.2), blur`
* **Scenario 2 (Rogue - Hooded Cloak):**
  * **Positive:** `RAW photorealistic portrait, 35mm lens, a cyberpunk rogue wearing a hooded cloak, standing in ancient ruins`
  * **Negative:** `(3d render, cgi, illustration:1.3), hat, (deformed hands:1.2), blur`

---

### Step 3: Multi-Layer Environment & Weather (3-Level Nesting)
Combines season, weather condition, time of day, and inline negative tags across 3 deep wildcard levels.

#### Positive Prompt
```text
[GRP:STYLE], cinematic landscape photography, 8k resolution,
[GRP:SUBJECT], portrait of a traveler,
[GRP:ENVIRONMENT], {60% in a summer setting with {70% sunny clear sky, -sunglasses | 30% sudden thunderstorm, -umbrella} | 40% in a winter setting with {80% heavy snowfall, -heavy_coat | 20% icy frozen lake, -ice_skates}}, {50% at golden hour dusk | 50% at midnight with {70% full moonlight | 30% aurora borealis}}
```

#### Negative Prompt Template
```text
(bad quality:1.4), $negative, (oversaturated:1.2), watermark, text
```

#### Expected Output Scenarios
* **Scenario 1 (Summer - Sunny Sky - Dusk):**
  * **Positive:** `cinematic landscape photography, 8k resolution, portrait of a traveler, in a summer setting with sunny clear sky, at golden hour dusk`
  * **Negative:** `(bad quality:1.4), sunglasses, (oversaturated:1.2), watermark, text`
* **Scenario 2 (Winter - Heavy Snowfall - Aurora):**
  * **Positive:** `cinematic landscape photography, 8k resolution, portrait of a traveler, in a winter setting with heavy snowfall, at midnight with aurora borealis`
  * **Negative:** `(bad quality:1.4), heavy_coat, (oversaturated:1.2), watermark, text`

---

### Step 4: Deep Nested Creature & Accessory Generator (3-Level Nesting with Skip Chance)
Demonstrates how optional skip-chance tags (`X%?`) interact inside deep nested wildcard choices.

#### Positive Prompt
```text
[GRP:STYLE], digital fantasy artwork, concept art,
[GRP:SUBJECT], a fantasy {70% dragon with {80% crimson scales, -wings | 20% golden scales, {30%? glowing crown, -horns}} | 30% griffin with {50% eagle wings, -beak | 50% raven wings, -feathers}},
[GRP:ENVIRONMENT], {20%? resting on a mountain peak, -cloudy}
```

#### Negative Prompt Template
```text
(worst quality, low quality:1.4), $negative, (deformed:1.2), signature
```

#### Expected Output Scenarios
* **Scenario 1 (Golden Scales Dragon + Crown Rolled + Mountain Peak Skipped):**
  * **Positive:** `digital fantasy artwork, concept art, a fantasy dragon with golden scales, glowing crown`
  * **Negative:** `(worst quality, low quality:1.4), horns, (deformed:1.2), signature`
* **Scenario 2 (Griffin Eagle Wings + Mountain Peak Rolled):**
  * **Positive:** `digital fantasy artwork, concept art, a fantasy griffin with eagle wings, resting on a mountain peak`
  * **Negative:** `(worst quality, low quality:1.4), beak, cloudy, (deformed:1.2), signature`
