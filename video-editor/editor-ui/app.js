/**
 * ReelStudio Pro — Main Application Logic
 * Full-featured local-first professional video editor
 */

// Global State
const state = {
  projectName: "Cinematic_Reel_01",
  aspectRatio: "9:16",
  resolution: { width: 1080, height: 1920, fps: 30 },
  currentTime: 0.0,
  duration: 15.0,
  isPlaying: false,
  zoom: 40, // pixels per second
  tracks: [
    { id: "track-video-2", type: "video", name: "Overlays & Titles", muted: false },
    { id: "track-video-1", type: "video", name: "Main Footage", muted: false },
    { id: "track-audio-1", type: "audio", name: "Voice / Speech", muted: false },
    { id: "track-audio-2", type: "audio", name: "Music & Beats", muted: false }
  ],
  clips: [],
  subtitles: [],
  selectedClipId: null,
  colorPreset: "teal_orange",
  colorAdjustments: { contrast: 1.15, saturation: 1.25, brightness: 1.00 },
  activeEffects: ["story-progress"],
  audioMixer: {
    master: 1.0,
    voice: 1.0,
    music: 0.75,
    ducking: true,
    loudnorm: true
  },
  mediaLibrary: [],
  activeCategory: "all",
  aiProposal: null
};

// DOM Elements
const el = {
  projectNameInput: document.getElementById("project-name-input"),
  saveStatus: document.getElementById("save-status"),
  btnSaveProject: document.getElementById("btn-save-project"),
  btnAiAutoEdit: document.getElementById("btn-ai-auto-edit"),
  btnExportModal: document.getElementById("btn-export-modal"),
  aspectBtns: document.querySelectorAll(".aspect-btn"),
  masterTimecode: document.getElementById("master-timecode"),
  
  // Left Panel
  tabBtns: document.querySelectorAll(".tab-btn"),
  tabPanes: document.querySelectorAll(".tab-pane"),
  mediaGrid: document.getElementById("media-grid"),
  mediaCatBtns: document.querySelectorAll(".media-cat-btn"),
  btnRefreshMedia: document.getElementById("btn-refresh-media"),
  btnReframeSelected: document.getElementById("btn-reframe-selected"),
  btnSilenceSelected: document.getElementById("btn-silence-selected"),
  
  // Color & Effects
  colorPresetCards: document.querySelectorAll(".color-preset-card"),
  sliderContrast: document.getElementById("slider-contrast"),
  sliderSaturation: document.getElementById("slider-saturation"),
  sliderBrightness: document.getElementById("slider-brightness"),
  contrastVal: document.getElementById("contrast-val"),
  saturationVal: document.getElementById("saturation-val"),
  brightnessVal: document.getElementById("brightness-val"),
  
  // Subtitles
  subtitlesList: document.getElementById("subtitles-list"),
  btnRunWhisper: document.getElementById("btn-run-whisper"),
  btnAddCaptionWord: document.getElementById("btn-add-caption-word"),
  captionColorInput: document.getElementById("caption-color-input"),
  
  // Audio Mixer
  mixerMaster: document.getElementById("mixer-master"),
  mixerVoice: document.getElementById("mixer-voice"),
  mixerMusic: document.getElementById("mixer-music"),
  mixerMasterVal: document.getElementById("mixer-master-val"),
  mixerVoiceVal: document.getElementById("mixer-voice-val"),
  mixerMusicVal: document.getElementById("mixer-music-val"),
  mixerDucking: document.getElementById("mixer-ducking"),
  mixerLoudnorm: document.getElementById("mixer-loudnorm"),
  
  // Preview
  previewFrame: document.getElementById("preview-frame"),
  mainVideoPlayer: document.getElementById("main-video-player"),
  mainAudioPlayer: document.getElementById("main-audio-player"),
  previewOverlay: document.getElementById("preview-overlay"),
  liveCaptionDisplay: document.getElementById("live-caption-display"),
  liveTitleDisplay: document.getElementById("live-title-display"),
  safeZonesOverlay: document.getElementById("safe-zones-overlay"),
  toggleSafeZones: document.getElementById("toggle-safe-zones"),
  previewResBadge: document.getElementById("preview-res-badge"),
  
  // Controls
  btnStepBackward: document.getElementById("btn-step-backward"),
  btnPlayPause: document.getElementById("btn-play-pause"),
  btnStepForward: document.getElementById("btn-step-forward"),
  btnSplitClip: document.getElementById("btn-split-clip"),
  btnDeleteClip: document.getElementById("btn-delete-clip"),
  btnSnapBeats: document.getElementById("btn-snap-beats"),
  
  // Timeline
  timelineZoomSlider: document.getElementById("timeline-zoom-slider"),
  btnZoomIn: document.getElementById("btn-zoom-in"),
  btnZoomOut: document.getElementById("btn-zoom-out"),
  timelineDurationLabel: document.getElementById("timeline-duration-label"),
  btnAddVideoTrack: document.getElementById("btn-add-video-track"),
  btnAddAudioTrack: document.getElementById("btn-add-audio-track"),
  timelineScrollArea: document.getElementById("timeline-scroll-area"),
  timelineLanesContainer: document.getElementById("timeline-lanes-container"),
  timelineRuler: document.getElementById("timeline-ruler"),
  rulerTicks: document.getElementById("ruler-ticks"),
  playhead: document.getElementById("playhead"),
  
  // AI Modal
  modalAiAutoEdit: document.getElementById("modal-ai-auto-edit"),
  btnCloseAiModal: document.getElementById("btn-close-ai-modal"),
  btnCancelAi: document.getElementById("btn-cancel-ai"),
  btnStartAiAnalysis: document.getElementById("btn-start-ai-analysis"),
  btnApplyAiTimeline: document.getElementById("btn-apply-ai-timeline"),
  autoEditDuration: document.getElementById("auto-edit-duration"),
  autoEditMusicSelect: document.getElementById("auto-edit-music-select"),
  autoEditColor: document.getElementById("auto-edit-color"),
  autoEditSnapBeats: document.getElementById("auto-edit-snap-beats"),
  autoEditWhisper: document.getElementById("auto-edit-whisper"),
  autoEditSilence: document.getElementById("auto-edit-silence"),
  aiStepper: document.getElementById("ai-stepper"),
  aiProposalPreview: document.getElementById("ai-proposal-preview"),
  aiProposalSummary: document.getElementById("ai-proposal-summary"),
  
  // Export Modal
  modalExport: document.getElementById("modal-export"),
  btnCloseExportModal: document.getElementById("btn-close-export-modal"),
  btnCancelExport: document.getElementById("btn-cancel-export"),
  btnStartExport: document.getElementById("btn-start-export"),
  exportPresetSelect: document.getElementById("export-preset-select"),
  exportQualitySelect: document.getElementById("export-quality-select"),
  exportProgressContainer: document.getElementById("export-progress-container"),
  exportProgressFill: document.getElementById("export-progress-fill"),
  exportProgressText: document.getElementById("export-progress-text"),
  exportResultContainer: document.getElementById("export-result-container"),
  exportFileDetails: document.getElementById("export-file-details"),
  exportDownloadLink: document.getElementById("export-download-link")
};

