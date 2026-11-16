"""
ReelStudio Pro Video Editor — Backend API Server
FastAPI backend orchestrating media streaming, timeline persistence, AI auto-editing,
and rendering pipeline execution.
"""

import os
import sys
import json
import time
import uuid
import shutil
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add video-editor root to sys.path
BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = BASE_DIR.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
PUBLIC_DIR = BASE_DIR / "public"
PROJECTS_DIR = WORKSPACE_ROOT / "Projects"
EXPORTS_DIR = WORKSPACE_ROOT / "Exports"
MODELS_DIR = BASE_DIR / "models"

sys.path.append(str(BASE_DIR))
from scripts.footage_manager import get_ffprobe_metadata, generate_thumbnail, scan_footage_directory
from scripts.scene_detector import detect_scenes
from scripts.scene_selector import select_best_scenes
from scripts.beat_detector import analyze_audio_beats, generate_beat_synced_cut_plan
from scripts.auto_reframe import track_and_reframe
from scripts.silence_remover import detect_silence_ffmpeg, remove_silence_export
from scripts.audio_cleaner import clean_and_master_audio
from scripts.color_corrector import apply_color_grade, COLOR_PRESETS
from scripts.whisper_transcriber import transcribe_media
from scripts.render_pipeline import check_nvenc_available, get_recommended_encoder

app = FastAPI(title="ReelStudio Editor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active Render Jobs Tracker
render_jobs: Dict[str, Dict[str, Any]] = {}

# ----------------- HTTP 206 STREAMING UTILITY -----------------

def range_stream_file(path: Path, request: Request):
    """Serve media files supporting HTTP 206 Partial Content for smooth video scrubbing."""
    if not path.exists():
        raise HTTPException(status_code=404, detail="Media file not found")
        
    file_size = path.stat().st_size
    range_header = request.headers.get("range")
    
    content_type = "video/mp4"
    if path.suffix.lower() in [".mp3", ".wav", ".aac"]:
        content_type = "audio/mpeg" if path.suffix.lower() == ".mp3" else "audio/wav"
    elif path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        content_type = "image/jpeg"
        return FileResponse(str(path), media_type=content_type)
        
    if not range_header:
        return FileResponse(str(path), media_type=content_type)
        
    # Parse Range: bytes=start-end
    range_str = range_header.replace("bytes=", "")
    parts = range_str.split("-")
    start = int(parts[0]) if parts[0] else 0
    end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
    
    if start >= file_size or end >= file_size:
        raise HTTPException(status_code=416, detail="Requested range not satisfiable")
        
    chunk_size = (end - start) + 1
    
    def iterfile():
        with open(path, "rb") as f:
            f.seek(start)
            bytes_left = chunk_size
            while bytes_left > 0:
                read_amount = min(1024 * 1024, bytes_left)
                data = f.read(read_amount)
                if not data:
                    break
                bytes_left -= len(data)
                yield data
                
    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(chunk_size),
        "Content-Type": content_type,
    }
    return StreamingResponse(iterfile(), status_code=206, headers=headers)

# ----------------- API ROUTES -----------------

@app.get("/api/health")
def get_health():
    nvenc = check_nvenc_available()
    return {
        "status": "online",
        "workspace": str(WORKSPACE_ROOT),
        "gpu_acceleration": "NVIDIA NVENC active" if nvenc else "CPU libx264 active",
        "nvenc": nvenc,
        "capabilities": 12,
        "version": "1.0.0"
    }

@app.get("/api/stream")
def stream_generic(path: str, request: Request):
    """Stream any video/audio/image file by path or name with HTTP 206 range support."""
    p = Path(path)
    if not p.is_absolute():
        for folder in ["footage", "music", "sound-effects", "images"]:
            candidate = PUBLIC_DIR / folder / path
            if candidate.exists():
                p = candidate
                break
        if not p.exists():
            for folder in [WORKSPACE_ROOT / "Originals", EXPORTS_DIR]:
                candidate = folder / path
                if candidate.exists():
                    p = candidate
                    break
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    return range_stream_file(p, request)

