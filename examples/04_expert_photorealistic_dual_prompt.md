# 04 - Expert Photorealistic Dual-Prompt Template

Demonstrates all advanced features:
- Dual-output routing with inline negative extraction (`-`)
- Precise placement via `$negative` placeholder
- Group-level organization (`[GRP:]`) and tag-level solo (`!`)
- Inline tag muting (`//`) and nested probabilistic wildcards

### Positive Prompt
```text
[GRP:STYLE], RAW photorealistic shot, 35mm lens, f/1.8 aperture, natural lighting, subsurface scattering,
[GRP:SUBJECT], cinematic portrait of a {60% female hacker with {70% cybernetic eye implants, -glasses | 30% holographic visor, -sunglasses} | 40% street runner},
[GRP:ENVIRONMENT], {70% standing in a neon-lit cyberpunk alley, -sunlight | 30% inside a high-tech server room, -nature},
[GRP:EXPERIMENTAL_OVERLAY], glitch art effect, // chromatic aberration
```

### Negative Prompt
```text
(3d render, cgi, illustration, anime, cartoon, 3d model, plastic skin, airwashed:1.3), (oversaturated:1.2), $negative, (deformed eyes, asymmetrical eyes:1.2), (cloned face:1.2), (blur, soft focus:1.15), watermark, text, signature
```