// ==========================================================================
// Initialization
// ==========================================================================
async function initApp() {
  setupEventListeners();
  applyColorFilters();
  await fetchMediaLibrary();
  
  // Check if saved project exists or initialize defaults
  await loadDefaultOrSavedProject();
  
  renderTimelineRuler();
  renderClips();
  renderSubtitlesList();
  updateTimecodeDisplay();
}

// ==========================================================================
// Event Listeners
// ==========================================================================
function setupEventListeners() {
  // Navigation & Project
  el.projectNameInput.addEventListener("change", (e) => {
    state.projectName = e.target.value.trim() || "Untitled_Reel";
    markProjectDirty();
  });
  el.btnSaveProject.addEventListener("click", saveProject);

  // Aspect Ratio
  el.aspectBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      el.aspectBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const aspect = btn.dataset.aspect;
      setAspectRatio(aspect);
    });
  });

  // Left Panel Tabs
  el.tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      el.tabBtns.forEach(b => b.classList.remove("active"));
      el.tabPanes.forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      const tabId = btn.dataset.tab;
      document.getElementById(tabId).classList.add("active");
    });
  });

  // Media Library Category filter & Refresh
  el.mediaCatBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      el.mediaCatBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.activeCategory = btn.dataset.cat;
      renderMediaGrid();
    });
  });
  el.btnRefreshMedia.addEventListener("click", fetchMediaLibrary);

  // Quick Action Buttons on Selected Media
  el.btnReframeSelected.addEventListener("click", handleAutoReframeSelected);
  el.btnSilenceSelected.addEventListener("click", handleSilenceCutSelected);

  // Color Presets & Sliders
  el.colorPresetCards.forEach(card => {
    card.addEventListener("click", () => {
      el.colorPresetCards.forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      state.colorPreset = card.dataset.preset;
      applyColorFilters();
      markProjectDirty();
    });
  });

  el.sliderContrast.addEventListener("input", (e) => {
    state.colorAdjustments.contrast = parseFloat(e.target.value);
    el.contrastVal.textContent = e.target.value;
    applyColorFilters();
  });
  el.sliderSaturation.addEventListener("input", (e) => {
    state.colorAdjustments.saturation = parseFloat(e.target.value);
    el.saturationVal.textContent = e.target.value;
    applyColorFilters();
  });
  el.sliderBrightness.addEventListener("input", (e) => {
    state.colorAdjustments.brightness = parseFloat(e.target.value);
    el.brightnessVal.textContent = e.target.value;
    applyColorFilters();
  });

  // Captions
  el.btnRunWhisper.addEventListener("click", handleAutoTranscribe);
  el.btnAddCaptionWord.addEventListener("click", () => {
    const word = prompt("Enter caption text:", "NEW CAPTION");
    if (word) {
      state.subtitles.push({
        start: Math.max(0, state.currentTime),
        end: Math.min(state.duration, state.currentTime + 1.2),
        word: word.trim()
      });
      state.subtitles.sort((a, b) => a.start - b.start);
      renderSubtitlesList();
      updateOverlays();
      markProjectDirty();
    }
  });
  el.captionColorInput.addEventListener("input", updateOverlays);

  // Audio Mixer
  el.mixerMaster.addEventListener("input", (e) => {
    state.audioMixer.master = parseFloat(e.target.value);
    el.mixerMasterVal.textContent = `${Math.round(state.audioMixer.master * 100)}%`;
    syncMixerVolumes();
  });
  el.mixerVoice.addEventListener("input", (e) => {
    state.audioMixer.voice = parseFloat(e.target.value);
    el.mixerVoiceVal.textContent = `${Math.round(state.audioMixer.voice * 100)}%`;
    syncMixerVolumes();
  });
  el.mixerMusic.addEventListener("input", (e) => {
    state.audioMixer.music = parseFloat(e.target.value);
    el.mixerMusicVal.textContent = `${Math.round(state.audioMixer.music * 100)}%`;
    syncMixerVolumes();
  });
  el.mixerDucking.addEventListener("change", (e) => {
    state.audioMixer.ducking = e.target.checked;
  });
  el.mixerLoudnorm.addEventListener("change", (e) => {
    state.audioMixer.loudnorm = e.target.checked;
  });

  // Safe Zones
  el.toggleSafeZones.addEventListener("change", (e) => {
    el.safeZonesOverlay.classList.toggle("active", e.target.checked);
  });

  // Playback Controls
  el.btnPlayPause.addEventListener("click", togglePlayPause);
  el.btnStepBackward.addEventListener("click", () => seekTo(Math.max(0, state.currentTime - 1.0)));
  el.btnStepForward.addEventListener("click", () => seekTo(Math.min(state.duration, state.currentTime + 1.0)));
  el.btnSplitClip.addEventListener("click", splitClipAtPlayhead);
  el.btnDeleteClip.addEventListener("click", deleteSelectedClip);
  el.btnSnapBeats.addEventListener("click", snapCutsToMusicBeats);

  // Keyboard Shortcuts
  window.addEventListener("keydown", (e) => {
    if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT" || e.target.tagName === "TEXTAREA") return;
    if (e.code === "Space") {
      e.preventDefault();
      togglePlayPause();
    } else if (e.code === "KeyS") {
      splitClipAtPlayhead();
    } else if (e.code === "Delete" || e.code === "Backspace") {
      deleteSelectedClip();
    } else if (e.code === "ArrowLeft") {
      seekTo(Math.max(0, state.currentTime - 0.2));
    } else if (e.code === "ArrowRight") {
      seekTo(Math.min(state.duration, state.currentTime + 0.2));
    }
  });

  // Timeline Zoom
  el.timelineZoomSlider.addEventListener("input", (e) => {
    state.zoom = parseInt(e.target.value);
    renderTimelineRuler();
    renderClips();
    updatePlayheadPosition();
  });
  el.btnZoomIn.addEventListener("click", () => {
    state.zoom = Math.min(120, state.zoom + 15);
    el.timelineZoomSlider.value = state.zoom;
    renderTimelineRuler();
    renderClips();
    updatePlayheadPosition();
  });
  el.btnZoomOut.addEventListener("click", () => {
    state.zoom = Math.max(10, state.zoom - 15);
    el.timelineZoomSlider.value = state.zoom;
    renderTimelineRuler();
    renderClips();
    updatePlayheadPosition();
  });

  // Ruler Seeking & Scrubbing
  el.timelineRuler.addEventListener("mousedown", onRulerMouseDown);

  // Track Creation
  el.btnAddVideoTrack.addEventListener("click", () => {
    const num = state.tracks.filter(t => t.type === "video").length + 1;
    const newId = `track-video-${num}`;
    state.tracks.unshift({ id: newId, type: "video", name: `Video ${num}`, muted: false });
    rebuildTimelineDOM();
  });
  el.btnAddAudioTrack.addEventListener("click", () => {
    const num = state.tracks.filter(t => t.type === "audio").length + 1;
    const newId = `track-audio-${num}`;
    state.tracks.push({ id: newId, type: "audio", name: `Audio ${num}`, muted: false });
    rebuildTimelineDOM();
  });

  // Modals Open/Close
  el.btnAiAutoEdit.addEventListener("click", () => el.modalAiAutoEdit.classList.add("active"));
  el.btnCloseAiModal.addEventListener("click", () => el.modalAiAutoEdit.classList.remove("active"));
  el.btnCancelAi.addEventListener("click", () => el.modalAiAutoEdit.classList.remove("active"));
  el.btnStartAiAnalysis.addEventListener("click", runAiAutoEditWizard);
  el.btnApplyAiTimeline.addEventListener("click", applyAiProposalToTimeline);

  el.btnExportModal.addEventListener("click", () => {
    el.modalExport.classList.add("active");
    el.exportProgressContainer.classList.add("hidden");
    el.exportResultContainer.classList.add("hidden");
    el.btnStartExport.classList.remove("hidden");
  });
  el.btnCloseExportModal.addEventListener("click", () => el.modalExport.classList.remove("active"));
  el.btnCancelExport.addEventListener("click", () => el.modalExport.classList.remove("active"));
  el.btnStartExport.addEventListener("click", startExportRender);

  // Transitions selection
  document.querySelectorAll(".transition-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      document.querySelectorAll(".transition-pill").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      if (state.selectedClipId) {
        const clip = state.clips.find(c => c.id === state.selectedClipId);
        if (clip) {
          clip.transition = pill.dataset.transition;
          markProjectDirty();
        }
      }
    });
  });

  // Effects cards
  document.querySelectorAll(".apply-effect-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const card = e.target.closest(".effect-card");
      const effectName = card.dataset.effect;
      if (!state.activeEffects.includes(effectName)) {
        state.activeEffects.push(effectName);
        btn.textContent = "Active";
        btn.classList.add("btn-primary");
        btn.classList.remove("btn-secondary");
      } else {
        state.activeEffects = state.activeEffects.filter(ef => ef !== effectName);
        btn.textContent = "Apply";
        btn.classList.remove("btn-primary");
        btn.classList.add("btn-secondary");
      }
      applyColorFilters();
    });
  });
}

