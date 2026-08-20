# 02 - Intermediate Groups & Weights Example

Demonstrates prompt grouping `[GRP:NAME]`, percentage weighting, and group-level mute.

### Positive Prompt
```text
[GRP:STYLE], RAW photo, 8k resolution, photorealistic, professional photography,
[GRP:SUBJECT], portrait of a young woman with {70% blue eyes | 20% green eyes | 10% brown eyes}, {20%? glowing neon face tattoos},
[GRP:CLOTHING], wearing a {60% leather jacket | 40% denim jacket},
//[GRP:ENVIRONMENT], standing in a rainy city street at night
```

### Negative Prompt
```text
(3d render, cgi, illustration, plastic skin:1.3), $negative, (deformed hands:1.2), blur, watermark
```
