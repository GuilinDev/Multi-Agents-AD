"""
Environment — manages the state of the virtual nursing home.
Tracks resident locations, ongoing events, staff assignments, etc.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class Location(str, Enum):
    ROOM = "room"
    HALLWAY = "hallway"
    DINING_ROOM = "dining_room"
    ACTIVITY_ROOM = "activity_room"
    GARDEN = "garden"
    NURSES_STATION = "nurses_station"
    BATHROOM = "bathroom"
    COMMON_AREA = "common_area"
    ENTRANCE = "entrance"  # for exit-seeking


class ResidentState(str, Enum):
    SLEEPING = "sleeping"
    RESTING = "resting"
    EATING = "eating"
    ACTIVITY = "activity"
    WANDERING = "wandering"
    AGITATED = "agitated"
    CALM = "calm"
    IN_DISTRESS = "in_distress"
    RECEIVING_CARE = "receiving_care"


@dataclass
class ResidentStatus:
    """Current status of a resident in the simulation."""
    patient_id: str
    name: str
    location: Location = Location.ROOM
    state: ResidentState = ResidentState.RESTING
    current_behavior: Optional[str] = None
    last_meal: Optional[datetime] = None
    last_medication: Optional[datetime] = None
    last_toileting: Optional[datetime] = None
    pain_level: int = 0  # 0-10
    agitation_level: int = 0  # 0-10
    active_event_id: Optional[int] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class StaffStatus:
    """Current status of a staff member."""
    caregiver_id: str
    name: str
    on_duty: bool = False
    current_task: Optional[str] = None
    attending_patient: Optional[str] = None
    tasks_completed: int = 0


class Environment:
    """The virtual nursing home environment."""

    def __init__(self):
        self.residents: Dict[str, ResidentStatus] = {}
        self.staff: Dict[str, StaffStatus] = {}
        self.event_log: List[dict] = []
        self.facility_alerts: List[str] = []

    def add_resident(self, patient_id: str, name: str):
        self.residents[patient_id] = ResidentStatus(
            patient_id=patient_id, name=name
        )

    def add_staff(self, caregiver_id: str, name: str):
        self.staff[caregiver_id] = StaffStatus(
            caregiver_id=caregiver_id, name=name
        )

    def update_resident(self, patient_id: str, **kwargs):
        if patient_id in self.residents:
            for k, v in kwargs.items():
                if hasattr(self.residents[patient_id], k):
                    setattr(self.residents[patient_id], k, v)

    def update_staff(self, caregiver_id: str, **kwargs):
        if caregiver_id in self.staff:
            for k, v in kwargs.items():
                if hasattr(self.staff[caregiver_id], k):
                    setattr(self.staff[caregiver_id], k, v)

    def get_residents_in_location(self, location: Location) -> List[ResidentStatus]:
        return [r for r in self.residents.values() if r.location == location]

    def get_agitated_residents(self, threshold: int = 5) -> List[ResidentStatus]:
        return [r for r in self.residents.values() if r.agitation_level >= threshold]

    def get_available_staff(self) -> List[StaffStatus]:
        return [s for s in self.staff.values()
                if s.on_duty and s.attending_patient is None]

    def log_event(self, event: dict):
        self.event_log.append(event)

    def get_facility_snapshot(self) -> dict:
        """Get a summary of current facility state."""
        return {
            "total_residents": len(self.residents),
            "residents_sleeping": sum(1 for r in self.residents.values()
                                      if r.state == ResidentState.SLEEPING),
            "residents_agitated": len(self.get_agitated_residents()),
            "staff_on_duty": sum(1 for s in self.staff.values() if s.on_duty),
            "staff_available": len(self.get_available_staff()),
            "active_events": sum(1 for r in self.residents.values()
                                 if r.active_event_id is not None),
            "total_events_today": len(self.event_log),
        }
