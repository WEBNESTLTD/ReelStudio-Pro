# ReelStudio Pro 🎬

**Professional Local-First AI Video Editor & Instagram Reels Workstation**  
*Configured, optimized, and verified for Windows 11 with NVIDIA GPU acceleration & CPU fallback.*

---

## 🌟 Overview

ReelStudio Pro is a complete local-first non-linear video editing (NLE) environment built for high-retention Instagram Reels, YouTube Shorts, and cinematic landscape videos. It integrates a responsive dark NLE interface with local AI engines (Whisper, Librosa, YOLO11, PySceneDetect, Auto-Editor) and dual rendering pipelines (FFmpeg and Remotion React compositions).

### Key Highlights
- **1-Click Launch**: Double-click `start_editor.bat` to launch the server and open the NLE editor in your browser.
- **11 Core Panels**: Media Library, Preview Monitor, Multi-track Timeline, Video Tracks (`V1`, `V2`), Audio Tracks (`A1`, `A2`), Effects, Transitions, Subtitle Editor, Color Grading, Audio Mixer, and Export Manager.
- **1-Click AI Auto-Edit**: Automatically scans scenes, aligns cuts to musical beats, transcribes speech with Whisper, applies cinematic color presets, and generates an inspectable timeline proposal requiring user approval before render.
- **Local & Private**: No cloud subscriptions, no telemetry, no API keys needed for local Whisper transcription and ML models.
- **Non-Destructive**: Original footage in `Originals/` is never modified or deleted.

---

## 🚀 Quick Start (1-Click Launch)

Simply double-click the launcher script in the workspace root:

```cmd
start_editor.bat
```

Or run via command line:
```powershell
cd E:\reelstudio
.\start_editor.bat
```

This will automatically start the FastAPI backend server on `http://127.0.0.1:8000` and open the ReelStudio Pro NLE interface in your default browser.

---

## 📋 System Prerequisites

| Component | Minimum Requirement | Recommended (Tested Environment) |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 (64-bit) | **Windows 11 Home (Build 26100)** |
| **Python** | Python 3.10+ (64-bit) | **Python 3.13.x** |
| **Node.js & npm** | Node.js 18.x LTS / npm 9.x | **Node.js v24.19.0 / npm 12.0.2** |
| **FFmpeg** | FFmpeg 5.x+ (in system PATH) | **FFmpeg 9.0.1 Essentials/Full (gyan.dev)** |
| **GPU / Acceleration** | Any x86-64 multi-core CPU | **NVIDIA RTX 3050 6GB Laptop GPU (Driver 616.56, CUDA 13.4)** |
| **RAM** | 8 GB System RAM | **16 GB RAM** |
| **Storage** | 5 GB free disk space | **NVMe SSD Storage** |

---

## 📦 Step-by-Step Installation & Setup

If setting up on a fresh machine or clone:

### 1. Clone Repository
```powershell
git clone https://github.com/WEBNESTLTD/ReelStudio-Pro.git
cd ReelStudio-Pro
```

