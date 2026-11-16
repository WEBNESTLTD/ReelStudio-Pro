import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

export const LowerThird: React.FC<{
  name: string;
  role: string;
  startFrame?: number;
}> = ({ name, role, startFrame = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const relativeFrame = Math.max(0, frame - startFrame);

  const slideX = spring({
    frame: relativeFrame,
    fps,
    config: { damping: 14, mass: 0.5, stiffness: 120 },
  });

  const opacity = interpolate(relativeFrame, [0, 10], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 240,
        left: 60,
        opacity,
        transform: `translateX(${(1 - slideX) * -80}px)`,
        display: 'flex',
        flexDirection: 'column',
        gap: 6,
        padding: '16px 28px',
        borderRadius: 16,
        background: 'rgba(15, 23, 42, 0.85)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        boxShadow: '0 12px 32px rgba(0,0,0,0.5)',
      }}
    >
      <span
        style={{
          color: '#FFFFFF',
          fontSize: 32,
          fontWeight: 800,
          letterSpacing: 1.5,
          textTransform: 'uppercase',
        }}
      >
        {name}
      </span>
      <span
        style={{
          color: '#38BDF8',
          fontSize: 22,
          fontWeight: 600,
          letterSpacing: 2,
        }}
      >
        {role}
      </span>
    </div>
  );
};

export const StoryProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = (frame / durationInFrames) * 100;

  return (
    <div
      style={{
        position: 'absolute',
        top: 40,
        left: 40,
        right: 40,
        height: 6,
        borderRadius: 3,
        background: 'rgba(255, 255, 255, 0.25)',
        overflow: 'hidden',
        zIndex: 100,
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: '100%',
          background: 'linear-gradient(90deg, #6366F1, #EC4899)',
          borderRadius: 3,
          boxShadow: '0 0 10px rgba(236, 72, 153, 0.8)',
        }}
      />
    </div>
  );
};
