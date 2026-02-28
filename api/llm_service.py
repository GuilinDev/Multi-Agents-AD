"""
LLM Service — Groq API wrapper for STT, event parsing, and summarization.
"""

import os
import json
import io
from groq import Groq

_client = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Transcribe audio bytes using Groq Whisper."""
    client = _get_client()
    transcription = client.audio.transcriptions.create(
        file=(filename, io.BytesIO(audio_bytes)),
        model="whisper-large-v3",
        language="en",
    )
    return transcription.text


async def parse_event(text: str) -> dict:
    """Parse a caregiver's event description into structured fields."""
    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a clinical event parser for a dementia care facility.\n"
                    "Given a caregiver's description of a behavioral event, extract:\n"
                    "- event_type: one of [Agitation, Sundowning, Refusal, Wandering, Fall, Aggression, Confusion, Sleep_Disturbance, Other]\n"
                    "- severity: one of [Low, Medium, High, Critical]\n"
                    "- location: where the event occurred (string, use 'Unknown' if not mentioned)\n"
                    "- trigger: identified trigger if mentioned (string, use 'Unknown' if not mentioned)\n"
                    "- summary: 1-2 sentence summary\n\n"
                    "Respond in JSON only. No markdown, no explanation."
                ),
            },
            {"role": "user", "content": text},
        ],
        temperature=0.1,
        max_tokens=300,
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
    return json.loads(raw)


async def summarize_events(events_data: list[dict]) -> dict:
    """Summarize a list of events for shift handoff. Returns {summary, pending_items}."""
    client = _get_client()
    events_text = json.dumps(events_data, indent=2, default=str)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a clinical shift handoff assistant for a dementia care facility.\n"
                    "Given a list of behavioral events from the current shift, produce:\n"
                    "1. A per-patient summary of events and interventions\n"
                    "2. A list of pending follow-up items for the next shift\n\n"
                    "Respond in JSON with keys:\n"
                    "- events_summary: list of {patient_name, patient_id, summary}\n"
                    "- pending_items: list of {patient_name, patient_id, item, priority}\n\n"
                    "JSON only. No markdown."
                ),
            },
            {"role": "user", "content": events_text},
        ],
        temperature=0.2,
        max_tokens=1000,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
    return json.loads(raw)
