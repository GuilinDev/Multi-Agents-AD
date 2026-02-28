"""
Pydantic schemas for Memowell API v2.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# --- Event schemas ---

class EventReportRequest(BaseModel):
    patient_id: int
    reporter_id: int
    text: Optional[str] = None  # Either text or audio file

class EventParsed(BaseModel):
    event_type: str
    severity: str
    location: str
    trigger: str
    summary: str

class ProtocolStep(BaseModel):
    text: str
    source: str
    title: str
    page: int
    filename: str
    score: Optional[float] = None

class EventReportResponse(BaseModel):
    event_id: int
    parsed: EventParsed
    protocols: list[ProtocolStep]
    transcription: Optional[str] = None

class InterventionRequest(BaseModel):
    text: Optional[str] = None

class OutcomeRequest(BaseModel):
    text: Optional[str] = None
    resolved: bool = False

class EventOut(BaseModel):
    id: int
    patient_id: int
    reporter_id: int
    shift: Optional[str] = None
    event_type: str
    severity: str
    description: str
    location: Optional[str] = None
    trigger: Optional[str] = None
    protocol_matched: Optional[list] = None
    intervention_description: Optional[str] = None
    intervention_at: Optional[datetime] = None
    outcome_description: Optional[str] = None
    outcome_at: Optional[datetime] = None
    resolved: bool = False
    follow_up: Optional[list] = None
    event_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Patient schemas ---

class PatientCreate(BaseModel):
    facility_id: int
    name: str
    room: Optional[str] = None
    diagnosis: Optional[str] = None
    cognitive_level: Optional[str] = None
    medications: Optional[list] = []
    allergies: Optional[list] = []
    special_notes: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    room: Optional[str] = None
    diagnosis: Optional[str] = None
    cognitive_level: Optional[str] = None
    medications: Optional[list] = None
    allergies: Optional[list] = None
    special_notes: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    is_active: Optional[bool] = None

class PatientOut(BaseModel):
    id: int
    facility_id: int
    name: str
    room: Optional[str] = None
    diagnosis: Optional[str] = None
    cognitive_level: Optional[str] = None
    medications: Optional[list] = None
    allergies: Optional[list] = None
    special_notes: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PatientDetail(PatientOut):
    events: list[EventOut] = []


# --- Handoff schemas ---

class HandoffGenerateRequest(BaseModel):
    facility_id: int
    from_shift: str  # Day, Evening, Night
    to_shift: str

class HandoffOut(BaseModel):
    id: int
    facility_id: int
    from_shift: str
    to_shift: str
    handoff_time: Optional[datetime] = None
    events_summary: Optional[list] = None
    pending_items: Optional[list] = None
    acknowledged_by_id: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AcknowledgeRequest(BaseModel):
    staff_id: int
