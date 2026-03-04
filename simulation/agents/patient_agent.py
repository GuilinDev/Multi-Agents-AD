"""
Patient Agent — simulates dementia patient behavior using LLM.
Each patient has a profile and generates behaviors based on time, environment, and history.

Inspired by Generative Agents (Stanford, 2023): memory + reflection + planning.
"""
import json
import random
from typing import Optional, List, Dict
from datetime import datetime

from simulation.engine.clock import SimulationClock
from simulation.engine.environment import Environment, ResidentState, Location


# Behavior probability weights by time of day
TIME_BEHAVIOR_WEIGHTS = {
    "morning": {
        "refusal_to_eat": 0.3,
        "medication_refusal": 0.4,
        "anxiety": 0.2,
        "wandering": 0.1,
        "bathing_refusal": 0.5,
    },
    "afternoon": {
        "sundowning": 0.1,  # starts building
        "wandering": 0.3,
        "restlessness": 0.3,
        "fall_risk": 0.2,
        "social_disinhibition": 0.2,
    },
    "evening": {
        "sundowning": 0.7,  # peak
        "agitation": 0.5,
        "exit_seeking": 0.3,
        "refusal_to_eat": 0.2,
        "emotional_lability": 0.3,
    },
    "night": {
        "nighttime_agitation": 0.5,
        "wandering": 0.3,
        "loud_vocalizations": 0.3,
        "fall_risk": 0.4,
        "REM_sleep_disorder": 0.3,
    },
}

# Severity modifiers by dementia stage
STAGE_SEVERITY = {
    "mild": 0.5,
    "moderate": 1.0,
    "severe": 1.5,
}


