"""
stream.py
---------
Handles opening video streams for the Traffic Analyzer.
Supports both direct RTSP/HTTP URLs and YouTube livestreams.
For YouTube sources, yt-dlp is used to resolve the raw stream URL
before handing a cv2.VideoCapture object back to the caller.
"""

import subprocess
import cv2


def get_youtube_stream_url(youtube_url: str) -> str:
    cmd = ["yt-dlp", "-g", youtube_url]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp error:\n{result.stderr}")

    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("http"):
            return line

    raise RuntimeError("No valid stream URL found.")


def open_stream(source: str, use_youtube: bool) -> cv2.VideoCapture:
    if use_youtube:
        print("Fetching YouTube stream URL via yt-dlp...")
        source = get_youtube_stream_url(source)
        print("Stream URL obtained.")

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open stream: {source}")

    return cap