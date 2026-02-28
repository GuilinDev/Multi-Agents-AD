"""
Memowell Data Models — SQLite via SQLAlchemy ORM
Based on PRD v1 Section 5.3
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float,
    DateTime, Boolean, Enum, ForeignKey, JSON,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///./memowell.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def utcnow():
    return datetime.now(timezone.utc)


# --- Enums ---

class StaffRole(str, enum.Enum):
    CNA = "CNA"
    NURSE = "Nurse"
    DON = "DON"
    ADMIN = "Admin"


class EventType(str, enum.Enum):
    AGITATION = "Agitation"
    SUNDOWNING = "Sundowning"
    REFUSAL = "Refusal"
    WANDERING = "Wandering"
    FALL = "Fall"
    AGGRESSION = "Aggression"
    CONFUSION = "Confusion"
    SLEEP_DISTURBANCE = "Sleep_Disturbance"
    OTHER = "Other"


class Severity(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ShiftType(str, enum.Enum):
    DAY = "Day"
    EVENING = "Evening"
    NIGHT = "Night"


# --- Models ---

class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    license_number = Column(String(100))
    timezone = Column(String(50), default="America/New_York")
    language = Column(String(10), default="en")
    shift_day_start = Column(String(5), default="07:00")
    shift_evening_start = Column(String(5), default="15:00")
    shift_night_start = Column(String(5), default="23:00")
    created_at = Column(DateTime, default=utcnow)

    patients = relationship("Patient", back_populates="facility")
    staff = relationship("CareStaff", back_populates="facility")
    handoffs = relationship("ShiftHandoff", back_populates="facility")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    name = Column(String(200), nullable=False)
    room = Column(String(50))
    photo_url = Column(String(500))
    diagnosis = Column(Text)
    cognitive_level = Column(String(50))  # MMSE/MoCA score
    medications = Column(JSON, default=list)
    allergies = Column(JSON, default=list)
    special_notes = Column(Text)
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    facility = relationship("Facility", back_populates="patients")
    events = relationship("BehavioralEvent", back_populates="patient")


class CareStaff(Base):
    __tablename__ = "care_staff"

    id = Column(Integer, primary_key=True, autoincrement=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(Enum(StaffRole), nullable=False)
    pin_code = Column(String(10))  # Simple auth for V1
    language_preference = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    facility = relationship("Facility", back_populates="staff")
    reported_events = relationship("BehavioralEvent", back_populates="reporter")


class BehavioralEvent(Base):
    """Core data model — behavioral event with Context → Intervention → Outcome."""
    __tablename__ = "behavioral_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("care_staff.id"), nullable=False)
    shift = Column(Enum(ShiftType))
    
    # Event details
    event_type = Column(Enum(EventType), nullable=False)
    severity = Column(Enum(Severity), default=Severity.MEDIUM)
    description = Column(Text, nullable=False)  # Original voice transcription
    location = Column(String(200))
    trigger = Column(Text)  # Identified trigger if any
    
    # RAG protocol match
    protocol_matched = Column(JSON)  # [{source, section, steps[]}]
    
    # Intervention
    intervention_description = Column(Text)
    intervention_at = Column(DateTime)
    
    # Outcome
    outcome_description = Column(Text)
    outcome_at = Column(DateTime)
    resolved = Column(Boolean, default=False)
    
    # Follow-up
    follow_up = Column(JSON, default=list)  # [{note, assigned_to, due_time}]
    
    # Timestamps
    event_at = Column(DateTime, default=utcnow)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    patient = relationship("Patient", back_populates="events")
    reporter = relationship("CareStaff", back_populates="reported_events")


class ShiftHandoff(Base):
    """Auto-generated shift handoff record."""
    __tablename__ = "shift_handoffs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    from_shift = Column(Enum(ShiftType), nullable=False)
    to_shift = Column(Enum(ShiftType), nullable=False)
    handoff_time = Column(DateTime, default=utcnow)
    
    # Auto-generated content
    events_summary = Column(JSON, default=list)  # Summary of events per patient
    pending_items = Column(JSON, default=list)  # Follow-up items for next shift
    
    # Acknowledgement
    acknowledged_by_id = Column(Integer, ForeignKey("care_staff.id"))
    acknowledged_at = Column(DateTime)
    
    # PDF export
    pdf_url = Column(String(500))
    
    created_at = Column(DateTime, default=utcnow)

    facility = relationship("Facility", back_populates="handoffs")
    acknowledged_by = relationship("CareStaff")


# --- Initialize DB ---

def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized: {DATABASE_URL}")


def seed_demo_data():
    """Seed with demo facility + patients for pilot."""
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Facility).count() > 0:
            print("Database already has data, skipping seed.")
            return

        # Demo facility
        facility = Facility(
            name="Sunrise Memory Care",
            address="123 Care Lane, Columbia, SC 29201",
            license_number="SC-MC-2024-001",
        )
        db.add(facility)
        db.flush()

        # Demo patients
        patients = [
            Patient(
                facility_id=facility.id,
                name="Margaret Thompson",
                room="201A",
                diagnosis="Alzheimer's Disease - Moderate Stage",
                cognitive_level="MMSE: 18/30",
                medications=["Donepezil 10mg", "Memantine 20mg"],
                special_notes="Responds well to music. Daughter visits Tuesdays.",
            ),
            Patient(
                facility_id=facility.id,
                name="Robert Chen",
                room="205B",
                diagnosis="Vascular Dementia",
                cognitive_level="MMSE: 22/30",
                medications=["Aspirin 81mg", "Lisinopril 10mg"],
                special_notes="Former engineer. Likes puzzles and routine.",
            ),
            Patient(
                facility_id=facility.id,
                name="Dorothy Williams",
                room="210A",
                diagnosis="Lewy Body Dementia",
                cognitive_level="MoCA: 14/30",
                medications=["Rivastigmine patch 13.3mg"],
                allergies=["Penicillin"],
                special_notes="Visual hallucinations common in evening. Do NOT use haloperidol.",
            ),
        ]
        db.add_all(patients)

        # Demo staff
        staff = [
            CareStaff(facility_id=facility.id, name="Maria Garcia", role=StaffRole.CNA, pin_code="1234"),
            CareStaff(facility_id=facility.id, name="James Wilson", role=StaffRole.NURSE, pin_code="5678"),
            CareStaff(facility_id=facility.id, name="Dr. Sarah Kim", role=StaffRole.DON, pin_code="9999"),
        ]
        db.add_all(staff)

        db.commit()
        print(f"✅ Seeded demo data: 1 facility, {len(patients)} patients, {len(staff)} staff")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_demo_data()
