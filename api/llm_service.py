"""
LLM Service — Multi-provider wrapper for STT, event parsing, and summarization.

Supports:
  - Groq API (cloud, fast inference)
  - Ollama (local, zero cost)

Set via environment variables:
  LLM_PROVIDER=groq|ollama  (default: groq)
  LLM_MODEL=model-name      (default: depends on provider)
  OLLAMA_BASE_URL=http://localhost:11434  (for ollama)
  GROQ_API_KEY=...           (for groq)
"""

import os
import json
import io
import logging

logger = logging.getLogger(__name__)

# Provider config
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Default models per provider
DEFAULT_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "ollama": "nemotron-3-nano:30b",
}

_client = None


def _get_model() -> str:
    """Get the configured model name."""
    return LLM_MODEL or DEFAULT_MODELS.get(LLM_PROVIDER, "llama-3.3-70b-versatile")


def _get_client():
    """Get or create the LLM client based on provider."""
    global _client
    if _client is not None:
        return _client

    if LLM_PROVIDER == "ollama":
        from openai import OpenAI
        _client = OpenAI(
            base_url=f"{OLLAMA_BASE_URL}/v1",
            api_key="ollama",  # ollama doesn't need a real key
        )
        logger.info(f"LLM: Using Ollama at {OLLAMA_BASE_URL} with model {_get_model()}")
    else:
        from groq import Groq
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
        logger.info(f"LLM: Using Groq with model {_get_model()}")

    return _client


def _chat_completion(messages: list, temperature: float = 0.1, max_tokens: int = 300) -> str:
    """Unified chat completion across providers."""
    client = _get_client()
    model = _get_model()

    # Ollama models with reasoning (e.g. nemotron, deepseek-r1) need more tokens
    # because reasoning tokens count against max_tokens in some configs
    effective_max = max_tokens
    if LLM_PROVIDER == "ollama":
        effective_max = max(max_tokens * 3, 1000)  # Give 3x headroom for local models

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=effective_max,
    )
    content = response.choices[0].message.content
    if not content:
        logger.warning(f"LLM returned empty content for model {model}")
        return ""
    return content.strip()


def _strip_markdown_fences(raw: str) -> str:
    """Strip markdown code fences from LLM output."""
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
    return raw


def _robust_json_parse(raw: str) -> dict | list:
    """Try hard to extract JSON from LLM output."""
    raw = _strip_markdown_fences(raw)
    # Try direct parse first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Try to find JSON object/array in the text
    import re
    # Find first { ... } or [ ... ]
    for pattern in [r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', r'\[.*\]']:
        match = re.search(pattern, raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                continue
    # Last resort: try fixing common issues
    raw_fixed = raw.replace("'", '"').replace("True", "true").replace("False", "false").replace("None", "null")
    try:
        return json.loads(raw_fixed)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON from LLM output: {raw[:200]}")
        raise


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Transcribe audio bytes using Groq Whisper (Groq-only, falls back to placeholder for ollama)."""
    if LLM_PROVIDER == "ollama":
        logger.warning("Audio transcription not supported with Ollama, returning placeholder")
        return "[Audio transcription requires Groq provider]"

    from groq import Groq
    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
    transcription = groq_client.audio.transcriptions.create(
        file=(filename, io.BytesIO(audio_bytes)),
        model="whisper-large-v3",
        language="en",
    )
    return transcription.text


async def parse_event(text: str) -> dict:
    """Parse a caregiver's event description into structured fields."""
    raw = _chat_completion(
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
    raw = _strip_markdown_fences(raw)
    try:
        return _robust_json_parse(raw)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"parse_event fallback — raw: {raw[:200]}, error: {e}")
        return {
            "event_type": "Other",
            "severity": "Medium",
            "location": "Unknown",
            "trigger": "Unknown",
            "summary": text[:200],
        }


async def summarize_protocols(event_description: str, raw_protocols: list[dict]) -> list[dict]:
    """Summarize raw protocol chunks into actionable steps for caregivers."""
    protocols_text = ""
    for i, p in enumerate(raw_protocols):
        protocols_text += f"\n--- Protocol {i+1} [Source: {p.get('source','Unknown')}, Page: {p.get('page',0)}] ---\n"
        protocols_text += p.get("text", p.get("text_preview", ""))[:500] + "\n"

    raw = _chat_completion(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a clinical protocol summarizer for dementia caregivers.\n"
                    "Given a behavioral event description and relevant protocol excerpts, produce actionable steps.\n\n"
                    "Rules:\n"
                    "- For each protocol, produce 2-3 specific action steps (one sentence each)\n"
                    "- Keep language simple and direct — these are for frontline caregivers\n"
                    "- Preserve the source reference\n"
                    "- If the event is a POSITIVE report (no behavioral issues), respond with a single entry:\n"
                    '  [{"source":"N/A","page":0,"steps":["No specific protocols needed. Continue monitoring."]}]\n\n'
                    "Respond in JSON only: list of {source, page, steps: [str]}\n"
                    "No markdown, no explanation."
                ),
            },
            {
                "role": "user",
                "content": f"Event: {event_description}\n\nProtocols:\n{protocols_text}",
            },
        ],
        temperature=0.1,
        max_tokens=500,
    )
    raw = _strip_markdown_fences(raw)
    try:
        return _robust_json_parse(raw)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"summarize_protocols fallback — error: {e}")
        return [{"source": "N/A", "page": 0, "steps": ["Unable to parse protocol summary. Review manually."]}]


async def summarize_events(events_data: list[dict]) -> dict:
    """Summarize a list of events for shift handoff. Returns {summary, pending_items}."""
    events_text = json.dumps(events_data, indent=2, default=str)
    raw = _chat_completion(
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
    raw = _strip_markdown_fences(raw)
    try:
        return _robust_json_parse(raw)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"summarize_events fallback — error: {e}")
        return {"events_summary": [], "pending_items": []}
