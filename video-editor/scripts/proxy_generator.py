"""
ReelStudio Proxy Generator
Generates lightweight 720p/540p editing proxies for smooth timeline playback and low memory usage.
"""

import os
import sys
import subprocess
from pathlib import Path

def generate_proxy(input_video_path, output_proxy_path=None, resolution="720"):
    """
    Generate an editing proxy.
    resolution: "720" (720x1280 vertical or 1280x720 horizontal), "540"
    """
    input_path = Path(input_video_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Source video not found: {input_path}")
        
    if output_proxy_path is None:
        proxy_dir = input_path.parent / 'proxies'
        proxy_dir.mkdir(exist_ok=True)
        output_proxy_path = proxy_dir / f"{input_path.stem}_proxy_{resolution}p.mp4"
    else:
        output_proxy_path = Path(output_proxy_path)
        output_proxy_path.parent.mkdir(parents=True, exist_ok=True)
        
    scale_filter = f"scale=-2:{resolution}"
    
    # Fast proxy encode: ultrafast preset, moderate CRF, AAC audio
    cmd = [
        'ffmpeg',
        '-y',
        '-i', str(input_path),
        '-vf', scale_filter,
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '26',
        '-c:a', 'aac',
        '-b:a', '128k',
        str(output_proxy_path)
    ]
    
    print(f"Generating {resolution}p proxy for {input_path.name}...")
    subprocess.run(cmd, check=True)
    print(f"Proxy created: {output_proxy_path}")
    return str(output_proxy_path)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        generate_proxy(sys.argv[1])
    else:
        print("Usage: python proxy_generator.py <source_video.mp4>")