// ==========================================================================
// Media Library & Inspection
// ==========================================================================
async function fetchMediaLibrary() {
  try {
    const res = await fetch("/api/media");
    if (!res.ok) throw new Error("Failed to fetch media");
    const data = await res.json();
    state.mediaLibrary = data.files || [];
    renderMediaGrid();
    updateMusicSelectDropdown();
  } catch (err) {
    console.error("Media load error:", err);
  }
}

function renderMediaGrid() {
  el.mediaGrid.innerHTML = "";
  const filtered = state.mediaLibrary.filter(item => {
    if (state.activeCategory === "all") return true;
    return item.category === state.activeCategory;
  });

  if (filtered.length === 0) {
    el.mediaGrid.innerHTML = `<div style="grid-column: 1/-1; font-size:0.75rem; color: var(--text-muted); text-align:center; padding: 20px;">No media files found</div>`;
    return;
  }

  filtered.forEach(file => {
    const card = document.createElement("div");
    card.className = "media-card";
    card.draggable = true;
    card.dataset.filePath = file.path;
    card.dataset.fileType = file.type;
    card.dataset.fileName = file.name;
    card.dataset.fileDuration = file.duration || 5.0;

    const durFormatted = `${(file.duration || 0).toFixed(1)}s`;
    const isVideo = file.type === "video";
    
    card.innerHTML = `
      <div class="media-thumb-wrapper">
        ${isVideo ? `<video src="/api/stream?path=${encodeURIComponent(file.path)}" preload="metadata" muted></video>` : `<div style="font-size:1.8rem;">🎵</div>`}
        <span class="media-badge">${file.category}</span>
        <span class="media-duration">${durFormatted}</span>
      </div>
      <div class="media-card-title" title="${file.name}">${file.name}</div>
    `;

    // Drag-and-drop to timeline
    card.addEventListener("dragstart", (e) => {
      e.dataTransfer.setData("application/json", JSON.stringify({
        path: file.path,
        type: file.type,
        name: file.name,
        duration: file.duration || 5.0
      }));
    });

    // Click to select
    card.addEventListener("click", () => {
      document.querySelectorAll(".media-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      card.dataset.activeSelection = "true";
    });

    // Double-click to preview or add to timeline
    card.addEventListener("dblclick", () => {
      addClipToTimeline(file.path, file.type, file.name, file.duration || 5.0);
    });

    el.mediaGrid.appendChild(card);
  });
}

function updateMusicSelectDropdown() {
  const musicFiles = state.mediaLibrary.filter(f => f.type === "audio");
  if (musicFiles.length > 0) {
    el.autoEditMusicSelect.innerHTML = musicFiles.map(m => 
      `<option value="${m.name}">${m.name} (${(m.duration || 0).toFixed(1)}s)</option>`
    ).join("");
  }
}

// ==========================================================================
// Timeline DOM & Clips Management
// ==========================================================================
function setAspectRatio(aspect) {
  state.aspectRatio = aspect;
  el.previewFrame.className = `preview-frame aspect-${aspect.replace(":", "-")}`;
  if (aspect === "9:16") {
    state.resolution = { width: 1080, height: 1920, fps: 30 };
    el.previewResBadge.textContent = "1080 x 1920 (9:16)";
  } else if (aspect === "16:9") {
    state.resolution = { width: 1920, height: 1080, fps: 30 };
    el.previewResBadge.textContent = "1920 x 1080 (16:9)";
  } else {
    state.resolution = { width: 1080, height: 1080, fps: 30 };
    el.previewResBadge.textContent = "1080 x 1080 (1:1)";
  }
  markProjectDirty();
}

function rebuildTimelineDOM() {
  const headersContainer = document.querySelector(".timeline-track-headers");
  headersContainer.innerHTML = "";
  
  // Rebuild track headers
  state.tracks.forEach(track => {
    const isVideo = track.type === "video";
    const header = document.createElement("div");
    header.className = "track-header";
    header.dataset.trackId = track.id;
    header.innerHTML = `
      <span class="track-tag ${isVideo ? 'tag-video' : 'tag-audio'}">${track.id.replace("track-", "").toUpperCase()}</span>
      <span class="track-title">${track.name}</span>
      <div class="track-btns">
        <button class="track-mute-btn" title="Mute/Hide">${track.muted ? '🔇' : (isVideo ? '👁' : '🔊')}</button>
      </div>
    `;
    const muteBtn = header.querySelector(".track-mute-btn");
    muteBtn.addEventListener("click", () => {
      track.muted = !track.muted;
      muteBtn.textContent = track.muted ? '🔇' : (isVideo ? '👁' : '🔊');
      markProjectDirty();
    });
    headersContainer.appendChild(header);
  });

  // Rebuild track lanes
  el.timelineLanesContainer.querySelectorAll(".timeline-track-lane").forEach(lane => lane.remove());
  state.tracks.forEach(track => {
    const lane = document.createElement("div");
    lane.className = "timeline-track-lane";
    lane.id = `lane-${track.id}`;
    lane.dataset.trackId = track.id;
    
    // Setup drop target
    lane.addEventListener("dragover", (e) => e.preventDefault());
    lane.addEventListener("drop", (e) => {
      e.preventDefault();
      try {
        const data = JSON.parse(e.dataTransfer.getData("application/json"));
        const laneRect = lane.getBoundingClientRect();
        const dropX = e.clientX - laneRect.left + el.timelineLanesContainer.scrollLeft;
        const dropTime = Math.max(0, dropX / state.zoom);
        addClipToTimeline(data.path, data.type, data.name, data.duration, track.id, dropTime);
      } catch (err) {
        console.error("Drop error:", err);
      }
    });

    el.timelineLanesContainer.appendChild(lane);
  });

  renderClips();
}

function addClipToTimeline(filePath, type, name, duration, trackId = null, startTime = null) {
  if (!trackId) {
    trackId = type === "video" ? "track-video-1" : "track-audio-2";
  }
  if (startTime === null) {
    // Append to end of existing clips on track or at playhead
    const clipsOnTrack = state.clips.filter(c => c.trackId === trackId);
    if (clipsOnTrack.length > 0) {
      const lastClip = clipsOnTrack.reduce((max, c) => (c.startTime + c.duration > max.startTime + max.duration ? c : max), clipsOnTrack[0]);
      startTime = lastClip.startTime + lastClip.duration;
    } else {
      startTime = state.currentTime;
    }
  }

  const newClip = {
    id: `clip_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
    trackId: trackId,
    name: name,
    path: filePath,
    startTime: startTime,
    duration: Math.min(duration, 15.0),
    sourceIn: 0.0,
    sourceDuration: duration,
    type: type,
    transition: "none",
    volume: 1.0
  };

  state.clips.push(newClip);
  updateTotalDuration();
  renderClips();
  markProjectDirty();
  selectClip(newClip.id);
}

function updateTotalDuration() {
  let maxTime = 15.0;
  state.clips.forEach(c => {
    if (c.startTime + c.duration > maxTime) {
      maxTime = c.startTime + c.duration;
    }
  });
  state.duration = Math.ceil(maxTime * 10) / 10;
  const frames = Math.round(state.duration * state.resolution.fps);
  el.timelineDurationLabel.textContent = `Duration: ${state.duration.toFixed(1)}s | ${frames} Frames`;
  renderTimelineRuler();
}

function renderTimelineRuler() {
  el.rulerTicks.innerHTML = "";
  const totalSeconds = Math.max(state.duration + 5, 20);
  const laneWidth = totalSeconds * state.zoom;
  el.timelineRuler.style.width = `${laneWidth}px`;
  
  document.querySelectorAll(".timeline-track-lane").forEach(lane => {
    lane.style.width = `${laneWidth}px`;
  });

  // Second markings
  for (let s = 0; s <= totalSeconds; s++) {
    const tick = document.createElement("div");
    tick.className = "ruler-tick";
    tick.style.left = `${s * state.zoom}px`;
    tick.textContent = `${s}s`;
    el.rulerTicks.appendChild(tick);
  }
}

function renderClips() {
  document.querySelectorAll(".timeline-clip").forEach(c => c.remove());

  state.clips.forEach(clip => {
    const lane = document.getElementById(`lane-${clip.trackId}`);
    if (!lane) return;

    const clipEl = document.createElement("div");
    clipEl.className = `timeline-clip ${clip.type}-clip ${clip.id === state.selectedClipId ? 'selected' : ''}`;
    clipEl.id = clip.id;
    clipEl.style.left = `${clip.startTime * state.zoom}px`;
    clipEl.style.width = `${Math.max(20, clip.duration * state.zoom)}px`;

    clipEl.innerHTML = `
      <div class="trim-handle trim-handle-left"></div>
      <span class="clip-label">${clip.name}</span>
      <span class="clip-duration-tag">${clip.duration.toFixed(1)}s</span>
      <div class="trim-handle trim-handle-right"></div>
    `;

    // Clip Selection
    clipEl.addEventListener("mousedown", (e) => {
      if (e.target.classList.contains("trim-handle")) return;
      e.stopPropagation();
      selectClip(clip.id);
      startDragClip(e, clip, clipEl);
    });

    // Left trim handle
    const leftHandle = clipEl.querySelector(".trim-handle-left");
    leftHandle.addEventListener("mousedown", (e) => {
      e.stopPropagation();
      startTrimClip(e, clip, "left");
    });

    // Right trim handle
    const rightHandle = clipEl.querySelector(".trim-handle-right");
    rightHandle.addEventListener("mousedown", (e) => {
      e.stopPropagation();
      startTrimClip(e, clip, "right");
    });

    lane.appendChild(clipEl);
  });
}

function selectClip(clipId) {
  state.selectedClipId = clipId;
  document.querySelectorAll(".timeline-clip").forEach(c => {
    c.classList.toggle("selected", c.id === clipId);
  });
  const clip = state.clips.find(c => c.id === clipId);
  if (clip && clip.transition) {
    document.querySelectorAll(".transition-pill").forEach(p => {
      p.classList.toggle("active", p.dataset.transition === clip.transition);
    });
  }
}

// Interactive Clip Dragging
function startDragClip(e, clip, clipEl) {
  const startX = e.clientX;
  const initialStartTime = clip.startTime;

  function onMouseMove(moveEvent) {
    const deltaX = moveEvent.clientX - startX;
    const deltaTime = deltaX / state.zoom;
    const newStartTime = Math.max(0, initialStartTime + deltaTime);
    clip.startTime = Math.round(newStartTime * 20) / 20; // 50ms snap
    clipEl.style.left = `${clip.startTime * state.zoom}px`;
    updateTotalDuration();
  }

  function onMouseUp() {
    window.removeEventListener("mousemove", onMouseMove);
    window.removeEventListener("mouseup", onMouseUp);
    renderClips();
    markProjectDirty();
  }

  window.addEventListener("mousemove", onMouseMove);
  window.addEventListener("mouseup", onMouseUp);
}

// Interactive Clip Trimming
function startTrimClip(e, clip, edge) {
  const startX = e.clientX;
  const initialStart = clip.startTime;
  const initialDuration = clip.duration;
  const initialSourceIn = clip.sourceIn;

  function onMouseMove(moveEvent) {
    const deltaX = moveEvent.clientX - startX;
    const deltaTime = deltaX / state.zoom;

    if (edge === "left") {
      const maxDelta = initialDuration - 0.5;
      const effectiveDelta = Math.min(deltaTime, maxDelta);
      const newStart = Math.max(0, initialStart + effectiveDelta);
      const newDuration = initialDuration - (newStart - initialStart);
      clip.startTime = Math.round(newStart * 20) / 20;
      clip.sourceIn = Math.max(0, initialSourceIn + (newStart - initialStart));
      clip.duration = Math.round(newDuration * 20) / 20;
    } else {
      const newDuration = Math.max(0.5, initialDuration + deltaTime);
      clip.duration = Math.round(newDuration * 20) / 20;
    }
    renderClips();
    updateTotalDuration();
  }

  function onMouseUp() {
    window.removeEventListener("mousemove", onMouseMove);
    window.removeEventListener("mouseup", onMouseUp);
    renderClips();
    markProjectDirty();
  }

  window.addEventListener("mousemove", onMouseMove);
  window.addEventListener("mouseup", onMouseUp);
}

// Split Clip at Playhead
function splitClipAtPlayhead() {
  const t = state.currentTime;
  const clip = state.clips.find(c => t > c.startTime && t < (c.startTime + c.duration));
  if (!clip) return;

  const firstDuration = t - clip.startTime;
  const secondDuration = clip.duration - firstDuration;

  clip.duration = firstDuration;

  const splitClip = {
    ...clip,
    id: `clip_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
    startTime: t,
    duration: secondDuration,
    sourceIn: clip.sourceIn + firstDuration
  };

  state.clips.push(splitClip);
  renderClips();
  markProjectDirty();
  selectClip(splitClip.id);
}

// Delete Selected Clip
function deleteSelectedClip() {
  if (!state.selectedClipId) return;
  state.clips = state.clips.filter(c => c.id !== state.selectedClipId);
  state.selectedClipId = null;
  updateTotalDuration();
  renderClips();
  markProjectDirty();
}

// ==========================================================================
// Playback Transport & Sync
// ==========================================================================
function togglePlayPause() {
  state.isPlaying = !state.isPlaying;
  el.btnPlayPause.textContent = state.isPlaying ? "⏸" : "▶";

  if (state.isPlaying) {
    if (state.currentTime >= state.duration) {
      seekTo(0);
    }
    playLoop();
  }
}

let lastPlayTime = null;
function playLoop(timestamp) {
  if (!state.isPlaying) {
    lastPlayTime = null;
    return;
  }
  if (!lastPlayTime) lastPlayTime = timestamp || performance.now();
  const delta = (timestamp - lastPlayTime) / 1000;
  lastPlayTime = timestamp;

  if (delta > 0 && delta < 0.2) {
    state.currentTime += delta;
    if (state.currentTime >= state.duration) {
      state.currentTime = state.duration;
      togglePlayPause();
      updatePlayheadPosition();
      updateTimecodeDisplay();
      return;
    }
  }

  updatePlayheadPosition();
  syncVideoAudioPlayback();
  updateOverlays();
  updateTimecodeDisplay();

  requestAnimationFrame(playLoop);
}

function seekTo(time) {
  state.currentTime = Math.max(0, Math.min(state.duration, time));
  updatePlayheadPosition();
  syncVideoAudioPlayback(true);
  updateOverlays();
  updateTimecodeDisplay();
}

function onRulerMouseDown(e) {
  const rulerRect = el.timelineRuler.getBoundingClientRect();
  const clickX = e.clientX - rulerRect.left;
  seekTo(clickX / state.zoom);

  function onMouseMove(moveEvent) {
    const moveX = moveEvent.clientX - rulerRect.left;
    seekTo(moveX / state.zoom);
  }

  function onMouseUp() {
    window.removeEventListener("mousemove", onMouseMove);
    window.removeEventListener("mouseup", onMouseUp);
  }

  window.addEventListener("mousemove", onMouseMove);
  window.addEventListener("mouseup", onMouseUp);
}

function updatePlayheadPosition() {
  const x = state.currentTime * state.zoom;
  el.playhead.style.left = `${x}px`;
  
  // Auto-scroll timeline to keep playhead in view during playback
  const scrollLeft = el.timelineLanesContainer.scrollLeft;
  const viewWidth = el.timelineLanesContainer.clientWidth;
  if (x > scrollLeft + viewWidth - 50) {
    el.timelineLanesContainer.scrollLeft = x - viewWidth / 2;
  }
}

function updateTimecodeDisplay() {
  const fps = state.resolution.fps;
  const totalFrames = Math.floor(state.currentTime * fps);
  const f = totalFrames % fps;
  const s = Math.floor(state.currentTime) % 60;
  const m = Math.floor(state.currentTime / 60) % 60;
  const h = Math.floor(state.currentTime / 3600);

  const pad = (n) => String(n).padStart(2, '0');
  el.masterTimecode.textContent = `${pad(h)}:${pad(m)}:${pad(s)}:${pad(f)}`;
}

// Media element synchronization
let currentActiveVideoPath = null;
let currentActiveAudioPath = null;

function syncVideoAudioPlayback(forceSeek = false) {
  // Find active video clip (prefer V2 then V1)
  const activeVideoClip = state.clips.find(c => 
    c.type === "video" && 
    state.currentTime >= c.startTime && 
    state.currentTime < (c.startTime + c.duration)
  );

  if (activeVideoClip) {
    const targetSourceTime = activeVideoClip.sourceIn + (state.currentTime - activeVideoClip.startTime);
    const streamUrl = `/api/stream?path=${encodeURIComponent(activeVideoClip.path)}`;

    if (currentActiveVideoPath !== activeVideoClip.path) {
      currentActiveVideoPath = activeVideoClip.path;
      el.mainVideoPlayer.src = streamUrl;
      el.mainVideoPlayer.currentTime = targetSourceTime;
      if (state.isPlaying) el.mainVideoPlayer.play().catch(() => {});
    } else if (forceSeek || Math.abs(el.mainVideoPlayer.currentTime - targetSourceTime) > 0.25) {
      el.mainVideoPlayer.currentTime = targetSourceTime;
    }

    if (state.isPlaying && el.mainVideoPlayer.paused) {
      el.mainVideoPlayer.play().catch(() => {});
    } else if (!state.isPlaying && !el.mainVideoPlayer.paused) {
      el.mainVideoPlayer.pause();
    }
  } else {
    if (!el.mainVideoPlayer.paused) el.mainVideoPlayer.pause();
  }

  // Find active audio clip (prefer A2 music or A1 voice)
  const activeAudioClip = state.clips.find(c => 
    c.type === "audio" && 
    state.currentTime >= c.startTime && 
    state.currentTime < (c.startTime + c.duration)
  );

  if (activeAudioClip) {
    const targetAudioTime = activeAudioClip.sourceIn + (state.currentTime - activeAudioClip.startTime);
    const audioUrl = `/api/stream?path=${encodeURIComponent(activeAudioClip.path)}`;

    if (currentActiveAudioPath !== activeAudioClip.path) {
      currentActiveAudioPath = activeAudioClip.path;
      el.mainAudioPlayer.src = audioUrl;
      el.mainAudioPlayer.currentTime = targetAudioTime;
      syncMixerVolumes();
      if (state.isPlaying) el.mainAudioPlayer.play().catch(() => {});
    } else if (forceSeek || Math.abs(el.mainAudioPlayer.currentTime - targetAudioTime) > 0.3) {
      el.mainAudioPlayer.currentTime = targetAudioTime;
    }

    if (state.isPlaying && el.mainAudioPlayer.paused) {
      el.mainAudioPlayer.play().catch(() => {});
    } else if (!state.isPlaying && !el.mainAudioPlayer.paused) {
      el.mainAudioPlayer.pause();
    }
  } else {
    if (!el.mainAudioPlayer.paused) el.mainAudioPlayer.pause();
  }
}

function syncMixerVolumes() {
  const master = state.audioMixer.master;
  const voice = state.audioMixer.voice * master;
  const music = state.audioMixer.music * master;

  // Check if voice clip is active for audio ducking
  const hasVoice = state.clips.some(c => 
    c.trackId === "track-audio-1" && 
    state.currentTime >= c.startTime && 
    state.currentTime < (c.startTime + c.duration)
  );

  let finalMusicVol = music;
  if (state.audioMixer.ducking && hasVoice) {
    finalMusicVol = music * 0.35; // Duck music by 65% during speech
  }

  el.mainVideoPlayer.volume = Math.min(1.0, voice);
  el.mainAudioPlayer.volume = Math.min(1.0, finalMusicVol);
}

// Live Subtitle & Title Overlays
function updateOverlays() {
  const t = state.currentTime;
  
  // Find active word or caption
  const activeSub = state.subtitles.find(s => t >= s.start && t <= s.end);
  if (activeSub) {
    const highlightColor = el.captionColorInput.value;
    el.liveCaptionDisplay.innerHTML = `<span class="highlight-word" style="color: ${highlightColor};">${activeSub.word}</span>`;
  } else {
    el.liveCaptionDisplay.innerHTML = "";
  }

  // Title display if near beginning
  if (t < 2.5 && state.activeEffects.includes("story-progress")) {
    el.liveTitleDisplay.textContent = state.projectName.replace(/_/g, " ").toUpperCase();
    el.liveTitleDisplay.style.display = "block";
  } else {
    el.liveTitleDisplay.style.display = "none";
  }
}

// ==========================================================================
// Color Grading & Effects Filters
// ==========================================================================
function applyColorFilters() {
  let filterStr = `contrast(${state.colorAdjustments.contrast}) saturate(${state.colorAdjustments.saturation}) brightness(${state.colorAdjustments.brightness})`;
  
  if (state.colorPreset === "teal_orange") {
    filterStr += " hue-rotate(5deg) sepia(0.08)";
  } else if (state.colorPreset === "moody_monochrome") {
    filterStr += " grayscale(1) contrast(1.2)";
  } else if (state.colorPreset === "warm_film") {
    filterStr += " sepia(0.25) saturate(1.1)";
  } else if (state.colorPreset === "vibrant_pop") {
    filterStr += " saturate(1.4) contrast(1.1)";
  } else if (state.colorPreset === "vintage_gold") {
    filterStr += " sepia(0.4) hue-rotate(-15deg)";
  }

  el.mainVideoPlayer.style.filter = filterStr;
}

// ==========================================================================
// Subtitle Editing
// ==========================================================================
function renderSubtitlesList() {
  el.subtitlesList.innerHTML = "";
  if (state.subtitles.length === 0) {
    el.subtitlesList.innerHTML = `<div style="font-size:0.75rem; color: var(--text-muted); padding: 8px;">No captions added yet. Click Auto Transcribe or + Add Word.</div>`;
    return;
  }

  state.subtitles.forEach((sub, idx) => {
    const item = document.createElement("div");
    item.className = "subtitle-item";
    item.innerHTML = `
      <span class="sub-time">${sub.start.toFixed(1)}s</span>
      <input type="text" class="sub-text" value="${sub.word}">
      <button class="sub-delete" title="Delete caption">×</button>
    `;

    // Click time to seek
    item.querySelector(".sub-time").addEventListener("click", () => seekTo(sub.start));

    // Edit text
    item.querySelector(".sub-text").addEventListener("change", (e) => {
      sub.word = e.target.value.trim();
      updateOverlays();
      markProjectDirty();
    });

    // Delete caption
    item.querySelector(".sub-delete").addEventListener("click", () => {
      state.subtitles.splice(idx, 1);
      renderSubtitlesList();
      updateOverlays();
      markProjectDirty();
    });

    el.subtitlesList.appendChild(item);
  });
}

async function handleAutoTranscribe() {
  const speechVideo = state.clips.find(c => c.type === "video");
  if (!speechVideo) {
    alert("Please add a video clip to the timeline first.");
    return;
  }

  el.btnRunWhisper.textContent = "Transcribing...";
  el.btnRunWhisper.disabled = true;

  try {
    const res = await fetch("/api/ai/transcribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_path: speechVideo.path })
    });
    const data = await res.json();
    if (data.status === "success" && data.words) {
      state.subtitles = data.words.map(w => ({
        start: w.start,
        end: w.end,
        word: w.word
      }));
      renderSubtitlesList();
      updateOverlays();
      markProjectDirty();
    } else {
      alert("Whisper speech transcription returned no words.");
    }
  } catch (err) {
    console.error("Transcription error:", err);
    alert("Whisper transcription failed: " + err.message);
  } finally {
    el.btnRunWhisper.textContent = "Auto Transcribe";
    el.btnRunWhisper.disabled = false;
  }
}

