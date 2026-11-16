---
name: remotion-create
description: Scaffolding and setting up new Remotion projects, compositions, and asset directories.
---

# Remotion Project Creation & Scaffolding

## Standard ReelStudio Project Layout
```
video-editor/
├── public/
│   ├── footage/       # Local MP4/MOV raw footage
│   ├── music/         # Background music tracks
│   ├── sound-effects/ # SFX (whooshes, risers, hits)
│   ├── images/        # Overlays, logos, graphics
│   └── fonts/         # Custom typography (Latin, Devanagari, Kannada)
├── src/
│   ├── Root.tsx       # Composition registry
│   ├── index.ts       # Entry point
│   ├── compositions/  # Reel (9:16), Landscape (16:9), Square (1:1)
│   ├── components/    # Reusable UI overlays, titles, badges
│   ├── captions/      # Animated typography and SRT renderers
│   ├── transitions/   # Dissolves, zooms, whip pans, slides
│   └── effects/       # Color grading, motion blur, letterbox
└── package.json
```

## Adding Compositions
To add a new composition:
1. Create a component in `src/compositions/MyComposition.tsx`.
2. Register it in `src/Root.tsx`:
   ```tsx
   <Composition
     id="MyReel"
     component={MyComposition}
     durationInFrames={30 * 15} // 15 seconds at 30 fps
     fps={30}
     width={1080}
     height={1920}
     defaultProps={{ ... }}
   />
   ```