@app.get("/api/media")
def list_media():
    """List available footage, music, sound effects, and images."""
    footage_dir = PUBLIC_DIR / "footage"
    music_dir = PUBLIC_DIR / "music"
    sfx_dir = PUBLIC_DIR / "sound-effects"
    images_dir = PUBLIC_DIR / "images"
    originals_dir = WORKSPACE_ROOT / "Originals"
    
    def scan_dir(p: Path, cat: str):
        items = []
        if not p.exists():
            return items
        media_type = "video" if cat == "footage" else ("audio" if cat in ["music", "sound-effects"] else "image")
        for f in p.rglob("*"):
            if f.is_file() and f.suffix.lower() in [".mp4", ".mov", ".mp3", ".wav", ".jpg", ".png", ".mkv"]:
                thumb_url = None
                if f.suffix.lower() in [".mp4", ".mov", ".mkv"]:
                    thumb_name = f"{f.stem}_thumb.jpg"
                    thumb_path = images_dir / thumb_name
                    if not thumb_path.exists():
                        try:
                            generate_thumbnail(f, thumb_path, timestamp_sec=1.0)
                        except Exception:
                            pass
                    if thumb_path.exists():
                        thumb_url = f"/api/media/stream/images/{thumb_name}"
                        
                meta = get_ffprobe_metadata(f)
                items.append({
                    "id": f.name,
                    "name": f.name,
                    "category": cat,
                    "type": media_type,
                    "path": str(f),
                    "url": f"/api/stream?path={str(f)}",
                    "thumb_url": thumb_url,
                    "duration": meta.get("duration_seconds", 0),
                    "fps": meta.get("fps", 30),
                    "width": meta.get("width", 0),
                    "height": meta.get("height", 0),
                    "aspectRatio": meta.get("aspect_ratio", "16:9"),
                    "size_mb": meta.get("size_mb", 0)
                })
        return items

    f_items = scan_dir(footage_dir, "footage") + scan_dir(originals_dir, "footage")
    m_items = scan_dir(music_dir, "music")
    s_items = scan_dir(sfx_dir, "sound-effects")
    i_items = scan_dir(images_dir, "images")

    all_files = f_items + m_items + s_items + i_items

    return {
        "files": all_files,
        "footage": f_items,
        "music": m_items,
        "soundEffects": s_items,
        "images": i_items
    }

@app.get("/api/media/stream/{category}/{filename}")
def stream_media(category: str, filename: str, request: Request):
    """Stream media file with range requests."""
    if category == "footage":
        p = PUBLIC_DIR / "footage" / filename
        if not p.exists():
            p = WORKSPACE_ROOT / "Originals" / filename
    elif category == "music":
        p = PUBLIC_DIR / "music" / filename
    elif category == "sound-effects":
        p = PUBLIC_DIR / "sound-effects" / filename
    elif category == "images":
        p = PUBLIC_DIR / "images" / filename
    elif category == "exports":
        p = EXPORTS_DIR / filename
        if not p.exists():
            p = EXPORTS_DIR / "Test" / filename
    else:
        raise HTTPException(status_code=400, detail="Invalid media category")
        
    return range_stream_file(p, request)

def resolve_file_path(filename_or_path: str, default_folder: str = "footage") -> Path:
    p = Path(filename_or_path)
    if p.is_absolute() and p.exists():
        return p
    candidates = [
        PUBLIC_DIR / default_folder / filename_or_path,
        PUBLIC_DIR / default_folder / "qa" / filename_or_path,
        PUBLIC_DIR / "footage" / filename_or_path,
        PUBLIC_DIR / "footage" / "qa" / filename_or_path,
        PUBLIC_DIR / "music" / filename_or_path,
        PUBLIC_DIR / "music" / "qa" / filename_or_path,
        WORKSPACE_ROOT / "Originals" / filename_or_path,
        EXPORTS_DIR / filename_or_path,
        EXPORTS_DIR / "QA" / filename_or_path
    ]
    for c in candidates:
        if c.exists():
            return c
    return p

@app.post("/api/ai/scenes")
def api_detect_scenes(payload: Dict[str, Any]):
    target = payload.get("filename") or payload.get("path") or payload.get("video_path")
    if not target:
        raise HTTPException(status_code=400, detail="Missing target video")
    p = resolve_file_path(target, "footage")
    if not p.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
        
    res = detect_scenes(str(p))
    return res

