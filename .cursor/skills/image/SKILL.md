---
name: image
description: Generate image assets from user prompts using the image generation tool. Use when the user asks to create, make, generate, or design an image, icon, illustration, mockup, concept art, or visual asset.
---

# Image

## Purpose

Create high-quality image outputs from user intent.

## When to use

Use this skill when the user asks for image generation, including prompts like:
- "make an image"
- "generate an icon"
- "create a mockup"
- "design concept art"
- "make this look like a poster"

## Workflow

1. Confirm the desired output details from the request:
   - subject
   - style
   - composition/layout
   - color palette
   - text to include (if any)
   - constraints (aspect ratio, transparent background, etc.)
2. If critical details are missing, ask a concise follow-up question.
3. Build a specific prompt that includes:
   - main subject and scene
   - art style and quality cues
   - composition and camera framing
   - lighting and color direction
   - explicit constraints and exclusions
4. Call the image generation tool with the composed description.
5. Return a short summary of what was generated and offer one revision pass.

## Prompt template

Use this template and fill in concrete values:

```text
[Output type], [subject], [setting/background], [composition], [style], [lighting], [colors], [mood], [text requirements], [constraints].
```

## Guardrails

- Only generate images when the user explicitly requests an image.
- Do not use image generation for charts, tables, or data-heavy visualizations.
- Keep prompts concrete and avoid vague adjectives without context.
- If user requests edits, preserve unchanged parts and modify only requested aspects.

