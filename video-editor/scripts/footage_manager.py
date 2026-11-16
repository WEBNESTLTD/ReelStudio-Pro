"""
ReelStudio Footage Manager
Extracts metadata, generates thumbnails, organizes video footage, and manages project assets.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

SUPPORTED_EXTENSIONS = {'.mp4', '.mov', '.m4v', '.mkv', '.avi', '.webm'}

def get_ffprobe_metadata(video_path):
    """Extract detailed video and audio streams metadata using ffprobe."""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        str(video_path)
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(result.stdout)
        
        video_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), None)
        audio_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'audio'), None)
        fmt = data.get('format', {})
        
        duration = float(fmt.get('duration', video_stream.get('duration', 0) if video_stream else 0))
        
        # Calculate FPS
        fps = 30.0
        if video_stream and 'r_frame_rate' in video_stream:
            num, den = video_stream['r_frame_rate'].split('/')
            if float(den) > 0:
                fps = round(float(num) / float(den), 2)
                
        width = int(video_stream.get('width', 0)) if video_stream else 0
        height = int(video_stream.get('height', 0)) if video_stream else 0
        
        aspect_ratio = "9:16 (Vertical Reel)" if height > width else ("16:9 (Landscape)" if width > height else "1:1 (Square)")
        
        return {
            'file_name': os.path.basename(video_path),
            'path': str(video_path),
            'duration_seconds': round(duration, 2),
            'fps': fps,
            'width': width,
            'height': height,
            'aspect_ratio': aspect_ratio,
            'video_codec': video_stream.get('codec_name', 'unknown') if video_stream else None,
            'audio_codec': audio_stream.get('codec_name', 'none') if audio_stream else 'none',
            'size_mb': round(os.path.getsize(video_path) / (1024 * 1024), 2)
        }
    except Exception as e:
        return {'file_name': os.path.basename(video_path), 'error': str(e)}

def generate_thumbnail(video_path, output_image_path, timestamp_sec=1.0):
    """Generate high quality JPEG thumbnail from video."""
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    cmd = [
        'ffmpeg',
        '-y',
        '-ss', str(timestamp_sec),
        '-i', str(video_path),
        '-vframes', '1',
        '-q:v', '2',
        str(output_image_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return output_image_path

def scan_footage_directory(dir_path):
    """Scan directory recursively for video footage."""
    files = []
    p = Path(dir_path)
    if not p.exists():
        return files
    for f in p.rglob('*'):
        if f.suffix.lower() in SUPPORTED_EXTENSIONS:
            meta = get_ffprobe_metadata(f)
            files.append(meta)
    return files

if __name__ == '__main__':
    workspace_root = Path(__file__).resolve().parent.parent.parent
    target_dirs = [
        workspace_root / 'Originals',
        workspace_root / 'video-editor' / 'public' / 'footage'
    ]
    print("=== REELSTUDIO FOOTAGE SCANNER ===")
    all_footage = []
    for d in target_dirs:
        print(f"Scanning: {d}")
        found = scan_footage_directory(d)
        all_footage.extend(found)
        print(f"  Found {len(found)} clips in {d.name}")
        
    print(f"\nTotal video clips detected: {len(all_footage)}")
    print(json.dumps(all_footage, indent=2))