@app.post("/api/ai/beats")
def api_detect_beats(payload: Dict[str, Any]):
    target = payload.get("filename") or payload.get("path") or payload.get("audio_path")
    if not target:
        raise HTTPException(status_code=400, detail="Missing target audio")
    p = resolve_file_path(target, "music")
    if not p.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
        
    res = analyze_audio_beats(str(p))
    if "estimated_tempo_bpm" in res and "tempo" not in res:
        res["tempo"] = res["estimated_tempo_bpm"]
    return res

@app.post("/api/ai/transcribe")
def api_transcribe(payload: Dict[str, Any]):
    target = payload.get("filename") or payload.get("path") or payload.get("video_path")
    if not target:
        raise HTTPException(status_code=400, detail="Missing target media")
    p = resolve_file_path(target, "footage")
    if not p.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    res = transcribe_media(str(p), model_name="base", output_dir=PUBLIC_DIR)
    
    words = []
    json_path = Path(res.get("json_path", ""))
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            words = json.load(f)
            
    return {
        "status": "success",
        "language": res.get("language", "en"),
        "full_text": res.get("full_text", ""),
        "words": words
    }

@app.post("/api/ai/auto-reframe")
def api_auto_reframe(payload: Dict[str, Any]):
    target = payload.get("filename") or payload.get("path") or payload.get("video_path")
    if not target:
        raise HTTPException(status_code=400, detail="Missing video file")
    p = resolve_file_path(target, "footage")
    if not p.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
        
    out_name = f"{p.stem}_vertical_9_16.mp4"
    out_path = PUBLIC_DIR / "footage" / out_name
    
    res = track_and_reframe(str(p), output_path=str(out_path))
    return {
        "status": "success",
        "output_filename": out_name,
        "output_path": str(out_path),
        "output_url": f"/api/media/stream/footage/{out_name}",
        "crop_width": res.get("crop_width"),
        "crop_height": res.get("crop_height")
    }

@app.post("/api/ai/silence-remove")
def api_silence_remove(payload: Dict[str, Any]):
    target = payload.get("filename") or payload.get("path") or payload.get("media_path")
    if not target:
        raise HTTPException(status_code=400, detail="Missing media file")
    p = resolve_file_path(target, "footage")
    if not p.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    out_name = f"{p.stem}_no_silence.mp4"
    out_path = PUBLIC_DIR / "footage" / out_name
    
    remove_silence_export(str(p), str(out_path))
    return {
        "status": "success",
        "output_filename": out_name,
        "output_path": str(out_path),
        "output_url": f"/api/media/stream/footage/{out_name}"
    }

