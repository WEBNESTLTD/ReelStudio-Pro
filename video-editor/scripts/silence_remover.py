"""
ReelStudio Silence Remover
Detects and removes pauses and dead air from speech/dialogue videos.
Provides both non-destructive JSON cut lists for Remotion and exported trimmed media via FFmpeg/Auto-Editor.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def detect_silence_ffmpeg(video_path, noise_threshold_db=-35, min_silence_duration=0.4):
    """
    Detect non-silent segments in a video file using FFmpeg's silencedetect filter.
    Returns list of active speech intervals: [{'start': s, 'end': e, 'duration': d}]
    """
    cmd = [
        'ffmpeg',
        '-i', str(video_path),
        '-af', f'silencedetect=noise={noise_threshold_db}dB:d={min_silence_duration}',
        '-f', 'null',
        '-'
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    lines = res.stderr.splitlines()
    
    silence_starts = []
    silence_ends = []
    
    for line in lines:
        if 'silence_start:' in line:
            parts = line.split('silence_start:')
            if len(parts) > 1:
                silence_starts.append(float(parts[1].split()[0]))
        elif 'silence_end:' in line:
            parts = line.split('silence_end:')
            if len(parts) > 1:
                silence_ends.append(float(parts[1].split()[0]))
                
    # Get total video duration
    dur_cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(video_path)
    ]
    dur_res = subprocess.run(dur_cmd, stdout=subprocess.PIPE, text=True)
    total_duration = float(dur_res.stdout.strip()) if dur_res.stdout.strip() else 0.0
    
    # Invert silence intervals into active speech segments
    active_segments = []
    cur_pos = 0.0
    
    for i in range(len(silence_starts)):
        s_start = silence_starts[i]
        if s_start > cur_pos + 0.1:
            active_segments.append({
                'start_sec': round(cur_pos, 3),
                'end_sec': round(s_start, 3),
                'duration_sec': round(s_start - cur_pos, 3)
            })
        if i < len(silence_ends):
            cur_pos = silence_ends[i]
            
    if cur_pos < total_duration - 0.1:
        active_segments.append({
            'start_sec': round(cur_pos, 3),
            'end_sec': round(total_duration, 3),
            'duration_sec': round(total_duration - cur_pos, 3)
        })
        
    return {
        'total_duration': total_duration,
        'silence_count': len(silence_starts),
        'speech_segments_count': len(active_segments),
        'segments': active_segments
    }

def remove_silence_export(video_path, output_path, noise_threshold_db=-35, min_silence_duration=0.4):
    """Export trimmed video with dead air removed using FFmpeg filtergraph."""
    detection = detect_silence_ffmpeg(video_path, noise_threshold_db, min_silence_duration)
    segments = detection['segments']
    
    if not segments:
        print("No active speech intervals detected or video is already continuous.")
        return video_path
        
    # Build filtergraph to extract and concatenate active speech
    filter_parts = []
    concat_inputs = ""
    for idx, seg in enumerate(segments):
        start = seg['start_sec']
        end = seg['end_sec']
        filter_parts.append(f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{idx}];")
        filter_parts.append(f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{idx}];")
        concat_inputs += f"[v{idx}][a{idx}]"
        
    filter_complex = "".join(filter_parts) + f"{concat_inputs}concat=n={len(segments)}:v=1:a=1[outv][outa]"
    
    cmd = [
        'ffmpeg', '-y',
        '-i', str(video_path),
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-map', '[outa]',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        str(output_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Exported trimmed video (silence removed): {output_path}")
    return str(output_path)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        v = sys.argv[1]
        print(f"Analyzing silence in: {v}")
        res = detect_silence_ffmpeg(v)
        print(json.dumps(res, indent=2))
    else:
        print("Usage: python silence_remover.py <video_file>")