### 2. Configure Python Virtual Environment
```powershell
cd video-editor
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

> **NVIDIA GPU Acceleration Note**: For optimal PyTorch GPU support with CUDA:
> ```powershell
> pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
> ```

### 3. Install Node.js & Remotion Dependencies
```powershell
npm install
```

### 4. Verify Local Installation
Verify all 10 core capabilities with the automated environment checker:
```powershell
cd ..
video-editor\.venv\Scripts\python.exe verify_installation.py
```

---

## 🖥️ Workstation Interface & Features

### 1. Media Library
- Browse footage, music, sound effects, and images with automatic thumbnail generation.
- Filter by media type (`All`, `Footage`, `Music`, `SFX`).
- Drag-and-drop clips directly onto timeline lanes.
- Quick tools: 1-click **Auto Reframe 9:16** and **Cut Silence**.

### 2. Preview Monitor & Instagram Safe Zones
- Hardware-accelerated HTML5 video/audio playback with HTTP 206 range requests for instant scrubbing.
- Switch aspect ratios on the fly: **9:16 Reel (1080x1920)**, **16:9 Cinema (1920x1080)**, or **1:1 Square (1080x1080)**.
- Overlay toggle for official Instagram Reels Safe Zones (header safe area, right interaction rail, bottom caption safe area).
- Real-time overlay preview for animated titles and word-level captions.

### 3. Multi-Track Timeline
- Multi-track hierarchy:
  - `V2`: Overlays, Titles & Lower Thirds (with visibility/mute toggle)
  - `V1`: Main Video Footage (with visibility/mute toggle)
  - `A1`: Voiceover & Speech Dialogue (with mute toggle)
  - `A2`: Background Music & Beats (with mute toggle)
- Dynamic zooming (10 to 120 pixels per second) with ruler timecode markings.
- Non-destructive clip editing:
  - Drag to rearrange along the timeline.
  - Left & right trim handles to adjust start, in-points, and durations.
  - `✂ Split` tool (`S` key) to split clips at the playhead.
  - `🗑 Delete` tool (`Delete`/`Backspace` key) to remove selected clips.
  - `🎵 Snap Beats` tool to snap video cut boundaries to Librosa-detected musical beats.

### 4. AI Auto-Edit Wizard
- Launch the wizard with the **AI Auto-Edit** button.
- Select target duration (15s, 30s, 60s), background music track, and cinematic color look.
- 4-step automated analysis:
  1. Detects scenes and cuts (PySceneDetect).
  2. Analyzes musical tempo (BPM) and beat onsets (Librosa).
  3. Curates high-retention video shots matching the rhythm.
  4. Transcribes speech and generates word-level subtitle timings (Whisper).
- Inspect the proposal and click **"Approve & Apply to Timeline"** to load the cut list into the timeline for manual fine-tuning.

### 5. Color Grading & Effects
- 5 cinematic color presets: *Teal & Orange (Blockbuster)*, *Moody Noir Monochrome*, *Warm Film (Golden Hour)*, *Vibrant Social Pop*, and *Vintage 1970s Gold*.
- Real-time sliders for Contrast, Saturation, and Brightness.
- Cinematic effects: Ken Burns dynamic push-in, vignette, 180° motion blur emulation, and story progress bar.
- Transitions: Cut, Cross Dissolve, Zoom In Punch, Slide Left, and Digital Glitch.

### 6. Subtitle Editor & Live Captions
- Automatic transcription via local OpenAI Whisper (`base.pt` offline model).
- Interactive word-level caption list: click any word timestamp to seek playhead directly to that moment.
- Live active word highlight color picker (defaults to high-visibility yellow `#FFE600`).
- Add, edit, or delete caption words directly in the editor.

### 7. Audio Mixer & Normalization
- Independent faders for Master Volume, Voiceover (A1), and Background Music (A2).
- Automatic speech ducking (ducks background music by 65% during dialogue).
- Broadcast-standard EBU R128 loudness normalization (-16 LUFS target).

### 8. Export Manager
- Presets: Instagram Reel (1080x1920 30 FPS / 60 FPS), Cinema (1920x1080), Square (1080x1080).
- Configurable quality/CRF (CRF 18 Master, CRF 21 Balanced, CRF 26 Small).
- Asynchronous background rendering with live progress tracking bar and instant download link.

---

## 📁 Project Architecture

```
ReelStudio/
│
├── .agents/
│   └── skills/                 # 10 Installed Antigravity AI video skills
│       ├── remotion-best-practices
│       ├── remotion-create
│       ├── remotion-markup
│       ├── remotion-captions
│       ├── remotion-render
│       ├── remotion-studio
│       ├── open-montage
│       ├── agent-video-editor
│       ├── claude-motion-design
│       └── cut-as-code
│
├── video-editor/               # Core application and engines
│   ├── editor-ui/              # Dark NLE Frontend UI
│   │   ├── index.html          # Single-page NLE interface (11 panels)
│   │   ├── styles.css          # Modern dark NLE theme
│   │   └── app.js              # State manager, timeline sync & API client
│   │
│   ├── server.py               # FastAPI backend (streaming, AI APIs, rendering)
│   │
│   ├── public/
│   │   ├── footage/            # Real video clips (MP4/MOV)
│   │   ├── music/              # Music tracks & beat marker JSON
│   │   ├── sound-effects/      # SFX assets
│   │   └── images/             # Video thumbnails & overlays
│   │
│   ├── src/                    # Remotion React 19 compositions
│   │   ├── compositions/       # ReelComposition, TestComposition
│   │   ├── components/         # MotionGraphics (LowerThird, StoryProgressBar)
│   │   ├── captions/           # CaptionRenderer (animated spring text)
│   │   ├── transitions/        # Crossfade, Zoom, Slide transitions
│   │   └── effects/            # ColorGrading, ThreeDEffects, Vignette
│   │
│   ├── scripts/                # Python ML engines & automation tools
│   │   ├── beat_detector.py    # Librosa tempo & beat-synchronized cuts
│   │   ├── auto_reframe.py     # YOLO & OpenCV 16:9 to 9:16 virtual camera reframer
│   │   ├── silence_remover.py  # Automatic silence removal (FFmpeg + Auto-Editor)
│   │   ├── audio_cleaner.py    # Adaptive FFT denoising & EBU R128 normalization
│   │   ├── color_corrector.py  # Cinematic color grades (Teal & Orange, Moody, Warm)
│   │   ├── whisper_transcriber.py # Local speech transcription (word timestamps)
│   │   ├── test_editor_app.py  # Full Phase 3 end-to-end verification suite
│   │   └── render_pipeline.py  # GPU NVENC & CPU libx264 multi-format renderer
│   │
│   ├── models/                 # Pre-cached lightweight models (yolo11n.pt)
│   └── package.json            # Node.js dependencies (Remotion 4.0.544)
│
├── Originals/                  # Safe storage for original unedited footage
├── Projects/                   # Project configurations and saved timelines (.json)
├── Exports/                    # Master exports and Demonstration Reel
│   ├── Demonstration_Reel.mp4  # Verified 1080x1920 9:16 Instagram Reel master
│   ├── Demonstration_Reel_30s_NVENC.mp4 # Verified 30s 1080x1920 NVENC master (Phase 3.2)
│   └── reel.mp4                # Verified Remotion programmatic render
├── Reports/                    # Verification reports
│   ├── installation-report.md  # Phase 1 & 2 capability verification report
│   ├── phase3-feature-verification.md # Phase 3 complete NLE verification report
│   └── phase3_2_gpu_validation.md # Phase 3.2 GPU activation and benchmark report
├── start_editor.bat            # 1-Click launcher for ReelStudio Pro
└── README.md
```

