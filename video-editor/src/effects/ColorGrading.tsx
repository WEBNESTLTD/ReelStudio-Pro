import React from 'react';

export type ColorPreset = 'tealOrange' | 'moodyMonochrome' | 'warmCinema' | 'vibrant' | 'none';

export interface ColorGradingProps {
  children: React.ReactNode;
  preset?: ColorPreset;
  vignette?: boolean;
}

export const ColorGrading: React.FC<ColorGradingProps> = ({
  children,
  preset = 'tealOrange',
  vignette = true,
}) => {
  let filter = 'none';

  switch (preset) {
    case 'tealOrange':
      filter = 'contrast(1.15) saturate(1.25) sepia(0.12) hue-rotate(-8deg)';
      break;
    case 'moodyMonochrome':
      filter = 'grayscale(1) contrast(1.3) brightness(0.9)';
      break;
    case 'warmCinema':
      filter = 'sepia(0.2) contrast(1.1) brightness(1.05) saturate(1.15)';
      break;
    case 'vibrant':
      filter = 'saturate(1.4) contrast(1.1) brightness(1.02)';
      break;
    default:
      filter = 'none';
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Graded Media Layer */}
      <div style={{ width: '100%', height: '100%', filter }}>{children}</div>

      {/* Cinematic Vignette Overlay */}
      {vignette && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(circle at center, transparent 55%, rgba(0,0,0,0.65) 100%)',
            pointerEvents: 'none',
          }}
        />
      )}
    </div>
  );
};
