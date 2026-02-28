"""
Memowell API — Voice-first Copilot for Dementia Behavioral Events
Caregiver Copilot REST API v2.0
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from rag_router import router as rag_router
from event_router import router as event_router
from patient_router import router as patient_router
from handoff_router import router as handoff_router
from models import init_db, seed_demo_data

app = FastAPI(
    title="Memowell API",
    description="Voice-first Copilot for Dementia Behavioral Events — Caregiver Copilot REST API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB + seed
init_db()
seed_demo_data()

# Routers
app.include_router(rag_router)
app.include_router(event_router)
app.include_router(patient_router)
app.include_router(handoff_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
