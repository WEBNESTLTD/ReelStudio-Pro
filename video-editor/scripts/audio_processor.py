"""
ReelStudio Audio Processor
Handles audio ducking, loudness normalization (EBU R128), fade ins/outs, and audio mixing.
"""

import os
import sys
import subprocess
from pathlib import Path

def normalize_audio(input_audio, output_audio):
    """Normalize audio loudness to EBU R128 standard (-16 LUFS for online media)."""
    cmd = [
        'ffmpeg',
        '-y',
        '-i', str(input_audio),
        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
        '-c:a', 'aac',
        '-b:a', '192k',
        str(output_audio)
    ]
    subprocess.run(cmd, check=True)
    return output_audio

def mix_music_and_voiceover(voice_path, music_path, output_path, music_duck_volume=0.2):
    """
    Mix dialogue voiceover with background music, automatically ducking music during speech.
    """
    filter_complex = (
        f"[1:a]asplit=2[music1][music2];"
        f"[music1][0:a]sidechaincompress=threshold=0.1:ratio=5:attack=20:release=300[ducked_music];"
        f"[ducked_music]volume={music_duck_volume}[quiet_music];"
        f"[0:a][quiet_music]amix=inputs=2:duration=first:dropout_transition=2[outa]"
    )
    cmd = [
        'ffmpeg',
        '-y',
        '-i', str(voice_path),
        '-i', str(music_path),
        '-filter_complex', filter_complex,
        '-map', '[outa]',
        '-c:a', 'aac',
        '-b:a', '192k',
        str(output_path)
    ]
    subprocess.run(cmd, check=True)
    return output_path

if __name__ == '__main__':
    print("ReelStudio Audio Processing Tools ready.")