class PatientAgent:
    """
    An AI-driven patient agent that generates realistic behavioral events.
    """

    def __init__(self, profile: dict):
        self.profile = profile
        self.id = profile["id"]
        self.name = profile["name"]
        self.diagnosis = profile["diagnosis"]
        self.stage = profile["stage"]
        self.common_behaviors = profile.get("common_behaviors", [])
        self.triggers = profile.get("triggers", [])
        self.effective_interventions = profile.get("effective_interventions", [])
        self.personality = profile.get("personality", "")
        self.medical_history = profile.get("medical_history", [])
        self.notes = profile.get("notes", "")

        # Memory (inspired by Generative Agents)
        self.memory: List[dict] = []  # recent events
        self.intervention_history: List[dict] = []  # what worked / didn't work
        self.current_mood: str = "neutral"
        self.agitation_level: int = 0  # 0-10

    def should_trigger_behavior(self, clock: SimulationClock, env: Environment) -> Optional[dict]:
        """
        Decide whether this patient should exhibit a behavior at the current time.
        Returns a behavior event dict or None.
        """
        time_of_day = clock.time_of_day
        hour = clock.hour
        severity_mod = STAGE_SEVERITY.get(self.stage, 1.0)

        # Get base probabilities for this time of day
        time_weights = TIME_BEHAVIOR_WEIGHTS.get(time_of_day, {})

        # Filter to behaviors this patient actually exhibits
        candidate_behaviors = []
        for behavior in self.common_behaviors:
            base_prob = time_weights.get(behavior, 0.05)  # default low probability
            adjusted_prob = min(base_prob * severity_mod, 0.9)

            # Boost if we have specific trigger conditions
            if self._check_triggers(clock, env):
                adjusted_prob = min(adjusted_prob * 1.5, 0.95)

            # Reduce probability if recently intervened successfully
            if self._recently_resolved(behavior):
                adjusted_prob *= 0.3

            candidate_behaviors.append({
                "behavior": behavior,
                "probability": adjusted_prob,
            })

        # Roll dice for each candidate
        triggered = []
        for cb in candidate_behaviors:
            if random.random() < cb["probability"]:
                triggered.append(cb["behavior"])

        if not triggered:
            return None

        # Pick the most significant behavior (or random if equal)
        behavior = triggered[0]

        return {
            "patient_id": self.id,
            "patient_name": self.name,
            "behavior": behavior,
            "time": clock.format_time(),
            "location": self._get_likely_location(time_of_day),
            "severity": self._estimate_severity(behavior),
            "context": self._generate_context(behavior, clock),
        }

    def _check_triggers(self, clock: SimulationClock, env: Environment) -> bool:
        """Check if environmental triggers are active."""
        triggers_active = []

        if "routine_change" in self.triggers and clock.is_shift_change():
            triggers_active.append("routine_change")
        if "darkness" in self.triggers and clock.time_of_day == "night":
            triggers_active.append("darkness")
        if "mealtime" in self.triggers and clock.hour in [7, 12, 17]:
            triggers_active.append("mealtime")
        if "medication_time" in self.triggers and clock.hour in [8, 12, 17, 21]:
            triggers_active.append("medication_time")

        return len(triggers_active) > 0

    def _recently_resolved(self, behavior: str, lookback: int = 3) -> bool:
        """Check if this behavior was recently resolved successfully."""
        recent = self.intervention_history[-lookback:]
        return any(
            h.get("behavior") == behavior and h.get("outcome") == "resolved"
            for h in recent
        )

    def _get_likely_location(self, time_of_day: str) -> str:
        """Where is this patient likely to be?"""
        if time_of_day == "night":
            return "room"
        if time_of_day == "morning" and self.profile.get("mobility", "").startswith("bed"):
            return "room"

        locations = {
            "morning": ["dining_room", "room", "bathroom"],
            "afternoon": ["activity_room", "common_area", "hallway", "garden"],
            "evening": ["dining_room", "common_area", "hallway", "room"],
        }
        return random.choice(locations.get(time_of_day, ["room"]))

    def _estimate_severity(self, behavior: str) -> str:
        """Estimate severity based on stage and behavior type."""
        high_severity = ["aggression", "fall_risk", "syncope_episodes", "exit_seeking", "dysphagia"]
        if behavior in high_severity or self.stage == "severe":
            return random.choice(["moderate", "severe"])
        if self.stage == "mild":
            return random.choice(["mild", "moderate"])
        return random.choice(["mild", "moderate", "severe"])

    def _generate_context(self, behavior: str, clock: SimulationClock) -> str:
        """Generate natural language context for the behavior event."""
        # This will be enhanced with LLM in the full version
        templates = {
            "sundowning": f"{self.name} is becoming increasingly agitated as the sun goes down. Pacing near the window, calling out for family.",
            "wandering": f"{self.name} found wandering in the hallway, appears confused about location. Tried to enter another resident's room.",
            "refusal_to_eat": f"{self.name} is refusing to eat, pushing the tray away. Has only had a few sips of water.",
            "aggression": f"{self.name} became combative during care. Swung at staff member when approached for toileting.",
            "visual_hallucinations": f"{self.name} reports seeing people in the room who aren't there. Appears frightened.",
            "fall_risk": f"{self.name} attempted to stand without assistance. Unsteady on feet, nearly fell.",
            "medication_refusal": f"{self.name} is refusing medications. Spat out pills, says 'they're trying to poison me.'",
            "nighttime_agitation": f"{self.name} is awake and calling out loudly. Disturbing other residents. Appears disoriented.",
            "emotional_lability": f"{self.name} started crying suddenly during activity. Unable to explain why. Mood shifted rapidly.",
            "exit_seeking": f"{self.name} found near the main entrance, trying to open the door. Says 'I need to go home.'",
            "bathing_refusal": f"{self.name} is resisting bathing. Becomes agitated when approached about shower time.",
            "repetitive_questions": f"{self.name} has been asking 'Where is my daughter?' every 2 minutes for the past hour.",
            "social_disinhibition": f"{self.name} made inappropriate comments to another resident during lunch. Other resident is upset.",
            "hiding_medications": f"{self.name} appeared to take medications but was later found hiding pills under the mattress.",
            "pica_plants": f"{self.name} was found eating flowers from the arrangement in the common area.",
            "loud_vocalizations": f"{self.name} is calling out loudly and repeatedly from bed. Disturbing adjacent rooms.",
            "freezing_gait": f"{self.name} froze in the doorway and is unable to initiate steps. Appears stuck.",
            "REM_sleep_disorder": f"{self.name} is acting out dreams physically — thrashing and yelling in sleep.",
            "dysphagia": f"{self.name} is coughing during meal. Possible aspiration event with thin liquids.",
            "sleep_disturbance": f"{self.name} is unable to fall asleep despite usual bedtime routine. Anxious and restless.",
            "PTSD_flashbacks": f"{self.name} appears to be reliving a traumatic event. Ducking and covering, shouting commands.",
            "hoarding": f"{self.name}'s room found filled with items taken from common areas — towels, utensils, other residents' belongings.",
            "shadowing": f"{self.name} is following staff member Lisa everywhere, becoming distressed when Lisa steps away.",
            "language_switching": f"{self.name} is speaking only Mandarin and appears unable to understand English instructions.",
            "skin_breakdown_risk": f"During repositioning, noted reddened area on {self.name}'s sacrum. Stage 1 pressure injury developing.",
        }

        return templates.get(
            behavior,
            f"{self.name} is exhibiting {behavior}. Staff attention needed."
        )

    def receive_intervention_result(self, behavior: str, intervention: str, outcome: str):
        """Record the result of an intervention for future behavior adjustment."""
        self.intervention_history.append({
            "behavior": behavior,
            "intervention": intervention,
            "outcome": outcome,  # "resolved", "partially_resolved", "ineffective", "escalated"
        })

        # Adjust agitation based on outcome
        if outcome == "resolved":
            self.agitation_level = max(0, self.agitation_level - 3)
        elif outcome == "partially_resolved":
            self.agitation_level = max(0, self.agitation_level - 1)
        elif outcome == "escalated":
            self.agitation_level = min(10, self.agitation_level + 2)

    def add_memory(self, event: dict):
        """Add an event to short-term memory."""
        self.memory.append(event)
        if len(self.memory) > 20:  # keep last 20 events
            self.memory.pop(0)
