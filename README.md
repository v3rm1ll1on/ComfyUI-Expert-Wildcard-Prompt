# Expert Text Prompt (ComfyUI Custom Node)

Ein leistungsstarker ComfyUI Text-Prompt Node mit AST-Parsing, erweiterten Wildcards, prozentualen Gewichtungen, Skip-Chancen, Gruppen und Mute/Solo-Steuerung.

---

## 🚀 Features

- 🎲 **Erweiterte Wildcards**: `{option1 | option2 | option3}`
- 📊 **Prozentuale Wahrscheinlichkeiten**: `{70% blue eyes | 30% green eyes}`
- ❓ **Skip-Chance (Optionale Tags)**: `{20%? optional sunglasses}` (wird zu 20% verworfen)
- 📁 **Gruppierung**: `[GRP:NAME]` zur Strukturierung von Prompts
- 🔇 **Mute-Funktion (`//`)**: Stummschalten von einzelnen Tags oder ganzen Gruppen
- 🎯 **Solo-Funktion (`!`)**: Isolieren von spezifischen Tags/Gruppen (blendete alles andere aus)
- ⚖️ **SDXL Gewichte & LoRAs**: Volle Unterstützung für `(tag:1.2)` und `<lora:name:1.0>`
- 🔢 **Deterministic Seed**: Gleicher Seed = Exakt selbe Wildcard-Auswahl

---

## 📦 Installation

 Navigiere in deinen ComfyUI `custom_nodes` Ordner und klone dieses Repository:

```bash
cd ComfyUI/custom_nodes
git clone git@github.com:v3rm1ll1on/comfyi_variable_prompt.git
```

Starte ComfyUI danach neu.

---

## 🔍 In ComfyUI finden

- **Node Name**: `Expert Text Prompt (Wildcards & AST)`
- **Kategorie**: `prompt/expert`

---

## 📖 Syntax & Beispiele

### 1. Wildcards mit Prozenten & Gewichtung
Definiere Wahrscheinlichkeiten für jede Option:
```text
a {70% cyberpunk female hacker | 30% futuristic street runner}
```

### 2. Skip-Chance (Optionale Tags)
Füge ein `X%?` am Anfang der Wildcard-Klammer ein, um festzulegen, wie wahrscheinlich das Tag **übersprungen** wird:
```text
{20%? glowing neon face tattoos}
```
*(Zu 20% wird kein Tattoo generiert, zu 80% wird das Tag eingesetzt).*

### 3. Mute & Solo Modus (`//` & `!`)

- **Mute (`//`)**: Deaktiviert ein Tag oder eine Gruppe:
  ```text
  masterpiece, // ruined background, leather jacket
  ```
- **Solo (`!`)**: Deaktiviert alle anderen Tags im Prompt und fokussiert sich nur auf das Solo-Tag:
  ```text
  red dress, blue shoes, ! golden necklace
  ```
  *(Ergebnis: `golden necklace`)*

### 4. Gruppen (`[GRP:NAME]`)
Organisiere deinen Prompt übersichtlich. Gruppen können auch gemutet oder gesoloed werden:
```text
[GRP:QUALITY], (masterpiece:1.2), ultra-detailed,

[GRP:CHARACTER], cyberpunk girl, neon hair,

//[GRP:BACKGROUND], city skyline at dusk
```

---

## 💡 Komplexer Beispiel-Prompt

```text
[GRP:QUALITY], (masterpiece:1.2), (best quality:1.2), ultra-detailed, 8k resolution, photorealistic, <lora:cyberpunk_style_v1:0.8>,

[GRP:CHARACTER], a {60% cyberpunk female hacker | 40% futuristic street runner}, (detailed face:1.15), {70% glowing cybernetic eye implants | 30% futuristic visor}, {15%? glowing neon face tattoos}, {50% neon blue hair, braided ponytail | 35% short pink undercut hair | 15% silver bob hair},

[GRP:CLOTHING], wearing {50% high-tech tactical jacket, leather straps | 50% sleek sci-fi bodysuit, illuminated seams}, // old ruined jacket, {30%? fingerless cyber gloves},

[GRP:SETTING], standing in a {80% rain-slicked cyberpunk alleyway, neon signs reflections | 20% high-tech server control room, holographic displays}, volumetric lighting, fog, dramatic rim light, cinematic night scene
```

---

## ⚙️ Parameter

- **`text`**: Dein Prompt mit der erweiterten Syntax.
- **`seed`**: Steuert den Zufallsgenerator für Wildcards. Gleicher Seed = Gleicher generierter Text.