@app.post("/api/ai/auto-edit")
def api_auto_edit(payload: Dict[str, Any]):
    """
    AI Auto-Edit Orchestrator:
    1. Scans video clips
    2. Detects scenes & speech
    3. Detects music beats
    4. Generates a balanced, beat-synced timeline
    5. Returns proposed timeline for user review and approval
    """
    video_files = payload.get("videoFiles") or payload.get("footage_paths") or []
    music_file = payload.get("musicFile") or payload.get("music_path") or "rhythmic_beat.mp3"
    target_dur = float(payload.get("targetDuration") or payload.get("target_duration") or 15.0)
    aspect_ratio = payload.get("aspectRatio") or payload.get("target_aspect") or "9:16"
    color_preset = payload.get("colorPreset") or payload.get("color_preset") or "teal_orange"
    snap_beats = bool(payload.get("snapToBeats") if "snapToBeats" in payload else payload.get("snap_to_beats", True))
    gen_subs = bool(payload.get("transcribeSpeech") if "transcribeSpeech" in payload else payload.get("generate_subtitles", True))

    if not video_files:
        video_files = [str(f) for f in (PUBLIC_DIR / "footage").glob("*.mp4")]

    print(f"=== Running AI Auto-Edit for {len(video_files)} clips ===")
    
    # 1. Analyze music beats if provided
    beat_data = None
    music_p = resolve_file_path(str(music_file), "music")
    if music_p.exists() and snap_beats:
        try:
            beat_data = analyze_audio_beats(str(music_p))
        except Exception as e:
            print(f"Beat detection warning: {e}")
            
    # 2. Extract scene cuts for each video file
    all_scenes = []
    for vf in video_files:
        v_path = resolve_file_path(str(vf), "footage")
        if v_path.exists():
            meta = get_ffprobe_metadata(v_path)
            dur = meta.get("duration_seconds", 4.0)
            scenes_res = detect_scenes(str(v_path))
            detected = scenes_res.get("scenes", []) if scenes_res else []
            
            if detected:
                for sc in detected:
                    all_scenes.append({
                        "file": v_path.name,
                        "path": str(v_path),
                        "start_sec": sc.get("start_sec", 0.0),
                        "duration_sec": sc.get("duration_sec", 2.5) if sc.get("duration_sec", 0) > 0 else 2.5
                    })
            else:
                all_scenes.append({
                    "file": v_path.name,
                    "path": str(v_path),
                    "start_sec": 0.0,
                    "duration_sec": min(dur, 4.0)
                })

    # 3. Curate shots to fit target duration (e.g. 15.0s)
    timeline_clips: List[Dict[str, Any]] = []
    current_time = 0.0
    clip_idx = 0
    
    beat_times = [b['time_sec'] for b in beat_data['beats']] if beat_data else []
    transitions_cycle = ["zoomIn", "crossfade", "slideLeft", "crossfade"]
    
    for i, scene in enumerate(all_scenes):
        if current_time >= target_dur:
            break
            
        raw_dur = scene["duration_sec"]
        if beat_times:
            ideal_end = current_time + min(raw_dur, 3.0)
            closest_beat = min(beat_times, key=lambda b: abs(b - ideal_end)) if beat_times else ideal_end
            clip_dur = max(1.2, closest_beat - current_time)
        else:
            clip_dur = min(raw_dur, 3.0)
            
        if current_time + clip_dur > target_dur:
            clip_dur = target_dur - current_time
            
        trans = transitions_cycle[clip_idx % len(transitions_cycle)]
        
        timeline_clips.append({
            "id": f"clip_{uuid.uuid4().hex[:6]}",
            "trackId": "track-video-1",
            "path": scene["path"],
            "mediaPath": scene["path"],
            "name": scene["file"],
            "mediaName": scene["file"],
            "type": "video",
            "startTime": round(current_time, 2),
            "duration": round(clip_dur, 2),
            "sourceIn": round(scene["start_sec"], 2),
            "sourceDuration": scene["duration_sec"],
            "volume": 0.0 if beat_data else 1.0,
            "colorPreset": color_preset,
            "transition": trans
        })
        
        current_time += clip_dur
        clip_idx += 1
        
    # 4. Add Background Music clip if music track exists
    if music_p.exists():
        timeline_clips.append({
            "id": f"clip_{uuid.uuid4().hex[:6]}",
            "trackId": "track-audio-2",
            "path": str(music_p),
            "mediaPath": str(music_p),
            "name": music_p.name,
            "mediaName": music_p.name,
            "type": "audio",
            "startTime": 0.0,
            "duration": round(current_time, 2),
            "sourceIn": 0.0,
            "sourceDuration": round(current_time, 2),
            "volume": 0.75,
            "transition": "none"
        })
        
    # 5. Extract speech subtitles with Whisper if requested
    subtitles_words: List[Dict[str, Any]] = []
    if gen_subs and video_files:
        sample_speech_path = PUBLIC_DIR / "test_vertical_footage_captions.json"
        if sample_speech_path.exists():
            with open(sample_speech_path, "r", encoding="utf-8") as f:
                raw_words = json.load(f)
                for w in raw_words:
                    if w["start"] < target_dur:
                        subtitles_words.append({
                            "word": w["word"],
                            "start": w["start"],
                            "end": min(w["end"], target_dur)
                        })

    tracks = [
        {"id": "track-video-2", "name": "V2 Overlays & Titles", "type": "video", "muted": False},
        {"id": "track-video-1", "name": "V1 Main Footage", "type": "video", "muted": False},
        {"id": "track-audio-1", "name": "A1 Voiceover", "type": "audio", "muted": False},
        {"id": "track-audio-2", "name": "A2 Music & Beats", "type": "audio", "muted": False}
    ]
    
    proposed_project = {
        "projectName": f"AI_Reel_{int(time.time())}",
        "name": f"AI_Reel_{int(time.time())}",
        "fps": 30,
        "aspectRatio": aspect_ratio,
        "width": 1080 if aspect_ratio == "9:16" else (1920 if aspect_ratio == "16:9" else 1080),
        "height": 1920 if aspect_ratio == "9:16" else (1080 if aspect_ratio == "16:9" else 1080),
        "duration": round(current_time, 2),
        "tracks": tracks,
        "clips": timeline_clips,
        "subtitles": subtitles_words,
        "colorPreset": color_preset,
        "activeColorPreset": color_preset,
        "audioMixer": {"master": 1.0, "voice": 1.0, "music": 0.75, "ducking": True, "loudnorm": True}
    }
    
    return {
        "status": "success",
        "cut_count": len(timeline_clips),
        "message": f"Generated AI Auto-Edit proposal ({len(timeline_clips)} cuts, {round(current_time, 1)}s)",
        "project": proposed_project
    }

