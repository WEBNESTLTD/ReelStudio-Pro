"""
ReelStudio Cinematic Color Corrector
Applies Hollywood color grades, contrast curves, saturation boosts, and 3D LUT simulations.
Presets include: Teal & Orange, Moody Monochrome, Warm Film, Vibrant Pop, and Vintage Gold.
"""

import os
import sys
import subprocess
from pathlib import Path

COLOR_PRESETS = {
    'teal_orange': {
        'name': 'Teal & Orange (Blockbuster Cinema)',
        'filter': "eq=contrast=1.18:brightness=-0.02:saturation=1.28,colorbalance=rs=0.08:gs=-0.02:bs=-0.1:rh=0.06:gh=-0.03:bh=-0.08:rm=-0.05:gm=0.04:bm=0.12"
    },
    'moody_monochrome': {
        'name': 'Moody Noir Monochrome',
        'filter': "hue=s=0,eq=contrast=1.35:brightness=-0.04"
    },
    'warm_film': {
        'name': 'Warm Film Stock (Kodak / Golden Hour)',
        'filter': "eq=contrast=1.12:saturation=1.15,colorbalance=rs=0.1:gs=0.04:bs=-0.08:rm=0.06:gm=0.02:bm=-0.05"
    },
    'vibrant_pop': {
        'name': 'Vibrant Social Pop',
        'filter': "eq=contrast=1.1:saturation=1.4:brightness=0.02"
    },
    'vintage_gold': {
        'name': 'Vintage 1970s Gold',
        'filter': "curves=vintage,eq=contrast=1.05:saturation=0.9"
    }
}

def apply_color_grade(video_path, output_path, preset='teal_orange', add_vignette=True):
    """
    Apply cinematic color grading to video footage using FFmpeg.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    preset_data = COLOR_PRESETS.get(preset, COLOR_PRESETS['teal_orange'])
    vf = preset_data['filter']
    
    if add_vignette:
        vf += ",vignette=PI/4"
        
    cmd = [
        'ffmpeg', '-y',
        '-i', str(video_path),
        '-vf', vf,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'copy',
        str(output_path)
    ]
    print(f"Applying '{preset_data['name']}' grade to {video_path.name}...")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Color-graded master saved to: {output_path}")
    return str(output_path)

if __name__ == '__main__':
    if len(sys.argv) > 2:
        apply_color_grade(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'teal_orange')
    else:
        print("Usage: python color_corrector.py <input_video> <output_video> [preset]")
        print("Available presets:", list(COLOR_PRESETS.keys()))
