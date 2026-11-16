import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

export interface CaptionWord {
  start: number; // in seconds
  end: number;
  word: string;
}

export interface CaptionRendererProps {
  words: CaptionWord[];
  activeColor?: string;
  inactiveColor?: string;
  fontSize?: number;
}

export const CaptionRenderer: React.FC<CaptionRendererProps> = ({
  words,
  activeColor = '#FBBF24', // Warm cinema gold
  inactiveColor = '#FFFFFF',
  fontSize = 58,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  // Filter words within reasonable view window (e.g., current ± 1.5 seconds)
  const visibleWords = words.filter(
    (w) => currentTime >= w.start - 0.5 && currentTime <= w.end + 1.2
  );

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 260, // Above Instagram Reels description & action buttons
        left: 0,
        right: 0,
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        padding: '0 60px',
        textAlign: 'center',
        fontFamily: "'Segoe UI', 'Noto Sans Devanagari', 'Noto Sans Kannada', sans-serif",
        fontWeight: 900,
        fontSize,
        lineHeight: 1.3,
        textShadow: '0 4px 16px rgba(0,0,0,0.9), 0 2px 4px rgba(0,0,0,0.8)',
        pointerEvents: 'none',
      }}
    >
      {visibleWords.map((item, idx) => {
        const isActive = currentTime >= item.start && currentTime <= item.end;
        const wordStartFrame = Math.round(item.start * fps);
        const relativeFrame = Math.max(0, frame - wordStartFrame);

        const wordPop = isActive
          ? spring({
              frame: relativeFrame,
              fps,
              config: { damping: 9, mass: 0.3, stiffness: 180 },
            })
          : 1;

        return (
          <span
            key={`${item.word}-${idx}`}
            style={{
              display: 'inline-block',
              margin: '0 8px',
              color: isActive ? activeColor : inactiveColor,
              transform: `scale(${isActive ? 1 + wordPop * 0.18 : 1})`,
              transformOrigin: 'center bottom',
              transition: 'color 0.08s ease',
            }}
          >
            {item.word}
          </span>
        );
      })}
    </div>
  );
};