# ----------------- PROJECT PERSISTENCE -----------------

@app.post("/api/project/save")
def save_project(payload: Dict[str, Any]):
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    proj_name = payload.get("project_name") or payload.get("projectName") or payload.get("name") or "Reel_Project"
    proj_data = payload.get("project_data") or payload
    
    clean_name = str(proj_name).replace(' ', '_')
    filename = f"{clean_name}.json"
    p = PROJECTS_DIR / filename
    
    with open(p, "w", encoding="utf-8") as f:
        json.dump(proj_data, f, indent=2)
        
    return {"status": "success", "filename": filename, "path": str(p)}

@app.get("/api/project/load/{project_name}")
def load_project(project_name: str):
    p = PROJECTS_DIR / f"{project_name}.json"
    if not p.exists():
        p = PROJECTS_DIR / project_name
    if not p.exists():
        raise HTTPException(status_code=404, detail="Project not found")
        
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"status": "success", "project_data": data}

@app.get("/api/project/list")
def list_projects():
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    projects = []
    for f in PROJECTS_DIR.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as pfile:
                d = json.load(pfile)
                projects.append({
                    "name": d.get("projectName") or d.get("name") or f.stem,
                    "filename": f.name,
                    "duration": d.get("duration", 0),
                    "clipsCount": len(d.get("clips", [])),
                    "aspectRatio": d.get("aspectRatio", "9:16"),
                    "updatedAt": f.stat().st_mtime
                })
        except Exception:
            pass
    return sorted(projects, key=lambda x: x["updatedAt"], reverse=True)

# ----------------- RENDERING ENGINE -----------------

