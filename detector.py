"""
detector.py
-----------
Wraps the YOLOv8 model to perform vehicle detection on individual frames.
Each call to detect() runs inference on a single frame and returns:
  - a dict of per-vehicle-type counts (bicycle, car, motorcycle, bus, truck)
    (only moving vehicles are counted — parked/stationary vehicles are excluded)
  - the frame annotated with bounding boxes, ready for display.
"""

import cv2
from ultralytics import YOLO
from config import VEHICLE_CLASSES, CONFIDENCE, MOTION_OVERLAP_THRESHOLD


class VehicleDetector:
    def __init__(self, model_path: str):
        print(f"Loading YOLO model: {model_path}")
        self.model = YOLO(model_path)
        # MOG2 background subtractor builds a model of the static scene.
        # Pixels that differ from the background (i.e. moving objects) become white.
        self._bg_sub = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=50, detectShadows=False
        )

    def detect(self, frame):
        """
        Run YOLO on a frame. Returns:
          counts      -- dict of {vehicle_type: count} for MOVING vehicles only
          annotated   -- frame with bounding boxes drawn
        """
        # Build the foreground/motion mask for this frame
        motion_mask = self._bg_sub.apply(frame)

        results = self.model(frame, verbose=False, conf=CONFIDENCE)
        counts = {name: 0 for name in VEHICLE_CLASSES.values()}

        if results[0].boxes is not None:
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                if cls_id not in VEHICLE_CLASSES:
                    continue

                # Clip bbox coords to frame bounds
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                x1 = max(0, x1); y1 = max(0, y1)
                x2 = min(frame.shape[1], x2); y2 = min(frame.shape[0], y2)

                roi = motion_mask[y1:y2, x1:x2]
                if roi.size == 0:
                    continue

                # Fraction of bbox pixels that are "in motion"
                motion_fraction = roi.mean() / 255.0
                if motion_fraction >= MOTION_OVERLAP_THRESHOLD:
                    counts[VEHICLE_CLASSES[cls_id]] += 1

        annotated = results[0].plot()
        return counts, annotated