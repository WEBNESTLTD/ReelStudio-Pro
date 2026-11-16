import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

export interface TransitionProps {
  children: React.ReactNode;
  durationInFrames: number;
  type?: 'crossfade' | 'zoomIn' | 'slideLeft';
}

export const CinematicTransition: React.FC<TransitionProps> = ({
  children,
  durationInFrames,
  type = 'crossfade',
}) => {
  const frame = useCurrentFrame();

  let opacity = 1;
  let transform = 'none';

  if (type === 'crossfade') {
    opacity = interpolate(frame, [0, durationInFrames], [0, 1], {
      extrapolateRight: 'clamp',
    });
  } else if (type === 'zoomIn') {
    const scale = interpolate(frame, [0, durationInFrames], [1.25, 1.0], {
      extrapolateRight: 'clamp',
    });
    opacity = interpolate(frame, [0, durationInFrames * 0.5], [0, 1], {
      extrapolateRight: 'clamp',
    });
    transform = `scale(${scale})`;
  } else if (type === 'slideLeft') {
    const translateX = interpolate(frame, [0, durationInFrames], [100, 0], {
      extrapolateRight: 'clamp',
    });
    transform = `translateX(${translateX}%)`;
  }

  return (
    <div style={{ width: '100%', height: '100%', opacity, transform }}>
      {children}
    </div>
  );
};
