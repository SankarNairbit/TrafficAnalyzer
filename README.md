# Traffic Analyzer

A Python application that processes a public traffic camera livestream in real time,
detects and counts vehicles by type, generates traffic events, and stores the data
in CSV format for Big Data analysis.

---

## Project Overview

This project was developed as part of the **Postgraduate Program in IoT & Big Data**.

The application reads a public traffic camera livestream, uses YOLOv8 to detect
vehicles frame by frame, classifies them by type (car, truck, bus, motorcycle,
bicycle), generates meaningful traffic events, and stores all data with timestamps
to a structured CSV file for further analysis.

**Stream source used:** https://www.youtube.com/watch?v=1xl0hX-nF2E

---

## What It Does

| Part | Description |
|------|-------------|
| 1 | Opens a public traffic camera livestream (YouTube or direct URL) |
| 2 | Detects and counts vehicles per type using YOLOv8 |
| 3 | Generates events: TRAFFIC_JAM, HEAVY_VEHICLE_PEAK, QUIET_PERIOD, RUSH_HOUR_START/END, SUSTAINED_FLOW, DEAD_ZONE, MIXED_TRAFFIC, SESSION_PEAK |
| 4 | Stores all data with timestamps, rolling averages, and time context to a CSV file |
| 5 | Data is structured for use in IoT / Big Data pipelines |

---

## Project Structure

```
TrafficAnalyzer/
├── main.py            # Main application loop and display overlay
├── config.py          # Configuration and all event thresholds
├── stream.py          # Stream opening (YouTube via yt-dlp, or direct URL)
├── detector.py        # YOLOv8 vehicle detection wrapper
├── events.py          # Rule-based event generation logic
├── storage.py         # CSV data writing with rolling averages
├── requirements.txt   # Python dependencies
├── README.md          # This file
└── data/              # Auto-created folder — stores traffic_data.csv
```

---

## Installation

### Prerequisites
- Python 3.9 or higher
- Git (to clone the repository)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd TrafficAnalyzer
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify yt-dlp can access the stream

```bash
yt-dlp -g "https://www.youtube.com/watch?v=1xl0hX-nF2E"
```

If this returns one or more `https://` URLs, the stream is accessible and you are ready to run.

---

## Configuration

All settings are in `config.py`. Key options:

| Setting | Default | Description |
|---|---|---|
| `STREAM_SOURCE` | YouTube URL | The livestream to process |
| `USE_YOUTUBE` | `True` | Set to `False` for direct RTSP/HTTP URLs |
| `FRAME_SAMPLE_INTERVAL` | `30` | Process every Nth frame (~1 sample/sec at 30fps) |
| `CONFIDENCE` | `0.35` | YOLO detection confidence threshold |
| `JAM_THRESHOLD` | `8` | Vehicles needed to start counting toward a jam |
| `JAM_CONSECUTIVE` | `3` | Consecutive samples above threshold to declare a jam |
| `QUIET_THRESHOLD` | `2` | Vehicles at or below this count = quiet period |
| `RUSH_DELTA_THRESHOLD` | `6` | Change in vehicle count to trigger rush hour events |
| `SUSTAINED_MEDIUM_COUNT` | `5` | Consecutive medium-density frames to trigger SUSTAINED_FLOW |
| `LONG_QUIET_MINUTES` | `2` | Quiet frames needed to trigger DEAD_ZONE |
| `HEAVY_RATIO_THRESHOLD` | `0.3` | Trucks+buses fraction to trigger HEAVY_VEHICLE_PEAK |

To use a different stream, update `STREAM_SOURCE`. To use a direct RTSP or HTTP
camera URL instead of YouTube, set `USE_YOUTUBE = False`.

---

## Running

```bash
python main.py
```

- A video window will open showing the live stream with detection boxes overlaid
- Vehicle counts and active events are shown on screen
- Press `q` to quit
- Data is automatically saved to `data/traffic_data.csv`

---

## Output Data (CSV)

Each row represents one sampled frame.

