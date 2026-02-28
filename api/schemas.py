"""Pydantic models for API request/response."""

from pydantic import BaseModel, Field
from typing import Optional


class StartSessionRequest(BaseModel):
    patient_id: str = "margaret"


class StartSessionResponse(BaseModel):
    session_id: str
    patient_name: str
    patient_id: str


class ChatRequest(BaseModel):
    session_id: str
    message: str = ""


class MonitorReport(BaseModel):
    emotion: str = "unknown"
    engagement: str = "medium"
    memory_quality: str = "unknown"
    cognitive_signs: str = ""
    risk_flags: str = ""
    recommendation: str = ""
    turn: int = 0
    timestamp: str = ""


class ChatResponse(BaseModel):
    response: str
    monitor: MonitorReport
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    turn: int = 0


class EndSessionResponse(BaseModel):
    session_id: str
    summary: str
    turns: int


class PatientInfo(BaseModel):
    id: str
    name: str
    age: int
    diagnosis: str
    cognitive_level: str


class TrendEntry(BaseModel):
    session_date: str
    turn: int
    emotion: str
    memory_quality: str
    engagement: str
    scores: dict
    risk_flags: str = ""


class SummaryResponse(BaseModel):
    patient_id: str
    patient_name: str
    summary: str
    session_count: int


class AlertEntry(BaseModel):
    date: str
    turn: int
    flag: str
    emotion: str
