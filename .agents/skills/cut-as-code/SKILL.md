---
name: cut-as-code
description: Inspectable cut-list generation, programmatic EDL/JSON video mapping, automated silence removal, and deterministic clip stitching.
---

# Cut-as-Code — Deterministic Programmatic Video Editing

## Overview
Cut-as-Code treats video editing as executable data structures. Every trim, cut, transition, and audio adjustment is stored as a version-controlled, inspectable JSON timeline.

## Data Schema & Cut List Architecture
```json
{
  "project": "Instagram_Reel_Master",
  "fps": 30,
  "resolution": [1080, 1920],
  "audio_track": "public/music/cyberpunk_beat.mp3",
  "cuts": [
    {
      "source": "public/footage/clip_01.mp4",
      "source_in_sec": 1.4,
      "source_out_sec": 4.6,
      "timeline_start_frame": 0,
      "duration_frames": 96,
      "reframe": { "focus_x": 0.52, "focus_y": 0.40, "zoom": 1.15 },
      "transition_in": "zoomIn",
      "audio_volume": 0.0
    },
    {
      "source": "public/footage/clip_02.mp4",
      "source_in_sec": 0.0,
      "source_out_sec": 3.0,
      "timeline_start_frame": 96,
      "duration_frames": 90,
      "reframe": { "focus_x": 0.48, "focus_y": 0.50, "zoom": 1.0 },
      "transition_in": "crossfade",
      "audio_volume": 1.0
    }
  ]
}
```

## Deterministic Execution Rules
1. **Never mutate source footage**: All trims and crops are computed via non-destructive timestamps.
2. **Audio Beat Snapping**: Every cut timestamp snaps to the nearest detected musical beat within a ±3 frame tolerance window.
3. **Silence Pruning**: Dead air longer than 400ms is automatically trimmed from spoken narration using `auto-editor` or FFmpeg `silencedetect`.
