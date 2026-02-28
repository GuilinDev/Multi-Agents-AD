"""FastAPI backend for Multi-Agent Alzheimer's Companion."""

import sys
import os
import uuid
import tempfile
from pathlib import Path

# Add parent directory so we can import existing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from agents import (
    ConversationState,
    therapy_respond,
    monitor_analyze,
    generate_caregiver_summary,
)
from tts_engine import text_to_speech, AUDIO_DIR
from image_gen import maybe_generate_scene, IMAGE_DIR
from memory_store import (
    load_memory,
    save_memory,
    extract_and_save_memories,
    format_memory_prompt,
    save_session_summary,
)
from trend_tracker import (
    save_trend_entry,
    load_trends,
    get_alert_history,
)
from patient_profile import PATIENTS

from schemas import (
    StartSessionRequest,
    StartSessionResponse,
    ChatRequest,
    ChatResponse,
    MonitorReport,
    EndSessionResponse,
    PatientInfo,
    SummaryResponse,
)

from rag_router import router as rag_router

app = FastAPI(
    title="Memowell API",
    description="Voice-first Copilot for Dementia Behavioral Events — Caregiver Copilot REST API",
    version="2.0.0",
)

app.include_router(rag_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: dict[str, dict] = {}


def _get_session(session_id: str) -> dict:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]


# --- Endpoints ---


@app.get("/api/patients", response_model=list[PatientInfo])
def list_patients():
    return [
        PatientInfo(
            id=pid,
            name=p["name"],
            age=p["age"],
            diagnosis=p["diagnosis"],
            cognitive_level=p["cognitive_level"],
        )
        for pid, p in PATIENTS.items()
    ]


@app.post("/api/session/start", response_model=StartSessionResponse)
def start_session(req: StartSessionRequest):
    if req.patient_id not in PATIENTS:
        raise HTTPException(status_code=404, detail="Patient not found")
    sid = str(uuid.uuid4())
    state = ConversationState(patient_id=req.patient_id)
    memory = load_memory(req.patient_id)
    sessions[sid] = {"state": state, "memory": memory}
    return StartSessionResponse(
        session_id=sid,
        patient_name=PATIENTS[req.patient_id]["name"],
        patient_id=req.patient_id,
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    session_id: str = Form(...),
    message: str = Form(""),
    audio: UploadFile | None = File(None),
):
    sess = _get_session(session_id)
    state: ConversationState = sess["state"]
    memory: dict = sess["memory"]

    # Transcribe audio if provided and no text message
    if audio and not message.strip():
        try:
            from groq import Groq

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            tmp.write(await audio.read())
            tmp.close()
            client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
            with open(tmp.name, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3", file=f
                )
            message = transcription.text
            os.unlink(tmp.name)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Audio transcription failed: {e}")

    if not message.strip():
        raise HTTPException(status_code=400, detail="No message provided")

    # Therapy agent
    memory_context = format_memory_prompt(memory)
    response = therapy_respond(state, message, memory_context)

    # Monitor agent
    report = monitor_analyze(state, message, response)
    save_trend_entry(state.patient_id, report)

    # Extract memories periodically
    if state.turn_count % 5 == 0 and state.turn_count > 0:
        sess["memory"] = extract_and_save_memories(
            state.patient_id, state.therapy_history, memory
        )

    # TTS
    audio_url = None
    try:
        audio_path = text_to_speech(response)
        audio_url = f"/api/audio/{os.path.basename(audio_path)}"
    except Exception:
        pass

    # Image
    image_url = None
    try:
        img_path = maybe_generate_scene(message, response)
        if img_path:
            image_url = f"/api/images/{os.path.basename(img_path)}"
    except Exception:
        pass

    return ChatResponse(
        response=response,
        monitor=MonitorReport(**{k: report.get(k, "") for k in MonitorReport.model_fields}),
        audio_url=audio_url,
        image_url=image_url,
        turn=state.turn_count,
    )


@app.post("/api/session/end", response_model=EndSessionResponse)
def end_session(session_id: str = Form(...)):
    sess = _get_session(session_id)
    state: ConversationState = sess["state"]
    memory: dict = sess["memory"]

    summary = "No conversation data."
    if state.turn_count > 0:
        summary = generate_caregiver_summary(state)
        save_session_summary(state.patient_id, memory, state.turn_count, [], summary)
        extract_and_save_memories(state.patient_id, state.therapy_history, memory)

    turns = state.turn_count
    del sessions[session_id]

    return EndSessionResponse(session_id=session_id, summary=summary, turns=turns)


@app.get("/api/trends/{patient_id}")
def get_trends(patient_id: str):
    if patient_id not in PATIENTS:
        raise HTTPException(status_code=404, detail="Patient not found")
    trends = load_trends(patient_id)
    alerts = get_alert_history(patient_id)
    return {"trends": trends, "alerts": alerts}


@app.get("/api/summary/{patient_id}", response_model=SummaryResponse)
def get_summary(patient_id: str):
    if patient_id not in PATIENTS:
        raise HTTPException(status_code=404, detail="Patient not found")
    memory = load_memory(patient_id)
    if memory["session_history"]:
        last = memory["session_history"][-1]
        summary = last["summary"]
    else:
        summary = "No sessions recorded yet."
    return SummaryResponse(
        patient_id=patient_id,
        patient_name=PATIENTS[patient_id]["name"],
        summary=summary,
        session_count=len(memory["session_history"]),
    )


@app.get("/api/audio/{filename}")
def serve_audio(filename: str):
    path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(path, media_type="audio/mpeg")


@app.get("/api/images/{filename}")
def serve_image(filename: str):
    path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path, media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
