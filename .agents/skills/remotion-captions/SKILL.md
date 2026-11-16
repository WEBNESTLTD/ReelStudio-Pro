---
name: remotion-captions
description: Best practices for generating, styling, and rendering animated AI captions, word highlights, and multilingual subtitles in Remotion.
---

# Remotion Captions & Subtitles Guide

## Architecture
1. **Transcription**: Use OpenAI Whisper (`video-editor/scripts/whisper_transcriber.py`) to generate word-level timestamped JSON:
   ```json
   [
     { "start": 0.5, "end": 0.8, "word": "Cinematic" },
     { "start": 0.82, "end": 1.2, "word": "Reels" }
   ]
   ```
2. **Synchronized Rendering**:
   Convert seconds to frames using `Math.round(second * fps)` and render active words highlighted with color/scale springs:

```tsx
import { useCurrentFrame, useVideoConfig, spring } from 'remotion';

export interface CaptionWord {
  start: number; // in seconds
  end: number;
  word: string;
}

export const CaptionRenderer: React.FC<{ words: CaptionWord[] }> = ({ words }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  return (
    <div style={{
      position: 'absolute',
      bottom: 220,
      width: '100%',
      textAlign: 'center',
      padding: '0 40px',
      fontFamily: 'system-ui, sans-serif',
      fontWeight: 800,
      fontSize: 54,
      textTransform: 'uppercase',
      textShadow: '0 4px 12px rgba(0,0,0,0.8)',
    }}>
      {words.map((item, idx) => {
        const isActive = currentTime >= item.start && currentTime <= item.end;
        const activeFrame = Math.max(0, frame - Math.round(item.start * fps));
        const scale = isActive
          ? spring({ frame: activeFrame, fps, config: { damping: 10, mass: 0.3 } })
          : 1;

        return (
          <span
            key={idx}
            style={{
              display: 'inline-block',
              margin: '0 10px',
              color: isActive ? '#FFE600' : '#FFFFFF',
              transform: `scale(${scale})`,
              transition: 'color 0.1s ease',
            }}
          >
            {item.word}
          </span>
        );
      })}
    </div>
  );
};
```

## Multilingual Support
For Hindi (Devanagari) and Kannada scripts:
- Use Unicode UTF-8 fonts with full glyph support (e.g. Noto Sans Devanagari, Noto Sans Kannada).
- Keep word segmentation clean and avoid breaking conjunct characters.
