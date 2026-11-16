import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig } from 'remotion';

export interface ThreeDCardProps {
  children: React.ReactNode;
  tiltAngle?: number;
}

export const ThreeDPerspectiveCard: React.FC<ThreeDCardProps> = ({
  children,
  tiltAngle = 15,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Subtle continuous 3D floating wobble
  const rotateX = interpolate(
    frame,
    [0, durationInFrames / 2, durationInFrames],
    [-tiltAngle * 0.4, tiltAngle * 0.4, -tiltAngle * 0.4]
  );
  
  const rotateY = interpolate(
    frame,
    [0, durationInFrames / 2, durationInFrames],
    [tiltAngle * 0.6, -tiltAngle * 0.6, tiltAngle * 0.6]
  );

  return (
    <div
      style={{
        perspective: 1200,
        transformStyle: 'preserve-3d',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(30px)`,
          transition: 'transform 0.1s ease-out',
        }}
      >
        {children}
      </div>
    </div>
  );
};