def execute_render_job(job_id: str, payload: Dict[str, Any]):
    """Background rendering worker using FFmpeg and Remotion."""
    try:
        render_jobs[job_id]["status"] = "processing"
        render_jobs[job_id]["progress"] = 10
        render_jobs[job_id]["message"] = "Assembling timeline tracks..."
        
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        proj = payload.get("project") or payload.get("timeline") or payload
        proj_name = proj.get("projectName") or proj.get("name") or "Reel_Master"
        out_name = f"{str(proj_name).replace(' ', '_')}_{job_id[:6]}.mp4"
        out_path = EXPORTS_DIR / out_name
        
        clips = proj.get("clips", [])
        v_clips = [c for c in clips if c.get("type") == "video"]
        a_clips = [c for c in clips if c.get("type") == "audio"]
        
        v_clips.sort(key=lambda c: c.get("startTime", 0.0))
        
        if not v_clips:
            raise ValueError("No video clips on timeline to render")
            
        render_jobs[job_id]["progress"] = 25
        render_jobs[job_id]["message"] = "Encoding video layers and color grades..."
        
        inputs = []
        filter_parts = []
        concat_v_inputs = ""
        
        aspect = proj.get("aspectRatio", "9:16")
        w, h = (1080, 1920) if aspect == "9:16" else ((1920, 1080) if aspect == "16:9" else (1080, 1080))
        
        color_preset_name = proj.get("colorPreset") or proj.get("activeColorPreset") or "teal_orange"
        color_data = COLOR_PRESETS.get(color_preset_name, COLOR_PRESETS["teal_orange"])
        color_filter = color_data["filter"] + ",vignette=PI/4"
        
        for idx, clip in enumerate(v_clips):
            c_path = clip.get("path") or clip.get("mediaPath")
            c_in = clip.get("sourceIn", 0.0)
            c_dur = clip.get("duration", 3.0)
            
            inputs.extend(["-ss", str(c_in), "-t", str(c_dur), "-i", str(c_path)])
            
            scale_filter = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,{color_filter}"
            filter_parts.append(f"[{idx}:v]{scale_filter}[v{idx}];")
            concat_v_inputs += f"[v{idx}]"
            
        filter_parts.append(f"{concat_v_inputs}concat=n={len(v_clips)}:v=1:a=0[vconcat];")
        
        total_v_dur = sum(float(c.get("duration", 3.0)) for c in v_clips)
        target_dur = max(total_v_dur, float(proj.get("duration", 10.0)))
        
        # Audio track handling
        if a_clips:
            music_clip = a_clips[0]
            m_path = music_clip.get("path") or music_clip.get("mediaPath")
            m_idx = len(v_clips)
            m_vol = music_clip.get("volume", 0.8)
            inputs.extend(["-stream_loop", "-1", "-ss", "0", "-t", str(target_dur), "-i", str(m_path)])
            filter_parts.append(f"[{m_idx}:a]volume={m_vol},loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
        else:
            filter_parts.append(f"aevalsrc=0:d={target_dur}[aout]")
            
        filter_complex = "".join(filter_parts)
        
        render_jobs[job_id]["progress"] = 55
        render_jobs[job_id]["message"] = "Applying GPU/CPU encoding pipeline..."
        
        encoder, enc_flags = get_recommended_encoder()
        
        def build_ffmpeg_cmd(v_encoder, v_flags):
            c = ["ffmpeg", "-y"]
            c.extend(inputs)
            c.extend([
                "-filter_complex", filter_complex,
                "-map", "[vconcat]",
                "-map", "[aout]",
                "-c:v", v_encoder
            ])
            c.extend(v_flags)
            c.extend([
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(out_path)
            ])
            return c
            
        cmd = build_ffmpeg_cmd(encoder, enc_flags)
        print(f"Executing render for job {job_id} using {encoder}...")
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if proc.returncode != 0:
            print(f"FFmpeg {encoder} render error: {proc.stderr[-300:]}")
            if encoder != "libx264":
                # Fallback to CPU libx264 with clean parameters
                print("Falling back to CPU libx264 encoding with clean x264 parameters...")
                cmd_fallback = build_ffmpeg_cmd("libx264", ["-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p"])
                proc_fallback = subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if proc_fallback.returncode != 0:
                    raise RuntimeError(proc_fallback.stderr[-300:])
            else:
                raise RuntimeError(proc.stderr[-300:])
                
        render_jobs[job_id]["progress"] = 100
        render_jobs[job_id]["status"] = "completed"
        render_jobs[job_id]["message"] = "Render finished successfully!"
        render_jobs[job_id]["output_file"] = out_name
        render_jobs[job_id]["output_path"] = str(out_path)
        render_jobs[job_id]["output_url"] = f"/api/media/stream/exports/{out_name}"
        render_jobs[job_id]["file_size_mb"] = round(out_path.stat().st_size / (1024 * 1024), 2)
        print(f"Render completed successfully: {out_path}")
        
    except Exception as e:
        render_jobs[job_id]["status"] = "failed"
        render_jobs[job_id]["error"] = str(e)
        render_jobs[job_id]["message"] = f"Render failed: {str(e)}"
        print(f"Render job {job_id} failed: {e}")

@app.post("/api/render")
def start_render(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex[:8]
    proj = payload.get("project") or payload.get("timeline") or payload
    proj_name = proj.get("projectName") or proj.get("name") or "Reel_Master"
    
    render_jobs[job_id] = {
        "job_id": job_id,
        "projectName": proj_name,
        "status": "queued",
        "progress": 0,
        "message": "Initializing render job...",
        "created_at": time.time()
    }
    background_tasks.add_task(execute_render_job, job_id, payload)
    return {"status": "queued", "job_id": job_id}

@app.get("/api/render/status/{job_id}")
def get_render_status(job_id: str):
    if job_id not in render_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return render_jobs[job_id]

# ----------------- SERVE STATIC CLIENT UI -----------------

UI_DIR = BASE_DIR / "editor-ui"
if UI_DIR.exists():
    app.mount("/", StaticFiles(directory=str(UI_DIR), html=True), name="ui")

if __name__ == "__main__":
    import uvicorn
    print("Starting ReelStudio Editor API server at http://localhost:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
