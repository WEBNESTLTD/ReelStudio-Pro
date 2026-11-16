import { Config } from '@remotion/cli/config';

// ReelStudio Remotion Configuration
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setPixelFormat('yuv420p');
Config.setCodec('h264');
Config.setCrf(18);
Config.setConcurrency(4); // Balanced for 16 GB RAM system
