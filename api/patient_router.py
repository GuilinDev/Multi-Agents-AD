"""
Patient Router — CRUD operations for patients.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import get_db, Patient
from schemas_v2 import PatientCreate, PatientUpdate, PatientOut, PatientDetail

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.get("", response_model=list[PatientOut])
def list_patients(facility_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Patient)
    if facility_id:
        q = q.filter(Patient.facility_id == facility_id)
    return q.filter(Patient.is_active == True).all()


@router.get("/{patient_id}", response_model=PatientDetail)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).get(patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    return patient


@router.post("", response_model=PatientOut, status_code=201)
def create_patient(req: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**req.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, req: PatientUpdate, db: Session = Depends(get_db)):
    patient = db.query(Patient).get(patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(patient, k, v)
    db.commit()
    db.refresh(patient)
    return patient
