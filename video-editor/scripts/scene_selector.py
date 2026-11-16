"""
ReelStudio Automated Scene Selector & Curated Assembly
Evaluates scene boundaries, motion dynamism, and clip durations.
Automatically curates the best clips to construct 15-second or 30-second Instagram Reels.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def select_best_scenes(scenes_list, target_duration_sec=15.0, min_clip_sec=1.5, max_clip_sec=4.0):
    """
    Filter and rank detected scene cuts to fit target Instagram Reel duration.
    Balances pacing and ensures no clip is either too short (<1.5s) or too slow (>4s).
    """
    valid_scenes = []
    for s in scenes_list:
        dur = s.get('duration_sec', 0)
        if dur >= min_clip_sec:
            # Score scene based on ideal reel pacing (around 2.5 seconds)
            pacing_score = 1.0 - (abs(dur - 2.5) / 10.0)
            valid_scenes.append({
                'scene_index': s['scene_index'],
                'start_sec': s['start_sec'],
                'end_sec': min(s['end_sec'], s['start_sec'] + max_clip_sec) if s['end_sec'] > 0 else s['start_sec'] + 2.5,
                'duration_sec': min(dur, max_clip_sec) if dur > 0 else 2.5,
                'pacing_score': round(pacing_score, 2)
            })
            
    # Sort by score and greedily pack into target duration
    valid_scenes.sort(key=lambda x: x['pacing_score'], reverse=True)
    
    selected = []
    accumulated_dur = 0.0
    
    for s in valid_scenes:
        if accumulated_dur + s['duration_sec'] <= target_duration_sec + 1.0:
            selected.append(s)
            accumulated_dur += s['duration_sec']
            
    # Re-order chronologically for coherent narrative flow
    selected.sort(key=lambda x: x['start_sec'])
    
    return {
        'target_duration_sec': target_duration_sec,
        'selected_scenes_count': len(selected),
        'total_curated_duration_sec': round(accumulated_dur, 2),
        'scenes': selected
    }

if __name__ == '__main__':
    sample_scenes = [
        {'scene_index': 1, 'start_sec': 0.0, 'end_sec': 3.2, 'duration_sec': 3.2},
        {'scene_index': 2, 'start_sec': 3.2, 'end_sec': 5.5, 'duration_sec': 2.3},
        {'scene_index': 3, 'start_sec': 5.5, 'end_sec': 8.0, 'duration_sec': 2.5},
        {'scene_index': 4, 'start_sec': 8.0, 'end_sec': 14.0, 'duration_sec': 6.0},
        {'scene_index': 5, 'start_sec': 14.0, 'end_sec': 17.5, 'duration_sec': 3.5}
    ]
    curated = select_best_scenes(sample_scenes, target_duration_sec=10.0)
    print("=== AUTOMATED SCENE SELECTION ===")
    print(json.dumps(curated, indent=2))
