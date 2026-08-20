# 03 - Advanced Pony V6 Templates

Optimized templates for Pony Diffusion V6 (and variants like Pony Realism). Utilizes score groups, complex character chains, pose variations, and negative score templates with `$negative`.

---

### Example 1: Standard Anime Warrior Girl

**Positive Prompt**
```text
[GRP:PONY_SCORES], score_9, score_8_up, score_7_up, rating_safe,
[GRP:CHARACTER], 1girl, solo, {70% anime warrior girl with {70% knight armor | 30% cyber suit} | 30% cyberpunk rogue}, {5% rare silver hair | blonde hair | black hair},
[GRP:ACTION], {70% standing calmly, holding a sword | 30% in an aggressive action pose},
[GRP:BG], {70% sunny day in a forest, -sunglasses | 30% rainy city alley, -umbrella}
```

**Negative Prompt**
```text
score_4_up, score_5_up, score_6_up, (3d render, cgi:1.3), $negative, (deformed eyes:1.2), bad anatomy, extra limbs
```

---

### Example 2: Kemonomimi / Neko Character Generator

**Positive Prompt**
```text
[GRP:PONY_SCORES], score_9, score_8_up, score_7_up, rating_safe,
[GRP:CHARACTER], 1girl, solo, cat girl, {cat ears, cat tail}, {long pink hair | short blue hair | twin tails blonde hair}, {50% cute maid outfit | 50% casual hoodie and pleated skirt},
[GRP:EXPRESSION], {60% smiling happily, blushing | 30% playful pout, looking at viewer | 10% wink},
[GRP:LOCATION], {cozy bedroom, soft lighting | colorful candy shop background | sakura trees park}
```

**Negative Prompt**
```text
score_4_up, score_5_up, score_6_up, $negative, 3d, realistic, photo, ugly, bad hands
```

---

### Example 3: Dynamic Action Battle Scene

**Positive Prompt**
```text
[GRP:PONY_SCORES], score_9, score_8_up, score_7_up, rating_safe,
[GRP:SUBJECT], 1boy, solo, male paladin, glowing holy magic, {glowing golden aura | blue lightning energy surrounding body},
[GRP:POSE], {jumping attack pose, sword raised high | defensive stance, shield up},
[GRP:ENVIRONMENT], crumbling ruined temple, fire particles in air, dramatic dynamic angle, cinematic shadows
```

**Negative Prompt**
```text
score_4_up, score_5_up, score_6_up, $negative, female, 1girl, peaceful, calm
```
