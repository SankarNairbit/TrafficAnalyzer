"""
config.py
---------
Central configuration for the Traffic Analyzer application.
All tunable parameters — stream source, model path, frame sampling rate,
event thresholds, and output settings — are defined here so that no
magic numbers are scattered across other modules.
"""

# ── Stream source ──────────────────────────────────────────────────────────────
# Set USE_YOUTUBE = False and put a direct URL if you have an RTSP/HTTP stream.
STREAM_SOURCE = "https://www.youtube.com/watch?v=u7GyFcQJs98"
USE_YOUTUBE = True

#"https://www.youtube.com/watch?v=1xl0hX-nF2E"

# ── Model ─────────────────────────────────────────────────────────────────────
MODEL_PATH = "yolov8n.pt"

# ── COCO class IDs for vehicles (used by YOLOv8 out of the box) ───────────────
VEHICLE_CLASSES = {
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

# ── Frame sampling ────────────────────────────────────────────────────────────
# Process every Nth frame to reduce CPU load (30 = ~1 sample/second at 30fps)
FRAME_SAMPLE_INTERVAL = 30

# ── Output ────────────────────────────────────────────────────────────────────
CSV_OUTPUT_DIR = "data"
CSV_FILENAME = "traffic_data.csv"

# ── Event thresholds ──────────────────────────────────────────────────────────
JAM_THRESHOLD = 8          # Total vehicles visible to trigger jam detection
JAM_CONSECUTIVE = 3         # How many consecutive samples before declaring jam
HEAVY_RATIO_THRESHOLD = 0.3 # Fraction of trucks+buses to trigger heavy peak event
QUIET_THRESHOLD = 2         # Total vehicles at or below this = quiet period
RUSH_DELTA_THRESHOLD = 6    # Sudden change in count to trigger rush hour event
SUSTAINED_MEDIUM_COUNT = 5 # new: N consecutive medium-density frames
LONG_QUIET_MINUTES = 2     # new: quiet for >2 min = DEAD_ZONE
MOTION_OVERLAP_THRESHOLD = 0.20  # Fraction of bbox pixels that must show motion to count as moving

# ── Display ───────────────────────────────────────────────────────────────────
SHOW_WINDOW = True
WINDOW_TITLE = "Traffic Analyzer - Vehicle Counter"
DISPLAY_WIDTH = 1280   # Resize window to this width (height scales automatically)

# ── Detection confidence ──────────────────────────────────────────────────────
CONFIDENCE = 0.35