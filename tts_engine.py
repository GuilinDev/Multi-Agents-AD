"""Text-to-speech using edge-tts (free, no API key needed)."""

import asyncio
import os
import hashlib
import edge_tts

VOICE = "en-US-JennyNeural"  # Warm female voice, good for therapy context
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_cache")
os.makedirs(AUDIO_DIR, exist_ok=True)


async def _synthesize(text: str, output_path: str):
    communicate = edge_tts.Communicate(text, VOICE, rate="-10%")  # Slightly slower
    await communicate.save(output_path)


def text_to_speech(text: str) -> str:
    """Convert text to speech, return path to audio file."""
    # Cache by content hash
    h = hashlib.md5(text.encode()).hexdigest()[:12]
    path = os.path.join(AUDIO_DIR, f"{h}.mp3")
    if not os.path.exists(path):
        asyncio.run(_synthesize(text, path))
    return path
