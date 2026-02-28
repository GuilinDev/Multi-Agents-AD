"""Multi-session persistent memory for patient conversations."""

import os
import json
import time
from agents import llm_call

DATA_DIR = os.path.join(os.path.dirname(__file__), "patient_data")
os.makedirs(DATA_DIR, exist_ok=True)


def _memory_path(patient_id: str) -> str:
    return os.path.join(DATA_DIR, f"{patient_id}_memory.json")


def load_memory(patient_id: str) -> dict:
    path = _memory_path(patient_id)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {
        "long_term_memories": [],
        "session_history": [],
        "preferences_learned": [],
    }


def save_memory(patient_id: str, memory: dict):
    path = _memory_path(patient_id)
    with open(path, "w") as f:
        json.dump(memory, f, indent=2)


def extract_and_save_memories(patient_id: str, therapy_history: list, memory: dict):
    """Use LLM to extract memorable facts from recent conversation."""
    if len(therapy_history) < 2:
        return memory

    recent = therapy_history[-10:]
    context = "\n".join(
        f"{'Patient' if m['role']=='user' else 'Companion'}: {m['content']}"
        for m in recent
    )

    system = """Extract key facts, stories, and preferences from this therapy conversation 
with an Alzheimer's patient. Output JSON:
{
  "new_memories": ["fact1", "fact2"],
  "new_preferences": ["pref1"]
}
Only include genuinely new/interesting facts. Output ONLY valid JSON."""

    raw = llm_call(system, [{"role": "user", "content": context}], temperature=0.3)
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(cleaned)
        for m in data.get("new_memories", []):
            if m not in memory["long_term_memories"]:
                memory["long_term_memories"].append(m)
        for p in data.get("new_preferences", []):
            if p not in memory["preferences_learned"]:
                memory["preferences_learned"].append(p)
    except (json.JSONDecodeError, IndexError):
        pass

    save_memory(patient_id, memory)
    return memory


def save_session_summary(patient_id: str, memory: dict, turn_count: int, topics: list[str], summary: str):
    """Save a session entry."""
    memory["session_history"].append({
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "summary": summary,
        "turns": turn_count,
        "key_topics": topics,
    })
    # Keep last 50 sessions
    memory["session_history"] = memory["session_history"][-50:]
    save_memory(patient_id, memory)


def format_memory_prompt(memory: dict) -> str:
    """Format memories for injection into therapy system prompt."""
    parts = []
    if memory["long_term_memories"]:
        facts = "; ".join(memory["long_term_memories"][-15:])
        parts.append(f"You remember from previous sessions: {facts}")
    if memory["preferences_learned"]:
        prefs = "; ".join(memory["preferences_learned"][-10:])
        parts.append(f"You've learned these preferences: {prefs}")
    if memory["session_history"]:
        last = memory["session_history"][-1]
        parts.append(f"Last session ({last['date']}): {last['summary'][:200]}")
    return "\n".join(parts)
