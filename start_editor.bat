@echo off
title ReelStudio Pro — Video Editor Workstation
echo =====================================================================
echo               REELSTUDIO PRO — AI VIDEO EDITOR
echo            Instagram Reels & Cinematic Video Workstation
echo =====================================================================
echo.

cd /d "%~dp0video-editor"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found in video-editor\.venv!
    echo Please ensure Phase 1 & 2 dependencies are installed.
    pause
    exit /b 1
)

echo [*] Starting ReelStudio local server on http://127.0.0.1:8000 ...
echo [*] Press Ctrl+C in this terminal window to stop the server.
echo.

:: Launch default browser after 1.5 seconds
start "" powershell -Command "Start-Sleep -Milliseconds 1500; Start-Process 'http://127.0.0.1:8000'"

:: Start FastAPI backend with Uvicorn
.venv\Scripts\python.exe -m uvicorn server:app --host 127.0.0.1 --port 8000

pause
