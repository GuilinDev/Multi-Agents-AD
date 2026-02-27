"""Dual-agent system: TherapyAgent + MonitorAgent."""

import os
import json
import time
from dataclasses import dataclass, field
from groq import Groq

from patient_profile import PATIENTS, DEFAULT_PATIENT

# ---------------------------------------------------------------------------
# LLM client (Groq + Llama)
# ---------------------------------------------------------------------------

MODEL = "llama-3.3-70b-versatile"

def get_client():
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")
    return Groq(api_key=api_key)

def llm_call(system: str, messages: list[dict], temperature: float = 0.7) -> str:
    """Call Groq Llama. messages = [{"role":"user"|"assistant","content":str}, ...]"""
    client = get_client()
    
    all_messages = [{"role": "system", "content": system}] + messages
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=all_messages,
        temperature=temperature,
        max_tokens=1024,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Therapy Agent
# ---------------------------------------------------------------------------

THERAPY_SYSTEM = """You are a compassionate reminiscence therapy companion for patients 
with early-stage Alzheimer's Disease. Your role is to engage the patient in warm, 
natural conversations that gently stimulate their long-term memories.

PATIENT PROFILE:
{profile}

GUIDELINES:
- Be warm, patient, and encouraging. Use the patient's first name.
- Ask open-ended questions about their past — teaching, family, garden, favorite memories.
- When they share a memory, show genuine interest and ask follow-up questions.
- If they seem confused, gently redirect without correcting. Never say "you already told me that."
- Use sensory cues: "What did the roses smell like?" "What color was the cabin?"
- Keep responses concise (2-4 sentences). This is a conversation, not a lecture.
- Occasionally reference things they've mentioned before to show you remember.
- If they seem tired or frustrated, offer to take a break or change topics.
- Use gentle humor when appropriate — Margaret enjoys it.
- NEVER break character. You are their companion, not an AI assistant.
"""

MONITOR_SYSTEM = """You are a clinical monitoring AI that analyzes conversations between 
a therapy companion and an Alzheimer's patient. You observe silently and produce structured 
assessments.

PATIENT PROFILE:
{profile}

For each exchange, output a JSON object with these fields:
{{
  "emotion": "primary emotion detected (e.g., happy, nostalgic, confused, anxious, calm, frustrated)",
  "engagement": "low | medium | high",
  "memory_quality": "clear | partial | confused | fabricated",
  "cognitive_signs": "any notable cognitive observations",
  "risk_flags": "any concerning patterns (empty string if none)",
  "recommendation": "brief suggestion for the therapy companion or caregiver"
}}

Output ONLY valid JSON. No extra text."""


@dataclass
class ConversationState:
    patient_id: str = DEFAULT_PATIENT
    therapy_history: list = field(default_factory=list)
    monitor_reports: list = field(default_factory=list)
    turn_count: int = 0
    session_start: float = field(default_factory=time.time)

    @property
    def patient(self):
        return PATIENTS[self.patient_id]


def therapy_respond(state: ConversationState, user_message: str) -> str:
    """Generate therapy agent response."""
    profile_text = json.dumps(state.patient, indent=2)
    system = THERAPY_SYSTEM.format(profile=profile_text)

    state.therapy_history.append({"role": "user", "content": user_message})
    
    response = llm_call(system, state.therapy_history, temperature=0.8)
    
    state.therapy_history.append({"role": "assistant", "content": response})
    state.turn_count += 1
    
    return response


def monitor_analyze(state: ConversationState, patient_msg: str, agent_msg: str) -> dict:
    """Monitor agent analyzes the latest exchange."""
    profile_text = json.dumps(state.patient, indent=2)
    system = MONITOR_SYSTEM.format(profile=profile_text)

    recent = state.therapy_history[-6:] if len(state.therapy_history) > 6 else state.therapy_history
    context = "\n".join([f"{'Patient' if m['role']=='user' else 'Companion'}: {m['content']}" 
                         for m in recent])
    
    messages = [{"role": "user", "content": f"Analyze this therapy exchange:\n\n{context}"}]
    
    raw = llm_call(system, messages, temperature=0.3)
    
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        report = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        report = {
            "emotion": "unknown",
            "engagement": "medium",
            "memory_quality": "unknown",
            "cognitive_signs": "parse error",
            "risk_flags": "",
            "recommendation": raw[:200]
        }
    
    report["turn"] = state.turn_count
    report["timestamp"] = time.strftime("%H:%M:%S")
    state.monitor_reports.append(report)
    
    return report


def generate_caregiver_summary(state: ConversationState) -> str:
    """Generate end-of-session caregiver summary."""
    if not state.monitor_reports:
        return "No session data available."
    
    profile_text = json.dumps(state.patient, indent=2)
    reports_text = json.dumps(state.monitor_reports, indent=2)
    duration = int(time.time() - state.session_start)
    
    system = f"""You are a clinical AI assistant generating a caregiver summary report.
Patient: {state.patient['name']}
Session duration: {duration} seconds, {state.turn_count} exchanges.

Based on the monitoring reports below, write a clear, compassionate summary for the 
patient's family caregiver (Susan). Include:
1. Overall mood and engagement level
2. Memory observations (what they remembered well vs. struggled with)
3. Any concerns or risk flags
4. Recommendations for the caregiver
5. Suggested topics for next session

Keep it warm but professional. This is for a family member, not a clinician."""

    messages = [{"role": "user", "content": f"Session monitoring reports:\n{reports_text}"}]
    return llm_call(system, messages, temperature=0.5)