// ==========================================================================
// Quick AI Tools (Reframe & Silence Cut)
// ==========================================================================
async function handleAutoReframeSelected() {
  const selectedCard = document.querySelector('.media-card[data-active-selection="true"]');
  if (!selectedCard) {
    alert("Click a footage card in the Media Library first.");
    return;
  }

  const filePath = selectedCard.dataset.filePath;
  const fileName = selectedCard.dataset.fileName;
  el.btnReframeSelected.textContent = "Reframing...";
  el.btnReframeSelected.disabled = true;

  try {
    const res = await fetch("/api/ai/auto-reframe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_path: filePath, target_aspect: "9:16" })
    });
    const data = await res.json();
    if (data.status === "success") {
      alert(`Auto-Reframe complete!\nReframed 9:16 clip saved to:\n${data.output_path}`);
      await fetchMediaLibrary();
    } else {
      alert("Auto reframe failed: " + data.message);
    }
  } catch (err) {
    alert("Error running auto-reframe: " + err.message);
  } finally {
    el.btnReframeSelected.textContent = "Auto Reframe 9:16";
    el.btnReframeSelected.disabled = false;
  }
}

async function handleSilenceCutSelected() {
  const selectedCard = document.querySelector('.media-card[data-active-selection="true"]');
  if (!selectedCard) {
    alert("Click a footage card in the Media Library first.");
    return;
  }

  const filePath = selectedCard.dataset.filePath;
  el.btnSilenceSelected.textContent = "Removing Silence...";
  el.btnSilenceSelected.disabled = true;

  try {
    const res = await fetch("/api/ai/silence-remove", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ media_path: filePath, threshold: "4%" })
    });
    const data = await res.json();
    if (data.status === "success") {
      alert(`Silence removed successfully!\nTightened clip saved to:\n${data.output_path}`);
      await fetchMediaLibrary();
    } else {
      alert("Silence removal failed: " + data.message);
    }
  } catch (err) {
    alert("Error cutting silence: " + err.message);
  } finally {
    el.btnSilenceSelected.textContent = "Cut Silence";
    el.btnSilenceSelected.disabled = false;
  }
}

