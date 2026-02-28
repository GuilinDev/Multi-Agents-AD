"""
Handoff Router — Shift handoff generation and acknowledgement.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import get_db, ShiftHandoff, BehavioralEvent, Patient, ShiftType, utcnow
from schemas_v2 import HandoffGenerateRequest, HandoffOut, AcknowledgeRequest
import llm_service

router = APIRouter(prefix="/api/handoffs", tags=["Handoffs"])


@router.post("/generate", response_model=HandoffOut, status_code=201)
async def generate_handoff(req: HandoffGenerateRequest, db: Session = Depends(get_db)):
    """Generate a shift handoff by summarizing events from the current shift."""
    # Query events for this shift
    events = (
        db.query(BehavioralEvent)
        .filter(
            BehavioralEvent.shift == req.from_shift,
        )
        .join(Patient)
        .filter(Patient.facility_id == req.facility_id)
        .order_by(BehavioralEvent.event_at.desc())
        .limit(100)
        .all()
    )

    if not events:
        # Create empty handoff
        handoff = ShiftHandoff(
            facility_id=req.facility_id,
            from_shift=req.from_shift,
            to_shift=req.to_shift,
            events_summary=[{"note": "No events this shift"}],
            pending_items=[],
        )
        db.add(handoff)
        db.commit()
        db.refresh(handoff)
        return handoff

    # Build events data for LLM
    events_data = []
    for e in events:
        patient = db.query(Patient).get(e.patient_id)
        events_data.append({
            "patient_name": patient.name if patient else "Unknown",
            "patient_id": e.patient_id,
            "event_type": e.event_type.value if e.event_type else "Other",
            "severity": e.severity.value if e.severity else "Medium",
            "description": e.description,
            "intervention": e.intervention_description,
            "outcome": e.outcome_description,
            "resolved": e.resolved,
            "event_at": str(e.event_at),
        })

    # Summarize with LLM
    summary = await llm_service.summarize_events(events_data)

    handoff = ShiftHandoff(
        facility_id=req.facility_id,
        from_shift=req.from_shift,
        to_shift=req.to_shift,
        events_summary=summary.get("events_summary", []),
        pending_items=summary.get("pending_items", []),
    )
    db.add(handoff)
    db.commit()
    db.refresh(handoff)
    return handoff


@router.get("", response_model=list[HandoffOut])
def list_handoffs(facility_id: int = None, limit: int = 20, db: Session = Depends(get_db)):
    q = db.query(ShiftHandoff)
    if facility_id:
        q = q.filter(ShiftHandoff.facility_id == facility_id)
    return q.order_by(ShiftHandoff.handoff_time.desc()).limit(limit).all()


@router.get("/{handoff_id}", response_model=HandoffOut)
def get_handoff(handoff_id: int, db: Session = Depends(get_db)):
    handoff = db.query(ShiftHandoff).get(handoff_id)
    if not handoff:
        raise HTTPException(404, "Handoff not found")
    return handoff


@router.post("/{handoff_id}/acknowledge")
def acknowledge_handoff(handoff_id: int, req: AcknowledgeRequest, db: Session = Depends(get_db)):
    handoff = db.query(ShiftHandoff).get(handoff_id)
    if not handoff:
        raise HTTPException(404, "Handoff not found")
    if handoff.acknowledged_by_id:
        raise HTTPException(400, "Already acknowledged")
    handoff.acknowledged_by_id = req.staff_id
    handoff.acknowledged_at = utcnow()
    db.commit()
    return {"handoff_id": handoff_id, "acknowledged_by": req.staff_id, "status": "acknowledged"}
