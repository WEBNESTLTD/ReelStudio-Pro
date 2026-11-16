---
name: claude-motion-design
description: Code-driven programmatic motion design, typography animations, physics-based easing curves, kinetic text, and layout architecture.
---

# Claude Motion Design — Code-Driven Animation & Layout

## Overview
Replaces rigid video templates with generative, code-driven motion design. Computes exact frame-by-frame transforms, springs, blur approximations, and kinetic layouts programmatically.

## Animation Framework in ReelStudio

### 1. Physics-Based Springs vs Linear Interpolation
```tsx
import { spring, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';

// Snappy pop-in spring for stickers, badges, and focal elements
const popScale = spring({
  frame,
  fps,
  config: {
    damping: 10,
    mass: 0.4,
    stiffness: 150,
  },
});

// Smooth, cinematic ease-out for camera push-ins and background drift
const cameraZoom = interpolate(frame, [0, durationInFrames], [1.0, 1.08], {
  easing: (t) => 1 - Math.pow(1 - t, 3), // cubic ease-out
  extrapolateRight: 'clamp',
});
```

### 2. Kinetic Typography Rules
- **Headline Punch**: Animate line by line or word by word with staggered frame offsets (`delay = index * 4`).
- **Letter Spacing Transition**: Expand tracking during entrance (`letterSpacing: interpolate(frame, [0, 20], [8, 2])`).
- **Backdrop Legibility**: Always pair animated text with high-blur backdrops (`backdropFilter: 'blur(16px)'`) or subtle black box pills (`rgba(0,0,0,0.65)`).

### 3. Motion Blur & Layer Depth
Simulate camera motion blur by interpolating a subtle multi-directional box-shadow or CSS blur filter during peak velocity frames (e.g. frame 2 to 8 of an entrance).
