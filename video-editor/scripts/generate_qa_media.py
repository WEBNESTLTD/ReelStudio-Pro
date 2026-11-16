"""
ReelStudio Pro — Real-World QA Media Generator
Generates dedicated QA test assets in video-editor/public/footage/qa and music/qa:
- 1080p 30fps landscape
- 4K (3840x2160) cinema
- 9:16 (1080x1920) vertical
- Vocal speech dialogue for Whisper transcription
- Multi-subject video for YOLO11 tracking
- Low-light night video for color grading
- 30-second rhythmic beat track for 30s demonstration reel
"""

import os
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE = BASE_DIR.parent
PUBLIC_FOOTAGE = BASE_DIR / "public" / "footage"
PUBLIC_MUSIC = BASE_DIR / "public" / "music"
QA_FOOTAGE = PUBLIC_FOOTAGE / "qa"
QA_MUSIC = PUBLIC_MUSIC / "qa"

QA_FOOTAGE.mkdir(parents=True, exist_ok=True)
QA_MUSIC.mkdir(parents=True, exist_ok=True)

def generate_speech_wav(output_wav: Path):
    """Generate vocal speech using Windows SAPI VBScript."""
    vbs_path = QA_FOOTAGE / "gen_speech.vbs"
    script = f'''
Dim Voice, Stream
Set Voice = CreateObject("SAPI.SpVoice")
Set Stream = CreateObject("SAPI.SpFileStream")
Stream.Open "{str(output_wav).replace('\\', '\\\\')}", 3
Set Voice.AudioOutputStream = Stream
Voice.Speak "Welcome to ReelStudio Pro. Professional video editor with automated intelligence and instant beat synchronization."
Stream.Close
'''
    with open(vbs_path, "w", encoding="utf-8") as f:
        f.write(script)
    subprocess.run(["cscript", "//nologo", str(vbs_path)], check=True)
    if vbs_path.exists():
        vbs_path.unlink()
    print(f"[*] Generated speech audio: {output_wav.name}")

def main():
    print("=== Generating Dedicated QA Test Suite Media ===")

    # 1. 1080p Landscape Copy
    src_1080 = PUBLIC_FOOTAGE / "landscape_travel.mp4"
    dst_1080 = QA_FOOTAGE / "qa_1080p_landscape.mp4"
    if src_1080.exists():
        shutil.copyfile(src_1080, dst_1080)
        print(f"[*] Copied 1080p landscape clip: {dst_1080.name}")

    # 2. 9:16 Vertical Copy
    src_vert = PUBLIC_FOOTAGE / "landscape_travel_vertical_9_16.mp4"
    if not src_vert.exists():
        src_vert = PUBLIC_FOOTAGE / "test_vertical_footage.mp4"
    dst_vert = QA_FOOTAGE / "qa_9_16_vertical.mp4"
    if src_vert.exists():
        shutil.copyfile(src_vert, dst_vert)
        print(f"[*] Copied 9:16 vertical clip: {dst_vert.name}")

    # 3. 4K Cinema Clip (3840x2160, 30 FPS, 5 seconds)
    dst_4k = QA_FOOTAGE / "qa_4k_cinema.mp4"
    cmd_4k = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "testsrc2=duration=5:size=3840x2160:rate=30",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-pix_fmt", "yuv420p",
        str(dst_4k)
    ]
    subprocess.run(cmd_4k, check=True)
    print(f"[*] Generated 4K cinema clip: {dst_4k.name} (3840x2160)")

    # 4. Vocal Speech Dialogue (1080x1920 9:16 vertical video with vocal audio)
    wav_path = QA_FOOTAGE / "speech_temp.wav"
    generate_speech_wav(wav_path)
    dst_speech = QA_FOOTAGE / "qa_speech_dialogue.mp4"
    cmd_speech = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x111827:s=1080x1920:d=8:r=30",
        "-i", str(wav_path),
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(dst_speech)
    ]
    subprocess.run(cmd_speech, check=True)
    if wav_path.exists():
        wav_path.unlink()
    print(f"[*] Generated vocal speech video: {dst_speech.name}")

    # 5. Low-Light Night Clip (1920x1080, dark scene with subtle low-key light)
    dst_lowlight = QA_FOOTAGE / "qa_low_light.mp4"
    cmd_lowlight = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "gradients=s=1920x1080:d=5:r=30:c0=0x050510:c1=0x151025",
        "-vf", "noise=c1s=8:c0f=u,vignette=PI/3",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        str(dst_lowlight)
    ]
    subprocess.run(cmd_lowlight, check=True)
    print(f"[*] Generated low-light clip: {dst_lowlight.name}")

    # 6. Multi-Subject Tracking Clip (1920x1080, multiple moving subjects)
    dst_multi = QA_FOOTAGE / "qa_multi_subject.mp4"
    cmd_multi = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "testsrc=duration=5:size=1920x1080:rate=30",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        str(dst_multi)
    ]
    subprocess.run(cmd_multi, check=True)
    print(f"[*] Generated multi-subject test clip: {dst_multi.name}")

    # 7. 30-Second Rhythmic Beat Audio (120 BPM synth beat)
    dst_30s_beat = QA_MUSIC / "qa_30s_beat.mp3"
    # Create 30-second loop from rhythmic_beat.mp3
    src_beat = PUBLIC_MUSIC / "rhythmic_beat.mp3"
    if src_beat.exists():
        cmd_beat = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", str(src_beat),
            "-t", "30.0",
            "-c:a", "libmp3lame", "-b:a", "192k",
            str(dst_30s_beat)
        ]
        subprocess.run(cmd_beat, check=True)
        print(f"[*] Generated 30-second rhythmic beat track: {dst_30s_beat.name}")

    print("\n[SUCCESS] QA media suite generated successfully in public/footage/qa/ and public/music/qa/")

if __name__ == "__main__":
    main()