async function snapCutsToMusicBeats() {
  const musicClip = state.clips.find(c => c.type === "audio");
  if (!musicClip) {
    alert("Please add a background music track to Audio 2 (A2) first.");
    return;
  }

  try {
    const res = await fetch("/api/ai/beats", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ audio_path: musicClip.path })
    });
    const data = await res.json();
    if (data.status === "success" && data.beats && data.beats.length > 0) {
      const beats = data.beats;
      // Snap each video clip boundary to nearest beat
      state.clips.forEach(clip => {
        if (clip.type === "video") {
          const nearestStartBeat = beats.reduce((prev, curr) => Math.abs(curr - clip.startTime) < Math.abs(prev - clip.startTime) ? curr : prev);
          if (Math.abs(nearestStartBeat - clip.startTime) < 0.6) {
            clip.startTime = nearestStartBeat;
          }
        }
      });
      renderClips();
      markProjectDirty();
      alert(`Snapped cuts to ${data.beats.length} Librosa detected beats (${data.tempo.toFixed(1)} BPM)!`);
    }
  } catch (err) {
    console.error("Beat snap error:", err);
  }
}

// ==========================================================================
// AI Auto-Edit Wizard
// ==========================================================================
async function runAiAutoEditWizard() {
  el.aiStepper.classList.remove("hidden");
  el.btnStartAiAnalysis.disabled = true;
  el.btnStartAiAnalysis.textContent = "Analyzing...";

  const targetDuration = parseFloat(el.autoEditDuration.value);
  const musicFileName = el.autoEditMusicSelect.value;
  const colorPreset = el.autoEditColor.value;

  // Step 1: Detect scenes
  setStepStatus("step-scenes", "active");
  await new Promise(r => setTimeout(r, 600));

  try {
    const footageFiles = state.mediaLibrary.filter(f => f.type === "video").map(f => f.path);
    const musicFile = state.mediaLibrary.find(f => f.name === musicFileName);
    const musicPath = musicFile ? musicFile.path : null;

    setStepStatus("step-scenes", "done");
    setStepStatus("step-beats", "active");

    const payload = {
      footage_paths: footageFiles,
      music_path: musicPath,
      target_duration: targetDuration,
      color_preset: colorPreset,
      snap_to_beats: el.autoEditSnapBeats.checked,
      generate_subtitles: el.autoEditWhisper.checked
    };

    const res = await fetch("/api/ai/auto-edit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    setStepStatus("step-beats", "done");
    setStepStatus("step-curate", "done");
    setStepStatus("step-captions", "done");

    if (data.status === "success") {
      state.aiProposal = data.project;
      el.aiProposalPreview.classList.remove("hidden");
      el.aiProposalSummary.textContent = `${data.cut_count} cuts curated, ${data.project.subtitles.length} words transcribed, ${data.project.duration.toFixed(1)}s total duration.`;
      el.btnApplyAiTimeline.classList.remove("hidden");
      el.btnStartAiAnalysis.classList.add("hidden");
    } else {
      alert("AI Auto-Edit error: " + data.message);
    }
  } catch (err) {
    alert("AI Auto-Edit failed: " + err.message);
  } finally {
    el.btnStartAiAnalysis.disabled = false;
    el.btnStartAiAnalysis.textContent = "Run Analysis";
  }
}

function setStepStatus(stepId, status) {
  const item = document.getElementById(stepId);
  if (!item) return;
  item.classList.remove("active", "done");
  item.classList.add(status);
}

function applyAiProposalToTimeline() {
  if (!state.aiProposal) return;
  
  state.clips = state.aiProposal.clips || [];
  state.subtitles = state.aiProposal.subtitles || [];
  state.duration = state.aiProposal.duration || 15.0;
  state.colorPreset = state.aiProposal.colorPreset || "teal_orange";

  updateTotalDuration();
  renderClips();
  renderSubtitlesList();
  applyColorFilters();
  updateOverlays();
  seekTo(0);
  
  el.modalAiAutoEdit.classList.remove("active");
  markProjectDirty();
  alert("AI Timeline Applied! You can now preview, make manual adjustments, or export.");
}

// ==========================================================================
// Export & Asynchronous Rendering
// ==========================================================================
async function startExportRender() {
  el.btnStartExport.classList.add("hidden");
  el.exportProgressContainer.classList.remove("hidden");
  el.exportProgressFill.style.width = "10%";
  el.exportProgressText.textContent = "Submitting render job...";

  const projectPayload = {
    projectName: state.projectName,
    aspectRatio: state.aspectRatio,
    resolution: state.resolution,
    duration: state.duration,
    clips: state.clips,
    subtitles: state.subtitles,
    colorPreset: state.colorPreset,
    audioMixer: state.audioMixer
  };

  try {
    const res = await fetch("/api/render", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project: projectPayload,
        engine: "ffmpeg",
        quality_crf: parseInt(el.exportQualitySelect.value)
      })
    });
    const data = await res.json();
    if (data.status === "queued" && data.job_id) {
      pollRenderStatus(data.job_id);
    } else {
      alert("Render submission failed: " + data.message);
      el.btnStartExport.classList.remove("hidden");
    }
  } catch (err) {
    alert("Render error: " + err.message);
    el.btnStartExport.classList.remove("hidden");
  }
}

