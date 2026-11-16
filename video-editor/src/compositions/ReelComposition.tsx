import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { ColorGrading } from '../effects/ColorGrading';
import { CaptionRenderer } from '../captions/CaptionRenderer';
import { StoryProgressBar, LowerThird } from '../components/MotionGraphics';
import { ThreeDPerspectiveCard } from '../effects/ThreeDEffects';

export interface ReelProps {
  title?: string;
  subtitle?: string;
  author?: string;
}

export const ReelComposition: React.FC<ReelProps> = ({
  title = 'CINEMATIC STORY',
  subtitle = 'SHOT ON IPHONE & CAMERA',
  author = '@creator',
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();

  // Dynamic zoom (Ken Burns / slow push-in)
  const zoom = interpolate(frame, [0, durationInFrames], [1.0, 1.12], {
    extrapolateRight: 'clamp',
  });

  // Animated intro typography
  const titleEntrance = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.5, stiffness: 100 },
  });

  const subtitleFade = interpolate(frame, [20, 45], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Sample AI captions data for demonstration
  const sampleCaptions = [
    { start: 1.0, end: 1.8, word: 'CREATE' },
    { start: 1.85, end: 2.6, word: 'CINEMATIC' },
    { start: 2.65, end: 3.5, word: 'REELS' },
    { start: 4.0, end: 4.8, word: 'POWERED' },
    { start: 4.85, end: 5.6, word: 'BY' },
    { start: 5.65, end: 6.8, word: 'REELSTUDIO' },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: '#000000', overflow: 'hidden' }}>
      {/* Instagram Story Progress Bar */}
      <StoryProgressBar />

      {/* Background Media with Dynamic Zoom and Color Grading */}
      <ColorGrading preset="tealOrange" vignette={true}>
        <div
          style={{
            width: '100%',
            height: '100%',
            transform: `scale(${zoom})`,
            background: 'radial-gradient(circle at center, #1E293B 0%, #0F172A 70%, #020617 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {/* Subtle animated light orb */}
          <div
            style={{
              position: 'absolute',
              width: 600,
              height: 600,
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(236, 72, 153, 0.25) 0%, transparent 70%)',
              transform: `translate(${Math.sin(frame / 20) * 80}px, ${Math.cos(frame / 25) * 50}px)`,
            }}
          />
        </div>
      </ColorGrading>

      {/* Main Reel Title Section with 3D Floating Perspective */}
      <Sequence from={0} durationInFrames={120}>
        <AbsoluteFill
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 40,
            pointerEvents: 'none',
          }}
        >
          <ThreeDPerspectiveCard tiltAngle={12}>
            <div
              style={{
                transform: `scale(${titleEntrance})`,
                textAlign: 'center',
              }}
            >
              <h1
                style={{
                  fontSize: 84,
                  fontWeight: 900,
                  color: '#FFFFFF',
                  letterSpacing: 4,
                  textTransform: 'uppercase',
                  margin: 0,
                  textShadow: '0 8px 30px rgba(0,0,0,0.9)',
                }}
              >
                {title}
              </h1>
              <p
                style={{
                  opacity: subtitleFade,
                  fontSize: 34,
                  color: '#38BDF8',
                  fontWeight: 600,
                  letterSpacing: 6,
                  marginTop: 20,
                  textTransform: 'uppercase',
                }}
              >
                {subtitle}
              </p>
            </div>
          </ThreeDPerspectiveCard>
        </AbsoluteFill>
      </Sequence>

      {/* AI Animated Captions */}
      <Sequence from={30} durationInFrames={270}>
        <CaptionRenderer words={sampleCaptions} />
      </Sequence>

      {/* Instagram Safe Zone Branding / Handle */}
      <div
        style={{
          position: 'absolute',
          top: 80,
          left: 50,
          display: 'flex',
          alignItems: 'center',
          gap: 14,
        }}
      >
        <div
          style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: 'linear-gradient(135deg, #F43F5E, #FB923C)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: 22,
            color: '#FFFFFF',
          }}
        >
          RS
        </div>
        <span style={{ fontSize: 26, fontWeight: 700, color: '#F8FAFC' }}>
          {author}
        </span>
      </div>
    </AbsoluteFill>
  );
};
