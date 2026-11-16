import React from 'react';
import { Composition } from 'remotion';
import { ReelComposition } from './compositions/ReelComposition';
import { TestComposition } from './compositions/TestComposition';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 9:16 Instagram Reel Composition */}
      <Composition
        id="ReelComposition"
        component={ReelComposition}
        durationInFrames={300} // 10 seconds at 30 fps
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: 'ReelStudio Cinematic Reel',
          subtitle: 'AI-Powered Local Production',
          author: '@reelstudio',
        }}
      />

      {/* 16:9 Landscape Video Composition */}
      <Composition
        id="LandscapeComposition"
        component={ReelComposition}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: 'Cinematic Landscape Feature',
          subtitle: 'High Definition Master',
          author: '@reelstudio',
        }}
      />

      {/* 1:1 Square Composition */}
      <Composition
        id="SquareComposition"
        component={ReelComposition}
        durationInFrames={300}
        fps={30}
        width={1080}
        height={1080}
        defaultProps={{
          title: 'Square Format Showcase',
          subtitle: 'Social Feed Optimized',
          author: '@reelstudio',
        }}
      />

      {/* Verification / Fast Test Composition */}
      <Composition
        id="TestComposition"
        component={TestComposition}
        durationInFrames={90} // 3 seconds at 30 fps
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          testName: 'ReelStudio Environment Verification',
        }}
      />
    </>
  );
};