async function pollRenderStatus(jobId) {
  const interval = setInterval(async () => {
    try {
      const res = await fetch(`/api/render/status/${jobId}`);
      const job = await res.json();

      el.exportProgressFill.style.width = `${job.progress}%`;
      el.exportProgressText.textContent = `Rendering: ${job.progress}% (${job.message})`;

      if (job.status === "completed") {
        clearInterval(interval);
        el.exportProgressContainer.classList.add("hidden");
        el.exportResultContainer.classList.remove("hidden");
        el.exportFileDetails.textContent = `Rendered to: ${job.output_path}`;
        el.exportDownloadLink.href = `/api/stream?path=${encodeURIComponent(job.output_path)}`;
        el.exportDownloadLink.textContent = "Open / Download Video";
      } else if (job.status === "failed") {
        clearInterval(interval);
        el.exportProgressText.textContent = `Error: ${job.message}`;
        el.btnStartExport.classList.remove("hidden");
      }
    } catch (err) {
      console.error("Poll error:", err);
    }
  }, 1000);
}

// ==========================================================================
// Project Persistence (Save & Load)
// ==========================================================================
function markProjectDirty() {
  el.saveStatus.textContent = "Unsaved Changes";
  el.saveStatus.style.color = "#f59e0b";
}

async function saveProject() {
  el.saveStatus.textContent = "Saving...";
  const projectData = {
    projectName: state.projectName,
    aspectRatio: state.aspectRatio,
    resolution: state.resolution,
    duration: state.duration,
    clips: state.clips,
    subtitles: state.subtitles,
    colorPreset: state.colorPreset,
    colorAdjustments: state.colorAdjustments,
    activeEffects: state.activeEffects,
    audioMixer: state.audioMixer
  };

  try {
    const res = await fetch("/api/project/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_name: state.projectName,
        project_data: projectData
      })
    });
    const result = await res.json();
    if (result.status === "success") {
      el.saveStatus.textContent = "Saved";
      el.saveStatus.style.color = "#10b981";
    }
  } catch (err) {
    el.saveStatus.textContent = "Save Failed";
    el.saveStatus.style.color = "#ef4444";
  }
}

