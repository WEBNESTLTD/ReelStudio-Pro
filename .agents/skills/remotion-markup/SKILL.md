---
name: remotion-markup
description: Guidelines and best practices for writing Remotion React markup, animation hooks, layout styling, and media.
---

# Remotion React Markup & Animation Guidelines

## 1. Frame-Driven Animations
Always compute values using `useCurrentFrame()`:
```tsx
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';

export const AnimatedTitle = ({ text }: { text: string }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Smooth entrance spring
  const scale = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.5, stiffness: 100 },
  });

  // Fade in
  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <h1 style={{ transform: `scale(${scale})`, opacity, textAlign: 'center' }}>
      {text}
    </h1>
  );
};
```

## 2. Dynamic Camera Zoom (Ken Burns / Punch-in)
```tsx
const frame = useCurrentFrame();
const zoom = interpolate(frame, [0, 150], [1.0, 1.15], {
  extrapolateRight: 'clamp',
});

<div style={{ transform: `scale(${zoom})`, overflow: 'hidden' }}>
  <Video src={staticFile('footage/main.mp4')} />
</div>
```

## 3. Audio & Ducking
```tsx
import { Audio, staticFile, interpolate, useCurrentFrame } from 'remotion';

// Ducking background music from frame 60 to 180 during dialogue
const frame = useCurrentFrame();
const musicVolume = interpolate(
  frame,
  [50, 60, 180, 190],
  [0.8, 0.2, 0.2, 0.8],
  { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
);

<Audio src={staticFile('music/bg.mp3')} volume={musicVolume} />
```
