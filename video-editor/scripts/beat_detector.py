"""
ReelStudio Music Beat Detector & Beat-Synced Cuts
Analyzes audio tracks using Librosa to detect BPM, musical downbeats, and energy onsets.
Generates frame-accurate cut timestamps for Remotion video timelines.
"""

import os
import sys
import json
from pathlib import Path
import soundfile as sf
import numpy as np
import librosa

def analyze_audio_beats(audio_path, target_fps=30):
    """
    Extract tempo (BPM), beat timestamps, and onset frame markers from an audio track.
    Returns structured data for Remotion timeline synchronization.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    print(f"Loading audio track: {audio_path.name}...")
    y, sr = sf.read(str(audio_path))
    
    # If stereo, convert to mono for analysis
    if len(y.shape) > 1:
        y = np.mean(y, axis=1)
        
    # Estimate tempo and beat frame positions
    print("Computing musical tempo and rhythmic beat positions...")
    tempo_raw, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    
    tempo = float(tempo_raw.item() if hasattr(tempo_raw, 'item') else tempo_raw)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # Compute onset strength to detect major peaks/drops
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    
    # Map to target video frames
    beat_markers = []
    for i, t in enumerate(beat_times):
        frame_idx = int(round(t * target_fps))
        is_downbeat = (i % 4 == 0) # 4/4 time signature downbeat
        beat_markers.append({
            'beat_index': i + 1,
            'time_sec': round(float(t), 3),
            'frame': frame_idx,
            'is_downbeat': is_downbeat
        })
        
    duration = len(y) / sr
    
    result = {
        'audio_file': audio_path.name,
        'duration_sec': round(duration, 2),
        'estimated_tempo_bpm': round(tempo, 1),
        'total_beats': len(beat_markers),
        'downbeats_count': sum(1 for b in beat_markers if b['is_downbeat']),
        'fps': target_fps,
        'beats': beat_markers
    }
    
    output_json = audio_path.parent / f"{audio_path.stem}_beats.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(f"Saved beat markers to: {output_json}")
    
    return result

def generate_beat_synced_cut_plan(beat_data, available_clips, cuts_per_bar=2):
    """
    Generate an EDL/JSON plan mapping raw clips to musical beats.
    cuts_per_bar: 1 (cut on every bar/downbeat), 2 (cut every 2 beats), 4 (rapid fast cuts)
    """
    beats = beat_data['beats']
    selected_beats = [b for i, b in enumerate(beats) if i % (4 // cuts_per_bar) == 0]
    
    timeline = []
    for i in range(len(selected_beats)):
        start_frame = selected_beats[i]['frame']
        if i + 1 < len(selected_beats):
            end_frame = selected_beats[i + 1]['frame']
        else:
            end_frame = int(round(beat_data['duration_sec'] * beat_data['fps']))
            
        dur_frames = end_frame - start_frame
        clip_assigned = available_clips[i % len(available_clips)] if available_clips else "placeholder.mp4"
        
        timeline.append({
            'cut_index': i + 1,
            'clip': clip_assigned,
            'timeline_start_frame': start_frame,
            'duration_frames': dur_frames,
            'transition': 'zoomIn' if selected_beats[i]['is_downbeat'] else 'crossfade'
        })
        
    return timeline

if __name__ == '__main__':
    if len(sys.argv) > 1:
        res = analyze_audio_beats(sys.argv[1])
        print(f"Tempo: {res['estimated_tempo_bpm']} BPM | Total Beats: {res['total_beats']}")
    else:
        sample_audio = Path(__file__).resolve().parent.parent / 'public' / 'music' / 'rhythmic_beat.mp3'
        if sample_audio.exists():
            res = analyze_audio_beats(sample_audio)
            print(f"Tempo: {res['estimated_tempo_bpm']} BPM | Total Beats: {res['total_beats']}")
        else:
            print("Usage: python beat_detector.py <audio_file>")
