"""
main.py
-------
Entry point for the Traffic Analyzer application.
Orchestrates the full pipeline:
  1. Opens a public livestream (YouTube or RTSP/HTTP) via stream.py
  2. Samples every Nth frame using the interval set in config.py
  3. Runs YOLOv8 vehicle detection on each sampled frame (detector.py)
  4. Evaluates rule-based traffic events (events.py)
  5. Persists results to CSV (storage.py)
  6. Displays the annotated frame with live overlays (OpenCV window)
Press 'q' in the display window or Ctrl+C in the terminal to stop.
"""

import sys
import cv2

from config import (
    STREAM_SOURCE, USE_YOUTUBE, MODEL_PATH,
    FRAME_SAMPLE_INTERVAL, SHOW_WINDOW, WINDOW_TITLE, DISPLAY_WIDTH,
)
from stream import open_stream
from detector import VehicleDetector
from events import EventGenerator
from storage import DataStore


def resize_for_display(frame):
    """Scale frame down to DISPLAY_WIDTH while preserving aspect ratio."""
    h, w = frame.shape[:2]
    if w <= DISPLAY_WIDTH:
        return frame
    scale = DISPLAY_WIDTH / w
    return cv2.resize(frame, (DISPLAY_WIDTH, int(h * scale)), interpolation=cv2.INTER_AREA)


def draw_overlay(frame, counts: dict, events: list):
    """Draw vehicle counts and active events onto the frame."""
    y = 30
    total = sum(counts.values())

    cv2.putText(frame, f"Total vehicles: {total}",
                (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    y += 28

    for name, count in counts.items():
        if count > 0:
            cv2.putText(frame, f"  {name.capitalize()}: {count}",
                        (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            y += 24

    for event in events:
        color = (0, 0, 255) if "JAM" in event else (0, 165, 255)
        cv2.putText(frame, f"EVENT: {event}",
                    (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        y += 28


def main():
    detector = VehicleDetector(MODEL_PATH)
    event_gen = EventGenerator()
    store = DataStore()

    print("Opening stream...")
    cap = open_stream(STREAM_SOURCE, USE_YOUTUBE)
    print("Stream opened. Press 'q' to quit.")

    frame_number = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("No frame received. The stream may have ended.")
                break

            frame_number += 1

            # Skip frames that are not sample frames
            if frame_number % FRAME_SAMPLE_INTERVAL != 0:
                if SHOW_WINDOW:
                    cv2.imshow(WINDOW_TITLE, resize_for_display(frame))
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
                continue

            counts, annotated_frame = detector.detect(frame)
            events = event_gen.check(counts)
            store.write(frame_number, counts, events)

            if events:
                print(f"[Frame {frame_number}] Events: {events} | Counts: {counts}")
            else:
                print(f"[Frame {frame_number}] Counts: {counts}")

            if SHOW_WINDOW:
                draw_overlay(annotated_frame, counts, events)
                cv2.imshow(WINDOW_TITLE, resize_for_display(annotated_frame))
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Session ended. Data saved to data/traffic_data.csv")


if __name__ == "__main__":
    main()