| Column | Description |
|---|---|
| `timestamp` | ISO 8601 datetime of the sample |
| `frame_number` | Frame index in the stream |
| `bicycle` | Number of bicycles detected |
| `car` | Number of cars detected |
| `motorcycle` | Number of motorcycles detected |
| `bus` | Number of buses detected |
| `truck` | Number of trucks detected |
| `total_vehicles` | Sum of all vehicle types |
| `density_level` | `low` / `medium` / `high` based on total count |
| `rolling_avg_5` | 5-sample rolling average of total vehicles |
| `hour_of_day` | Hour extracted from timestamp (0–23) |
| `day_of_week` | Full weekday name (e.g. `Tuesday`) |
| `events` | Pipe-separated list of triggered events (empty if none) |

---

## Events

| Event | Trigger Condition |
|---|---|
| `TRAFFIC_JAM` | Total vehicles ≥ 8 for 3 or more consecutive samples |
| `HEAVY_VEHICLE_PEAK` | Trucks + buses make up ≥ 30% of all detected vehicles |
| `QUIET_PERIOD` | Total vehicles ≤ 2 |
| `RUSH_HOUR_START` | Sudden increase of ≥ 6 vehicles between consecutive samples |
| `RUSH_HOUR_END` | Sudden decrease of ≥ 6 vehicles between consecutive samples |
| `SUSTAINED_FLOW` | Medium-density traffic for 5 or more consecutive samples |
| `DEAD_ZONE` | Extended quiet period beyond the LONG_QUIET_MINUTES threshold |
| `MIXED_TRAFFIC` | 3 or more distinct vehicle types visible in the same frame |
| `SESSION_PEAK` | Highest vehicle count recorded so far in the current session |

All thresholds are configurable in `config.py`.

---

## Big Data Pipeline

```
Public Livestream
      ↓
Frame Sampling (OpenCV)
      ↓
Object Detection (YOLOv8 — edge inference)
      ↓
Feature Extraction (counts, density, rolling average)
      ↓
Event Generation (threshold-based rules)
      ↓
Local CSV / MQTT Broker
      ↓
Cloud Storage (S3, Azure Blob, InfluxDB, TimescaleDB)
      ↓
Big Data Processing (Spark, Pandas, Kafka Streams)
      ↓
Dashboard / Alerts (Grafana, Power BI)
```

The Python script acts as an **IoT edge device** — it runs local inference and
only publishes compact event messages upstream (not raw video), exactly how real
smart city sensors operate.

### Who uses this data?

- **City traffic departments** — identify congestion hotspots and optimise signal timing
- **Logistics companies** — plan delivery windows around `HEAVY_VEHICLE_PEAK` hours
- **Urban planners** — correlate `RUSH_HOUR_START` patterns with public transport schedules
- **Road maintenance teams** — prioritise repairs based on heavy vehicle frequency
- **Retailers near roads** — understand customer traffic patterns using `hour_of_day` and `day_of_week`

### Scalability considerations

- Replace CSV with **InfluxDB** or **TimescaleDB** for efficient time-series queries
- Publish events via **MQTT** for real-time dashboard updates (e.g. Grafana)
- Multiple camera feeds can be processed in parallel using Python `multiprocessing`
- Deploy on a **Raspberry Pi** or edge device for on-site low-latency processing
- Containerise with **Docker** for repeatable cloud deployment

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.9+ | Core programming language |
| OpenCV | Video capture and frame display |
| YOLOv8 (Ultralytics) | Real-time vehicle detection |
| yt-dlp | YouTube stream URL extraction |
| CSV (stdlib) | Structured data storage |

---

## Known Issues & Troubleshooting

**`[WinError 2] The system cannot find the file specified`**  
→ `yt-dlp` is not installed or not in PATH. Run: `pip install yt-dlp`

**`No supported JavaScript runtime could be found`**  
→ Install Node.js from https://nodejs.org/ and restart your terminal.

**`SSL: CERTIFICATE_VERIFY_FAILED`**  
→ Run: `pip install --upgrade certifi`

**`No video formats found`**  
→ Update yt-dlp: `pip install -U yt-dlp`

**No vehicles detected**  
→ Try lowering `CONFIDENCE` in `config.py` (e.g. to `0.25`). The camera angle
may also not be suitable if vehicles appear too small or at a head-on angle.

**`AttributeError: _medium_streak` or `_quiet_streak`**  
→ These attributes must be initialised in `EventGenerator.__init__()`. Ensure
you are running the latest version of `events.py`.

---

## License

This project is for educational purposes as part of the IoT & Big Data postgraduate program.