---

## ⚡ Hardware Acceleration & Encoder Tiers

ReelStudio Pro features an automated 4-tier intelligent encoder priority ladder:
1. **Tier 1 — NVIDIA NVENC (`h264_nvenc`)**: Dedicated hardware ASIC encoding on NVIDIA RTX 3050 (up to 234+ FPS on 1080p).
2. **Tier 2 — Intel QuickSync (`h264_qsv`)**: Dedicated Intel hardware encoding (active when iGPU is available).
3. **Tier 3 — Windows Media Foundation (`h264_mf`)**: Optimized Windows MFT pipeline.
4. **Tier 4 — CPU Multi-Threaded (`libx264`)**: High-fidelity AVX2 multi-threaded CPU fallback.

---

## 🧪 Verification & Test Suites

To execute the Phase 3.2 GPU activation and full workflow regression suite:

```powershell
video-editor\.venv\Scripts\python.exe video-editor\scripts\test_phase3_2_gpu_suite.py
```

To execute the automated end-to-end NLE verification suite:

```powershell
video-editor\.venv\Scripts\python.exe video-editor\scripts\test_editor_app.py
```

To run Remotion Studio independently:
```powershell
cd video-editor
npm start
```

To render via the Remotion CLI:
```powershell
cd video-editor
npm run build
```

---

## ⚖️ Third-Party Dependencies & Licensing Notice

ReelStudio Pro integrates open-source libraries and frameworks. Review the following licenses for compliance with your deployment model:

| Component | Upstream Project | License | Commercial Considerations |
| :--- | :--- | :--- | :--- |
| **YOLO Subject Tracking** | [Ultralytics YOLO11](https://github.com/ultralytics/ultralytics) | **AGPL-3.0** / Commercial | AGPL-3.0 copyleft applies if distributed or offered as a network service. For proprietary SaaS/closed commercial distribution, an [Ultralytics Enterprise License](https://ultralytics.com/license) is required. |
| **Local Speech Transcription**| [OpenAI Whisper](https://github.com/openai/whisper) | **MIT** | Permissive; commercial use permitted. |
| **Computer Vision** | [OpenCV](https://github.com/opencv/opencv) | **Apache 2.0** | Permissive; commercial use permitted. |
| **Scene Detection** | [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | **BSD 3-Clause** | Permissive; commercial use permitted. |
| **Audio Beat Detection** | [Librosa](https://github.com/librosa/librosa) | **ISC** | Permissive; commercial use permitted. |
| **Automated Silence Removal** | [Auto-Editor](https://github.com/WyattBlue/auto-editor) | **The Unlicense** | Public domain dedication; unrestricted use. |
| **API & Web Server** | [FastAPI](https://github.com/tiangolo/fastapi) | **MIT** | Permissive; commercial use permitted. |
| **Programmatic Video Engine** | [Remotion](https://github.com/remotion-dev/remotion) | **Remotion License** | Free for individuals and companies with ≤3 people / ≤$50k revenue; [Company License](https://www.remotion.dev/license) required for larger organizations. |
| **Media Transcoding Pipeline** | [FFmpeg](https://ffmpeg.org) | **LGPL 2.1+ / GPL 2.0+** | CLI process invocation. Does not link statically or dynamically to application code. |

---

## 🔒 Privacy & Safety Guarantee

- **Zero Cloud Leakage**: All AI models (Whisper, Librosa, YOLO, Auto-Editor) execute 100% locally on your machine. No footage, transcripts, or telemetry are transmitted to third-party APIs.
- **Non-Destructive Editing**: Source media in `Originals/` is strictly mounted read-only and will never be overwritten or deleted.
- **Excluded Deliverables**: High-capacity video exports and model binaries are excluded from Git version control via `.gitignore`.

