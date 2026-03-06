"""
Event Router — Behavioral event reporting with Context → Intervention → Outcome loop.
"""

from datetime import datetime, timezone, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import get_db, BehavioralEvent, Patient, CareStaff, Facility, EventType, Severity, ShiftType, utcnow
from schemas_v2 import (
    EventReportResponse, EventParsed, ProtocolStep,
    InterventionRequest, OutcomeRequest, EventOut,
)
import llm_service
import rag_service

router = APIRouter(prefix="/api/events", tags=["Events"])


def _determine_shift() -> str:
    """Determine current shift based on UTC hour (rough heuristic)."""
    hour = datetime.now(timezone.utc).hour
    if 11 <= hour < 19:  # ~7am-3pm ET
        return "Day"
    elif 19 <= hour or hour < 3:  # ~3pm-11pm ET
        return "Evening"
    else:
        return "Night"


@router.post("/report", response_model=EventReportResponse)
async def report_event(
    patient_id: int = Form(...),
    reporter_id: int = Form(...),
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Report a behavioral event via text or audio. Returns parsed event + matched protocols."""
    # Validate patient and reporter exist
    patient = db.query(Patient).get(patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    reporter = db.query(CareStaff).get(reporter_id)
    if not reporter:
        raise HTTPException(404, "Reporter not found")

    # Get text from audio or form
    transcription = None
    if audio:
        audio_bytes = await audio.read()
        transcription = await llm_service.transcribe_audio(audio_bytes, audio.filename or "audio.wav")
        description = transcription
    elif text:
        description = text
    else:
        raise HTTPException(400, "Either text or audio file is required")

    # Parse event with LLM
    parsed = await llm_service.parse_event(description)

    # Map to enums (with fallback)
    try:
        event_type = EventType(parsed.get("event_type", "Other"))
    except ValueError:
        event_type = EventType.OTHER
    try:
        severity = Severity(parsed.get("severity", "Medium"))
    except ValueError:
        severity = Severity.MEDIUM

    # Skip RAG for positive/no-issue reports
    # Only skip RAG if the parsed summary indicates explicitly positive/no-issue
    combined_text = (parsed.get("summary", "") + " " + description).lower()
    is_positive = any(kw in combined_text
                      for kw in ["good day", "doing well", "doing good", "doing great", "doing fine",
                                 "no issue", "no issues", "no concern", "no concerns", "no problem",
                                 "stable", "no incident", "uneventful", "all good", "everything is fine",
                                 "no notable", "routine", "normal day", "no behavioral"])
    if event_type == EventType.OTHER and severity == Severity.LOW and is_positive:
        protocols_formatted = []
        summarized = [{"source": "N/A", "page": 0, "steps": ["No specific protocols needed. Continue monitoring."]}]
    else:
        # Search protocols via RAG
        raw_protocols = rag_service.search_by_event_type(event_type.value)
        protocols_formatted = rag_service.format_protocol_for_display(raw_protocols)

        # LLM post-processing: summarize into actionable steps
        try:
            summarized = await llm_service.summarize_protocols(description, protocols_formatted)
        except Exception:
            summarized = []

        # Merge steps back into formatted protocols
        for i, p in enumerate(protocols_formatted):
            if i < len(summarized):
                p["steps"] = summarized[i].get("steps", [])

    # Create DB record
    event = BehavioralEvent(
        patient_id=patient_id,
        reporter_id=reporter_id,
        shift=_determine_shift(),
        event_type=event_type,
        severity=severity,
        description=description,
        location=parsed.get("location", "Unknown"),
        trigger=parsed.get("trigger", "Unknown"),
        protocol_matched=[
            {"source": s.get("source", ""), "page": s.get("page", 0), "steps": s.get("steps", [])}
            for s in summarized
        ],
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Build response protocols
    if protocols_formatted:
        response_protocols = [ProtocolStep(**p) for p in protocols_formatted]
    else:
        response_protocols = [
            ProtocolStep(source=s.get("source", "N/A"), page=s.get("page", 0), steps=s.get("steps", []))
            for s in summarized
        ]

    return EventReportResponse(
        event_id=event.id,
        parsed=EventParsed(**parsed),
        protocols=response_protocols,
        transcription=transcription,
    )


@router.post("/{event_id}/intervention")
async def record_intervention(
    event_id: int,
    audio: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Record an intervention for an event."""
    event = db.query(BehavioralEvent).get(event_id)
    if not event:
        raise HTTPException(404, "Event not found")

    if audio:
        audio_bytes = await audio.read()
        description = await llm_service.transcribe_audio(audio_bytes)
    elif text:
        description = text
    else:
        raise HTTPException(400, "Either text or audio is required")

    event.intervention_description = description
    event.intervention_at = utcnow()
    db.commit()
    return {"event_id": event_id, "intervention": description, "status": "recorded"}


@router.post("/{event_id}/outcome")
async def record_outcome(
    event_id: int,
    text: Optional[str] = Form(None),
    resolved: bool = Form(False),
    audio: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Record the outcome, completing the C→I→O loop."""
    event = db.query(BehavioralEvent).get(event_id)
    if not event:
        raise HTTPException(404, "Event not found")

    if audio:
        audio_bytes = await audio.read()
        description = await llm_service.transcribe_audio(audio_bytes)
    elif text:
        description = text
    else:
        raise HTTPException(400, "Either text or audio is required")

    event.outcome_description = description
    event.outcome_at = utcnow()
    event.resolved = resolved
    db.commit()
    return {"event_id": event_id, "outcome": description, "resolved": resolved, "status": "recorded"}


@router.get("", response_model=list[EventOut])
def list_events(
    patient_id: Optional[int] = None,
    shift: Optional[str] = None,
    event_date: Optional[date] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List events with optional filters."""
    q = db.query(BehavioralEvent)
    if patient_id:
        q = q.filter(BehavioralEvent.patient_id == patient_id)
    if shift:
        q = q.filter(BehavioralEvent.shift == shift)
    if event_date:
        q = q.filter(
            BehavioralEvent.event_at >= datetime.combine(event_date, datetime.min.time()).replace(tzinfo=timezone.utc),
            BehavioralEvent.event_at < datetime.combine(event_date, datetime.max.time()).replace(tzinfo=timezone.utc),
        )
    return q.order_by(BehavioralEvent.event_at.desc()).limit(limit).all()


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event details."""
    event = db.query(BehavioralEvent).get(event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    return event


# --- Bulk Import (bypass LLM, for syncing pre-parsed simulation data) ---

class BulkPatient(BaseModel):
    name: str
    room: str = ""
    diagnosis: str = ""
    cognitive_level: str = ""
    medications: list = []
    special_notes: str = ""

class BulkEvent(BaseModel):
    patient_name: str
    reporter_name: str = "Simulation Agent"
    shift: str = "Day"
    event_type: str = "Other"
    severity: str = "Medium"
    description: str
    location: str = ""
    trigger: str = ""
    protocol_matched: list = []
    intervention_description: str = ""
    outcome_description: str = ""
    resolved: bool = False
    event_at: Optional[str] = None

class BulkImportRequest(BaseModel):
    patients: List[BulkPatient] = []
    events: List[BulkEvent] = []

@router.delete("/bulk-clear")
def bulk_clear(db: Session = Depends(get_db)):
    """Clear all events and non-seed patients for re-import. Keeps seed patients (id 1-3)."""
    deleted_events = db.query(BehavioralEvent).delete()
    deleted_patients = db.query(Patient).filter(Patient.id > 3).delete()
    db.commit()
    return {"events_deleted": deleted_events, "patients_deleted": deleted_patients}

@router.post("/bulk-import")
def bulk_import(req: BulkImportRequest, db: Session = Depends(get_db)):
    """
    Bulk import pre-parsed simulation data. No LLM calls.
    Creates patients if they don't exist, then inserts events directly.
    """
    # Ensure facility exists
    facility = db.query(Facility).first()
    if not facility:
        facility = Facility(name="Sunrise Memory Care", address="Simulation")
        db.add(facility)
        db.flush()

    # Ensure at least one reporter exists
    reporter = db.query(CareStaff).first()
    if not reporter:
        reporter = CareStaff(facility_id=facility.id, name="Simulation Agent", role="CNA")
        db.add(reporter)
        db.flush()

    # Create patients
    patient_map = {}
    for p in req.patients:
        existing = db.query(Patient).filter(Patient.name == p.name).first()
        if existing:
            patient_map[p.name] = existing.id
        else:
            new_p = Patient(
                facility_id=facility.id,
                name=p.name, room=p.room, diagnosis=p.diagnosis,
                cognitive_level=p.cognitive_level, medications=p.medications,
                special_notes=p.special_notes,
            )
            db.add(new_p)
            db.flush()
            patient_map[p.name] = new_p.id

    # Build patient name lookup for events (include existing patients not in req.patients)
    all_patients = db.query(Patient).all()
    for ap in all_patients:
        if ap.name not in patient_map:
            patient_map[ap.name] = ap.id

    # Import events
    imported = 0
    skipped = 0
    for e in req.events:
        pid = patient_map.get(e.patient_name)
        if not pid:
            # Auto-create patient
            new_p = Patient(facility_id=facility.id, name=e.patient_name, room="TBD")
            db.add(new_p)
            db.flush()
            patient_map[e.patient_name] = new_p.id
            pid = new_p.id

        # Map enums safely (handle both "Agitation" and "AGITATION" formats)
        try:
            etype = EventType(e.event_type)
        except ValueError:
            try:
                etype = EventType(e.event_type.replace('_', ' ').title().replace(' ', '_'))
            except ValueError:
                etype = EventType.OTHER
        try:
            sev = Severity(e.severity)
        except ValueError:
            try:
                sev = Severity(e.severity.title())
            except ValueError:
                sev = Severity.MEDIUM

        # Map shift
        shift_map = {"DAY": "Day", "EVENING": "Evening", "NIGHT": "Night", "Day": "Day", "Evening": "Evening", "Night": "Night"}
        shift_val = shift_map.get(e.shift, e.shift)

        evt = BehavioralEvent(
            patient_id=pid,
            reporter_id=reporter.id,
            shift=shift_val,
            event_type=etype,
            severity=sev,
            description=e.description,
            location=e.location,
            trigger=e.trigger,
            protocol_matched=e.protocol_matched,
            intervention_description=e.intervention_description or None,
            intervention_at=utcnow() if e.intervention_description else None,
            outcome_description=e.outcome_description or None,
            outcome_at=utcnow() if e.outcome_description else None,
            resolved=e.resolved,
            event_at=datetime.fromisoformat(e.event_at) if e.event_at else utcnow(),
        )
        db.add(evt)
        imported += 1

    db.commit()
    return {
        "status": "ok",
        "patients_in_map": len(patient_map),
        "events_imported": imported,
        "events_skipped": skipped,
    }


# --- Simulation Dashboard Stats ---

@router.get("/stats/dashboard")
def simulation_dashboard(db: Session = Depends(get_db)):
    """Aggregate stats for the simulation dashboard. No LLM calls."""
    total_events = db.query(BehavioralEvent).count()
    total_patients = db.query(Patient).count()
    patients_with_events = db.query(BehavioralEvent.patient_id).distinct().count()

    # Event type distribution
    type_dist = db.query(
        BehavioralEvent.event_type, func.count(BehavioralEvent.id)
    ).group_by(BehavioralEvent.event_type).all()
    event_types = {(t.value if hasattr(t, 'value') else str(t)): c for t, c in type_dist}

    # Severity distribution
    sev_dist = db.query(
        BehavioralEvent.severity, func.count(BehavioralEvent.id)
    ).group_by(BehavioralEvent.severity).all()
    severities = {(s.value if hasattr(s, 'value') else str(s)): c for s, c in sev_dist}

    # Shift distribution
    shift_dist = db.query(
        BehavioralEvent.shift, func.count(BehavioralEvent.id)
    ).group_by(BehavioralEvent.shift).all()
    shifts = {(s.value if hasattr(s, 'value') else str(s)): c for s, c in shift_dist}

    # Protocol coverage (events with non-empty protocol_matched)
    events_with_protocols = db.query(BehavioralEvent).filter(
        BehavioralEvent.protocol_matched.isnot(None),
        BehavioralEvent.protocol_matched != '[]',
        BehavioralEvent.protocol_matched != 'null',
    ).count()
    protocol_coverage = round(events_with_protocols / total_events * 100, 1) if total_events else 0

    # Intervention rate
    events_with_intervention = db.query(BehavioralEvent).filter(
        BehavioralEvent.intervention_description.isnot(None),
    ).count()
    intervention_rate = round(events_with_intervention / total_events * 100, 1) if total_events else 0

    # Resolution rate
    resolved_events = db.query(BehavioralEvent).filter(BehavioralEvent.resolved == True).count()
    resolution_rate = round(resolved_events / total_events * 100, 1) if total_events else 0

    # Top patients by event count
    top_patients = db.query(
        Patient.name, func.count(BehavioralEvent.id).label("count")
    ).join(BehavioralEvent).group_by(Patient.name).order_by(
        func.count(BehavioralEvent.id).desc()
    ).limit(10).all()

    return {
        "total_events": total_events,
        "total_patients": total_patients,
        "patients_with_events": patients_with_events,
        "event_types": event_types,
        "severities": severities,
        "shifts": shifts,
        "protocol_coverage_pct": protocol_coverage,
        "intervention_rate_pct": intervention_rate,
        "resolution_rate_pct": resolution_rate,
        "top_patients": [{"name": n, "events": c} for n, c in top_patients],
    }
