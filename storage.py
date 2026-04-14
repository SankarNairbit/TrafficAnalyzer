"""
storage.py
----------
Handles persisting traffic data to a CSV file for the Traffic Analyzer.
Each sampled frame produces one row containing: timestamp, frame number,
per-vehicle-type counts, total vehicles, density label, a 5-sample rolling
average, hour of day, day of week, and any active event names.
The CSV file and its parent directory are created automatically on first run.
"""

import csv
import os
from collections import deque
from datetime import datetime
from config import CSV_OUTPUT_DIR, CSV_FILENAME

FIELDNAMES = [
    "timestamp", "frame_number",
    "bicycle", "car", "motorcycle", "bus", "truck",
    "total_vehicles", "density_level", "rolling_avg_5",
    "hour_of_day", "day_of_week", "events",
]


def _density_label(total: int) -> str:
    if total <= 2:
        return "low"
    elif total <= 10:
        return "medium"
    else:
        return "high"


class DataStore:
    def __init__(self):
        os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
        self._path = os.path.join(CSV_OUTPUT_DIR, CSV_FILENAME)
        self._recent_totals = deque(maxlen=5)  # rolling window of last 5 samples
        self._init_csv()
        print(f"Storing data to: {self._path}")

    def _init_csv(self):
        if not os.path.exists(self._path):
            with open(self._path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()

    def write(self, frame_number: int, counts: dict, events: list):
        total = sum(counts.values())
        now = datetime.now()

        self._recent_totals.append(total)
        rolling_avg = round(sum(self._recent_totals) / len(self._recent_totals), 2)

        row = {
            "timestamp": now.isoformat(),
            "frame_number": frame_number,
            "bicycle": counts.get("bicycle", 0),
            "car": counts.get("car", 0),
            "motorcycle": counts.get("motorcycle", 0),
            "bus": counts.get("bus", 0),
            "truck": counts.get("truck", 0),
            "total_vehicles": total,
            "density_level": _density_label(total),
            "rolling_avg_5": rolling_avg,
            "hour_of_day": now.hour,
            "day_of_week": now.strftime("%A"),
            "events": "|".join(events) if events else "",
        }
        with open(self._path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(row)