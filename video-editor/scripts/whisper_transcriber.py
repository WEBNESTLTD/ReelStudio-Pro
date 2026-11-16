"""
ReelStudio Whisper Transcriber
Transcribes video/audio locally using OpenAI Whisper.
Generates word-level timestamps JSON for Remotion animated captions and standard .srt subtitles.
No OpenAI API key required.
Supports English, Hindi, Kannada, and multilingual transcription.
"""

import os
import sys
import json
import argparse
from pathlib import Path

def format_timestamp_srt(seconds):
    """Format seconds into SRT timestamp HH:MM:SS,mmm"""
    millis = int((seconds % 1) * 1000)
    seconds = int(seconds)
    mins = seconds // 60
    hours = mins // 60
    mins = mins % 60
    secs = seconds % 60
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def transcribe_media(media_path, model_name="base", language=None, output_dir=None):
    """
    Transcribe media using local Whisper model.
    model_name: 'tiny', 'base', 'small', 'medium', 'large'
    """
    import whisper
    
    media_path = Path(media_path)
    if not media_path.exists():
        raise FileNotFoundError(f"File not found: {media_path}")
        
    if output_dir is None:
        output_dir = media_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    
    options = {}
    if language:
        options['language'] = language
        
    print(f"Transcribing '{media_path.name}'...")
    result = model.transcribe(str(media_path), word_timestamps=True, **options)
    
    detected_lang = result.get('language', 'unknown')
    print(f"Detected language: {detected_lang}")
    
    # 1. Extract word-level timestamps for Remotion
    words_data = []
    for segment in result.get('segments', []):
        for w in segment.get('words', []):
            clean_word = w.get('word', '').strip()
            if clean_word:
                words_data.append({
                    'word': clean_word,
                    'start': round(w.get('start', 0.0), 3),
                    'end': round(w.get('end', 0.0), 3)
                })
                
    json_path = output_dir / f"{media_path.stem}_captions.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(words_data, f, ensure_ascii=False, indent=2)
    print(f"Saved Remotion word captions: {json_path}")
    
    # 2. Extract standard SRT subtitle file
    srt_path = output_dir / f"{media_path.stem}.srt"
    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result.get('segments', []), 1):
            start = format_timestamp_srt(segment['start'])
            end = format_timestamp_srt(segment['end'])
            text = segment['text'].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
    print(f"Saved SRT subtitle file: {srt_path}")
    
    return {
        'language': detected_lang,
        'full_text': result.get('text', '').strip(),
        'words_count': len(words_data),
        'json_path': str(json_path),
        'srt_path': str(srt_path)
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ReelStudio Local Whisper Transcriber")
    parser.add_argument("media", help="Path to video or audio file")
    parser.add_argument("--model", default="base", help="Whisper model size (tiny, base, small, etc.)")
    parser.add_argument("--lang", default=None, help="Language code (e.g. en, hi, kn)")
    parser.add_argument("--out", default=None, help="Output directory")
    args = parser.parse_args()
    
    res = transcribe_media(args.media, args.model, args.lang, args.out)
    print(json.dumps(res, indent=2))
