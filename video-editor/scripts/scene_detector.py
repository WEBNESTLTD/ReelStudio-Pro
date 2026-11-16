"""
ReelStudio Scene Detector
Detects scene cuts, shot boundaries, and generates timestamp cut-lists for Remotion timelines.
Uses PySceneDetect if installed, with native FFmpeg scene-detection filter fallback.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def detect_scenes_pyscenedetect(video_path, threshold=27.0):
    """Detect scenes using PySceneDetect library (v0.6+ / v0.7+)."""
    try:
        from scenedetect import open_video, SceneManager, ContentDetector
        
        video = open_video(str(video_path))
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=threshold))
        
        scene_manager.detect_scenes(video=video)
        scene_list = scene_manager.get_scene_list()
        
        scenes = []
        for i, scene in enumerate(scene_list):
            start_sec = scene[0].seconds
            end_sec = scene[1].seconds
            scenes.append({
                'scene_index': i + 1,
                'start_sec': round(start_sec, 3),
                'end_sec': round(end_sec, 3),
                'duration_sec': round(end_sec - start_sec, 3),
                'start_frame': scene[0].frame_num,
                'end_frame': scene[1].frame_num,
            })
        return {'engine': 'PySceneDetect v0.7', 'scenes': scenes}
    except Exception as e:
        print(f"PySceneDetect error: {e}")
        return None

def detect_scenes_ffmpeg(video_path, threshold=0.35):
    """Detect scenes using FFmpeg's built-in scene filter fallback."""
    cmd = [
        'ffmpeg',
        '-i', str(video_path),
        '-filter_complex', f"select='gt(scene,{threshold})',showinfo",
        '-f', 'null',
        '-'
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    lines = result.stderr.split('\n')
    
    timestamps = [0.0]
    for line in lines:
        if 'showinfo' in line and 'pts_time:' in line:
            parts = line.split('pts_time:')
            if len(parts) > 1:
                time_str = parts[1].split()[0]
                try:
                    t = float(time_str)
                    if t not in timestamps:
                        timestamps.append(t)
                except ValueError:
                    pass
                    
    # Format into scenes
    scenes = []
    for i in range(len(timestamps)):
        start = timestamps[i]
        end = timestamps[i + 1] if i + 1 < len(timestamps) else None
        scenes.append({
            'scene_index': i + 1,
            'start_sec': round(start, 3),
            'end_sec': round(end, 3) if end is not None else -1,
            'duration_sec': round(end - start, 3) if end is not None else -1
        })
    return {'engine': 'FFmpeg Native Scene Filter', 'scenes': scenes}

def detect_scenes(video_path, threshold=0.35):
    """Run scene detection with automated engine selection."""
    print(f"Detecting scenes for: {video_path}")
    result = detect_scenes_pyscenedetect(video_path)
    if result is None:
        print("PySceneDetect not present in environment; utilizing native FFmpeg engine.")
        result = detect_scenes_ffmpeg(video_path, threshold)
    return result

if __name__ == '__main__':
    if len(sys.argv) > 1:
        vpath = sys.argv[1]
        res = detect_scenes(vpath)
        print(json.dumps(res, indent=2))
    else:
        print("Usage: python scene_detector.py <video_file>")
