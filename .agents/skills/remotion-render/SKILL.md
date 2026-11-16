---
name: remotion-render
description: Best practices, commands, hardware flags, and output formats for rendering Remotion compositions to MP4 videos.
---

# Remotion Video Rendering Guide

## CLI Commands
```bash
# Render Instagram Reel (1080x1920)
npx remotion render src/index.ts ReelComposition ../Exports/MyReel.mp4

# Render with specific concurrency (optimized for 16GB RAM)
npx remotion render src/index.ts ReelComposition ../Exports/MyReel.mp4 --concurrency=4

# Render test composition
npx remotion render src/index.ts TestComposition ../Exports/Test/test.mp4

# Still frame thumbnail render
npx remotion still src/index.ts ReelComposition ../Exports/thumbnail.png --frame=30
```

## Encoding Configuration
- Default video codec: H.264 (`--codec=h264`)
- Audio codec: AAC
- Pixel format: YUV420P (`--pixel-format=yuv420p` for maximum Instagram & mobile compatibility)
- Quality / CRF: 18 - 22 for crisp high-bitrate output.
