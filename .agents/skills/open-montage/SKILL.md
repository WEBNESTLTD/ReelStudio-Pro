---
name: open-montage
description: Agentic video production orchestrator for research, scripting, narrative pacing, asset staging, and programmatic video assembly.
---

# OpenMontage — Agentic Video Production Skill

## Overview
OpenMontage transforms the agent into an end-to-end video producer capable of turning rough ideas, existing footage, or written scripts into fully assembled, beat-synced programmatic video compositions.

## Video Production Pipeline

### 1. Scripting & Narrative Architecture
- **Hook (0:00 - 0:03)**: Fast motion, punchy statement, dynamic zoom, high-contrast title.
- **Problem / Context (0:03 - 0:10)**: Establish narrative friction, introduce problem or setting.
- **Core Value / Action (0:10 - 0:40)**: Beat-synced cuts, B-roll overlays, animated captions.
- **Call-to-Action (0:40 - 0:60)**: Visual logo sting, final CTA, clean outro.

### 2. Shot-Listing & Asset Mapping
Map available raw footage clips to narrative beats:
```json
[
  {
    "beat": "Intro Hook",
    "clip": "public/footage/aerial_intro.mp4",
    "start_frame": 0,
    "duration_frames": 90,
    "caption": "EXPLORE THE UNSEEN",
    "transition": "zoomIn"
  },
  {
    "beat": "Feature Showcase",
    "clip": "public/footage/detail_shot.mp4",
    "start_frame": 90,
    "duration_frames": 150,
    "caption": "PRECISION ENGINEERED",
    "transition": "crossfade"
  }
]
```

### 3. Programmatic Assembly
Generate modular Remotion `<Sequence>` or `<Series>` components matching the shot list, ensuring audio levels duck during voiceovers and snap to music beats.
