"""
ReelStudio Render Pipeline — Intelligent Encoder Selection
Multi-tier hardware acceleration with verified fallback:
1. NVIDIA NVENC (when genuinely available on RTX 3050)
2. Intel QuickSync (when genuinely available and supported)
3. Windows Media Foundation (when suitable)
4. CPU libx264 (reliable universal fallback)
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Tuple, List, Dict, Any

def test_encoder_probe(encoder_name: str, extra_args: List[str] = None) -> bool:
    """Run a micro-probe to check if an encoder can genuinely initialize and encode a frame."""
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=duration=0.1:size=320x240:rate=30',
        '-c:v', encoder_name
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.extend(['-f', 'null', '-'])
    try:
        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc.returncode == 0
    except Exception:
        return False

def check_nvenc_available() -> bool:
    """Verify if NVIDIA NVENC hardware encoder is currently operational."""
    return test_encoder_probe('h264_nvenc', ['-pix_fmt', 'yuv420p'])

def check_qsv_available() -> bool:
    """Verify if Intel QuickSync hardware encoder is currently operational."""
    return test_encoder_probe('h264_qsv')

def check_mf_available() -> bool:
    """Verify if Windows Media Foundation encoder is available."""
    return test_encoder_probe('h264_mf')

def get_encoder_status_matrix() -> Dict[str, Any]:
    """Inspect and report live runtime operational status of all 4 encoders."""
    nvenc_ok = check_nvenc_available()
    qsv_ok = check_qsv_available()
    mf_ok = check_mf_available()
    
    return {
        "nvenc": {
            "name": "NVIDIA NVENC (h264_nvenc)",
            "tier": 1,
            "type": "NVIDIA Hardware ASIC",
            "available": nvenc_ok,
            "device": "NVIDIA GeForce RTX 3050 6GB Laptop GPU"
        },
        "qsv": {
            "name": "Intel QuickSync (h264_qsv)",
            "tier": 2,
            "type": "Intel Hardware QSV",
            "available": qsv_ok,
            "device": "Intel UHD Graphics"
        },
        "mf": {
            "name": "Windows Media Foundation (h264_mf)",
            "tier": 3,
            "type": "Windows MFT Framework",
            "available": mf_ok,
            "device": "System Media Foundation MFT"
        },
        "libx264": {
            "name": "CPU Multi-Threaded (libx264)",
            "tier": 4,
            "type": "x86-64 SIMD Software",
            "available": True,
            "device": "Intel CPU (AVX2/FMA3)"
        }
    }

def get_recommended_encoder(preference: str = "auto") -> Tuple[str, List[str]]:
    """
    Intelligent Encoder Selection Priority:
    1. NVIDIA NVENC (when genuinely available)
    2. Intel QuickSync (when genuinely available and supported)
    3. Windows Media Foundation (when requested/suitable)
    4. CPU libx264 (reliable high-efficiency fallback)
    """
    if preference == "nvenc" or preference == "auto":
        if check_nvenc_available():
            print("[TIER 1 HARDWARE] NVIDIA NVENC H.264 is operational on RTX 3050.")
            return ('h264_nvenc', ['-preset', 'p4', '-tune', 'hq', '-cq', '20', '-pix_fmt', 'yuv420p'])
            
    if preference == "qsv" or preference == "auto":
        if check_qsv_available():
            print("[TIER 2 HARDWARE] Intel QuickSync Video H.264 is operational.")
            return ('h264_qsv', ['-global_quality', '20', '-pix_fmt', 'nv12'])
            
    if preference == "mf":
        if check_mf_available():
            print("[TIER 3 FRAMEWORK] Windows Media Foundation H.264 MFT is operational.")
            return ('h264_mf', ['-b:v', '5M'])

    print("[TIER 4 CPU FALLBACK] Utilizing CPU libx264 (universal master quality).")
    return ('libx264', ['-preset', 'fast', '-crf', '19', '-pix_fmt', 'yuv420p'])

def render_remotion_composition(composition_id: str, output_path: str, concurrency: int = 4) -> str:
    """Render Remotion composition using Remotion CLI."""
    video_editor_dir = Path(__file__).resolve().parent.parent
    out_p = Path(output_path).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        'npx',
        'remotion',
        'render',
        'src/index.ts',
        composition_id,
        str(out_p),
        f'--concurrency={concurrency}',
        '--pixel-format=yuv420p'
    ]
    print(f"Executing Remotion render: {composition_id} -> {out_p.name}")
    subprocess.run(cmd, cwd=str(video_editor_dir), check=True)
    print(f"Render complete: {out_p}")
    return str(out_p)

if __name__ == '__main__':
    print("=== REELSTUDIO INTELLIGENT ENCODER MATRIX ===")
    matrix = get_encoder_status_matrix()
    for k, v in matrix.items():
        print(f"[{'PASS' if v['available'] else 'OFFLINE'}] Tier {v['tier']}: {v['name']} ({v['type']})")
    rec, flags = get_recommended_encoder()
    print(f"\nActive Selected Encoder: {rec} with flags {flags}")
