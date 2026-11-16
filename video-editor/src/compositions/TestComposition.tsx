import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export interface TestCompositionProps {
  testName?: string;
}

export const TestComposition: React.FC<TestCompositionProps> = ({
  testName = 'ReelStudio Test Render',
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();

  // Entrance spring
  const titleScale = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.6, stiffness: 120 },
  });

  const subtitleOpacity = interpolate(frame, [15, 35], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Animated background gradient movement
  const gradientAngle = interpolate(frame, [0, durationInFrames], [45, 135]);
  const circlePulse = spring({
    frame: frame % 30,
    fps,
    config: { damping: 10, mass: 0.4 },
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(${gradientAngle}deg, #090A0F 0%, #151828 50%, #0D1B2A 100%)`,
        color: '#FFFFFF',
        fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 60,
      }}
    >
      {/* Decorative Glow */}
      <div
        style={{
          position: 'absolute',
          width: 500,
          height: 500,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, transparent 70%)',
          transform: `scale(${1 + circlePulse * 0.15})`,
        }}
      />

      {/* ReelStudio Logo Badge */}
      <div
        style={{
          padding: '12px 28px',
          borderRadius: 30,
          background: 'linear-gradient(90deg, #6366F1, #EC4899)',
          fontWeight: 700,
          fontSize: 28,
          letterSpacing: 2,
          textTransform: 'uppercase',
          marginBottom: 30,
          boxShadow: '0 8px 30px rgba(99, 102, 241, 0.4)',
        }}
      >
        REELSTUDIO VERIFIED
      </div>

      {/* Main Title */}
      <h1
        style={{
          fontSize: 72,
          fontWeight: 900,
          textAlign: 'center',
          lineHeight: 1.15,
          margin: 0,
          transform: `scale(${titleScale})`,
          textShadow: '0 10px 40px rgba(0,0,0,0.8)',
          background: 'linear-gradient(180deg, #FFFFFF 0%, #CBD5E1 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}
      >
        {testName}
      </h1>

      {/* Subtitle & Specs */}
      <div
        style={{
          opacity: subtitleOpacity,
          marginTop: 24,
          fontSize: 32,
          color: '#94A3B8',
          textAlign: 'center',
          maxWidth: 800,
        }}
      >
        Resolution: {width}x{height} | {fps} FPS | Frame {frame}/{durationInFrames}
      </div>

      {/* Bottom Status Indicator */}
      <div
        style={{
          position: 'absolute',
          bottom: 120,
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          background: 'rgba(255, 255, 255, 0.08)',
          padding: '16px 36px',
          borderRadius: 16,
          border: '1px solid rgba(255, 255, 255, 0.15)',
        }}
      >
        <div
          style={{
            width: 14,
            height: 14,
            borderRadius: '50%',
            backgroundColor: '#10B981',
            boxShadow: '0 0 12px #10B981',
          }}
        />
        <span style={{ fontSize: 26, fontWeight: 600, color: '#E2E8F0' }}>
          Remotion Engine Active
        </span>
      </div>
    </AbsoluteFill>
  );
};
