"""
events.py
---------
Rule-based event generator for the Traffic Analyzer.
On each sampled frame, EventGenerator.check() evaluates the current
vehicle counts and returns a list of triggered event names, such as:
  TRAFFIC_JAM, HEAVY_VEHICLE_PEAK, QUIET_PERIOD, RUSH_HOUR_START,
  RUSH_HOUR_END, SUSTAINED_FLOW, DEAD_ZONE, MIXED_TRAFFIC, SESSION_PEAK.
All thresholds are sourced from config.py.
"""

from config import (
    JAM_THRESHOLD, JAM_CONSECUTIVE,
    HEAVY_RATIO_THRESHOLD, QUIET_THRESHOLD,
    RUSH_DELTA_THRESHOLD,SUSTAINED_MEDIUM_COUNT, LONG_QUIET_MINUTES,
)


class EventGenerator:
    def __init__(self):
        self._jam_streak = 0
        self._medium_streak = 0
        self._quiet_streak = 0
        self._session_max = 0
        self._prev_total = 0

    def check(self, counts: dict) -> list:
        """
        Evaluate vehicle counts and return a list of triggered event names.

        Events:
          TRAFFIC_JAM         - sustained high vehicle density
          HEAVY_VEHICLE_PEAK  - truck+bus ratio exceeds threshold
          QUIET_PERIOD        - very few vehicles visible
          RUSH_HOUR_START     - sudden large increase in vehicles
          RUSH_HOUR_END       - sudden large decrease in vehicles
        """
        events = []

        total = sum(counts.values())
        heavy = counts.get("truck", 0) + counts.get("bus", 0)

        # Traffic jam: sustained high density
        if total >= JAM_THRESHOLD:
            self._jam_streak += 1
        else:
            self._jam_streak = 0

        if self._jam_streak >= JAM_CONSECUTIVE:
            events.append("TRAFFIC_JAM")

        # Heavy vehicle peak
        if total > 0 and (heavy / total) >= HEAVY_RATIO_THRESHOLD:
            events.append("HEAVY_VEHICLE_PEAK")

        # Quiet period
        if total <= QUIET_THRESHOLD:
            self._quiet_streak += 1
            self._medium_streak = 0
            events.append("QUIET_PERIOD")
        else:
            self._quiet_streak = 0

        # Medium density streak (not a jam, not quiet)
        if QUIET_THRESHOLD < total < JAM_THRESHOLD:
            self._medium_streak += 1
        elif total >= JAM_THRESHOLD or total <= QUIET_THRESHOLD:
            self._medium_streak = 0

        # Rush hour transitions
        delta = total - self._prev_total
        if delta >= RUSH_DELTA_THRESHOLD:
            events.append("RUSH_HOUR_START")
        elif delta <= -RUSH_DELTA_THRESHOLD:
            events.append("RUSH_HOUR_END")

        
        # SUSTAINED_FLOW - medium traffic for X consecutive samples (not a jam, but steady)
        if self._medium_streak >= SUSTAINED_MEDIUM_COUNT:
            events.append("SUSTAINED_FLOW")

        # DEAD_ZONE - extended quiet (longer than QUIET_PERIOD chain)
        if self._quiet_streak >= LONG_QUIET_MINUTES:
            events.append("DEAD_ZONE")

        # VEHICLE_DIVERSITY - multiple types visible at once (realistic urban footprint)
        types_seen = sum(1 for v in counts.values() if v > 0)
        if types_seen >= 3:
            events.append("MIXED_TRAFFIC")

        # PEAK_FRAME - highest count seen in the session
        if total > self._session_max:
            self._session_max = total
            events.append("SESSION_PEAK")

        

        self._prev_total = total
        return events