async function loadDefaultOrSavedProject() {
  try {
    const res = await fetch(`/api/project/load/${state.projectName}`);
    if (res.ok) {
      const data = await res.json();
      if (data.status === "success" && data.project_data) {
        const p = data.project_data;
        state.aspectRatio = p.aspectRatio || "9:16";
        state.duration = p.duration || 15.0;
        state.clips = p.clips || [];
        state.subtitles = p.subtitles || [];
        state.colorPreset = p.colorPreset || "teal_orange";
        state.colorAdjustments = p.colorAdjustments || state.colorAdjustments;
        state.audioMixer = p.audioMixer || state.audioMixer;
        setAspectRatio(state.aspectRatio);
        return;
      }
    }
  } catch (e) {
    // Fallback to sample setup
  }

  // If no saved project exists, populate starter clips from footage
  const sampleVideos = state.mediaLibrary.filter(f => f.type === "video");
  const sampleAudio = state.mediaLibrary.filter(f => f.type === "audio");

  if (sampleVideos.length > 0) {
    let t = 0;
    sampleVideos.slice(0, 3).forEach((vid, i) => {
      const dur = 4.0;
      state.clips.push({
        id: `clip_init_${i}`,
        trackId: "track-video-1",
        name: vid.name,
        path: vid.path,
        startTime: t,
        duration: dur,
        sourceIn: 0.0,
        sourceDuration: vid.duration || 5.0,
        type: "video",
        transition: i > 0 ? "crossfade" : "none",
        volume: 1.0
      });
      t += dur;
    });

    if (sampleAudio.length > 0) {
      state.clips.push({
        id: `clip_init_audio`,
        trackId: "track-audio-2",
        name: sampleAudio[0].name,
        path: sampleAudio[0].path,
        startTime: 0.0,
        duration: t,
        sourceIn: 0.0,
        sourceDuration: sampleAudio[0].duration || 15.0,
        type: "audio",
        transition: "none",
        volume: 0.75
      });
    }

    state.duration = t;
    state.subtitles = [
      { start: 0.2, end: 1.5, word: "EXPLORE" },
      { start: 1.6, end: 3.0, word: "THE JOURNEY" },
      { start: 4.2, end: 6.0, word: "CINEMATIC MOMENTS" },
      { start: 7.5, end: 11.0, word: "REELSTUDIO PRO" }
    ];
  }
}

// Start app on DOMContentLoaded
window.addEventListener("DOMContentLoaded", initApp);
