# 06 - Nested Wildcards In-Depth Examples

Comprehensive examples showcasing deep wildcard nesting, combined probabilities, skip-chances, and negative tag routing.

---

### Example A: Character Outfit & Armor Generator (2-Level Nesting)
Generates complex character variations with sub-options for armor and weapons.

```text
a {60% female warrior with {70% full plate knight armor | 30% cybernetic power suit} | 40% cyberpunk rogue wearing {50% a leather coat | 50% a hooded cloak}}
```

**Possible Resolved Outcomes:**
- `a female warrior with full plate knight armor` (42% overall chance: 60% * 70%)
- `a female warrior with cybernetic power suit` (18% overall chance: 60% * 30%)
- `a cyberpunk rogue wearing a leather coat` (20% overall chance: 40% * 50%)
- `a cyberpunk rogue wearing a hooded cloak` (20% overall chance: 40% * 50%)

---

### Example B: Multi-Layer Environment & Weather (3-Level Nesting)
Combines season, weather condition, time of day, and inline negative tags.

```text
a portrait of a traveler, {60% in a summer setting with {70% sunny clear sky, -sunglasses | 30% sudden thunder storm, -umbrella} | 40% in a winter setting with {80% heavy snow fall, -heavy_coat | 20% icy frozen lake, -skates}}, {50% at golden hour dusk | 50% at midnight with {70% full moon light | 30% aurora borealis}}
```

**Positive Output Examples:**
- `a portrait of a traveler, in a summer setting with sunny clear sky, at golden hour dusk`
- `a portrait of a traveler, in a winter setting with heavy snow fall, at midnight with aurora borealis`

**Negative Output Examples:**
- `sunglasses` (if summer sunny sky is chosen)
- `heavy_coat` (if winter heavy snow fall is chosen)

---

### Example C: Deep Nested Creature & Accessory Generator (3-Level Nesting with Skip Chance)
Shows how optional tags (`X%?`) interact inside nested wildcards.

```text
a fantasy artwork of a {70% dragon with {80% crimson scales | 20% golden scales, {30%? glowing crown}} | 30% griffin with {50% eagle wings | 50% raven wings}}, {20%? resting on a mountain peak}
```
