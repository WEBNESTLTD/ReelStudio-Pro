---
name: remotion-best-practices
description: Master best practices for Remotion video creation, React animation, timing, layout, and rendering.
---

# Remotion Best Practices Guide

## Core Architecture Principles
1. **Frame-Based Animation Over Time**:
   - Always use `useCurrentFrame()` and `useVideoConfig()` to compute layout, transforms, and opacities.
   - Never use CSS `@keyframes`, `transition`, or `setTimeout`/`setInterval` for video rendering because they don't sync with frame-by-frame rendering.
   - Use `interpolate(frame, inputRange, outputRange, options)` for smooth linear or clamped interpolation.
   - Use `spring({ frame, fps, config })` for physically-based bouncy and smooth animations.

2. **Composition Structure**:
   - Keep root registry in `src/Root.tsx` using `<Composition>` with exact `id`, `component`, `durationInFrames`, `fps`, `width`, and `height`.
   - Organize multi-scene timelines using `<Sequence>` (for absolute offsets or layered tracks) or `<Series>` (for sequential clips one after another).
   - Use `<Series.Sequence durationInFrames={...}>` for sequential editing.

3. **Media Handling**:
   - Use `<Video src={staticFile("footage/clip.mp4")} />` from `remotion` for local video footage.
   - Use `<Audio src={staticFile("music/track.mp3")} />` for background music and audio tracks.
   - Use `<Img src={...} />` instead of standard `<img>` for guaranteed frame-load synchronization.
   - Use `staticFile()` to reference files placed in `public/`.

4. **Performance & Memory Management**:
   - When editing 4K or high bitrate footage, generate 720p or 1080p editing proxies.
   - Set Remotion studio concurrency according to available RAM (16GB RAM: 2-4 threads max).
   - Keep assets local in `public/` to avoid remote fetch latency and frame timeouts.

5. **Audio Ducking & Levels**:
   - Duck background music volume during speech sequences (e.g. volume from 0.7 down to 0.15-0.2).
   - Use volume ramps with `interpolate()` to prevent audio clicks or abrupt transitions.
