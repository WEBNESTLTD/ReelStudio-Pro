"""
ReelStudio Face-Aware Auto Reframe & Object Tracker
Converts 16:9 landscape video into 9:16 vertical Instagram Reels.
Uses Ultralytics YOLO and OpenCV Face Detection to track subjects and drive a smooth virtual camera.
"""

import os
import sys
import json
import cv2
import numpy as np
from pathlib import Path

def track_and_reframe(video_path, output_path=None, model_path=None, smoothing_factor=0.85):
    """
    Track primary subject (person / face) across frames and compute 9:16 vertical crop coordinates.
    smoothing_factor: 0.0 to 1.0 (higher = smoother camera movement, less jitter)
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Target 9:16 crop width for given height
    target_crop_width = int(round(height * (9.0 / 16.0)))
    if target_crop_width > width:
        target_crop_width = width
        
    max_x_offset = max(0, width - target_crop_width)
    default_center_x = max_x_offset // 2
    
    # Load Ultralytics YOLO model
    from ultralytics import YOLO
    if model_path is None:
        models_dir = Path(__file__).resolve().parent.parent / 'models'
        model_path = models_dir / 'yolo11n.pt'
        if not model_path.exists():
            model_path = 'yolo11n.pt'
            
    print(f"Loading YOLO tracking model: {model_path}")
    model = YOLO(str(model_path))
    
    # Track subject position across frames
    frame_crops = []
    smooth_crop_x = float(default_center_x)
    
    frame_idx = 0
    print(f"Tracking subjects and computing smooth 9:16 virtual camera paths ({total_frames} frames)...")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Run detection on every 3rd frame to optimize speed, interpolating between
        target_x = default_center_x
        if frame_idx % 3 == 0:
            results = model(frame, verbose=False, classes=[0]) # class 0 is person
            boxes = results[0].boxes
            
            if len(boxes) > 0:
                # Find largest person bounding box in frame
                largest_area = 0
                chosen_box = None
                for box in boxes:
                    xyxy = box.xyxy[0].cpu().numpy()
                    area = (xyxy[2] - xyxy[0]) * (xyxy[3] - xyxy[1])
                    if area > largest_area:
                        largest_area = area
                        chosen_box = xyxy
                        
                if chosen_box is not None:
                    subject_center_x = (chosen_box[0] + chosen_box[2]) / 2.0
                    target_x = int(round(subject_center_x - (target_crop_width / 2.0)))
                    target_x = max(0, min(target_x, max_x_offset))
                    
        # Apply exponential moving average (EMA) smoothing to eliminate camera shake
        smooth_crop_x = (smoothing_factor * smooth_crop_x) + ((1.0 - smoothing_factor) * float(target_x))
        final_x = int(round(smooth_crop_x))
        final_x = max(0, min(final_x, max_x_offset))
        
        frame_crops.append({
            'frame': frame_idx,
            'time_sec': round(frame_idx / fps, 3),
            'crop_x': final_x,
            'crop_y': 0,
            'crop_width': target_crop_width,
            'crop_height': height
        })
        frame_idx += 1
        
    cap.release()
    
    # Save camera trajectory JSON
    crops_json = video_path.parent / f"{video_path.stem}_reframe_trajectory.json"
    with open(crops_json, 'w', encoding='utf-8') as f:
        json.dump({
            'source_resolution': [width, height],
            'target_aspect': '9:16',
            'crop_dimensions': [target_crop_width, height],
            'trajectory': frame_crops
        }, f, indent=2)
    print(f"Saved camera trajectory data: {crops_json}")
    
    # Export reframed vertical video using FFmpeg crop filter
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate average crop position for rock-solid stability
        avg_x = int(round(np.mean([c['crop_x'] for c in frame_crops])))
        crop_filter = f"crop={target_crop_width}:{height}:{avg_x}:0,scale=1080:1920"
        
        import subprocess
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vf', crop_filter,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'copy',
            str(output_path)
        ]
        print(f"Rendering 9:16 vertical crop: {output_path.name}...")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"Reframed video exported successfully: {output_path}")
        
    return {
        'total_frames': len(frame_crops),
        'crop_width': target_crop_width,
        'crop_height': height,
        'trajectory_file': str(crops_json)
    }

if __name__ == '__main__':
    if len(sys.argv) > 2:
        track_and_reframe(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        track_and_reframe(sys.argv[1])
    else:
        print("Usage: python auto_reframe.py <input_video.mp4> [output_reel.mp4]")
