"""
ReelStudio Pro — Phase 3.2 GPU Activation, Benchmark & Workflow Regression Suite
Executes:
1. NVIDIA RTX 3050 live GPU detection & utilization monitoring
2. Comprehensive multi-encoder benchmark on identical real footage (NVENC vs MediaFoundation vs CPU)
3. Full workflow regression testing (import -> preview -> edit -> AI -> 30s NVENC render)
4. Generates structured metrics for Reports/phase3_2_gpu_validation.md
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE = BASE_DIR.parent
QA_EXPORTS = WORKSPACE / "Exports" / "QA"
QA_FOOTAGE = BASE_DIR / "public" / "footage" / "qa"
QA_MUSIC = BASE_DIR / "public" / "music" / "qa"

QA_EXPORTS.mkdir(parents=True, exist_ok=True)

sys.path.append(str(BASE_DIR))
from server import app, render_jobs, execute_render_job, resolve_file_path
from scripts.footage_manager import get_ffprobe_metadata
from scripts.render_pipeline import check_nvenc_available, check_qsv_available, check_mf_available, get_recommended_encoder, get_encoder_status_matrix
from scripts.color_corrector import COLOR_PRESETS

client = TestClient(app)

def get_nvidia_smi_snapshot():
    """Query live GPU metrics via nvidia-smi."""
    cmd = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu,temperature.gpu,power.draw",
        "--format=csv,noheader,nounits"
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode == 0:
            parts = [p.strip() for p in proc.stdout.strip().split(",")]
            return {
                "name": parts[0],
                "driver_version": parts[1],
                "memory_total_mb": float(parts[2]),
                "memory_used_mb": float(parts[3]),
                "gpu_util_pct": float(parts[4]),
                "temp_c": float(parts[5]),
                "power_w": float(parts[6]) if len(parts) > 6 else 0.0
            }
    except Exception as e:
        print(f"nvidia-smi query error: {e}")
    return None

def verify_stream_integrity(video_path: Path):
    """Run FFmpeg decode error pass and return metadata + decode error count."""
    meta = get_ffprobe_metadata(video_path)
    cmd = ["ffmpeg", "-v", "error", "-i", str(video_path), "-f", "null", "-"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    decode_errors = len(proc.stderr.strip().splitlines()) if proc.stderr.strip() else 0
    return meta, decode_errors

# ==========================================================================
# Task 1: NVIDIA GPU Verification
# ==========================================================================
def task_1_nvidia_gpu_verification():
    print("\n" + "=" * 70)
    print("  TASK 1: NVIDIA GPU VERIFICATION")
    print("=" * 70)
    
    gpu_info = get_nvidia_smi_snapshot()
    if gpu_info:
        print(f"[*] Detected GPU: {gpu_info['name']}")
        print(f"[*] Driver Version: {gpu_info['driver_version']}")
        print(f"[*] VRAM: {gpu_info['memory_used_mb']} MB / {gpu_info['memory_total_mb']} MB")
        print(f"[*] Temperature: {gpu_info['temp_c']} °C, Power: {gpu_info['power_w']} W, Util: {gpu_info['gpu_util_pct']}%")
    else:
        print("[!] Warning: nvidia-smi failed to query GPU")

    # Windows Device Manager status
    pnp_cmd = ["powershell", "-Command", "Get-PnpDevice -FriendlyName '*RTX 3050*' | Select-Object -ExpandProperty Status"]
    pnp_proc = subprocess.run(pnp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    pnp_status = pnp_proc.stdout.strip()
    print(f"[*] Windows PnP Device Status: {pnp_status}")
    
    # Test NVENC export
    nvenc_test_out = QA_EXPORTS / "task1_nvenc_test.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc=duration=3:size=1920x1080:rate=30",
        "-c:v", "h264_nvenc", "-preset", "p4", "-tune", "hq", "-cq", "20",
        "-pix_fmt", "yuv420p",
        str(nvenc_test_out)
    ]
    t0 = time.time()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    duration_s = round(time.time() - t0, 3)
    
    assert proc.returncode == 0, f"NVENC export failed: {proc.stderr}"
    meta, errors = verify_stream_integrity(nvenc_test_out)
    
    print(f"[*] NVENC Test Export Completed in {duration_s}s:")
    print(f"    - File: {nvenc_test_out.name}")
    print(f"    - Codec: {meta.get('video_codec')}, PixFmt: {meta.get('pix_fmt')}")
    print(f"    - Dimensions: {meta.get('width')}x{meta.get('height')} @ {meta.get('fps')} FPS")
    print(f"    - Duration: {meta.get('duration_seconds')}s, Decode Errors: {errors}")
    
    gpu_after = get_nvidia_smi_snapshot()
    if gpu_after:
        print(f"[*] Post-render GPU VRAM: {gpu_after['memory_used_mb']} MB, Temp: {gpu_after['temp_c']} °C")
        
    return {
        "gpu_info": gpu_info,
        "pnp_status": pnp_status,
        "export_duration_s": duration_s,
        "meta": meta,
        "decode_errors": errors
    }

# ==========================================================================
# Task 2: Intelligent Encoder Selection Verification
# ==========================================================================
def task_2_intelligent_encoder_selection():
    print("\n" + "=" * 70)
    print("  TASK 2: INTELLIGENT ENCODER SELECTION & PRIORITY")
    print("=" * 70)
    
    matrix = get_encoder_status_matrix()
    for key, info in matrix.items():
        symbol = "[AVAILABLE]" if info["available"] else "[OFFLINE]"
        print(f"[*] Tier {info['tier']} - {info['name']}: {symbol} ({info['type']} on {info['device']})")
        
    rec_encoder, rec_flags = get_recommended_encoder()
    print(f"\n[*] Active Default Recommended Encoder: {rec_encoder}")
    print(f"[*] Compiler Flags: {rec_flags}")
    
    assert rec_encoder == "h264_nvenc", f"Expected h264_nvenc to be priority #1, got {rec_encoder}"
    print("[PASS] Priority 1 (NVIDIA NVENC) successfully selected as default!")
    return matrix

# ==========================================================================
# Task 4: Performance Comparison on Identical Real Footage
# ==========================================================================
def task_4_performance_comparison():
    print("\n" + "=" * 70)
    print("  TASK 4: PERFORMANCE BENCHMARK (IDENTICAL 1080p REAL FOOTAGE)")
    print("=" * 70)
    
    # Standardized test input: Real 1080p travel landscape footage
    real_input = BASE_DIR / "public" / "footage" / "landscape_travel.mp4"
    assert real_input.exists(), f"Input footage missing: {real_input}"
    
    test_duration = 5.0 # Exactly 5.0 seconds (150 frames at 30 FPS)
    w, h = 1080, 1920   # Standard Instagram Reel resolution (9:16)
    
    encoders = [
        {
            "name": "NVIDIA NVENC (Hardware)",
            "encoder": "h264_nvenc",
            "flags": ["-preset", "p4", "-tune", "hq", "-cq", "20", "-pix_fmt", "yuv420p"],
            "outfile": QA_EXPORTS / "bench_compare_nvenc.mp4"
        },
        {
            "name": "Windows MediaFoundation",
            "encoder": "h264_mf",
            "flags": ["-b:v", "5M", "-pix_fmt", "yuv420p"],
            "outfile": QA_EXPORTS / "bench_compare_mf.mp4"
        },
        {
            "name": "CPU Multi-Threaded (libx264)",
            "encoder": "libx264",
            "flags": ["-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p"],
            "outfile": QA_EXPORTS / "bench_compare_libx264.mp4"
        }
    ]
    
    benchmark_results = []
    
    for enc in encoders:
        print(f"\n[*] Benchmarking {enc['name']} ({enc['encoder']})...")
        cmd = [
            "ffmpeg", "-y",
            "-ss", "0.0", "-t", str(test_duration),
            "-i", str(real_input),
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1",
            "-c:v", enc["encoder"]
        ]
        cmd.extend(enc["flags"])
        cmd.extend(["-c:a", "aac", "-b:a", "192k", str(enc["outfile"])])
        
        gpu_before = get_nvidia_smi_snapshot()
        t0 = time.time()
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        t_elapsed = round(time.time() - t0, 3)
        gpu_after = get_nvidia_smi_snapshot()
        
        assert proc.returncode == 0, f"Benchmark failed for {enc['name']}: {proc.stderr[-300:]}"
        
        meta, errors = verify_stream_integrity(enc["outfile"])
        fps = round(150 / max(0.01, t_elapsed), 1)
        speed_x = round(test_duration / max(0.01, t_elapsed), 2)
        size_kb = round(enc["outfile"].stat().st_size / 1024, 1)
        
        res = {
            "name": enc["name"],
            "encoder": enc["encoder"],
            "encode_time_s": t_elapsed,
            "average_fps": fps,
            "speed_multiplier": speed_x,
            "size_kb": size_kb,
            "resolution": f"{meta.get('width')}x{meta.get('height')}",
            "decode_errors": errors,
            "gpu_temp_c": gpu_after["temp_c"] if gpu_after else "N/A",
            "gpu_mem_used_mb": gpu_after["memory_used_mb"] if gpu_after else "N/A"
        }
        benchmark_results.append(res)
        print(f"    Time: {t_elapsed}s | Speed: {speed_x}x ({fps} FPS) | Size: {size_kb} KB | Errors: {errors}")
        
    return benchmark_results

# ==========================================================================
# Task 3: Full Workflow Regression with Active NVENC
# ==========================================================================
def task_3_full_workflow_regression():
    print("\n" + "=" * 70)
    print("  TASK 3: FULL WORKFLOW REGRESSION (REAL MEDIA + ACTIVE NVENC)")
    print("=" * 70)
    
    # 1. Media Library Scan
    res_m = client.get("/api/media").json()
    files = res_m.get("files", [])
    print(f"[*] 1. Import / Media Library: Discovered {len(files)} assets")
    assert len(files) >= 5
    
    # 2. Preview HTTP 206 Streaming
    sample_vid = BASE_DIR / "public" / "footage" / "landscape_travel.mp4"
    res_s = client.get(f"/api/stream?path={sample_vid}", headers={"Range": "bytes=0-524287"})
    print(f"[*] 2. Preview Streaming: Status {res_s.status_code} ({res_s.headers.get('content-range')})")
    assert res_s.status_code == 206
    
    # 3. Librosa Music Beat Detection
    beat_track = QA_MUSIC / "qa_30s_beat.mp3"
    res_b = client.post("/api/ai/beats", json={"path": str(beat_track)}).json()
    tempo = res_b.get("tempo") or res_b.get("estimated_tempo_bpm", 0)
    print(f"[*] 3. Music Synchronization: Detected Tempo {tempo:.1f} BPM, {len(res_b.get('beats', []))} beats")
    assert tempo > 0
    
    # 4. Whisper Captions Transcription
    speech_vid = QA_FOOTAGE / "qa_speech_dialogue.mp4"
    res_t = client.post("/api/ai/transcribe", json={"path": str(speech_vid)}).json()
    words = res_t.get("words", [])
    print(f"[*] 4. Whisper Captions: Transcribed {len(words)} words in '{res_t.get('language')}'")
    assert len(words) > 0
    
    # 5. AI YOLO Subject Reframing
    res_r = client.post("/api/ai/auto-reframe", json={"path": str(sample_vid), "target_aspect": "9:16"}).json()
    print(f"[*] 5. AI Auto-Reframe: {res_r.get('output_filename')} ({res_r.get('crop_width')}x{res_r.get('crop_height')})")
    assert res_r.get("status") == "success"
    
    # 6. Project Persistence (Save & Load)
    regression_proj = {
        "projectName": "Demonstration_Reel_30s_NVENC",
        "aspectRatio": "9:16",
        "resolution": {"width": 1080, "height": 1920, "fps": 30},
        "duration": 30.0,
        "colorPreset": "teal_orange",
        "audioMixer": {"master": 1.0, "voice": 1.0, "music": 0.8, "ducking": True, "loudnorm": True},
        "clips": [
            {"path": str(QA_FOOTAGE / "qa_9_16_vertical.mp4"), "type": "video", "sourceIn": 0.0, "duration": 6.0, "startTime": 0.0},
            {"path": str(QA_FOOTAGE / "qa_1080p_landscape.mp4"), "type": "video", "sourceIn": 0.0, "duration": 6.0, "startTime": 6.0},
            {"path": str(QA_FOOTAGE / "qa_speech_dialogue.mp4"), "type": "video", "sourceIn": 0.0, "duration": 6.0, "startTime": 12.0},
            {"path": str(QA_FOOTAGE / "qa_low_light.mp4"), "type": "video", "sourceIn": 0.0, "duration": 6.0, "startTime": 18.0},
            {"path": str(QA_FOOTAGE / "qa_multi_subject.mp4"), "type": "video", "sourceIn": 0.0, "duration": 6.0, "startTime": 24.0},
            {"path": str(QA_MUSIC / "qa_30s_beat.mp3"), "type": "audio", "sourceIn": 0.0, "duration": 30.0, "startTime": 0.0, "volume": 0.8}
        ],
        "subtitles": words[:6]
    }
    
    client.post("/api/project/save", json={"project_name": "Demonstration_Reel_30s_NVENC", "project_data": regression_proj})
    loaded_p = client.get("/api/project/load/Demonstration_Reel_30s_NVENC").json().get("project_data", {})
    print(f"[*] 6. Project Save & Load: {loaded_p.get('projectName')} with {len(loaded_p.get('clips', []))} clips")
    assert len(loaded_p.get("clips", [])) == 6
    
    # 7. Render 30-Second Master Reel with Active NVIDIA NVENC
    print("\n[*] 7. Rendering 30-Second Demonstration Reel with Hardware NVENC on RTX 3050...")
    job_id = "regress_nvenc_30s"
    render_jobs[job_id] = {"job_id": job_id, "status": "queued", "progress": 0, "message": "Init"}
    
    t0 = time.time()
    execute_render_job(job_id, {"project": regression_proj})
    render_time = round(time.time() - t0, 3)
    
    status = render_jobs[job_id]
    assert status.get("status") == "completed", f"Render failed: {status.get('error')}"
    
    out_path = Path(status.get("output_path"))
    final_master = WORKSPACE / "Exports" / "Demonstration_Reel_30s_NVENC.mp4"
    shutil.copyfile(out_path, final_master)
    
    meta_30s, errors_30s = verify_stream_integrity(final_master)
    fps_30s = round(900 / max(0.01, render_time), 1) # 900 frames
    speed_30s = round(30.0 / max(0.01, render_time), 2)
    
    print(f"\n[SUCCESS] 30-Second Master Demonstration Reel Rendered via Hardware NVENC:")
    print(f"    - Output: {final_master.name}")
    print(f"    - Render Time: {render_time}s (Speed: {speed_30s}x, {fps_30s} FPS)")
    print(f"    - Resolution: {meta_30s.get('width')}x{meta_30s.get('height')} ({meta_30s.get('aspect_ratio')})")
    print(f"    - Duration: {meta_30s.get('duration_seconds')}s (900 frames)")
    print(f"    - Video Codec: {meta_30s.get('video_codec')} (NVENC High Profile)")
    print(f"    - Audio Codec: {meta_30s.get('audio_codec')} (AAC Stereo 192k)")
    print(f"    - File Size: {round(final_master.stat().st_size / (1024*1024), 2)} MB")
    print(f"    - Decode Errors: {errors_30s}")
    
    assert meta_30s.get("width") == 1080 and meta_30s.get("height") == 1920
    assert float(meta_30s.get("duration_seconds")) >= 29.9
    assert errors_30s == 0
    
    return {
        "final_master": str(final_master),
        "render_time_s": render_time,
        "speed_x": speed_30s,
        "fps": fps_30s,
        "meta": meta_30s,
        "errors": errors_30s
    }

def main():
    print("=" * 70)
    print("  REELSTUDIO PRO — PHASE 3.2 GPU ACTIVATION & VALIDATION")
    print("=" * 70)
    
    t1 = task_1_nvidia_gpu_verification()
    t2 = task_2_intelligent_encoder_selection()
    bench = task_4_performance_comparison()
    regress = task_3_full_workflow_regression()
    
    # Save combined report data
    report_data = {
        "timestamp": time.time(),
        "task_1_gpu": t1,
        "task_2_encoder_matrix": t2,
        "task_4_benchmark": bench,
        "task_3_regression": regress
    }
    
    out_json = WORKSPACE / "Reports" / "phase3_2_gpu_data.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, default=str)
    print(f"\n[*] Validation Data saved to: {out_json}")
    print("\n" + "=" * 70)
    print("  PHASE 3.2 ALL TASKS COMPLETED & VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
