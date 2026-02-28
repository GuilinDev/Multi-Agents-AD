"""Cognitive trend tracking and visualization."""

import os
import json
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "patient_data")
os.makedirs(DATA_DIR, exist_ok=True)

EMOTION_MAP = {"happy": 5, "calm": 4, "nostalgic": 3, "confused": 2, "anxious": 1, "frustrated": 0}
MEMORY_MAP = {"clear": 3, "partial": 2, "confused": 1, "fabricated": 0}
ENGAGEMENT_MAP = {"high": 2, "medium": 1, "low": 0}


def _trends_path(patient_id: str) -> str:
    return os.path.join(DATA_DIR, f"{patient_id}_trends.json")


def load_trends(patient_id: str) -> list:
    path = _trends_path(patient_id)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


def save_trend_entry(patient_id: str, report: dict):
    """Save a monitor report as a trend data point."""
    trends = load_trends(patient_id)
    entry = {
        "session_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "turn": report.get("turn", 0),
        "emotion": report.get("emotion", "unknown"),
        "memory_quality": report.get("memory_quality", "unknown"),
        "engagement": report.get("engagement", "medium"),
        "scores": {
            "emotion": EMOTION_MAP.get(report.get("emotion", ""), 2),
            "memory_quality": MEMORY_MAP.get(report.get("memory_quality", ""), 1),
            "engagement": ENGAGEMENT_MAP.get(report.get("engagement", ""), 1),
        },
        "risk_flags": report.get("risk_flags", ""),
    }
    trends.append(entry)
    # Keep last 500 entries
    trends = trends[-500:]
    with open(_trends_path(patient_id), "w") as f:
        json.dump(trends, f, indent=2)
    return trends


def create_trend_chart(patient_id: str, figsize=(8, 4)) -> plt.Figure | None:
    """Create a matplotlib figure of cognitive trends."""
    trends = load_trends(patient_id)
    if len(trends) < 2:
        return None

    turns = list(range(len(trends)))
    emotions = [t["scores"]["emotion"] for t in trends]
    memory = [t["scores"]["memory_quality"] for t in trends]
    engagement = [t["scores"]["engagement"] for t in trends]

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(turns, emotions, "o-", color="#4CAF50", label="Emotion (0-5)", linewidth=2, markersize=4)
    ax.plot(turns, memory, "s-", color="#2196F3", label="Memory Quality (0-3)", linewidth=2, markersize=4)
    ax.plot(turns, engagement, "^-", color="#9C27B0", label="Engagement (0-2)", linewidth=2, markersize=4)

    ax.set_xlabel("Turn")
    ax.set_ylabel("Score")
    ax.set_title("Cognitive Trends Over Time")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.5, 5.5)
    fig.tight_layout()
    return fig


def get_alert_history(patient_id: str) -> list[dict]:
    """Get all risk flags from trends."""
    trends = load_trends(patient_id)
    alerts = []
    for t in trends:
        if t.get("risk_flags"):
            alerts.append({
                "date": t["session_date"],
                "turn": t["turn"],
                "flag": t["risk_flags"],
                "emotion": t["emotion"],
            })
    return alerts
