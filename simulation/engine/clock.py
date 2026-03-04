"""
Simulation Clock — manages virtual time for the nursing home simulation.
Accelerates real time so an 8-hour shift runs in minutes.
"""
from datetime import datetime, timedelta
from typing import Optional, Callable, List
import asyncio


class SimulationClock:
    """Virtual clock that accelerates time for simulation."""

    def __init__(
        self,
        start_time: datetime = None,
        speed_multiplier: float = 60.0,  # 1 real second = 1 virtual minute
    ):
        self.start_time = start_time or datetime(2026, 3, 3, 7, 0, 0)  # 7:00 AM
        self.current_time = self.start_time
        self.speed_multiplier = speed_multiplier
        self.running = False
        self._callbacks: List[dict] = []  # scheduled callbacks

    @property
    def hour(self) -> int:
        return self.current_time.hour

    @property
    def time_of_day(self) -> str:
        h = self.hour
        if 6 <= h < 12:
            return "morning"
        elif 12 <= h < 17:
            return "afternoon"
        elif 17 <= h < 21:
            return "evening"
        else:
            return "night"

    @property
    def elapsed_hours(self) -> float:
        return (self.current_time - self.start_time).total_seconds() / 3600

    def advance(self, minutes: int = 30):
        """Advance clock by N virtual minutes."""
        self.current_time += timedelta(minutes=minutes)

    def schedule_at(self, time: datetime, callback: Callable, label: str = ""):
        """Schedule a callback at a specific virtual time."""
        self._callbacks.append({
            "time": time,
            "callback": callback,
            "label": label,
            "fired": False,
        })

    def schedule_recurring(self, interval_minutes: int, callback: Callable, label: str = ""):
        """Schedule a recurring callback every N virtual minutes."""
        self._callbacks.append({
            "interval": interval_minutes,
            "callback": callback,
            "label": label,
            "last_fired": self.start_time,
        })

    async def check_callbacks(self):
        """Check and fire any due callbacks."""
        for cb in self._callbacks:
            if "time" in cb and not cb.get("fired"):
                if self.current_time >= cb["time"]:
                    await cb["callback"]()
                    cb["fired"] = True
            elif "interval" in cb:
                elapsed = (self.current_time - cb["last_fired"]).total_seconds() / 60
                if elapsed >= cb["interval"]:
                    await cb["callback"]()
                    cb["last_fired"] = self.current_time

    def format_time(self) -> str:
        return self.current_time.strftime("%H:%M")

    def format_datetime(self) -> str:
        return self.current_time.strftime("%Y-%m-%d %H:%M")

    def is_shift_change(self) -> Optional[str]:
        """Check if current time is a shift change."""
        h, m = self.hour, self.current_time.minute
        if h == 7 and m == 0:
            return "day_start"
        elif h == 15 and m == 0:
            return "evening_start"
        elif h == 23 and m == 0:
            return "night_start"
        return None

    def __repr__(self):
        return f"SimClock({self.format_datetime()}, speed={self.speed_multiplier}x)"
