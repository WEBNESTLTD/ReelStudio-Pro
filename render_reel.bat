@echo off
REM ReelStudio - Render Reel Composition
echo ========================================================
echo           REELSTUDIO RENDER ENGINE (1080x1920)
echo ========================================================
cd video-editor
npx remotion render src/index.ts ReelComposition ../Exports/Reel_Output.mp4 --concurrency=4
echo.
echo Render output saved to: Exports/Reel_Output.mp4
pause
